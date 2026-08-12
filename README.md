# Humanizer FR

Skill Claude qui détecte les motifs d'écriture IA et réécrit le texte dans une voix humaine — la vôtre, si vous lui donnez votre corpus. Fork français documenté de [Aboudjem/humanizer-skill](https://github.com/Aboudjem/humanizer-skill).

*French fork of the humanizer skill: 54 AI-writing patterns + 14 French-specific ones, a 0–100 AI-tell score, 5 built-in voices, and an `-empreinte` command that builds a custom voice profile from your own writing corpus, with real measurements.*

## Ce que c'est

Un skill pour Claude (claude.ai, Claude Code, et tout éditeur qui lit des fichiers SKILL.md). Pas de serveur, pas de dépendance, pas d'appel réseau : des fichiers Markdown que le modèle lit, plus un `verify.py` optionnel pour tester le paquet.

Ce qu'il fait :

- Détecte 54 motifs d'écriture IA (catalogue P1–P54) plus 14 motifs propres au français (FR1–FR14) : participes en chapelet, nominalisations vides, triades adjectivales décoratives, fausses gammes, clôtures génériques, tirets cadratins, uniformité rythmique…
- Attribue un score 0–100 de « tell IA » (plus bas = plus humain), avec la liste des motifs trouvés et où.
- Réécrit dans une des 5 voix intégrées (`casual`, `professional`, `technical`, `warm`, `blunt`) ou dans une voix personnalisée.
- Construit votre propre profil de voix depuis votre corpus réel avec `-empreinte` : règles mesurées, preuves citées, interdits, paliers d'intensité.
- Connaît les faux positifs du français : le pronominal, le passif ordinaire ou « notamment » ne sont pas des tells, et le skill ne les signale pas.
- Vérifie ses propres réécritures avec une porte chiffrée : budgets de densité (contrastes, punchlines de fin de paragraphe, cadratins), scan de cluster local, `scripts/gate.py` qui compte de façon déterministe, et pièges de régression dans `evals/traps.json`.

## Ce que ce n'est pas

Un outil de contournement de détecteurs. La philosophie du skill : un texte bien écrit ne déclenche pas les détecteurs parce qu'il n'a pas les tics paresseux qu'ils cherchent. On répare l'écriture, pas le score. Le skill porte aussi un garde-fou anti-fabrication strict : il n'invente jamais un chiffre, une date ou une citation pour « faire vécu ».

## Installation

### claude.ai (Pro, Max, Team, Enterprise — avec l'exécution de code activée)

1. Téléchargez ce dépôt (`Code > Download ZIP`), extrayez-le.
2. Re-zippez le dossier `humanizer/` seul — le ZIP doit contenir `humanizer/` comme racine, avec `SKILL.md` dedans.
3. Dans claude.ai : `Customize > Skills`, bouton `+`, uploadez le ZIP.
4. Test : nouvelle conversation, tapez `/humanizer -help`.

### Claude Code

```bash
git clone https://github.com/VOTRE_COMPTE/humanizer-fr.git
cp -r humanizer-fr/humanizer ~/.claude/skills/humanizer   # global
# ou, dans un projet :
cp -r humanizer-fr/humanizer .claude/skills/humanizer     # local au repo
```

### Autres éditeurs (Cursor, Codex, etc.)

Copiez le dossier `humanizer/` dans le répertoire de skills de votre éditeur. Le point d'entrée est `SKILL.md` ; il charge les fichiers de `references/` à la demande.

## Utilisation

```
/humanizer <texte>              réécriture (défaut)
/humanizer -score <texte>       détection + score 0-100, sans réécriture
/humanizer -fr <texte>          force le catalogue français
/humanizer -voix                liste les voix disponibles
/humanizer -empreinte           construit un profil de voix depuis votre corpus
/humanizer -audit <chemin>      score des fichiers, pires en premier
/humanizer -help                cette liste

options : --voice casual|professional|technical|warm|blunt|<perso>
          --purpose essay|email|marketing|technical|general
          --aggressive  --iterate N  --score  --file <chemin>
          --ignore-code  --ignore-quotes  --openings N
```

Le déclenchement est aussi conversationnel : « rends ce texte plus humain », « on dirait du ChatGPT, tu peux reprendre ? », « ça sonne généré » suffisent, en français comme en anglais.

## Créer votre voix : `-empreinte`

C'est la pièce maîtresse du fork. Au lieu de réécrire vers une voix générique, le skill construit la vôtre :

1. Vous fournissez au moins 3 textes écrits par vous, sans retouche par un modèle, 1 200 mots minimum (idéal : 8 textes, 3 surfaces, 3 000 mots). Mails, posts, messages — le tout-venant vaut mieux que le poli.
2. Le skill fait six passes : relevé, mesure (si un outil d'exécution de code est disponible, il compte réellement — longueurs de phrases, ponctuation, connecteurs, personnes grammaticales), inférence sur 9 dimensions, extraction de règles avec preuves citées au caractère près, validation par deux tests (discrimination et bouclage), écriture du profil.
3. Il produit `humanizer-context.md` : un bloc `## Voice: <nom>` avec 12 règles maximum classées par pouvoir discriminant, chacune avec fréquence, preuve, échec par excès et échec par défaut, plus les interdits et la liste des traits à ne jamais « corriger ».

Chaque affirmation du profil est étiquetée : observé (avec taux), inféré (avec raisonnement) ou non observable. Le skill refuse de produire un profil sur un corpus trop mince, et vous dit quels textes combleraient les trous.

### Où mettre le profil

- À la racine du projet : `SKILL.md` charge `humanizer-context.md` automatiquement. Aucune réinstallation.
- Embarqué dans le skill : posez `humanizer-context.md` à côté de `SKILL.md` avant de zipper — le profil voyage alors avec le skill (nouveauté 2.1.0). Un fichier à la racine du projet garde la priorité pour les voix de même nom.

Un profil construit sur corpus réel prime sur les cinq voix intégrées et sur les règles de style du skill, interdiction du tiret cadratin comprise : si votre corpus prouve que vous en utilisez, le profil gagne.

## Comment ça marche

Quatre passes, chacune un seul travail : détection (non destructive — `-score` s'arrête là), suppression des tells, injection de la voix (rythme, burstiness, lexique), vérification finale (variance des phrases, listes noires, motifs restants).

Deux garde-fous structurants, hérités des régressions constatées en amont et re-durcis ici :

- Anti-fabrication : jamais de chiffre, date, nom ou anecdote inventés pour « concrétiser ». Sur une proposition commerciale, une invention chiffrée est une faute contractuelle, pas un défaut de style.
- Préséance des skills de voix : si un skill de marque dédié est chargé dans la même session, il possède la forme positive (signatures, antithèses, hooks) et humanizer se cantonne à la forme négative (vocabulaire IA, chapelets de participes, remplissage, calques). Un skill de voix existe pour construire une signature reconnaissable ; la gommer comme un tell est précisément l'échec que cette clause empêche.

## Le français est traité comme une langue, pas comme une traduction

`references/patterns.fr.md` : catalogue FR1–FR14, vocabulaire IA français à trois niveaux, faux positifs propres au français, signes d'écriture humaine française. `references/examples.fr.md` : trois exemples travaillés complets (post LinkedIn, mail commercial, paragraphe de proposition) avec scores avant/après et — colonne qui compte autant que les autres — ce qui a été délibérément conservé. `evals/evals.fr.json` : 11 cas de déclenchement rejouables, dont 2 cas négatifs.

## Contenu du dépôt

```
humanizer/
  SKILL.md                        point d'entrée, 4 passes, garde-fous, préséance
  CHANGELOG.md                    manifeste de rebase : toutes les divergences vs l'amont
  verify.py                       114 tests d'intégrité du paquet (python3 verify.py)
  scripts/
    gate.py                       porte chiffrée : cadratins, contrastes, kickers, clusters, tier 1
  references/
    patterns.md                   catalogue P1–P53 (anglais, hérité de l'amont)
    patterns.fr.md                catalogue FR1–FR14 + faux positifs français
    examples.fr.md                3 exemples travaillés, scores avant/après
    empreinte.md                  procédure -empreinte complète (6 passes, 2 tests)
    commands.md                   routage des commandes, contrat des profils de voix
    always-on-templates.md        gabarits de sortie
  evals/
    evals.fr.json                 cas de test à rejouer sur Haiku, Sonnet et Opus
    traps.json                    pièges de régression distillés d'échecs réels
docs/
  tests.md                        documentation de l'ensemble de la suite de tests
site/
  tests.html                      page de test publiable (statique, autonome), ressource catalia.fr
```

Le CHANGELOG n'est pas décoratif : c'est un manifeste de rebase. Quand l'amont publie une version, on réapplique les divergences listées (D1–D21) et on relance `verify.py`.

## Tests

La suite tient en quatre couches, toutes documentées dans [`docs/tests.md`](docs/tests.md) : le harnais du paquet (`verify.py`, 114 checks), la porte chiffrée (`scripts/gate.py`, 5 compteurs déterministes), les cas de déclenchement (`evals/evals.fr.json`, 11 cas) et les pièges de régression (`evals/traps.json`, 10 pièges, protocole de rejeu A/B).

Une version publiable de cette documentation existe en page statique autonome : [`site/tests.html`](site/tests.html), destinée à être publiée comme ressource sur [catalia.fr](https://www.catalia.fr). Contrat de la page : ses chiffres se mettent à jour dans le même commit que le code, et sa prose française passe sa propre porte (`gate.py --fr` sort PASS sur le texte extrait — la commande de vérification est dans `docs/tests.md`).

## Généalogie et crédits

Fork de [Aboudjem/humanizer-skill](https://github.com/Aboudjem/humanizer-skill) 0.5.0 (Adam Boudjemaa, MIT), lui-même héritier de [blader/humanizer](https://github.com/blader/humanizer) et adossé à [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing). Ce fork ajoute : le catalogue français et ses faux positifs, les exemples et évals FR, la commande `-empreinte` et son contrat de profil mesuré, les profils embarqués, la clause de préséance des skills de voix, le garde anti-fabrication re-durci, et `verify.py`.

## Licence

MIT — voir [LICENSE](LICENSE). Copyright amont : Adam Boudjemaa. Divergences du fork : voir `humanizer/CHANGELOG.md`.
