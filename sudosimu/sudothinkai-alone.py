'''Le module sudothinkai contient la classe SudoThinkAI.
ThinkAI est la classe qui encapsule la simulation d'intelligence. Celle-ci va
permettre au joueur simulé de choisir comment il poursuit sa résolution, en
cherchant de l'information dans la grille et en sélectionnant les techniques
les plus appropriées en fonction de l'état présent de la grille et d'un
"savoir-faire" de résolution, éventuellement sujet à de l'apprentissage.
C'est ici que sera évalué la décision d'abandon si aucune technique ne permet
de faire de nouveau placement.

Dans la classe SudoAI, contrairement à toutes les autres classes du programme,
l'information utilisée dans la résolution est considérée comme un savoir
permanent, non sujet à l'obsolescence de la mémoire de travail. C'est le
savoir-faire du joueur, sa capacité globale à "jouer au Sudoku".

TEST :
Ce module importe le module 'sudotest' et utilise l'objet global sudoTest de
classe SudoTest pour gérer de manière paramétrable les I/O de test du code.
'''

from sudosimu import sudoui as ui
from sudosimu import sudorules as rules
from sudosimu.sudorules import Sudoku_Error
from sudosimu.sudomemory import SudoMemory
#import sudoknowledge

#techniques de résolution
#Chiffre/rang-colonne
from sudosimu.techchrc.techchrcr import TechChRCrow   #par rang pour un chiffre
from sudosimu.techchrc.techchrcc import TechChRCcol   #par colonne pour un chiffre
from sudosimu.techchrc.techchrcg import TechChRCgrid   #grille entière pour un chiffre
from sudosimu.techchrc.techchrcga import TechChRCgridAll  #grille entière tous les chiffres
#Dernier placement
from sudosimu.techlplc.techlplcr import TechLastPlcRow    #sur un rang
from sudosimu.techlplc.techlplcc import TechLastPlcCol    #sur une colonne
from sudosimu.techlplc.techlplcs import TechLastPlcSqr    #sur un carré
#from sudosimu.techlplc.techlplcp import TechLastPlcSqr    #sur une case (place)
from sudosimu.techlplc.techlplcg import TechLastPlcGrid   #sur la grille entière

from sudosimu.sudothinktech import SudoThinkTech

from sudosimu.sudotest import *


class SudoThinkAI():
    '''Cette classe regroupe les méthodes qui réalisent la réflexion du
    joueur et choisissent la prochaine action à réaliser.
    '''

    def __init__(self, mem, know=None):
        '''Initialisations, notamment les variables de classe qui représentent
        le savoir-faire de résolution non incluses dans la mémoire de travail.
        Le paramètre optionnel 'know' décrit la connaissance technique et
        tactique de résolution de Sudoku qu'a le joueur.
        '''
        TEST.display("thinkai", 2, "SudoThinkAI - Création d'instance")
        TEST.display("thinkai", 1, "Création de l'intelligence artificielle.")
        assert isinstance(mem, SudoMemory)
        assert know is None or isinstance(know, SudoKnowledge)
        self._mem = mem
        self._know = know
        self._AItechs = dict()
        self._AInbtechs = 0
        #autres flags
        self._gridCompleted = False
        self._gridChecking = False
        self._initOk = True

        #gestion du cycle de résolution (test)
        self._step = 1
        self._nbtotplc = 0  #nombre total de placements de la résolution
        self._nbplcloop = 0     #nombre de placements sur la boucle en cours
        self._nbplc = 0     #nombre de placements de la technique en cours
        return

    #alternance de chrc et lplc
    from sudosimu.ai.ai_chrclplc import _ai_chrc_lplc

    def suggestAction(self):
        '''Indique la prochaine action à effectuer. Il peut s'agir de
        l'application d'une technique de résolution, ou bien d'une observation
        de la grille, d'un placement, ou de l'indication que la résolution est
        terminée pour diverses raisons.
        Retourne un tuple indiquant l'action et des arguments complémentaires.
        '''
        TEST.display("thinkai", 3, "ThinkAI : méthode suggestAction()")
        assert self._initOk
        mem = self._mem
        #PRINCIPE DE RESOLUTION
        #Boucle qui enchaîne Ch/RC-grille et LastPlc-grille, avec vérification
        #de grille terminée.
        #Tant que des chiffres sont placés, la boucle reprend. Elle s'arrête
        #quand l'enchaînement des techniques ne fait plus de placements sur
        #une boucle entière.

        #PREMIERE ETAPE - Ch/RC sur toute la grille
        if self._step == 1:
            tech = mem.recall("ai_suggested_tech", self)
            #s'il n'y a pas encore de technique en cours d'exécution
            if tech is None:
                TEST.display("thinkai", 1, "AI : choix de la technique : "\
                             "TechChRCgridAll")
                TEST.display("thinkai", 3, "Thinkai - Etape #1 de suggestion "\
                             "avec la technique TechChRCgrid.")
                try:
                    tech = TechChRCgridAll(mem, None)
                except:
                    #on gère l'exception
                    TEST.display("thinkai", 1, "La résolution s'interrompt "\
                                 "sur une erreur irrécupérable.")
                    TEST.display("thinkai", 3, "ThinkAI - Erreur fatale : "\
                                 "L'instanciation de la technique de résolution "\
                                 "a échoué.")
                    raise rules.Sudoku_Error
                mem.memorize("ai_suggested_tech", tech, self)
                mem.memorize("ai_suggested_tech_end", False, self)
                #initialiser le compteur de placements de la boucle
                self._nbplcloop = 0
                TEST.display("thinkai", 1, "lancement de la technique.")
                return ("tech", (tech, "insert"))
            #si la tech est terminée => passage à l'étape suivante
            elif mem.recall("ai_suggested_tech_end", self) is True:
                endDetails = mem.recall("ai_suggested_tech_end_details", self)
                #récupérer le nombre de placements faits par la technique
                nbplc = endDetails[1]
                TEST.display("thinkai", 1, "AI : La technique {0} se termine "\
                             "avec {1} placement(s)."\
                             .format(tech.techName(), nbplc))
                self._nbtotplc += nbplc
                self._nbplcloop += nbplc
                #on termine la technique proprement
                del(tech)
                mem.memorize("ai_suggested_tech", None, self)
                #étape suivante
                self._step = 2
                TEST.display("thinkai", 3, "ThinkAI - Fin de l'étape #1")
                TEST.pause("thinkai", 1)
                return ("continue", None)
            #sinon, continuer d'appliquer la même technique
            else:

                TEST.display("thinkai", 2, "AI : Poursuite de la technique : "\
                             "{0}.".format(tech.techName()))
                return ("tech", (tech, "same"))

        #DEUXIEME ETAPE - Vérifier si la grille est terminée
        if self._step == 2:
            TEST.display("thinkai", 3, "Thinkai - Etape #2 de suggestion. "\
                         "Vérification de grille terminée.")
            if self._gridChecking is False:
                #Commencer la vérification
                self._gridChecking = True
                self._gridCompleted = False
                return ("check", None)
            else:
                #Résultat de vérification
                checked = self._gridCompleted
                self._gridChecking = False
            #Si la grille est terminée, retourner "end", sinon passer
            #à l'étape suivante
            if checked is True:
                TEST.display("thinkai", 1, "AI : Vérification : la grille "\
                             "est terminée.")
                return ("end", ("win",))
            else:
                TEST.display("thinkai", 1, "AI : Vérification : la grille "\
                             "n'est pas terminée.")
                TEST.display("thinkai", 1, "Progression de la résolution :\n"\
                             "Total placements faits : {0}\n"\
                             "Placements dans le cycle de techniques : {1}\n"\
                             .format(self._nbtotplc, self._nbplcloop))
                self._step = 3
                TEST.display("thinkai", 3, "ThinkAI - Fin de l'étape #2")
                TEST.pause("thinkai", 1)
                return ("continue", None)



        #TROISIEME ETAPE - LastPlc sur toute la grille
        if self._step == 3:
            tech = mem.recall("ai_suggested_tech", self)
            #s'il n'y a pas encore de technique en cours d'exécution
            if tech is None:
                TEST.display("thinkai", 1, "AI : choix de la technique : "\
                             "TechLastPlcGrid")
                TEST.display("thinkai", 3, "Thinkai - Etape #3 de suggestion "\
                             "avec la technique TechLastPlcGrid.")
                try:
                    tech = TechLastPlcGrid(mem, None)
                except:
                    #on gère l'exception
                    TEST.display("thinkai", 1, "La résolution s'interrompt "\
                                 "sur une erreur irrécupérable.")
                    TEST.display("thinkai", 3, "ThinkAI - Erreur fatale : "\
                                 "L'instanciation de la technique de résolution "\
                                 "a échoué.")
                    raise rules.Sudoku_Error
                mem.memorize("ai_suggested_tech", tech, self)
                mem.memorize("ai_suggested_tech_end", False, self)
                return ("tech", (tech, "insert"))
            #si la tech est terminée => recommencer ou abandon
            elif mem.recall("ai_suggested_tech_end", self) is True:
                endDetails = mem.recall("ai_suggested_tech_end_details", self)
                #récupérer le nombre de placements faits par la technique
                #le format est :("succeed", nb))
                nbplc = endDetails[1]
                TEST.display("thinkai", 1, "AI : La technique {0} se termine "\
                             "avec {1} placement(s)."\
                             .format(tech.techName(), nbplc))
                self._nbtotplc += nbplc
                self._nbplcloop += nbplc
                #on termine la technique proprement
                del(tech)
                mem.memorize("ai_suggested_tech", None, self)
                #étape suivante
                self._step = 4
                TEST.display("thinkai", 3, "ThinkAI - Fin de l'étape #3")
                TEST.pause("thinkai", 1)
                return ("continue", None)
            #sinon, continuer d'appliquer la même tech
            else:
                TEST.display("thinkai", 2, "AI : Poursuite de la technique : "\
                             "{0}.".format(tech.techName()))
                return ("tech", (tech, "same"))

        #QUATRIEME ETAPE - Vérifier si la grille est terminée
        if self._step == 4:
            TEST.display("thinkai", 3, "Thinkai - Etape #4 de suggestion. "\
                         "Vérification de grille terminée.")
            if self._gridChecking is False:
                #Commencer la vérification
                self._gridChecking = True
                self._gridCompleted = False
                return ("check", None)
            else:
                #Résultat de vérification
                checked = self._gridCompleted
                self._gridChecking = False
            #Si la grille est terminée, retourner "end", sinon passer
            #à la fin de la boucle
            if checked is True:
                TEST.display("thinkai", 1, "AI : Vérification : la grille "\
                             "est terminée.")
                return ("end", ("win",))
            else:
                TEST.display("thinkai", 1, "AI : Vérification : la grille "\
                             "n'est pas terminée.")
                TEST.display("thinkai", 1, "Progression de la résolution :\n"\
                             "Total placements faits : {0}\n"\
                             "Placements dans le cycle de techniques : {1}\n"\
                             .format(self._nbtotplc, self._nbplcloop))
                TEST.pause("thinkai", 1)

        #FIN DE LA BOUCLE DE SUGGESTIONS AI
        #continuer si des placements ont été faits au cours de la boucle
        #de techniques, sinon abandonner.
        if self._nbplcloop >0:
            #recommencer à l'étape #1
            self._step = 1
            TEST.display("thinkai", 2, "AI : Recommencer l'enchaînement de "\
                         "techniques tant qu'il y a des placements faits.")
            TEST.pause("thinkai", 1)
            return ("continue", None)
        else:
            #fin
            TEST.display("thinkai", 1, "AI : Plus de placements possibles, "\
                         "abandon après le placement de {0} chiffres."\
                         .format(self._nbtotplc))
            return ("end", ("loose", self._nbtotplc))

        return #par principe            
        
    def _newTechInst(self, techClass, techArgs=None):
        '''Crée une nouvelle instance de la technique indiquée et l'initialise.
        '''
        TEST.display("thinkai", 3, "ThinkAI - méthode _newTechInst()")
        TEST.display("thinkai", 3, "ThinkAI - Création d'une instance de la "\
                     "classe {0}".format(techClass.techClassName()))
        assert self._initOk
#### ATTENTION à faire une bonne gestion d'erreur ici
        tech = techClass(self._mem, techArgs)
        r = tech.init(self._mem)
        if r is None:
            return None
        else:
            return tech

    def _suggestTech(self):
        '''suggère une action opportune'''
        assert self._initOk
        pass
        #Dans cette version une seule technique est utilisée, TechLastPlc,
        #donc la méthode conseille toujours de continuer par l'application
        #de cette technique.
        


    def checkCompleted(self, checked):
        '''Retour d'une vérification de grille terminée.'''
        assert self._initOk
        TEST.display("thinkai", 3, "ThinkAI - Retour de vérification de "\
                     "grille terminée : {0}".format(checked))
        self._mem.memorize("ai_grid_completed", checked, self)
        self._gridCompleted = checked
        return ("continue", None)
    
    def aiObsResult(self, found):
        '''Retour d'une observation demandée par ThinkAI'''
        assert self._initOk
        TEST.display("thinkai", 3, "ThinkAI - retour d'observation : {0}" \
                     .format(found))
        TEST.display("thinkai", 3, "ThinkAI - ne fait rien en retour d'obs.")
        #mémorise le résultat d'observation faite par AI
        self._mem.memorize("ai_obsfound", found, self)
        return ("continue", None)

    def aiPlaceResult(self, placed=True):
        '''Retour d'un placement demandé par ThinkAI'''
        assert self._initOk
        TEST.display("thinkai", 3, "ThinkAI - retour de placement ")
        TEST.display("thinkai", 3, "ThinkAI - ne fait rien en retour de place")
        self._mem.memorize("ai_placedok", placed, self)
        return ("continue", None)

    def techObsResult(self, found):
        '''Retour de l'observation de la technique suggérée par AI'''
        assert self._initOk
        tech = self._mem.recallSafe("ai_suggested_tech", self)
        TEST.display("thinkai", 3, "ThinkAI - retour d'observation par {0}: {1}" \
                     .format(tech, found))
        TEST.display("thinkai", 3, "ThinkAI - ne fait rien en retour d'obs.")
        #mémorise le résultat trouvé par la technique suggérée
        self._mem.memorize("ai_tech_obsfound", found, self)
        return ("continue", None)

    def techPlaceResult(self, placed=None):
        '''Retour du placement de la technique suggérée par AI'''
        assert self._initOk
        TEST.display("thinkai", 3, "dans ThinkAI.placeOk()")
        TEST.display("thinkai", 3, "ne fait rien pour le moment.")
        self._mem.memorize("ai_tech_placedok", placed, self)
        return ("continue", None)

    def techReturnsEnd(self, endDetails=None):
        '''Prend connaissance que la technique suggérée a indiqué sa fin
        avec son résultat final.
        '''
        TEST.display("thinkai", 3, "ThinkAI - dans techReturnsEnd()")
        assert self._initOk
##        #vérifier la validité du résultat retourné
##        if endDetails[0] not in ("end", "noplace", "succeed", "quit", "fail"):
##            raise Sudoku_Error("ThinkAI - une technique a signalé sa fin"\
##                               "avec un code invalide : {0}".format(endDetails))
        TEST.display("thinkai", 3, "ThinkAI - Code de fin de technique "\
                                   "reçu : {0}".format(endDetails))
        #mémorise la fin de technique pour l'itération suivante de AI, et répond
        #de continuer la résolution.
        self._mem.memorize("ai_suggested_tech_end", True, self)
        self._mem.memorize("ai_suggested_tech_end_details", endDetails, self)
        return ("continue", None)

    def techReturnsFail(self, failDetails=None):
        '''Prend connaissance que la technique a généré un fail.'''
        TEST.display("thinkai", 3, "ThinkAI - dans techReturnFail()")
        assert self._initOk
##        #vérifier la validité du résultat retourné
##        if endDetails[0] not in ("end", "noplace", "succeed", "quit", "fail"):
##            raise Sudoku_Error("ThinkAI - une technique a signalé sa fin"\
##                               "avec un code invalide : {0}".format(endDetails))
        TEST.display("thinkai", 3, "ThinkAI - Code de fail de technique "\
                                   "reçu : {0}".format(failDetails))
        #mémorise le fail pour le traiter dans l'itération suivante, et répond
        #de continuer la résolution
        self._mem.memorize("ai_suggested_tech_fail", True, self)
        self._mem.memorize("ai_suggested_tech_fail_details", failDetails, self)
        return ("continue", None)

    def actionResult(self):
        '''Récupère de Thinking le résultat de la dernière action effectuée
        par la technique que ThinkAI a suggéré d'utiliser.
        '''
        assert self._initOk
        return (None, None)

    def techName(self, tech):
        '''Retourne le nom de la classe de la technique de l'instance indiquée'''
        assert self._initOk
        if tech is not None:
            return tech.techName()
        else:
            return None

    def lastTechName(self):
        '''Retourne le nom de la dernière technique suggérée'''
        assert self._initOk
        lastTech = self._tmp_uniqueTech
        if lastTech is None: 
            return None
        else:
            return lastTech.techName()
        
        
            

##TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 
##TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 

if __name__ == "__main__":

    #import sudoobserver
    #import sudogrid
    import sudomemory
    import sudotestall
    testlevel = 3
    TEST.levelAll(testlevel)
    ui.display("Tous les niveaux de test sont à {0}".format(testlevel))

    mem = sudomemory.SudoMemory()
    ai = SudoThinkAI()
    #ai.init(mem)
