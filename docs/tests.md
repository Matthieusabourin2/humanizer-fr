# Les tests du humanizer-fr

Un skill est de la prose qui prétend gouverner un modèle. Sans tests, cette prose dérive : une section réécrite casse un comportement promis trois versions plus tôt, et personne ne le voit avant l'échec en production. Ce document décrit l'ensemble des tests définis dans ce dépôt, ce que chacun couvre, comment le lancer, et la règle qui gouverne leur évolution.

La suite tient en quatre couches. Aucune ne juge la qualité rédactionnelle : chacune vérifie qu'une promesse précise du paquet existe et se comporte comme annoncé. Depuis la 3.0.0-fr, la détection elle-même est déterministe : `scripts/scan.py` produit le score 0-100 et les patterns mécaniques en moins de 0,1 s, le harnais le teste (section 13), et la [démo en ligne](https://www.catalia.fr/ressources/humanizer) tourne sur le même moteur.

| Couche | Fichier | Ce qu'elle teste | Verdict | Exécution |
|---|---|---|---|---|
| Harnais du paquet | `humanizer/verify.py` | L'intégrité structurelle : tout ce que SKILL.md promet existe | 123 checks, sortie 0/1 | automatique, locale |
| Porte chiffrée | `humanizer/scripts/gate.py` | Une sortie du skill respecte les budgets de densité et le contrat du profil | PASS/FAIL déterministe | automatique, locale |
| Cas de déclenchement | `humanizer/evals/evals.fr.json` | Le skill se déclenche (ou pas) sur les bons prompts | 11 cas, attentes textuelles | rejeu manuel multi-modèles |
| Pièges de régression | `humanizer/evals/traps.json` | Les échecs réels déjà corrigés ne reviennent pas | 13 pièges, protocole A/B | rejeu manuel + gate.py |

Une version publiable de cette documentation existe sous forme de page statique autonome : [`site/tests.html`](../site/tests.html), destinée à être publiée comme ressource sur catalia.fr. Sa maintenance est décrite en fin de document.

---

## 1. `verify.py` : le harnais du paquet

**Ce que c'est.** Un script Python sans dépendance (PyYAML excepté) qui vérifie que le paquet est cohérent avec lui-même. Chaque test échoue bruyamment. Le défaut classique qu'il attrape : référencer un fichier absent, promettre une commande non routée, renuméroter un pattern sans mettre à jour le compteur.

**Lancement :**

```bash
python3 humanizer/verify.py            # depuis la racine du dépôt
python3 verify.py                      # depuis humanizer/
```

Sortie 0 si tout passe, 1 sinon, avec la liste des échecs. État au 13/08/2026 (v3.0.0-fr) : **123 tests passés, 0 échec**.

**Les 15 sections :**

| # | Section | Ce qu'elle garde |
|---|---|---|
| 1 | Frontmatter | YAML parsable, `name: humanizer`, description sous 1 024 caractères, ni Bash ni WebFetch dans `allowed-tools` |
| 2 | Intégrité des références | Chaque `references/*.md` cité dans SKILL.md existe ; aucun fichier orphelin non cité |
| 3 | Couverture des commandes | Au moins 6 commandes déclarées dans `commands.md`, toutes routées depuis SKILL.md, convention tiret simple/double documentée |
| 4 | Garde anti-fabrication | Les quatre verrous anti-invention (contrainte dure, Concretizer bridé, Soul Injection bridée, 2e question d'audit) sont présents mot pour mot |
| 5 | Couche française | FR1 à FR14 présents, 3 niveaux de confiance, faux positifs FR documentés, règles EN intransposables neutralisées, routage FR déclaré |
| 6 | Préséance voix | La clause de préséance existe et protège nommément rule-of-three, antithèses, hooks d'ouverture, clôtures rhétoriques |
| 7 | Moteur `-empreinte` | Seuils (3 textes, 1 200 mots, promotion 70 %), tests de discrimination et de bouclage, condition d'arrêt simulée sur un corpus trop mince |
| 8 | Exemples FR | 3 exemples complets avant/après, 3 surfaces, scores CLI, colonne « conservé délibérément », avertissement anti-fabrication |
| 9 | Métriques non mesurables | Le skill s'interdit de citer burstiness ou perplexité qu'il ne peut pas calculer ; plancher de 40 mots pour noter |
| 10 | Jeu d'évaluation | `evals.fr.json` existe, au moins 10 cas, cas négatifs, anti-fabrication, préséance et `-empreinte` couverts |
| 11 | Déclenchement | Chaque cas d'eval qui doit déclencher a au moins un terme de son prompt dans la description du frontmatter ; le périmètre négatif est nommé |
| 12 | Maintenabilité | Version et amont tracés dans le frontmatter, CHANGELOG en manifeste de rebase (divergences D1–D26, procédure, retraits amont) |
| 13 | Vérificateur déterministe | `scan.py` : tokenizer unicode, routé avant la réécriture dans SKILL.md, sépare prose truffée (> 40) et prose humaine (< 20), détecte FR1/FR5/FR7, mêmes chiffres sur deux passes |
| 14 | Porte chiffrée v2.2 | P54 au catalogue, budgets de densité, scan de cluster, numbers gate obligatoire, et exécution réelle de `gate.py` sur 7 échantillons de contrôle |
| 15 | Conformité skill-authoring | Corps de SKILL.md sous 500 lignes, table de rationalisations, constantes de `gate.py` justifiées, terme canonique dominant |

La section 14 mérite une lecture : elle ne vérifie pas seulement que `gate.py` existe, elle l'importe et le fait tourner sur des échantillons de contrôle (cluster à détecter, cadratin de signature, tier 1 FR, contrôle humain propre, citation à masquer, texte trop court). Si une constante de calibration bouge, ces échantillons cassent.

**Quand le lancer.** Avant chaque commit qui touche `humanizer/`, et systématiquement après un rebase sur l'amont (procédure dans `humanizer/CHANGELOG.md`).

---

## 2. `gate.py` : la porte chiffrée

**Ce que c'est.** Le garde-fou contre l'auto-notation. Le modèle qui vient de réécrire un texte est le plus mal placé pour jurer qu'il est propre ; `gate.py` compte à sa place, de façon déterministe. C'est l'implémentation exécutable du numbers gate de SKILL.md, contrat de profil compris.

**Lancement :**

```bash
python3 humanizer/scripts/gate.py texte.txt            # anglais par défaut
python3 humanizer/scripts/gate.py texte.txt --fr       # catalogue français
cat texte.txt | python3 humanizer/scripts/gate.py -    # depuis stdin
python3 humanizer/scripts/gate.py texte.txt --json     # sortie machine
python3 humanizer/scripts/gate.py texte.txt --profile humanizer-context.md   # + contrat du profil (check 6)
```

Sortie 0 = conforme, 1 = violations (listées une par une).

**Les 6 checks :**

| # | Check | Seuil | Pourquoi ce seuil |
|---|---|---|---|
| 1 | Tirets cadratins et demi-cadratins hors citations | 0, signature comprise | Tell le plus documenté ; l'exemption « mobilier de marque » exige une attestation du profil chargé |
| 2 | Constructions de contraste dures (famille P9) | budget = 1 pour 200 mots | Échelle d'un profil auteur mesuré : 1 à 2 par texte de 200 à 350 mots |
| 3 | Atterrissages de paragraphe (P54, kickers ≤ 9 mots) | ratio ≤ 0,25 et jamais 2 d'affilée | 1 atterrissage autorisé par 4 paragraphes ; le mail fautif de référence sortait à 0,28, les contrôles humains à 0 |
| 4 | Clusters locaux | 0 fenêtre de 4 phrases portant 2+ familles structurelles | Taille du cluster réellement observé dans l'incident de référence |
| 5 | Vocabulaire Tier 1 (EN et FR niveau 1) | 0 occurrence | « delve », « tapestry » / « incontournable », « dans un monde où »… indéfendables en prose humaine |
| 6 | Contrat du profil de voix (`--profile`) | interdits = 0, plafonds à la fréquence attestée, surfaces respectées | La signature d'un auteur est attestée à une fréquence et sur une surface : le check lit le contrat chiffré du bloc `## Voice` et l'applique, citations toujours masquées |

Trois garde-fous d'ingénierie autour de ces comptes :

- **Masquage des citations** : le contenu entre guillemets (droits, français ou typographiques, 300 caractères max) est remplacé avant tout comptage. Un cadratin cité n'est pas un cadratin écrit.
- **Plancher de 40 mots** : sous ce seuil, le script refuse de juger (`sample too short`). Le ratio de kickers n'est jugé qu'à partir de 5 paragraphes : en dessous, il mesurerait une ligne de clôture, pas une cadence.
- **Constantes justifiées** : chaque nombre du script est commenté avec sa provenance (loi d'Ousterhout, pas de nombre magique). Toutes sont calibrées sur le corpus d'incident du 12/08/2026 : un mail commercial d'environ 900 mots qui devait échouer, trois contrôles humains qui devaient passer, rejouables via `traps.json`.

**Ce que la porte n'est pas.** Un juge littéraire. Elle compte ce que le modèle doit montrer, rien de plus. Un texte peut passer la porte et rester médiocre ; il ne peut pas la passer en portant les tics qu'elle compte.

---

## 3. `evals.fr.json` : les cas de déclenchement

**Ce que c'est.** 11 cas qui vérifient que le skill se déclenche sur les bons prompts, ne se déclenche pas sur les mauvais, et fait ce qu'il annonce une fois déclenché. Format : `prompt`, `should_trigger`, `expect` (attente textuelle vérifiable à l'œil).

| id | Vérifie | Attendu |
|---|---|---|
| `fr-trigger-direct` | Déclenchement sur demande explicite FR | Charge `patterns.fr.md`, supprime « dans un monde où » et « crucial », zéro cadratin |
| `fr-trigger-indirect` | Déclenchement sans mot-clé (« on dirait du ChatGPT non ? ») | Se déclenche, demande le texte s'il manque |
| `fr-participes` | Détection FR1 (participes en chapelet) | Coupe la phrase, ne signale pas de tell anglais |
| `fr-faux-positif` | Français normal non signalé | Pronominal, passif et « notamment » isolé passent sans remarque |
| `fr-trop-court` | Plancher de notation | Refuse de scorer sous 40 mots |
| `fr-anti-fabrication` | Garde anti-invention | Aucun chiffre inventé pour « concrétiser » ; dit ce qui manque |
| `fr-preseance-voix` | Préséance d'un skill de marque chargé | Conserve hook nominal et antithèse au lieu de les traiter en P31/P9 |
| `cmd-help` | Routage `-help` | Liste des commandes, aucune réécriture |
| `cmd-empreinte-corpus-court` | Condition d'arrêt `-empreinte` | Exige 3 textes ; sous 1 200 mots, s'arrête sans produire de profil |
| `no-trigger-code` | Cas négatif : code | Ne se déclenche pas |
| `no-trigger-traduction` | Cas négatif : traduction littérale | Ne se déclenche pas |

**Protocole de rejeu.** Manuel, dans une session neuve avec le skill installé (`claude -p "<prompt>"` en Claude Code, nouvelle conversation sur claude.ai), sur **Haiku, Sonnet et Opus** : la sensibilité de déclenchement varie selon le modèle, un cas qui passe sur Opus peut rater sur Haiku. La couverture déclenchement/description est en plus vérifiée statiquement par la section 11 de `verify.py`.

---

## 4. `traps.json` : les pièges de régression

**Ce que c'est.** 13 pièges distillés d'échecs réels : la salve du 12/08/2026 : passe cosmétique sur un mail commercial anglais, cadratin de signature exempté à tort, cluster local invisible dans des totaux globaux propres, contrainte de surface d'un profil ignorée, puis trois échecs de la v3 (scanner court-circuité, plafond de fréquence du profil dépassé, appel à l'action inventé au nom de la voix). Chaque cas suit le format d'eval officiel Anthropic (`query` + `expected_behavior`). Les cas `gate: true` sont vérifiables mécaniquement en passant la sortie à `gate.py`.

| id | gate | Le piège |
|---|---|---|
| `trap-structural-no-dash` | oui | Un texte sans cadratin mais saturé de contrastes et de punchlines ne doit pas être déclaré propre |
| `trap-signature-dash` | oui | Le cadratin d'une ligne de signature est un cadratin ; aucune exemption sans attestation du profil |
| `trap-local-cluster` | oui | 2 familles structurelles en 4 phrases se détectent même quand les totaux globaux passent |
| `trap-surface-profile` | non | Un trait attesté en post ne s'exporte pas dans un mail : la surface fait partie de l'attestation |
| `trap-signature-density` | non | Une signature attestée à 1 par texte ne justifie pas 8 occurrences : la fréquence fait partie de l'attestation |
| `trap-false-positive-human` | oui | Un mail humain concret passe la porte et n'est pas réécrit de force |
| `trap-quoted-ai` | oui | Les tells cités entre guillemets ne sont ni réécrits ni comptés |
| `trap-fabrication` | non | Aucun chiffre inventé pour concrétiser une abstraction (régression D1) |
| `trap-too-short` | oui | Sous 40 mots, refus de noter |
| `trap-zero-punch` | oui | Plafonds, pas cibles : on n'injecte pas de punchlines pour « humaniser » un texte plat |
| `trap-scan-first` | non | Le modèle exécute `scan.py` avant toute analyse et cite son score et ses patterns tels quels |
| `trap-profile-frequence` | oui | Une formule signature plafonnée à 1 par le contrat du profil ne survit pas en 3 exemplaires |
| `trap-voice-fabrication` | non | Aucun appel à l'action ni engagement inventé au nom de la voix de l'auteur |

**Protocole de rejeu A/B.** Ne jamais faire noter le skill par l'instance qui vient de l'éditer. Rejouer chaque `query` dans une session neuve, sur Haiku, Sonnet et Opus, vérifier chaque assertion d'`expected_behavior`, puis passer la sortie à `gate.py` quand `gate: true`.

**La règle d'édition (TDD documentaire).** Toute nouvelle section de SKILL.md exige un piège dans `traps.json` qui échouait sans elle. C'est la règle qui empêche le skill de grossir en prose décorative : si on ne peut pas écrire le piège, la section n'a pas de raison d'exister. Symétriquement, la section 14 de `verify.py` doit référencer toute nouvelle promesse chiffrée.

---

## 5. La page de test : `site/tests.html`

Version publiable de ce document : une page statique autonome (un seul fichier, zéro dépendance, zéro tracking), aux couleurs Catalia, inspirée de la page du skill amont ([humanizer-skill.vercel.app](https://humanizer-skill.vercel.app/)). Elle est destinée à être publiée comme ressource sur [catalia.fr](https://www.catalia.fr).

**Contrat de la page :**

- Elle documente les quatre couches ci-dessus avec les mêmes chiffres. Si un chiffre change (nombre de tests, de cas, de pièges, seuils de la porte), la page se met à jour dans le même commit que le code : c'est le pendant visuel de la règle TDD documentaire.
- Sa prose française passe sa propre porte : `gate.py --fr` sort PASS sur le texte de la page. Une ressource qui documente une porte chiffrée ne peut pas se permettre de la rater.
- 100 % statique, identique pour tous les visiteurs, aucun formulaire, aucun paramètre d'URL porteur d'identité (même règle que les autres pages ressources du site).

**Vérification locale :**

```bash
# extraire le texte et le passer à la porte
python3 - <<'EOF'
import re, html, subprocess
t = open("site/tests.html", encoding="utf-8").read()
t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", t, flags=re.S)
t = re.sub(r"<[^>]+>", " ", t)
subprocess.run(["python3", "humanizer/scripts/gate.py", "-", "--fr"],
               input=html.unescape(t), text=True)
EOF
```

---

## Ajouter un test : la règle en trois lignes

1. **Un échec réel d'abord.** Un piège naît d'un échec observé, pas d'une hypothèse. Le distiller dans `traps.json` au format `query` + `expected_behavior`, avec `gate: true` si la sortie est vérifiable mécaniquement.
2. **La promesse ensuite.** Écrire ou modifier la section de SKILL.md qui corrige l'échec, et ajouter le check correspondant dans `verify.py` (section 14 ou 15) pour que la promesse ne puisse plus disparaître silencieusement.
3. **Rejouer.** `verify.py` doit sortir 0, le piège doit passer en session neuve sur les trois modèles, et si la page `site/tests.html` cite un chiffre devenu faux, la corriger dans le même commit.
