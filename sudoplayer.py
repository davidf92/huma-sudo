# -*- coding: cp1252 -*-

''' Programme HumaSudo
    Résolution humaine simulée de Sudoku 
    Module sudoplayer : Classes qui gèrent les joueurs
'''

import sudoio
import sudorules
import sudogrid

class SudoPlayer():
    ''' Classe qui simule un joueur.
    '''

    def __init__(self, name="joueur"):
        '''initialise le nouveau joueur. Par défaut son nom est 'joueur'
        '''
        self.setname(name)

    def setname(self, name="joueur"):
        '''change le nom du joueur
        '''
        self.__name = name
        
    @property
    def name(self):
        '''retourne le nom du joueur
        '''
        return(self.__name)

    def __str__(self):
        return("Le joueur : '" + self.name + "'")

            


# if __name__ == '__main__':
    
