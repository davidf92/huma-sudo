'''Module 'sudobaseclass' : définit la classe racine des classes du simulateur
Cette classe présente des attributs et méthodes communs tels que l'intégration
dans l'environnement, l'intégration dans le système de test du code, ainsi que
diverses règles communes au fonctionnement de toutes les classes.
'''

'''
Historique des modifications :
15/11//2017 - Version initiale
'''

#import de l'environnement. Possible sans référence circulaire car les classes
#d'environnement ne dérivent pas de la classe racine.
from sudosimu import sudoenv

class SudoBaseClass(object):
    '''Classe racine pour la hiérarchie de classes du simulateur.
    Présente l'intégration de un environnement par défaut et dans le système
    de test de cet environnement.
    '''

    def __init__(self, env=None, testlabel=None, testlevel=None):
        #initialisation de l'environnement par défaut de l'instance
        #print("SudoBaseClass.__init__() - self = %s" % (str(self)))
        print("SudoBaseClass.__init__() - env = %s" % (str(env)))
        print("SudoBaseClass.__init__() - testlabel = %s" % (str(testlabel)))
        print("SudoBaseClass.__init__() - testlevel = %s" % (str(testlevel)))
        self._initEnv(env, testlabel, testlevel)
        return

    def _initEnv(self, env, testlabel, testlevel):
        '''Initialise un environnement qui sera l'environnement par défaut
        des classes dérivées, si celles-ci ne s'intègrent pas dans un autre
        environnement explicite.
        '''
        #print("SudoBaseClass._initEnv() - self = %s" % (str(self)))
        #print("SudoBaseClass._initEnv() - env = %s" % (str(env)))
        print("SudoBaseClass._initEnv() - testlabel = %s" % (str(testlabel)))
        print("SudoBaseClass._initEnv() - testlevel = %s" % (str(testlevel)))
        assert isinstance(env, sudoenv.SudoEnv) or env is None
        assert isinstance(testlabel, str) and len(testlabel)>0 \
                or testlabel  is None
        assert isinstance(testlevel, int) and testlevel>=0 \
                or testlevel is None
        #environnement par défaut s'il n'est pas spécifié
        if env is None:
            self._env = sudoenv.DEFAULT_ENV()
        else:
            self._env = env
        #système de test
        if testlabel is None:
            self._testlabel = sudoenv.TEST_DEFAULT_LABEL
        else:
            self._testlabel = testlabel
        if testlevel is None:
            self._testlevel = sudoenv.TEST_DEFAULT_LEVEL
        else:
            self._testlevel = testlevel
        #enregistrement du label dans le système de test
        self.envTestLevel(self._testlabel, self._testlevel)
        #ok
        TEST = self.env.TEST
        TEST.display(self._testlabel, 3, "SudoBaseClass - L'instanciation "\
                     "de la classe de base est terminée.")
        return True
        
    def setEnv(self, env):
        '''Indique un nouvel environnement pour la simulation.
        Ne fait rien ici car c'est toujours l'environnement de base.
        '''
        assert isinstance(env, sudoenv.SudoEnv) or env is None
        return

    def getEnv(self):
        '''Retourne l'instance de l'environnement utilisé.'''
        return self._env

    env = property(getEnv, setEnv, doc=\
        '''\'env\' est l'environnement d'exécution de la simulation.''')

    def envTestLevel(self, key, level=None):
        '''Retourne le niveau de test et le modifie s'il est indiqué.'''
        return self.env.test.test(key, level)

    def envTestLevelAll(self, level):
        '''Modifie le niveau de test pour tous les labels de l'environnement.'''
        return self.env.test.levelAll(level)
    
    @property
    def envTestKeys(self):
        return self.env.test.keys
