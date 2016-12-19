# -*- coding: cp1252 -*-

''' Programme HumaSudo
    R�solution humaine simul�e de Sudoku 
    Module sudogame : gestion d'une partie
'''

import sudoplayer
import sudogrid
import sudoio
import sudorules as rules
from sudorules import Sudoku_Error

class SudoGame():
    '''Cette classe g�re les parties
    Chaque instance r�soud une partie d'un joueur avec une grille.
    Quand la partie est gagn�e ou abandonn�e, l'instance est tu�e.
    Au cours de la partie, le joueur peut gagner en exp�rience , ce qui lui
    servira pour ses parties suivantes.
    '''

    def __init__(self, player=None, grid=None):
        '''Cr�e une partie. Enregistre le joueur et la grille s'ils sont
        indiqu�s lors de l'instantiation
        '''
#Comment v�rifier que 'player' et 'grid' sont de la bonne classe,
#et si non d�clencher une exception de type ?
        self.__player = player
        self.__grid = self.__startGrid = grid
        self.__playing = False
        self.__init = (grid == None and player == None)

    def newGrid(self, grid=None):
        '''Propose une nouvelle grille au m�me joueur
        '''
        #v�rifications
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
        Permet de jouer une m�me grille avec diff�rents joueurs
        '''
        if player == None:
            raise Sudoku_Error("Nouvelle partie mais pas de joueur :")
        #si une partie est en cours, l'arr�ter
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
        '''Annule une partie mais garde le m�me joueur et la m�me grille
        de d�part.
        '''
        if self.__playing:
            self.__grid = self.__startGrid
            self.__playing = False

    def reinit(self):
        '''R�initialise compl�tement l'instance, sans joueur ni grille
        Equivalent � instancier la classe sans fournir d'arguments
        '''
        self.__grid = None
        self.__startGrid = None
        self.__player = None
        self.__playing = False
        self.__init = False
        
    @property
    def grid(self):
        '''Retourne la grille dans son �tat actuel du jeu
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
        '''Retourne l'�tat de jeu
        '''
        return self.__playing

    @property
    def isInit(self):
        '''Retourne l'�tat d'initialisation
        '''
        return self.__init


if __name__ == "__main__":

    fich_facile = "grille_easy1.sudo"
    valeurs = sudoio.sudoFichReadLines(fich_facile,1)
    print "Cr�ation et remplissage de la grille"
    gr = sudogrid.SudoGrid()
    gr.fillByRowLines(valeurs)
    print gr
    print "\nCr�ation du joueur"
    pl = sudoplayer.SudoPlayer()
    print pl
    print "\nCr�ation de la partie"
    game = SudoGame(pl,gr)
    print "game.player :"
    print game.player
    print "game.grid :"
    game.grid.show()

    
