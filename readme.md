# SudoSimu
**Simulation de joueur humain de sudoku**

Projet d�velopp� en Python 3, enti�rement en paradigme objet. Il simule un joueur humain qui tente de r�soudre une grille de Sudoku. Le programme n'utilise pas la force brute ni aucune optimisation algorithmique et ne cherche pas la rapidit�. Au contraire il tente de reproduire fid�lement la cognition avec ses capacit�s et ses limites : exploration visuelle de la grille, r�flexion, m�moire, intuition, exp�rience du jeu.

L'objectif du projet est strictement de faire une simulation r�aliste, et en particulier d'�viter les approches algorithmiques classiques et les optimisations m�me les plus basiques qui n'ont pas d'�quivalent cognitif. Un bon exemple est de bannir la r�cursion. La rapidit� pure n'est pas un objectif, pour autant le souhait humainement r�aliste de performance n'est pas n�glig� : habilet�, bonnes intuitions, �vitement de recherches inutiles et d'impasses.
Si le niveau du joueur est bien simul�, celui-ci r�soudra plus ou moins facilement certaines grilles et �chouera � d'autres. Le programme prend en compte pour cela des donn�es de "profil cognitif". Ce profil comporte des caract�ristiques d'exp�rience du jeu et de capacit� d'apprentissage. Des r�solutions successives de la m�me grille devraient donc �tre de plus en plus performantes.

Le programe ne comporte aucun algorithme de r�solution certaine, donc il ne peut pas "aider". Si la r�solution simul�e �choue, le programme ne comporte pas de moyen de conna�tre la grille r�solue. A l'inverse il ne permet pas de faire des erreurs et il n'y a donc pas besoin de "v�rification". Les raisonnements sont limit�s mais ne sont pas faux et les chiffres trouv�s sont correctement plac�s. Le joueur peut donc �chouer mais il ne peut pas "se tromper".

Une interface compl�te permet de suivre le raisonnement, les prises de d�cision, les informations recherch�es et observ�es dans la grille, les techniques choisies ainsi que leur d�roulement. Elle permet �galement de suivre les limites et d�faillance de m�moire qui obligent parfois � devoir rechercher des informations pr�c�demment connues ou � devoir reprendre un raisonnement � son d�but. A l'inverse la r�solution peut �tre ex�cut�e sans aucun affichage jusqu'� son r�sultat : r�solution ou �chec, ainsi que log et statistiques. Le d�tail et les domaines d'informations sorties / affich�es sont largement param�trables, allant jusqu'� la capacit� de test du code au niveau �l�mentaire. 
Il est possible d'ex�cuter des r�solutions simultan�es en batch, par exemple dans le but d'en comparer les r�sultats, un peu � l'exemple des parties simultan�es d'�checs et autres jeux de r�flexion.

### Impl�mentation du r�alisme :

**Classe SudoThinking** -- la r�flexion qui permet d'encha�ner logiquement des actions et de d�rouler des techniques syst�matiques. Les limites cognitives plafonnent la complexit� de cette r�flexion et la capacit� de combiner des informations et des actions.

**Classe SudoMemory** -- La m�moire qui permet de savoir ce que l'on est en train de faire, ce que l'on voit, ce que l'on pense. C'est donc ce que l'on appelle une m�moire de travail. Elle est limit�e de mani�re r�aliste par la quantit� d'informations et l'oubli plus ou moins rapide.
Remarque : la r�solution se fait sans notes, enti�rement de m�moire.

**Classe SudoGridView** -- la recherche visuelle dans la grille. Le simulateur ne dispose d'aucun moyen de connaissance et m�morisation compl�te de la grille. Celle-ci ne peut �tre connue que de mani�re parcellaire, ce qui n�cessite de l'explorer du regard � la recherche d'informations, des chiffres pr�sents, des cases vides et de leurs combinaisons. La m�moire permet au joueur de se rem�morer plus ou moins longtemps ce qu'il a vu de la grille.

**Classes SudoTechxxxxxx** -- des techniques de r�solution r�alistes, qui consistent en encha�nements logiques et syst�matiques dans tout ou partie de la grille � la recherche d'informations (donc des observations de la grille), qui aboutissent �ventuellement � la d�couverte d'un placement possible.

**Classes SudoThinkAI et SudoAIxxxx** -- la r�flexion de plus haut niveau (sorte d'intelligence artificielle), la capacit�s de d�cision, l'�valuation d'opportunit�s, la prise en compte d'intuitions, la notion de choix "prudent" ou au contraire "optimiste" voire "agressif". D'une part le programme reproduit des techniques de r�solution simples (autrement dit des raisonnements logiques) et d'autre part il tente d'appliquer la bonne technique au bon moment. Par exemple il cherche des coups triviaux (ex: s'il reste une seule case libre dans un carr�) et des opportunit�s apparues apr�s un placement. S'il applique une technique qui ne donne rien, il va l'abandonner et en choisir une autre.

**Classe SudoLearning** -- la capacit� d'apprentissage, tant au fil de la r�solution d'une grille que d'une grille � l'autre. Par exemple les encha�nements qui "marchent" plus ou moins bien selon que la grille est plus ou moins remplie, ou au contraire ce qui est de la perte de temps.

**Classe SudoPlayerProfile** -- le param�trage des capacit�s du joueur dans tous les aspects de r�flexion, m�moire, vision de la grille, intuition et habilet�, apprentissage.

### Impl�mentations de bas niveau

**Classe SudoGrid** -- Mod�lisation de la grille. C'est la seule classe li�e � la simulation qui est exempte du besoin de r�alisme. 
Une seule autre classe acc�de � SudoGrid, c'est SudoGridView qui simule les "observations" de la grille. Aucune autre classe de simulation, notamment SudoThinking et SudoMemory, n'y a un acc�s direct, et le code source de ces classes n'importe m�me pas le module dans lequel est cod�e SudoGrid.

**Classe SudoRules** -- D�finit les r�gles du Sudoku qui sont la liste de 1 � 9 et les unicit�s de chiffres par groupement. SudoRules est utilis�e dans SudoGrid et dans le code qui effectue les placements pour en v�rifier la r�gularit�. D�finit aussi la hi�rarche des exceptions utilis�es dans le programme, principalement pour prendre en compte les d�faillance de m�moire et de r�flexion.

### Impl�mentations des fonctions techniques :

**Classe SudoEnv** -- L'environnemnet de la simulation : regroupe toutes les interfaces, les interactions, les affichages.

**Classe SudoUI et SudoGUI** -- Les interfaces utilisateurs, dont GUI bas� sur Tkinter.

**Classe SudoTest** -- Les fonctions de test et d'affichage conditionnel pr�sentes dans tout le code source du programme.

### Interfaces :

Une interface graphique repose sur Tkinter et Tix. Elle est enti�rement compatible avec le paradigme �v�nementiel. Elle permet une ex�cution du simulateur seul ainsi que l'int�gration sous forme de package dans un programme ext�rieur et l'int�gration dans l'interface GUI �v�nementielle dudit programme.
La modularit� de l'interface utilisateur permet ais�ment de modifier ou d'ajouter d'autres modes d'E/S (ex: console) ou d'autres librairies GUI.
Une interface syst�me permet de lire et �crire des fichiers format�s qui d�finissent une grille, ainsi que d'enregister en fichier des logs d'ex�cution, des statistiques de performance et des progressions. Il y a plusieurs formats de mod�lisations de grille qui permettent facilement d'interfacer avec des g�n�rateurs de grilles al�atoires.
Il n'y a aucune d�pendance du syst�me sous-jacent ni de sa distribution et seules les librairies Python standards sont utilis�es.


### Note sur le d�veloppement et sur le code : 

Le code privil�gie une utilisation propre et compl�te de Python, dans un style lisible pour ne pas dire scolaire. C'est du Python 3, la compatibilit� avec Python 2.7 n'est pas assur�e. Les commentaires et sauts de lignes sont abondants au d�triment volontaire de la compacit�. Toutes les classes et fonctions sont document�es de mani�re standard.
Le code est tr�s structur�, les noms de variables et d'objets sont compos�s et explicites. Le d�coupage et la modularit� sont fins avec des fonctions nombreuses et courtes pour la claret� et la lisibilit�. Les modules sont nombreux et la plupart codent une seule classe. Le paradigme objet est strictement respect�, il n'y a pas de variables globales � part des constantes, il n'y a quasiment pas de fonctions � l'ext�rieur des classes. A l'inverse, le code utilise autant que possible tous les types de collections, d'it�rations, des fonctions lambda. Les classes utilisent des m�thodes courtes, simples et nombreuses ainsi que des propri�t�s, seters et geters. Il y a de l'h�ritage de classes. Le code utilise syst�matiquements les exceptions et le contr�le de leur propagation partout o� cela est pertinent.Le programme est regroup� dans un package et des sous-packages et utilise abondamment les imports. 

Le d�veloppement a �t� conduit en totalit� dans une d�marche "test-driven" afin d'en optimiser la qualit�. C'est d'ailleurs un effort qui a �t� largement b�n�ficiaire gr�ce � un besoin de d�buggage tr�s limit�. Tout le code, chaque fonction et m�thode, contient du code de suivi d'ex�cution � un niveau tr�s fin et param�tr�, y compris des pauses d'ex�cution et des tests conditionnels. 
Tout les modules sont ex�cutables directement dans un interpr�teur (if __name__ == "__main__" ....) et comportent � la fin du code de test qui a �t� utilis� pendant le d�veloppement et n'a volontairement pas �t� supprim�. Bien s�r cet abondance de code "inutile" nuit � la rapidit� d'ex�cution, mais encore une fois celle-ci n'est pas un objectif et ce n'est pas perceptible dans la d�marche de simulation interactive qui est l'objectif du projet.

Pour ce qui est de l'import du package dans un programme "ext�rieur", ce dernier peut facilement param�trer la propagation des exceptions et l'ex�cution conditionnelle du code de test int�gr�.

Suite du projet

C'est un projet �volutif car il est toujours possible d'am�liorer le r�alisme de la simulation, d'ajouter de nouvelles techniques et d'en int�grer l'utilisation via l'AI, d'enrichir la capacit� de d�cision en prenant en compte plus de combinaisons de situations, d'affiner les profils de capacit�s et limitations de m�moire et de r�flexion. Un domaine particulier � d�velopper est la mod�lisation de la m�moire : car la m�moire humaine est associative d'une mani�re quasi-infinie. Cela est tr�s difficile � simuler. De m�me pour l'intelligence artificielle en d�veloppant des r�seaux de neurones.

Pour am�liorer le "niveau" de r�solution en conservant le r�alisme, il faudra incontournablement ajouter des techniques plus puissantes. En revanche celles-ci sont en g�n�ral plus longues � ex�cuter dans la r�alit�, donc vouloir les utiliser syst�matiquement (pour leur puissance) plut�t que des techniques plus simples irait � l'encontre du r�alisme de recherche de simplicit� et de rapidit�. Ajouter des techniques va donc de pair avec leur prise en compte pr�cise dans l'AI et le syst�me de d�cision.

Il y a donc dans l'ensemble un gros potentiel pour prolonger ce projet et am�liorer le niveau de jeu tout en am�liorant le r�alisme de la simulation.