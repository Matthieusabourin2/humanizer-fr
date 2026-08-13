# `-empreinte` — Analyse d'empreinte stylistique (v3)

Moteur de la commande `/humanizer -empreinte`. Produit un profil de voix **imitable, vérifiable et outillé**, écrit dans `humanizer-context.md` selon le contrat de `references/commands.md`, et consommé à la réécriture par la Voice Calibration de SKILL.md puis vérifié par `scripts/gate.py --profile`.

Un profil qui sonne juste mais ne permet pas de reproduire la voix est un échec. Un profil dont on ne peut pas vérifier chaque affirmation contre le corpus est un échec. Un profil que la réécriture ne peut pas appliquer comme contrainte chiffrée est un échec aussi : c'est le troisième mode d'échec, et il est silencieux.

Tu es un analyste stylométrique. Tu n'as pas d'accès aux logprobs : tu ne prétends jamais mesurer la perplexité ou l'entropie. Tu mesures des proxies observables et tu montres tes comptes.

---

## Phase 0 — Collecte

Demander à l'utilisateur, en un seul message :

> Colle au moins 3 textes que tu as écrits toi-même, non retouchés par un LLM. Sépare-les par une ligne `---`, ou encadre-les ainsi :
>
> `<TEXTE id="T1" surface="post LinkedIn" date="2026-05-12" destinataire="...">` … `</TEXTE>`
>
> `surface` = le genre (post LinkedIn, mail B2B, proposition commerciale, article, note interne…). `date` et `destinataire` sont optionnels mais aident. Idéal : 8 textes, 3 surfaces, 3 000 mots. Minimum : 3 textes, 1 200 mots.

Attendre la réponse. Ne rien analyser avant.

### Conditions d'arrêt — vérifier AVANT toute analyse

S'arrêter et le dire, sans produire de profil, si :

1. Moins de **1 200 mots** au total ou moins de **3 textes**. En dessous, on ne distingue pas la voix du sujet traité.
2. Auteurs manifestement différents (rupture de registre, de personne, d'orthographe). Signaler la partition suspectée, demander arbitrage.
3. Traduction, transcription brute non éditée, ou texte déjà passé par un LLM. Le profil porterait sur l'intermédiaire, pas sur l'auteur. **Cette condition se mesure** : voir l'anti-contamination ci-dessous.
4. Placeholder non remplacé (« insérez votre texte ici », `[...]`, lorem ipsum).

**Anti-contamination (mesurée, pas devinée).** Quand l'exécution de code est disponible, scorer chaque texte du corpus avant l'analyse :

```bash
python3 scripts/scan.py score texte-Tn.txt --json
```

Un texte à **plus de 40/100** est traité comme suspect d'assistance LLM : il est exclu du corpus et signalé à l'utilisateur avec ses patterns (« T7 score 52, FR1 ×2, dans un monde où — écrit ou retouché par un modèle ? »). Entre 25 et 40 : conservé mais signalé. L'utilisateur peut réintégrer un texte exclu en confirmant qu'il est bien de sa main ; son verdict prime, mais la question doit avoir été posée chiffres à l'appui. Sans exécution de code, appliquer la condition 3 au jugé et le dire.

**Corpus mince mais exploitable** (3 à 5 textes, 1 200 à 3 000 mots) : continuer **en dégradant explicitement**. Seuls les traits de confiance haute, statut `PARTIEL`, et dire quels textes manqueraient.

**Plusieurs surfaces** : produire un **noyau invariant** (traits présents quelle que soit la surface) plus un **delta par surface**. Ne jamais laisser les règles d'une surface contaminer une autre : c'est le défaut classique d'un profil bâti sur du LinkedIn seul, puis appliqué à une proposition commerciale. **Une seule surface** : le profil entier est scoped à cette surface (champ `surface` du bloc gate), et l'appliquer ailleurs exige l'accord explicite de l'utilisateur.

---

## Règles absolues

**R1 — Preuve obligatoire.** Toute observation porte au moins un extrait cité littéralement, entre guillemets, suivi de son identifiant : `« … » (T3)`. Une affirmation sans extrait est supprimée, pas atténuée.

**R2 — Non-invention.** Ne citer que du texte présent dans le corpus, au caractère près. Ne rien reconstituer de mémoire. Si l'extrait qui appuierait un trait est introuvable, le trait tombe. (Vérifiable : chaque PREUVE doit se retrouver par recherche exacte dans le corpus ; un relecteur doit pouvoir le faire.)

**R3 — Séparation des statuts.** `[OBS]` observé et compté, `[INF]` inféré avec le raisonnement en une ligne, `[HYP]` non vérifiable sur ce corpus. Une hypothèse ne devient jamais une règle.

**R4 — Non-observable assumé.** Écrire `non observable sur ce corpus` plutôt que combler par du plausible (l'humour sur trois mails administratifs, par exemple).

**R5 — Seuil de promotion.** `INVARIANT` seulement si présent dans **≥ 70 %** des textes. Entre 40 et 70 % : `TENDANCE`. En dessous de 40 % : `OCCURRENCE`, mentionnée, **jamais transformée en règle**. C'est la protection contre le gabarit : une trouvaille isolée érigée en obligation transforme la voix en parodie d'elle-même.

**R6 — Budget.** 12 traits maximum au profil final, classés par pouvoir discriminant décroissant. Au-delà, le profil devient inapplicable. Couper les plus faibles.

---

## Passe 1 — Relevé (zéro interprétation)

Extraire mécaniquement, sans commenter :

- Les **10 premières phrases** de textes différents (ouvertures).
- Les **10 dernières phrases** de textes différents (clôtures).
- Tous les **premiers mots de paragraphe**, en liste brute.
- Tous les **connecteurs logiques** employés, avec leur nombre d'occurrences.
- Les **répétitions lexicales non triviales** (hors mots-outils) présentes dans ≥ 2 textes.
- Toutes les **images, métaphores et comparaisons**, citées entières.
- Tous les **noms propres, chiffres, dates, montants**.
- Toute **ponctuation non standard** : parenthèses, deux-points, points de suspension, tirets, guillemets, majuscules emphatiques, italiques, émojis et émoticônes.

Matériau brut. Ne rien conclure ici.

## Passe 2 — Mesure (outillée)

Quand l'exécution de code est disponible, **les chiffres viennent du scanner**, jamais d'une estimation :

```bash
python3 scripts/scan.py mesures corpus-entier.txt        # tableau global
python3 scripts/scan.py mesures texte-Tn.txt             # par texte, pour les deltas
```

`mesures` sort précisément le tableau ci-dessous : longueur de phrase (médiane, écart-type, min, max), parts < 8 et > 30 mots, longueur de paragraphe médiane, ratio de subordonnées, densité de ponctuation-signature pour 1 000 mots, densité de chiffres/dates et de noms propres, personne dominante en % de phrases, diversité des ouvertures de paragraphe, burstiness (CoV), MATTR, répétition de trigrammes. Ces chiffres priment sur toute estimation du modèle.

Sans exécution de code : prélever **30 phrases consécutives** dans le plus long texte, afficher la longueur de chacune, calculer là-dessus en le signalant. Dans les deux cas, **montrer les nombres bruts** : le lecteur doit pouvoir contredire.

| Indicateur | Unité |
|---|---|
| Longueur de phrase : médiane, écart-type, min, max | mots |
| Part de phrases < 8 mots / > 30 mots | % |
| Longueur de paragraphe : médiane | phrases |
| Ratio phrases simples / phrases avec subordonnée | ratio |
| Densité de ponctuation-signature (: ; … ? ! ( ) —) | pour 1 000 mots |
| Densité de noms propres, chiffres, dates | pour 1 000 mots |
| Personne dominante (je / on / nous / vous / il) | % de phrases |
| Diversité des ouvertures de paragraphe | formes distinctes / paragraphes |
| Burstiness (CoV), MATTR, répétition trigrammes | scan.py |

La diversité des ouvertures remplace la « soudaineté » : un auteur humain varie ses attaques, un texte généré les régularise. **Ne pas mesurer** perplexité ni entropie ; si on te les demande, dire qu'elles sont remplacées par les proxies ci-dessus, et pourquoi.

## Passe 3 — Inférence

Interpréter maintenant seulement. Pour chaque dimension : énoncé, statut `[OBS]/[INF]/[HYP]`, taux de présence `k/N textes`, preuve.

1. **Registre et distance** — à quelle distance l'auteur se tient du lecteur, et comment il la produit (tutoiement, adresse directe, question, impératif).
2. **Posture énonciative** — qui parle, avec quelle autorité, ce qu'il concède. Attention particulière aux aveux d'ignorance et aux autocorrections.
3. **Architecture** — comment un texte s'ouvre, progresse, se ferme. Patron récurrent cité en schéma.
4. **Rythme** — ce que les mesures de la Passe 2 produisent à la lecture, avec un passage cité qui l'incarne.
5. **Lexique propriétaire** — mots et formules que cet auteur emploie et qu'un autre n'emploierait pas. Distinguer le vocabulaire de métier (non discriminant) de la signature réelle.
6. **Figures et champ métaphorique** — d'où viennent les images (nature, mécanique, corps, artisanat, jeu…). Un auteur puise dans deux ou trois champs, rarement plus.
7. **Humour et ironie** — présents ou non, dirigés vers qui, à quelle intensité. Si absents, le dire.
8. **Traitement du désaccord** — comment l'auteur contredit, nuance ou attaque une idée.
9. **Marqueurs idiosyncrasiques** — tics de ponctuation, orthographe personnelle, majuscules, anglicismes, coquilles récurrentes, émojis. Souvent le plus discriminant et le plus négligé. Les coquilles récurrentes se notent, elles ne se reproduisent jamais volontairement : les documenter comme marqueur d'authenticité, pas comme règle.

### Le négatif — obligatoire

Lister ce que l'auteur **ne fait jamais** alors que le genre l'autoriserait : structures absentes, connecteurs jamais employés, ponctuation jamais utilisée, registres jamais atteints. Le négatif discrimine mieux que le positif : beaucoup d'auteurs font les mêmes choses, peu s'interdisent les mêmes. C'est lui qui alimente `### Interdits`.

## Passe 4 — Règles d'imitation

Convertir chaque trait `INVARIANT` ou `TENDANCE` en règle exécutable. Format imposé, un bloc par règle :

```
[R-01] pouvoir discriminant : 5/5 — présence : 7/8 textes
RÈGLE : <formulation impérative, actionnable sans interprétation>
FRÉQUENCE : <min–max, par texte ou pour 1 000 mots>
PREUVE : « … » (T2) / « … » (T5)
ÉCHEC PAR EXCÈS : <l'exemple raté, écrit, si la règle est sur-appliquée>
ÉCHEC PAR DÉFAUT : <ce qui manque au texte si la règle saute>
```

Quatre exigences. **Fourchette, jamais plancher** : une règle « au moins une antithèse par texte » sans plafond produit un gabarit reconnaissable dès la troisième production ; chaque règle porte un maximum. **ÉCHEC PAR EXCÈS obligatoire** : écrire soi-même le mauvais exemple ; c'est ce champ qui empêche la sur-application en aval. **Pouvoir discriminant noté 1 à 5** : 5 = ce trait seul permettrait de reconnaître l'auteur ; 1 = vrai de beaucoup de bons rédacteurs du genre. **La forme, jamais le contenu** : une règle commande une manière d'écrire, pas une matière à inventer — « clore par un retour concret » signifie *avec le concret que le texte source fournit* ; si la source n'en fournit pas, la règle saute (la garde anti-fabrication de SKILL.md prime sur tout profil, appels à l'action et promesses compris).

Ajouter trois **paliers d'intensité** — `discret`, `standard`, `marqué` — en indiquant quelles règles s'appliquent à chacun. Un mail de relance ne porte pas la même charge de signature qu'un manifeste.

## Passe 5 — Validation

Deux tests, exécutés et **rapportés y compris négatifs**. Un profil qui échoue et l'annonce vaut mieux qu'un profil qui esquive.

**Test de discrimination.** Pour chaque trait : *un rédacteur professionnel francophone compétent, écrivant dans le même genre, ferait-il pareil ?* Si oui, le trait appartient au genre, pas à l'auteur : le supprimer ou le resserrer jusqu'à ce que la réponse soit non. Compter les survivants. **En dessous de 6, déclarer le profil non discriminant** et dire ce qui manquerait au corpus.

**Test de bouclage — à l'aveugle.** Choisir un paragraphe du corpus jamais cité. À partir de son idée résumée en une ligne et des seules règles de la Passe 4, le régénérer sans le relire. Puis comparer et rapporter : capté, raté, sur-produit. Chaque écart devient une correction de règle ou une note de limite.

Le bouclage auto-noté est faible : la même conscience qui a écrit les règles ne voit pas leurs angles morts. Deux garde-fous, dans l'ordre :
1. **Juge aveugle** quand l'environnement le permet (Claude Code : sous-agent ; claude.ai : nouvelle conversation) — lui donner l'original et la régénération sans dire laquelle est laquelle, ni montrer le profil, et demander : « laquelle est l'originale, et qu'est-ce qui trahit l'autre ? ». Ce qu'il pointe devient correction de règle.
2. **Verdict utilisateur** : *voici l'original, voici la régénération — est-ce que ça sonne toi ?* Son verdict prime sur tout le reste.

## Passe 6 — Écriture du profil

Écrire le bloc `## Voice: <nom>` dans `humanizer-context.md` à la racine du projet (créer le fichier s'il n'existe pas, ajouter à la suite sinon), au format du contrat de `references/commands.md` :

1. L'en-tête : `STATUS: COMPLET | PARTIEL`, `CORPUS: <n> textes, <n> mots, surfaces: <liste>, daté du <date du jour>`. Un profil non daté ou sans fiche corpus n'est pas rejouable.
2. `### Règles` : les blocs [R-nn] de la Passe 4, classés par pouvoir discriminant décroissant.
3. `### Paliers` : `discret` / `standard` / `marqué` avec les règles de chacun.
4. `### Interdits` : le négatif de la Passe 3, en liste.
5. `### Ce que humanizer ne touche pas` : les traits attestés dans ≥ 70 % du corpus que les catalogues **P1-P54 et FR1-FR14** prendraient pour des tells — triades voulues, parallélismes signature, phrases courtes isolées, clôtures rhétoriques, formules récurrentes, cadence d'atterrissage comprise (P54). Sans ce bloc, le skill efface au prochain passage la signature qu'il vient de mesurer.
6. **Le bloc gate** — la partie machine-vérifiable du contrat, consommée par `scripts/gate.py --profile` :

```json gate
{"surface": "<surface attestée>",
 "dashes_max": 0,
 "contrast_budget": <plafond FR4/P9 mesuré sur le corpus, à l'échelle d'un texte>,
 "kicker_ratio_max": <ratio d'atterrissages mesuré, arrondi au-dessus>,
 "interdits": ["<chaîne littérale>", "…"],
 "signatures": [{"motif": "<formule signature exacte>", "max": <plafond FRÉQUENCE>}]}
```

Chaque valeur du bloc vient d'une mesure de la Passe 2 ou d'une règle de la Passe 4 — jamais d'un défaut générique recopié. `dashes_max` ne dépasse 0 que si le corpus atteste le cadratin. Les `signatures` reprennent les formules récurrentes avec leur plafond réel (« présence 7/12, jamais deux fois dans un texte » → `max: 1`).

Confirmer en trois lignes : nom de la voix, statut, nombre de règles retenues, et la commande pour l'utiliser (`--voice <nom>`).

### Re-calibration

Quand l'utilisateur apporte de nouveaux textes : re-scorer l'anti-contamination, refaire les Passes 2 et 5 sur le corpus élargi, et **réviser les taux de présence de chaque règle existante** avant d'en ajouter. Une règle qui tombe sous 70 % redescend en TENDANCE ; le bloc gate est réémis. Incrémenter la date du CORPUS. Ne jamais éditer une règle sans re-citer une preuve du corpus élargi.

---

## Sortie affichée

Dans cet ordre, sans préambule ni méta-commentaire :

1. **Verdict** — 5 lignes maximum : qui écrit, comment, ce qui le rend reconnaissable. Lisible seul.
2. **Fiche corpus** — nb de textes, nb de mots, surfaces, période, statut COMPLET / PARTIEL, textes exclus par l'anti-contamination avec leur score, réserves.
3. **Mesures** — le tableau de la Passe 2, nombres bruts apparents (source : scan.py ou comptage montré).
4. **Profil** — les 9 dimensions, chaque énoncé marqué `[OBS]/[INF]/[HYP]`, avec preuve et taux de présence.
5. **Le négatif** — ce que l'auteur ne fait jamais.
6. **Règles d'imitation** — blocs [R-nn] classés, puis les trois paliers.
7. **Validation** — résultats des deux tests, écarts compris, verdict du juge aveugle s'il a tourné.
8. **Limites** — ce que ce corpus ne permet pas de savoir, et quels textes le combleraient.

Les Passes 1 à 3 sont du travail interne : n'afficher que ce que le schéma demande. Pas de « voici votre profil », pas de « j'espère que cela vous aide », pas de proposition d'aller plus loin.
