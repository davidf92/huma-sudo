# -*- coding: cp1252 -*-

''' Programme HumaSudo
    Résolution humaine simulée de Sudoku 
    Module sudoku : programme principal
'''

#from sudogrid import *
#from sudoplayer import *

import sudoplayer
import sudogrid
import sudoio
import sudogame
import sudorules as rules

class Sudoku(rules.SudoRules):
    '''Classe principale pour un jeu de simulation humaine de Sudoku
    '''

    def __init__(self):
        '''Crée les objets principaux : le joueur, la grille, la partie
        '''
        print "Création d'un joueur"
        self.___player = sudoplayer.SudoPlayer()
        
        print "Création d'une grille de jeu vide"
        self.__grid = sudogrid.SudoGrid()

    def createGame(self):
        self.__game = sodugame.SudoGame(self.__player,self.__grid)
                    

    
if __name__ == "__main__":

    print "Hello, jeu de Sudoku humain\n"

    print "Niveau : facile"
    fich_facile = "grille_easy1.sudo"

    valeurs = sudoio.sudoFichReadLines(fich_facile,1)
    
    print "\nValeurs à insérer dans la grille :"
    print valeurs

    print "\nCréation de la grille et remplissage"
    gr = sudogrid.SudoGrid()
    gr.fillByRowLines(valeurs)
    print gr
    print "\nReprésentation de la grille :"
    gr.show(3)

    print "\nCréation du joueur"
    pl = sudoplayer.SudoPlayer()
    print "La partie sera jouée par :", pl.name

    print "\nCréation de la partie"
    game = sudogame.SudoGame(pl,gr)

    
