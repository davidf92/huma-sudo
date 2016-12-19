# -*- coding: cp1252 -*-

''' Programme HumaSudo
    Résolution humaine simulée de Sudoku 
    Module sudogrid : modélisation de la grille
'''

import sudorules as rules

class SudoGrid(rules.SudoRules):
    ''' Classe pour une grille de Sudoku de 9x9 qui respecte les règles
    d'unicité des chiffres dans chaque rang, colonne et carré 3x3.
    Les cases vides sont représentées par des 0
    '''
#TODO Ecrire la fonction coordToRC()
#TODO Ecrire la fonction placeSQ()
#TODO Ecrire la fonction placePLC()
    

    def __init__(self, showstyle=3):
        ''' Crée une instance de grille Sudoku initialement vide
        '''
        self.__rows = [SudoBloc() for i in range(9)]
        self.__cols = [SudoBloc() for i in range(9)]
        self.__sqrs = [SudoBloc() for i in range(9)]
        self.__isValidGrid = True
        self.__showStyle = showstyle

    def isValidSudoGrid(self):
        '''Permet de contrôler que l'objet est bien une instance de SudoGrid
        est est correctement initialisée
        '''
        return self.__isValidGrid
    
    def valRC(self, iRow, iCol):
        '''Retourne la valeur de la case indiquée en coordonnées RC
        '''
        return self.__rows[iRow-1].val(iCol)

    def valSQ(self, iS, iQ):
        '''Retourne la valeur de la case indiquée en coordonnées RC
        '''
        return self.__sqrs[iS-1].val(iQ)

    def row(self,iRow):
        ''' retourne un objet Bloc contenant le rang demandé
        '''
        if not 1<= iRow <=9:
            raise IndexError \
                  ("Erreur : indice doit être entre 1 et 9")
        return self.__rows[iRow-1]

    def col(self,iCol):
        ''' retourne un objet Bloc contenant la colonne demandée
        '''
        if not 1<= iCol <=9:
            raise IndexError \
                  ("Erreur : indice doit être entre 1 et 9")
        return self.__cols[iCol-1]


    def sqr(self,iSqr):
        ''' retourne un objet Bloc contenant le carré demandée
        '''
        if not 1<= iSqr <=9:
            raise IndexError \
                  ("Erreur : indice doit être entre 1 et 9")
        return self.__sqrs[iSqr-1]

    def placeRC(self, iRow, iCol, value, check=True):
        ''' place un chiffre sur la grille, ou efface (place un 0).
        Les coordonnées sont données en RC (row,col)
        Si c'est indiqué vérifier la validité du placement (règles d'unicité)
        '''
        #vérifier les règles Sudoku si c'est demandé
        #validité de la nouvelle valeur
                
        if (check is True):
            res = self.checkValRC(iRow, iCol, value)
            if not res:
                raise Sudoku_Error ("Ce chiffre est invalide dans cette case")

        #placer sur le rang, la colonne et le carré
        self.__rows[iRow-1].place(iCol,value)
        self.__cols[iCol-1].place(iRow,value)
        iSqr, iPlc = self.coordToSQ(iRow,iCol) #obtenir les coordonnées SQ
        self.__sqrs[iSqr-1].place(iPlc,value)
        return True #succès

    def placeSQ(self, iSqr, iPlc, value, check=True):
        '''Place un chiffre sur la grille ou efface (place un 0).
        Les coordonnées sont données en carré (sqr,plc)
        Si c'est indiqué vérifier la validité du placement (règles d'unicité)
        '''
#TODO Fonction à écrire
        pass
    
    def placePLC(self, valPlc, check=True):
        '''Place un chiffre sur la grille ou efface (place un 0).
        Les coordonnées  et la valeur sont indiqués en placement (spv)
        Si c'est indiqué vérifier la validité du placement (règles d'unicité)
        '''
#TODO Fonction à écrire
        pass
        
    def setRow(self, iRow, aList, check=True):
        ''' Enregistre un rang entier de valeurs dans la grille.
        Les vérifications peuvent être évitées avec un argument False
        '''
        #Faire toutes les vérifications avant de modifier la grille
        if check:
            self.checkCoord(iRow)
            self.checkAsBloc(aList)
            self.checkAsRow(iRow, aList, False) #arguments déjà validés
        #Placer les valeurs de la liste une par une     
        for iCol in range(1,10):
            self.placeRC(iRow,iCol,aList[iCol-1],False) #vérif déjà faite
        return True     #succès
    
    def setRowLine(self, iRow, aLine, check=True):
        '''Enregistre une chaine de caractères comme nouveau rang.
        Vérifie si indiqué que la ligne contient bien 9 chiffres.
        '''
        if check:
            if len(aLine) != 9:
                raise Sudoku_Error("La ligne doit faire 9 caractères. Abandon")

        row = list()
        for i in range(9):
            row.append(int(aLine[i]))
        return self.setRow(iRow, row, check)
        
    def setCol(self, iCol, aList, check=True):
        ''' Enregistre une colonne entière de valeurs dans la grille.
        Les vérifications peuvent être évitées avec un argument False
        '''
        #Faire toutes les vérifications avant de modifier la grille
        if check:
            self.checkVal(iCol)
            self.checkAsBloc(aList)
            self.checkAsCol(iCol, aList, False) #arguments déjà validés
        #Placer les valeurs de la liste une par une     
        for iRow in range(1,10):
            self.placeRC(iRow,iCol,aList[iRow-1],False) #vérif déjà faite
        return True     #succès

    def setSqr(self,iSqr, aList, check=True):
        ''' Enregistre un carré entier dans la grille.
        Les vérifications peuvent être évitées avec un argument False
        '''
        #Faire toutes les vérifications avant de modifier la grille
        if check:
            self.checkVal(iSqr)
            self.checkAsBloc(aList)
            self.checkAsSqr(iSqr, aList, False) #arguments déjà validés
        #Placer les valeurs de la liste une par une     
        for iPlc in range(1,10):
            self.placeSQ(iSqr,iPlc,aList[iPlc-1],False) #vérif déjà faite
        return True     #succès

    def fillByRowLists(self, rowLists, check=True):
        '''Remplit entièrement une grille avec une liste de listes rangs par
        rangs, soit 9 listes de 9 valeurs.
        '''
        if check:
#TODO Faire ici tous les tests sur la liste de données
            pass

        iRow = 1
        for rowList in rowLists:
            if iRow>9:
                raise Sudoku_Error \
                      ("Trop de rangs dans la liste, " \
                       "lecture interrompue. La grille a été remplie.")
            self.setRow(iRow,rowList,False) #vérifications déjà faites
            iRow = iRow+1
        return True     #succès

    def fillByRowLines(self, rowLines, check=True):
        '''Remplit entièrement une grille avec une liste de lignes de valeurs
        (en chaînes de caractères) rang par rang, soit 9 lignes de 9 car.
        '''
        if check:
#TODO Faire ici tous les tests sur la liste de données
            pass

        iRow = 1
        for line in rowLines:
            if iRow>9:
                raise Sudoku_Error \
                      ("Trop de rangs dans la liste, " \
                       "lecture interrompue. La grille a été remplie.")
            self.setRowLine(iRow,line,False) #vérifications déjà faites
            iRow = iRow+1
        return True     #succès

    def checkAsRow(self, iRow, aList, check=True):
        '''Vérifie la validité d'une liste pour être insérée dans un rang
        Sauf refus, vérifie d'abord la validité de la liste comme Bloc
        '''
        if check:
            self.checkCoord([iRow])
            self.checkAsBloc(aList)
        #vérifier chaque valeur par rapport aux colonnes
        for iCol in range(1,10):
            if self.__cols[iCol-1].containsExcept(aList[iCol-1],iRow):
                raise Exception \
                      ("Le nouveau rang est incompatible avec la colonne ", \
                       iCol)
        #vérifier chaque valeur par rapport aux carrés,
        for iCol in range(1,10):
            coordS, coordQ = self.coordToSQ(iRow, iCol)
            if self.__sqrs[coordS-1].containsExcept(aList[iCol-1],coordQ-1):
                raise Exception \
                      ("Le nouveau rang est incompatible avec le carré ", \
                       coordS)
            
    def checkValRC(self,iRow,iCol,value):
        ''' Vérifie qu'un chiffre est valide pour la case indiquée en RC
        '''
        #si c'est déjà la valeur contenue, cas trivial
        if self.valRC(iRow,iCol) == value:
            return True
        if self.__rows[iRow-1].contains(value):
            return False                
        if self.__cols[iCol-1].contains(value):
            return False
        #passer en coordonnées SQ
        iSqr = self.coordToSQ(iRow,iCol)[0] #première valeur du couple retourné
        if self.__sqrs[iSqr-1].contains(value):
            return False
        return True

    def checkValSQ(self,iSqr,iPlc,value):
        ''' Vérifie qu'un chiffre est valide pour la case indiquée en SQ
        '''
        #si c'est déjà la valeur contenue, cas trivial
        if self.valSQ(iSqr,iPlc) == value:
            return True
        if self.__sqrs[iSqr-1].contains(value):
            return False
        #passer en coordonnées RC
        iRow,iCol = self.coordToRC(iSqr,iPlc)
        if self.__rows[iRow-1].contains(value):
            return False                
        if self.__cols[iCol-1].contains(value):
            return False
        return True

    def coordToSQ(self,iRow,iCol, check=True):
        ''' retourne dans une liste les coordonnées SQ pour RC indiqué
        La première valeur est le num. du carré dans la grille,
        La seconde valeur est le num. de la case dans le carré.
        '''
        if check:
            if not self.checkCoordList([iRow,iCol]):
                raise Exception \
                      ("Les coordonnées ", [iRow,ICol], " sont invalides")
        iS = 1 + (iCol-1)/3 + 3*((iRow-1)/3)
        iQ = 1 + (iCol-1)%3 + 3*((iRow-1)%3)
        return iS, iQ
        
    def coordToRC(self,iSqr,iPlc):
        ''' retourne dans une liste les coordonnées RC pour SQ indiqué
        La première valeur est le rang, la seconde est la colonne
        '''
#TODO - Fonction à écrire !!!
        pass

    def show(self,style=None):
        '''Retourne une représentation tabulaire de la grille suivant le style
        indiqué. Le contenu est retourné sous forme d'une liste de lignes qui
        peut être imprimée directement avec un énumérateur
        '''
#TODO : Transformer show() et _showRow() pour retourner le texte
#       au lieu d'imprimer directement.
#       La fonction d'impression doit être dans le module 'sudoio' et non ici

        #style à utiliser
        if style == None:
            style = self.__showStyle
            
        #régler les séparateurs de rangs suivant le style
        if   style == 1:
            topsep=""; rowsep="               "; botsep="";
        elif style == 2:
            topsep = rowsep = botsep = "-------------";
        elif style == 3:
            topsep = rowsep = botsep = "-------------------";
            
        else:
            topsep = rowsep = botsep = colsep = ""
            
        #bordure supérieure
        if len(topsep)!=0: print(topsep)
        #rangs 1-3
        for iRow in range(1,4):
            self._showRow_(iRow,style)
        if len(rowsep)!=0: print(rowsep)
        #rangs 4-6
        for iRow in range(4,7):
            self._showRow_(iRow,style)
        if len(rowsep)!=0: print(rowsep)
        #rangs 7-9
        for iRow in range(7,10):
            self._showRow_(iRow,style)
        #bordure inférieure
        if len(botsep)!=0: print(botsep)
        

    def _showRow_(self, iRow, style):
        ''' Affiche un rang compact de 9 valeurs par blocs de 3
        avec le séparateur indiqué entre les blocs
        '''
        #régler les séparateurs de colonnes suivant le style
        #ainsi que le caractère pour une case vide (valeur 0)
        if   style == 1:
            leftsep=""; midsep="   "; rightsep=""; chrvide="."
        elif style == 2:
            leftsep = midsep = rightsep="|"; chrvide=" "
        elif style == 3:
            leftsep="| "; midsep=" | "; rightsep=" |"; chrvide=" "
        else:
            leftsep = midsep = rightsep = ""; chrvide = "."
            
        strRow = ""
        strRow = strRow + leftsep
        for iCol in range(1,10):
            val = self.__rows[iRow-1].val(iCol)
            if val == 0:
                strRow = strRow + chrvide
            else:
                strRow = strRow + str(val)
            if iCol in (3,6):
                strRow = strRow + midsep
        strRow = strRow + rightsep
        print strRow

#    @property
    def showStyle(self,style=None):
        '''Affiche ou Change le style d'affichage par la fonction show()
        '''
        if style == None:
            return self.__showStyle
        self.__showStyle = style

    def __str__(self):
        print("Classe SudoGrid : une grille Sudoku 9x9")
        print("Contenu actuel de la grille :")
        strGrid = str(self.__rows[0])
        for iRow in range(1,9):
            strGrid = strGrid + "\n" + str(self.__rows[iRow])
        return(strGrid)
        

class SudoBloc(rules.SudoRules):
    '''Bloc de 9 chiffres ou vides selon les règles de Sudoku,
    Un bloc peut être utilisé comme rang, colonne ou carré de grille Sudoku
    Une case vide est indiquée par une valeur 0
    Le bloc peut être initialisé à sa création avec une liste de 9 chiffres.
    Toutes les méthodes vérifient que les règles d'unicité sont respectées.
    '''

    def __init__(self, aList=None):
        '''Instancie un nouveau bloc, soit vide soit avec le contenu de la
        liste de chiffres passée en paramètre.
        '''
        self.__values = list()
        if aList==None:
            self.__values.extend(0 for i in range(9))
        else:
            self.fill(aList)

    def fill(self, aList):
        '''Remplit un bloc avec le contenu de la liste indiquée
        '''
        self.__values = [aList[i] for i in range(9)]
        return self

    def place(self, idx, val):
        '''Place un chiffre dans un bloc à la place indiquée
        '''
        self.__values[idx-1] = val
        return self

    def val(self, idx):
        '''Retourne la valeur contenue à l'index indiqué
        '''
        return self.__values[idx-1]
    
    def contains(self,val):
        '''Indique si un bloc contient le chiffre indiqué (True/False)
        Retourne toujours 'False' pour la valeur 0. Utiliser isFull() pour
        savoir si un Bloc contient une valeur 0 = case vide
        '''
        if val==0:
            return False
        for i in self.__values:
            if i==val :
                return True
        return False

    def containsExcept(self,val,idx):
        '''indique si un blic contient le chiffre indiqué ailleurs qu'à
        la case indiquée (True,False)
        Retourne toujours 'False' pour la valeur 0. Utiliser isFull() pour
        savoir si un Bloc contient une valeur 0 = case vide
        '''
        if val==0:
            return False
        for i in range(9):
            if i == idx-1:
                continue
            if self.__values[i] == val:
                return True
        return False
        
    def isEmpty(self):
        '''Indique si un bloc est vide (True/False)
        '''
        for i in self.__values:
            if i>0: return False
        return True

    def isFull(self):
        '''Indique si un bloc est rempli, donc 9 chiffres (True/False)
        '''
        for i in self.__values:
            if i == 0:
                return False
            return True

    def __str__(self):
        '''Imprime le bloc sous forme de liste (pour la fonction print)
        '''
        return str(self.values) #une liste contenant les valeurs
    
##        strList = list()
##        for val in self.__values:
##            strList.append(val)
##        return str(strList)
        
    def show(self):
        '''Imprime une description et le contenu du bloc
        '''
        print("Classe SudoBloc : un bloc Sudoku de 9 valeurs uniques,\n" \
              "en ligne, colonne ou carré 3x3")
        print("Contenu actuel du bloc :")
        print self

    @property
    def values(self):
        '''Retourne une liste du contenu du bloc sous forme de propriété
        '''
        return [self.__values[i] for i in range(9)]


if __name__ == "__main__":
    gr = SudoGrid()
    bl = SudoBloc()
    list9 = [2,5,0,6,8,0,0,3,4]
    import sudoio
    vals = sudoio.sudoFichReadLines("grille_easy1.sudo")
    print "fichier lu :\n", vals
    gr.fillByRowLines(vals)
    print gr
    

