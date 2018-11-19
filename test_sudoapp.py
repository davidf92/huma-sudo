'''Module 'main_test' : Fonctions utilitaires pour les tests réalisés
dans le shell directement depuis les scripts. Celles-ci incluent :
- Lecture de fichiers de grilles
- Initialisation de grilles
- Initialisation d'interface GUI
Grâce à ces fonctions la "plate-forme" de test est rapidement prête. Il ne
reste plus qu'à écrire le code de test spécifique à chaque module.
'''

from sudosimu.sudoapp import *
#from sudosimu.sudogrid import SudoGrid

from test_modules import *
from sudosimu import sudotestall

#interface
testlev(0)
testMakeUI()
#données de jeu
grid = None
gridInit = None
mem = None
think = None
view = None
game = None
params = None
#fonctions de jeu
def newGrid():
    global gridInit
    gridInit = testNewGrid()
    newGame()
    return
def resetGrid():
    global grid
    global gridInit
    grid = gridInit.copy()
    testShowGrid(grid)
    return
def newGame():
    global grid
    global mem
    global think
    global view
    global game
    resetGrid()
    mem = SudoMemory()
    think = SudoThinking(mem)
    view = SudoGridView(grid)
    game = SudoGame(mem, think, view)
    return
def go():
    global game
    game.play(params)
    return

#Initialisation des tests et de la partie
TEST.level("main", 1)
ui.display("\nTest du module sudoapp")
ui.display("----------------------\n")

TEST.level("app", 3)
ui.display("Création  et initialisation de l'application...")
app = SudoApp()
ui.display("Initialisation de l'interface utilisateur...")
app.makeUI()
ui.display("Création d'un joueur...")
app.newPlayer("David")
ui.display("Chargement d'une grille...")
g = app.newGrid()

ui.display("L'application est prête pour un essai de résolution.")
g.show()



#Paramètres de la partie
params = None
#jeu
TEST.display("main", 1, "Prêt à jouer.")
print("\n...>>> game.play(params) \nou >>> go()")

#ui.sudoPause()
#go()
    


##    #TEST     
##    import sudotestall
##    from sudogrid import SudoGrid, SudoBloc
##    testlevel = 3
##    TEST.levelAll(testlevel)
##    ui.display("Tous les niveaux de test sont à {0}".format(testlevel))
##
##    #mode GUI
##    ui.UImode(ui.GUI)
##    TEST.displayUImode(MODE_BOTH, 1)
##
##    TEST.display("main", 1, "\nCréation de la grille.")
##    grid = SudoGrid()
##    gridInit = SudoGrid()
##    newGrid()
##    ui.displayGridAll(grid)
##
##    TEST.display("main", 1, "\nCréation de la partie.")
##    mem = None
##    think = None
##    view = None
##    game = None
##    gameParam = (mem, think, view, game)
##    #newGame(grid)
##    (mem, think, view, game) = newGame(grid)
##    
##    TEST.display("main", 1, "Ok prêt à jouer")
##
##    TEST.levelAll(0)
##    TEST.level("thinkai", 1)
###    TEST.level("game", 1)
##    

