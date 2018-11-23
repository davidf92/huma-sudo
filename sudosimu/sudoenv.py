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

Derni�re mise � jour : 23/11/2018
Historique des modifications :
23/11/2018 - Reprise pour bien fournir un syst�me d'environnement g�n�ralis�
au programme, qui englobe les UI et les moyens de test (SudoTest)
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
    '''Cette classe repr�sente l'environnement d'ex�cution du
    simulateur. Elle fournit aux autres modules une interface UI et GUI, ainsi
    qu'un environnement de test et des fonctions d'affichage dans une console.
    L'environnement peut �ventuellement avoir un nom.
    '''
    def __init__(self, envname=None):
        '''Initialisation un environnement d'ex�cution et des interfaces que
        l'environnement fournit. 
        '''
        #v�rificatioin des param�tres
        try:
            assert envname is None or isinstance(envname, str)
        except:
            raise Exception("Erreur d'initialisation de l'environnement.")
        if envname is None or envname == "":
            envname = "Environnement"
        self._name = envname
        self._test = sudotest.SudoTest()

#### A MODIFIER IMPERATIVEMENT APRES EVOLUTION DU MODULE SUDOUI qui devrait
#### cr�er une classe SudoUI et donc instancier self._ui = SudoUI()
        #interface UI
        self._ui = ui   #c'est le module - ni une classe ni une instance.

        return
        
    def getTest(self):
        ''' Retourne l'instance d'environnement de test.'''
        return self._test
    
    def setTest(self, testclass):
        '''Permet d'utiliser un autre environnement de test cr�� ext�rieurement'''
        try:
            assert isinstance(testclass, sudotest.SudoTest)
        except:
            raise Exception("Erreur d'initialisation de l'environnement.")
        self._test = testclass
        return

    test = property(getTest, setTest)

    def setName(self, name):
        '''Modifie le nom de l'environnement = une cha�ne de caract�res.
        Le nom ne peut pas �tre vide'''
        assert isinstance(name, str) and not name==""
        self._name = name
        return

    def getName(self):
        '''Retourne le nom de l'environnement.'''
        return self._name

    name = property(getName, setName)

#### EVOLUTION : Voir si l'on met permet d'assigner un autre environnement 
#### d'interface UI d�fini ext�rieurement. Permettrait � plusieurs instances de
#### simulation de partager une interface UI commune.    
#### Dans ce cas ajouter getter + setter.
    @property
    def ui(self):
        return self._ui

##M�thodes d'affichage
    def display(self, text=None):
        '''Affiche un texte sur l'interface UI. Identique � ui.display().
        Un texte vide fait afficher un saut de ligne '\n'.
        '''
        #important pour la s�curit� (faille par d�passement de buffer)
        assert isinstance(text, str) 
        return self._ui.display(text)
    
    def displayError(self, title=None, text=None):
        '''Affiche une erreur avec la fonction de ui d'affichage avec titre.
        Le texte d'erreur ne devrait pas �tre vide donc exception dans ce cas.
        S'il n'y a qu'un seul param�tre, l'utilise comme texte avec titre "Erreur"
        '''
        #important pour la s�curit� (faille par d�passement de buffer)
        assert isinstance(title, str) or title is None
        assert isinstance(text, str) or text is None
        #s'il n'y a qu'un seul param�tre il devient le texte et non le titre
        if (title is not None and not title == "") \
           and (text is None or text == ""):
            text = title
            title = "Erreur"
        elif title is None or title == "":
            title = "Erreur"
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
#DEFAULT_ENV = SudoEnv           #Classe d'environnement par d�faut



class SudoEnvQuiet(SudoEnv):
    '''Cette sous-classe rend le syst�me de test silencieux et supprime
    tous les affichages quand les m�thodes de SudoEnv sont utilis�es.
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

#### EVOLUTION - Apr�s �volution du module 'sudoui' avec classe SudoUI:
        #self._ui.noOutput()
        
        return

    def display(self, text=None):
        '''N'affiche rien dans la classe SudoEnvQuiet.'''
        return

    def displayError(self, title=None, text=None):
        '''N'affiche rien dans la classe SudoEnvQuiet.'''
        return
                 
#end class SudoEnvQuiet

