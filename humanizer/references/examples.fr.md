# Exemples travaillés en français

Le catalogue anglais `patterns.md` fournit trois exemples complets, tous en anglais et tous sur du contenu technique ou encyclopédique. Ce fichier fournit l'équivalent sur les trois surfaces françaises réellement produites : post LinkedIn, mail commercial, paragraphe de proposition.

Chaque exemple indique les patterns déclenchés, la réécriture, et ce qui a été **délibérément conservé**. Cette dernière colonne compte autant que les deux autres : c'est elle qui empêche le nettoyage de devenir un aplatissement.

Les entreprises citées sont fictives. Aucun chiffre de ces exemples ne doit être réutilisé dans un texte réel : la contrainte anti-fabrication du SKILL.md s'applique aussi à ce fichier.

---

## Exemple 1 — Post LinkedIn

**Avant**

> Dans un monde où l'intelligence artificielle transforme en profondeur nos organisations, il est crucial de repenser nos méthodes de travail.
>
> Force est de constater que les entreprises qui réussissent leur transformation sont celles qui placent l'humain au cœur de leur démarche, permettant ainsi de libérer le potentiel de chaque collaborateur et favorisant une culture d'innovation durable.
>
> Que vous soyez dirigeant d'une PME ou responsable d'un grand groupe, une chose est certaine : l'IA n'est plus une option, c'est une nécessité incontournable.
>
> Et vous, où en êtes-vous dans votre transformation ?

**Patterns déclenchés** — FR1 participes en chapelet (*permettant, favorisant*), niveau 1 sur *dans un monde où*, *force est de constater*, *au cœur de*, *incontournable*, FR3 fausse gamme (*que vous soyez X ou Y*), FR7 clôture générique vide, FR14 uniformité rythmique, quatre phrases entre vingt et trente mots. Score scan.py avant : **63/100**.

**Après**

> Trois dirigeants m'ont dit la même phrase cette semaine. « On a déployé l'outil, personne ne s'en sert. »
>
> Le déploiement n'était pas le problème. Ils avaient acheté un logiciel à des gens qui n'avaient pas encore changé de façon de penser leur métier. L'outil est arrivé dans un environnement qui n'avait rien demandé, et il est resté là, comme un tableau blanc dans une salle où personne ne se réunit.
>
> Ce qui a débloqué, chez le troisième, c'est une réunion de deux heures sans écran où on a listé ce que son équipe fait vraiment de ses journées.
>
> Où est-ce que ça coince chez vous, l'outil ou l'usage ?

**Conservé délibérément** — la question finale, parce que sur LinkedIn c'est une convention du genre et qu'elle appelle une réponse réelle, contrairement à l'originale. La phrase de deux mots isolée. L'image du tableau blanc, qui est une comparaison et non un aphorisme fabriqué au sens de FR11.

Score scan.py après : **13/100**. (Chiffres mesurés par `scripts/scan.py` v3, 13/08/2026 ; la burstiness d'un texte court reste bruitée, le score et les patterns portent le signal.)

---

## Exemple 2 — Mail commercial de relance

**Avant**

> Bonjour Madame Durand,
>
> J'espère que ce message vous trouve en pleine forme. Je me permets de revenir vers vous suite à notre échange du mois dernier concernant votre projet de transformation.
>
> Comme évoqué, notre approche innovante, personnalisée et éprouvée permet d'accompagner vos équipes dans la durée, en garantissant une montée en compétence progressive et en s'adaptant aux spécificités de votre organisation.
>
> N'hésitez pas à revenir vers moi si vous souhaitez échanger davantage. Je reste à votre entière disposition.

**Patterns déclenchés** — P20 artefacts conversationnels (*j'espère que ce message vous trouve*), FR5 triade adjectivale (*innovante, personnalisée et éprouvée*), FR1 participes en chapelet (*garantissant, s'adaptant*), FR7 clôture générique (*n'hésitez pas, à votre entière disposition*), FR2 verbes vides. Aucune information nouvelle dans tout le mail : c'est le vrai défaut, et aucun pattern lexical ne le capture. Score scan.py avant : **56/100**.

**Après**

> Bonjour Madame Durand,
>
> Vous m'aviez dit en juin que le sujet reviendrait après la clôture. Nous y sommes.
>
> Depuis, j'ai travaillé avec deux structures de votre taille sur le même point de blocage : les équipes utilisent l'outil pour rédiger plus vite et pas du tout pour décider mieux. J'ai une lecture de pourquoi, et elle tient en trente minutes.
>
> Jeudi 14h ou vendredi 10h ?
>
> Antoine

**Conservé délibérément** — la formule d'appel et la signature, qui ne sont pas des tells. Le mail est passé de quatre-vingt-dix mots à soixante-dix, mais surtout il contient maintenant une information et une demande. Le nettoyage lexical seul n'aurait rien réglé : le mail d'origine était vide, pas mal écrit.

Score scan.py après : **0/100**.

---

## Exemple 3 — Paragraphe de proposition commerciale

**Avant**

> Notre méthodologie s'appuie sur une approche holistique visant à optimiser l'appropriation des outils par vos collaborateurs. À travers un parcours structuré en trois temps, nous procédons à la mise en place d'un dispositif sur mesure, permettant de maximiser l'impact et de garantir un retour sur investissement mesurable, tout en s'inscrivant dans une démarche d'amélioration continue.

**Patterns déclenchés** — FR2 nominalisation (*procédons à la mise en place*, *l'appropriation*, *l'optimisation*), FR1 participes en chapelet (*visant, permettant, s'inscrivant*), niveau 2 en densité (*optimiser, maximiser, garantir, mesurable*), FR12 densité informationnelle plate, une seule idée sur cinquante-sept mots. Score scan.py avant : **58/100**.

**Après**

> Le parcours tient en trois temps, construits sur mesure. Il vise une chose : que vos collaborateurs se servent réellement des outils dans leur travail. Le retour sur investissement se mesure, et le dispositif s'ajuste en cours de route au lieu d'attendre la fin du programme.

**Conservé délibérément** — les « trois temps », le sur-mesure, le retour sur investissement mesurable et l'amélioration continue : ce sont les seules affirmations de la source, et chacune survit sous une forme vérifiable. Rien n'est ajouté pour les remplacer.

**Point de vigilance sur la contrainte anti-fabrication** — la source annonce trois temps sans dire lesquels, et la réécriture ne les nomme pas. Le Concretizer est ici tenté au plus fort : écrire « on cartographie, on construit les cas d'usage, on mesure sur deux indicateurs » rendrait le paragraphe bien plus vivant, et chacun de ces mots serait inventé, « deux » compris. Une version antérieure de cet exemple a commis exactement cette faute. Le remède n'est pas stylistique : c'est à l'auteur de la proposition de nommer les trois temps, et le skill doit le lui signaler plutôt que de les écrire à sa place. Sur une proposition commerciale, une invention chiffrée ou une étape de méthode inventée est une faute contractuelle, pas un défaut de style.

Score scan.py après : **13/100** (mesuré le 01/10/2026 ; la version fautive antérieure sortait à 23).

---

## Ce que ces trois exemples ont en commun

Aucun ne se règle par substitution lexicale. Dans les trois cas, le nettoyage des tells révèle un problème de fond : rien à dire dans l'exemple 2, une seule idée étirée dans l'exemple 3, un propos générique dans l'exemple 1. Un texte français qui déclenche beaucoup de patterns est presque toujours un texte qui n'a pas décidé ce qu'il voulait dire.

C'est aussi pourquoi le score seul ne suffit pas. Un texte vide et court peut sortir à 5/100 sans rien valoir.
