# -*- coding: cp1252 -*-

''' Programme HumaSudo
    R�solution humaine simul�e de Sudoku 
    Module sudomem : m�moire de jeu du joueur
'''

from sudoio import display
from sudorules import Sudoku_Error
import sudogrid


class SudoMemory():
    '''Cette classe repr�sente la m�moire de jeu d'un joueur, sa connaissance
    de la partie en cours. C'est l'accumulation des observations successives
    de la grille et la m�moire des cases remplies.
    '''

    def __init__(self):
        pass



if __name__ == '__main__':

    mem = SudoMemory()
    
