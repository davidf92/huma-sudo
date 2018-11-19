'''Module 'main_test' : Fonctions utilitaires pour les tests réalisés
dans le shell directement depuis les scripts. Celles-ci incluent :
- Lecture de fichiers de grilles
- Initialisation de grilles
- Initialisation d'interface GUI
Grâce à ces fonctions la "plate-forme" de test est rapidement prête. Il ne
reste plus qu'à écrire le code de test spécifique à chaque module.
'''

from sudosimu.sudogame import *
from sudosimu import sudotestall
from sudosimu.sudogrid import SudoGrid

from test_modules import *

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
    '''Demande à l'utilisateur (console) de choisir une nouvelle grille, puis
    initialise une partie avec cette grille.
    '''
    global gridInit
    gridInit = testNewGrid()
    return newGame()
def resetGrid():
    '''Prépare ou réinitialise la grille de jeu comme copie de la grille
    choisie. ResetGrid() est utilisée quand une nouvelle grille est chargée,
    ainsi que quand une nouvelle partie est initialisée pour la même grille.
    '''
    global grid
    global gridInit
    if not isinstance(gridInit, SudoGrid):
        print("Erreur, il n'y a pas de grille chargée.")
        return False
    grid = gridInit.copy()
    testShowGrid(grid)
    return True
def newGame():
    '''Initialise une nouvelle partie sur la grille déjà chargée.'''
    global grid
    global mem
    global think
    global view
    global game
    if not resetGrid():
        return False
    mem = SudoMemory()
    think = SudoThinking(mem)
    view = SudoGridView(grid)
    game = SudoGame(mem, think, view)
    return True
def play(newParams=None):
    global params
    if newParams is None:
        r = game.play(params)
    else:
        r = game.play(newParams)
    return r
def resume():
    return game.resume()
def again():
    return game.again()
def step():
    return game.step()
def observe():
    return game.observe()
def place():
    return game.place()

#Initialisation des tests et de la partie
TEST.level("main", 1)
TEST.display("main", 1, "\nTest du module sudogame")
TEST.display("main", 1, "----------------------------\n")
newGrid()
ui.display("Création  et initialisation de la partie")
newGame()
#Niveaux de commentaires pour la partie
TEST.level("thinkai", 1)

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

