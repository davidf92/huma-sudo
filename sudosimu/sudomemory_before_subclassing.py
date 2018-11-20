# -*- coding: cp1252 -*-

'''Programme HumaSudo
Résolution humaine simulée de Sudoku
Module sudomem : mémoire de jeu du joueur
'''

from sudosimu import sudoui as ui
from sudosimu import sudorules as rules
from sudosimu.sudorules import Sudoku_Error
from sudosimu.sudomemprofile import SudoMemProfile
from sudosimu.sudotest import *


#####
#   METHODES A ECRIRE :
#   Mémorisation d'informations durables, isolées du risque d'oubli
#     def memorizeSafe(.....<mêmes paramètres>  )
#     def recallSafe(...)
#####

class SudoMemory():
    '''Cette classe représente la mémoire de jeu d'un joueur, sa connaissance
    de la partie en cours, de ses observations et de ses essais de résolution.
    C'est la mémoire de travail de sa réflexion.
    '''
    def __init__(self,profile=None):
        '''Initialisation de l'instance de mémoire d'un joueur avec le profil
        mémoire indiqué. Le profil correspond à des capacités et des limites
        de performance de la mémoire.
        '''
        self._mem = None
        self.profile(profile)
        self._init2()

    def _init2(self):
        '''Suite de l'initialisation. Création du conteneur d'informations
        qui est initialement vide.
        '''
        self._mem = dict()
        self._itemNo = 0              #l'index unique d'infos en mémoire
        self._observation = None
        self._profile = None
        self._initOk = True

    def profile(self, profile=None):
        '''Assigne ou retourne le profil mémoire'''
        if profile is not None:
            assert isinstance(profile, SudoMemProfile)
        self._profile = profile
        pass

        
    def memorize(self, item, value, copy=None):
        '''Mémorise une information sous forme d'une clé associée à un
        identifiant d'exemplaire (en pratique un objet instance de technique
        de résolution) passé en option en paramètre.
        Stocke aussi un identifiant unique d'item mémoire.
        '''
        assert self._initOk
        #index unique de l'info mémoire
        self._itemNo += 1
        #construire la clé de stockage dans le dictionnaire
        if copy is not None:
            key = (item, copy)
        else:
            key = item
        #ajouter au dictionnaire la valeur avec son identifiant unique
        self._mem[key]= (value, self._itemNo)      
        return True

    def increment(self, item, incr, copy=None):
        '''Incrémente une information mémoire numérique et la retourne.
        Crée cette information si elle n'existe pas encore ou si elle est None,
        sauf si à la fois l'information et l'incrément sont None.
        Retourne False si l'incrémentation n'est pas possible, notamment si
        soir l'information soit l'incrément n'est pas numérique. Traite un
        incrément None comme zéro sans signaler d'erreur.
        '''
        assert self._initOk
        #traiter les différents cas particuliers et erreurs
        value = self.recall(item, copy)
        if value is None and incr is None:
            return None
        if value is None:
            value = 0
        if str(type(value)) not in ("<class 'int'>", "<class 'float'>") :
            return False
        if incr is None:
            incr = 0
        if str(type(incr)) not in ("<class 'int'>", "<class 'float'>") :
            return False
        #ok pour incrémenter
        newValue = value + incr
        self.memorize(item, newValue, copy)
        #retourne la nouvelle valeur
        return newValue
        
    def memorizeStack(self, item, value, copy=None):
        '''Mémorize une information en l'ajoutant à une pile FIFO associée
        à une clé. C'est une version identique à memorize() à laquelle s'ajoute
        la pile.
        Chaque évolution de la pile est un item mémoire distinct
        '''
        assert self._initOk
##  A FAIRE PLUS TARD
        pass
##    
        #est-ce qu'une pile existe pour cet item ?
        
    def recall(self, item, copy=None):
        '''Se remémore une information pour la clé et l'identifiant de copie
        fournis. Retourne None si l'information est inconnue.
        '''
        assert self._initOk
        #construire la clé de recherche dans le dictionnaire
        if copy is not None:
            key = (item, copy)
        else:
            key = item
        memValue = self._mem.get(key, None)
        if memValue is None:
            return None
        else:
            return memValue[0] #ne pas retourner l'identifiant d'item mémoire

    def recallSafe(self, item, copy=None):
        '''Se remémore une information. Cette version ne fait pas de traitement
        d'obsolescence de la mémoire de travail
        '''
        assert self._initOk
##METTRE A JOUR ICI QUAND IL Y AURA LE TRAITEMENT D'OBSOLESCENCE
        return self.recall(item, copy)
        
    def memorizeObs(self, observation, copy=None):
        """Mémorise le résultat de la observation pour l'identifiant de copie
        indiqué en paramètre.
        """
        assert self._initOk
        self.memorize("mem_observation", observation, copy)
        return True

    def recallObs(self, copy=None):
        """Se remémore le résultat de la dernière observation pour l'identifiant
        de copie indiqué.
        ATTENTION : doit toujours retourner un tuple car les méthodes
        d'observations le font. Donc pb si retourne None ou False
        """
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
        """Ecrit la totalité du contenu de la mémoire"""
        assert self._initOk
        for i in self._mem:
            ui.display("{0} : {1}".format(i, self._mem[i][0]))
        return

    def flush(self):
        '''Vide complètement la mémoire et la remet dans son état initial.
        Le profil mémoire reste le même.
        '''
        self._init2()
        return
        
    def __str__(self):
        if self._profile is None:
            txt = "Une mémoire de jeu sans profil"
        else:
            txt = "Une mémoire de jeu de profil : {0}".format(self._profile)
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

    
