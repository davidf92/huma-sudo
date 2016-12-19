# -*- coding: cp1252 -*-

''' Programme HumaSudo
    Résolution humaine simulée de Sudoku 
    Module sudomem : mémoire de jeu du joueur
'''

from sudoio import display
from sudorules import Sudoku_Error
import sudogrid


class SudoMemory():
    '''Cette classe représente la mémoire de jeu d'un joueur, sa connaissance
    de la partie en cours. C'est l'accumulation des observations successives
    de la grille et la mémoire des cases remplies.
    '''

    def __init__(self):
        pass



if __name__ == '__main__':

    mem = SudoMemory()
    
