'''test_package.py' : Fonctions utilitaires pour les tests unitaires dans
le package. Celles-ci incluent :
- Lecture de fichiers de grilles
- Initialisation de grilles
- Initialisation d'interface GUI
'''

import sudosimu
from sudosimu import sudoui as ui
from sudosimu import sudogrid as gr
from sudosimu import sudoplayer as pl
from sudosimu.sudotest import *
from sudosimu import sudotestall


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


