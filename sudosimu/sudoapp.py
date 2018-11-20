'''Module 'sudoapp' : Trame d'application gérée avec une classe dédiée SudoApp.

L'application ainsi définie englobe la manipulation de la grille, du joueur et
des parties, gère toutes les options de résolution et l'avancement pas-à-pas
paramétré. Permet aussi de gérer les détails d'affichage d'avancement de la
résolution.

Historique des modifications :
15/11/2017 - Evolution pour utiliser le système d'environnement avec SudoEnv
24/10/2017 - Version initiale
'''

if __name__ in ("__main__", "sudoapp"):
    import sudoenv
    import sudoui as ui
    import sudorules as rules
    from sudorules import *
    from sudogrid import SudoGrid
    from sudoplayer import SudoPlayer
    from sudogame import SudoGame
    from sudomemprofile import SudoMemProfile
    from sudothinkprofile import SudoThinkProfile
    from sudomemory import SudoMemory
    from sudothinking import SudoThinking
    from sudogame import *
    from sudotest import *
    import sudotestall
elif __name__ == "sudosimu.sudoapp":
    from sudosimu import sudoenv
    from sudosimu import sudoui as ui
    from sudosimu import sudorules as rules
    from sudosimu.sudorules import *
    from sudosimu.sudogrid import SudoGrid
    from sudosimu.sudoplayer import SudoPlayer
    from sudosimu.sudogame import SudoGame
    from sudosimu.sudomemprofile import SudoMemProfile
    from sudosimu.sudothinkprofile import SudoThinkProfile
    from sudosimu.sudomemory import SudoMemory
    from sudosimu.sudothinking import SudoThinking
    from sudosimu.sudogame import *
    from sudosimu.sudotest import *
    from sudosimu import sudotestall
else:
    raise Exception("Impossible de faire les imports dans le module sudoapp.")


#### CONVENTIONS ####
#1)Nommage : Les propriétés et méthodes de classes commençant par un '_' doivent être
#considérées comme privées et ne doivent donc pas être accédées dans l'usage
#de ces classes (même si le langage Python ne rend pas cela impossible).
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
PLACE = "place"     #pause uniquement à chaque placement
FAIL = "fail"       #pause à chaque difficulté ou erreur de jeu
END = "end"         #explicitement jusqu'à la fin (équivalent à 'None')
                    #END s'impose contre les autres paramètres.
EXCEPT = "except"   #pause à chaque déclenchement d'un exception. C'est plutôt
                    #destiné au débuggage, ça n'a pas de sens pour un joueur.
NOEXCEPT = "noexcept" #pour annuler explicitement la pause sur exception.


class SudoApp:
    '''Classe qui englobe une application de simulation de Sudoku. Cette classe
    permet de manipuler des joueurs, des grilles, de créer et jouer des parties,
    faire de la résolution par étapes en suivant l'affichage de l'évolution,
    et de gérer des interfaces utilisateur fonctionnelles ou événementielles.
    '''

    def __init__(self):
        '''Initialise l'instance et crée un joueur par défaut. Il suffit donc
        d'ouvrir une interface UI et charger une grille pour pouvoir
        tenter une résolution.
        '''
        TEST.display("app", 3, "SudoApp - dans __init__()")
        self._initInstance()
        self.newPlayer()
        return

    def _initInstance(self):
        '''Initialise les propriétés de l'instance. Dans cette version une
        instance d'application ne gère qu'une grille à la fois pour un seul
        joueur.
        '''
        TEST.display("app", 3, "SudoApp - dans _initInstance()")
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
        self._displayUImode = None
        self._displayUImodeLevel = None
        #partie et contrôle de résolution
        self._game = None
        #self._gameInit = False  #indique s'il y a une grille chargée
        self._gameReady = False #indique si la partie est prête à être jouée
        self._playing = False   #indique si la résolution est en cours
        self._finished = False  #indique si la résolution est terminée
        self._pauseParams = None  #paramètres de pause en résol. par étapes
        return True

    def makeUI(self):
        '''Prépare l'interface utilisateur console et graphique.
        Par défaut, définit l'utilisation console et fenêtre à la fois.
        '''
        TEST.display("app", 3, "SudoApp - dans makeUI()")
        self._uiMode = ui.GUI
        self._displayUImode = MODE_BOTH    #REMPLACER PAR ui.MODE_BOTH ?
        self._displayUImodeLevel = 1

        ui.UImode(self._uiMode)
        TEST.displayUImode(self._displayUImode, self._displayUImodeLevel)
        TEST.display("game", 3, "SudoApp - Interface utilisateur initialisée.")
        return True

    def close(self):
        '''Arrête l'application et ferme l'interface graphique s'il y en a une.
        '''
###############################################################################
# L'intérêt potentiel de cette méthode est de permettre la sauvegarde de données
# telles que des statistiques de résolution, des données de performance et
# d'apprentissage sur le plan AI, ou encore les connaissances développées
# par les joueurs.
###############################################################################
        ui.closeGUI()
        return
    
    def newPlayer(self, name=None):
        '''Crée pour l'application un nouveau joueur avec le nom indiqué.
        Cela oblige à annuler toute résolution de grille en cours. S'il y a
        une grille chargée, elle est réinitialisée.
        '''
        TEST.display("app", 3, "SudoApp - dans newPlayer()")
        if name is None:
            name = self._defaultPlayerName
        self._player = SudoPlayer(name)
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
        TEST.display("app", 3, "SudoApp - dans newGrid()")
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
        TEST.display("app", 3, "SudoApp - dans newGridFromFile()")
        
        #choix de fichier s'il n'est pas indiqué
        if fname is None:
            TEST.display("app", 1,"Choisir une grille depuis un fichier "\
                                  "de test :")
            fname = ui.sudoNumTestFich()
            TEST.display("app", 3, "nom de fichier : {0}\n".format(fname))
            if fname is None:    #impossible de lire un fichier de grille
                ui.displayError("Erreur fichier", "Impossible de lire le "\
                    "fichier indiqué, ou ce fichier n'est pas un fichier "\
                    "de grille SudoSimu valide.")
                TEST.display("app", 3, "newGridFromFile - Erreur : pas de nom "\
                                         "de fichier.")
                return None
            TEST.display("app", 1, "Fichier choisi : {0}\n".format(fname))

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
        self.resetPlayingGrid() #affiche aussi la nouvelle grille de jeu
        return self._gameGrid

    def solveGrid(self, params=None):
        '''Crée une nouvelle partie avec la grille et le joueur initialisés, et
        lance la résolution, c'est-à-dire commence à jouer la grille, avec
        les paramètes indiqués.
        Retourne un résultat final ou intermédiaire de résolution suivant le
        paramétrage.
        '''
        self._initGame()
        r = self._solveGame(params)

    def _solveGame(params):
        '''Lance la résolution d'une grille par le joueur. Le paramètre
        indique le contrôle d'avancement de la résolutino demandé par le
        joueur : d'un coup jusqu'à la fin, par étapes, pas-à-pas, etc.
        Retourne le résultat de la résolution.
        '''
####CONTINUER ICI##################################        

        return
    

    def _initGame(self):
        '''Prépare une partie. Pour cela, vérifie qu'une grille est prête
        à jouer et demande au joueur de préparer ses moyens de résolution
        (mem, etc.) pour cette grille.
        '''
        #Vérifier qu'une grille est chargée
        if self._gridReady is not True:
            ui.DisplayError("Erreur", "Choisissez d'abord une grille.")
            return False
        #Réinitialiser la grille de jeu
        self.resetPlayingGrid()

        #Moyens de résolution du joueur. Normalement il y a toujours un
        #joueur initialisé.
        if not isinstance(self._player, SudoPlayer):
            raise Sudoku_Error("Erreur dans sudoapp.initGame(): pas de joueur "\
                               "initialisé. ")
####Gestion propre d'exceptions à faire ici        
        try:
            (mem, think, view) = self._player.makeGameRessources(self._playingGrid)
            self._game = SudoGame(mem, think, view)
        except:
            errmsg = "Impossible de préparer une résolution."
            ui.displayError("Erreur", errmsg)
            self._game = None
            self._gameReady = None
            self._playing = False
            self._finished = False
            raise Sudoku_Error(errmsg)
        #ok
        TEST.display("app", 3, "SudoApp - Parti correctement initialisée.")
        TEST.display("app", 2, "Ok la partie estprête à être jouée.")
        self._gameReady = True
        self._playing = False
        self._finished = False
        return self._game
            
    def resetPlayingGrid(self, grid=None):
        '''Réinitialise la grille de jeu, soit à la grille initiale soit
        à la nouvelle instance de grille passée en paramètre (pas une copie).
        S'il y a une partie en cours elle est annulée d'office.
        '''
        if grid is None and self._gameGrid is None:
            return
        if grid is not None:
            #devient la nouvelle grille à jouer
            assert isinstance(grid, SudoGrid)
            self._gameGrid = grid
        self._playingGrid = self._gameGrid.copy()
        #état de l'appli : grille prête à être jouée mais pas de partie prête
        self.showPlayingGrid()
        self._gridReady = True
        self._gameReady = False
        self._playing = False
        self._finished = False
        
        return    

    def resetGame(self):
        '''Réinitialise la grille de la partie au niveau initial et affiche.'''
        self._initGame()
        return True

    def setPauseParams(self, params):
        '''Définit les paramètres de pause pour l'avancement par étapes de
        la résolution.
        '''
        self._pauseParams = params
        return True

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
    
    @property
    def player(self):
        return self._player

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

