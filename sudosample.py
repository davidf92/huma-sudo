# -*- coding: cp1252 -*-

''' Programme HumaSudo
    Résolution humaine simulée de Sudoku 
    Module sudogrid : modélisation de la grille
'''

from sudoio import display
from sudogrid import *

def makeSample(sd):
    ''' Initialise une grille avec un exemple du niveau indiqué
    Le niveau peut être "facile", "moyen", "difficile", expert"
    '''
    #entrer le contenu de la grille rang par rang
    sd.enterRow(1,[3,7,0,0,0,0,0,4,2])
    sd.enterRow(2,[2,9,0,8,0,6,7,0,1])
    sd.enterRow(3,[0,0,4,2,0,0,9,0,0])

    sd.enterRow(4,[7,0,0,0,0,0,0,0,0])
    sd.enterRow(5,[0,5,2,0,7,1,0,6,8])
    sd.enterRow(6,[6,0,8,0,2,5,4,0,9])

    sd.enterRow(7,[0,2,1,7,0,3,6,8,4])
    sd.enterRow(8,[0,4,3,6,0,2,5,9,7])
    sd.enterRow(9,[9,0,7,5,8,4,2,0,3])
    
    print sd


class SudoSample(SudoGrid):
    '''Une classe qui fournit une grille d'exemple de niveau facile
    '''

    def __init__(self,level):
        '''crée l'instance de classe d'exemple
        '''
        try:
            if level == "facile":
                print("Création d'une grille niveau 'facile'")
                self.enterRow(1,[3,7,0,0,0,0,0,4,2])
                self.enterRow(2,[2,9,0,8,0,6,7,0,1])
                self.enterRow(3,[0,0,4,2,0,0,9,0,0])

                self.enterRow(4,[7,0,0,0,0,0,0,0,0])
                self.enterRow(5,[0,5,2,0,7,1,0,6,8])
                self.enterRow(6,[6,0,8,0,2,5,4,0,9])

                self.enterRow(7,[0,2,1,7,0,3,6,8,4])
                self.enterRow(8,[0,4,3,6,0,2,5,9,7])
                self.enterRow(9,[9,0,7,5,8,4,2,0,3])
            elif level == "moyen":
                print("Uniquement le niveau 'facile' pour le moment.")
            elif level == "difficile":
                print("Uniquement le niveau 'facile' pour le moment.")
            elif level == "expert":
                print("Uniquement le niveau 'facile' pour le moment.")
            else:
                print("Paramètre '" + str(level) + "' invalide.")
                raise Exception \
                     ("Indiquer un niveau : facile, moyen, difficile ou expert")
        finally:
            pass


        
def test():
    print "Préparation d'une grille d'exemple
    smp = SudoGrid()
    print smp
    makeSample(smp)
    print(smp)
    smp.show(3)

if __name__ == "__main__":
    test()
    
