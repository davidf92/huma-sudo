# -*- coding: cp1252 -*-

''' Programme HumaSudo
    R�solution humaine simul�e de Sudoku
    
    Module sudorules - Contient :
    - classe SudoRule() : r�gles de remplissage de grille Sudoku
    - classe SudoException() : exceptions aux r�gles de Sudoku
    
'''

class SudoRules():
    '''Cette classe abstraite impl�mente les prod�cures de v�rification des
    r�gles de Sudoku : les coordonn�es et les valeurs de 1 � 9 ainsi que
    les r�gles d'unicit� ligne/colonne/carr�.
    Egalement les r�gles de transformation de rep�res de coordonn�es
    Les classes Bloc et Grid d�rivent de cette classe.
    '''

    def checkVal(self,value):
        ''' V�rifie la validit� d'une valeur de chiffre entre 0 et 9
        '''
        if not 0<=value<=9:
            raise Sudoku_Error \
                  ("La valeur '" + str(value) + "' est invalide.")
        return True

    def checkCoord(self,coord):
        '''V�rifie la validit� d'une coordonn�e entre 1 et 9
        '''
        self.checkCoordList((coord,))
        return True
        
##    def checkCoordList(coordList):
##        ''' V�rifie une liste de coordonn�es de grille entre 1 et 9
##        '''
##        for iCoord in coordList:
##            if not 1<=iCoord<=9:
##                raise Sudoku_Error \
##                      ("La coordonn�e '" + str(iCoord) + "' est invalide.")
##        return True

    def checkCoordList(self,coordList):
        ''' V�rifie une liste de coordonn�es de grille entre 1 et 9
        '''
        for iCoord in coordList:
            if not 1<=iCoord<=9:
                raise Sudoku_Error \
                      ("La coordonn�e '" + str(iCoord) + "' est invalide.")
        return True

    def checkCoordVal(self, coordList, value):
        '''V�rifie la validit� des coordonn�es (entre 1 et 9) et de la valeur
        (entre 0 et 9)
        '''
        try:
            self.checkVal(value)
            self.checkCoordList(coordList)
            return True
        finally:
            pass

    def checkValBloc(self, aValue, aBloc):
        '''V�rifie qu'une valeur est valide et unique par rapport au contenu
        d'un bloc
        '''
        self.checkVal(self, aValue)
        if aBloc.contains(aValue):
            raise Sudoku_Error \
                  ("Le bloc ", aBloc.values, " contient d�j� la valeur ", \
                  aValue)
        return True

    def checkAsBloc(self, aList, aValue=0):
        '''V�rifie la validit� d'une liste de chiffres par rapport aux r�gles,
        pour que cette liste soit utilis�e comme Bloc.
        V�rifie aussi la validit� d'unicit� d'une nouvelle valeur par rapport
        � la liste.
        '''
        #la liste doit contenir exactement 9 valeurs
        if not len(aList) == 9:
            raise Sudoku_Error \
                  ("La longuer de la liste " + aList + " est diff�rente de 9")

        #les valeurs doivent �tre toutes entre 0 et 9
        for val in aList:
            if not self.checkVal(val):
                return False

        #les valeurs non nulles doivent �tre toutes uniques entre elles,
        #incluant une autre valeur pass�e en param�tre
        vals=set()
        aList.append(aValue)
        for val in aList:
            if val in vals:
                raise Sudoku_Error \
                      ("La valeur " + str(val) + " n'est pas unique.")
            if val != 0:
                vals.add(val)
        return True

##    def coordToSQ(iRow, iCol, check=True):
##        ''' retourne dans une liste les coordonn�es SQ pour RC indiqu�
##        La premi�re valeur est le num. du carr� dans la grille,
##        La seconde valeur est le num. de la case dans le carr�.
##        '''
##        if check:
##            if not SudoRules.checkCoordList([iRow,iCol]):
##                raise Exception \
##                      ("Les coordonn�es ", [iRow,iCol], " sont invalides")
##        iSqr = int( 1 + 3*((iRow-1)//3) + (iCol-1)//3 )
##        iPlc = int( 1 + 3*((iRow-1)%3)  + (iCol-1)%3  )
##        return iSqr, iPlc
        
    def coordToSQ(self, iRow, iCol, check=True):
        ''' retourne dans une liste les coordonn�es SQ pour RC indiqu�
        La premi�re valeur est le num. du carr� dans la grille,
        La seconde valeur est le num. de la case dans le carr�.
        '''
        if check:
            if not self.checkCoordList([iRow,iCol]):
                raise Exception \
                      ("Les coordonn�es ", [iRow,iCol], " sont invalides")
        iSqr = int( 1 + 3*((iRow-1)//3) + (iCol-1)//3 )
        iPlc = int( 1 + 3*((iRow-1)%3)  + (iCol-1)%3  )
        return iSqr, iPlc
        
    def coordToRC(self, iSqr,iPlc, check=True):
        ''' retourne dans une liste les coordonn�es RC pour SQ indiqu�
        La premi�re valeur est le rang, la seconde est la colonne
        '''
        if check:        
            if not self.checkCoordList([iSqr,iPlc]):
                raise Exception \
                      ("Les coordonn�es ", [iSqr,iPlc], " sont invalides")
        iRow = int( 1 + 3*((iSqr-1)//3) + (iPlc-1)//3 )
        iCol = int( 1 + 3*((iSqr-1)%3)  + (iPlc-1)%3  )
        return iRow, iCol

    def ruleCoordToRC(iSqr,iPlc, check=True):
        '''M�thode de classe.
        Retourne dans une liste les coordonn�es RC pour SQ indiqu�
        La premi�re valeur est le rang, la seconde est la colonne
        '''
##        if check:        
##            if not self.checkCoordList([iSqr,iPlc]):
##                raise Exception \
##                      ("Les coordonn�es ", [iSqr,iPlc], " sont invalides")
        iRow = int( 1 + 3*((iSqr-1)//3) + (iPlc-1)//3 )
        iCol = int( 1 + 3*((iSqr-1)%3)  + (iPlc-1)%3  )
        return iRow, iCol


    def ruleCoordToSQ(iRow, iCol, check=True):
        '''M�thode de classe.
        Retourne dans une liste les coordonn�es SQ pour RC indiqu�
        La premi�re valeur est le num. du carr� dans la grille,
        La seconde valeur est le num. de la case dans le carr�.
        '''
##        if check:
##            if not self.checkCoordList([iRow,iCol]):
##                raise Exception \
##                      ("Les coordonn�es ", [iRow,iCol], " sont invalides")
        iSqr = int( 1 + 3*((iRow-1)//3) + (iCol-1)//3 )
        iPlc = int( 1 + 3*((iRow-1)%3)  + (iCol-1)%3  )
        return iSqr, iPlc
        

class Sudoku_Error(Exception):
    '''D�finit l'ensemble d'exceptions aux r�gles de Sudoku
    En pratique pour le moment, sert uniquement � afficher le nom de cette
    classe d'exceptions, ce qui est plus explicite.
    '''
##    def __init__(self, arg):
##        self.args = arg
    pass
