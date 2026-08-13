# Benchmarks v2.3.0-fr → 3.0.0-fr

Protocole : `claude -p` headless, session neuve par run (protocole A/B de `evals/traps.json` : jamais noté par l'instance qui édite), modèle épinglé `claude-sonnet-5`, skill installé dans un projet de test isolé, 2 répétitions par cas. Textes de référence : un paragraphe FR de 139 mots chargé de 9 patterns plantés (FR1, FR3, FR4, FR5, FR7, FR13, FR14, P5, P13) et un texte humain de contrôle de 132 mots. Mesures du 13/08/2026.

## Latence et coût (headless, bout en bout)

| Cas | v2.3 (baseline) | v3.0 | Δ |
|---|---|---|---|
| `-score` texte IA, rep 1/2 | 93,8 s / 132,9 s | À REMPLIR | |
| réécriture texte IA, rep 1/2 | 95,5 s / 165,4 s | À REMPLIR | |
| `-score` texte humain, rep 1/2 | 53,7 s / 47,8 s | À REMPLIR | |
| tokens de sortie (score IA) | 9 154 / 12 500 | À REMPLIR | |
| tokens de sortie (réécriture) | 8 768 / 14 757 | À REMPLIR | |

## Exhaustivité du scan

| Mesure | v2.3 | v3.0 |
|---|---|---|
| Patterns plantés détectés (9 attendus) | dépend du modèle, non garanti | **9/9, déterministe (scan.py)** |
| Temps de la passe mécanique | 90 s+ (modèle) | **< 0,1 s** |
| Reproductibilité du score | non (auto-notation) | **oui (même entrée → même score)** |

Séparation du score sur corpus de contrôle (scan.py) : 12 textes humains réels 0-19, exemples « avant » 56-63, texte IA de référence 62. Écart minimal humain/IA : 37 points.

## Qualité de réécriture

Scores scan.py des réécritures produites (plus bas = plus humain) :

| Réécriture | v2.3 | v3.0 |
|---|---|---|
| texte IA (139 mots, 9 patterns) | À REMPLIR | À REMPLIR |

Panel de juges à l'aveugle (fidélité au sens, naturel du français, absence de tells) : voir section jugement ci-dessous.

## Chaîne d'empreinte (E2E)

Corpus : 12 posts LinkedIn réels de l'auteur (~3 100 mots, mono-surface). Vérifications : anti-contamination scorée, profil `## Voice: matthieu` écrit dans `humanizer-context.md` avec bloc ```json gate```, réécriture `--voice matthieu` conforme à `gate.py --profile` (0 violation).

Résultats : À REMPLIR.
