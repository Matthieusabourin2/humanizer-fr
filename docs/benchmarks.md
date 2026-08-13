# Benchmarks v2.3.0-fr → 3.0.0-fr

Protocole : `claude -p` headless, session neuve par run (protocole A/B de `evals/traps.json` : jamais noté par l'instance qui édite), modèle épinglé `claude-sonnet-5`, skill installé dans un projet de test isolé, 2 répétitions par cas. Textes de référence : un paragraphe FR de 139 mots chargé de 9 patterns plantés (FR1, FR3, FR4, FR5, FR7, FR13, FR14, P5, P13) et un texte humain de contrôle de 132 mots. Mesures du 13/08/2026.

## Latence et coût (headless, bout en bout, rep 1 / rep 2)

| Cas | v2.3 (baseline) | v3.0 | Lecture |
|---|---|---|---|
| `-score` texte IA | 93,8 s / 132,9 s | **69,9 s / 51,6 s** | **-46 % en moyenne** |
| `-score` texte humain | 53,7 s / 47,8 s | **40,1 s / 46,0 s** | -15 % |
| réécriture texte IA | 95,5 s / 165,4 s | 194,5 s / 148,1 s | voir note ① |
| tokens de sortie, score IA | 9 154 / 12 500 | **5 373 / 3 735** | **-58 %** |
| tokens de sortie, score humain | 4 458 / 4 081 | **2 821 / 3 065** | -31 % |
| tokens de sortie, réécriture | 8 768 / 14 757 | 17 485 / 13 843 | note ① |

① La réécriture v3 fait un travail que la v2.3 ne faisait pas : scan.py en entrée, gate.py en sortie, et **itération jusqu'à conformité** (le run à 194 s compte 15 tours : la porte a refusé un premier jet et le modèle a corrigé avant de livrer). Le chemin nominal (run 2 : 6 tours, 148 s) est comparable à la baseline, avec une vérification déterministe que la baseline n'avait pas. Le mode `-score`, l'opération d'audit courante, est deux fois plus rapide.

## Exhaustivité du scan

| Mesure | v2.3 | v3.0 |
|---|---|---|
| Patterns plantés détectés (9 attendus) | dépend du modèle, non garanti, invérifiable | **9/9, déterministe (scan.py)** |
| Temps de la passe mécanique | 90 s+ (modèle) | **< 0,1 s** |
| Reproductibilité du score | non (auto-notation) | **oui : même entrée → même score** |

Séparation du score (scan.py, corpus de calibration) : 12 textes humains réels **0-19**, exemples « avant » de examples.fr.md **56-63**, texte IA de référence **62**. Écart minimal humain/IA : **37 points**.

## Qualité de réécriture (scores scan.py de la sortie, plus bas = plus humain)

| Réécriture du texte IA (62/100 en entrée) | Score sortie | Gate |
|---|---|---|
| v2.3, voix professional | 9 | non vérifiée |
| v3.0, voix professional | **3** | gate.py PASS |
| v3.0, `--voice matthieu` (profil mesuré) | **5** | **gate.py `--profile` PASS, vérifié indépendamment** |

**Panel de 3 juges à l'aveugle** (lentilles : fidélité, naturel, tics ; réécritures anonymisées A/B/C, 2 posts authentiques comme référence de voix) :

- **Voix : unanimité des 3 juges** — la réécriture `--voice matthieu` est la plus proche de la voix de référence (négations nominales, anglicismes métier gardés, première personne assumée, chute-invitation : les marqueurs du corpus sont calqués).
- **Naturel** : `--voice matthieu` et v3-professional devant la baseline (8-8,5/10 contre 6-7).
- **Fidélité : l'axe faible des trois systèmes** (4,5-7/10). Les juges ont attrapé : des inversions de sens (« les experts s'accordent » réécrit en « personne ne sait »), des ajouts de couleur, et — le plus grave — un **appel à l'action inventé** par la réécriture `--voice` (« écrivez-moi, on regarde ça ensemble »), poussé par les règles de clôture du profil.

**Correctifs immédiats issus du panel** (inclus dans cette version) : la garde anti-fabrication compte désormais explicitement les engagements et les inversions de position comme des fabrications ; la Voice Calibration subordonne toute règle de profil à cette garde (« un profil gouverne la forme, jamais le contenu ») ; piège de régression `trap-voice-fabrication` ajouté.

## Chaîne d'empreinte (E2E)

Corpus : 12 posts LinkedIn réels de l'auteur (3 221 mots, mono-surface). Chaîne exécutée en headless, session neuve :

1. `-empreinte` → profil `## Voice: matthieu` écrit dans `humanizer-context.md` (9,4 Ko, 11 min 47 s, opération unique) : 8 règles [R-nn] avec preuves citées et taux de présence, STATUS PARTIEL correctement déclaré (mono-surface), bloc « Ce que humanizer ne touche pas » motivé règle par règle, **bloc ```json gate``` mesuré** (budgets, 8 interdits issus du négatif). Le moteur a de lui-même fait juger son test de bouclage à l'aveugle et intégré les remarques du juge dans les champs ÉCHEC.
2. Réécriture `--voice matthieu` du texte IA (125 s) → score scan.py **5/100**, `gate.py --fr --profile humanizer-context.md` : **PASS** (0 cadratin, contraste 1/2, kickers 1/5, 0 interdit, 0 tier 1), vérifié hors session — les chiffres annoncés par le modèle dans son résumé correspondent exactement.

Verdict : le problème « l'empreinte n'est pas prise en compte globalement » est clos — le profil est un contrat appliqué et vérifié, plus une ambiance. Reste ouvert (documenté dans traps.json) : la tension profil/fabrication attrapée par le panel, couverte par les correctifs ci-dessus, à rejouer via `trap-voice-fabrication`.
