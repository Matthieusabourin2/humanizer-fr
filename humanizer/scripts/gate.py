#!/usr/bin/env python3
"""Porte chiffrée du humanizer v2.2 : compte ce que le modèle doit montrer.

Checks déterministes 1-5 du numbers gate de SKILL.md :
  1. tirets cadratins + demi-cadratins hors citations (doit être 0)
  2. constructions de contraste dures (famille P9) vs budget
  3. atterrissages de paragraphe (P54) : ratio et plus longue série
  4. fenêtres-cluster de 4 phrases, 2+ familles structurelles distinctes
  5. vocabulaire Tier 1 / FR niveau 1 (doit être 0)

Usage : python3 gate.py texte.txt [--fr] [--contrast-budget N] [--json]
        cat texte.txt | python3 gate.py -
Sortie 0 = conforme, 1 = violations. Heuristique assumée : ce script est
un garde-fou contre l'auto-notation, pas un juge littéraire.
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


def analyze(text, fr=False, contrast_budget=None, kicker_ratio_max=0.25):
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
    budget = contrast_budget if contrast_budget is not None else max(1, math.ceil(nwords / 200))
    kr = len(kickers) / body_pars if body_pars else 0
    longest_run = max(runs) if runs else 0

    viol = []
    if dashes:
        viol.append(f"dashes={dashes} (must be 0, signature included)")
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

    return {"words": nwords, "body_paragraphs": body_pars, "dashes": dashes,
            "contrast_hard": len(contrast), "contrast_budget": budget,
            "contrast_samples": contrast[:8], "soft_contrast": soft,
            "kickers": len(kickers), "kicker_ratio": round(kr, 2),
            "kicker_longest_run": longest_run, "kicker_samples": kickers[:6],
            "clusters": len(clusters), "cluster_samples": clusters[:4],
            "tier1": tier1_hits, "violations": viol, "pass": not viol}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--fr", action="store_true")
    ap.add_argument("--contrast-budget", type=int, default=None)
    ap.add_argument("--kicker-ratio", type=float, default=0.25)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    text = sys.stdin.read() if a.file == "-" else open(a.file, encoding="utf-8").read()
    r = analyze(text, fr=a.fr, contrast_budget=a.contrast_budget, kicker_ratio_max=a.kicker_ratio)
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
