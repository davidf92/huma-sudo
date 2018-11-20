'''Application Sudoku qui utilise le package SudoSimu.
Utilise aussi le script 'main-test.py' qui contient quelques fonctions
utilitaires pour des tests applicatifs.
'''

import sudosimu as sudo
import sudo.sudotestall
from sudosimu.sudotest import *
import sudo.sudotestall
from main_test import *

#interface
testlev(0)
testMakeUI()

#fonctions de renouvellement du jeu
grid = None
def newGrid():
    global grid
    grid = testNewGrid()
    testShowGrid(grid)
    return
david = None
def go():
    global david
    resetGrid()
    david.solve(grid, params)
    return
def resetGrid():
    global grid
    testShowGrid(grid)
    return

#Initialisation des tests
TEST.level("main", 1)
ui.display("\nTest du module sudoplayer")
ui.display("----------------------------\n")
newGrid()
TEST.display("main", 1, "\nCréation et initialisation du joueur")
TEST.display("main", 1, "Création du joueur : 'david'")
david = SudoPlayer("David")
#Niveaux de commentaires pour la partie
TEST.level("thinkai", 1)
#    TEST.level("player", 3)
#    TEST.level("game", 3)


#Paramètres de la partie
params = None
#Jeu
TEST.display("main", 1, "Prêt à jouer.\n")
print("\n...>>> david.solve(grid) \nou >>> go()")

#ui.sudoPause()
#go()
    
