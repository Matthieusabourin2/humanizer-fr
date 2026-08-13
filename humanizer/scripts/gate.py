#!/usr/bin/env python3
"""Porte chiffrée du humanizer v3 : compte ce que le modèle doit montrer.

Checks déterministes 1-6 du numbers gate de SKILL.md :
  1. tirets cadratins + demi-cadratins hors citations (doit être 0,
     sauf plafond attesté par un profil)
  2. constructions de contraste dures (famille P9/FR4) vs budget
  3. atterrissages de paragraphe (P54) : ratio et plus longue série
  4. fenêtres-cluster de 4 phrases, 2+ familles structurelles distinctes
  5. vocabulaire Tier 1 / FR niveau 1 (doit être 0)
  6. contrat de profil (--profile) : Interdits absents, plafonds FRÉQUENCE
     des signatures respectés, budgets du bloc `gate` appliqués

Usage : python3 gate.py texte.txt [--fr] [--contrast-budget N] [--json]
                                  [--profile humanizer-context.md] [--voice NOM]
        cat texte.txt | python3 gate.py -
Sortie 0 = conforme, 1 = violations. Heuristique assumée : ce script est
un garde-fou contre l'auto-notation, pas un juge littéraire.

Le check 6 lit, dans le bloc `## Voice: <nom>` du fichier de profil, un bloc
fencé ```json gate``` émis par `-empreinte` (références/empreinte.md) :
  {"dashes_max": 0, "contrast_budget": 2, "kicker_ratio_max": 0.4,
   "interdits": ["en conclusion"], "signatures": [{"motif": "…", "max": 1}]}
Les champs absents gardent les défauts du gate. `max` d'une signature =
occurrences maximales dans le texte évalué (plafond FRÉQUENCE, pas cible).
"""
import argparse, json, math, re, sys, unicodedata

# Constantes calibrées sur le corpus d'incident du 12/08/2026 (un mail commercial
# de ~900 mots qui devait échouer, trois contrôles humains qui devaient passer),
# rejouables via evals/traps.json. Pas de nombre magique (loi d'Ousterhout) :
#   contraste 1/200 mots  -> échelle d'un profil-auteur mesuré (1-2 par texte de 200-350 mots)
#   kicker <= 9 mots      -> seuil où le mail fautif sort à 0.28 et les contrôles à 0
#   ratio 0.25            -> 1 atterrissage autorisé par 4 paragraphes (P54)
#   fenêtre de 4 phrases  -> taille du cluster réellement observé (paragraphe Step 0)
#   plancher 5 paragraphes-> sous 5, le ratio mesure une ligne de clôture, pas une cadence
#   masque citations 300c -> couvre une réplique citée sans avaler un paragraphe entier

TIER1_EN = ["delve", "tapestry", "testament", "underscore", "multifaceted",
            "realm", "interplay", "it's worth noting", "it's important to note",
            "in today's"]
TIER1_FR = ["incontournable", "plonger dans", "plongeons", "au cœur de", "au coeur de",
            "à l'ère de", "dans un monde où", "dans un monde ou", "force est de constater",
            "il convient de noter", "il est important de souligner", "s'impose comme",
            "témoigne de", "temoigne de", "ne se limite pas à", "va bien au-delà de",
            "révolutionner", "revolutionner", "un enjeu majeur", "un levier puissant"]

SUBORDINATORS = {"before", "after", "because", "while", "when", "if", "unless", "until",
                 "avant", "après", "apres", "parce", "pendant", "quand", "si", "sauf"}

CONTRAST_EN = [
    re.compile(r"\bnot\s+(?:only|just|merely|simply)\b", re.I),
    re.compile(r"\bnot\s+because\b", re.I),
    re.compile(r"^not\s+an?\b.*?,\s*(?:just|but)\b", re.I),
    re.compile(r",\s*not\s+(?:an?\s+|the\s+|to\s+)?[\w'][^,;:]*[.!?]?$", re.I),
]
CONTRAST_FR = [
    re.compile(r"\bnon\s+pas\b.*\bmais\b", re.I),
    re.compile(r"\bce n['’]est pas\b.*\bc['’]est\b", re.I),
    re.compile(r",\s*pas\s+(?:un|une|le|la|les|de|d['’])\s*[\w'][^,;:]*[.!?]?$", re.I),
    re.compile(r"\bpas\s+(?:seulement|juste)\b", re.I),
]
FLIP_NEXT = re.compile(r"^(?:I'm|I am|It's|It is|That's|This is|C'est|Je suis)\b", re.I)
SOFT_EN = re.compile(r"\brather than\b|\binstead of\b", re.I)
SOFT_FR = re.compile(r"\bplutôt que\b|\bau lieu de\b", re.I)


def mask_quotes(t):
    return re.sub(r'"[^"\n]{1,300}"|«[^»\n]{1,300}»|“[^”\n]{1,300}”', ' "…" ', t)


def paragraphs(t):
    return [b.strip() for b in re.split(r"\n\s*\n", t) if b.strip()]


def is_header(par):
    return not re.search(r"[.!?]", par) and len(par.split()) <= 10


def sentences(par):
    parts = re.split(r"(?<=[.!?])\s+(?=[\"«“A-ZÀ-Ý0-9])", par.replace("\n", " "))
    return [x.strip() for x in parts if x.strip()]


def words(s):
    return re.findall(r"[\w'’%$€-]+", s, re.UNICODE)


def is_fragment(sent):
    w = [x.lower().strip(".,!?:;\"'«»") for x in words(sent)]
    if not w or sent.rstrip().endswith(":"):
        return False
    if w[0] in SUBORDINATORS and len(w) <= 5:
        return True
    verbish = {"is", "are", "was", "were", "be", "am", "do", "does", "did", "has", "have",
               "had", "can", "will", "get", "got", "go", "keep", "sign", "pay", "run",
               "stop", "works", "worked", "est", "sont", "a", "ont", "fait", "va", "peut"}
    return len(w) <= 4 and not (set(w) & verbish)


def load_profile_gate(path, voice=None):
    """Extrait le bloc ```json gate``` d'un profil ## Voice: dans humanizer-context.md.

    voice=None : premier profil trouvé. Retourne {} si fichier ou bloc absents
    (le gate tourne alors avec ses défauts, et le signale)."""
    try:
        doc = open(path, encoding="utf-8").read()
    except OSError:
        return {"_error": f"profil introuvable: {path}"}
    blocks = re.split(r"(?m)^## Voice:\s*", doc)[1:]
    for b in blocks:
        name = b.split("\n", 1)[0].strip()
        if voice and name.lower() != voice.lower():
            continue
        m = re.search(r"```json gate\n(.*?)```", b, re.S)
        if not m:
            return {"_error": f"profil '{name}' sans bloc ```json gate``` (empreinte v3 requis)"}
        try:
            cfg = json.loads(m.group(1))
        except ValueError as e:
            return {"_error": f"bloc gate du profil '{name}' illisible: {e}"}
        cfg["_voice"] = name
        return cfg
    return {"_error": f"aucun profil{' ' + voice if voice else ''} dans {path}"}


def analyze(text, fr=False, contrast_budget=None, kicker_ratio_max=0.25, profile=None):
    text = unicodedata.normalize("NFC", text)
    masked = mask_quotes(text)
    nwords = len(words(masked))
    if nwords < 40:
        return {"error": "sample too short (<40 words), gate refuses to judge", "words": nwords}

    dashes = masked.count("\u2014") + masked.count("\u2013")
    low = masked.lower()
    tier1_hits = sorted({t for t in (TIER1_FR if fr else TIER1_EN) if t in low})

    pats = CONTRAST_FR if fr else CONTRAST_EN
    soft_rx = SOFT_FR if fr else SOFT_EN
    contrast, soft, kickers, runs, clusters = [], 0, [], [], []
    body_pars, run = 0, 0

    for par in paragraphs(masked):
        if is_header(par):
            continue
        body_pars += 1
        sents = sentences(par)
        flags = []
        for i, s in enumerate(sents):
            fam = set()
            if "\u2014" in s or "\u2013" in s:
                fam.add("dash")
            if any(rx.search(s) for rx in pats):
                fam.add("contrast")
            if " not " in f" {s.lower()} " and i + 1 < len(sents) and FLIP_NEXT.search(sents[i + 1]):
                fam.add("contrast")
            if is_fragment(s):
                fam.add("fragment")
            if any(t in s.lower() for t in (TIER1_FR if fr else TIER1_EN)):
                fam.add("tier1")
            if fam & {"contrast"}:
                contrast.append(s[:70])
            soft += len(soft_rx.findall(s))
            flags.append(fam)
        # clusters : fenêtre de 4 phrases intra-paragraphe (ou tout le ¶ si <=4)
        span = max(1, len(sents) - 3) if len(sents) > 4 else 1
        width = 4 if len(sents) >= 4 else len(sents)
        for i in range(span):
            window = flags[i:i + width]
            fams = set().union(*window)
            hits = sum(len(f) for f in window)
            if len(fams) >= 2 or hits >= 3:
                clusters.append(" | ".join(x[:45] for x in sents[i:i + width]))
                break
        # kicker : dernière phrase courte
        if sents and len(words(sents[-1])) <= 9:
            kickers.append(sents[-1])
            run += 1
            runs.append(run)
        else:
            run = 0

    # dédoublonner les contrastes comptés deux fois sur la même phrase
    contrast = list(dict.fromkeys(contrast))

    # check 6 : le contrat du profil ajuste les plafonds et ajoute ses contraintes
    profile = profile or {}
    prof_viol = []
    if profile.get("_error"):
        prof_viol.append(f"profile: {profile['_error']}")
    dashes_max = int(profile.get("dashes_max", 0))
    if profile.get("contrast_budget") is not None and contrast_budget is None:
        contrast_budget = int(profile["contrast_budget"])
    if profile.get("kicker_ratio_max") is not None:
        kicker_ratio_max = float(profile["kicker_ratio_max"])
    # Comme les checks 1-5 : les citations sont masquées (un interdit CITÉ n'est
    # pas une violation), et le comptage respecte les frontières de mots.
    low_all = masked.replace("’", "'").lower()

    def count_bounded(needle):
        needle = str(needle).replace("’", "'").lower()
        return len(re.findall(r"\b" + re.escape(needle) + r"\b", low_all)) if needle else 0

    for interdit in profile.get("interdits", []):
        c = count_bounded(interdit)
        if c:
            prof_viol.append(f"interdit présent: « {interdit} » ×{c}")
    signatures = []
    for sig in profile.get("signatures", []):
        cap = int(sig.get("max", 1))
        c = count_bounded(sig.get("motif", ""))
        signatures.append({"motif": sig.get("motif"), "count": c, "max": cap})
        if c > cap:
            prof_viol.append(f"signature au-delà du plafond FRÉQUENCE: « {sig.get('motif')} » ×{c} > {cap}")

    budget = contrast_budget if contrast_budget is not None else max(1, math.ceil(nwords / 200))
    kr = len(kickers) / body_pars if body_pars else 0
    longest_run = max(runs) if runs else 0

    viol = []
    if dashes > dashes_max:
        cap_txt = "0, signature included" if not dashes_max else f"plafond profil {dashes_max}"
        viol.append(f"dashes={dashes} (must be {cap_txt})")
    if len(contrast) > budget:
        viol.append(f"contrast={len(contrast)} > budget={budget}")
    if kr > kicker_ratio_max and body_pars >= 5:
        viol.append(f"kicker_ratio={kr:.2f} > {kicker_ratio_max}")
    if longest_run > 1:
        viol.append(f"kicker_run={longest_run} > 1")
    if clusters:
        viol.append(f"clusters={len(clusters)}")
    if tier1_hits:
        viol.append(f"tier1={tier1_hits}")
    viol.extend(prof_viol)

    return {"words": nwords, "body_paragraphs": body_pars, "dashes": dashes,
            "contrast_hard": len(contrast), "contrast_budget": budget,
            "contrast_samples": contrast[:8], "soft_contrast": soft,
            "kickers": len(kickers), "kicker_ratio": round(kr, 2),
            "kicker_longest_run": longest_run, "kicker_samples": kickers[:6],
            "clusters": len(clusters), "cluster_samples": clusters[:4],
            "tier1": tier1_hits,
            "profile_voice": profile.get("_voice"), "profile_signatures": signatures,
            "violations": viol, "pass": not viol}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--fr", action="store_true")
    ap.add_argument("--contrast-budget", type=int, default=None)
    ap.add_argument("--kicker-ratio", type=float, default=0.25)
    ap.add_argument("--profile", default=None,
                    help="humanizer-context.md contenant le profil (check 6)")
    ap.add_argument("--voice", default=None, help="nom du profil à charger")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    text = sys.stdin.read() if a.file == "-" else open(a.file, encoding="utf-8").read()
    prof = load_profile_gate(a.profile, a.voice) if a.profile else None
    r = analyze(text, fr=a.fr, contrast_budget=a.contrast_budget,
                kicker_ratio_max=a.kicker_ratio, profile=prof)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=1))
    elif "error" in r:
        print(r["error"])
    else:
        print(f"words={r['words']}  dashes={r['dashes']}  contrast={r['contrast_hard']}/{r['contrast_budget']}"
              f"  kickers={r['kickers']}/{r['body_paragraphs']} (run {r['kicker_longest_run']})"
              f"  clusters={r['clusters']}  tier1={len(r['tier1'])}")
        for v in r["violations"]:
            print("  VIOLATION:", v)
        print("PASS" if r["pass"] else "FAIL")
    sys.exit(0 if r.get("pass") else 1)


if __name__ == "__main__":
    main()
