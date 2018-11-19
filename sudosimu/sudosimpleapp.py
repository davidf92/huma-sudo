'''Module 'sudoapp' : Trame d'application gérée avec une classe dédiée SudoApp.

L'application ainsi définie englobe la manipulation de la grille, du joueur et
des parties, gère toutes les options de résolution et l'avancement pas-à-pas
paramétré. Permet aussi de gérer les détails d'affichage d'avancement de la
résolution.
'''
'''
Historique des modifications :
15/11/2017 - Evolution pour utiliser le système d'environnement avec SudoEnv
    Ok validé.
24/10/2017 - Version initiale

Problèmes, bugs, modifications à faire :
15/11/2017 - Il y a des bugs probables dans les vérifications _checkxxxxx et dans
    les commandes de haut niveau et les méthodes qui utilisent ces vérifs.
'''

#Imports différents pour exécuter en package ou pour tester depuis ce module
if __name__ in ("__main__", "sudosimpleapp"):
    import sudobaseclass as base
    import sudoenv
    import sudoui as ui
    import sudorules as rules
    from sudorules import *
    from sudoapp import SudoApp
    from sudogrid import SudoGrid
    from sudoplayer import SudoPlayer
    from sudogame import SudoGame
    from sudomemprofile import SudoMemProfile
    from sudothinkprofile import SudoThinkProfile
    from sudomemory import SudoMemory
    from sudothinking import SudoThinking
    from sudogame import *
elif __name__ == "sudosimu.sudosimpleapp":
    from sudosimu import sudobaseclass as base
    from sudosimu import sudoenv
    from sudosimu import sudoui as ui
    from sudosimu import sudorules as rules
    from sudosimu.sudorules import *
    from sudosimu.sudoapp import SudoApp
    from sudosimu.sudogrid import SudoGrid
    from sudosimu.sudoplayer import SudoPlayer
    from sudosimu.sudogame import SudoGame
    from sudosimu.sudomemprofile import SudoMemProfile
    from sudosimu.sudothinkprofile import SudoThinkProfile
    from sudosimu.sudomemory import SudoMemory
    from sudosimu.sudothinking import SudoThinking
    from sudosimu.sudogame import *
else:
    raise Exception("Impossible de faire les imports dans le module sudosimpleapp.")

#### CONVENTIONS ####
#1)Nommage : Les propriétés et méthodes de classes commençant par un '_' doivent être
#considérées comme privées et ne doivent donc pas être accédées dans l'usage
#de ces classes (même si le langage Python ne rend pas cela impossible). Néanmoins
#leur accès direct est utile pour des expérimentations et des tests.
#2)Fonctions : sauf indication contraire les fonctions et méthodes retournent
#True si elles sont bien déroulé et None ou False dans le cas contraire. Si elles
#doivent retourner un objet, elles retournent None en cas d'erreur.
################################

#Constantes qui définissent les conditions de pause du jeu que le joueur peut
#souhaiter. En l'absence de ces indication le jeu se poursuit par défaut d'une
#traite jusqu'à la victoire ou l'échec.
#Les indications de pause sont cumulatives par addition. Ex : OBS + FAIL
STEP = "step"       #pause à chaque itération
OBS = "obs"         #pause à chaque observation et chaque placement
OBSERVE = OBS       #synonyme
PLACE = "place"     #pause uniquement à chaque placement
FAIL = "fail"       #pause à chaque difficulté ou erreur de jeu
END = "end"         #explicitement jusqu'à la fin (équivalent à 'None')
                    #END s'impose contre les autres paramètres.
EXCEPT = "except"   #pause à chaque déclenchement d'un exception. C'est plutôt
                    #destiné au débuggage, ça n'a pas de sens pour un joueur.
NOEXCEPT = "noxcept" #pour annuler explicitement la pause sur exception.


class SudoSimpleApp(base.SudoBaseClass, SudoApp):
    '''Classe qui représente une application simplifiée de simulation de Sudoku.
    Il peut y avoir un joueur et une grille à la fois dans une interface UI
    de jeu unique. Il n'y a qu'une partie en cours à la fois. Les méthodes
    permettent de contrôler la progression de la résolution et les affichages.
    SudoSimpleApp utilise l'environnement par défaut.
    Avec SudoSimpleApp il suffit de choisir une grille pour simuler une
    résolution dans une interface UI mixte graphique/console.
    '''

    def __init__(self, env=None, testlevel=sudoenv.TEST_SIMPLEAPPLEVEL):
        '''Initialise l'instance et crée un joueur par défaut. Utilise
        l'environnement par défaut SudoEnv() et ignore le paramètre (il est
        présent pour compatibilité du code appelant.
        '''
        #init de la classe racine
        assert isinstance(env, sudoenv.SudoEnv) or env is None
        assert isinstance(testlevel, int) and testlevel>=0 \
                or testlevel is None
        #reprendre un précédente niveau de test s'il existe déjà
        oldlev = env.testLevel("simpleapp")
        if oldlev is not None and testlevel != oldlev:
            testlevel = oldlev
        base.SudoBaseClass.__init__(self, env=env, \
                                    testlabel="simpleapp", testlevel=testlevel)
        #ok init de cette classe
        TEST = self.env.TEST
        TEST.display("simpleapp", 3, "SudoSimpleApp - dans __init__()")
        self._initInstance()
        self.newPlayer()
        return

    def _initInstance(self):
        '''Initialise les propriétés de l'instance. Dans cette version une
        instance d'application ne gère qu'une grille à la fois pour un seul
        joueur.
        '''
        TEST = self.env.TEST
        TEST.display("simpleapp", 3, "SudoSimpleApp - dans _initInstance()")
        self._player= None
        self._defaultPlayerName = "Pierre Dupont"
        #propriétés de grilles
        self._gridFileName = None
        self._gridAsLines = None    #image 'ligne' du contenu de la grille
        self._gameGrid = None       #la grille telle que créée (initiale)
        self._playingGrid = None    #grille modifiée en cours de résolution
        self._gridReady = False     #indique qu'une grille est chargée
        #propriétés d'interface utilisateur
        self._useSudoApp = True
        self._uiMode = None
        self._testMode = None
        self._testModeLevel = None
        #partie et contrôle de résolution
        self._game = None
        self._gameReady = False #indique si la partie est prête à être jouée
        self._playing = False   #indique si la résolution est en cours
        self._finished = False  #indique si la résolution est terminée
        self._pauseParams = None  #paramètres de pause en résol. par étapes
        return True

    def setEnv(self, env):
        '''Surchage la méthode de la classe racine. Ne fait rien car
        l'environnement de SudoSimpleApp reste celui de base.
        '''
        return

#### ATTENTION : Il faut paramétrer cette méthode
    def makeUI(self):
        '''Prépare l'interface utilisateur console et graphique.
        Par défaut, définit l'utilisation console et fenêtre à la fois.
        '''
        TEST = self.env.TEST
        TEST.display("simpleapp", 3, "SudoSimpleApp - dans makeUI()")
        self._uiMode = sudoenv.UI_BOTH
        self._testMode = sudoenv.TEST_BOTH
        self._testModeLevel = 1

        ui.UImode(self._uiMode)
        TEST.displayUImode(self._testMode, self._testModeLevel)
        TEST.display("simpleapp", 3, "SudoSimpleApp - Interface utilisateur prête.")
        return True
#################################################

    def close(self):
        '''Arrête l'application et ferme l'interface graphique s'il y en a une.
        '''
###############################################################################
# L'intérêt potentiel de cette méthode est de permettre la sauvegarde de données
# telles que des statistiques de résolution, des données de performance et
# d'apprentissage sur le plan AI, ou encore les connaissances développées
# par les joueurs.
###############################################################################
        TEST = self.env.TEST
        ui.closeGUI()
        return

    def newPlayer(self, name=None):
        '''Crée pour l'application un nouveau joueur avec le nom indiqué.
        Cela oblige à annuler toute résolution de grille en cours. S'il y a
        une grille chargée, elle est réinitialisée.
        Transfert l'objet d'environnement à la classe SudoPlayer.
        '''
        TEST = self.env.TEST
        TEST.display("simpleapp", 3, "SudoSimpleApp - dans newPlayer()")
        if name is None:
            name = self._defaultPlayerName
        #créer l'objet player et lui transmettre l'environnement
        self._player = SudoPlayer(name, env=self._env)
        if self._playing is True:
            ui.display("Nouveau joueur", "La partie en cours est annulée.")
            #self.abortGame()   #abandonner sans perdre les stats
        self.resetPlayingGrid()
        return self._player

    def newGrid(self, source=None):
        '''Crée une nouvelle grille depuis la source de chiffres indiquée.
        La source peut indiquer un fichier ou une grille aléatoire.
        Retourne l'instance de la nouvelle grille (pas une copie)
        '''
        TEST = self.env.TEST
        TEST.display("simpleapp", 3, "SudoSimpleApp - dans newGrid()")
#### Dans cette version : grille = uniquement source fichier de test.
#    Le paramètre source est ignoré
#    Ajouter aussi une gestion d'exceptions.

        #Lit une grille depuis un fichier et initialise les grilles de l'app.
        self.newGridFromFile()
        return self._gameGrid

    def newGridFromFile(self, fname=None):
        '''Initialise la grille de l'application à partir d'un fichier
        au format de grilles SudoSimu. Retourne cette grille.
        Si aucun nom de fichier n'est indiqué, en demande à l'utilisateur. Dans
        ce cas il ne peut s'agir que d'un fichier de test SudoSimu.
        Retourne l'instance de la nouvelle grille (pas un copie)
        '''
        TEST = self.env.TEST
        TEST.display("simpleapp", 3, "SudoSimpleApp - dans newGridFromFile()")
        
        #choix de fichier s'il n'est pas indiqué
        if fname is None:
            TEST.display("simpleapp", 1,"Choisir une grille depuis un fichier "\
                                  "de test :")
            fname = ui.sudoNumTestFich()
            TEST.display("simpleapp", 3, "nom de fichier : {0}\n".format(fname))
            if fname is None:    #impossible de lire un fichier de grille
                ui.displayError("Erreur fichier", "Impossible de lire le "\
                    "fichier indiqué, ou ce fichier n'est pas un fichier "\
                    "de grille SudoSimu valide.")
                TEST.display("simpleapp", 3, "newGridFromFile - Erreur : pas de nom "\
                                         "de fichier.")
                return None
            TEST.display("simpleapp", 1, "Fichier choisi : {0}\n".format(fname))

        #lecture du fichier et initialisation des grilles
        vals = ui.sudoFichReadLines(fname)
        if vals is None:
            ui.displayError("Erreur fichier", "Impossible de lire le "\
                "fichier indiqué, ou ce fichier n'est pas un fichier "\
                "de grille SudoSimu valide.")
            return None
        self._gridFileName = fname
        self._gridAsLines = vals
        self._gameGrid = SudoGrid()
        self._gameGrid.fillByRowLines(vals)
        self._resetPlayingGrid() #affiche aussi la nouvelle grille de jeu
        return self._gameGrid

    def newRandomGrid(self, level="easy"):
        '''Initialise une grille aléatoire du niveau de difficulté indiqué.
        Par défaut le niveau est "easy" (facile).
        '''
        TEST = self.env.TEST
        TEST.display("simpleapp", 3, "SudoSimpleApp - dans newRandomGrid()")
#### ATTENTION ########################
# Les grilles aléatoires ne sont pas encore intégrées.
#######################################
        TEST.display("simpleapp", 1, "Les grilles aléatoires ne sont pas disponibles. "\
                     "Choisissez une grille depuis un fichier.")
        return False

    def _initGame(self):
        '''Prépare une partie. Pour cela, vérifie qu'une grille est prête
        à jouer et demande au joueur de préparer ses moyens de résolution
        (mem, etc.) pour cette grille.
        '''
        TEST = self.env.TEST
        #Vérifier qu'une grille est chargée
        if self._gridReady is not True:
            ui.DisplayError("Erreur", "Choisissez d'abord une grille.")
            return False
        #Réinitialiser la grille de jeu
        self.resetPlayingGrid()

        #Normalement il y a toujours un joueur initialisé.
        if not isinstance(self._player, SudoPlayer):
            raise Sudoku_Error("Erreur dans sudoapp.initGame(): pas de joueur "\
                               "initialisé. ")
        #nouvelle partie avec les moyens cognitifs du joueur
        try:
            (mem, think, view) = self._player.makeGameRessources(self._playingGrid)
            #passer l'environnement au nouvel objet SudoGame
            self._game = SudoGame(mem, think, view, env=self._env)
        except:
            errmsg = "Impossible de préparer une résolution."
            ui.displayError("Erreur", errmsg)
            self._game = None
            self._gameReady = None
            self._playing = False
            self._finished = False
            raise Sudoku_Error(errmsg)
        #ok
        TEST.display("simpleapp", 3, "SudoSimpleApp - Partie correctement initialisée.")
        TEST.display("simpleapp", 1, "La partie est prête pour une résolution.")
        self._gameReady = True
        self._playing = False
        self._finished = False
        return self._game

    def setPause(self, params):
        '''Définit les paramètres de pause pour l'avancement par étapes de
        la résolution.
        '''
        TEST = self.env.TEST
        self._pauseParams = params
        return True

    def solve(self, params=None):
        '''Lance la résolution avec le paramètre de pause indiqué, ou celui
        préréglé. Retourne un résultat "end", "pause" ou "fail", ou retourne
        'False' en cas d'erreur.
        Doit être appelée une seule fois, les appels suivants retournent une
        erreur. Pour continuer la résolution, utiliser resume() ou les méthodes
        de résolution pas-à-pas ou par étapes.
        '''
        TEST = self.env.TEST
        TEST.display("simpleapp", 3, "SudoSimpleApp - dans solve()")
        #vérification de début de résolution prêt
        if self._checkBeforePlaying() is not True:
            TEST.display("simpleapp", 3, "SudoSimpleApp - résolution impossible.")
            return False
        #ok résolution
        if params is not None:
            self.setPause(params)
        r = self._game.play(self._pauseParams, True)
        if r[0] == "pause":
            self._playing = True
        else:
            self._playing = False
        return r

    def next(self, params=None):
        '''Méthode de haut niveau, continue la résolution avec le paramètre
        de pause indiqué et mémorise ces paramètres pour la suite, ou utilise
        le paramètre préréglé.
        Retourne le résultat de résoultion, ou False
        '''
        TEST = self.env.TEST
        TEST.display("simpleapp", 3, "SudoSimpleApp - dans solvePause()")
        if self._playing is not True:
            return False
        if params is not None:
            self.setPause(params)
        r = self._game.play(self._pauseParams, True)
        if r[0] == "pause":
            self._playing = True
        else:
            self._playing = False
        return r
        
        
        return self._playGame(params)
    
    def solveToEnd(self):
        '''Méthode de haut niveau, lance ou continuela résolution jusqu'à la fin,
        sans pause intermédiaire équivalent à solve(END) ou next(END).
        '''
        TEST = self.env.TEST
        TEST.display("simpleapp", 3, "SudoSimpleApp - dans solveEnd()")
        return self.solve(END)

    def _playGame(self, params=None):
        '''Méthode de bas niveau, exécute directement la méthode de début
        de résolution de la propriété '_game' de l'instance, sans vérification.
        Met à jour la propriété '_playing'.
        '''
        TEST = self.env.TEST
        TEST.display("simpleapp", 3, "SudoSimpleApp - dans _playGame()")
        #vérifier la situation de résolution de l'appli
        r = self._checkBeforePlaying()
        if r is not True:
            return False
#### ATTENTION : Faire la gestion correcte des exceptions
        self._playing = True
        playResult = self._game.play(params)
        self._checkPlayResult(playResult)
        return playResult

    def _resumeGame(self):
        '''Continue la partie en cours jusqu'à la fin.
        Retourne le résultat.
        '''
        TEST = self.env.TEST
        TEST.display("simpleapp", 3, "SudoSimpleApp - dans _resumeGame()")

        #vérifier la situation de résolution de l'appli
        r = self._checkBeforePlaying()
        if r is not True:
            return False
#### ATTENTION : Faire la gestion correcte des exceptions
        self._playing = True
        playResult = self._game.resume()
        self._checkPlayResult(playResult)
        return playResult

    def _stepGame(self):
        '''Joue une itération de la partie en cours.
        Retourne le résultat.
        '''
        TEST = self.env.TEST
        TEST.display("simpleapp", 3, "SudoSimpleApp - dans _playGame()")
        #vérifier la situation de résolution de l'appli
        r = _checkBeforePlaying()
        if r is not True:
            return False
#### ATTENTION : Faire la gestion correcte des exceptions
        self._playing = True
        playResult = self._game.step()
        self._checkPlayResult(playResult)
        return playResult

##        result = None
##        r = None        #retour de la méthode
##        try:
##            #fait uniquement une itération de pensée
##            result = self._game.again()
##            #est-ce que la partie est terminée ?
##            if self._isGameFinished(result):
##                self._playing = False
##                self._finished = True
##                r = self._giveGameResult(result)
##                self._gameReady = False
##            else:
##                self._playing = True
##                self._finished = False
##                r = self._giveStepResult(result)
##        except:
##            DisplayError("Erreur", "La résolution a rencontré une erreur "\
##                         "inconnue et doit être abandonnée.")
##            self._gameReady = False
##            self._playing = False
##            raise Sudoku_Error("Interruption dans SudoPlayer.playGame()")
##        return r
        
##        try:
##            result = self._game.resume()
##            self._playing = False
##            self._finished = True
##            r = self._giveGameResult(result)
##            self._gameReady = False
##        except:
##            DisplayError("Erreur", "La résolution a rencontré une erreur "\
##                         "inconnue et doit être abandonnée.")
##            self._gameReady = False
##            self._playing = False
##            raise Sudoku_Error("Interruption dans SudoPlayer.playGame()")
##        return r
        
    def _checkBeforePlaying(self):
        '''Vérifie les conditions pour commencer la résolution : qu'il y ait
        une grille chargée et que la partie soit initialisée sans être en cours
        ni déjà terminée.
        '''
        TEST = self.env.TEST
        TEST.display("simpleapp", 3, "SudoSimpleApp - dans _checkBeforePlaying()")
        #cas où il n'est pas possible de jouer => erreur
        if self._playing is True:
            TEST.display("simpleapp", 1, "La résolution est déjà commencée. "\
                         "Utilisez une des commandes pour continuer ou la "\
                         "commande d'abandon.")
            return False
        elif self._gridReady is not True:
            TEST.display("simpleapp", 1, "Résolution impossible, il n'y a pas de "\
                         "grille prête à jouer. Commencez par choisir une "\
                         "grille ou réinitialiser la grille actuelle.")
            return False
        elif self._finished is True:
            TEST.display("simpleapp", 1, "La résolution est déjà terminée. Faites "\
                         "'Recommencer' pour une nouvelle résolution ou "\
                         "choisissez une nouvelle grille.")
            return False
        #ok possible de commencer, besoin d'initialiser la résolution
        else:
            if self._gameReady is not True:
                self._initGame()
        #message de début de résolution
        TEST.display("simpleapp", 1, "Début de résolution de la grille")
        self._playing is True
        return True


    def _checkBeforeContinuing(self):
        '''Vérifie que la partie est déjà commencée mais pas terminée, afin de
        la continuer.'''
        TEST = self.env.TEST
        TEST.display("simpleapp", 3, "SudoSimpleApp - dans _checkBeforeContinuing()")
        if self._playing is not True:
            TEST.display("simpleapp", 1, "La résolution doit être en cours pour "\
                         "utiliser cette commande. Commencez d'abord.")
            return False
        else:
            return True
        
    def _checkPlayResult(self, result):
        '''Analyse le résultat de l'avancement du jeu et affiche les informations
        spécifique à chaque cas de pause, de fin ou d'erreur. Met à jour les
        indicateurs d'état suivant que la partie continue ou est terminée.
        '''
        TEST = self.env.TEST
        #tous les cas de fin normale "end"
        if solveResult[0] == "end":
            self._finished = True
            self._playing = False
            self._gameReady = False
            if solveResult[1][0] == "win":
                TEST.display("player", 1, "La grille est gagnée !!!\n"\
                             "Résultats détaillés :\n{0}"\
                             .format(solveResult[1][1]))
                return
            elif solveResult[1][0] == "quit":
                TEST.display("player", 1, "La grille est perdue, impossible"\
                             "de réussir à la résoudre.\n"\
                             "Résultats détaillés :\n{0}"\
                             .format(solveResult[1][1]))
                return
            elif solveResult[1][0] == "fail":
                TEST.display("player", 1, "La grille est abandonnée "\
                             "volontairement.\nRésultats détaillés :\n{0}"\
                             .format(solveResult[1][1]))
                return
            #les autres cas "end" sont gérés à la fin
        elif solveResult[0] == "pause":
            self._finished = False
            self._playing = True
            self._gameReady = False
            TEST.display("player", 1, "La résolution est en pause.\n"\
                         "Détails : \n{0}"\
                         .format(solveResult[1][1]))
            return
        #Dans tous les autres cas, c'est une fin par erreur
        self._finished = True
        self._playing = False
        self._gameReady = False
        TEST.display("player", 1, "La résolution s'arrête à cause d'une "\
                     "erreur irrécupérable. \nDétails :\n{0}"\
                     .format(solveResult))
        return

        
    def _resetPlayingGrid(self, grid=None):
        '''Réinitialise la grille de jeu, soit à la grille initiale soit
        à la nouvelle instance de grille passée en paramètre (pas une copie).
        S'il y a une partie en cours elle est annulée d'office et une nouvelle
        partie est initialisée avec la nouvelle grilleq
        '''
        TEST = self.env.TEST
        if grid is None and self._gameGrid is None:
            return
        if grid is not None:
            #devient la nouvelle grille à jouer
            assert isinstance(grid, SudoGrid)
            self._gameGrid = grid
        self._playingGrid = self._gameGrid.copy()
        self.showPlayingGrid()
        self._gridReady = True
        #initialise une partie sur la grille prête
        self._initGame()
        return True

    def reset(self):
        '''Réinitialise la partie. Dans la version d'application simple,
        c'est équivalent à réinitialiser la grille, ce qui prépare d'office
        une nouvelle partie.
        '''
        return self._resetPlayingGrid()

    def showPlayingGrid(self):
        return self.showAnyGrid(self._playingGrid)

    def showGameGrid(self):
        '''Affiche la grille qui est à résoudre, c'est-à-dire la grille
        initiale.
        '''
        return self.showAnyGrid(self._gameGrid)
    
    def showAnyGrid(self, grid):
        '''Affiche une grille sur les interfaces actives. Affiche n'importe
        quelle grille, pas forcément celle d'une partie en cours.
        '''
        ui.displayGridClear()
        ui.displayGridAll(grid)
        return
    
##    def getEnv(self):
##        '''Retourne l'instance d'environnement utilisé.'''
##        return self._env
##
##    env = property(getEnv, setEnv, doc=\
##        '''\'env\' est l'environnement d'exécution de la simulation.''')
##
##    def envTestLevel(self, key, level=None):
##        return self._env.test.level(key, level)
##
##    def envTestLevelAll(self, level):
##        return self._env.test.levelAll(level)
    
    @property
    def player(self):
        return self._player

    @property
    def grid(self):
        return self._gameGrid

    @property
    def gameGrid(self):
        return self._gameGrid

    @property
    def playingGrid(self):
        return self._playingGrid

    @property
    def game(self):
        return self._game

    @property
    def isPlaying(self):
        return self._playing

    @property
    def isFinished(self):
        return self._finished

  
def testlev(lev):
    TEST.levelAll(lev)


#TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST
#TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST


if __name__ == "__main__":

    #installer l'interface
    testlev(0)
    testMakeUI()

    
    #fonctions de renouvellement du jeu
    grid = None
    def newGrid():
        global grid
        grid = testNewGrid()
        testShowGrid(grid)
        return
    david = None
    def go():
        global david
        resetGrid()
        david.solve(grid, params)
        return
    def resetGrid():
        global grid
        testShowGrid(grid)
        return

    #Initialisation des tests
    TEST.level("main", 1)
    ui.display("\nTest du module sudoplayer")
    ui.display("----------------------------\n")
    newGrid()
    TEST.display("main", 1, "\nCréation et initialisation du joueur")
    TEST.display("main", 1, "Création du joueur : 'david'")
    david = pl.SudoPlayer("David")
    #Niveaux de commentaires pour la partie
    TEST.level("thinkai", 1)
    #    TEST.level("player", 3)
    #    TEST.level("game", 3)


    #Paramètres de la partie
    params = None
    #Jeu
    TEST.display("main", 1, "Prêt à jouer.\n")
    print("\n...>>> david.solve(grid) \nou >>> go()")

    #ui.sudoPause()
    #go()

