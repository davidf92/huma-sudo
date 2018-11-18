# Human Sudoku
Simulation de joueur humain de sudoku

Projet développé en Python 3, entièrement en paradigme objet. Il simule un joueur humain qui tente de résoudre une grille de Sudoku. Le programme n'utilise pas la force brute ni aucune optimisation algorithmique et ne cherche pas la rapidité. Au contraire il tente de reproduire fidèlement la cognition avec ses capacités et ses limites : exploration visuelle de la grille, réflexion, mémoire, intuition, expérience du jeu.
L'objectif du projet est strictement de faire une simulation réaliste, et en particulier d'éviter les approches algorithmiques classiques et les optimisations même les plus basiques qui n'ont pas d'équivalent cognitif. Un bon exemple est de bannir la récursion. La rapidité pure n'est pas un objectif, pour autant le souhait humainement réaliste de performance n'est pas négligé : habileté, bonnes intuitions, évitement de recherches inutiles et d'impasses.
Si le niveau du joueur est bien simulé, celui-ci résoudra plus ou moins facilement certaines grilles et échouera à d'autres. Le programme prend en compte pour cela des données de "profil cognitif". Ce profil comporte des caractéristiques d'expérience du jeu et de capacité d'apprentissage. Des résolutions successives de la même grille devraient donc être de plus en plus performantes.

L'interface permet de suivre le raisonnement, les prises de décision, les informations recherchées et observées dans la grille, les techniques choisies ainsi que leur déroulement. Elle permet également de suivre les limites et défaillance de mémoire qui obligent parfois à devoir rechercher des informations précédemment connues ou à devoir reprendre un raisonnement à son début.

Implémentation du réalisme :

a/ Classe SudoThinking : la réflexion qui permet d'enchaîner logiquement des actions et de dérouler des techniques systématiques. Les limites cognitives plafonnent la complexité de cette réflexion et la capacité de combiner des informations et des actions.

b/ Classe SudoMemory : La mémoire qui permet de savoir ce que l'on est en train de faire, ce que l'on voit, ce que l'on pense. C'est donc ce que l'on appelle une mémoire de travail. Elle est limitée de manière réaliste par la quantité d'informations et l'oubli plus ou moins rapide.

c/ Classe SudoGridView : la recherche visuelle dans la grille. La grille ne peut pas être connue exhaustivement, elle ne peut qu'être explorée du regard à la recherche d'informations, des chiffres présents, des cases vides et des combinaisons de cet ensemble. La mémoire permet au joueur de se remémorer plus ou moins longtemps ce qu'il a vu.

d/ Classes SudoTechxxxxxx : des techniques de résolution réalistes, qui consistent en enchaînements logiques et systématiques dans tout ou partie de la grille à la recherche d'informations (donc des observations de la grille), qui aboutissent éventuellement à la découverte d'un placement possible.

e/ Classes SudoThinkAI et SudoAIxxxx : la réflexion de plus haut niveau (sorte d'intelligence artificielle), la capacités de décision, l'évaluation d'opportunités, la prise en compte d'intuitions, la notion de choix "prudent" ou au contraire "optimiste" voire "agressif"

f/ Classe SudoLearning : la capacité d'apprentissage, tant au fil de la résolution d'une grille que d'une grille à l'autre. Par exemple les enchaînements qui "marchent" plus ou moins bien selon que la grille est plus ou moins remplie, ou au contraire ce qui est de la perte de temps.

g/ Classes SudoPlayerProfile : le paramétrage des capacités du joueur dans tous les aspects de réflexion, mémoire, vision de la grille, intuition et habileté, apprentissage.

Pour commencer, le joueur humain qui est simulé a beaucoup de "limites cognitives" et il n'est pas "surdoué". Il ne peut donc pas "connaître par coeur" toute la grille. Il doit l'observer de manière répétitive et intensive pour y chercher visuellement les informations parcellaires avec lesquelles il "réfléchit" . De même, le joueur a une "mémoire de travail" limitée, imparfaite, et éphémère. Il a toutes les chances d'avoir oublié un détail vu quelques minutes auparavant. Enfin, le joueur a une certaine intelligence qui lui permet de tenter d'appliquer des techniques de résolution "humaines", mais la limite de son intelligence l'empêche de faire des raisonnements complexes comme par exemple imbriquer trop de techniques entre elles. S'il essaie, il va tout mélanger en mémoire et aboutir à une confusion qui le fera échouer et le forcera à revenir à des techniques plus simples.

Il y a évidemment une limite de niveau car le programme ne simule pas la possibilité pour le joueur de noter (sur papier) des hypothèses. S'il fait un essai de valeur incertain, il doit donc se le rappeler. Dans la réalité à partir d'un certain niveau de grille, il faut soit une mémoire hors du commun, soit un bloc-note. Mais cette simulation pourrait être ajoutée au programme actuel.

A l'inverse, il y a une simulation d'intelligence. D'une part le programme reproduit des techniques de résolution simples (autrement dit des raisonnements logiques) et d'autre part il tente d'appliquer la bonne technique au bon moment. Par exemple il cherche des coups triviaux (ex: s'il reste une seule case libre dans un carré) et des opportunités apparues après un placement. S'il applique une technique qui ne donne rien, il va l'abandonner et en utiliser une autre.

Enfin le programme simule une capacité d'apprentissage grâce à du code de type réseau neuronal. Par conséquent des choses qui marchent bien seront préférées par la suite.

Le "niveau du joueur" est calibré par des profils de mémoire et d'intelligence qui tentent d'être des simulations réalistes. Il est donc tout-à-fait logique qu'un joueur échoue à résoudre une grille trop compliquée pour lui. La rapidité du jeu est adaptée via des fonctions temporelles, sachant que le but est plus de voir comment le programme progresse, que de résoudre le plus vite possible.

C'est un projet évolutif car il est toujours possible d'améliorer le réalisme de la simulation. Un bon exemple est la mémoire, car la mémoire humaine est associative d'une manière quasi-infinie. Cela est très difficile à simuler. De même pour l'intelligence artificielle. Il y a donc un gros potentiel pour améliorer le niveau de jeu tout en améliorant le réalisme de la simulation.

Sur le plan des interfaces, le code de simulation est entièrement distinct de celui des E/S. Il est donc possible d'ajouter facilement des modes d'affichage, par exemple fenêtrés. Dans la version actuelle les grilles sont lues comme des listes de chiffres (ou 0 représente une case vide). Il est donc possible et facile d'interfacer le programme avec des générateurs de grilles, ou d'utiliser des fichiers de format texte, Excel, etc. Enfin le programme fonctionne par itération infinie de boucles réflexion/observation/placement/mémorisation/apprentissage. Chaque itération fait une seule action élémentaire, par exemple chercher une info dans la grille ou placer un chiffre. Donc le code est naturellement adapté à une interface d'exécution événementielle.

Le code contient déjà des fonctions paramétrables de journalisation (log) des actions. Cela permet de suivre comment le programme a joué, et c'est aussi très utile pour tester et débugger.
