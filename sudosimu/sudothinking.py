# -*- coding: cp1252 -*-

'''SudoThinking est la classe qui encapsule la réflexion du joueur pendant la
résolution et qui applique la logique d'enchaînement des différentes actions,
principalement l'observation de la grille pour y chercher de l'information. 
'''

'''
Dernière mise-à-jour : 14/11/2018
Historique des modifications :
14/11/2018 - Correction code de test obsolete / sudoenv, sudoui
08/12/2017 - Le retour de ai.decideAction est modifié pour prendre en compte la
    vérification de grille terminée, qui est décidée dans le module 'thinkai'.
    La fonction _endGameDetails() est ajoutée pour cela.
'''

#exécution directe du module
if __name__ in ("__main__", "sudothinking"):
    import sudobaseclass as base
    import sudoenv
#    import sudoui as ui        #OBSOLETE
    import sudorules as rules
    from sudorules import Sudoku_Error
    import sudogridview as gridview
    from sudogridview import SudoGridView
    from sudomemory import SudoMemory
    from sudothinkprofile import SudoThinkProfile
    from sudothinkai import SudoThinkAI
#exécution en package
elif __name__ == "sudosimu.sudothinking":
    from sudosimu import sudobaseclass as base
    from sudosimu import sudoenv
#    from sudosimu import sudoui as ui      #OBSOLETE
    from sudosimu import sudorules as rules
    from sudosimu.sudorules import Sudoku_Error
    from sudosimu import sudogridview as gridview
    from sudosimu.sudogridview import SudoGridView
    from sudosimu.sudomemory import SudoMemory
    from sudosimu.sudothinkprofile import SudoThinkProfile

#### TEST DU MODULE sudolplcp
    from sudosimu.sudothinkai import SudoThinkAI
    ##from sudosimu.sudothinkai_testlplcp import SudoThinkAI
####
else:
    raise Exception("Impossible de faire les imports dans le module sudothinking.")


class SudoThinking(base.SudoBaseClass):
    '''Réflexion de l'utilisateur pour la résolution de la grille et
    l'enchaînement des observations et placements.
    '''
    def __init__(self, mem, profile=None, \
                 env=None, testlevel=sudoenv.TEST_THINKINGLEVEL):
        '''Initialisation de l'instance. Un profil de pensée peut être donné.'''
        #init de la classe racine
        #reprendre un précédente niveau de test s'il existe déjà
        assert isinstance(env, sudoenv.SudoEnv) or env is None
        assert isinstance(testlevel, int) and testlevel>=0 \
                or testlevel is None
        oldlev = env.testLevel("thinking")
        if oldlev is not None and testlevel != oldlev:
            testlevel = oldlev
        base.SudoBaseClass.__init__(self, env=env, \
                                    testlabel="thinking", testlevel=testlevel)
        #ok init de cette classe
        TEST = self.env.TEST
        TEST.display("thinking", 3, "SudoThinking - Dans __init__(), "\
                                     "nouvelle instance.")
        assert isinstance(mem, SudoMemory)
        assert profile is None or isinstance(profile, SudoThinkProfile)
        TEST.display("thinking", 1, "Création de la pensée du joueur")
        self._mem = mem
        self._profile = profile
        #crée et initialise l'instance de SudoAI avec la mémoire de travail
        self._thinkAI = SudoThinkAI(mem, env=self.env)
        self._initOk = True
        return

    def analyse(self):
        '''Fait l'analyse de la situation en cours en consultant l'AI, appelle
        la technique de résolution choisie en gérant les imbrications, et
        traite la suite des observations et des placements.
        Retourne une donnée "next_action" qui indique ce que va être la
        prochaine action de jeu (observation, placement, fin, etc.)
        '''
        TEST = self.env.TEST
        TEST.display("thinking", 3, "Thinking - dans analyse()")
        assert self._initOk
        TEST.display("thinking", 1, "Itération de résolution")
        mem = self._mem
        #Commencer par la prise en compte des résultats de l'action précédente.
        lastAction = mem.recall("think_lastaction", self)
        if lastAction in ("observe", "place"):
            self._lastActionResult(lastAction)
        
        #Demande à l'AI d'indiquer l'action suivante
        (suggest, suggestDetails) = self._thinkAI.decideAction()
        TEST.display("thinking", 2, "Thinking : Suggestion suivante de AI = {0}" \
                     .format((suggest, suggestDetails)))
        
        #Cas ou l'action sera à faire par une technique structurée
        if suggest == "tech":
            (tech, techRelation) = suggestDetails
            nextAction = self._applyTech(tech, techRelation)
            #préparer l'itération suivante
            mem.memorize("think_lastsuggest", "tech", self)
            mem.memorize("think_lasttech", tech, self)
        #Cas où l'action sera à faire directement par ThinkAI:
        elif suggest in ("observe", "place", "continue"):
            nextAction = self._applyAI(suggest, suggestDetails)
            mem.memorize("think_lastsuggest", "thinkAI", self)
            mem.memorize("think_lasttech", "thinkAI", self)
        #Cas où AI vérifie si la grille est terminée
        elif suggest == "check":
            nextAction = self._checkCompleted()
            mem.memorize("think_lastsuggest", "check", self)
        #Cas où AI décide que c'est la fin de résolution
        elif suggest == "end":
            details = self._endGameDetails(suggestDetails)
            nextAction = ("end", details)
            mem.memorize("think_lastsuggest", "end", self)
            mem.memorize("think_lasttech", None, self)
        #Cas où il y a eu un fail : gestion spécifique
        elif suggest == "fail":
            details = self._failDetails(suggestDetails)
            nextAction = ("fail", details)
            mem.memorize("think_lastsuggest", "fail", self)
            mem.memorize("think_lasttech", None, self)
        else:
            #ne devrait jamais arriver
            raise Sudoku_Error("ThinkAI.suggestAction() retourne '{0}' "\
                                 .format(suggest) + " : invalide.")

        #mémorisation de ce qui est décidé. La prochaine action deviendra la
        #précédente action de l'itération suivante de Thinking.analyse()
        mem.memorize("think_lastaction", nextAction[0], self)
        mem.memorize("think_lastaction_details", nextAction[1], self)
                         
        TEST.display("thinking", 2, "Thinking : Action suivante = {0}" \
                     .format(nextAction))
        #affichage en clair
        if nextAction[0] in ("continue", "observe", "place"):
            TEST.display("thinking", 1, "Action décidée par la pensée du "\
                         "joueur :\n{0}".format(nextAction))
        elif nextAction[0] == "end":
            TEST.display("thinking", 1, "l'AI a décidé d'arrêter la partie "\
                         "avec le résultat :\n{0}.".format(nextAction[1]))
        elif nextAction[0] == "fail":
            TEST.display("thinking", 1, "l'AI a détecté un incident dans la "\
                         "résolution et va tenter de le résoudre.")
        return nextAction

    def _lastActionResult(self, lastAction):
        '''En début d'analyse du jeu, récupère les résultats d'observation ou
        placement de l'action précédente et les transmets à la technique
        concernée et à l'AI.
        '''
        TEST = self.env.TEST
        TEST.display("thinking", 3, "Thinking - dans _lastActionResult()")
        assert self._initOk
        mem = self._mem
        lastSuggest = mem.recall("think_lastsuggest", self)
        #Cas d'une précédente action directe de AI.
        if lastSuggest == "thinkAI":
            #retour d'une observation
            if lastAction == "observe":
                TEST.display("thinking", 3, "Thinking : Cas particulier : "\
                             "AI retourne 'observe' ")
                pattern = mem.recall("think_lastobspattern", self)
                found = mem.recallObs()
                TEST.display("thinking", 3, "l'observation retournée est {0}"\
                                             .format(found))
                self._thinkAI.aiObsResult(pattern, found)
            #retour d'un placement
            elif lastAction == "place":
                TEST.display("thinking", 3, "Thinking : Cas particulier : "\
                             "AI retourne 'place' ")
                placement = mem.recall("think_lastplacement", self)
#### ATTENTION - A faire : gestion des retours de placements ################
                placed = True
#############################################################################
                self._thinkAI.aiPlaceResult(placement, placed)
        #Cas d'une technique appliquée lors de l'itération précédente.
        #Transmet aussi son résultat à AI pour la prise de décision
        elif lastSuggest == "tech":
            lastTech = mem.recall("think_lasttech", self)
            #retour d'une observation
            if lastAction == "observe":
                TEST.display("thinking", 3, "Thinking : Cas particulier : "\
                             "AI retourne 'observe' ")
                pattern = mem.recall("think_lastobspattern", self)
                found = mem.recallObs()
                TEST.display("thinking", 3, "l'observation retournée est {0}"\
                             .format(found))
                #le résultat est transmis à la technique
                lastTech.obsFound(found)
                #et à l'AI
                self._thinkAI.techObsResult(pattern, found)
            #retour d'un placement
            elif lastAction == "place":
                TEST.display("thinking", 3, "Thinking : Cas particulier : "\
                             "AI retourne 'place' ")
                placement = mem.recall("think_lastplacement", self)
#### ATTENTION - A faire : gestion des retours de placements ################
                placed = True
#############################################################################
                lastTech.placeOk(placed)
                self._thinkAI.techPlaceResult(placement, placed)

        #Cas de la vérification par AI de grille terminée
        elif lastSuggest == "check":
            checked = mem.recallObs()
            TEST.display("thinking", 3, "Thinking : Résultat de l'observation "\
                         "de grille terminée : {0}".format(checked))
            self._thinkAI.checkCompleted(checked)
        return

    def _checkCompleted(self):
        '''Vérification par AI si la grille est terminée ou non.'''
        TEST = self.env.TEST
        TEST.display("thinking", 3, "Thinking : dans _checkCompleted()")
        assert self._initOk
        TEST.display("thinking", 2, "Thinking - Vérification de grille "\
                                     "terminée.")
        return ("observe", (gridview.OBS_GRID_COMPLETED, None))

    
    def _applyAI(self, action, actionDetails):
        '''Application d'une action directe demandée par ThinkAI, en dehors
        du contexte d'une technique structurée.
        '''
        TEST = self.env.TEST
        TEST.display("thinking", 3, "Thinking : fontion _applyAI()")
        assert self._initOk
        if action == "observe":
            pattern = actionDetails[0]
            nextAction = ("observe", pattern)
        elif action == "place":
            placement = actionDetails[0]
            nextAction = ("place", placement)
        elif action == "continue":
            nextAction = ("continue", None)
##            #la précédente action était aussi faite par ThinkAI
##            lastAction = mem.recall("thinking_lastaction", self)
##            #cas particulier : ThinkAI a fait une observation juste avant
##            if lastAction == "observe":
##                found = mem.recallObs()
##                nextAction = self._thinkAI.obsFound(found)
##            else:
##                nextAction = ("continue", None)
        else:
            #ne devrait jamais arriver
            raise Sudoku_Error("erreur retour de ThinkAI.suggestAction()")

        #ok _applyAI() se termine bien
        TEST.display("thinking", 3,
                     "Thinking : AI retourne : {0}" \
                     .format(nextAction))
        return nextAction

    def _applyTech(self, tech, techRelation):
        '''Application d'une technique de résolution structurée. Il y a
        plusieurs cas selon que c'est la même technique que lors de l'itération
        précédente, ou une nouvelle technique imbriquée ou la reprise d'une
        technique précédemment interrompue.
        Le retour de la technique doit être traité par AI avant de décider
        de la prochaine action.
        '''
        TEST = self.env.TEST
        TEST.display("thinking", 3, "Thinking : Fonction _applyTech()")
        TEST.display("thinking", 2, \
                     "Action = application de la technique {0}" \
                     .format(tech.techName()))
        assert self._initOk
        mem = self._mem

        #Application de la technique
        #cas de la même technique qu'à l'itération précédente
        if techRelation == "same":
            TEST.display("thinking", 3, "Thinking - Application de la même"\
                         "technique.")
            techResult = tech.apply()
        #cas de l'insertion d'une nouvelle technique
        elif techRelation == "insert":
            TEST.display("thinking", 3, \
                         "Thinking - Insertion de nouvelle technique.")
            techResult = tech.apply()
        #cas du retour à une technique mise en attente
        elif techRelation == "revert":
            TEST.display("thinking", 3, \
                         "Thinking - Retour au niveau précédent de technique.")
            techResult = tech.resume() 
        else:
            #ne devrait jamais arriver
            raise Sudoku_Error( \
                "Erreur dans Thinkingretour invalide de tech.apply")
        TEST.display("thinking", 3, "Thinking - La technique {0} a retourné "\
                     "{1}".format(tech.techName(), techResult))

        #Observation ou placement : le joueur se rappelle ce qu'il est
        #en train de faire
        if techResult[0] == "observe":
            mem.memorize("think_lastobspattern", techResult[1], self)
            nextAction = techResult
        elif techResult[0] == "place":
            mem.memorize("think_lastplacement", techResult[1], self)
            nextAction = techResult
        #Cas d'un retour 'fail' de la technique
        elif techResult[0] == "fail":
            failDetails = techResult[1]
            TEST.display("thinking", 3, "Thinking - La technique {0} retourne "\
                         " 'fail'.".format(tech.techName()))
            nextAction = self._thinkAI.techReturnsFail(failDetails)
        #Dans le cas où la technique appliquée a signalé sa fin avec "end",
        #transmettre à AI qui va décider de la prochaine action. 
        elif techResult[0] == "end":
            endDetails = techResult[1]
            TEST.display("thinking", 3, "la technique {0} signale sa fin" \
                         .format(tech.techName()) + "avec le résultat : '{0}'"\
                         .format(endDetails))
            nextAction = self._thinkAI.techReturnsEnd(endDetails)
        else:
            nextAction = techResult
        return nextAction


##    def _sameTechTransmitLastResult(self, mem, tech, lastAction):
##        '''transmet à la dernière technique le résultat de sa dernière action,
##        si AI décide l'appliquer de nouveau cette technique.
##        Puis transmet également à AI ce résultat de la technique.
##        '''
##        TEST.display("thinking", 3, "Thinking - Transmission à {0} de son " +\
##                    "résultat de dernière action : {1}" \
##                    .format(tech.techName(), lastAction))
##        assert self._initOk
##        if lastAction == "observe":
##            TEST.display("thinking", 3, \
##                         "Thinking - Retour d'observation de la dernière technique.")
##            meth = tech.obsFound
##            methAI = self._thinkAI.returnTechObs
##            args = mem.recallObs()
##            TEST.display("thinking", 3, "l'observation retournée est {0}"\
##                                         .format(args))
##        elif lastAction == "place":
##            TEST.display("thinking", 3, \
##                         "Thinking - Retour de placement de la dernière technique.")
##            meth = tech.placeOk
##            methAI = self._thinkAI.returnTechPlace
##            args = None
##        else:
##            TEST.display("thinking", 3, \
##                         "Thinking - Erreur dans _sameTechTransmitLastResult() " + \
##                         "la valeur de 'lastAction' est incorrecte")
##            #ne devrait jamais arriver
#### TRAITEMENT FAIL à faire
##            raise Sudoku_Error("Fail mémoire dans Thinking")
##        #transmet à la technique son résultat et à AI le retour de la technique
##        try:
##            meth(mem, args)
##            methAI(mem, args)
##            r = ("continue", None)
##        except:
##### A FAIRE ###
##  ### Un bon traitement d'erreur. Pour le moment = exception
##            raise Sudoku_Error("Fail dans Thinking._lastTechResult()")
##            r = ("fail", None)
##
##        return r
        
    def _endGameDetails(self, endDetails):
        '''La partie est terminée. Fait toute action nécessaire à la fin.
        Fournit également un texte affichable, qui sera ajouté aux 'endDetails'.
        '''
        TEST = self.env.TEST
        assert self._initOk
        endTitle = "Résultat : la partie est terminée"
        endText = ""
        return (endTitle, endText)

    def _failDetails(self, fDetails):
        '''La partie est terminée. Fait toute action nécessaire à la fin.
        Fournit également un texte affichable, qui sera ajouté aux 'endDetails'.
        '''
        TEST = self.env.TEST
        assert self._initOk
        failTitle = "Fail : la résolution génère une erreur."
        failText = "La résolution va continuer en tentant de gérer l'erreur."
        return (failTitle, failText)
    
#end class     





##TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 
##TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 



if __name__ == "__main__":
                    
    import sudogrid

    env = sudoenv.SudoEnv()
    ui = env.ui
    TEST = env.test
    
    grid=None
    mem=None
    think=None
    view=None
    testlevel = 3
    TEST.levelAll(testlevel)
    print("Tous les niveaux de test sont à {0}".format(testlevel))
    
    print("\nTest du module sudothinking")
    print("----------------------------\n")
    print("\nCréation de la grille")
    gr = sudogrid.SudoGrid()
    bl = sudogrid.SudoBloc()
    list9 = [2,5,0,6,8,0,0,3,4]
#    import sudoui
    ui.display("Choisir un fichier de test")
    fich = ui.sudoNumTestFich()
    if not fich:
        ui.display("Abandon")
        exit()
    print("Fichier choisi : {0}\n".format(fich))
    vals = ui.sudoFichReadLines(fich)
    print("Variable SudoBloc : bl")
    bl = sudogrid.SudoBloc()
    print("Variables SudoGrid : gr et grid")
    gr = sudogrid.SudoGrid()
    gr.fillByRowLines(vals)
    grid = gr
    gridInit = grid.copy()
    print("Grille test choisie : grid = ")
    gr.show()

    print("\nCréation de la mémoire de travail")
    print("Variable SudoMemory : mem")
    mem = SudoMemory(env=env)
    
    print("Variable SudoGridView : view")
    view = SudoGridView(grid, env=env)
    print("\nTEST au niveau 3\n")
    TEST.test("techlastplc",3)
    TEST.test("loop", 0)
    #sudoio.sudoPause()

    #Paramètres I/O tests
    TEST.test("analyse", 1)
    TEST.test("thinking",2)
    TEST.test("thinkai", 3)
    TEST.test("think-pause",1)
    TEST.test("techchrc",0)    
    TEST.test("techlastplc",2)
    
    #créer l'instance de pensée
    ui.display("\nCréation et initialisation de la pensée: objet 'think'.")
    think = SudoThinking(mem, env=env)
##    think.init(mem)
    ui.display("\nOk prêt à commencer la résolution avec 'think' et 'mem'.\n")
    ui.sudoPause()
    
    #mode GUI
    ui.UImode(ui.GUI)
    ui.displayGridAll(grid)
    ui.display("HumaSudo - Test du module 'sudothinking'")

    TEST.levelAll(3)
    print("Tous les niveaux de test sont mis à 3.")
    TEST.level("thinkai", 3)

#stats de résolution
    nb_iter = 0
    nb_obs = 0
    nb_plc = 0
    nb_stats = [nb_iter, nb_obs, nb_plc]
    
def stats():
    print("Résultats du travail de résolution :")
    print("Nombre d'itérations de réflexion : " + str(nb_stats[0]))
    print("Nombre d'observations : " + str(nb_stats[1]))
    print("Nombre de placements : " + str(nb_stats[2]))

def stats_reset():
    nb_stats[0]=0
    nb_stats[1]=0
    nb_stats[2]=0
    
def reset(grid, think, view):
    gr.fillByRowLines(vals)
#    grid.copyFrom(gridInit)
    mem = SudoMemory(env=env)
    view = SudoGridView(grid, env=env)
    think = SudoThinking(mem, env=env)
    ui.display("Le test est réinitialisé")
    
def analyse():
    #print("\nDébut de résolution")
    (action, actionDetails) = think.analyse()
    nb_stats[0] += 1
    if action == "continue":
        TEST.display("analyse", 1, "La résolution continue.")
    elif action == "observe":
        nb_stats[1] +=1   #stats
        pattern = actionDetails
        TEST.display("analyse", 1, "Observation demandée: {0}".format(pattern))
        found = view.lookup(pattern)
        TEST.display("analyse", 1, "Résultat : {0}".format(found))
        mem.memorizeObs(found)
    elif action == "place":
        nb_stats[2] += 1   #stats
        placement = actionDetails
        (row, col, chiffre) = placement
        TEST.display("analyse", 1, "Placement demandé : {0}".format(placement))
        r = view.place(placement)
        ui.displayGridValue(row, col, chiffre)
        
    elif action == "end":
        TEST.display("analyse", 1, "Fin de la partie")
        TEST.display("analyse", 1, "La partie se termine avec le résultat : "+\
                     "{0}".format(actionDetails))
                     
##        (title, texte) = actionDetails
##        TEST.display("analyse", 0, title)
##        TEST.display("analyse", 0, texte)
    return (action, actionDetails)


def game():
    it = 0
    while True:
        r = analyse()
        it += 1
        if r[0] not in ("continue", "observe", "place"):
            print("Fin de résolution après {0} itérations de pensée."\
                  .format(it))
            break

def place():
    it = 0
    while True:
        r = analyse()
        it += 1
        if r[0] in ("continue", "observe"):
            continue
        if r[0] == "place":
            print("Placement de {0} en {1}"\
                  .format(r[1][2], (r[1][0], r[1][1])))
        else:
            #tous les autres cas "end", "fail" etc.
            print("Fin de résolution après {0} itérations de pensée."\
                  .format(it))
        break
        
def loopStep(tech):
    '''Cette fonction exécute une seule itération de boucle ROMA '''

    
    TEST.display("loop", 1, "\nDébut de boucle")
    r = tech.apply(mem)
    action = r[0]
    TEST.display("loop", 2,
                 "Résultat de tech.solve() : {0}".format(r))
    status = tech.status(mem)
    TEST.display("loop", 2,
                 "statut d'avancement de tech: {0}".format(status))
    if action == "observe":
        pattern = r[1]
        found = view.lookup(pattern)
        TEST.display("loop", 1,
                     "Résultat de view.lookup() : {0}".format(found))
        mem.memorizeObs(found)
        tech.obsFound(found)
    elif action == "place":
        placement = r[1]
        r = view.place(placement)
##        (row, col, chiffre) = placement
##        r = grid.placeRC(row, col, chiffre, True)
        TEST.display("loop", 1,
                     "Résultat de grid.place() : {0}".format(r))
    elif action == "continue":
        pass
    else:
        TEST.display("loop", 2,
                     "action retournée par solve() : {0}".format(action))
    return status
        
                
def loopTech(tech, pause=False):
    '''Cette fonction applique répétitivement la technique 'LastPlc' sur la
    grille 'grid' jusqu'à un certain état d'avancement. Par exemple faire tous
    les carrés, ou tous les carrés et rangs, etc.
    '''
    TEST.display("loop", 1,
                 "Boucle de résolution de TechLastPlc sur tous les carrés")
    tech.reset(mem)
    grid = gr
    iter = 0
    while True:

        if grid.isCompleted():
            print("\nGrille terminée.")
            return

        status = loopStep(tech)

        #contrôler fin du while
        iter +=1
        if iter > 100:
            TEST.display("loop", 0,
                         "Plus de 100 itérations de boucle !!! Stop.")
            break
#        if status[0] not in ("sqr", "row", "col"):
        if status[0] not in ("sqr", "row"):
            TEST.display("loop", 1,
                         "Boucle : les carrés, rangs et colonnes sont terminés.")
            break
        if pause:
            r = ui.sudoPause(True)
            if r:
                ui.display("")
            else:   #Ctrl-C ou Ctrl-D
                ui.display("Interruption clavier")
                break
        continue

#    tech.abort(mem)
    return

                    
