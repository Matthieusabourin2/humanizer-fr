# CHANGELOG

## 2.3.0-fr — 12 août 2026

Alignement sur les méthodologies de référence, vérifiées en ligne le jour même : le guide officiel Anthropic « Skill authoring best practices » (platform.claude.com) et la méthodologie TDD documentaire de superpowers (obra/writing-skills). Cinq écarts retenus, trois pratiques écartées avec motif.

**D17 — Table de rationalisations (`SKILL.md`, garde-fous).** Pattern superpowers pour les skills de discipline : capturer les excuses exactes que l'agent produit sous pression et leur opposer la réponse. Les six lignes de la table sont les six justifications réellement utilisées le 12/08 pour laisser passer des violations (« lockup de marque », « c'est sa signature », « chaque dispositif se défend », « la rhétorique est trop efficace », « le genre l'exige », « les cadratins sont partis »).

**D18 — Constantes justifiées (`scripts/gate.py`).** Loi d'Ousterhout, exigence explicite de la doc officielle : aucun nombre magique. Chaque seuil (contraste 1/200, kicker ≤ 9 mots, ratio 0.25, fenêtre de 4, plancher de 5 paragraphes, masque 300 c.) est annoté avec sa dérivation empirique sur le corpus d'incident, et la consigne de recalibrage passe par evals/traps.json, pas par une impression.

**D19 — `evals/traps.json` au format d'éval officiel.** Champs `query` + `expected_behavior` (assertions vérifiables une à une), protocole de rejeu Claude A/B : jamais noté par l'instance qui vient d'éditer le skill, session neuve, sur Haiku, Sonnet et Opus. Règle d'édition TDD documentaire de superpowers inscrite dans le protocole : toute nouvelle section du SKILL.md exige un piège qui échouait sans elle.

**D20 — Terminologie et péremption (`SKILL.md`).** Terme canonique unique « landed ending » (kicker lié une fois à la définition de P54), suppression de la mention datée « circa 2025-2026 » conformément à la règle anti-information périssable de la doc.

**D21 — Corps sous 500 lignes.** Compression des ajouts 2.2 (budgets, cluster scan, numbers gate, préséance) : corps de SKILL.md à 493 lignes hors frontmatter, sous le plafond officiel de 500.

Écarté, avec motif : renommage en gérondif (« humanizing-text ») — casserait /humanizer, l'historique et la mémoire musculaire, la doc classe les noms orientés action comme alternative acceptable ; éclatement supplémentaire en fichiers de référence — la porte chiffrée doit rester non-esquivable dans le corps, l'externaliser recréerait l'échec d'origine ; réécriture de la description — le déclenchement n'a jamais été le mode de défaillance observé.

Vérification : python3 verify.py . — 114 tests verts.

Publication publique : profil de voix de l'auteur exclu du paquet, exemples et échantillons anonymisés, défaut de `--voice` généralisé au profil embarqué s'il existe.

## 2.2.0-fr — 12 août 2026

Origine : incident du même jour, humanisation d'un mail commercial EN. Trois échecs en une session. Passe cosmétique : cadratins traités mais moteur de contraste (12 occurrences) et cadence de punchlines (18 paragraphes sur 24) conservés. Cadratin de signature exempté au titre d'un « lockup de marque » que rien n'atteste. Cluster local de trois dispositifs en quatre phrases invisible aux comptages globaux, et contrainte de surface du profil (R-08 : gradation en post uniquement, jamais en mail) ignorée. Cause racine commune : vérification qualitative auto-notée, sans chiffres.

**D12 — Budgets de densité et scan de cluster local (`SKILL.md`).** Les tells structurels sont des problèmes de dosage : chaque instance peut se défendre pendant que le total est machine. Budgets par défaut (contraste 1/200 mots, punchlines 1/4 paragraphes jamais 2 de suite, cadratins 0, Tier 1 zéro), plafonds et non cibles. Fenêtre de 4 phrases intra-paragraphe : 2 familles structurelles distinctes ou 3 occurrences = cluster à réécrire localement, même si chaque élément était individuellement justifié. Exemple travaillé avant/après inclus.

**D13 — P9 élargi, P54 ajouté (`SKILL.md`).** P9 compte désormais toute la famille de contraste sur un seul budget (not only, not just, not because, X-not-Y final, Not-a-X-just-Y, bascule en deux phrases). P54 « Kicker Cadence » : la punchline de fin de paragraphe systématique, signature du drafting assisté 2025-2026. Catalogue 53 → 54.

**D14 — Portée du zéro-tolérance et plafond des signatures (`SKILL.md`).** Zéro cadratin s'applique à chaque caractère de la sortie : objets, en-têtes, blocs de signature, baselines. Aucune exemption « mobilier de marque » sans attestation du profil chargé. Préserver une signature d'auteur = la préserver à sa FRÉQUENCE attestée et sur sa surface attestée ; l'efficacité rhétorique n'est jamais un critère de conservation, la paternité attestée oui.

**D15 — `scripts/gate.py`.** Porte chiffrée déterministe des checks 1-5 du numbers gate (cadratins, contraste vs budget, punchlines et série max, clusters, Tier 1 EN/FR), masquage des citations, plancher 40 mots, garde-fou ratio sur textes courts (< 5 paragraphes). Sortie 0/1. Ses chiffres priment sur le comptage du modèle ; sans environnement d'exécution, comptage manuel obligatoire et montré. Le numbers gate est obligatoire en modes rewrite et edit : une vérification qui ne produit pas de chiffres n'a pas eu lieu.

**D16 — `evals/traps.json` + `verify.py` section [14].** Dix pièges de régression distillés des échecs réels (structurel sans cadratin, cadratin de signature, cluster local, surface de profil, densité de signature, faux positif humain, citations, anti-fabrication, plancher 40 mots, zéro-punch à ne pas « punchifier »). verify.py exécute gate.py sur cinq échantillons embarqués et vérifie les promesses du SKILL.md. 106 tests au moment de cette version.


## 2.1.1-fr — 12 août 2026

Itération privée non publiée : profil de voix personnel de l'auteur défini comme voix par défaut. Généralisée dans la 2.3.0 publique : le profil embarqué, s'il existe, est la voix par défaut.

## 2.1.0-fr — 12 août 2026

**D10 — Profils de voix embarqués (`humanizer-context.md`).** SKILL.md charge désormais `humanizer-context.md` aussi depuis le dossier du skill, en plus de la racine du projet (qui garde la priorité pour les voix de même nom). `-voix` liste les profils des deux emplacements ; le contrat de persistance documente l'option embarquée. Aucun profil n'est livré avec le skill : `-empreinte` construit le vôtre depuis votre propre corpus. Version de publication du dépôt public.

## 2.0.0-fr — 11 août 2026

Fork de `Aboudjem/humanizer-skill` 0.5.0 (branche main). Neuf divergences, toutes listées ci-dessous. Ce fichier est le manifeste de rebase : quand l'amont publie une version, réappliquer ces neuf points et relancer `verify.py`.

### Corrections de régression amont

**D1 — Garde anti-fabrication restauré (`SKILL.md`).** L'amont 0.5.0 a supprimé la règle « never invent facts » et la question d'audit associée, présentes en 2.9.1. Deux techniques poussaient activement à l'invention : le Concretizer donnait en exemple de transformer une abstraction en « 900ms à 40ms », et Soul Injection recommandait d'ajouter une scène vécue. Contrainte remise en dur avant les garde-fous, les deux techniques bridées, seconde question d'audit rétablie. Critique sur du texte client.

**D2 — Métriques non mesurables neutralisées (`SKILL.md`).** Burstiness et perplexité étaient présentées comme calculables depuis le modèle. Interdiction de citer un chiffre non mesuré, proxy observable en repli, renvoi au CLI déterministe.

### Ajouts français

**D3 — `references/patterns.fr.md`.** Catalogue FR1 à FR14, vocabulaire à trois niveaux, faux positifs propres au français, signes d'écriture humaine française. Neutralise P8, P17 et P26, intransposables.

**D4 — `references/examples.fr.md`.** Trois exemples travaillés complets sur post LinkedIn, mail commercial et paragraphe de proposition, avec scores avant et après et colonne « conservé délibérément ».

**D5 — `evals/evals.fr.json`.** Onze cas de déclenchement et de comportement en français, dont deux cas négatifs. Remplace `evals/evals.json` de l'amont, anglophone.

**D6 — CLI francisé (`cli/`).** Tokenizer passé en `\p{L}\p{N}` avec drapeau unicode : le regex `[a-z0-9]` d'origine fragmentait les mots accentués et faussait diversité lexicale et MATTR sur tout texte français. Listes de tells FR branchées sur `lexicalTells`. 26 tests amont toujours verts.

### Ajouts fonctionnels

**D7 — `references/commands.md` et `references/empreinte.md`.** Surface de commandes à tiret simple, et moteur d'empreinte stylistique en six passes. Persistance via `humanizer-context.md`, que l'amont charge déjà automatiquement : aucune reconstruction du package n'est nécessaire pour ajouter une voix.

**D8 — Clause de préséance sur skill de voix (`SKILL.md`).** Quand un skill de marque est chargé, humanizer ne gouverne que le négatif. Sans elle, il efface triades, antithèses, hooks et clôtures signature.

**D9 — Périmètre négatif et ancrage du score (`SKILL.md`).** Section « When NOT to use », exclusions dans la description, échantillons de contrôle chiffrés pour calibrer le score, plancher de 40 mots.

### Retiré de l'amont

`references/patterns.zh.md` (annexe chinoise), `README.md`, `docs-site/`, `landing/`, `.github/`, `submissions/`. Le CLI est livré séparément.

### Vérification

`python3 verify.py humanizer` — 64 tests au moment de ce fork. À relancer après toute modification et après tout rebase.
