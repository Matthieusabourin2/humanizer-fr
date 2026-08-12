# Tells de l'IA en français (FR1 à FR14)

Le catalogue P1-P53 du SKILL.md est calibré sur l'anglais. Ses listes de mots (`delve`, `tapestry`, `boasts`, `nestled`) ne déclenchent rien sur du texte français, et trois de ses règles ne s'y transposent pas du tout : P17 Title Case (la capitalisation française est déjà minuscule), P26 paires à trait d'union (règle typographique anglaise), P8 évitement de la copule (le français emploie `constituer`, `représenter`, `s'imposer comme` avec une légitimité différente de `serves as`).

Ce fichier remplace ces listes pour tout texte français. Les principes du SKILL.md restent valables : grappes plutôt qu'occurrences isolées, retenue plutôt que zèle, jamais de réécriture dans une citation ou du code.

---

## Lexique — trois niveaux de confiance

**Niveau 1, toujours signaler.** Ces formes ne survivent presque jamais dans de la prose française non assistée : *véritable* (adjectif antéposé emphatique), *incontournable*, *plonger dans / plongeons*, *au cœur de*, *à l'ère de*, *dans un monde où*, *force est de constater*, *il convient de noter*, *il est important de souligner que*, *s'impose comme*, *témoigne de*, *ne se limite pas à*, *va bien au-delà de*, *révolutionner*, *un enjeu majeur*, *un levier puissant*.

**Niveau 2, signaler en densité (2 occurrences ou plus dans un paragraphe).** *crucial, essentiel, clé (adjectif), pertinent, robuste, innovant, dynamique, riche (figuré), optimiser, favoriser, permettre de, s'inscrire dans, refléter, notamment, ainsi, en effet, par ailleurs, de plus, en outre, toutefois, néanmoins, dès lors, en somme.* Une seule occurrence n'est rien : la prose française écrite emploie légitimement *notamment*, *ainsi* et *en effet* bien plus souvent que l'anglais n'emploie *moreover*. C'est l'empilement qui trahit.

**Niveau 3, contexte seulement.** *important, significatif, divers, efficace, utile, puissant.* Jamais signalés seuls.

---

## FR1 — Participes présents en chapelet

L'équivalent français du pattern P3. L'IA accroche des participes en fin de phrase pour simuler de la profondeur : *permettant de, offrant, garantissant, reflétant, soulignant, illustrant, favorisant, s'inscrivant dans, contribuant à*.

Avant : *La plateforme centralise les données, permettant aux équipes de gagner du temps et favorisant une meilleure collaboration.*
Après : *La plateforme centralise les données. Les équipes ne ressaisissent plus rien.*

C'est le tell français le plus fiable, plus que le tiret cadratin.

## FR2 — Nominalisation et verbes vides

*Procéder à la mise en place de, effectuer une analyse, réaliser une optimisation, apporter une amélioration, mettre en œuvre une démarche visant à.* Le français administratif fait cela aussi, ce qui rend le tell moins net : signaler seulement en grappe avec le niveau 1.

Avant : *Nous avons procédé à la mise en place d'une démarche d'optimisation.*
Après : *Nous avons optimisé le processus.*

## FR3 — « Que vous soyez X ou Y »

Fausse gamme française, cousine de P12. *Que vous soyez débutant ou expert, indépendant ou grand groupe.* Les deux pôles ne sont presque jamais sur une échelle réelle : c'est une manière de ne s'adresser à personne en prétendant s'adresser à tous.

## FR4 — « Il ne s'agit pas seulement de X, c'est Y »

Parallélisme négatif français (P9). Variantes : *ce n'est pas simplement… mais bien…*, *loin d'être un simple…, c'est…*, *bien plus qu'un…*. Une fois dans un texte est une figure ; deux fois est une signature machine.

## FR5 — Triade adjectivale

*Innovant, efficace et durable. Simple, rapide et sécurisé.* Trois adjectifs coordonnés en fin de syntagme. Le français y est encore plus vulnérable que l'anglais parce que l'isocolie sonne bien. Une triade **verbale** rythmée est un choix d'auteur ; une triade **adjectivale** est presque toujours du remplissage.

## FR6 — Signposting

*Dans cet article, nous allons explorer. Voyons ensemble. Passons maintenant à. Sans plus attendre. Décryptage.* L'IA annonce ce qu'elle va faire au lieu de le faire.

## FR7 — Clôtures génériques

*En conclusion. Pour aller plus loin. N'hésitez pas à. Alors, prêt à franchir le pas ? Et vous, qu'en pensez-vous ?* Couper le paragraphe et finir sur le dernier fait concret. Attention au faux positif : sur un post LinkedIn, la question finale est une convention du genre, pas un tell. Ne la signaler que si elle est vide (elle ne pourrait pas recevoir de réponse intéressante).

## FR8 — Anglicismes de traduction

*Adresser un problème* (pour traiter), *supporter* (pour prendre en charge), *délivrer* (pour livrer ou tenir), *impacter*, *opportunité* (pour occasion), *basé sur* (pour fondé sur), *au final*, *en termes de*, *définitivement* (pour assurément), *challenger* (verbe), *initier* (pour lancer). Signale la calque, pas l'emprunt installé : *digital*, *process* ou *deadline* sont du parler d'entreprise réel.

## FR9 — Typographie

Trois signaux, dans l'ordre de fiabilité.

Le tiret cadratin collé à l'anglaise, *mot—mot*, sans espace. La typographie française ne fait pas ça : elle emploie le tiret espacé, la virgule ou la parenthèse. Un tiret collé dans un texte français est un copier-coller de sortie LLM.

Les guillemets droits `"..."` là où le français attend les chevrons `« … »`, ou l'alternance des deux dans le même texte.

Les espaces insécables avant `: ; ? !` appliquées avec une régularité parfaite. Un humain qui tape vite en oublie ; l'uniformité totale est aussi suspecte que l'absence totale. Ne jamais signaler seul.

## FR10 — Gras erratique en cours de paragraphe

Équivalent P42. En français, se combine souvent avec des listes à puces où chaque item ouvre par un mot en gras suivi de deux points. Signaler la structure, pas le gras isolé.

## FR11 — Aphorismes fabriqués

*X n'est pas un outil, c'est un miroir. La donnée est le nouveau pétrole. L'IA est le langage de demain.* La formule fait profond sans rien préciser. Remplacer par la revendication concrète qu'elle désigne.

Exception : si l'auteur possède une formule signature attestée dans son corpus, elle n'est pas un tell. Vérifier avant de couper.

## FR12 — Densité informationnelle plate

Équivalent P43. Un long développement qui reformule une seule idée. Test : supprimer une phrase sur deux et vérifier si quelque chose manque. Si non, le passage tourne à vide.

## FR13 — Connecteurs scolaires en tête de paragraphe

*De plus, Par ailleurs, En outre, En effet, Ainsi, Néanmoins, Cependant, Toutefois, Dès lors, Par conséquent.* Chacun est correct isolément. Le tell est la **régularité** : trois paragraphes consécutifs ouverts par un connecteur logique différent, comme un devoir de classe. Compter les ouvertures de paragraphe avant de conclure.

## FR14 — Uniformité rythmique

Le français littéraire tolère des phrases longues à subordination multiple, ce qui rend la variance plus difficile à lire que l'anglais. Ne pas confondre longueur et platitude. Le tell n'est pas la phrase longue : c'est l'**écart-type faible**, quatre phrases consécutives entre dix-huit et vingt-quatre mots.

---

## Faux positifs propres au français

Ne pas signaler, ces traits ne prouvent rien.

Le registre soutenu. Le français professionnel écrit est plus formel que l'anglais équivalent ; ce n'est pas de la machine.

Les constructions pronominales et le passif. *Le dossier s'est réglé, il a été décidé que* sont du français normal, pas de l'évitement d'agent.

Le subjonctif, la concordance des temps, les incises longues. Marques d'un scripteur lettré.

*Notamment*, *ainsi*, *en effet*, *par ailleurs* pris isolément. Voir niveau 2.

L'accord parfait et l'orthographe sans faute. Beaucoup de gens écrivent bien.

Les majuscules accentuées correctes (*Être*, *À*). Signe d'un clavier bien configuré, rien d'autre.

---

## Signes d'écriture française humaine, à préserver

L'oral qui affleure : *bon*, *du coup*, *en vrai*, une ellipse de *ne*, une phrase qui commence par *Et* ou *Mais*.

Le détail invérifiable et daté : un nom de rue, un montant exact, une heure, un prénom.

L'incise personnelle entre parenthèses, l'autocorrection en cours de phrase, la digression qui revient.

Le mot rare employé juste, l'image qui vient d'un métier précis.

Une phrase qui s'arrête sans conclure.
