'''Module 'test_sudoai' (fichier test_sudoai.py): Test du module 'sudoai'.
'''

import sudosimu as su
import sudosimu.sudoui as ui
import sudosimu.sudoai as ai

def resdata():
    '''Liste les données en cours de la résolution.'''
    ui.display("Données de résolution :")
    ui.display("ai.ai_begin = " + str(ai.ai_begin))
    ui.display("ai.ai_niv = " + str(ai.ai_niv))
    ui.display("ai.ai_nivmax = %s" % (ai.ai_nivmax))
    ui.display("ai.ai_intech = " + str(ai.ai_intech))
    ui.display("ai.ai_tech = " + str(ai.ai_tech))
    ui.display("ai.ai_ltech = " + str(ai.ai_ltech))
    ui.display("ai.ai_opport = " + str(ai.ai_opport))
    ui.display("ai.ai_lact = " + str(ai.ai_lact))

def show():
    '''Liste la valeur actuelle de tous les critères et règles.'''
    cr.show()
    ui.display("")
    ru.show()

def simu_begin():
    ai.ai_begin = True
    ai.ai_niv = 0
    ai.ai_nivmax = 2
    ai.ai_intech = False
    ai.ai_tech = None
    ai.ai_ltech = None
    ai.ai_lact = None
    ai.ai_opport = False
    ui.display("Simulation : dans Techchrc.")
    resdata()
    sai.update()
    ui.display("Règles mises à jour.\n")
    cr.show()
    ru.show()
    
def simu_inchrc():
    ai.ai_begin = False
    ai.ai_niv = 1
    ai.ai_nivmax = 2
    ai.ai_intech = True
    ai.ai_tech = "techchrc"
    ai.ai_ltech = "techlplc"
    ai.ai_lact = "obs"
    ai.ai_opport = False
    ui.display("Simulation : dans Techchrc.")
    resdata()
    sai.update()
    ui.display("Règles mises à jour.\n")
    cr.show()
    ru.show()

def simu_inchrcend():
    ai.ai_begin = False
    ai.ai_niv = 1
    ai.ai_nivmax = 2
    ai.ai_intech = True
    ai.ai_tech = "techchrc"
    ai.ai_ltech = "techlplc"
    ai.ai_lact = "end"
    ai.ai_opport = False
    ui.display("Simulation : dans Techchrc.")
    resdata()
    sai.update()
    ui.display("Règles mises à jour.\n")
    cr.show()
    ru.show()

def simu_inchrcplace():
    ai.ai_begin = False
    ai.ai_niv = 1
    ai.ai_nivmax = 2
    ai.ai_intech = True
    ai.ai_tech = "techchrc"
    ai.ai_ltech = "techlplc"
    ai.ai_lact = "place"
    ai.ai_opport = False
    ui.display("Simulation : dans Techchrc.")
    resdata()
    sai.update()
    ui.display("Règles mises à jour.\n")
    cr.show()
    ru.show()

#Commencer par créer un environnement pour ce script afin d'avoir une UI,
#et un système de test par défaut.
env = su.Env("mainEnv")
TEST = env.test
TEST.test("main", 2)
TEST.test("player", 4)

print("test : " + str(TEST.keys))

#Quel est le mode UI initial ?
print("Dans test_sudosimpleapp.py")
print("ui.__guimode = " + str(ui.__uimode))

ui.display("\nTest du module sudosimpleapp")
ui.display("----------------------------\n")

TEST.levelAll(0)  #par défaut niveaux à 0 pour toute la simulation
#ok ça marche #print("test : " + str(TEST.keys))

#ai.TEST.level("ai", 3)
ui.display("Ok environnement prêt pour AI")

ui.display("Création du système AI : sai = ai.SudoAI")
mem = su.SudoMemory()
sai = ai.SudoAI(mem, env=env)

ui.display("\nRécupération des données : data = sai.data")
data = sai.data

ui.display("\nToutes les données du système : sai.show()")
sai.show()




