# -*- coding: cp1252 -*-

''' Programme HumaSudo
    Résolution humaine simulée de Sudoku
    
    Module sudorules - Contient :
    - classe SudoRule() : règles de remplissage de grille Sudoku
    - classe SudoException() : exceptions aux règles de Sudoku
    
'''

class SudoRules():
    '''Cette classe abstraite implémente les prodécures de vérification des
    règles de Sudoku : les coordonnées et les valeurs de 1 à 9 ainsi que
    les règles d'unicité ligne/colonne/carré.
    Les classes Bloc et Grid dérivent de cette classe.
    '''

    def checkVal(self,value):
        ''' Vérifie la validité d'une valeur de chiffre entre 0 et 9
        '''
        if not 0<=value<=9:
            raise Sudoku_Error \
                  ("La valeur '" + str(value) + "' est invalide.")
        return True

    def checkCoord(self,coord):
        '''Vérifie la validité d'une coordonnée entre 1 et 9
        '''
        self.checkCoordList((coord,))
        return True
        
    def checkCoordList(self,coordList):
        ''' Vérifie une liste de coordonnées de grille entre 1 et 9
        '''
        for iCoord in coordList:
            if not 1<=iCoord<=9:
                raise Sudoku_Error \
                      ("La coordonnée '" + str(iCoord) + "' est invalide.")
        return True

    def checkCoordVal(self, coordList, value):
        '''Vérifie la validité des coordonnées (entre 1 et 9) et de la valeur
        (entre 0 et 9)
        '''
        try:
            self.checkVal(value)
            self.checkCoordList(coordList)
            return True
        finally:
            pass

    def checkValBloc(self, aValue, aBloc):
        '''Vérifie qu'une valeur est valide et unique par rapport au contenu
        d'un bloc
        '''
        self.checkVal(self, aValue)
        if aBloc.contains(aValue):
            raise Sudoku_Error \
                  ("Le bloc ", aBloc.values, " contient déjà la valeur ", \
                  aValue)
        return True

    def checkAsBloc(self, aList, aValue=0):
        '''Vérifie la validité d'une liste de chiffres par rapport aux règles,
        pour que cette liste soit utilisée comme Bloc.
        Vérifie aussi la validité d'unicité d'une nouvelle valeur par rapport
        à la liste.
        '''
        #la liste doit contenir exactement 9 valeurs
        if not len(aList) == 9:
            raise Sudoku_Error \
                  ("La longuer de la liste " + aList + " est différente de 9")

        #les valeurs doivent être toutes entre 0 et 9
        for val in aList:
            if not self.checkVal(val):
                return False

        #les valeurs non nulles doivent être toutes uniques entre elles,
        #incluant une autre valeur passée en paramètre
        vals=set()
        aList.append(aValue)
        for val in aList:
            if val in vals:
                raise Sudoku_Error \
                      ("La valeur " + str(val) + " n'est pas unique.")
            if val != 0:
                vals.add(val)
        return True


class Sudoku_Error(Exception):
    '''Définit l'ensemble d'exceptions aux règles de Sudoku
    En pratique pour le moment, sert uniquement à afficher le nom de cette
    classe d'exceptions, ce qui est plus explicite.
    '''
##    def __init__(self, arg):
##        self.args = arg
    pass
