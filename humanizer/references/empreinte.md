# `-empreinte` — Analyse d'empreinte stylistique

Moteur de la commande `/humanizer -empreinte`. Produit un profil de voix **imitable et vérifiable**, écrit dans `humanizer-context.md` selon le contrat de `references/commands.md`.

Un profil qui sonne juste mais ne permet pas de reproduire la voix est un échec. Un profil dont on ne peut pas vérifier chaque affirmation contre le corpus est un échec.

---

## Phase 0 — Collecte

Demander à l'utilisateur, en un seul message :

> Colle au moins 3 textes que tu as écrits toi-même, non retouchés par un LLM. Sépare-les par une ligne `---`. Pour chacun, indique la surface (post LinkedIn, mail, proposition, article, note) et la date si tu l'as. Plus il y a de surfaces différentes, plus le profil sera juste.
>
> Idéal : 8 textes, 3 surfaces, 3 000 mots. Minimum : 3 textes, 1 200 mots.

Attendre la réponse. Ne rien analyser avant.

### Conditions d'arrêt — vérifier avant toute analyse

S'arrêter et le dire, sans produire de profil, si :

1. Moins de **1 200 mots** ou moins de **3 textes**. En dessous, on ne distingue pas la voix du sujet traité.
2. Auteurs manifestement différents (rupture de registre, de personne, d'orthographe). Signaler la partition suspectée, demander arbitrage.
3. Traduction, transcription brute, ou texte déjà passé par un LLM. Le profil porterait sur l'intermédiaire.
4. Placeholder non remplacé.

Corpus mince mais exploitable, 3 à 5 textes ou 1 200 à 3 000 mots : continuer **en dégradant explicitement**. Seuls les traits de confiance haute, statut `PARTIEL`, et dire quels textes manqueraient.

Plusieurs surfaces dans le corpus : produire un **noyau invariant** plus un **delta par surface**. Ne jamais laisser les règles d'une surface contaminer une autre. C'est le défaut classique d'un profil bâti sur du LinkedIn seul, puis appliqué à une proposition commerciale.

---

## Règles absolues

**R1 — Preuve obligatoire.** Toute observation porte au moins un extrait cité littéralement, entre guillemets, suivi de son identifiant : `« … » (T3)`. Une affirmation sans extrait est supprimée, pas atténuée.

**R2 — Non-invention.** Ne citer que du texte présent dans le corpus, au caractère près. Ne rien reconstituer de mémoire. Si l'extrait qui appuierait un trait est introuvable, le trait tombe.

**R3 — Séparation des statuts.** `[OBS]` observé et compté, `[INF]` inféré avec le raisonnement en une ligne, `[HYP]` non vérifiable sur ce corpus. Une hypothèse ne devient jamais une règle.

**R4 — Non-observable assumé.** Écrire `non observable sur ce corpus` plutôt que combler par du plausible.

**R5 — Seuil de promotion.** `INVARIANT` seulement si présent dans **≥ 70 %** des textes. Entre 40 et 70 % : `TENDANCE`. En dessous de 40 % : `OCCURRENCE`, mentionné, **jamais transformé en règle**. C'est la protection contre le gabarit : une trouvaille isolée érigée en obligation transforme la voix en parodie d'elle-même.

**R6 — Budget.** 12 traits maximum, classés par pouvoir discriminant décroissant. Au-delà, le profil devient inapplicable.

---

## Passe 1 — Relevé (zéro interprétation)

Extraire mécaniquement, sans commenter : les 10 premières phrases de textes différents ; les 10 dernières ; tous les premiers mots de paragraphe en liste brute ; tous les connecteurs employés avec leur nombre d'occurrences ; les répétitions lexicales non triviales présentes dans ≥ 2 textes ; toutes les images et comparaisons citées entières ; tous les noms propres, chiffres, dates, montants ; toute ponctuation non standard.

Matériau brut. Ne rien conclure ici.

## Passe 2 — Mesure

Si un outil d'exécution de code est disponible, **compter réellement**. Sinon, prélever 30 phrases consécutives dans le plus long texte, afficher la longueur de chacune, calculer là-dessus en le signalant. Dans les deux cas, **montrer les nombres bruts** : le lecteur doit pouvoir contredire.

Longueur de phrase (médiane, écart-type, min, max) ; part de phrases < 8 mots et > 30 mots ; longueur de paragraphe médiane ; ratio phrases simples / phrases à subordonnée ; densité de ponctuation-signature `: ; … ? ! ( )` pour 1 000 mots ; densité de noms propres, chiffres et dates pour 1 000 mots ; part de mots > 12 caractères ; personne dominante en % de phrases ; temps dominant et part de passif ; diversité des ouvertures de paragraphe, soit le nombre de formes distinctes sur le nombre de paragraphes.

Ce dernier indicateur remplace la « soudaineté » : un auteur humain varie ses attaques, un texte généré les régularise.

**Ne pas mesurer** perplexité ni entropie : pas d'accès aux logprobs. Si on te les demande, dire qu'elles sont remplacées par les proxies ci-dessus, et pourquoi.

Le CLI optionnel du dépôt (`cli/`) calcule burstiness, MATTR, type-token ratio et répétition trigramme de façon déterministe. Quand il est disponible, ses chiffres priment sur toute estimation.

## Passe 3 — Inférence

Interpréter maintenant seulement. Pour chaque dimension : énoncé, statut `[OBS]/[INF]/[HYP]`, taux de présence `k/N textes`, preuve.

Registre et distance au lecteur. Posture énonciative, avec attention aux aveux d'ignorance et aux autocorrections. Architecture, soit comment un texte s'ouvre, progresse et se ferme, en schéma. Rythme, avec un passage cité qui l'incarne. Lexique propriétaire, en distinguant le vocabulaire de métier, non discriminant, de la signature réelle. Champ métaphorique, en notant que deux ou trois sources suffisent à un auteur. Humour et ironie, dirigés vers qui et à quelle intensité, ou absents. Traitement du désaccord. Marqueurs idiosyncrasiques, tics de ponctuation, orthographe personnelle, anglicismes, coquilles récurrentes : souvent le plus discriminant et le plus négligé.

### Le négatif — obligatoire

Lister ce que l'auteur **ne fait jamais** alors que le genre l'autoriserait. Structures absentes, connecteurs jamais employés, ponctuation jamais utilisée, registres jamais atteints. Le négatif discrimine mieux que le positif : beaucoup d'auteurs font les mêmes choses, peu s'interdisent les mêmes.

## Passe 4 — Règles d'imitation

Convertir chaque trait `INVARIANT` ou `TENDANCE` en règle exécutable, au format du contrat de `references/commands.md`.

Trois exigences. **Fourchette, jamais plancher** : une règle du type « au moins une antithèse par texte » sans plafond produit un gabarit reconnaissable dès la troisième production ; chaque règle porte un maximum. **Champ EXCÈS obligatoire** : écrire soi-même le mauvais exemple, c'est lui qui empêche la sur-application en aval. **Discriminant noté 1 à 5**, où 5 signifie que ce trait seul permettrait de reconnaître l'auteur.

Ajouter trois paliers d'intensité, `discret`, `standard`, `marqué`, en indiquant quelles règles s'appliquent à chacun. Un mail de relance ne porte pas la même charge de signature qu'un manifeste.

## Passe 5 — Validation

Deux tests, exécutés et **rapportés y compris négatifs**. Un profil qui échoue et l'annonce vaut mieux qu'un profil qui esquive.

**Test de discrimination.** Pour chaque trait : *un rédacteur professionnel compétent, écrivant dans le même genre, ferait-il pareil ?* Si oui, le trait appartient au genre, pas à l'auteur : le supprimer ou le resserrer jusqu'à ce que la réponse soit non. Compter les survivants. **En dessous de 6, déclarer le profil non discriminant** et dire ce qui manquerait au corpus.

**Test de bouclage.** Choisir un paragraphe du corpus jamais cité. Sans le relire, le réécrire à partir des seules règles de la passe 4, en partant de son idée en une ligne. Comparer ensuite à l'original et rapporter : ce que les règles ont capté, raté, sur-produit. Chaque écart devient une correction de règle ou une note de limite.

Le test de bouclage est auto-noté, donc faible. Le soumettre à l'utilisateur : *voici l'original, voici la régénération, est-ce que ça sonne toi ?* Son verdict prime.

## Passe 6 — Écriture du profil

Écrire le bloc `## Voice: <nom>` dans `humanizer-context.md` à la racine du projet, en créant le fichier s'il n'existe pas et en ajoutant à la suite s'il existe déjà. Confirmer en trois lignes : nom de la voix, statut, nombre de règles retenues, et la commande pour l'utiliser (`--voice <nom>`).

Remplir impérativement le bloc `### Ce que humanizer ne touche pas` avec les traits attestés dans ≥ 70 % du corpus que les catalogues P1-P53 et FR1-FR14 prendraient pour des tells : triades voulues, parallélismes négatifs signature, phrases courtes isolées, clôtures rhétoriques, formules récurrentes. Sans ce bloc, le skill effacera au prochain passage la signature qu'il vient de mesurer.

---

## Sortie affichée

Dans cet ordre, sans préambule.

Verdict en 5 lignes maximum : qui écrit, comment, ce qui le rend reconnaissable. Lisible seul. Puis la fiche corpus, le tableau de mesures avec les nombres bruts, le profil des 9 dimensions marquées `[OBS]/[INF]/[HYP]` avec preuves et taux de présence, le négatif, les règles classées, les résultats des deux tests écarts compris, et enfin les limites du corpus avec les textes qui les combleraient.

Les passes 1 et 2 sont du travail interne : n'afficher que les mesures, pas le relevé brut.
