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
TEST = mainEnv.test
TEST.test("main", 2)

print("test : " + str(TEST.keys))

#Quel est le mode UI initial ?
print("Dans test_sudosimpleapp.py")
print("ui.__guimode = " + str(ui.__uimode))

ui.display("\nTest du module sudosimpleapp")
ui.display("----------------------------\n")

TEST.levelAll(0)  #par défaut niveaux à 0 pour toute la simulation
TEST.test("simpleapp", 1)

ui.display("Création de l'app.")
app = su.SimpleApp(env=mainEnv)

ui.display("ui.display() avant app.makeUI.")
app.makeUI()
ui.display("ui.display() après app.makeUI.")
#print("Après app.makeUI, ui.__guimode = " + str(ui.__uimode))

app.newPlayer("David")
#TEST.levelAll(0)
TEST.test("thinkai", 0)
TEST.test("ai", 0)
TEST.test("aicrit", 0)
TEST.test("airule", 0)
TEST.test("aitact", 1)
app.newGrid()

ui.display("L'application est prête pour un essai de résolution.")

#test de l'ai
tai = app._game._think._thinkAI
ai = tai._ai
data = ai._data
crits = ai._crits
rules = ai._rules

#app.solve()

