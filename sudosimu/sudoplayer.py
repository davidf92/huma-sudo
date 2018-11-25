'''Joueur de Sudoku.

Dans cette version un joueur ne peut résoudre qu'un partie à la fois. Il ne
gère donc pas de table de ses ressources de résolution allouées à une partie
(mémoire, réflexion etc.)

Historique des modifications :
15/11/2017 - Evolution pour utiliser le système d'environnement avec SudoEnv
    ainsi que tout le support de TEST dans sudoenv.
'''

if __name__ in ("__main__", "sudoplayer"):
    import sudobaseclass as base
    import sudoenv
    import sudoui as ui
    import sudorules as rules
    from sudorules import Sudoku_Error
    from sudogrid import SudoGrid
    from sudogridview import SudoGridView
    from sudomemprofile import SudoMemProfile
    from sudothinkprofile import SudoThinkProfile
    from sudomemory import SudoMemory
    from sudothinking import SudoThinking
    from sudogame import SudoGame
elif __name__ == "sudosimu.sudoplayer":
    from sudosimu import sudobaseclass as base
    from sudosimu import sudoenv
    from sudosimu import sudoui as ui
    from sudosimu import sudorules as rules
    from sudosimu.sudorules import Sudoku_Error
    from sudosimu.sudogrid import SudoGrid
    from sudosimu.sudogridview import SudoGridView
    from sudosimu.sudomemprofile import SudoMemProfile
    from sudosimu.sudothinkprofile import SudoThinkProfile
    from sudosimu.sudomemory import SudoMemory
    from sudosimu.sudothinking import SudoThinking
    from sudosimu.sudogame import SudoGame
else:
    raise Exception("Impossible de faire les imports dans le module sudoplayer.")


#ATTENTION :
#La gestion d'erreurs est à faire partout.

class SudoPlayer(base.SudoBaseClass):
    '''Représente un joueur de Sudoku. Un joueur a des capacités cognitives,
    une mémoire de travail, une connaissance et de l'expérience du jeu.
    '''

    def __init__(self, name=None, \
                 env=None, testlevel=sudoenv.TEST_PLAYERLEVEL):
        '''Initialisation de l'instance. Donne un nom par défaut au joueur.'''
        #init de la classe racine
        assert isinstance(env, sudoenv.SudoEnv) or env is None
        assert isinstance(testlevel, int) and testlevel>=0 \
                or testlevel is None
        #reprendre un précédente niveau de test s'il existe déjà
        oldlev = env.testLevel("player")
        if oldlev is not None and testlevel != oldlev:
            testlevel = oldlev
        base.SudoBaseClass.__init__(self, env=env, \
                                    testlabel="player", testlevel=testlevel)
        #ok init de cette classe
        TEST = self.env.TEST
        TEST.display("player", 3, "SudoPlayer - dans __init__()")        
        assert isinstance(name, str) or name is None
        if name is None:
            self._name = "Anonyme"
        else:
            self._name = name
        TEST.display("player", 1, "Création du joueur : \'{0}\'".format(name))
        #suite de l'initialisation
        self._init2()
        self._initOk = True
        return
    
    def _init2(self):
        '''Suite d'initialisation de l'instance.'''
        TEST = self.env.TEST
        self._mem = None
        self._think = None
        self._view = None
        self._game = None
        self._know = None
        self._memProfile = None
        self._thinkProfile = None
        #les grilles : l'originale, les copies et la grille de jeu
        self._initGrid = None
        self._initGridCopy = None
        self._gameGrid = None
        #variables de contrôle du jeu
        self._gameReady = False
        self._gameFinished = False
        self._playing = False
        TEST.display("player", 3, "SudoPlayer - Initialisation terminée")
        return

    def initProfiles(self, memProfile, thinkProfile, knowledge):
        '''Complète l'initialisation. Tout complément d'initialisation doit
        être ajouté ici.
        '''
        TEST = self.env.TEST
        setMemProfile(memProfile)
        setThinkProfile(thinkProfile)
##        setKnowledge(knowledge)
        self._init2()
        self._initOk = True

    def setKnowledge(self, knowledge):
        '''Cette méthode n'est pas encore implémentée.'''
        TEST = self.env.TEST
#### A PROGRAMMER
        return
####

    def loadKnowledge(self, knowledgeSource):
        '''Obtient un savoir-faire de jeu (instance de SudoKnowledge).'''
        TEST = self.env.TEST
## A PROGRAMMER
        return
######

    def saveKnowledge(self, knowledgeSource):
        '''Sauvegarde le savoir-faire qui a évolué grâce aux parties jouées.'''
        TEST = self.env.TEST
## A PROGRAMMER
        return
######
        
    def setMemProfile(self, memProfile):
        '''Définit le profil de mémoire.'''
        TEST = self.env.TEST
## A PROGRAMMER
        return
######
        assert isinstance(memProfile, SudoMemProfile)
        self._memProfile = memProfile.copy()
    
    def setThinkProfile(self, thinkProfile):
        '''Définit le profil de mémoire.'''
        TEST = self.env.TEST
## A PROGRAMMER
        return
######
        assert isinstance(thinkProfile, SudoThinkProfile)
        self._thinkProfile = thinkProfile.copy()

    def makeGameRessources(self, grid):
        '''Crée un ensemble de ses ressources cognitives de résolution :
        mémoire, réflexion et interaction avec une grille.
        Retourne ces objets dans une liste.
        '''
        TEST = self.env.TEST
        TEST.display("player", 3, "SudoPlayer - dans _initGame()")
        TEST.display("player", 2, "Préparation du joueur pour la partie...")
        assert self._initOk
        assert isinstance(grid, SudoGrid)
        #préparation de la mémoire du joueur pour la partie
        try:
            mem = SudoMemory(self._memProfile, env=self.env)
        except:
            ui.displayError("Erreur", "Impossible de créer la mémoire de jeu.")
            #self._mem = None
            raise Sudoku_Error("new SudoMemory fail in SudoPlayer.initGame()")
        #préparation de la pensée du joueur pour la partie
        try:
            think = SudoThinking(mem, self._thinkProfile, env=self.env)
        except:
            ui.displayError("Erreur", "Impossible de créer la pensée.")
            #self._think = None
            raise Sudoku_Error("new SudoThinking fail in SudoPlayer.initGame()")
        #création de la vue sur la grille
        try:
            view = SudoGridView(grid, env=self.env)
        except:
            ui.displayError("Erreur", "Impossible de créer la vue sur la grille.")
            #self._view = None
            raise Sudoku_Error("new SudoGridView fail in SudoPlayer.initGame()")
        #ok
        return (mem, think, view)

        
##    def solve(self, grid, params=None):
##        '''Tente la résolution de la grille indiquée, donc joue une partie avec
##        la classe SudoGame. Des paramètres de contrôle du jeu peuvent être
##        indiqués, dans ce cas ils remplacent les paramètres pré-initialisés.
##        Retourne le résultat de la partie : gagnée ou abandonnée ou erreur.
##        '''
##        TEST.display("player", 3, "SudoPlayer - dans solve()")
##        assert self._initOk
##        assert isinstance(grid, SudoGrid)
##        self._initGrids(grid)
##        self._initGame()
##
##        TEST.display("player", 1, "Début de résolution de la grille")
##        solveResult = self._game.play(params)
######
###### FAIRE LA GESTION DES EXCEPTIONS
######
##        #tous les cas de fin normale "end"
##        if solveResult[0] == "end":
##            self._gameFinished = True
##            self._playing = False
##            self._gameReady = False
##            if solveResult[1][0] == "win":
##                TEST.display("player", 1, "La grille est gagnée !!!\n"\
##                             "Résultats détaillés :\n{0}"\
##                             .format(solveResult[1][1]))
##                return
##            elif solveResult[1][0] == "quit":
##                TEST.display("player", 1, "La grille est perdue, impossible"\
##                             "de réussir à la résoudre.\n"\
##                             "Résultats détaillés :\n{0}"\
##                             .format(solveResult[1][1]))
##                return
##            elif solveResult[1][0] == "fail":
##                TEST.display("player", 1, "La grille est abandonnée "\
##                             "volontairement.\nRésultats détaillés :\n{0}"\
##                             .format(solveResult[1][1]))
##                return
##            #les autres cas "end" sont gérés à la fin
##        elif solveResult[0] == "pause":
##            self._gameFinished = False
##            self._playing = True
##            self._gameReady = False
##            TEST.display("player", 1, "La résolution est en pause.\n"\
##                         "Détails : \n{0}"\
##                         .format(solveResult[1][1]))
##            return
##        #Dans tous les autres cas, c'est une fin par erreur
##        self._gameFinished = True
##        self._playing = False
##        self._gameReady = False
##        TEST.display("player", 1, "La résolution s'arrête à cause d'une "\
##                     "erreur irrécupérable. \nDétails :\n{0}"\
##                     .format(solveResult))
##        return
##
##    def _initGrids(self, grid):
##        '''Prépare la grille de jeu et ses copies. 
##        La partie se joue avec une copie de la grille indiquée.
##        '''
##        TEST.display("player", 3, "SudoPlayer - dans _initGrids()")
##        assert isinstance(grid, SudoGrid)
##        assert self._initOk
##        self._gameGrid = grid.copy()
##        self._initGrid = grid
##        self._initGridCopy = grid.copy()
##        
##    def _initGame(self):
##        '''Suite de la préparation de résolution. Création de l'objet SudoGame
##        et de la mémoire et la pensée du joueur.
##        '''
######
###### FAIRE LA GESTION DES EXCEPTIONS
######
##        TEST.display("player", 3, "SudoPlayer - dans _initGame()")
##        TEST.display("player", 2, "Préparation de la partie...")
##        assert self._initOk
##        self._gameReady = False
##        #préparation de la mémoire du joueur pour la partie
##        try:
##            self._mem = SudoMemory(self._memProfile)
##        except:
##            ui.displayError("Erreur", "Impossible de créer la mémoire de jeu.")
##            self._mem = None
##            raise Sudoku_Error("new SudoMemory fail in SudoPlayer.initGame()")
##        #préparation de la pensée du joueur pour la partie
##        try:
##            self._think = SudoThinking(self._mem, self._thinkProfile)
##        except:
##            ui.displayError("Erreur", "Impossible de créer la pensée.")
##            self._think = None
##            raise Sudoku_Error("new SudoThinking fail in SudoPlayer.initGame()")
##        #création de la vue sur la grille
##        try:
##            self._view = SudoGridView(self._gameGrid)
##        except:
##            ui.displayError("Erreur", "Impossible de créer la vue sur la grille.")
##            self._view = None
##            raise Sudoku_Error("new SudoGridView fail in SudoPlayer.initGame()")
##        #création de la partie
##        try:
##            self._game = SudoGame(self._mem, self._think, self._view)
##        except:
##            ui.displayError("Erreur", "Impossible de créer la partie.")
##            self._game = None
##            raise Sudoku_Error("new SudoGame fail in SudoPlayer.initGame()")
##        #ok
##        TEST.display("player", 3, "SudoPlayer - Parti initialisée :\n"\
##                     "mem = {0}\nthink = {1}game = {2}"\
##                     .format(self._mem, self._think, self._game))
##        TEST.display("player", 2, "Ok la partie estprête à être jouée.")
##        self._gameReady = True
##        self._playing = False
##        self._gameFinished = False
##        return True
##            
##    def stepGame(self):
##        '''Joue un coup de la partie en cours.
##        Retourne le résultat.
##        '''
##        TEST.display("player", 3, "SudoPlayer - dans stepGame()")
##        TEST.display("player", 2, "Etape de résolution")
##        assert self._initOk
##        assert self._gameReady
##        assert self._playing
##        result = None
##        r = None        #retour de la méthode
##        try:
##            #fait uniquement une itération de pensée
##            result = self._game.again()
##            #est-ce que la partie est terminée ?
##            if self._isGameFinished(result):
##                self._playing = False
##                self._gameFinished = True
##                r = self._giveGameResult(result)
##                self._gameReady = False
##            else:
##                self._playing = True
##                self._gameFinished = False
##                r = self._giveStepResult(result)
##        except:
##            DisplayError("Erreur", "La résolution a rencontré une erreur "\
##                         "inconnue et doit être abandonnée.")
##            self._gameReady = False
##            self._playing = False
##            raise Sudoku_Error("Interruption dans SudoPlayer.playGame()")
##        return r
##        
##    def resumeGame(self):
##        '''Continue la partie en cours jusqu'à la fin.
##        Retourne le résultat.
##        '''
##        TEST.display("player", 3, "SudoPlayer - dans stepGame()")
##        TEST.display("player", 2, "Etape de résolution")
##        assert self._initOk
##        assert self._gameReady
##        assert self._playing
##        result = None
##        r = None        #retour de la méthode
##        try:
##            result = self._game.resume()
##            self._playing = False
##            self._gameFinished = True
##            r = self._giveGameResult(result)
##            self._gameReady = False
##        except:
##            DisplayError("Erreur", "La résolution a rencontré une erreur "\
##                         "inconnue et doit être abandonnée.")
##            self._gameReady = False
##            self._playing = False
##            raise Sudoku_Error("Interruption dans SudoPlayer.playGame()")
##        return r
##        
##    def reInitGame(self):
##        '''Réinitialise la dernière partie. Suivant le paramètre initial, il
##        faut reprendre la même instance de grille ou faire une autre copie.
##        '''
##        #restaurer l'objet 'grid' de jeu, soir l'original soit une copie
##
##        if self._sameInst is True:
##            self._gameGrid.copyFrom(self._initGridCopy)
##        else:
##            self._gameGrid = self._initGridInst.copy()
##        r = self._initGame2()
##        return r
##    
##    def replayGame(self, complete=True):
##        '''Rejoue la dernière partie. Suivant le paramètre initial, il faut
##        reprendre la même instance de grille ou faire une autre copie.
##        '''
##        #restaurer l'objet 'grid' de jeu, soir l'original soit une copie
##        r = self.reInitGame()
##        r = self.playGame(complete)
##        return r
##
##    def keepPlaying(self, complete=True):
##        '''Recommence une nouvelle partie à partir de l'état actuel de la grille.
##        Permet de modifier artificiellement soit la grille soit des paramètres
##        de mémoire et/ou de pensée, puis de reprendre la résolution sur ces
##        nouvelles bases.
##        '''
##        r = self._initGame2()
##        r = self.playGame(complete)
##        return r
##    
    @property
    def gameGrid(self):
        return self._gameGrid
    
    def _isGameFinished(self, result):
        '''Indique si le résultat du dernier coup signifie que la partie
        est terminée : gagnée, perdue, abandonnée, etc. ou au contraire
        si elle continue : observation, placement, etc.
        '''
        TEST = self.env.TEST
        assert self._initOk
        lastAction = result[0]
        if lastAction in ("continue", "observe", "place", "fail"):
            return False
        else:
            return True

    def _giveGameResult(self, result):
        '''Donne le résultat de la partie qui est terminée.'''
        TEST = self.env.TEST
        #Version limitée : affiche simplement la résultat résumé
        TEST.display("player", 1, "Player - Résultat de la partie : {0}"\
                                    .format(result))
        return result


    def _giveStepResult(self, result):
        '''Donne le résultat de l'itération de pensée.'''
        TEST = self.env.TEST
        #Version limitée : affiche simplement la résultat résumé
        TEST.display("player", 1, "Player - Résultat du coup : {0}"\
                                    .format(result))
        return result

    def memProfile(self, newProfile=None):
        '''Initialise la capacité mémoire du joueur avec un profile mémoire.
        Si l'argument est 'None', retourne le profil mémoire actuel.'''
        TEST = self.env.TEST
        assert self._initOk
        if newProfile is not None:
            assert isinstance(newProfile, SudoMemProfile)
            self._memProfile = newProfile
        TEST.display("player", 3, "Dans memProfile() - Le profil mémoire est "\
                     "maintenant {0}".format(self._memProfile))
        return self._memProfile

    def thinkProfile(self, newProfile=None):
        '''Initialise la capacité de réflexion du joueur'''
        TEST = self.env.TEST
        assert self._initOk
        if newProfile is not None:
            assert isinstance(newProfile, SudoThinkProfile)
            self._thinkProfile = newProfile
        TEST.display("player", 3, "Dans thinkProfile() - Le profil de pensée "\
                     "est maintenant {0}".format(self._thinkProfile))
        return self._thinkProfile

    def profiles(self):
        TEST = self.env.TEST
        assert self._initOk
        return ("Joueur : {0} de profile mémoire : {1} et profil "\
                .format(self._name, self._memProfile) +\
                "de pensée : {0}".format(self._thinkProfile))
    
    def name(self, newName=None):
        '''modifie ou retourne le nom du joueur.'''
        TEST = self.env.TEST
        assert self._initOk
        if newName is not None:
            self._name = newName
        TEST.display("player", 3, "dans name()- Le joueur s'appelle maintenant : "\
                     "{0}".format(self._name))
        return self._name

    def isReady(self):
        assert self._initOk
        assert self._ready
        return True

    @property
    def name(self):
        assert self._initOk
        return self._name
    
    @property
    def mem(self):
        assert self._initOk
        return self._mem

    @property
    def think(self):
        assert self._initOk
        return self._think

    @property
    def view(self):
        assert self._initOk
        return self._view

    @property
    def game(self):
        assert self._initOk
        return self._game

    @property
    def gameGrid(self):
        assert self._initOk
        return self._gameGrid

    @property
    def initGrid(self):
        assert self._initOk
        return self._initGrid
    
        
    def __str__(self):
        '''Retourne comme forme d'écriture le nom du joueur ou un nom
        par défaut.
        '''
        assert self._initOk
        name = str(self._name)
        if name is None or name == "":
            name = "Un joueur"
        txt = "Joueur '{0}' avec un profil mémoire '{1}' et un profil de "\
              "pensée '{2}'".format(name, self._memProfile, self._thinkProfile)
        return txt
    

        
#TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST
#TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST

if __name__ == "__main__":


    import sudotestall
    from sudogrid import SudoGrid
    from test_main import *

    #interface
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
    david = SudoPlayer("David")
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
    
