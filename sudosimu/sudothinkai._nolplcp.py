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

Historique des mises-à-jour
22/10/2017 Déport dans un sous-module de la fonction qui propose une
technique. Le code de suggestAction() est déporté dans cette fonction. De cette
manière il est simple (dans la phase de développement) de modifier la
stratégie de résolution sans toucher au code générique.

TEST :
Ce module importe le module 'sudotest' et utilise l'objet global sudoTest de
classe SudoTest pour gérer de manière paramétrable les I/O de test du code.
'''


##IMPORTS DU MOTEUR DE SIMULATION
#exécution interne au package
if __name__ in ("__main__", "sudothinkai"):
    import sudobaseclass as base
    import sudoenv
    import sudoui as ui
    import sudorules as rules
    from sudorules import Sudoku_Error
    from sudomemory import SudoMemory
    import sudoai as ai
#exécution depuis l'extérieur du package sudosimu
elif __name__ == "sudosimu.sudothinkai":
    from sudosimu import sudobaseclass as base
    from sudosimu import sudoenv
    from sudosimu import sudoui as ui
    from sudosimu import sudorules as rules
    from sudosimu.sudorules import Sudoku_Error
    from sudosimu.sudomemory import SudoMemory
    from sudosimu import sudoai as ai
#import sudoknowledge
else:
    raise Exception("Impossible de faire les imports dans le module sudothinkai.")

####IMPORTS DES MODULES DE TECHNIQUES DE RESOLUTION
if __name__ in ("__main__", "sudothinkai"):
    from sudotechimports import *
elif __name__ == "sudosimu.sudothinkai":
    from sudosimu.sudotechimports import *
else:
    raise Exception("Impossible de faire les imports dans le module sudothinkai.")
    
##if __name__ in ("__main__", "sudothinkai"):
##    #Chiffre/rang-colonne
##    from techchrc.techchrcr import TechChRCrow   #par rang pour un chiffre
##    from techchrc.techchrcc import TechChRCcol   #par colonne pour un chiffre
##    from techchrc.techchrcg import TechChRCgrid   #grille entière pour un chiffre
##    from techchrc.techchrcga import TechChRCgridAll  #grille entière tous les chiffres
##    #Dernier placement
##    from techlplc.techlplcr import TechLastPlcRow    #sur un rang
##    from techlplc.techlplcc import TechLastPlcCol    #sur une colonne
##    from techlplc.techlplcs import TechLastPlcSqr    #sur un carré
##    #from techlplc.techlplcp import TechLastPlcSqr    #sur une case (place)
##    from techlplc.techlplcg import TechLastPlcGrid   #sur la grille entière
##elif __name__ == "sudosimu.sudothinkai":
##    #Chiffre/rang-colonne
##    from sudosimu.techchrc.techchrcr import TechChRCrow   #par rang pour un chiffre
##    from sudosimu.techchrc.techchrcc import TechChRCcol   #par colonne pour un chiffre
##    from sudosimu.techchrc.techchrcg import TechChRCgrid   #grille entière pour un chiffre
##    from sudosimu.techchrc.techchrcga import TechChRCgridAll  #grille entière tous les chiffres
##    #Dernier placement
##    from sudosimu.techlplc.techlplcr import TechLastPlcRow    #sur un rang
##    from sudosimu.techlplc.techlplcc import TechLastPlcCol    #sur une colonne
##    from sudosimu.techlplc.techlplcs import TechLastPlcSqr    #sur un carré
##    #from sudosimu.techlplc.techlplcp import TechLastPlcSqr    #sur une case (place)
##    from sudosimu.techlplc.techlplcg import TechLastPlcGrid   #sur la grille entière
##else:
##    raise Exception("Impossible de faire les imports dans le module sudothinkai.")
##
#OBSOLETE
#from sudosimu.sudothinktech import SudoThinkTech


##Dictionnaire d'identification des techniques
##ATTENTION : les noms de techniques doivent être les mêmes que ceux connus
##par SudoAI dans sudoai.py
TechDict = { "techchrcga", TechChRCgridAll, \
             "techlplcg", TechLastPlcGrid \
           }


class SudoThinkAI(base.SudoBaseClass):
    '''Cette classe regroupe les méthodes qui réalisent la réflexion du
    joueur et choisissent la prochaine action à réaliser.
    '''

    def __init__(self, mem, know=None, \
                 env=None, testlevel=sudoenv.TEST_THINKAILEVEL):
        '''Initialisations, notamment les variables de classe qui représentent
        le savoir-faire de résolution non incluses dans la mémoire de travail.
        Le paramètre optionnel 'know' décrit la connaissance technique et
        tactique de résolution de Sudoku qu'a le joueur.
        '''
        #init de la classe racine
        assert isinstance(env, sudoenv.SudoEnv) or env is None
        assert isinstance(testlevel, int) and testlevel>=0 \
                or testlevel is None
        base.SudoBaseClass.__init__(self, env=env, \
                                    testlabel="thinkai", testlevel=testlevel)
        #ok init de cette classe
        TEST = self.env.TEST
        TEST.display("thinkai", 3, "SudoThinkAI - Dans __init__()")
        TEST.display("thinkai", 1, "Création de l'intelligence artificielle.")
        assert isinstance(mem, SudoMemory)
        self._mem = mem
        assert know is None or isinstance(know, SudoKnowledge)
        self._know = know
        #init du système de décision AI
        self._initAI()
        #init de la pile des techniques en cours
        self._initTechPile()
        #gestion de la vérification de fin de partie
        self._needGridChecking = False
        self._checkingGrid = False
        self._gridCompleted = False
        #gestion du cycle de résolution (test)
        self._step = 1
        self._nbtotplc = 0  #nombre total de placements de la résolution
        self._nbplcloop = 0     #nombre de placements sur la boucle en cours
        self._nbplc = 0     #nombre de placements de la technique en cours

        self._initOk = True
        return

    def _initAI(self):
        '''Initialisation du système de décision et mise en place des
        données d'avancement pour le début de résolution.
        '''
        TEST = self.env.TEST
        TEST.display("thinkai", 3, "ThinkAI - Dans _initAI()")
        #créer du système de décision SudoAI
        try:
            self._ai = ai.SudoAI(self._mem, env=self._env)
            #récupérer le dictionnaire de données
            self._aiData = self._ai.data
        except:
            raise Sudoku_Error("Dans SudoThinkAI._initAI() : "\
                               "Impossible d'initialiser le système AI")
        #données d'avancement de la résolution
        self._begin = True      #True si c'est le début de résolution
        self._techNiv = 0       #Niveau d'empilement de techniques
        #ATTENTION : AMELIORER la définition de techNivMax (knowledge)
        self._techNivMax = 3    #Niveau max d'empilement acceptable
        self._inTech = False    #True si une technique est en cours
        self._opport = False    #True si une recherche d'opportunité est en cours
        self._tech = None       #code de la technique en cours
        self._techInst = None   #instance de la technique en cours
        self._techName = None   #Nom de la technique en cours
        self._lastTech = None   #code de la préc. tech. de même niveau
##        self._lastTechInst = None   #instance de la préc. tech. de même niveau
##        self._lastTechName = None #Nom de la préc. tech. de même niveau
##        self._lastTechNivInf = None     #Inst. préc.tech. de niveau inférieur
##        self._lastTechNivInfName = None #Nom. préc.tech. de niveau inférieur
##        self._lastTechNivInf2 = None        #idem niveau -2
##        self._lastTechNivInf2Name = None    #idem niveau -2
        self._lastAction = None     #Dernière action exécutée
        self._lastTechAction = None #Dernière action exécutée par une tech
        self._lastAIaction = None   #Dernière action exécutée pra l'AI
        if TEST.ifLevel("thinkai", 3) is True:
            self._dispDataSet()


    def decideAction(self):
        '''Indique la prochaine action à effectuer. Il peut s'agir de
        l'application d'une technique de résolution, ou bien d'une observation
        de la grille, d'un placement, ou de l'indication que la résolution est
        terminée pour diverses raisons.
        Retourne un tuple indiquant l'action et des arguments complémentaires.
        '''
        TEST = self.env.TEST
        TEST.display("thinkai", 3, "ThinkAI : méthode decideAction()")
        assert self._initOk

        #Vérifier d'abord si la grille est terminée
        r = self._gridCheckingProcess()
        if r is not None:
            return r
        
        #Interroger le système de décision
        self._makeDataSet()
        try:
            suggestion = self._ai.suggest()
        except:
            raise Sudoku_Error("SudoThinkAI.decideAction() : "\
                               "Erreur en appelant SudoAI.suggest()")

        #analyser la réponse
        su = suggestion[0]
        TEST.display("thinkai", 3, "decideAction() - La suggestion AI est : "\
                                   "{0}".format(su))
        if su == "continue":
            #continuer la technique en cours - rien à changer
            TEST.display("thinkai", 3, "SudoThinkAI.decideAction() - Décision "\
                         " = continuer la technique en cours.")
            action = ("tech", (self._techInst, "same"))
        elif su == "start_tech":
            #insérer une nouvelle technique
            TEST.display("thinkai", 3, "SudoThinkAI.decideAction() - Décision "\
                         " = insérer une technique ({0}).".format(suggestion[1]))
            action = self._startTech(suggestion[1])
            TEST.display("thinkai", 1, "AI : Lancement d'une nouvelle technique "\
                         "de résolution : {0}.".format(self._techName))
        elif su == "abort_tech":
            TEST.display("thinkai", 3, "SudoThinkAI.decideAction() - Décision "\
                         "= abandonner la technique en cours.")
            TEST.display("thinkai", 1, "AI : Abandon de la technique de "\
                         "résolution : {0}.".format(self._techName))
            action = self._abortTech()
        elif su == "abort_all":
            TEST.display("thinkai", 3, "SudoThinkAI.decideAction() - Décision "\
                         " abandon de toutes les techniques en cours.")
            action = self._abortAllTechs()
            TEST.display("thinkai", 1, "AI : Abandon de toutes les techniques "\
                         "de résolution en cours.")
        else:
            #ne devrait pas arriver
            raise Sudoku_Error("SudoThinkAI.decideAction() : "\
                               "erreur dans le retour de suggestion de SudoAI.")
        #dans tous les cas la résolution n'en est plus au début
        self._begin = False
        #TEST : affichage des nouvelles données de résolution en cours
        if TEST.ifLevel("thinkai", 3) is True:
            TEST.display("thinkai", 3, "ThinkAI - Nouvelles données de "\
                                       "résolution :")
            self._dispDataSet()
        #TEST : pause de vérification des données
        TEST.pause("thinkai", 4)
        TEST.display("thinkai", 3, "SudoThinkAI - Décision retournée = {0}. "\
                                 .format(r))
        return action

    def _startTech(self, suggested):
        '''Lancement d'une nouvelle technique et insertion dans la pile de
        techniques en cours.
        '''
        TEST = self.env.TEST
        TEST.display("thinkai", 3, "ThinkAI : dans _startTech()")
        assert self._initOk

        #instancier la technique suggérée
        if suggested == "techchrcga":
            #la tech ChRCgridAll ne prend pas d'argument
            TEST.display("thinkai", 3, "ThinkAI - Nouvelle instance de technique "\
                                    "TechChRCgridAll.")
            inst = self._newTechInst(TechChRCgridAll, None)
        elif suggested == "techlplcg":
            #la tech LastPlcGrid ne prend pas d'argument
            TEST.display("thinkai", 3, "ThinkAI - Nouvelle instance de technique "\
                                    "TechLastPlcGrid.")
            inst = self._newTechInst(TechLastPlcGrid, None)

        #mettre à jour les informations de résolution en cours
##        self._lastTechNivInf = self._tech
##        self._lastTechNivInfName = self._techName
##        self._techPilePush(tech)
        self._tech = suggested
        self._techInst = inst
        self._techName = inst.techName()
        self._techNiv += 1
        self._inTech = True
##        self._opport = True if self._techNiv >= 2 else False
        self._lastTech = None
        self._lastTechname =None
        self._lastAction = None
        self._lastTechAction = None
        #Retour vers Thinking = insertion de la nouvelle technique
        return ("tech", (self._techInst, "insert"))
        
        
    def _abortTech(self):
        '''Abandon de la technique en cours. Dépilement et retour à la tech
        précédente s'il y en a une.
        '''
        TEST = self.env.TEST
        TEST.display("thinkai", 3, "ThinkAI : dans _abortTech()")
        assert self._initOk
        #vérifications de cohérence
        assert self._techNiv > 0
        assert self._tech is not None
        #supprimer l'instance de la technique abandonnée
        del(self._techInst)
        #dépiler
        #retour à la tech précédente et mise à jour des données de résolution
        #s'il y avait plus d'1 tech empilée, il en reste encore maintenant
##        self._techPilePop()
##        t = self._techPileGet()
##        if t is None:
##            self._tech = None
##            self._techName = None
##            self._inTech = False
##        else:
##            self._tech = t
##            self._techName = t.techName()
##            self._inTech = True
        
        #enregistrer la dernière technique en cours comme "précédente".
        self._lastTech = self._tech
        self._lastTechName = self._techName

#### DANS LA VERSION ACTUELLE, 1 seul niveau donc abort renvoie au niveau 0
##   et donc il ny a plus de technique en cours
        self._tech = None
        self._techInst = None
        self._techName = None
        #self._techNiv -= 1
        self._techNiv = 0
        self._inTech = False
        self._lastAction = None
        self._lastTechAction = None
        return ("continue", None)
    
##        self._tech = self._lastTechNivInf
##        self._techName = self._lastTechNivInfName
##        self._inTech = True if self._tech is not None else False
##        self._opport = True if self._techNiv >= 2 else False
#### NOTE : C'est ici qu'il va falloir géger la possibilité (MemProfile) de se
# rappeler ce que l'on faisait avant, au moins 2 niveaux avant, c'est-à-dire
# une fois revenu au niveau 1 ne pas avoir oublié ce que l'on faisait avant.
##        self._lastTechNivInf = None
##        self._lastTechNivInfName = None
######
##        self._lastAction = None
##        self._lastTechAction = None
##        
##        #L'action décidée dépend du niveau d'imbrication auquel on est revenu.
##        if self._techInst is None:
##            action = ("continue", None)
##        else:
##            action = ("tech", (self._techInst, "revert"))
##
##        return action

    def _abortAllTechs(self):
        '''Lancement d'une nouvelle technique et insertion dans la pile de
        techniques en cours.
        '''
        TEST = self.env.TEST
        TEST.display("thinkai", 3, "ThinkAI : dans _abortAllTechs()")
        TEST.display("thinkai", 3, "METHODE A ECRIRE")
        assert self._initOk
        raise Sudoku_Error("_abortAllTechs() n'existe pas encore.")

    def _newTechInst(self, techClass, techArgs=None):
        '''Crée une nouvelle instance de la technique indiquée et l'initialise.
        '''
        TEST = self.env.TEST
        TEST.display("thinkai", 3, "ThinkAI - dans _newTechInst()")
        TEST.display("thinkai", 3, "ThinkAI - Création d'une instance de la "\
                     "classe {0}".format(techClass.techClassName()))
        assert self._initOk
#### ATTENTION à faire une meilleure gestion d'erreur ici
        try:
            tech = techClass(self._mem, techArgs)
        except:
            raise Sudoku_Error("SudoThinkAI._newTechInst() : "\
                               "Erreur instanciation de tech de résolution.")
        if tech is None:
            raise Sudoku_Error("SudoThinkAI._newTechInst() : "\
                               "Erreur instanciation de tech de résolution.")
        return tech

    def _makeDataSet(self):
        '''Remplissage du dictionnaire de données qui sera utilisé par le
        système de décision.
        '''
        TEST = self.env.TEST
        TEST.display("thinkai", 3, "ThinkAI - dans _makeDataSet()")
#### TODO : REMPLACER LES VARIABLES D'INSTANCE PAR DES DONNEES MEMOIRE        
        self._aiData[ai.DATA_BEGIN] = self._begin
        self._aiData[ai.DATA_NIV] = self._techNiv
        self._aiData[ai.DATA_NIVMAX] = self._techNivMax
        self._aiData[ai.DATA_INTECH] = self._inTech
        self._aiData[ai.DATA_OPPORT] = self._opport
        self._aiData[ai.DATA_TECH] = self._tech
        self._aiData[ai.DATA_LTECH] = self._lastTech
        self._aiData[ai.DATA_LACT] = self._lastAction
        self._aiData[ai.DATA_LTECHACT] = self._lastTechAction
        self._aiData[ai.DATA_LAIACT] = self._lastAIaction

    def _dispDataSet(self):
        '''Affiche la valeur des données d'avancement de la résolution.'''
        TEST = self.env.TEST
        TEST.display("thinkai", 3, "ThinkAI - dans _dispDataSet()")
        ui.display("self._begin = {0}".format(self._begin))
        ui.display("self._techNiv = {0}".format(self._techNiv))
        ui.display("self._techNivMax = {0}".format(self._techNivMax))
        ui.display("self._inTech = {0}".format(self._inTech))
        ui.display("self._opport = {0}".format(self._opport))
        ui.display("self._tech = {0}".format(self._tech))
        ui.display("self._lastTech = {0}".format(self._lastTech))
        ui.display("self._lastAction = {0}".format(self._lastAction))
        ui.display("self._lastTechAction = {0}".format(self._lastTechAction))
        ui.display("self._lastAIaction = {0}".format(self._lastAIaction))
        return
        
    ##GESTION DE LA PILE DE TECHNIQUES EN COURS
    ##-----------------------------------------

    #Utilisation d'une liste en LIFO avec append() et pop()
    def _initTechPile(self):
        '''Crée la pile des techniques en cours, initialement vide.'''
        self._techNiv = 0
        self._techPile = list()
        return

    def _techPilePush(self, tech):
        self._techPile.append(tech)
        self._techNiv +=1
        return

    def _techPilePop(self):
        try:
            self._techPile.pop()
        except IndexError:
            raise Sudoku_Error("SudoAI : erreur de dépilement de la pile "\
                               "des techniques en cours.")
        self._techNiv -= 1
        return

    def _techPileGet(self):
        if len(self._techPile) == 0:
            return None
        else:
            return self._techPile[-1]   #dernier élément

    ##VERIFICATION DE FIN DE GRILLE
    ##-----------------------------
    def _gridCheckingProcess(self):
        '''Process de vérification de grille terminée. Il se passe en trois
        étapes : d'abord le lancement de la vérification, puis la méthode
        callback est appelée avec le résultat, puis test du résultat.
        '''
        TEST = self.env.TEST
        TEST.display("thinkai", 3, "Thinkai - dans _gridCheckingProcess()")
        assert self._initOk
        if self._needGridChecking is True:
            TEST.display("thinkai", 2, "ThinkAI - La grille doit être vérifiée.")
            return self._startGridChecking()
        if self._checkingGrid is True:
            TEST.display("thinkai", 3, "ThinkAI - Itération après vérification "\
                                       "de la grille :")
            if self._gridCompleted is True:
                TEST.display("thinkai", 3, "ThinkAI - Grille terminée.")
                return self._winResult()
        #La grille n'est pas en vérification ou n'est pas terminée
        TEST.display("thinkai", 3, "ThinkAI - La grille n'est pas terminée.")
        self._gridCompleted = False
        self._gridChecking = False
        self._needGridChecking = False
####
        TEST.pause("thinkai", 4)
        
        return None
        
    def _startGridChecking(self):
        '''Lancement d'une vérification de fin de grille.'''
        TEST = self.env.TEST
        TEST.display("thinkai", 3, "ThinkAI - Dans _startGridChecking()")
        assert self._initOk
        TEST.display("thinkai", 3, "ThinkAI - Retour \"check\" pour "\
                                   "vérification de la grille.")
        self._needGridChecking = False
        self._checkingGrid = True
        self._gridCompleted = False
####
        TEST.pause("thinkai", 4)
        
        return ("check", None)

    #callback
    def checkCompleted(self, checked):
        '''Retour d'une vérification de grille terminée.'''
        TEST = self.env.TEST
        TEST.display("thinkai", 3, "ThinkAI - Méthode checkCompleted()")
        assert self._initOk
        TEST.display("thinkai", 3, "ThinkAI - Retour de vérification de "\
                     "grille terminée : {0}".format(checked))
        self._gridCompleted = checked
        self._mem.memorize("ai_grid_completed", checked, self)
####
        TEST.pause("thinkai", 4)
        
        return ("continue", None)
    
        
    ##METHODES CALL-BACK DE RETOUR DES ACTIONS
    ##----------------------------------------
    #callback
    def aiObsResult(self, found):
        '''Retour d'une observation demandée par ThinkAI'''
        TEST = self.env.TEST
        TEST.display("thinkai", 3, "ThinkAI - Méthode aiObsResult()")
        assert self._initOk
        TEST.display("thinkai", 3, "ThinkAI - retour d'observation : {0}" \
                     .format(found))
        #mémorise le résultat d'observation faite par AI
        self._mem.memorize("ai_obsfound", found, self)
        #après chaque placement on vérifie si la grille est terminée
        self._needGridChecking = True
        #pas besoin de vérification de grille après une observation
        self._needGridChecking = False
        #mise à jour des données d'avancement de résolution
        self._lastAction = "place"
        self._lastAIaction = "place"
        return ("continue", None)

    #callback
    def aiPlaceResult(self, placed=True):
        '''Retour d'un placement demandé par ThinkAI'''
        TEST = self.env.TEST
        TEST.display("thinkai", 3, "ThinkAI - Méthode aiPlaceResult()")
        assert self._initOk
        TEST.display("thinkai", 3, "ThinkAI - retour de placement par AI : "\
                     "{0}.".format(placed))
        self._mem.memorize("ai_placedok", placed, self)
        return ("continue", None)

    #callback
    def techObsResult(self, found):
        '''Retour de l'observation de la technique suggérée par AI'''
        TEST = self.env.TEST
        TEST.display("thinkai", 3, "ThinkAI - Méthode techObsResult()")
        assert self._initOk
        tech = self._mem.recallSafe("ai_suggested_tech", self)
        TEST.display("thinkai", 3, "ThinkAI - retour d'observation par {0}: {1}" \
                     .format(tech, found))
        #mémorise le résultat trouvé par la technique suggérée
        self._mem.memorize("ai_tech_obsfound", found, self)
        #pas besoin de vérification de grille après une observation
        self._needGridChecking = False
        #mise à jour des données d'avancement de résolution
        self._lastAction = "observe"
        self._lastTechAction = "observe"

        return ("continue", None)

    #callback
    def techPlaceResult(self, placed=None):
        '''Retour du placement de la technique suggérée par AI'''
        TEST = self.env.TEST
        TEST.display("thinkai", 3, "ThinkAI - Méthode techPlaceResult()")
        assert self._initOk
        tech = self._mem.recallSafe("ai_suggested_tech", self)
        TEST.display("thinkai", 3, "ThinkAI - retour de placement par {0}: {1}" \
                     .format(tech, placed))
        self._mem.memorize("ai_tech_placedok", placed, self)
        #après chaque placement on prévoit de vérifier si la grille est terminée
#### NOTE : A optimiser avec l'AI pour ne pas vérifier à chaque fois.
        self._needGridChecking = True
        #mise à jour des données d'avancement de résolution
        self._lastAction = "place"
        self._lastTechAction = "place"

        return ("continue", None)

    #callback
    def techReturnsEnd(self, endDetails=None):
        '''Prend connaissance que la technique suggérée a indiqué sa fin
        avec son résultat final.
        '''
        TEST = self.env.TEST
        TEST.display("thinkai", 3, "ThinkAI - dans techReturnsEnd()")
        assert self._initOk
        tech = self._mem.recallSafe("ai_suggested_tech", self)
        TEST.display("thinkai", 3, "ThinkAI - Résultat \"end\" par la "\
                                 "technique {0}".format(tech))
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

        #mise à jour des données d'avancement de résolution
        self._lastAction = "end"
        self._lastTechAction = "end"
####
        TEST.pause("thinkai", 4)

        return ("continue", None)

    #callback
    def techReturnsFail(self, failDetails=None):
        '''Prend connaissance que la technique a généré un fail.'''
        TEST = self.env.TEST
        TEST.display("thinkai", 3, "ThinkAI - dans techReturnFail()")
        assert self._initOk
        tech = self._mem.recallSafe("ai_suggested_tech", self)
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

        #mise à jour des données d'avancement de résolution
        self._lastAction = "end"
        self._lastTechAction = "end"

        return ("continue", None)

    #callback
    def actionResult(self):
        '''Récupère de Thinking le résultat de la dernière action effectuée
        par la technique que ThinkAI a suggéré d'utiliser.
        '''
        TEST = self.env.TEST
        TEST.display("thinkai", 3, "ThinkAI - Méthode actionResult()")
        assert self._initOk
        TEST.display("thinkai", 3, "ERREUR : METHODE actionResult() INCOMPLETE")
        return (None, None)


    ##FIN DE PARTIE
    ##-------------
    def _winResult(self):
        TEST = self.env.TEST
        TEST.display("thinkai", 3, "ThinkAI - dans _winResult()")
        assert self._initOk
        TEST.display("thinkai", 1, "AI : Grille terminée, la partie est gagnée.")
        return ("end", ("win",None))
    

    def techName(self, tech):
        '''Retourne le nom de la classe de la technique de l'instance indiquée'''
        TEST = self.env.TEST
        assert self._initOk
        if tech is not None:
            return tech.techName()
        else:
            return None

    def lastTechName(self):
        '''Retourne le nom de la dernière technique suggérée'''
        TEST = self.env.TEST
        assert self._initOk
        lastTech = self._tmp_uniqueTech
        if lastTech is None: 
            return None
        else:
            return lastTech.techName()
        
        
            

##TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 
##TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 

if __name__ == "__main__":

    env = sudoenv.SudoEnv("TEST THINKAI")
    TEST = env.TEST
    TEST.levelAll(0)

    #lancement de l'AI
    ui.display("\nSIMULATION : Lancement de l'AI")
    mem = SudoMemory(env=env)
    TEST.level("memory", 0)
    tai = SudoThinkAI(mem, env = env)
    TEST.test("thinkai", 3)
    TEST.test("ai", 3)

    #affichage des données initiales
    ui.display("\nSIMULATION : Données initiales :")
    tai._aiData.disp()

    #simulation : premier appel par Thinking
    ui.display("\nSIMULATION : Premier appel par Thinking")
    TEST.pause("thinkai", 1)
    da = tai.decideAction()

    #simulation : la première technique a fait une observation
    #found = (2, (1,4))
    #tai.techObsResult(found)
    #itération et nouvel appel par Thinking
    #da = tai.decideAction()

##    #import sudoobserver
##    #import sudogrid
##    import sudomemory
##    import sudotestall
##    testlevel = 3
##    TEST.levelAll(testlevel)
##    ui.display("Tous les niveaux de test sont à {0}".format(testlevel))
##
##    mem = sudomemory.SudoMemory()
##    ai = SudoThinkAI(mem)
##    #ai.init(mem)
