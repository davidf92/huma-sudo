# -*- coding: utf8 -*-

'''Programme SudoSimu - Simulation de résolution humaine du jeu de Sudoku.
Module sudoenv : environnement logiciel d'exécution du simulateur.

L'environnement, à travers la classe SudoEnv, regroupe l'ensemble du contexte
d'interface utilisateur, de log d'informations, d'accès à des bibliothèques de
grilles, etc. Des environnements permettent par exemple de réaliser facilement
de l'exécution en batch de résolutions en grandes quantités, sans interface
utilisateur, ou de faire des tests en interface console, ou en interface
graphique.
Les environnements sont construits comme une hiérarchie de classes, ce qui
permet d'en créer facilement de nouveaux, par exemple pour un nouveau
framework GUI.

Une sous-classe particulière, SudoEnvQuiet, permet de supprimer totalement
les outputs, ce qui est utile pour des utilisations en batch (résolutions
massives, apprentissage, etc.)

Dernière mise à jour : 25/11/2018
Historique des modifications :
25/11/2018 # -*- coding: utf8 -*-
23/11/2018 - Reprise pour bien fournir un système d'environnement généralisé
au programme, qui englobe les UI et les moyens de test (SudoTest)
15/11/2017 - Evolution pour utiliser le système d'environnement avec SudoEnv
    ainsi que tout le support de TEST dans sudoenv.
'''

if __name__ in ("__main__", "sudoenv"):
    import sudorules as rules
    import sudotest
#    from sudotestall import *   #constantes pour les tests
    import sudoui as ui

elif __name__ == "sudosimu.sudoenv":
    from sudosimu import sudorules as rules
    from sudosimu import sudotest
#    from sudosimu.sudotestall import *   #constantes pour les tests
    from sudosimu import sudoui as ui
else:
    raise Exception("Impossible de faire les imports dans le module sudoenv.")

#CONSTANTES
#Système de test, label et niveau par défaut
TEST_DEFAULTLABEL = "sudo"       #Label de test de code par défaut
TEST_DEFAULTLEVEL = 0            #Niveau de test de code par défaut
#Valeurs des niveaux de test par défaut pour les différents labels
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
#Reprise de constantes déclarées dans d'autres modules
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
    '''Cette classe représente l'environnement d'exécution du
    simulateur. Elle fournit aux autres modules une interface UI et GUI, ainsi
    qu'un environnement de test et des fonctions d'affichage dans une console.
    L'environnement peut éventuellement avoir un nom.
    '''
    def __init__(self, envname=None, testclass=None):
        '''Initialisation un environnement d'exécution et des interfaces que
        l'environnement fournit. 
        '''
        #vérificatioin des paramètres
        try:
            assert envname is None or isinstance(envname, str)
        except:
            raise Exception("Erreur d'initialisation de l'environnement.")
        if envname is None or envname == "":
            envname = "Environnement"
        self._name = envname
#Paramètre 'testclass': permet d'utiliser une autre classe de test que celle
#incluse dans sudosimu. C'est à son développeur de s'assurer que cette autre
#classe supporte bien toutes les méthodes de SudoTest
        if testclass is None:
            self._test = sudotest.SudoTest()
        else:
            self._test = testclass()

#### A MODIFIER IMPERATIVEMENT APRES EVOLUTION DU MODULE SUDOUI qui devrait
#### créer une classe SudoUI et donc instancier self._ui = SudoUI()
        #interface UI
        self._ui = ui   #c'est le module - ni une classe ni une instance.

        return
        
    def getTest(self):
        ''' Retourne l'instance d'environnement de test.'''
        return self._test
    
    def setTest(self, testclass):
        '''Permet d'utiliser un autre environnement de test créé extérieurement'''
        try:
            assert isinstance(testclass, sudotest.SudoTest)
        except:
            raise Exception("Erreur d'initialisation de l'environnement.")
        self._test = testclass()
        return

    test = property(getTest, setTest)

## VERIFIER L'UTILITE DE CE CODE
## Permettre de faire dans le code : TEST = env.TEST
## et utiliser TEST.display() et les autres
    TEST = test

    def setName(self, name):
        '''Modifie le nom de l'environnement = une chaîne de caractères.
        Le nom ne peut pas être vide'''
        assert isinstance(name, str) and not name==""
        self._name = name
        return

    def getName(self):
        '''Retourne le nom de l'environnement.'''
        return self._name

    name = property(getName, setName)

#### EVOLUTION : Voir si l'on met permet d'assigner un autre environnement 
#### d'interface UI défini extérieurement. Permettrait à plusieurs instances de
#### simulation de partager une interface UI commune.    
#### Dans ce cas ajouter getter + setter.
    @property
    def ui(self):
        return self._ui

##Méthodes d'affichage
    def display(self, text=None):
        '''Affiche un texte sur l'interface UI. Identique à ui.display().
        Un texte vide fait afficher un saut de ligne '\n'.
        '''
        #important pour la sécurité (faille par dépassement de buffer)
        assert isinstance(text, str) 
        return self._ui.display(text)
    
    def displayError(self, title=None, text=None):
        '''Affiche une erreur avec la fonction de ui d'affichage avec titre.
        Le texte d'erreur ne devrait pas être vide donc exception dans ce cas.
        S'il n'y a qu'un seul paramètre, l'utilise comme texte avec titre "Erreur"
        '''
        #important pour la sécurité (faille par dépassement de buffer)
        assert isinstance(title, str) or title is None
        assert isinstance(text, str) or text is None
        #s'il n'y a qu'un seul paramètre il devient le texte et non le titre
        if (title is not None and not title == "") \
           and (text is None or text == ""):
            text = title
            title = "Erreur"
        elif title is None or title == "":
            title = "Erreur"
        return self._ui.displayError(title, text)

##Quelques méthodes qui permettrent de paramétrer ditectement le système de test
    def testLabel(self, key, level=0):
        return self._test.test(key, level)

    def testLevel(self, key, level=None):
        return self._test.level(key, level)

    @property
    def testKeys(self):
        '''Retourne le dictionnaire de clés du système de test de code de
        l'environnement.
        '''
        return self._test.keys

    def testDispKeys(self):
        '''Affiche en liste les clés du système de test de code.'''
        keys = self._test.keys #dictionnaire des clés
        if len(keys) == 0:
            ui.display("Aucune clé dans TEST.")
        else:
            for testkey in keys:
                ui.display("\"{0}\" : {1}".format(testkey, keys[testkey]))
        return
        
#end class SudoEnv
DEFAULT_ENV = SudoEnv           #Classe d'environnement par défaut



class SudoEnvQuiet(SudoEnv):
    '''Cette sous-classe rend le système de test silencieux et supprime
    tous les affichages quand les méthodes de SudoEnv sont utilisées.
    '''
    def __init__(self, envname=None):
        '''Reprend l'initialisation de la classe SudoEnv. S'il n'y a pas de
        nom mettre un nom explicite.
        '''
        if envname is None or \
           (isinstance(envname, str) and envname == ""):
            envname = "Silencieux"
        SudoEnv.__init__(self, envname)
        self._test.isQuiet = True

#### EVOLUTION - Après évolution du module 'sudoui' avec classe SudoUI:
        #self._ui.noOutput()
        
        return

    def display(self, text=None):
        '''N'affiche rien dans la classe SudoEnvQuiet.'''
        return

    def displayError(self, title=None, text=None):
        '''N'affiche rien dans la classe SudoEnvQuiet.'''
        return
                 
#end class SudoEnvQuiet

