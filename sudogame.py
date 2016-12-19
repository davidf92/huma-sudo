# -*- coding: cp1252 -*-

''' Programme HumaSudo
    Résolution humaine simulée de Sudoku 
    Module sudogame : gestion d'une partie
'''

import sudoplayer
import sudogrid
import sudoio
import sudorules as rules
from sudorules import Sudoku_Error

class SudoGame():
    '''Cette classe gère les parties
    Chaque instance résoud une partie d'un joueur avec une grille.
    Quand la partie est gagnée ou abandonnée, l'instance est tuée.
    Au cours de la partie, le joueur peut gagner en expérience , ce qui lui
    servira pour ses parties suivantes.
    '''

    def __init__(self, player=None, grid=None):
        '''Crée une partie. Enregistre le joueur et la grille s'ils sont
        indiqués lors de l'instantiation
        '''
#Comment vérifier que 'player' et 'grid' sont de la bonne classe,
#et si non déclencher une exception de type ?
        self.__player = player
        self.__grid = self.__startGrid = grid
        self.__playing = False
        self.__init = (grid == None and player == None)

    def newGrid(self, grid=None):
        '''Propose une nouvelle grille au même joueur
        '''
        #vérifications
        if grid == None:
            raise Sudoku_Error("Nouvelle partie mais pas de grille !")
##        if grid.isEmpty():
##            raise Sudoku_Error("Nouvelle partie mais grille vide !")
        
        self.__startGrid = grid
        self.__grid = grid
        self.__playing = False
        self.__init = True
            
        return grid
    
    def newPlayer(self, player):
        '''Change le joueur et remet la grille initiale.
        Permet de jouer une même grille avec différents joueurs
        '''
        if player == None:
            raise Sudoku_Error("Nouvelle partie mais pas de joueur :")
        #si une partie est en cours, l'arrêter
        if self.__playing:
            self.cancelGame()
        self.__player = player
        self.__playing = False
        self.__init = True
        return player
        
    def play(self):
        '''Joue la partie
        '''

    def cancelGame(self):
        '''Annule une partie mais garde le même joueur et la même grille
        de départ.
        '''
        if self.__playing:
            self.__grid = self.__startGrid
            self.__playing = False

    def reinit(self):
        '''Réinitialise complètement l'instance, sans joueur ni grille
        Equivalent à instancier la classe sans fournir d'arguments
        '''
        self.__grid = None
        self.__startGrid = None
        self.__player = None
        self.__playing = False
        self.__init = False
        
    @property
    def grid(self):
        '''Retourne la grille dans son état actuel du jeu
        '''
        return self.__grid

    @property
    def startGrid(self):
        '''Retourne la grille initiale du jeu
        '''
        return self.__startGrid
    
    @property
    def player(self):
        '''Retourne le nom du joueur
        '''
        return self.__player

    @property
    def isPlaying(self):
        '''Retourne l'état de jeu
        '''
        return self.__playing

    @property
    def isInit(self):
        '''Retourne l'état d'initialisation
        '''
        return self.__init


if __name__ == "__main__":

    fich_facile = "grille_easy1.sudo"
    valeurs = sudoio.sudoFichReadLines(fich_facile,1)
    print "Création et remplissage de la grille"
    gr = sudogrid.SudoGrid()
    gr.fillByRowLines(valeurs)
    print gr
    print "\nCréation du joueur"
    pl = sudoplayer.SudoPlayer()
    print pl
    print "\nCréation de la partie"
    game = SudoGame(pl,gr)
    print "game.player :"
    print game.player
    print "game.grid :"
    game.grid.show()

    
