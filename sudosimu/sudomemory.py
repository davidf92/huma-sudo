# -*- coding: cp1252 -*-

'''Programme HumaSudo
R�solution humaine simul�e de Sudoku
Module sudomem : m�moire de jeu du joueur
'''

#imports pour test du module
if __name__ in ("__main__", "sudomemory"):
    import sudobaseclass as base
    import sudoenv
    import sudoui as ui
    import sudorules as rules
    from sudorules import Sudoku_Error
    from sudomemprofile import SudoMemProfile
    #from sudotest import *
#imports pour le package
elif __name__ == "sudosimu.sudomemory":
    from sudosimu import sudobaseclass as base
    from sudosimu import sudoenv
    from sudosimu import sudoui as ui
    from sudosimu import sudorules as rules
    from sudosimu.sudorules import Sudoku_Error
    from sudosimu.sudomemprofile import SudoMemProfile
    #from sudosimu.sudotest import *
else:
    raise Exception("Impossible de faire les imports dans le module sudomemory.")


#####
#   METHODES A ECRIRE :
#   M�morisation d'informations durables, isol�es du risque d'oubli
#     def memorizeSafe(.....<m�mes param�tres>  )
#     def recallSafe(...)
#####

class SudoMemory(base.SudoBaseClass):
    '''Cette classe repr�sente la m�moire de jeu d'un joueur, sa connaissance
    de la partie en cours, de ses observations et de ses essais de r�solution.
    C'est la m�moire de travail de sa r�flexion.
    '''
    def __init__(self, profile=None, env=None, \
                                    testlevel=sudoenv.TEST_MEMORYLEVEL):
        '''Initialisation de l'instance de m�moire d'un joueur avec le profil
        m�moire indiqu�. Le profil correspond � des capacit�s et des limites
        de performance de la m�moire.
        '''
        assert isinstance(profile, SudoMemProfile) or profile is None
        #init de la classe racine
        assert isinstance(env, sudoenv.SudoEnv) or env is None
        assert isinstance(testlevel, int) and testlevel>=0 \
                or testlevel is None
        #reprendre un pr�c�dente niveau de test s'il existe d�j�
        oldlev = env.testLevel("memory")
        if oldlev is not None and testlevel != oldlev:
            testlevel = oldlev
        base.SudoBaseClass.__init__(self, env=env, \
                                    testlabel="memory", testlevel=testlevel)
        #ok init de cette classe
        TEST = self.env.TEST
        TEST.display("memory", 3, "SudoMemory - Dans __init__()")
        self._mem = None
        self.profile(profile)
        self._init2()

    def _init2(self):
        '''Suite de l'initialisation. Cr�ation du conteneur d'informations
        qui est initialement vide.
        '''
        self._mem = dict()
        self._itemNo = 0              #l'index unique d'infos en m�moire
        self._observation = None
        self._profile = None
        self._initOk = True

    def profile(self, profile=None):
        '''Assigne ou retourne le profil m�moire'''
        TEST = self.env.TEST
        TEST.display("memory", 3, "SudoMemory - Dans profile()")
        if profile is not None:
            assert isinstance(profile, SudoMemProfile)
        self._profile = profile
        pass

        
    def memorize(self, item, value, copy=None):
        '''M�morise une information sous forme d'une cl� associ�e � un
        identifiant d'exemplaire (en pratique un objet instance de technique
        de r�solution) pass� en option en param�tre.
        Stocke aussi un identifiant unique d'item m�moire. L'identifiant unique
        est incr�ment� � chaque m�morisation m�me pour une cl� d�j� existante.
        '''
        TEST = self.env.TEST
        TEST.display("memory", 3, "SudoMemory - Dans memorize()")
        assert self._initOk
        #index unique de l'info m�moire
        self._itemNo += 1
        #construire la cl� de stockage dans le dictionnaire
        if copy is not None:
            key = (item, copy)
        else:
            key = item
        #ajouter au dictionnaire la valeur avec son identifiant unique
        TEST.display("memory", 3, "SudoMemory - M�morisation de la cl� = {0}, "\
                             "valeur = {1}, comme item # = {2}"
                                 .format(key, value, self._itemNo))
        self._mem[key]= (value, self._itemNo)      
        return True

    def increment(self, item, incr, copy=None):
        '''Incr�mente une information m�moire num�rique et la retourne.
        Cr�e cette information si elle n'existe pas encore ou si elle est None,
        sauf si � la fois l'information et l'incr�ment sont None.
        Retourne False si l'incr�mentation n'est pas possible, notamment si
        soir l'information soit l'incr�ment n'est pas num�rique. Traite un
        incr�ment None comme z�ro sans signaler d'erreur.
        '''
        TEST = self.env.TEST
        TEST.display("memory", 3, "SudoMemory - Dans increment()")
        assert self._initOk
        #traiter les diff�rents cas particuliers et erreurs
        value = self.recall(item, copy)
        if value is None and incr is None:
            return None
        if value is None:
            value = 0
        if str(type(value)) not in ("<class 'int'>", "<class 'float'>") :
            TEST.display("memory", 3, "SudoMemory - Incr�mentation impossible "\
                                "pour {0}.".format(str(item)))
            return False
        if incr is None:
            incr = 0
        if str(type(incr)) not in ("<class 'int'>", "<class 'float'>") :
            TEST.display("memory", 3, "SudoMemory - Incr�mentation impossible "\
                                "pour {0}.".format(str(item)))
            return False
        #ok pour incr�menter
        newValue = value + incr
        self.memorize(item, newValue, copy)
        #retourne la nouvelle valeur
        return newValue
        
    def memorizeStack(self, item, value, copy=None):
        '''M�morize une information en l'ajoutant � une pile FIFO associ�e
        � une cl�. C'est une version identique � memorize() � laquelle s'ajoute
        la pile.
        Chaque �volution de la pile est un item m�moire distinct
        '''
        TEST = self.env.TEST
        TEST.display("memory", 3, "SudoMemory - Dans memorizeStack()")
        assert self._initOk
##  A FAIRE PLUS TARD
        pass
##    
        #est-ce qu'une pile existe pour cet item ?
        
    def recall(self, item, copy=None):
        '''Se rem�more une information pour la cl� et l'identifiant de copie
        fournis. Retourne None si l'information est inconnue.
        '''
        TEST = self.env.TEST
        TEST.display("memory", 3, "SudoMemory - Dans recall()")
        assert self._initOk
        #construire la cl� de recherche dans le dictionnaire
        if copy is not None:
            key = (item, copy)
        else:
            key = item
        memValue = self._mem.get(key, None)
        if memValue is None:
            rec = None
        else:
            rec = memValue[0] #ne pas retourner l'identifiant d'item m�moire
        TEST.display("memory", 3, "SudoMemory - Rappel de la cl� = {0}, "\
                     "valeur = {1}".format(key, rec))
        return rec

    def recallSafe(self, item, copy=None):
        '''Se rem�more une information. Cette version ne fait pas de traitement
        d'obsolescence de la m�moire de travail
        '''
        TEST = self.env.TEST
        TEST.display("memory", 3, "SudoMemory - Dans recallSafe()")
        assert self._initOk
##METTRE A JOUR ICI QUAND IL Y AURA LE TRAITEMENT D'OBSOLESCENCE
        return self.recall(item, copy)
        
    def memorizeObs(self, observation, copy=None):
        """M�morise le r�sultat de la observation pour l'identifiant de copie
        indiqu� en param�tre.
        """
        TEST = self.env.TEST
        TEST.display("memory", 3, "SudoMemory - Dans memorize0bs()")
        assert self._initOk
        self.memorize("mem_observation", observation, copy)
        return True

    def recallObs(self, copy=None):
        """Se rem�more le r�sultat de la derni�re observation pour l'identifiant
        de copie indiqu�.
        ATTENTION : doit toujours retourner un tuple car les m�thodes
        d'observations le font. Donc pb si retourne None ou False
        """
        TEST = self.env.TEST
        TEST.display("memory", 3, "SudoMemory - Dans recallObs()")
        assert self._initOk
        obs = self.recall("mem_observation", copy)
        return obs

    @property
    def initOK(self):
        return self._initOK
    
    @property
    def dict(self):
        assert self._initOk
        return self._mem.copy()
    
    def printAll(self):
        """Ecrit la totalit� du contenu de la m�moire"""
        assert self._initOk
        for i in self._mem:
            ui.display("{0} : {1}".format(i, self._mem[i][0]))
        return

    def flush(self):
        '''Vide compl�tement la m�moire et la remet dans son �tat initial.
        Le profil m�moire reste le m�me.
        '''
        self._init2()
        return
        
    def __str__(self):
        if self._profile is None:
            txt = "Une m�moire de jeu sans profil"
        else:
            txt = "Une m�moire de jeu de profil : {0}".format(self._profile)
        return txt
                      
#TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST
#TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST

    
def testMem():
    pass


if __name__ == '__main__':
    mem = SudoMemory()
    memprof = SudoMemProfile("Mon profil")
    print(mem)
    memprof.name("Mon nouveau profil")
    print(memprof)
    print(mem)
    testMem()

    
