'''Jeu de Sudoku en simulation humaine. Joue au Sudoku de la même manière
qu'un joueur humain en utilisant des capacités cognitives simulées avec leurs
imperfections et leurs limites. Tente également d'apprendre à mieux jouer.
'''

import sudoio
from sudoio import sudoPause, display, displayError
import sudorules as rules

import sudogrid
from sudogrid import SudoGrid
from sudogame import SudoGame
from sudoplayer import SudoPlayer
from sudomemprofile import SudoMemProfile
from sudothinking import SudoThinkProfile

import sudotest
from sudotest import sudoTest as TEST       #objet global


class Sudoku():
    '''Encapsule le jeu dans son ensemble. Une instance de Sudoku gère des
    grilles, des joueurs créés avec des niveaux de compétences, et fait se
    jouer des parties par les joueurs avec les grilles.
    '''

    def __init__(self):
        '''Instanciation'''
        self._initOk = False
        self.init()

    def init(self):
        '''initialisatino ou réinitialisation du jeu.'''
        display("Jeu de Sudoku - Simulation de joueur humain")
        TEST.display("sudoku", 3, "Sudoku - dans init()")
        self._player = None
        self._playerOk = False
        self._playerReady = False
        self._playerMemProfile = None
        self._playerThinkProfile = None
        self._playerProfilesOk = False
        self._gridOk = False
        self._gameOk = False

        self._initOk = True
        TEST.display("sudoku", 1, "Jeu de Sudoku initialisé.")
        return

    def createPlayer(self, name=None):
        '''Crée un joueur en lui attribuant un nom. Le joueur n'a pas
        initialement de mémoire ni de pensée, cela est créé ensuite.
        '''
        assert self._initOk
        try:
            self._player = SudoPlayer(name)
            self._player.init()
        except:
            displayError("Erreur","Impossible de créer le joueur")
            self._player = None
            self._playerOk = False
            raise Sudoku_Error("Sudoku.createPlayer(): erreur de création")
        self._playerOk = True
        TEST.display("sudoku", 2, "Sudoku - Joueur {0} créé" \
                                     .format(self._player.name()))
        return

    def playerProfile(self, memProfile=None, thinkProfile=None):
        '''Donne au joueur des capacités mémoire et pensée selon des profiles'''
        TEST.display("sudoku", 3, "Sudoku - dans playerProfile()")
        assert self._initOk
        try:
            if memProfile is not None:
                assert isinstance(memProfile, SudoMemProfile)
            self._player.memProfile(memProfile)
            self._playerMemProfile = memProfile
            if thinkProfile is not None:
                assert isinstance(thinkProfile, SudoThinkProfile)
            self._player.thinkProfile(thinkProfile)
            self._playerThinkProfile = thinkProfile
            self._playerProfilesOk = True
        except:
            DisplayError("Erreur", "Impossible de créer le profil du joueur")
            self._PlayerProfilesOk = False
            raise Sudoku_Error("Impossible de définir le profile du joueur")
        return

    def playerPlay(self, player, grid):
        assert self._initOk
        assert player is not None and isinstance(player, SudoPlayer)
        assert grid is not None and isinstance(grid, SudoGrid)
        gameResult = player.play(grid)
        display(gameResult)
        return gameResult

##    def createGame(self, player, grid):
##        '''Crée une partie avec un joueur et une grille de Sudoku'''
##        assert self._initOk
##        assert isinstance(player, SudoPlayer) and self._playerOk
##        assert isinstance(grid, SudoGrid)
##        try:
##            self._game = SudoGame()
##            self._game.init(player, grid)
##        except:
##            DisplayError("Erreur", "Impossible de créer la partie")
##            self._gameOk = False
##            raise Sudoku_Error("Impossible de créer la partie")
##        self._grid = grid
##        self._gridOk = True
##        self._gameOk = True
##        TEST.display("sudoku", 1, "La partie est prête à être jouée")
##        return self._game
##
##    def play():
##        '''Lance le jeu.'''
##        result = self._game.play()
##        #resultDetails = self._game.details()
##        return
    
    

#TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST
if __name__ == "__main__":

    import sudotestall
    testAlllevel = 1
    TEST.levelAll(testAlllevel)
    display("Tous les niveaux de test sont à {0}".format(testAlllevel))

    s = Sudoku()
    s.createPlayer("David")
    
