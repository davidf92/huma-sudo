'''Module 'main_test' : Fonctions utilitaires pour les tests réalisés
dans le shell directement depuis les scripts. Celles-ci incluent :
- Lecture de fichiers de grilles
- Initialisation de grilles
- Initialisation d'interface GUI
Grâce à ces fonctions la "plate-forme" de test est rapidement prête. Il ne
reste plus qu'à écrire le code de test spécifique à chaque module.
'''

import sudosimu as su
import sudosimu.sudoui as ui

#Commencer par créer un environnement pour ce script afin d'avoir une UI,
#et un système de test par défaut.
mainEnv = su.Env("mainEnv")
TESTAPP = mainEnv.test
TESTAPP.test("main", 2)

#pour avoir TEST des modules de techniques qui n'utilient pas 'env'
from sudosimu.sudotest import *
print("sudoenv.TEST : " + str(TEST.keys))
print("su.Env.test : " + str(TESTAPP.keys))

#Quel est le mode UI initial ?
print("Dans test_sudosimpleapp.py")
print("ui.__guimode = " + str(ui.__uimode))

ui.display("\nTest du module sudosimpleapp")
ui.display("----------------------------\n")

TEST.levelAll(0)  #par défaut niveaux à 0 pour toute la simulation
#ok ça marche #print("test : " + str(TEST.keys))

ui.display("Création d'une application de support de test")
app = su.SimpleApp(env=mainEnv)
TESTAPP.test("simpleapp", 3)
TESTAPP.test("player", 3)
TESTAPP.test("ai", 1)
TESTAPP.test("thinkai", 3)

ui.display("ui.display() avant app.makeUI.")
app.makeUI()
ui.display("ui.display() après app.makeUI.")
print("Après app.makeUI, ui.__guimode = " + str(ui.__uimode))

app.newPlayer("David")
app.newGrid()

ui.display("Création des variables de test 'game', 'mem', 'think'.")
game = app.game
mem = game._mem
think = game._think
tai = think._thinkAI
ai = tai._ai
ui.display("Import de TechLastPlcPlace")
from sudosimu.techlplc.techlplcp import TechLastPlcPlace
ui.display("Import de sudotest.* pour avoir TEST des techniques.")
from sudosimu.sudotest import *
ui.display("Réglage des niveaux de TEST")
TESTAPP.levelAll(0)
TESTAPP.test("thinkai", 3)

TEST.test("techlplcplace", 3)
TEST.test("techlplcrow", 1)
TEST.test("techlplccol", 1)
TEST.test("techlplcsqr", 1)

ui.display("Création d'une instance de TechLastPlcPlace pour la case (7,9)")
tech = TechLastPlcPlace(mem, (7,9))
ui.display("L'application est prête pour un essai avec 'tech' ")


