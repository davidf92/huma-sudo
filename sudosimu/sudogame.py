'''Module sudogame (sudosimu.sudogame.py)
Cette classe encapsule la gestion d'une partie = la résolution d'une grille.
C'est ici qu'est la boucle de simulation ROMA : Réfléchir, Observer, Mémoriser,
Apprendre.
La classe SudoGame est instanciée par un joueur (SudoPlayer) qui résout une
grille (SudoGrid). Le joueur commence  la résolution en y associant sa mémoire
(SudoMemory) et sa réflexion (SudoThinking).
Un objet SudoGame crée une instance d'observateur (SudoObserver) qui est le
moyen d'observation de la grille par le joueur (les classes mémoire et pensée
n'y ont pas accès directement).
'''

'''
Historique des modifications :
15/11/2017 - Evolution pour utiliser le système d'environnement avec SudoEnv
    ainsi que tout le support de TEST dans sudoenv.
08/11/2017 - Réécriture du fonctionnement des paramètres de pause.
    Suppression de tout l'ancien code permettant de réinitialiser la partie,
    car c'est une fonctionalité qui n'a plus de sens.

Dernière mise à jour : 15/11/2017:
'''

if __name__ in ("__main__", "sudogame"):
    import sudobaseclass as base
    import sudoenv
    import sudoui as ui
    import sudorules as rules
    from sudorules import Sudoku_Error
    from sudogridview import SudoGridView
    from sudomemory import SudoMemory
    from sudothinking import SudoThinking
elif __name__ == "sudosimu.sudogame":
    from sudosimu import sudobaseclass as base
    from sudosimu import sudoenv
    from sudosimu import sudoui as ui
    from sudosimu import sudorules as rules
    from sudosimu.sudorules import Sudoku_Error
    from sudosimu.sudogridview import SudoGridView
    from sudosimu.sudomemory import SudoMemory
    from sudosimu.sudothinking import SudoThinking
else:
    raise Exception("Impossible de faire les imports dans le module sudogame.")

#OBSOLETE
#from sudosimu.sudoobserver import SudoObserver

#constantes qui définissent les conditions de pause du jeu
#que le joueur peut souhaiter. En l'absence de ces indication le jeu
#se poursuit d'un coup jusqu'à la victoire ou l'abandon.
#les indications sont cumulatives addition. Ex : OBS + FAIL
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

class SudoGame(base.SudoBaseClass):
    '''Exécute la résolution d'une grille par un joueur'''

    def __init__(self, mem, think, view, env=None, \
                                         testlevel=sudoenv.TEST_GAMELEVEL):
        '''Initialisation de la nouvelle instance de jeu. Les paramètres sont
        les capacités que le joueur attribue à ce jeu (mem, think) et l'accès
        à la grille (view).
        '''
        #init de la classe racine
        assert isinstance(env, sudoenv.SudoEnv) or env is None
        assert isinstance(testlevel, int) and testlevel>=0 \
                or testlevel is None
        #reprendre un précédente niveau de test s'il existe déjà
        oldlev = env.testLevel("game")
        if oldlev is not None and testlevel != oldlev:
            testlevel = oldlev
        base.SudoBaseClass.__init__(self, env=env, \
                                    testlabel="game", testlevel=testlevel)
        #ok init de cette classe
        TEST = self.env.TEST
        TEST.display("game", 3, "SudoGame - Dans __init__()")
        assert isinstance(mem, SudoMemory)
        assert isinstance(think, SudoThinking)
        assert isinstance(view, SudoGridView)
        self._mem = mem
        self._think = think
        self._view = view
        #initialiser le contrôle de la partie
        self._modeExcept = EXCEPT_MODE #voir les globales au début
        self._initGame()
        return

    def _initGame(self):
        '''Prépare les données de contrôle d'exécution.'''
        self._pauseParams = None
        self._solveResult = None
        self._lastAction = None
        self._lastActionDetails = None
        self._playing = False
        self._finished = False
        self._initOk = True # A SUPPRIMER du code, inutile maintenant
        return

    def play(self, pauseParams=None, pauseMem=True):
        '''Joue la partie et résout la grille. Peut être appelée répétitivement
        jusqu'à la fin de la partie. Le paramètre 'pauseParams' permet de 
        spécifier des règles d'interruption (pause) périodique de la partie
        (chaque itération, observation, placement, etc.) et à chaque appel de
        play() la consigne de pause peut être modifiée. play() sans arguments
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
        TEST.display("game", 3, "SudoGame - dans play()")
        assert self._initOk
        self._lastAction = None
        self._lastActionDetails = None

        #partie déjà terminée ?
        if self._finished is True:
            TEST.display("game", 3, "Game - appel de play() alors que la "\
                                         "partie est déjà terminée.")
            TEST.display("game", 1, "La partie est déjà terminée.")
            return None
        #début de partie
        if self._playing is False:
            #ok pour commencer la résolution
            TEST.display("game", 3, "Game - Début de résolution.")
            TEST.display("game", 1, "Début de la partie de Sudoku.")
            self._playing = True
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
        TEST.display("game", 3, "Avancement de résolution avec le "\
                         "paramètre de pause : {0}".format(pause))
        #résolution
        playResult = self._playLoop(pause)
        TEST.display("game", 3, "Game - Retour à play(). \nRésultat retourné "\
                                 ": {0}".format(playResult))

        #Si la partie s'est mise en pause, indique la cause de cette pause.
        if playResult[0] == "pause":
            TEST.display("game", 1, "Pause de jeu. Détails : {0}"\
                                     .format(playResult[1]))

        #Si la partie est terminée, indiquer le résultat de la partie et
        #mettre à jour les indicateurs d'avancement
        elif playResult[0] == "end":
            self._playing = False
            self._finished = True
            TEST.display("game", 1, "Partie terminé. Détails : {0}"\
                                     .format(playResult[1]))

        #Si la partie rencontre une erreur non fatale :
        elif playResult[0] == "fail":
            TEST.display("game", 1, "La partie rencontre une erreur. "\
                                     "Détail : {0}".format(playResult[1]))
        #tout autre résultas -> Fin de partie forcée
        else:
            self._playing = False
            self._finished = True
            TEST.display("game", 1, "ATTENTION : résultat de jeu anormal : {0}"\
                                 .format(playResult))
            TEST.display("game", 1, "La partie est abandonnée.")
            return ("end", ("Erreur fatale", playResult))
        #ok retour normal
        return playResult

    def setPauseParams(self, pauseParams):
        '''Définit les options de pause. L'argument doit être explicite, donc
        pour annuler toutes les pauses il faut appeler setPauseParams(None).
        '''
        TEST = self.env.TEST
        self._pauseParams = pauseParams
        return
    
    def playOnce(self, pauseParams=None):
        '''Avance la résolution jusqu'à la fin ou jusqu'à la pause paramétrée.
        La résolution doit être déjà en cours. Ne mémorise pas le paramètre
        'pauseParams' pour les appels suivants. Voir aussi la méthode play().
        '''
        TEST = self.env.TEST
        TEST.display("game", 3, "Game - dans playOnce()")
        if not self._checkPlaying():
            return None
        else:
            return self.play(pauseParams, False)

    def playToEnd(self):
        '''Fait la résolution complète sans pause. La résolution doit être déjà
        en cours. '''
        TEST = self.env.TEST
        TEST.display("game", 3, "Game - dans playToEnd()")
        if not self._checkPlaying():
            return None
        else:
            return self.play(END)

    def again(self):
        '''Continue la partie jusqu'à une prochaine pause selon le même
        paramètre que la fois précédente. La partie doit déjà être en cours.
        '''
        TEST = self.env.TEST
        TEST.display("game", 3, "Game - dans again()")
        assert self._initOk
        if not self._checkPlaying():
            return None
        else:
            return self.play()
    
    def resume(self):
        '''Poursuit la partie jusqu'à sa fin. Equivalent à play(END). La
        résolution doit être déjà en cours. 
        '''
        TEST = self.env.TEST
        TEST.display("game", 3, "Game - dans resume()")
        assert self._initOk
        if not self._checkPlaying():
            return None
        else:
            return self.playToEnd()
        
    def step(self):
        '''Fait une seule itération, quel que soit le paramètre de pause
        précédemment utilisé. La résolution doit être déjà en cours. 
        '''
        TEST = self.env.TEST
        TEST.display("game", 3, "Game - dans step()")
        assert self._initOk
        if not self._checkPlaying():
            return None
        else:
            return self.play(STEP, False)

    def observe(self):        
        '''Commence ou continue la partie jusqu'à la prochaine observation.
        La résolution doit être déjà en cours.
        '''
        TEST = self.env.TEST
        TEST.display("game", 3, "Game - dans observe()")
        assert self._initOk
        if not self._checkPlaying():
            return None
        else:
            return self.play(OBSERVE, False)

    def place(self):
        '''Commence ou continue la partie jusqu'au prochaine placement.
        La résolution doit être déjà en cours.
        '''
        TEST = self.env.TEST
        TEST.display("game", 3, "Game - dans place()")
        assert self._initOk
        if not self._checkPlaying():
            return None
        else:
            return self.play(PLACE, False)

    def abort(self):
        '''Interrompt une partie en cours.'''
        TEST = self.env.TEST
        TEST.display("game", 3, "Game - dans abort()")
        assert self._initOk
        if not self._checkPlaying():
            return None
        else:
            r = self._abort()
        return r

    def _checkPlaying(self):
        '''Fait une vérification de partie en cours avant d'appeler play().
        Utilisé par les méthodes de continuation de résolution.
        Retourne le résultat du jeu ou False si la partie n'est pas en cours
        '''
        TEST = self.env.TEST
        TEST.display("game", 3, "Game - dans _checkPlaying()")
        if self._finished is True:
            TEST.display("game", 3, "Game - Erreur, commande de suite de "\
                         "résolution alors que la partie déjà terminée.")
            ui.displayError("Erreur", "La partie est déjà terminée.")
            r = False
        elif self._playing is False:
            TEST.display("game", 3, "Game - Erreur, commande de suite de "\
                         "résolution alors que la partie n'est pas commencée.")
            ui.displayError("Erreur", "La partie n'est pas encore commencée.")
            r = False
        else:
            r = True
        return r
        
    def _playLoop(self, pauseParams):
        '''Exécute la boucle itérative d'analyse et action de jeu. La boucle
        s'interrompt selon les paramètres reçus du joueur.
        Retourne "pause", "end" ou "fail" suivant le paramétrage de pause.
        Retourne avec "pause" le résultat de la dernière itération jouée.
        En cas d'erreur ou d'exception gérée, retourne un message spécifique.
        '''
        TEST = self.env.TEST
        TEST.display("game", 3, "Game - dans _playLoop()")

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
                TEST.display("game", 2, "SudoGame - lance une itération de jeu.")

                #itération de jeu avec indication de gestion des exceptions
                #(cet argument est transmis dans tout le code sous-jacent)
                #est enregistré dans un attribut de l'objet
                playResult = self._iterate(self._pauseExcept)
                TEST.display("game", 3, "SudoGame - retour à _playLoop \n"\
                             "L'itération de réflexion a retourné : {0}"\
                             .format(playResult))

                #sortir de la boucle dans tous les cas de pause de jeu
                #indiqués par 'player' en paramètre.
                action = playResult[0]
                if pauseParams is None:
                    #ne s'arrête qu'à la fin du jeu
                    if action == "end":
                        r = self._endGame(playResult)
                        break
                    else:
                        continue
                if action == "continue" and STEP in pauseParams:
                    r = ("pause", self._pauseContinue(playResult))
                    break
                elif action == "observe" and OBS in pauseParams:
                    r = ("pause", self._pauseObserve(playResult))
                    break
                elif action == "place" and (OBS in pauseParams
                                                or PLACE in pauseParams):
                    r = ("pause", self._pausePlace(playResult))
                    break
                elif action == "fail" and FAIL in pauseParams:
                    r = ("pause", self._pauseFail(playResult))
                    break
                elif action == "end":
                    r = self._endGame(playResult)
                    break
                #si le résultat n'est pas un résultat normal de jeu :
                elif action not in ("continue", "observe", "place",\
                                    "end", "fail"):
                    #pourrait être géré avec une exception...
                    TEST.display("game", 1, "ATTENTION : résultat de jeu anormal : {0}"\
                                         .format(playResult))
                    TEST.display("game", 1, "La partie est abandonnée.")
                    return ("end", ("Erreur fatale", playResult))
                    
                #tous les cas autres que "continue" où il y a STEP
                elif STEP in pauseParams:
                    r = ("pause", playResult)
                    break
                #s'il n'y a aucune de ces combinaisons, la boucle continue.
                continue
            except:
                #Gère l'exception suivant le paramètrage
                exceptMsg = "Exception dans SudoGame._playLoop()"
                if self._pauseExcept is True:
                    ui.DisplayError("Exception", exceptMsg)
                    r = ("fail", ("except", exceptMsg))
                    break
                else:
                    raise Sudoku_Error(exceptMsg)
        #end loop
        TEST.display("game", 3, "_playLoop - Fin de la boucle d'itérations.")
        return r

    def _iterate(self, pauseExcept):
        '''Joue une itération de boucle ROMA (Réfléchir-Observer/Placer
        -Mémoriser-Apprendre). Retourne le résultat du coup.
        '''
        TEST = self.env.TEST
        TEST.display("game", 3, "Sudogame - dans _iterate()")
        assert self._initOk
        assert self._playing

        try:
            thinkResult = self._think.analyse()
            #différents résultats possibles de la réflexion
            TEST.display("game", 3, "Sudogame - Retour à Game - Action : {0}"\
                                     .format(thinkResult))
            TEST.display("game", 2, "Résultat de l'itération d'analyse "\
                         ": {0}".format(thinkResult))
            action = thinkResult[0]
            if action == "continue":
                TEST.display("game", 2, "Réflexion : la résolution continue.")
            elif action == "observe":
##                nb_stats[1] +=1   #stats
                pattern = thinkResult[1]
                TEST.display("game", 2, "Observation demandée: {0}"\
                                        .format(pattern))
                found = self._view.lookup(pattern)
                TEST.display("game", 1, "Résultat de l'observation : {0}"\
                                         .format(found))
                self._mem.memorizeObs(found)
            elif action == "place":
##                nb_stats[2] += 1   #stats
                placement = thinkResult[1]
                TEST.display("game", 1, "Placement demandé : {0}"\
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
                TEST.display("game", 1, "Fin de la partie")
                TEST.display("game", 1, "La partie se termine avec le résultat "\
                                        ": {0}".format(endDetails))
            elif action =="fail":
                failDetails = thinkResult[1]
                msg = "Le jeu rencontre une difficulté : retour d'erreur (fail)"\
                      " dans le module \'Thinking\', méthode analyse().\n"\
                      "Détail : {0}".format(failDetails)
                
                TEST.display("game", 1, msg)
            else:
                #ne devrait jamais arriver
                TEST.display("game", 3, "Game - valeur erronée retournée par "\
                             "think.analyse() dans _iterate().")
                ui.displayError("Erreur", "Module sudogame dans _iterate(): "\
                                "valeur invalide retournée par think.analyse()")
                raise Sudoku_Error()
        except:
            #Gère les exceptions suivant le paramètrage
            exceptMsg = "Exception dans SudoGame._iterate()"
            if self._pauseExcept is True:
                ui.DisplayError("Exception", exceptMsg)
                thinkResult = ("except", exceptMsg)
            else:
                raise Sudoku_Error(exceptMsg)
        
        #garder les résultats de l'itération de réflexion
        self._lastAction = thinkResult[0]
        self._lastActionDetails = thinkResult[1]
        return thinkResult

    def _pauseContinue(self, playResult):
        TEST = self.env.TEST
        TEST.display("game", 1, "Le jeu fait une pause après une itération "\
                     "de réflexion.")
        #à traiter plus complètement si besoin
        return playResult
    
    def _pauseObserve(self, playResult):
        '''Affiche un message spécifique si la boucle de jeu s'est arrêtée
        sur une observation de la grille.
        '''
        TEST = self.env.TEST
        TEST.display("game", 1, "Le jeu fait une pause après une observation.")
        #à traiter plus complètement si besoin
        return playResult
                    
    def _pausePlace(self, playResult):
        '''Affiche un message spécifique si la boucle de jeu s'est arrêtée
        sur un placement dans la grille.
        '''
        TEST = self.env.TEST
        TEST.display("game", 1, "Le jeu fait une pause après un placement.")
        #à traiter plus complètement si besoin
        return playResult
                    
    def _pauseFail(self, playResult):
        '''Affiche un message spécifique si la boucle de jeu s'est arrêtée
        sur un retour d'action "fail".
        '''
        TEST = self.env.TEST
        TEST.display("game", 1, 'Le jeu fait une pause après erreur ("fail")')
        #à traiter plus complètement si besoin
        return playResult

    def _pauseExcept(self, playResult):
        '''Affiche un message spécifique si la boucle de jeu s'est arrêtée
        sur une exception gérée.
        '''
        TEST = self.env.TEST
        TEST.display("game", 1, "Le jeu fait une pause après exception gérée.")
        #à traiter plus complètement si besoin
        return

    def _endGame(self, gameResult):
        ''' L'action retournée indique la fin de la partie ("end").
        Traitement du résultat de la partie et affichage d'informations
        spécifiques pour le joueur.
        '''
        TEST = self.env.TEST
        TEST.display("game", 1, "Fin de la partie. Détails des résultats "\
                     " : {0}".format(gameResult))
        return gameResult        

##    def reset(self):
##        '''Réinitialise l'instance de jeu avec la grille initiale.'''
##        self._grid.copyFrom(self._initGrid)
##        self._initGame()
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
    def playing(self):
        assert self._initOk
        return self._playing

#TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST
#TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST



if __name__ == "__main__":

    import sudotestall
    from sudogrid import SudoGrid
    from test_main import *

    #interface
    testlev(0)
    testMakeUI()
    #données de jeu
    grid = None
    gridInit = None
    mem = None
    think = None
    view = None
    game = None
    params = None
    #fonctions de jeu
    def newGrid():
        global gridInit
        gridInit = testNewGrid()
        newGame()
        return
    def resetGrid():
        global grid
        global gridInit
        grid = gridInit.copy()
        testShowGrid(grid)
        return
    def newGame():
        global grid
        global mem
        global think
        global view
        global game
        resetGrid()
        mem = SudoMemory()
        think = SudoThinking(mem)
        view = SudoGridView(grid)
        #view = SudoGridView(grid, env=self._env)
        game = SudoGame(mem, think, view)
        return
    def go():
        global game
        game.play(params)
        return
    #Initialisation des tests et de la partie
    TEST.level("main", 1)
    TEST.display("main", 1, "\nTest du module sudogame")
    TEST.display("main", 1, "----------------------------\n")
    newGrid()
    ui.display("Création  et initialisation de la partie")
    newGame()
    #Niveaux de commentaires pour la partie
    TEST.level("thinkai", 1)

    #Paramètres de la partie
    params = None
    #jeu
    TEST.display("main", 1, "Prêt à jouer.")
    print("\n...>>> game.play(params) \nou >>> go()")

    #ui.sudoPause()
    #go()
    


##    #TEST     
##    import sudotestall
##    from sudogrid import SudoGrid, SudoBloc
##    testlevel = 3
##    TEST.levelAll(testlevel)
##    ui.display("Tous les niveaux de test sont à {0}".format(testlevel))
##
##    #mode GUI
##    ui.UImode(ui.GUI)
##    TEST.displayUImode(MODE_BOTH, 1)
##
##    TEST.display("main", 1, "\nCréation de la grille.")
##    grid = SudoGrid()
##    gridInit = SudoGrid()
##    newGrid()
##    ui.displayGridAll(grid)
##
##    TEST.display("main", 1, "\nCréation de la partie.")
##    mem = None
##    think = None
##    view = None
##    game = None
##    gameParam = (mem, think, view, game)
##    #newGame(grid)
##    (mem, think, view, game) = newGame(grid)
##    
##    TEST.display("main", 1, "Ok prêt à jouer")
##
##    TEST.levelAll(0)
##    TEST.level("thinkai", 1)
###    TEST.level("game", 1)
##    
