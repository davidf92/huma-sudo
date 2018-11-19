'''Module 'sudobaseclass' : définit la classe racine des classes du simulateur
Cette classe présente des attributs et méthodes communs tels que l'intégration
dans l'environnement, l'intégration dans le système de test du code, ainsi que
diverses règles communes au fonctionnement de toutes les classes.
'''

'''
Historique des modifications :
------------------------------
15/11//2017 - Version initiale

TODO
----
17/11/2017 - BUG insoluble pour le moment : l'appel de _initEnv depuis __init__
lève une exception TypeError pour un nombre anormal de paramètres alors que ça
passe très bien pour toutes les autres classes instanciées. Je ne trouve aucune
explication. Copie de cette version de code dans 'sudobaseclass_a.py'
Le code fonctionne en intégrant _initEnv dans __init__ mais ça reste inexpliqué.
'''



#import de l'environnement. Possible sans référence circulaire car les classes
#d'environnement ne dérivent pas de la classe racine.

if __name__ in ("__main__", "sudobaseclass"):
    import sudoenv
elif __name__ == "sudosimu.sudobaseclass":
    from sudosimu import sudoenv
else:
    raise Exception("Impossible de faire les imports dans le module sudobaseclass.")

class SudoBaseClass(object):
    '''Classe racine pour la hiérarchie de classes du simulateur.
    Présente l'intégration de un environnement par défaut et dans le système
    de test de cet environnement.
    '''

    def __init__(self, env=None, testlabel=None, testlevel=None):
        '''Initialisation de l'objet. Consiste principalement à mettre en
        place son environnement SudoEnv.
        '''
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
            self._testlabel = sudoenv.TEST_DEFAULTLABEL
        else:
            self._testlabel = testlabel
        if testlevel is None:
            self._testlevel = sudoenv.TEST_DEFAULTLEVEL
        else:
            self._testlevel = testlevel
        #enregistrement du label dans le système de test
        self.envTestLevel(self._testlabel, self._testlevel)
        #ok
##        TEST = self.env.TEST
##        TEST.display(self._testlabel, 3, "SudoBaseClass - L'instanciation "\
##                     "de la classe de base est terminée.")
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
