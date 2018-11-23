'''Module sudotestall du programme sudosimu : simulation de jeu de Sudoku.
Initialise le mode de test pour l'exécution des autres modules. Cette
initialisation permet de remplir le dictionnaire des labels de test et de
vérifier ensuite que les niveaux correspondent aux valeurs attendues.
'''

if __name__ in ("__main__", "sudotestall"):
    import sudoenv
elif __name__ == "sudosimu.sudotestall":
    from sudosimu import sudoenv
else:
    raise Exception("Impossible de faire les imports dana le module sudotestall")

'''l'utilisation normale consiste à importer ce module dans un autre module
à la suite de l'initialisation du code de test, pour utiliser l'environnement
déjà créé et donc TEST déjà défini.
Dans le cas contraire :
'''
try:
    _dummy_ = TEST
except:
    env = sudoenv.SudoEnv()
    TEST = env.test

#utilisé pour le contrôle d'exécution
TEST.test("__nofail__")
TEST.test("__noexcept__")
#utilisé pour les tests unitaires
TEST.test("main")
TEST.test("loop")
TEST.test("step")
TEST.test("all")

#support applicatif
TEST.test("sudoku")
TEST.test("app")
TEST.test("simpleapp")
#interfaces
TEST.test("ui")
TEST.test("gui")
#simulation de résolution
TEST.test("grid")
TEST.test("simu")
TEST.test("player")
TEST.test("game")
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


