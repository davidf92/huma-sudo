'''Le module 'sudoainode' contient la classe SudoAInode. C'est une classe racine
pour les classes de règles AI présentes dans le module 'sudoai'.
'''

if __name__ in ("__main__", "sudoainode"):
    import sudobaseclass as base
    import sudoenv
    import sudoui as ui
    import sudorules as rules
    from sudorules import Sudoku_Error
    from sudomemory import SudoMemory
elif __name__ == "sudosimu.sudoainode":
    from sudosimu import sudobaseclass as base
    from sudosimu import sudoenv
    from sudosimu import sudoui as ui
    from sudosimu import sudorules as rules
    from sudosimu.sudorules import Sudoku_Error
    from sudosimu.sudomemory import SudoMemory
else:
    raise Exception("Impossible de faire les imports dans le module sudobaseclass.")


class SudoAInode(base.SudoBaseClass):
    '''Classe de base des noeuds du système décisionnel de type réseau neuronal.
    Un 'noeud' représente typiquement une simulation de neurone qui produit un
    signal de sortie à partir d'un ensemble de signaux d'entrée, affectés de
    coefficients, de seuils maximaux et minimaux et d'autres facteurs
    arithmétiques. Les classes dérivées servent à simuler des critères et règles
    du système AI.
    '''
    def __init__(self, inputs, env=None, testlevel=sudoenv.TEST_AINODELEVEL):
        '''Initialise une instance. L'argument 'inputs' doit être un tuple de
        3 tuples correspondant chacun à un ensemble d'entrées.
        '''
        #init de la classe racine
        assert isinstance(env, sudoenv.SudoEnv) or env is None
        assert isinstance(testlevel, int) and testlevel>=0 \
                or testlevel is None
        #reprendre un précédente niveau de test s'il existe déjà
        oldlev = env.testLevel("ainode")
        if oldlev is not None and testlevel != oldlev:
            testlevel = oldlev
        base.SudoBaseClass.__init__(self, env=env, \
                                    testlabel="ainode", testlevel=testlevel)
        #ok init de cette classe
        TEST = self.env.TEST
        TEST.display("ainode", 3, "SudoAI - Dans __init__()")
        TEST.display("ainode", 1, "Création du système décisionnel AI")
##        assert isinstance(nodeInput, SudoAInodeInput)
        #vérification de type et cardinalité
        self._verifInputs(inputs)
        self._inputs = inputs
        return
    
    def _verifInputs(self, inputs):
        assert isinstance(inputs, tuple) and len(inputs) == 3
        for i in inputs:
            assert isinstance(i, tuple) or i is None
        return True

    def eval(self):
        '''Evalue le noeud et retourne la valeur.'''

    def setInputs(self, inputs):
        self._verifInputs()
        self._inputs = inputs

    def getInputs(self):
        return self._inputs

    inputs = property(getInputs, setInputs)
    
            


##class SudoAInodeInput(tuple, base.SudoBaseClass):
##    '''Représente les entrées d'un noeud décisionnel (neurone). Ces entrées
##    sont rassemblées en un tuple de 3 tuples qui correspondent à des entrées
##    impératives, restrictives ou contributives.
##    '''
##    def __new__(cls, inputs, env=None, testlevel=sudoenv.TEST_AINODEINPUT):
##        
##    def __init__(self, inputs, env=None, testlevel=sudoenv.TEST_AINODEINPUT):
##        #init de la classe racine
##        assert isinstance(env, sudoenv.SudoEnv) or env is None
##        assert isinstance(testlevel, int) and testlevel>=0 \
##                or testlevel is None
##        base.SudoBaseClass.__init__(self, env=env, \
##                                    testlabel="ai", testlevel=testlevel)
##        #ok init de cette classe
##        TEST = self.env.TEST
##        TEST.display("ai", 3, "SudoAInodeInput - Dans __init__()")
##        TEST.display("ai", 1, "Création d'un noeud décisionnel du système AI")
##        #vérification de type et cardinalité
##        assert isinstance(inputs, tuple) and len(inputs) == 3
##        for i in inputs:
##            assert isinstance(i, tuple) or i is None
##        #association des inputs aux items de l'instance en tant que tuple
##        self[0] = inputs[0]
##        self[1] = inputs[1]
##        self[2] = inputs[2]
        
        
