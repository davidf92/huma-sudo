# -*- coding: utf8 -*-

'''Module sudotestall du programme sudosimu : simulation de jeu de Sudoku.
Initialise le dictionnaire des labels de test pour tous les modules du
programme. Sert à exécuter des tests avec un dictionnaire prérempli de
ces labels pour utiliser la méthode levelAll(). Inutile en dehors de tests.

Ce module n'est pas requis. Cependant pour l'utiliser il faut l'importer
**après** l'import de sudotest.py, par exemple :
   import sudotest
   import sudotestall
'''

if "sudosimu." in __name__:
    from sudosimu.sudotest import *
else:
    from sudotest import *
    
#utilisé pour le contrôle d'exécution
TEST.test("__nofail__")
TEST.test("__noexcept__")
#utilisé pour les tests unitaires
TEST.test("main")
TEST.test("loop")
TEST.test("step")
TEST.test("all")
#support applicatif avec l'import complet du package
TEST.test("sudoku")
TEST.test("app")
TEST.test("simpleapp")
TEST.test("simu")
TEST.test("player")
TEST.test("game")
#interfaces
TEST.test("ui")
TEST.test("gui")
#simulation de résolution
TEST.test("grid")
TEST.test("observer")       #OBSOLETE
TEST.test("gridview")
TEST.test("memory")
TEST.test("memprofile")
TEST.test("thinking")
TEST.test("thinkprofile")
TEST.test("thinkai")
TEST.test("thinktech")
TEST.test("ai")
#techniques de résolution
#'chiffre/rang-colonne'
TEST.test("techchrcrow")
TEST.test("techchrccol")
TEST.test("techchrcplc")
TEST.test("techchrcgrid")
TEST.test("techchrcgridall")
#'dernier placement'
TEST.test("techlplcrow")
TEST.test("techlplccol")
TEST.test("techlplcsqr")
TEST.test("techlplcplc")
TEST.test("techlplcgrid")
        
