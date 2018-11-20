# SudoSimu
**Simulation de joueur humain de sudoku**


Projet développé en Python 3, entièrement en paradigme objet. Il simule un joueur humain qui tente de résoudre une grille de Sudoku. Le programme n'utilise pas la force brute ni aucune optimisation algorithmique et ne cherche pas la rapidité. Au contraire il tente de reproduire fidèlement la cognition avec ses capacités et ses limites : exploration visuelle de la grille, réflexion, mémoire, intuition, expérience du jeu.

L'objectif du projet est strictement de faire une simulation réaliste, et en particulier d'éviter les approches algorithmiques classiques et les optimisations même les plus basiques qui n'ont pas d'équivalent cognitif. Un bon exemple est de bannir la récursion. La rapidité pure n'est pas un objectif, pour autant le souhait humainement réaliste de performance n'est pas négligé : habileté, bonnes intuitions, évitement de recherches inutiles et d'impasses.
Si le niveau du joueur est bien simulé, celui-ci résoudra plus ou moins facilement certaines grilles et échouera à d'autres. Le programme prend en compte pour cela des données de "profil cognitif". Ce profil comporte des caractéristiques d'expérience du jeu et de capacité d'apprentissage. Des résolutions successives de la même grille devraient donc être de plus en plus performantes.

Le programe ne comporte aucun algorithme de résolution certaine, donc il ne peut pas "aider". Si la résolution simulée échoue, le programme ne comporte pas de moyen de connaître la grille résolue. A l'inverse il ne permet pas de faire des erreurs et il n'y a donc pas besoin de "vérification". Les raisonnements sont limités mais ne sont pas faux et les chiffres trouvés sont correctement placés. Le joueur peut donc échouer mais il ne peut pas "se tromper".

Une interface complète permet de suivre le raisonnement, les prises de décision, les informations recherchées et observées dans la grille, les techniques choisies ainsi que leur déroulement. Elle permet également de suivre les limites et défaillance de mémoire qui obligent parfois à devoir rechercher des informations précédemment connues ou à devoir reprendre un raisonnement à son début. A l'inverse la résolution peut être exécutée sans aucun affichage jusqu'à son résultat : résolution ou échec, ainsi que log et statistiques. Le détail et les domaines d'informations sorties / affichées sont largement paramétrables, allant jusqu'à la capacité de test du code au niveau élémentaire. 
Il est possible d'exécuter des résolutions simultanées en batch, par exemple dans le but d'en comparer les résultats, un peu à l'exemple des parties simultanées d'échecs et autres jeux de réflexion.


### Implémentation du réalisme :

- **Classe SudoThinking** -- la réflexion qui permet d'enchaîner logiquement des actions et de dérouler des techniques systématiques. Les limites cognitives plafonnent la complexité de cette réflexion et la capacité de combiner des informations et des actions.

- **Classe SudoMemory** -- La mémoire qui permet de savoir ce que l'on est en train de faire, ce que l'on voit, ce que l'on pense. C'est donc ce que l'on appelle une mémoire de travail. Elle est limitée de manière réaliste par la quantité d'informations et l'oubli plus ou moins rapide.
Remarque : la résolution se fait sans notes, entièrement de mémoire.

- **Classe SudoGridView** -- la recherche visuelle dans la grille. Le simulateur ne dispose d'aucun moyen de connaissance et mémorisation complète de la grille. Celle-ci ne peut être connue que de manière parcellaire, ce qui nécessite de l'explorer du regard à la recherche d'informations, des chiffres présents, des cases vides et de leurs combinaisons. La mémoire permet au joueur de se remémorer plus ou moins longtemps ce qu'il a vu de la grille.

- **Classes SudoTechxxxxxx** -- des techniques de résolution réalistes, qui consistent en enchaînements logiques et systématiques dans tout ou partie de la grille à la recherche d'informations (donc des observations de la grille), qui aboutissent éventuellement à la découverte d'un placement possible.

- **Classes SudoThinkAI et SudoAIxxxx** -- la réflexion de plus haut niveau (sorte d'intelligence artificielle), la capacités de décision, l'évaluation d'opportunités, la prise en compte d'intuitions, la notion de choix "prudent" ou au contraire "optimiste" voire "agressif". D'une part le programme reproduit des techniques de résolution simples (autrement dit des raisonnements logiques) et d'autre part il tente d'appliquer la bonne technique au bon moment. Par exemple il cherche des coups triviaux (ex: s'il reste une seule case libre dans un carré) et des opportunités apparues après un placement. S'il applique une technique qui ne donne rien, il va l'abandonner et en choisir une autre.

- **Classe SudoLearning** -- la capacité d'apprentissage, tant au fil de la résolution d'une grille que d'une grille à l'autre. Par exemple les enchaînements qui "marchent" plus ou moins bien selon que la grille est plus ou moins remplie, ou au contraire ce qui est de la perte de temps.

- **Classe SudoPlayerProfile** -- le paramétrage des capacités du joueur dans tous les aspects de réflexion, mémoire, vision de la grille, intuition et habileté, apprentissage.


### Implémentations de bas niveau

- **Classe SudoGrid** -- Modélisation de la grille. C'est la seule classe liée à la simulation qui est exempte du besoin de réalisme. 
Une seule autre classe accède à SudoGrid, c'est SudoGridView qui simule les "observations" de la grille. Aucune autre classe de simulation, notamment SudoThinking et SudoMemory, n'y a un accès direct, et le code source de ces classes n'importe même pas le module dans lequel est codée SudoGrid.

- **Classe SudoRules** -- Définit les règles du Sudoku qui sont la liste de 1 à 9 et les unicités de chiffres par groupement. SudoRules est utilisée dans SudoGrid et dans le code qui effectue les placements pour en vérifier la régularité. Définit aussi la hiérarche des exceptions utilisées dans le programme, principalement pour prendre en compte les défaillance de mémoire et de réflexion.


### Implémentations des fonctions techniques :

- **Classe SudoEnv** -- L'environnemnet de la simulation : regroupe toutes les interfaces, les interactions, les affichages.

- **Classe SudoUI et SudoGUI** -- Les interfaces utilisateurs, dont GUI basé sur Tkinter.

- **Classe SudoTest** -- Les fonctions de test et d'affichage conditionnel présentes dans tout le code source du programme.


### Interfaces :

Une interface graphique repose sur Tkinter et Tix. Elle est entièrement compatible avec le paradigme événementiel. Elle permet une exécution du simulateur seul ainsi que l'intégration sous forme de package dans un programme extérieur et l'intégration dans l'interface GUI événementielle dudit programme.
La modularité de l'interface utilisateur permet aisément de modifier ou d'ajouter d'autres modes d'E/S (ex: console) ou d'autres librairies GUI.
Une interface système permet de lire et écrire des fichiers formatés qui définissent une grille, ainsi que d'enregister en fichier des logs d'exécution, des statistiques de performance et des progressions. Il y a plusieurs formats de modélisations de grille qui permettent facilement d'interfacer avec des générateurs de grilles aléatoires.
Il n'y a aucune dépendance du système sous-jacent ni de sa distribution et seules les librairies Python standards sont utilisées.


### Note sur le développement et sur le code : 

Le code privilégie une utilisation propre et complète de Python, dans un style lisible pour ne pas dire scolaire. C'est du Python 3, la compatibilité avec Python 2.7 n'est pas assurée. Les commentaires et sauts de lignes sont abondants au détriment volontaire de la compacité. Toutes les classes et fonctions sont documentées de manière standard.
Le code est très structuré, les noms de variables et d'objets sont composés et explicites. Le découpage et la modularité sont fins avec des fonctions nombreuses et courtes pour la clareté et la lisibilité. Les modules sont nombreux et la plupart codent une seule classe. Le paradigme objet est strictement respecté, il n'y a pas de variables globales à part des constantes, il n'y a quasiment pas de fonctions à l'extérieur des classes. A l'inverse, le code utilise autant que possible tous les types de collections, d'itérations, des fonctions lambda. Les classes utilisent des méthodes courtes, simples et nombreuses ainsi que des propriétés, seters et geters. Il y a de l'héritage de classes. Le code utilise systématiquements les exceptions et le contrôle de leur propagation partout où cela est pertinent.Le programme est regroupé dans un package et des sous-packages et utilise abondamment les imports. 

Le développement a été conduit en totalité dans une démarche "test-driven" afin d'en optimiser la qualité. C'est d'ailleurs un effort qui a été largement bénéficiaire grâce à un besoin de débuggage très limité. Tout le code, chaque fonction et méthode, contient du code de suivi d'exécution à un niveau très fin et paramétré, y compris des pauses d'exécution et des tests conditionnels. 
Tout les modules sont exécutables directement dans un interpréteur (if __name__ == "__main__" ....) et comportent à la fin du code de test qui a été utilisé pendant le développement et n'a volontairement pas été supprimé. Bien sûr cet abondance de code "inutile" nuit à la rapidité d'exécution, mais encore une fois celle-ci n'est pas un objectif et ce n'est pas perceptible dans la démarche de simulation interactive qui est l'objectif du projet.

Pour ce qui est de l'import du package dans un programme "extérieur", ce dernier peut facilement paramétrer la propagation des exceptions et l'exécution conditionnelle du code de test intégré.


### Suite du projet

C'est un projet évolutif car il est toujours possible d'améliorer le réalisme de la simulation, d'ajouter de nouvelles techniques et d'en intégrer l'utilisation via l'AI, d'enrichir la capacité de décision en prenant en compte plus de combinaisons de situations, d'affiner les profils de capacités et limitations de mémoire et de réflexion. Un domaine particulier à développer est la modélisation de la mémoire : car la mémoire humaine est associative d'une manière quasi-infinie. Cela est très difficile à simuler. De même pour l'intelligence artificielle en développant des réseaux de neurones.

Pour améliorer le "niveau" de résolution en conservant le réalisme, il faudra incontournablement ajouter des techniques plus puissantes. En revanche celles-ci sont en général plus longues à exécuter dans la réalité, donc vouloir les utiliser systématiquement (pour leur puissance) plutôt que des techniques plus simples irait à l'encontre du réalisme de recherche de simplicité et de rapidité. Ajouter des techniques va donc de pair avec leur prise en compte précise dans l'AI et le système de décision.

Il y a donc dans l'ensemble un gros potentiel pour prolonger ce projet et améliorer le niveau de jeu tout en améliorant le réalisme de la simulation.
