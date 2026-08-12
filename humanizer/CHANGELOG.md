# CHANGELOG

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
