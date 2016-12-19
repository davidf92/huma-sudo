# -*- coding: cp1252 -*-

''' Programme HumaSudo
    Résolution humaine simulée de Sudoku
    Module sudothinking : raisonnement de résolution par le joueur
'''

import sudoio
import sudorules as rules

class SudoThinking():
    '''Cette classe encapsule les méthodes de raisonnement de résolution
    d'une grille de Sudoku.
