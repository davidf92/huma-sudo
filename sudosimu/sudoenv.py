# -*- coding: cp1252 -*-

'''Programme SudoSimu - Simulation de r�solution humaine du jeu de Sudoku.
Module sudoenv : environnement logiciel d'ex�cution du simulateur.

L'environnement, � travers la classe SudoEnv, regroupe l'ensemble du contexte
d'interface utilisateur, de log d'informations, d'acc�s � des biblioth�ques de
grilles, etc. Des environnements permettent par exemple de r�aliser facilement
de l'ex�cution en batch de r�solutions en grandes quantit�s, sans interface
utilisateur, ou de faire des tests en interface console, ou en interface
graphique.
Les environnements sont construits comme une hi�rarchie de classes, ce qui
permet d'en cr�er facilement de nouveaux, par exemple pour un nouveau
framework GUI.

Une sous-classe particuli�re, SudoEnvQuiet, permet de supprimer totalement
les outputs, ce qui est utile pour des utilisations en batch (r�solutions
massives, apprentissage, etc.)

Derni�re mise � jour : 15/11/2017

Historique des modifications :
15/11/2017 - Evolution pour utiliser le syst�me d'environnement avec SudoEnv
    ainsi que tout le support de TEST dans sudoenv.
'''

if __name__ in ("__main__", "sudoenv"):
    import sudorules as rules
    import sudotest
    import sudoui as ui
elif __name__ == "sudosimu.sudoenv":
    from sudosimu import sudorules as rules
    from sudosimu import sudotest
    from sudosimu import sudoui as ui
else:
    raise Exception("Impossible de faire les imports dans le module sudoenv.")

#CONSTANTES
#Syst�me de test, label et niveau par d�faut
TEST_DEFAULTLABEL = "sudo"       #Label de test de code par d�faut
TEST_DEFAULTLEVEL = 0            #Niveau de test de code par d�faut
#Valeurs des niveaux de test par d�faut pour les diff�rents labels
TEST_APPLEVEL = 0
TEST_SIMPLEAPPLEVEL = 0
TEST_PLAYERLEVEL = 0
TEST_GAMELEVEL = 0
TEST_SIMULEVEL = 0
TEST_VIEWLEVEL = 0
TEST_MEMORYLEVEL = 0
TEST_THINKINGLEVEL = 0
TEST_THINKAILEVEL = 0
TEST_AILEVEL = 0
TEST_AIDATALEVEL = 0
TEST_AICRITLEVEL = 0
TEST_AIRULELEVEL = 0
TEST_AITACTSLEVEL = 0
TEST_AINODELEVEL = 0
TEST_AINODEINPUT = 0
#Reprise de constantes d�clar�es dans d'autres modules
STD = ui.STD
GUI = ui.GUI
UI_STD = ui.UI_STD
UI_GUI = ui.UI_GUI
UI_BOTH = ui.UI_BOTH

MODE_STD = sudotest.MODE_STD
MODE_GUI = sudotest.MODE_GUI
MODE_SELECT = sudotest.MODE_SELECT
MODE_BOTH = sudotest.MODE_BOTH
TEST_STD = sudotest.MODE_STD
TEST_GUI = sudotest.MODE_GUI
TEST_SELECT = sudotest.MODE_SELECT
TEST_BOTH = sudotest.MODE_BOTH

class SudoEnv():
    '''Cette classe repr�sente le concept d'environnement d'ex�cution du
    simulateur de Sudoku, incluant notamment l'interface utilisateur et des
    �l�ments d'interface syst�me comme les fichiers.
    '''
    def __init__(self, envname=None, testclass=None):
        '''Initialisation d'un environnement d'ex�cution. Celui contient au
        minimum les objets UI qui permettent des outputs de d�roulement de la
        r�solution. Cet environnement peut utiliser optionnellement une autre
        classe que 'SudoTest' pour le test du code.
        '''
##########################
##        print("TEST SudoEnv(__init__(), envname={0}, testclass={0}"\
##              .format(str(envname), str(testclass)))
##        print("type(testclass) = " + str(type(testclass)))
##        print(testclass)
##        print(sudotest.SudoTest)
##        print(isinstance(testclass, sudotest.SudoTest))
##        print()
###########################
        assert envname is None or isinstance(envname, str)
        self._name = envname
#Param�tre 'testclass': si ce n'est pas SudoTest, c'est � son d�veloppeur de
#s'assurer que cette classe supporte bien toutes les m�thodes utilis�es.
        if testclass is None:
            self._test = sudotest.SudoTest()
        else:
            self._test = testclass()
#### A MODIFIER IMPERATIVEMENT APRES EVOLUTION DU MODULE SUDOUI
        #interface UI
        self._ui = ui   #c'est le module - ni une classe ni une instance.
        return
        
    def getTest(self):
        ''' Retourne l'objet de test (instance SudoTest) qui va permettre
        au code appelant d'utiliser directement cette interface.
        '''
        return self._test
    
    def setTest(self, testclass):
        '''Modifie la classe du syst�me de test de l'environnement.'''
        assert isinstance(testclass, sudotest.SudoTest)
        self._test = testclass()
        return

    test = property(getTest, setTest, doc=\
        '''Permet de faire dans le code :
        TEST = env.TEST
        TEST.display("<label>", <level>, "<Test output>)
        ''')
    TEST = test

    def setName(self, name):
        '''Modifie le nom de l'environnement = une cha�ne de caract�res.'''
        assert isinstance(name, str)
        self._name = name
        return

    def getName(self):
        '''Retourne le nom de l'environnement.'''
        return self._name

    name = property(getName, setName)

##Voir si l'on met aussi une m�thode setter et un attribut property pour ui
    @property
    def ui(self):
        return self._ui

    def display(self, text):
        '''Affiche un texte sur l'interface UI. Un texte vide fait afficher un
        saut de ligne '\n'.
        '''
        #important pour la s�curit� (faille par d�passement de buffer)
        assert isinstance(text, str) 
        return self._ui.display(text)
    
    def displayError(self, title, text):
        #important pour la s�curit� (faille par d�passement de buffer)
        assert isinstance(title, str) or title is None
        assert isinstance(text, str) or text is None
        return self._ui.displayError(title, text)

##Quelques m�thodes qui permettrent de param�trer ditectement le syst�me de test
    def testLabel(self, key, level=0):
        return self._test.test(key, level)

    def testLevel(self, key, level=None):
        return self._test.level(key, level)

    @property
    def testKeys(self):
        '''Retourne le dictionnaire de cl�s du syst�me de test de code de
        l'environnement.
        '''
        return self._test.keys

    def testDispKeys(self):
        '''Affiche en liste les cl�s du syst�me de test de code.'''
        keys = self._test.keys #dictionnaire des cl�s
        if len(keys) == 0:
            ui.display("Aucune cl� dans TEST.")
        else:
            for testkey in keys:
                ui.display("\"{0}\" : {1}".format(testkey, keys[testkey]))
        return
        
#end class SudoEnv
DEFAULT_ENV = SudoEnv           #Classe d'environnement par d�faut



class SudoEnvQuiet(SudoEnv):
    '''Cette sous-classe rend le syst�me de test silencieux et supprime
    les outputs de ses propres m�thodes.
    '''
    def __init__(self, envname=None, testclass=None):
        '''Ne tient pas compte des param�tres.'''
        self._name = "Quiet environment"
        self._test = sudotest.SudoTest()
        self._test.beQuiet(True)
        self._ui = ui
##Apr�s �volution du module 'sudoui'
        #self._ui.noOutput()
        return

    def display(self, text):
        '''N'affiche rien dans la classe SudoEnvQuiet.'''
        return

    def displayError(self, title, text):
        '''N'affiche rien dans la classe SudoEnvQuiet.'''
        return
                 
#end class SudoEnvQuiet
