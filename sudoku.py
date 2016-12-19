# -*- coding: cp1252 -*-

''' Programme HumaSudo
    R�solution humaine simul�e de Sudoku 
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
        '''Cr�e les objets principaux : le joueur, la grille, la partie
        '''
        print "Cr�ation d'un joueur"
        self.___player = sudoplayer.SudoPlayer()
        
        print "Cr�ation d'une grille de jeu vide"
        self.__grid = sudogrid.SudoGrid()

    def createGame(self):
        self.__game = sodugame.SudoGame(self.__player,self.__grid)
                    

    
if __name__ == "__main__":

    print "Hello, jeu de Sudoku humain\n"

    print "Niveau : facile"
    fich_facile = "grille_easy1.sudo"

    valeurs = sudoio.sudoFichReadLines(fich_facile,1)
    
    print "\nValeurs � ins�rer dans la grille :"
    print valeurs

    print "\nCr�ation de la grille et remplissage"
    gr = sudogrid.SudoGrid()
    gr.fillByRowLines(valeurs)
    print gr
    print "\nRepr�sentation de la grille :"
    gr.show(3)

    print "\nCr�ation du joueur"
    pl = sudoplayer.SudoPlayer()
    print "La partie sera jou�e par :", pl.name

    print "\nCr�ation de la partie"
    game = sudogame.SudoGame(pl,gr)

    
