'''Le module sudothinktech contient la classe ThinkTech.
ThinkTech est une classe qui représente une technique de résolution en cours
d'utilisation.

TEST :
Ce module importe le module 'sudotest' et utilise l'objet global sudoTest de
classe SudoTest pour gérer de manière paramétrable les I/O de test du code.
'''

from sudosimu import sudoio
from sudosimu.sudoio import sudoPause, display, displayError
from sudosimu import sudorules as rules
from sudosimu.sudorules import Sudoku_Error

from sudosimu import sudoobserver
from sudosimu import sudomemory
from sudosimu.sudomemory import SudoMemory
from sudosimu import sudogrid
from sudosimu.techchrc.techchrcr import TechChRCrow
from sudosimu.techchrc.techchrcc import TechChRCcol
from sudosimu.techlplc.techlplcs import TechLastPlcSqr
from sudosimu.techlplc.techlplcr import TechLastPlcRow
from sudosimu.techlplc.techlplcc import TechLastPlcCol
from sudosimu.techlplc.techlplcg import TechLastPlcGrid
#from  sudotechlastplc import TechLastPlc
#imports pour le code de test et d'affichage de debuggage
from sudosimu.sudotest import *


class SudoThinkTech():
    '''ThinkTech est une classe qui représente une technique de résolution.
    Chaque fois que le joueur décide (SudoAI) d'appliquer une technique, une
    instance de cette classe est utilisée pour gérer l'état d'utilisation de la
    technique en question.
    Cet état n'est pas la succession des étapes logiques de la technique, mais
    plutôt représente comment le joueur réfléchit à l'utilisation de cette technique.
    Exemple : continuer à l'appliquer, ou en insérer une autre pour profiter
    d'une opportunité et reprendre la précédente, etc.
    '''

##Dans cette version les données de la technique sont stockées en propriétés
##de l'instance. Cependant ce n'est pas réaliste car le joueur peut ne plus se
##souvenir où il en était dans une technique qui a été mise en attente par
##l'imbricatino d'autres techniques.
##Donc il faudra revoir le code pour gérer toutes les informations dans la
##mémoire de travail, avec Memory.memorize() et Memory.recall()

    def __init__(self, techClass, techArgs=None):
        '''Crée une instance de la classe de la technique représentée.
        Initialisation cette instance de technique. Crée dans la mémoire
        de travail les informations d'état de la technique.
        '''
        #instancier la technique depuis sa classe
        self._techInst = techClass(mem, techArgs)
        #autres initialisations
        self._techClass = techClass
        self._techArgs = techArgs
        self._techState = "new"
        self._lastAction = None
        self._lastObsPattern = None
        self._lastObsFound = None
        self._lastPlacement = None
        self._lastPlacedResult = None
        return

    def init(self, mem):
        '''Initialise l'instance de technique'''
        r = self._techInst.init(mem)
        return r

    def apply(self, mem):
        '''Applique la technique'''
        r = self._techInst.apply(mem)
        self._memTechReturn(r)
        self._techState = "active"
        return r

    def resume(self, mem):
        '''Relance la technique quand elle a été suspendue'''
        r = self._techInst.resume(mem)
        self._techState = "active"
        return r

    def obsFound(self, mem, found):
        '''Transmet à la technique un résultat d'observation'''
        r = self._techInst.obsFound(mem, found)
        self._lastObsFound = found
        return r
    
    def placeOk(self, mem, placed=None):
        '''Transmet à la technique un résultat d'observation'''
        r = self._techInst.placeOk(mem, placed)
        self._lastPlacedResult = placed
        return r

    def techName(self):
        '''Retourne le nom de la technique'''
        return self.techName()
    def suspend(self, mem):
        '''Suspend la technique'''
        self._techState = "standby"
        return

    def reset(self, mem):
        '''Appelle 'reset' de la technique'''
        r = self._techInst.reset(mem)
        self._techState = "new"
        return r

    def _memTechReturn(self, techReturn):
        '''mémorise les infos d'actions "observe" et "place" '''
        (action, actionDetails) = techReturn
        if action == "observe":
            pattern = actionDetails
            self._lastObsPattern = pattern
        elif action == "place":
            placement = actionDetails
            self._lastPlacement = placement
        self._lastAction = action
        return

    @property
    def state(self):
        return self._techState

    @property
    def lastAction(self):
        return self._lastAction

    @property
    def techClass(self):
        return self._techClass
    
    def techName(self):
        return self._techInst.techName()

##TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 
##TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 

if __name__ == "__main__":

    import sudotestall
    testlevel = 3
    TEST.levelAll(testlevel)
    display("Tous les niveaux de test sont à {0}".format(testlevel))

##    lastplc = SudoThinkTech(TechLastPlc)
##    mem = SudoMemory()
##    lastplc.init(mem)
##
##    display("Appel de lastplc.apply()")
##    r = lastplc.apply(mem)
##    display("retour : {0}".format(r))
##    s = lastplc.state
##    display("Etat de lastplc : {0}".format(s))
##    last = lastplc.lastAction
##    display("Dernière action de lastplc : {0}".format(last))
    
            
    
    
    pass
