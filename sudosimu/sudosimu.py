# -*- coding: cp1252 -*-

'''Module sudosimu (sudosimu.sudosimu.py)
Script de la classe SudoSimu, qui encapsule la totalité de la simulation de
résolution de Sudoku. C'est ici qu'est la boucle de simulation ROMA : Réfléchir,
Observer, Mémoriser, Apprendre.

La classe SudoSimu est instanciée avec les capacités cognitives du joueur,
SudoMemory et SudoThinking, ainsi qu'avec la vue sur la grille SudoGridView.
En revanche elle n'a aucun accès direct à la grille.
Comme le reste du programme, SudoSimu utilise l'environnement SudoEnv et
interagit avec l'interface utilisateur via SudoUI.
'''

'''
Dernière mise à jour : 14/11/2018
Historique des modifications :
14/11/2018 - Version initiale
    Reprise du code de sudogame.py et adaptation de l'ancienne classe SudoGame
    renommée en SudoSimu. Adaptation du code de test et des displays.
'''

if __name__ in ("__main__", "sudosimu"):
    import sudobaseclass as base
    import sudoenv
    import sudoui as ui
    import sudorules as rules
    from sudorules import Sudoku_Error
    from sudogridview import SudoGridView
    from sudomemory import SudoMemory
    from sudothinking import SudoThinking
elif __name__ == "sudosimu.sudosimu":
    from sudosimu import sudobaseclass as base
    from sudosimu import sudoenv
    from sudosimu import sudoui as ui
    from sudosimu import sudorules as rules
    from sudosimu.sudorules import Sudoku_Error
    from sudosimu.sudogridview import SudoGridView
    from sudosimu.sudomemory import SudoMemory
    from sudosimu.sudothinking import SudoThinking
else:
    raise Exception("Impossible de faire les imports dans le module sudosimu.")

#constantes utilisées pour les pauses de boucle de résolution
STEP = "step"       #pause à chaque itération
OBS = "obs"         #pause à chaque observation et chaque placement
OBSERVE = OBS       #synonyme
PLACE = "place"     #pause uniquement à chaque placement
FAIL = "fail"       #pause à chaque difficulté ou erreur de jeu
END = "end"         #explicitement jusqu'à la fin (équivalent à 'None')
                    #END s'impose contre les autres paramètres.
EXCEPT = "except"   #pause à chaque déclenchement d'un exception. C'est plutôt
                    #destiné au débuggage, ça n'a pas de sens pour un joueur.
NOEXCEPT = "noexcept" #pour annuler explicitement la pause sur exception.
PAUSEPARLIST = (STEP, OBS, PLACE, FAIL, END, EXCEPT, NOEXCEPT)

#constance utilisée pour contrôler la boucle
STOP = "stop"
LOOP = "loop"

#gestion initiale des exceptions dans toute la partie
#Mode debug : déclencher et propager les exceptions
EXCEPT_MODE = EXCEPT
#Mode release : gérer les exceptions
#EXCEPT_MODE = NOEXCEPT

class SudoSimu(base.SudoBaseClass):
    ''' Encapsule la simulation de résolution avec la cognition du joueur et
    la vue sur la grille (mais pas la grille elle-même). Contient la boucle
    de résolution itérative.
    '''
#class SudoGame(base.SudoBaseClass):
#    '''Exécute la résolution d'une grille par un joueur'''

    def __init__(self, mem, think, view, env=None, \
                                         testlevel=sudoenv.TEST_SIMULEVEL):
        '''Initialisation de la nouvelle instance de jeu. Les paramètres sont
        les capacités que le joueur attribue à ce jeu (mem, think) et la vue
        de la grille (view).
        '''
        #init de la classe racine
        assert isinstance(env, sudoenv.SudoEnv) or env is None
        assert isinstance(testlevel, int) and testlevel>=0 \
                or testlevel is None
        #reprendre un précédente niveau de test s'il existe déjà
        oldlev = env.testLevel("simu")
        if oldlev is not None and testlevel != oldlev:
            testlevel = oldlev
        base.SudoBaseClass.__init__(self, env=env, \
                                    testlabel="simu", testlevel=testlevel)
        #ok init de cette classe
        TEST = self.env.TEST
        TEST.display("simu", 3, "SudoSimu - Dans __init__()")
        assert isinstance(mem, SudoMemory)
        assert isinstance(think, SudoThinking)
        assert isinstance(view, SudoGridView)
        self._mem = mem
        self._think = think
        self._view = view
        #initialiser le contrôle de la partie
        self._modeExcept = EXCEPT_MODE #voir les globales au début
        self._initSimu()
        return

    def _initSimu(self):
        '''Prépare les données de contrôle d'exécution.'''
        self._pauseParams = None
        self._solveResult = None
        self._lastAction = None
        self._lastActionDetails = None
        self._solving = False
        self._finished = False
        self._initOk = True # A SUPPRIMER du code, inutile maintenant
        return

    def solve(self, pauseParams=None, pauseMem=True):
        '''Joue la partie et résout la grille. Peut être appelée répétitivement
        jusqu'à la fin de la partie. Le paramètre 'pauseParams' permet de 
        spécifier des règles d'interruption (pause) périodique de la partie
        (chaque itération, observation, placement, etc.) et à chaque appel de
        solve() la consigne de pause peut être modifiée. solve() sans arguments
        commence ou continue la résolution avec les paramètres de pause
        précédents. Le paramètre 'pauseMem' indique si le paramètre de pause
        indiqué doit être mémorisé (Oui par défaut).
        Retourne "pause", "end" ou "fail" suivant le cas. Retourne avec "end"
        le résultat de la partie ("win", "quit", etc.). Retourne avec "pause"
        le résultat de la dernière itération jouée ("observe", "place", etc.)
        Retourne avec "fail" les éventuelles exceptions gérées. Retourne
        None si la partie est déjà terminée.
        '''
        TEST = self.env.TEST
        TEST.display("simu", 3, "SudoSimu - dans solve()")
        assert self._initOk
        self._lastAction = None
        self._lastActionDetails = None

        #partie déjà terminée ?
        if self._finished is True:
            TEST.display("simu", 3, "SudoSimu - appel de solve() alors que la "\
                                         "partie est déjà terminée.")
            TEST.display("simu", 1, "La partie est déjà terminée.")
            return None
        #début de partie
        if self._solving is False:
            #ok pour commencer la résolution
            TEST.display("simu", 3, "SudoSimu - Début de résolution.")
            TEST.display("simu", 1, "Début de la partie de Sudoku.")
            self._solving = True
####Des actions particulières de début de partie ?
####Mettre des compteurs, etc.
######################################
            
        #mémorise le paramètre de pause indiqué si c'est demandé
        if pauseParams is not None and pauseMem is True:
            self._pauseParams = pauseParams
        #résolution avec le paramètre indiqué ou celui déjà mémorisé
        if pauseParams is None:
            pause = self._pauseParams
        else:
            pause = pauseParams
        TEST.display("simu", 3, "Avancement de résolution avec le "\
                         "paramètre de pause : {0}".format(pause))
        #résolution
        solveResult = self._solveLoop(pause)
        TEST.display("simu", 3, "Simu - Retour à solve(). \nRésultat retourné "\
                                 ": {0}".format(solveResult))

        #Si la partie s'est mise en pause, indique la cause de cette pause.
        if solveResult[0] == "pause":
            TEST.display("simu", 1, "Pause de jeu. Détails : {0}"\
                                     .format(solveResult[1]))

        #Si la partie est terminée, indiquer le résultat de la partie et
        #mettre à jour les indicateurs d'avancement
        elif solveResult[0] == "end":
            self._solving = False
            self._finished = True
            TEST.display("simu", 1, "Partie terminé. Détails : {0}"\
                                     .format(solveResult[1]))

        #Si la partie rencontre une erreur non fatale :
        elif solveResult[0] == "fail":
            TEST.display("simu", 1, "La partie rencontre une erreur. "\
                                     "Détail : {0}".format(solveResult[1]))
        #tout autre résultas -> Fin de partie forcée
        else:
            self._solving = False
            self._finished = True
            TEST.display("simu", 1, "ATTENTION : résultat de jeu anormal : {0}"\
                                 .format(solveResult))
            TEST.display("simu", 1, "La partie est abandonnée.")
            return ("end", ("Erreur fatale", solveResult))
        #ok retour normal
        return solveResult

    def setPauseParams(self, pauseParams):
        '''Définit les options de pause. L'argument doit être explicite, donc
        pour annuler toutes les pauses il faut appeler setPauseParams(None).
        '''
        TEST = self.env.TEST
        self._pauseParams = pauseParams
        return
    
    def solveOnce(self, pauseParams=None):
        '''Avance la résolution jusqu'à la fin ou jusqu'à la pause paramétrée.
        La résolution doit être déjà en cours. Ne mémorise pas le paramètre
        'pauseParams' pour les appels suivants. Voir aussi la méthode solve().
        '''
        TEST = self.env.TEST
        TEST.display("simu", 3, "Simu - dans playOnce()")
        if not self._checkPlaying():
            return None
        else:
            return self.solve(pauseParams, False)

    def next(self, pauseParams=None):
        '''Continue la partie jusqu'à la prochaine pause indiquée en argument
        et mémorise l'argument de pause pour la suite.
        Equivalent à solve une fois que la partie est commencée.
        '''
        TEST = self.env.TEST
        TEST.display("simu", 3, "Simu - dans again()")
        assert self._initOk
        if not self._checkPlaying():
            return None
        else:
            return self.solve(pauseParams, True)
        
    def again(self):
        '''Continue la partie jusqu'à une prochaine pause selon le même
        paramètre que la fois précédente. La partie doit déjà être en cours.
        '''
        TEST = self.env.TEST
        TEST.display("simu", 3, "Simu - dans again()")
        assert self._initOk
        if not self._checkPlaying():
            return None
        else:
            return self.solve()
        
    def resume(self):
        '''Poursuit la partie jusqu'à sa fin. Equivalent à solve(END). La
        résolution doit être déjà en cours. 
        '''
        TEST = self.env.TEST
        TEST.display("simu", 3, "Simu - dans resume()")
        assert self._initOk
        if not self._checkPlaying():
            return None
        else:
            return self.solveToEnd()
        
    def solveToEnd(self):
        '''Fait la résolution complète sans pause. La résolution doit être déjà
        en cours. '''
        TEST = self.env.TEST
        TEST.display("simu", 3, "Simu - dans solveToEnd()")
        if not self._checkPlaying():
            return None
        else:
            return self.solve(END)

    def step(self):
        '''Fait une seule itération, quel que soit le paramètre de pause
        précédemment utilisé. La résolution doit être déjà en cours. 
        '''
        TEST = self.env.TEST
        TEST.display("simu", 3, "Simu - dans step()")
        assert self._initOk
        if not self._checkPlaying():
            return None
        else:
            return self.solve(STEP, False)

    def observe(self):        
        '''Commence ou continue la partie jusqu'à la prochaine observation.
        La résolution doit être déjà en cours.
        '''
        TEST = self.env.TEST
        TEST.display("simu", 3, "Simu - dans observe()")
        assert self._initOk
        if not self._checkPlaying():
            return None
        else:
            return self.solve(OBSERVE, False)

    def place(self):
        '''Commence ou continue la partie jusqu'au prochaine placement.
        La résolution doit être déjà en cours.
        '''
        TEST = self.env.TEST
        TEST.display("simu", 3, "Simu - dans place()")
        assert self._initOk
        if not self._checkPlaying():
            return None
        else:
            return self.solve(PLACE, False)

    def abort(self):
        '''Interrompt une partie en cours.'''
        TEST = self.env.TEST
        TEST.display("simu", 3, "Simu - dans abort()")
        assert self._initOk
        if not self._checkPlaying():
            return None
        else:
            r = self._abort()
        return r

    def _checkPlaying(self):
        '''Fait une vérification de partie en cours avant d'appeler solve().
        Utilisé par les méthodes de continuation de résolution.
        Retourne le résultat du jeu ou False si la partie n'est pas en cours
        '''
        TEST = self.env.TEST
        TEST.display("simu", 3, "Simu - dans _checkPlaying()")
        if self._finished is True:
            TEST.display("simu", 3, "Simu - Erreur, commande de suite de "\
                         "résolution alors que la partie déjà terminée.")
            ui.displayError("Erreur", "La partie est déjà terminée.")
            r = False
        elif self._solving is False:
            TEST.display("simu", 3, "Simu - Erreur, commande de suite de "\
                         "résolution alors que la partie n'est pas commencée.")
            ui.displayError("Erreur", "La partie n'est pas encore commencée.")
            r = False
        else:
            r = True
        return r
        
    def _solveLoop(self, pauseParams):
        '''Exécute la boucle itérative d'analyse et action de jeu. La boucle
        s'interrompt selon les paramètres reçus du joueur.
        Retourne "pause", "end" ou "fail" suivant le paramétrage de pause.
        Retourne avec "pause" le résultat de la dernière itération jouée.
        En cas d'erreur ou d'exception gérée, retourne un message spécifique.
        '''
        TEST = self.env.TEST
        TEST.display("simu", 3, "Simu - dans _solveLoop()")

        #mode de gestion des exceptions : il reste inchangé à moins qu'il y
        #ait un argument explicite.
        if pauseParams is not None:
            if EXCEPT in pauseParams:
                self._modeExcept = EXCEPT
            elif NOEXCEPT in pauseParams:
                self._modeExcept = NOEXCEPT

        #Boucle ROMA - Réfléchir/Observer/Mémoriser/Apprendre
        while True:
            try:
                TEST.display("simu", 2, "SudoSimu - lance une itération de jeu.")

                #itération de jeu avec indication de gestion des exceptions
                #(cet argument est transmis dans tout le code sous-jacent)
                #est enregistré dans un attribut de l'objet
                solveResult = self._iterate(self._pauseExcept)
                TEST.display("simu", 3, "SudoSimu - retour à _solveLoop \n"\
                             "L'itération de réflexion a retourné : {0}"\
                             .format(solveResult))

                #sortir de la boucle dans tous les cas de pause de jeu
                #indiqués par 'player' en paramètre.
                action = solveResult[0]
                if pauseParams is None:
                    #ne s'arrête qu'à la fin du jeu
                    if action == "end":
                        r = self._endSimu(solveResult)
                        break
                    else:
                        continue
                if action == "continue" and STEP in pauseParams:
                    r = ("pause", self._pauseContinue(solveResult))
                    break
                elif action == "observe" and OBS in pauseParams:
                    r = ("pause", self._pauseObserve(solveResult))
                    break
                elif action == "place" and (OBS in pauseParams
                                                or PLACE in pauseParams):
                    r = ("pause", self._pausePlace(solveResult))
                    break
                elif action == "fail" and FAIL in pauseParams:
                    r = ("pause", self._pauseFail(solveResult))
                    break
                elif action == "end":
                    r = self._endSimu(solveResult)
                    break
                #si le résultat n'est pas un résultat normal de jeu :
                elif action not in ("continue", "observe", "place",\
                                    "end", "fail"):
                    #pourrait être géré avec une exception...
                    TEST.display("simu", 1, "ATTENTION : résultat de jeu anormal : {0}"\
                                         .format(solveResult))
                    TEST.display("simu", 1, "La partie est abandonnée.")
                    return ("end", ("Erreur fatale", solveResult))
                    
                #tous les cas autres que "continue" où il y a STEP
                elif STEP in pauseParams:
                    r = ("pause", solveResult)
                    break
                #s'il n'y a aucune de ces combinaisons, la boucle continue.
                continue
            except:
                #Gère l'exception suivant le paramètrage
                exceptMsg = "Exception dans SudoSimu._solveLoop()"
                if self._pauseExcept is True:
                    ui.displayError("Exception", exceptMsg)
                    r = ("fail", ("except", exceptMsg))
                    break
                else:
                    raise Sudoku_Error(exceptMsg)
        #end loop
        TEST.display("simu", 3, "_solveLoop - Fin de la boucle d'itérations.")
        return r

    def _iterate(self, pauseExcept):
        '''Joue une itération de boucle ROMA (Réfléchir-Observer/Placer
        -Mémoriser-Apprendre). Retourne le résultat du coup.
        '''
        TEST = self.env.TEST
        TEST.display("simu", 3, "SudoSimu - dans _iterate()")
        assert self._initOk
        assert self._solving

        try:
            thinkResult = self._think.analyse()
            #différents résultats possibles de la réflexion
            TEST.display("simu", 3, "SudoSimu - Retour à Simu - Action : {0}"\
                                     .format(thinkResult))
            TEST.display("simu", 2, "Résultat de l'itération d'analyse "\
                         ": {0}".format(thinkResult))
            action = thinkResult[0]
            if action == "continue":
                TEST.display("simu", 2, "Réflexion : la résolution continue.")
            elif action == "observe":
##                nb_stats[1] +=1   #stats
                pattern = thinkResult[1]
                TEST.display("simu", 2, "Observation demandée: {0}"\
                                        .format(pattern))
                found = self._view.lookup(pattern)
                TEST.display("simu", 1, "Résultat de l'observation : {0}"\
                                         .format(found))
                self._mem.memorizeObs(found)
            elif action == "place":
##                nb_stats[2] += 1   #stats
                placement = thinkResult[1]
                TEST.display("simu", 1, "Placement demandé : {0}"\
                                        .format(placement))
                valid = self._view.place(placement)
####
#### A FAIRE ICI : transmission du résultat de validité du placement.
#### En utilisant une fonction mem.memorizePlace (à écrire)
####                
                (row, col, chiffre) = placement
                ui.displayGridValue(row, col, chiffre)
            elif action == "end":
                endDetails = thinkResult[1]
                TEST.display("simu", 1, "Fin de la partie")
                TEST.display("simu", 1, "La partie se termine avec le résultat "\
                                        ": {0}".format(endDetails))
            elif action =="fail":
                failDetails = thinkResult[1]
                msg = "Le jeu rencontre une difficulté : retour d'erreur (fail)"\
                      " dans le module \'Thinking\', méthode analyse().\n"\
                      "Détail : {0}".format(failDetails)
                
                TEST.display("simu", 1, msg)
            else:
                #ne devrait jamais arriver
                TEST.display("simu", 3, "Simu - valeur erronée retournée par "\
                             "think.analyse() dans _iterate().")
                ui.displayError("Erreur", "Module SudoSimu dans _iterate(): "\
                                "valeur invalide retournée par think.analyse()")
                raise Sudoku_Error()
        except:
            #Gère les exceptions suivant le paramètrage
            exceptMsg = "Exception dans SudoSimu._iterate()"
            if self._pauseExcept is True:
                ui.displayError("Exception", exceptMsg)
                thinkResult = ("except", exceptMsg)
            else:
                raise Sudoku_Error(exceptMsg)
        
        #garder les résultats de l'itération de réflexion
        self._lastAction = thinkResult[0]
        self._lastActionDetails = thinkResult[1]
        return thinkResult

    def _pauseContinue(self, solveResult):
        TEST = self.env.TEST
        TEST.display("simu", 1, "Le jeu fait une pause après une itération "\
                     "de réflexion.")
        #à traiter plus complètement si besoin
        return solveResult
    
    def _pauseObserve(self, solveResult):
        '''Affiche un message spécifique si la boucle de jeu s'est arrêtée
        sur une observation de la grille.
        '''
        TEST = self.env.TEST
        TEST.display("simu", 1, "Le jeu fait une pause après une observation.")
        #à traiter plus complètement si besoin
        return solveResult
                    
    def _pausePlace(self, solveResult):
        '''Affiche un message spécifique si la boucle de jeu s'est arrêtée
        sur un placement dans la grille.
        '''
        TEST = self.env.TEST
        TEST.display("simu", 1, "Le jeu fait une pause après un placement.")
        #à traiter plus complètement si besoin
        return solveResult
                    
    def _pauseFail(self, solveResult):
        '''Affiche un message spécifique si la boucle de jeu s'est arrêtée
        sur un retour d'action "fail".
        '''
        TEST = self.env.TEST
        TEST.display("simu", 1, 'Le jeu fait une pause après erreur ("fail")')
        #à traiter plus complètement si besoin
        return solveResult

    def _pauseExcept(self, solveResult):
        '''Affiche un message spécifique si la boucle de jeu s'est arrêtée
        sur une exception gérée.
        '''
        TEST = self.env.TEST
        TEST.display("simu", 1, "Le jeu fait une pause après exception gérée.")
        #à traiter plus complètement si besoin
        return

    def _endSimu(self, simuResult):
        ''' L'action retournée indique la fin de la partie ("end").
        Traitement du résultat de la partie et affichage d'informations
        spécifiques pour le joueur.
        '''
        TEST = self.env.TEST
        TEST.display("simu", 1, "Fin de la partie. Détails des résultats "\
                     " : {0}".format(simuResult))
        return simuResult        

##    def reset(self):
##        '''Réinitialise l'instance de jeu avec la grille initiale.'''
##        self._grid.copyFrom(self._initGrid)
##        self._initSimu()
##        return

                    
    @property
    def lastAction(self):
        return(self._lastAction, self._lastActionDetails)

##    @property
##    def solveResult(self):
##        return self._solveResult
    

    def showGrid(self, style=None):
        '''Montre la grille dans son état actuel, avec le style d'affichage
        indiqué.
        '''
#        self._grid.show(style)
        return
    
    @property
    def thinkAction(self):
        assert self._initOk
        return self._lastAction

    @property
    def thinkDetails(self):
        assert self._initOk
        return self._lastActionDetails

    @property
    def pauseParams(self):
        assert self._initOk
        return self._pauseParams

    @property
    def finished(self):
        assert self._initOk
        return self._finished

    @property
    def solving(self):
        assert self._initOk
        return self._solving



#TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST
#TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST

if __name__ == "__main__":

#    import sudotestall     #OBSOLETE#

    from sudogrid import SudoGrid
    from test_main import *

    #interface
    env = sudoenv.SudoEnv()
    TEST = env.test
    ui = env.ui
    testlev(0)
    testMakeUI()
    #données de jeu
    grid = None
    gridInit = None
    mem = None
    think = None
    view = None
    simu = None
    params = None
    #fonctions de jeu
    def newGrid():
        global gridInit
        gridInit = testNewGrid()
        newSimu()
        return
    def resetGrid():
        global grid
        global gridInit
        grid = gridInit.copy()
        testShowGrid(grid)
        return
    def newSimu():
        global grid
        global mem
        global think
        global view
        global simu
        resetGrid()
        mem = SudoMemory(env=env)
        think = SudoThinking(mem, env=env)
        view = SudoGridView(grid, env=env)
        simu= SudoSimu(mem, think, view, env)
        return
    def go():
        global simu
        simu.solve(params)
        return

    #Initialisation des tests et de la partie
    TEST.level("main", 1)
    TEST.display("main", 1, "\nTest du module sudosimu")
    TEST.display("main", 1, "----------------------------\n")
    newGrid()
    ui.display("Création  et initialisation de la partie")
    newSimu()
    #Niveaux de commentaires pour la partie
    TEST.level("thinkai", 1)

    #Paramètres de la partie
    params = None
    #jeu
    TEST.display("main", 1, "Prêt à jouer.")
    print("\n...>>> simu.solve(params) \nou >>> go()")

    #ui.sudoPause()
    #go()
    

