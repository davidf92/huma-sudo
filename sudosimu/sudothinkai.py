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

Historique des mises-à-jour :
06/12/2017 - Les règles de décision sont totalement importées du module
'sudoai' et les autres imports directs de code d'enchaînement de techniques sont
supprimés. Cette architecture est conçue pour rester à long terme.
21/11/2017 - Les classes dérivent de la classe de base SudoBaseClass et
utilisent les contextes d'environnement et de test liés fournis par cette classe.
L'import du module 'sudotest' est supprimé. Cette architecture est définitive.
21/11/2017 - Les imports sont mis à jour comme dans tous les autres modules
pour exécuter ce module isolément, depuis l'intérieur du dossier 'sudosimu'ou
depuis d'extérieur sous forme de package.
22/10/2017 - Déport dans un sous-module de la fonction qui propose une
technique. Le code de suggestAction() est déporté dans cette fonction. De cette
manière il est simple (dans la phase de développement) de modifier la
stratégie de résolution sans toucher au code générique.
'''


#exécution interne au package
if __name__ in ("__main__", "sudothinkai"):
    import sudobaseclass as base
    import sudoenv
    import sudoui as ui
    import sudorules as rules
    from sudorules import Sudoku_Error
    from sudomemory import SudoMemory
    import sudoai as ai
    from sudotechimports import *
#exécution depuis l'extérieur du package sudosimu
elif __name__ == "sudosimu.sudothinkai":
    from sudosimu import sudobaseclass as base
    from sudosimu import sudoenv
    from sudosimu import sudoui as ui
    from sudosimu import sudorules as rules
    from sudosimu.sudorules import Sudoku_Error
    from sudosimu.sudomemory import SudoMemory
    from sudosimu import sudoai as ai
    from sudosimu.sudotechimports import *
else:
    raise Exception("Impossible de faire les imports dans le module sudothinkai.")

#OBSOLETE
#from sudosimu.sudothinktech import SudoThinkTech

##Dictionnaire d'identification des techniques
##ATTENTION : les noms de techniques doivent être les mêmes que ceux connus
##par SudoAI dans sudoai.py
TechDict = { "techchrcga", TechChRCgridAll, \
             "techlplcg", TechLastPlcGrid, \
             "techlplcp", TechLastPlcPlace
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
        #reprendre un précédente niveau de test s'il existe déjà
        oldlev = env.testLevel("thinkai")
        if oldlev is not None and testlevel != oldlev:
            testlevel = oldlev
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
        self._gridChecked = False   #état de la grille inconnu au début
        self._checkingGrid = False
        self._gridCompleted = False
        #gestion du cycle de résolution (test)
        self._step = 1
        self._nbtotplc = 0  #nombre total de placements de la résolution
        self._nbplcloop = 0     #nombre de placements sur la boucle en cours
        self._nbplc = 0     #nombre de placements de la technique en cours

        self._initOk = True
        if TEST.ifLevel("thinkai", 3) is True:
            self._dispVariables()
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
        self._techNivMax = 2    #Niveau max d'empilement acceptable
        self._inTech = False    #True si une technique est en cours
        self._opport = False    #True si une recherche d'opportunité est en cours
        #technique en cours
        self._tech = None       #code de la technique en cours
        self._techInst = None   #instance de la technique en cours
        self._techName = None   #Nom de la technique en cours
        #précédente tech de même niveau
        self._lastTech = None   #code de la préc. tech. de même niveau
        self._lastTechName = None #Nom de la préc. tech. de même niveau
        #tech de niveau inférieur (active)
        self._techNivInf = None
        self._techNivInfInst = None
        self._techNivInfName = None
        #précédente tech de niveau inférieur
        self._lastTechNivInf = None     #Inst. préc.tech. de niveau inférieur
        self._lastTechNivInfName = None #Nom. préc.tech. de niveau inférieur
        #actions
        self._lastAction = None     #Dernière action exécutée
        self._lastTechAction = None #Dernière action exécutée par une tech
        self._lastAIaction = None   #Dernière action exécutée pra l'AI

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

        #Suivre le processus de vérification de grille s'il est commencé
        if self._checkingGrid is True:
            r = self._gridCheckingProcess()
            if r is not None:
                return r

###### VERSION DE TEST DU MODULE techlplcp
## Dans cette version, sudothinkai créée une instance de TechLastPlcPlace
## et retourne toujours cette instance sans interroger AI.
##        
##        if self._techInst is None:
##            TEST.display("thinkai", 3, "ThinkAI - VERSION DE TEST - "\
##                         "Création d'une instance de TechLastPlcPlace pour "\
##                         "la case (7,9)")
##            inst = self._newTechInst(TechLastPlcPlace, (7,9))
##            self._techInst = inst
##            return("tech", (inst, "insert"))
##        else:
##            TEST.display("thinkai", 3, "ThinkAI - VERSION DE TEST - "\
##                         "Suite de la même instance de TechLastPlcPlace.")
##            return ("tech", (self._techInst, "same"))
##            
##################
        
        #Interroger le système de décision
        if TEST.ifLevel("thinkai", 3) is True:
            self._dispVariables()
        self._makeDataSet()
        try:
            suggestion = self._ai.suggest()
        except:
            raise Sudoku_Error("SudoThinkAI.decideAction() : "\
                               "Erreur en appelant SudoAI.suggest()")

        #analyser la réponse
        TEST.display("thinkai", 3, "Retour à ThinkAI.decideAction()")
        su = suggestion[0]
        TEST.display("thinkai", 3, "decideAction() - La suggestion AI est : "\
                                   "{0}".format(su))
        if su == "continue":
            #continuer la technique en cours - rien à changer
            TEST.display("thinkai", 3, "SudoThinkAI.decideAction() - Décision "\
                         " = continuer la technique en cours.")
            action = ("tech", (self._techInst, "same"))
        elif su == "check":
            #vérifier si la grille est remplie
            TEST.display("thinkai", 3, "SudoThinkAI.decideAction() - Décision "\
                         "= vérifier si la grille est terminée.")
            action = self._startGridChecking()
        elif su == "start_tech":
            #insérer une nouvelle technique
            TEST.display("thinkai", 3, "SudoThinkAI.decideAction() - Décision "\
                         " = insérer la technique \"{0}\".".format(suggestion[1]))
            TEST.display("thinkai", 1, "AI : Lancement d'une nouvelle technique "\
                         "de résolution : \"{0}\".".format(self._techName))
            action = self._startTech(suggestion[1])
        elif su == "discard_tech":
            #arrêter la technique en cours
            TEST.display("thinkai", 3, "SudoThinkAI.decideAction() - Décision "\
                         "= arrêter la technique en cours.")
            TEST.display("thinkai", 1, "AI : Arrêt de la technique de "\
                         "résolution \"{0}\".".format(self._techName))
            action = self._discardTech()
        elif su == "discard_all":
            #arrêter toutes les techniques en cours
            TEST.display("thinkai", 3, "SudoThinkAI.decideAction() - Décision "\
                         "= arrêter toutes les technique en cours.")
            TEST.display("thinkai", 1, "AI : Arrêt de toutes les techniques "\
                         "de résolution en cours.")
            action = self._discardAll()
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
            self._dispVariables()
        #TEST : pause de vérification des données
        TEST.pause("thinkai", 4)
        TEST.display("thinkai", 3, "SudoThinkAI - Décision retournée = {0}. "\
                                 .format(action))
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
        elif suggested == "techlplcp":
            #la tech LastPlcPlace prend comme argument la case où a été
            #fait le placement précédent
            (row, col, val) = self._mem.recall("ai_lastplacement", self)
            inst = self._newTechInst(TechLastPlcPlace, (row, col))

        #mettre à jour les données d'avancement de la résolution en cours
        self._begin = False
        self._inTech = True
        self._techNiv += 1
        self._opport = True if self._techNiv >= 2 else False
        #pas encore d'action dans la nouvelle technique
        self._lastAction = None
        self._lastTechAction = None
        #tech active de niveau inférieur
        self._techNivInf = self._tech
        self._techNivInfInst = self._techInst
        self._techNivInfName = self._techName
        #précédente tech de niveau inférieur
        self._lastTechNivInf = self._lastTech
        self._lastTechNivInfName = self._lastTechName
        #nouvelle technique en cours
        self._tech = suggested
        self._techInst = inst
        self._techName = inst.techName()
        self._lastTech = None
        
        #Retour vers Thinking = insertion de la nouvelle technique
        return ("tech", (self._techInst, "insert"))
        
        
    def _discardTech(self):
        '''Abandon de la technique en cours. Dépilement et retour à la tech
        précédente s'il y en a une.
        '''
        TEST = self.env.TEST
        TEST.display("thinkai", 3, "ThinkAI : dans _discardTech()")
        assert self._initOk
        #vérifications de cohérence
        assert self._techNiv > 0
        assert self._tech is not None
        #supprimer l'instance de la technique abandonnée
        del(self._techInst)
        #dépiler

        #mettre à jour les données d'avancement de la résolution en cours
        self._techNiv -= 1
        self._inTech = True if self._techNiv > 0 else False
        self._opport = True if self._techNiv >= 2 else False
        #précédente tech de même niveau = celle qui se termine
        self._lastTech = self._tech
        self._lastTechName = self._techName
        #technique en cours = la précédente de niveau inférieur
        self._tech = self._techNivInf
        self._techInst = self._techNivInfInst
        self._techName = self._techNivInfName
        #tech de niveau inférieur (active)
        self._techNivInf = None
        self._techNivInfInst = None
        self._techNivInfName = None
        #précédente tech de niveau inférieur
        self._lastTechNivInf = None     
        self._lastTechNivInfName = None 
        #actions
        self._lastAction = None     
        self._lastTechAction = None 
        self._lastAIaction = None   

        #l'action précédente est maintenant celle de la technique de niveau
        #inférieur s'il y en avait une, c-à-d le "place" qui avait déclenché
        #l'imbrication
        if self._techNiv >= 1:
            self._lastAction = "place"
            self._lastTechAction = "place"
        else:
            self._lastAction = None
            self._lastTechAction = None

        #Retour vers thinking = reprendre la technique de niveau inférieur
        #s'il y en avait une, sinon passer à l'itération suivante
        if self._techInst is not None:
            action = ("tech", (self._techInst, "revert"))
        else:
            action = ("continue", None)
        return action
    
    def _discardAll(self):
        '''Arrêt de toutes les techniques en cours et retour au niveau 0. La
        pile d'imbrication est alors vide.
        '''
        TEST = self.env.TEST
        TEST.display("thinkai", 3, "ThinkAI : dans _discardAll()")
        TEST.display("thinkai", 3, "METHODE A ECRIRE")
        assert self._initOk
        raise Sudoku_Error("_discardAll() n'existe pas encore.")


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
        TEST.display("thinkai", 3, "Retour à ThinkAI._newTechInst")
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
        self._aiData[ai.AIDATA_BEGIN] = self._begin
        self._aiData[ai.AIDATA_NIV] = self._techNiv
        self._aiData[ai.AIDATA_NIVMAX] = self._techNivMax
        self._aiData[ai.AIDATA_INTECH] = self._inTech
        self._aiData[ai.AIDATA_OPPORT] = self._opport
        self._aiData[ai.AIDATA_GRIDCHECKED] = self._gridChecked
        self._aiData[ai.AIDATA_TECH] = self._tech
        self._aiData[ai.AIDATA_LTECH] = self._lastTech
        self._aiData[ai.AIDATA_LACT] = self._lastAction
        self._aiData[ai.AIDATA_LTECHACT] = self._lastTechAction
        self._aiData[ai.AIDATA_LAIACT] = self._lastAIaction
        return

    def _dispVariables(self):
        '''Affichage des variables d'avancement de la résolution.'''
        TEST = self.env.TEST
        TEST.display("thinkai", 3, "ThinkAI - Variables d'avancement "\
                     "de la résolution :")
        TEST.display("thinkai",3, "_begin = {0}".format(self._begin))
        TEST.display("thinkai",3, "_techNiv = {0}".format(self._techNiv))
        TEST.display("thinkai",3, "_techNivMax = {0}".format(self._techNivMax))
        TEST.display("thinkai",3, "_inTech = {0}".format(self._inTech))
        TEST.display("thinkai",3, "_opport = {0}".format(self._opport))
        TEST.display("thinkai",3, "_tech = {0}".format(self._tech))
        TEST.display("thinkai",3, "_lastTech = {0}".format(self._lastTech))
        TEST.display("thinkai",3, "_lastAction = %s" %(self._lastAction))
        TEST.display("thinkai",3, "_lastTechAction = %s" %(self._lastTechAction))
        TEST.display("thinkai",3, "_gridChecked = %s" %(self._gridChecked))
        TEST.display("thinkai",3, "_gridCompleted = %s" %(self._gridCompleted))
        TEST.display("thinkai",3, "_checkingGrid = %s" %(self._checkingGrid))
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
        if self._checkingGrid is True:
            TEST.display("thinkai", 3, "ThinkAI - Itération après vérification "\
                                       "de la grille :")
            if self._gridCompleted is True:
                TEST.display("thinkai", 3, "ThinkAI - Grille terminée.")
                return self._winResult()
        #La grille n'est pas en vérification ou n'est pas terminée
        TEST.display("thinkai", 3, "ThinkAI - La grille n'est pas terminée.")
        self._gridCompleted = False
        self._checkingGrid = False
        self._gridChecked = True
        if TEST.ifLevel("thinkai", 3) is True:
            self._dispVariables()
        return None
        
    def _startGridChecking(self):
        '''Lancement d'une vérification de fin de grille.'''
        TEST = self.env.TEST
        TEST.display("thinkai", 3, "ThinkAI - Dans _startGridChecking()")
        assert self._initOk
        TEST.display("thinkai", 3, "ThinkAI - Retour \"check\" pour "\
                                   "vérification de la grille.")
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
    def aiObsResult(self, pattern, found):
        '''Retour d'une observation demandée par ThinkAI. Le retour contient
        l'information recherchée (pattern) et le résultat (found), qui sont
        alors mémorisés par le joueur.
        '''
        TEST = self.env.TEST
        TEST.display("thinkai", 3, "ThinkAI - Méthode aiObsResult()")
        assert self._initOk
        TEST.display("thinkai", 3, "ThinkAI - retour d'observation : {0}" \
                     .format(found))
        #mémorise l'observation et son résultat
        self._mem.memorize("ai_lastobspattern", pattern, self)
        self._mem.memorize("ai_lastobsfound", found, self)
        self._lastAction = "observe"
        self._lastAIaction = "observe"
        if TEST.ifLevel("thinkai", 3) is True:
            self._dispVariables()
        return ("continue", None)

    #callback
    def aiPlaceResult(self, placement, placed=True):
        '''Retour d'un placement demandé par ThinkAI Le retour contient les
        données du placement demandé (placement) et le résultat (placed), qui
        sont mémorisés par le joueur.
        '''
        TEST = self.env.TEST
        TEST.display("thinkai", 3, "ThinkAI - Méthode aiPlaceResult()")
        assert self._initOk
        TEST.display("thinkai", 3, "ThinkAI - retour de placement par AI : "\
                     "{0}.".format(placed))
        #mémorise le placement fait et son résultat
        mem = self._mem
        mem.memorize("ai_lastplacement", placement, self)
        mem.memorize("ai_lastplacedok", placed, self)
        self._lastAction = "place"
        self._lastAIaction = "place"
        return ("continue", None)

    #callback
    def techObsResult(self, pattern, found):
        '''Retour de l'observation de la technique suggérée par AI. Le retour
        contient l'information recherchée (pattern) et le résultat (found).
        '''
        TEST = self.env.TEST
        TEST.display("thinkai", 3, "ThinkAI - Méthode techObsResult()")
        assert self._initOk
        tech = self._mem.recallSafe("ai_suggested_tech", self)
        TEST.display("thinkai", 3, "ThinkAI - retour d'observation par {0}: {1}" \
                     .format(tech, found))
        #mémorise l'observation et son résultat
        self._mem.memorize("ai_lastobspattern", pattern, self)
        self._mem.memorize("ai_lastobsfound", found, self)
        self._lastAction = "observe"
        self._lastTechAction = "observe"
        if TEST.ifLevel("thinkai", 3) is True:
            self._dispVariables()
        return ("continue", None)

    #callback
    def techPlaceResult(self, placement, placed=True):
        '''Retour du placement de la technique suggérée par AI. le retour
        contient les données du placement demandé (placement) ainsi que le
        résultat (placed).
        '''
        TEST = self.env.TEST
        TEST.display("thinkai", 3, "ThinkAI - Méthode techPlaceResult()")
        assert self._initOk
        tech = self._mem.recallSafe("ai_suggested_tech", self)
        TEST.display("thinkai", 3, "ThinkAI - retour de placement par {0}: {1}" \
                     .format(tech, placed))
        #mémorise le placement fait et son résultat
        mem = self._mem
        mem.memorize("ai_lastplacement", placement, self)
        mem.memorize("ai_lastplacedok", placed, self)
        #mise à jour des données d'avancement de résolution
        self._lastAction = "place"
        self._lastTechAction = "place"
        #il y a eu un placement donc l'état de la grille n'est plus connu
        self._gridChecked = False
        if TEST.ifLevel("thinkai", 3) is True:
            self._dispVariables()
        return ("continue", None)

    #callback
    def techReturnsEnd(self, endDetails=None):
        '''Prend connaissance que la technique suggérée a indiqué sa fin
        avec son résultat final.
        '''
        TEST = self.env.TEST
        TEST.display("thinkai", 3, "ThinkAI - dans techReturnsEnd()")
        assert self._initOk
        #tech = self._mem.recallSafe("ai_suggested_tech", self)
        tech = self._tech
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
