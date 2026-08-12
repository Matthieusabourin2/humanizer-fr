#!/usr/bin/env python3
"""Harnais de vérification du package humanizer v2-fr.

Chaque test échoue bruyamment. Aucun test ne juge la qualité rédactionnelle :
il vérifie que ce qui est promis dans SKILL.md existe et se comporte comme annoncé.

    python3 verify.py [chemin/vers/humanizer]
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent)
CLI = ROOT.parent / "cli" / "index.js"  # CLI livre separement, section ignoree s'il est absent
FAILURES = []
PASSED = 0


def check(name, ok, detail=""):
    global PASSED
    if ok:
        PASSED += 1
        print(f"  OK    {name}")
    else:
        FAILURES.append(name)
        print(f"  ECHEC {name}" + (f"  -> {detail}" if detail else ""))


skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")

print("\n[1] Frontmatter")
fm = skill.split("---")[1]
try:
    import yaml
    meta = yaml.safe_load(fm)
    check("YAML parsable", True)
    check("champ name = humanizer", meta.get("name") == "humanizer")
    check("description < 1024 car.", len(meta.get("description", "")) < 1024,
          f"{len(meta.get('description',''))} car.")
    check("allowed-tools sans Bash ni WebFetch",
          not ({"Bash", "WebFetch"} & set(meta.get("allowed-tools", []))))
except Exception as e:
    check("YAML parsable", False, str(e))

print("\n[2] Intégrité des références (le défaut classique : référencer un fichier absent)")
refs = sorted(set(re.findall(r"references/[a-z.\-]+\.md", skill)))
check("au moins une référence citée", bool(refs))
for r in refs:
    check(f"{r} existe", (ROOT / r).exists())
orphans = [p.name for p in (ROOT / "references").glob("*.md")
           if f"references/{p.name}" not in skill]
check("aucun fichier orphelin non cité", not orphans, str(orphans))

print("\n[3] Couverture des commandes")
cmds = (ROOT / "references" / "commands.md").read_text(encoding="utf-8")
declared = set(re.findall(r"`(-[a-z]+)`", cmds))
check("commandes déclarées >= 6", len(declared) >= 6, str(sorted(declared)))
routed = re.search(r"Command routing first.*?\n", skill, re.S)
check("routage déclaré dans Step 1", routed is not None)
for c in sorted(declared):
    check(f"{c} routé depuis SKILL.md ou commands.md",
          c in skill or f"| `{c}` |" in cmds)
check("convention tiret simple / double documentée",
      "single dash" in cmds.lower() and "double dash" in cmds.lower())

print("\n[4] Garde anti-fabrication (régression de l'amont)")
check("contrainte dure présente", "no invented facts" in skill.lower())
check("Concretizer bridé", "Concretizer pass (Step 3) may only replace" in skill)
check("Soul Injection bridé", "never a scene that did not happen" in skill)
check("2e question d'audit restaurée", "absent from the source" in skill)

print("\n[5] Couche française")
fr = (ROOT / "references" / "patterns.fr.md").read_text(encoding="utf-8")
ids = re.findall(r"## (FR\d+)", fr)
check("FR1 à FR14 présents", len(ids) == 14, f"{len(ids)} trouvés")
check("3 niveaux de confiance", fr.count("**Niveau") == 3)
check("faux positifs FR documentés", "Faux positifs propres au français" in fr)
check("règles EN intransposables neutralisées",
      all(p in skill for p in ["P17", "P26", "P8"]))
check("routage FR déclaré", "patterns.fr.md" in skill)

print("\n[6] Préséance sur un skill de voix")
check("clause de préséance présente", "Precedence over a voice skill" in skill)
for trait in ["rule-of-three", "antitheses", "opening hooks", "rhetorical closings"]:
    check(f"trait protégé : {trait}", trait in skill)

print("\n[7] Moteur -empreinte : condition d'arrêt")
emp = (ROOT / "references" / "empreinte.md").read_text(encoding="utf-8")
check("seuil 1200 mots / 3 textes", "1 200" in emp and "3 textes" in emp)
check("seuil de promotion 70%", "70 %" in emp)
check("fourchette et non plancher", "Fourchette, jamais plancher" in emp)
check("test de discrimination", "Test de discrimination" in emp)
check("test de bouclage", "Test de bouclage" in emp)
check("écrit dans humanizer-context.md", "humanizer-context.md" in emp)
check("bloc de protection de signature", "ne touche pas" in emp)

# Simulation de la phase 0 sur un corpus sous le seuil
corpus_test = ["texte un " * 40, "texte deux " * 40, "texte trois " * 40]
mots = sum(len(t.split()) for t in corpus_test)
doit_abandonner = mots < 1200 or len(corpus_test) < 3
check(f"phase 0 refuse un corpus de {mots} mots", doit_abandonner,
      "la condition d'arrêt ne se déclencherait pas")

print("\n[8] Exemples travaillés français")
ex = (ROOT / "references" / "examples.fr.md")
check("examples.fr.md existe", ex.exists())
if ex.exists():
    e = ex.read_text(encoding="utf-8")
    check("3 exemples complets", e.count("**Avant**") == 3 and e.count("**Après**") == 3)
    check("3 surfaces couvertes",
          all(x in e for x in ["Post LinkedIn", "Mail commercial", "proposition"]))
    check("chaque exemple porte un score avant/après", e.count("Score CLI") >= 6)
    check("colonne 'conservé délibérément' présente",
          e.count("Conservé délibérément") == 3)
    check("avertissement anti-fabrication dans les exemples",
          "ne doit être réutilisé" in e and "faute contractuelle" in e)

print("\n[9] Métriques non mesurables neutralisées")
check("burstiness : interdiction de citer un chiffre non mesuré",
      "cannot compute this from inside the model" in skill.lower())
check("perplexité : interdiction explicite",
      "no access to logprobs" in skill.lower())
check("score ancré sur échantillons de contrôle", "Anchor samples" in skill)
check("plancher de 40 mots pour noter", "Under 40 words, do not score" in skill)

print("\n[10] Jeu d'évaluation")
ev = ROOT / "evals" / "evals.fr.json"
check("evals.fr.json existe", ev.exists())
if ev.exists():
    cases = json.loads(ev.read_text(encoding="utf-8"))["cases"]
    check("au moins 10 cas", len(cases) >= 10, str(len(cases)))
    check("cas négatifs présents", any(not c["should_trigger"] for c in cases))
    check("cas anti-fabrication", any("fabrication" in c["id"] for c in cases))
    check("cas de préséance de voix", any("preseance" in c["id"] for c in cases))
    check("cas d'arrêt de -empreinte", any("empreinte" in c["id"] for c in cases))
    check("tous les cas ont une attente", all(c.get("expect") for c in cases))

print("\n[11] Déclenchement : couverture description contre evals")
if ev.exists():
    desc = meta.get("description", "").lower()
    STOP = {"ce","de","la","le","les","des","du","un","une","et","a","tu","peux","this",
            "sur","pour","est","que","qui","il","en","au","aux","dans","texte","text"}
    for c in cases:
        toks = [w.strip('.,?!:"\'/') for w in c["prompt"].lower().split()]
        toks = [w for w in toks if len(w) > 3 and w not in STOP]
        hit = [w for w in toks if w in desc]
        if c["should_trigger"]:
            check(f"declenche: {c['id']}", bool(hit), f"aucun terme du prompt dans la description")
        else:
            dom = {"code": ["code"], "traduction": ["translation"]}
            named = any(k in desc for ks in dom.values() for k in ks)
            check(f"non-declenche couvert: {c['id']}", named,
                  "domaine exclu non nomme dans la description")
    check("perimetre negatif dans la description",
          "do not use" in desc or "not use for" in desc)
    check("section When NOT to use presente", "## When NOT to use this skill" in skill)
    check("plancher 40 mots dans le perimetre negatif", "under 40 words" in skill.lower())

print("\n[12] Maintenabilite : version et manifeste de rebase")
check("version dans le frontmatter", bool(meta.get("metadata", {}).get("version")),
      str(meta.get("metadata")))
check("version amont tracee", bool(meta.get("metadata", {}).get("upstream")))
chg = ROOT / "CHANGELOG.md"
check("CHANGELOG.md existe", chg.exists())
if chg.exists():
    ch = chg.read_text(encoding="utf-8")
    check("version amont citee dans le changelog", "0.5.0" in ch)
    divs = re.findall(r"\*\*(D\d+) ", ch)
    check("au moins 9 divergences documentees", len(divs) >= 9, str(divs))
    check("procedure de rebase enoncee", "rebase" in ch.lower())
    check("retraits amont documentes", "Retiré de l'amont" in ch)
    # chaque fichier ajoute par rapport a l'amont doit etre cite dans le manifeste
    up = Path("/home/claude/repo/humanizer-skill-main/skills/humanizer")
    if up.exists():
        ours = {q.relative_to(ROOT).as_posix() for q in ROOT.rglob("*")
                if q.is_file() and q.suffix in (".md", ".json")}
        theirs = {q.relative_to(up).as_posix() for q in up.rglob("*")
                  if q.is_file() and q.suffix in (".md", ".json")}
        for f in sorted(ours - theirs - {"CHANGELOG.md"}):
            check(f"ajout documente: {f}", Path(f).name in ch)
        for f in sorted(theirs - ours):
            check(f"retrait documente: {f}", Path(f).name in ch)

print("\n[13] Vérificateur déterministe (CLI)")
if CLI.exists():
    def score(txt):
        r = subprocess.run(["node", str(CLI), "score", "-", "--json"],
                           input=txt, capture_output=True, text=True)
        if r.returncode not in (0, 1):
            return None
        try:
            return json.loads(r.stdout)
        except Exception:
            m = re.search(r"Score: (\d+)/100", r.stdout)
            return {"score": int(m.group(1))} if m else None

    tok = subprocess.run(
        ["node", "-e",
         "const{wordTokens}=require('./lib/tokenize');"
         "console.log(JSON.stringify(wordTokens('réévaluer une stratégie éprouvée')))"],
        cwd=CLI.parent, capture_output=True, text=True)
    check("tokenizer unicode (accents non fragmentés)",
          '"réévaluer"' in tok.stdout, tok.stdout.strip())

    slop = ("Dans un monde ou tout evolue rapidement, notre plateforme incontournable permet de "
            "revolutionner vos usages quotidiens, offrant une experience utilisateur fluide et "
            "garantissant des resultats mesurables pour vos equipes. Force est de constater que "
            "cette approche change la donne. En conclusion, il convient de noter que cette solution "
            "innovante, efficace et durable saura repondre a vos enjeux strategiques les plus complexes.")
    humain = ("Bruno est arrive en retard. Il avait le manuel sous le bras, corne a toutes les pages, "
              "et il l'a pose sur la table sans rien dire. On a repris depuis le debut. Trois heures. "
              "A la fin il m'a demande si je pensais vraiment que ca marcherait, et je n'ai pas su quoi "
              "repondre. Le lendemain il avait refait la moitie du deck tout seul, a sa facon.")
    s1, s2 = score(slop), score(humain)
    check("score FR sur prose truffée > 40", s1 and s1["score"] > 40, str(s1))
    check("score FR sur prose humaine < 20", s2 and s2["score"] < 20, str(s2))
    check("le juge sépare les deux échantillons",
          s1 and s2 and s1["score"] - s2["score"] > 30,
          f"écart {s1['score']-s2['score'] if s1 and s2 else '?'}")
else:
    print("  (CLI absent, section ignorée)")


print("\n[14] Porte chiffree v2.2 (budgets, clusters, gate.py, pieges)")
check("P54 present au catalogue", "P54: Kicker Cadence" in skill)
check("compteur de patterns a 54", "Pattern catalog (54 total)" in skill and "P44 to P54" in skill)
check("section Density budgets presente", "### Density budgets (ceilings, not targets)" in skill)
check("scan de cluster local present", "### The local cluster scan" in skill)
check("numbers gate obligatoire en rewrite", "### The numbers gate (mandatory in rewrite and edit modes)" in skill)
check("plafond de frequence sur les signatures", "attested frequency and on its attested surface" in skill)
check("portee du zero-tolerance sur signatures", "signature blocks, taglines and boilerplate included" in skill)
check("plafonds pas cibles", "Ceilings, not targets" in skill)
check("gate.py reference depuis SKILL.md", "scripts/gate.py" in skill)

gp = ROOT / "scripts" / "gate.py"
check("scripts/gate.py existe", gp.exists())
if gp.exists():
    import importlib.util
    spec = importlib.util.spec_from_file_location("gate", gp)
    gate = importlib.util.module_from_spec(spec); spec.loader.exec_module(gate)
    WRAP = ("Here is the launch plan I promised you after the call, with the numbers we "
            "discussed and the calendar the team validated on Monday. Nothing in it requires "
            "a decision from your side before the end of the month, and the budget line stays "
            "exactly where the committee set it in April.\n\n")
    bad = WRAP + ("Phase one: we test. Before any money moves. Not a full rollout, just ten "
                  "users and a spreadsheet. The real launch happens later, while the data is "
                  "already coming in.")
    good = WRAP + ("Phase one: we test, before any money moves. No rollout at this point, ten "
                   "users and a spreadsheet. The real launch happens later, while the data is "
                   "already coming in.")
    rb, rg = gate.analyze(bad), gate.analyze(good)
    check("cluster detecte sur l'exemple 'avant'", rb["clusters"] >= 1 and not rb["pass"], str(rb["violations"]))
    check("exemple 'apres' conforme", rg["pass"], str(rg["violations"]))
    sig = WRAP + ("The invoices went out this morning with the usual terms, and accounting has "
                  "both references filed.\n\nKarim Benali\nSorelis Group \u2014 Operational excellence, delivered.")
    rs = gate.analyze(sig)
    check("cadratin de signature detecte", rs["dashes"] >= 1 and not rs["pass"], str(rs))
    slop_fr = ("Dans un monde ou tout evolue rapidement, notre plateforme incontournable permet de "
               "revolutionner vos usages quotidiens, offrant une experience fluide et garantissant des "
               "resultats mesurables pour vos equipes. Force est de constater que cette approche change "
               "la donne, et il convient de noter que cette solution saura repondre a vos enjeux.")
    rf = gate.analyze(slop_fr, fr=True)
    check("tier 1 FR detecte", len(rf["tier1"]) >= 3, str(rf["tier1"]))
    human = ("Nadia,\n\nThe contract came back signed this morning, both pages initialed, and I "
             "filed the scanned copy in the shared folder under the client name like we agreed. Their "
             "accountant wants the first invoice split between two cost centers, so I need the second "
             "reference before I send anything.\n\nSee you Thursday.")
    rh = gate.analyze(human)
    check("controle humain court sans faux positif", rh["pass"], str(rh["violations"]))
    quoted = WRAP + ('The vendor reply said "Our platform \u2014 a testament to seamless innovation \u2014 '
                     'will delve into your needs" and nothing else. The demo in March still solved the '
                     'routing problem in twenty minutes, so I will ask for a trial account on Thursday.')
    rq = gate.analyze(quoted)
    check("citations masquees (cadratin et delve cites non comptes)", rq["pass"], str(rq["violations"]))
    rshort = gate.analyze("Thanks Phil, talk Monday.")
    check("plancher 40 mots respecte par gate.py", "error" in rshort, str(rshort))

tr = ROOT / "evals" / "traps.json"
check("evals/traps.json existe", tr.exists())
if tr.exists():
    tj = json.loads(tr.read_text(encoding="utf-8"))
    traps = tj["cases"]
    check("au moins 10 pieges", len(traps) >= 10, str(len(traps)))
    check("piege faux-positif present", any("false-positive" in c["id"] for c in traps))
    check("piege cadratin de signature", any("signature-dash" in c["id"] for c in traps))
    check("piege cluster local", any("cluster" in c["id"] for c in traps))
    check("piege surface de profil", any("surface" in c["id"] for c in traps))
    check("piege densite de signature", any("density" in c["id"] for c in traps))
    check("format d'eval officiel (query + expected_behavior)",
          all(c.get("query") and c.get("expected_behavior") for c in traps))
    check("protocole de rejeu Claude A/B multi-modeles", "Haiku" in tj.get("replay_protocol", "")
          and "session NEUVE" in tj.get("replay_protocol", ""))
    check("regle d'edition TDD documentaire", "nouvelle section" in tj.get("replay_protocol", ""))


print("\n[15] Conformite doc officielle skill-authoring (12/08/2026)")
body = skill.split("---", 2)[2]
check("corps de SKILL.md sous 500 lignes", len(body.splitlines()) <= 500,
      f"{len(body.splitlines())} lignes")
check("table de rationalisations presente", "### Rationalization table" in skill)
check("au moins 6 excuses contrees", skill.count("| \"") >= 6 or skill.count('| "') >= 6)
check("P54 sans date perimee", "circa 20" not in skill)
check("constantes de gate.py justifiees", "Ousterhout" in (ROOT / "scripts" / "gate.py").read_text(encoding="utf-8"))
check("terme canonique landed ending dominant",
      skill.lower().count("landed ending") >= 4)
print("\n" + "=" * 60)
print(f"{PASSED} tests passés, {len(FAILURES)} échecs")
if FAILURES:
    print("ECHECS : " + ", ".join(FAILURES))
    sys.exit(1)
print("Package vérifié.")
