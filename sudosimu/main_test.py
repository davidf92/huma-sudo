'''Module 'main_test' : Fonctions utilitaires pour les tests réalisés
dans le shell directement depuis les scripts. Celles-ci incluent :
- Lecture de fichiers de grilles
- Initialisation de grilles
- Initialisation d'interface GUI
Grâce à ces fonctions la "plate-forme" de test est rapidement prête. Il ne
reste plus qu'à écrire le code de test spécifique à chaque module.
'''

import sudoui as ui
import sudogrid as gr
import sudoplayer as pl
from sudotest import *
import sudotestall

##import sudosimu
##from sudosimu import sudoui as ui
##from sudosimu import sudogrid as gr
##from sudosimu import sudoplayer as pl
##from sudosimu.sudotest import *
##from sudosimu import sudotestall

def testMakeUI():
    '''Prépare l'interface utilisateur console et graphique.'''
    ui.UImode(ui.GUI)
    TEST.displayUImode(MODE_BOTH, 1)

def testReadGridFileNum():
    ui.display("Choisir un fichier de test")
    fich = ui.sudoNumTestFich()
    if not fich:
        ui.display("Abandon")
        exit()
    ui.display("Fichier choisi : {0}\n".format(fich))
    vals = ui.sudoFichReadLines(fich)
    return vals

def testNewGrid():
    vals = testReadGridFileNum()
    grid = gr.SudoGrid()
    grid.fillByRowLines(vals)
    ui.display("Grille test choisie : grid = ")
    grid.show()
    #testShowGrid(grid)
##    ui.displayGridClear()
##    ui.displayGridAll(grid)
    return grid

def testlev(lev):
    TEST.levelAll(lev)

def testShowGrid(grid):
    ui.displayGridClear()
    ui.displayGridAll(grid)
    return    


#TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST
#TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST


if __name__ == "__main__":

    #installer l'interface
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
    david = pl.SudoPlayer("David")
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

