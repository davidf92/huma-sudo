# -*- coding: cp1252 -*-
'''Programme SudoSimu - Module sudogrid - Contient les classes 'SudoGrid' et
'SudoBloc'.
Ces classes de bas niveau repr�sentent les objets du fondement du
programme, la grille de Sudoku. SudoGrid repr�sente une grille enti�re, alors
que SudoBloc repr�sente un 'bloc' de 9 chiffres devant �tre uniques, soit
un carr� 3x3, une ligne ou une colonne de la grille.
SudoGrid et SudoBloc d�rivent d'une classe SudoRules qui d�crit la seule r�gle
du Sudoku, l'unicit� de chaque chiffre dans chaque bloc.
'''

#Imports suivant que l'ex�cution est int�rieure ou ext�rieure au package
#Int�rieur : faire MAIN_TEST = True dans le module ex�cut�.
if __name__ in ("__main__", "sudogrid"):
    import sudorules as rules
elif __name__ == "sudosimu.sudogrid":
    from sudosimu import sudorules as rules
else:
    raise Exception("Impossible de faire les imports dans le module sudogrid.")


class SudoGrid(rules.SudoRules):
    '''Classe pour une grille de Sudoku de 9x9 qui respecte les r�gles
    d'unicit� des chiffres dans chaque rang, colonne et carr� 3x3.
    Les cases vides sont repr�sent�es par des 0
    '''
#TODO Ecrire la fonction coordToRC()
#TODO Ecrire la fonction placeSQ()
#TODO Ecrire la fonction placePLC()
    

    def __init__(self, showstyle=3):
        '''Cr�e une instance de grille Sudoku initialement vide.'''
        self.__rows = [SudoBloc() for i in range(9)]
        self.__cols = [SudoBloc() for i in range(9)]
        self.__sqrs = [SudoBloc() for i in range(9)]
        self.__isValidGrid = True
        self.__showStyle = showstyle

    def isValidSudoGrid(self):
        '''Permet de contr�ler que l'objet est bien une instance de SudoGrid
        est est correctement initialis�e.
        '''
        return self.__isValidGrid

    def isFull(self):
        '''Indique si la grille est termin�e.'''
##        #On teste si les 9 sqrs sont complets (identique avec rows ou cols)
##        for iRow in range(1,10):
##            if not (self.__rows[iRow-1].isFull()):
##                return False
##        return True
        return (self.nbEmpty() == 0)

    def nbVal(self):
        '''Retourne le nombre de cases occup�es de la grille.'''
        return 81 - self.nbEmpty()
##        nb = 0
##        for iSqr in range(1,10):
##            nb += self.__sqrs[iSqr-1].nbVal()
##        return nb

    def nbEmpty(self):
        '''Retourne le nombre de cases vides de la grille.'''
        nb = 0
        for iSqr in range(1,10):
            nb += self.__sqrs[iSqr-1].nbEmpty()
        return nb
    
    def valRC(self, iRow, iCol):
        '''Retourne la valeur de la case indiqu�e en coordonn�es RC.'''
        return self.__rows[iRow-1].val(iCol)

    def valSQ(self, iS, iQ):
        '''Retourne la valeur de la case indiqu�e en coordonn�es RC.'''
        return self.__sqrs[iS-1].val(iQ)

    def row(self,iRow):
        '''Retourne un objet Bloc contenant le rang demand�.'''
        if not 1<= iRow <=9:
            raise IndexError \
                  ("Erreur : indice doit �tre entre 1 et 9")
        return self.__rows[iRow-1]

    def col(self,iCol):
        '''etourne un objet Bloc contenant la colonne demand�e.'''
        if not 1<= iCol <=9:
            raise IndexError \
                  ("Erreur : indice doit �tre entre 1 et 9")
        return self.__cols[iCol-1]


    def sqr(self,iSqr):
        '''Retourne un objet Bloc contenant le carr� demand�e.'''
        if not 1<= iSqr <=9:
            raise IndexError \
                  ("Erreur : indice doit �tre entre 1 et 9")
        return self.__sqrs[iSqr-1]

    def copy(self):
        '''Retourne une copie identique de la grille.'''
        gr = SudoGrid()
        gr.copyFrom(self)
        return gr
            
    def placeRC(self, iRow, iCol, value, check=True):
        '''Place un chiffre sur la grille, ou efface (place un 0).
        Les coordonn�es sont donn�es en RC (row,col).
        Si c'est indiqu� v�rifier la validit� du placement (r�gles d'unicit�).
        '''
        #v�rifier les r�gles Sudoku si c'est demand�
        #validit� de la nouvelle valeur
                
        if (check is True):
            res = self.checkValRC(iRow, iCol, value)
            if not res:
                raise Sudoku_Error ("Ce chiffre est invalide dans cette case")

        #placer sur le rang, la colonne et le carr�
        self.__rows[iRow-1].place(iCol,value)
        self.__cols[iCol-1].place(iRow,value)
        iSqr, iPlc = self.coordToSQ(iRow,iCol) #obtenir les coordonn�es SQ
        self.__sqrs[iSqr-1].place(iPlc,value)
        return True #succ�s

    def placeSQ(self, iSqr, iPlc, value, check=True):
        '''Place un chiffre sur la grille ou efface (place un 0).
        Les coordonn�es sont donn�es en carr� (sqr,plc)
        Si c'est indiqu� v�rifier la validit� du placement (r�gles d'unicit�).
        '''
#TODO Fonction � �crire
        pass
    
    def placePLC(self, valPlc, check=True):
        '''Place un chiffre sur la grille ou efface (place un 0).
        Les coordonn�es  et la valeur sont indiqu�s en placement (spv)
        Si c'est indiqu� v�rifier la validit� du placement (r�gles d'unicit�).
        '''
#TODO Fonction � �crire
        pass
        
    def setRow(self, iRow, aList, check=True):
        '''Enregistre un rang entier de valeurs dans la grille.
        Les v�rifications peuvent �tre �vit�es avec un argument False.
        '''
        #Faire toutes les v�rifications avant de modifier la grille
        if check:
            self.checkCoord(iRow)
            self.checkAsBloc(aList)
            self.checkAsRow(iRow, aList, False) #arguments d�j� valid�s
        #Placer les valeurs de la liste une par une     
        for iCol in range(1,10):
            self.placeRC(iRow,iCol,aList[iCol-1],False) #v�rif d�j� faite
        return True     #succ�s

    def setRowBloc(self, iRow, aBloc, check=True):
        '''Enregistre un bloc comme rang de la grille. Les v�rifications
        peuvent �tre �vit�es avec un argument False.
        '''
        return self.setRow(iRow, aBloc.values, check)
        
    def setRowLine(self, iRow, aLine, check=True):
        '''Enregistre une chaine de caract�res comme nouveau rang.
        V�rifie si indiqu� que la ligne contient bien 9 chiffres.
        '''
        if check:
            if len(aLine) != 9:
                raise Sudoku_Error("La ligne doit faire 9 caract�res. Abandon")

        row = list()
        for i in range(9):
            row.append(int(aLine[i]))
        return self.setRow(iRow, row, check)
        
    def setCol(self, iCol, aList, check=True):
        '''Enregistre une colonne enti�re de valeurs dans la grille.
        Les v�rifications peuvent �tre �vit�es avec un argument False.
        '''
        #Faire toutes les v�rifications avant de modifier la grille
        if check:
            self.checkVal(iCol)
            self.checkAsBloc(aList)
            self.checkAsCol(iCol, aList, False) #arguments d�j� valid�s
        #Placer les valeurs de la liste une par une     
        for iRow in range(1,10):
            self.placeRC(iRow,iCol,aList[iRow-1],False) #v�rif d�j� faite
        return True     #succ�s

    def setSqr(self,iSqr, aList, check=True):
        ''' Enregistre un carr� entier dans la grille.
        Les v�rifications peuvent �tre �vit�es avec un argument False
        '''
        #Faire toutes les v�rifications avant de modifier la grille
        if check:
            self.checkVal(iSqr)
            self.checkAsBloc(aList)
            self.checkAsSqr(iSqr, aList, False) #arguments d�j� valid�s
        #Placer les valeurs de la liste une par une     
        for iPlc in range(1,10):
            self.placeSQ(iSqr,iPlc,aList[iPlc-1],False) #v�rif d�j� faite
        return True     #succ�s

    def copyFrom(self, aGrid):
        '''Remplit enti�rement une grille � partir d'une autre, donc en
        faisant une copie.
        '''
        #V�rifier que aGrid est une grille valide
        assert isinstance(aGrid, SudoGrid)
        #Il faut obligatoirement copier les valeurs une par une, ne pas faire
        #d'assignation de blocs qui ne seraient pas des copies.
        #Inutile de faire la v�rification d'int�grit�.
        for iRow in range(1,10):
            for iCol in range(1,10):
                self.placeRC(iRow, iCol, aGrid.valRC(iRow, iCol), False)
        return True
            
    def fillByRowLists(self, rowLists, check=True):
        '''Remplit enti�rement une grille avec une liste de listes rangs par
        rangs, soit 9 listes de 9 valeurs.
        '''
        if check:
#TODO Faire ici tous les tests sur la liste de donn�es
            pass

        iRow = 1
        for rowList in rowLists:
            if iRow>9:
                raise Sudoku_Error \
                      ("Trop de rangs dans la liste, " \
                       "lecture interrompue. La grille a �t� remplie.")
            self.setRow(iRow,rowList,False) #v�rifications d�j� faites
            iRow = iRow+1
        return True     #succ�s

    def fillByRowLines(self, rowLines, check=True):
        '''Remplit enti�rement une grille avec une liste de lignes de valeurs
        (en cha�nes de caract�res) rang par rang, soit 9 lignes de 9 car.
        '''
        if check:
#TODO Faire ici tous les tests sur la liste de donn�es
            pass

        iRow = 1
        for line in rowLines:
            if iRow>9:
                raise Sudoku_Error \
                      ("Trop de rangs dans la liste, " \
                       "lecture interrompue. La grille a �t� remplie.")
            self.setRowLine(iRow,line,False) #v�rifications d�j� faites
            iRow = iRow+1
        return True     #succ�s

    def checkAsRow(self, iRow, aList, check=True):
        '''V�rifie la validit� d'une liste pour �tre ins�r�e dans un rang
        Sauf refus, v�rifie d'abord la validit� de la liste comme Bloc.
        '''
        assert 1<=iRow<=9
        if check is True:
            self.checkCoord([iRow])
            self.checkAsBloc(aList)
        #v�rifier chaque valeur par rapport aux colonnes
        for iCol in range(1,10):
            if self.__cols[iCol-1].containsExcept(aList[iCol-1],iRow):
                raise Exception \
                      ("Le nouveau rang est incompatible avec la colonne ", \
                       iCol)
        #v�rifier chaque valeur par rapport aux carr�s,
        for iCol in range(1,10):
            coordS, coordQ = self.coordToSQ(iRow, iCol)
            if self.__sqrs[coordS-1].containsExcept(aList[iCol-1],coordQ-1):
                raise Exception \
                      ("Le nouveau rang est incompatible avec le carr� ", \
                       coordS)
            
    def checkValRC(self,iRow,iCol,value):
        ''' V�rifie qu'un chiffre est valide pour la case indiqu�e en RC
        '''
        assert 1<=iRow<=9 and 1<=iCol<=9 and 1<=value<=9
        #si c'est d�j� la valeur contenue, cas trivial
        if self.valRC(iRow,iCol) == value:
            return True
        if self.__rows[iRow-1].contains(value):
            return False                
        if self.__cols[iCol-1].contains(value):
            return False
        #passer en coordonn�es SQ
        iSqr = self.coordToSQ(iRow,iCol)[0] #premi�re valeur du couple retourn�
        if self.__sqrs[iSqr-1].contains(value):
            return False
        return True

    def checkValSQ(self,iSqr,iPlc,value):
        ''' V�rifie qu'un chiffre est valide pour la case indiqu�e en SQ
        '''
        assert 1<=iSqr<=9 and 1<=iPlc<=9 and 1<=value<=9
        #si c'est d�j� la valeur contenue, cas trivial
        if self.valSQ(iSqr,iPlc) == value:
            return True
        if self.__sqrs[iSqr-1].contains(value):
            return False
        #passer en coordonn�es RC
        iRow,iCol = self.coordToRC(iSqr,iPlc)
        if self.__rows[iRow-1].contains(value):
            return False                
        if self.__cols[iCol-1].contains(value):
            return False
        return True

##    def coordToSQ(self, iRow, iCol, check=True):
##        ''' retourne dans une liste les coordonn�es SQ pour RC indiqu�
##        La premi�re valeur est le num. du carr� dans la grille,
##        La seconde valeur est le num. de la case dans le carr�.
##        '''
##        if check:
##            if not self.checkCoordList([iRow,iCol]):
##                raise Exception \
##                      ("Les coordonn�es ", [iRow,iCol], " sont invalides")
##        iSqr = int( 1 + 3*((iRow-1)//3) + (iCol-1)//3 )
##        iPlc = int( 1 + 3*((iRow-1)%3)  + (iCol-1)%3  )
##        return iSqr, iPlc
##        
##    def coordToRC(self, iSqr,iPlc, check=True):
##        ''' retourne dans une liste les coordonn�es RC pour SQ indiqu�
##        La premi�re valeur est le rang, la seconde est la colonne
##        '''
##        if check:        
##            if not self.checkCoordList([iSqr,iPlc]):
##                raise Exception \
##                      ("Les coordonn�es ", [iSqr,iPlc], " sont invalides")
##        iRow = int( 1 + 3*((iSqr-1)//3) + (iPlc-1)//3 )
##        iCol = int( 1 + 3*((iSqr-1)%3)  + (iPlc-1)%3  )
##        return iRow, iCol

    def show(self,style=None):
        '''Retourne une repr�sentation tabulaire de la grille suivant le style
        indiqu�. Le contenu est retourn� sous forme d'une liste de lignes qui
        peut �tre imprim�e directement avec un �num�rateur
        '''
#TODO : Transformer show() et _showRow() pour retourner le texte
#       au lieu d'imprimer directement.
#       La fonction d'impression doit �tre dans le module 'sudoio' et non ici

        #style � utiliser
        if style == None:
            style = self.__showStyle
            
        #r�gler les s�parateurs de rangs suivant le style
        if   style == 1:
            topsep=""; rowsep="               "; botsep="";
        elif style == 2:
            topsep = rowsep = botsep = "-------------";
        elif style == 3:
            topsep = rowsep = botsep = "-------------------";
            
        else:
            topsep = rowsep = botsep = colsep = ""
            
        #bordure sup�rieure
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
        #bordure inf�rieure
        if len(botsep)!=0: print(botsep)
        

    def _showRow_(self, iRow, style):
        ''' Affiche un rang compact de 9 valeurs par blocs de 3
        avec le s�parateur indiqu� entre les blocs
        '''
        #r�gler les s�parateurs de colonnes suivant le style
        #ainsi que le caract�re pour une case vide (valeur 0)
        assert 1 <= iRow <= 9
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
        print (strRow)

#    @property
    def showStyle(self,style=None):
        '''Affiche ou Change le style d'affichage par la fonction show()
        '''
        if style == None:
            return self.__showStyle
        self.__showStyle = style

    def __str__(self):
        print("Classe SudoGrid : une grille Sudoku 9x9")
        print("Contenu de la grille :")
        strGrid = str(self.__rows[0])
        for iRow in range(1,9):
            strGrid = strGrid + "\n" + str(self.__rows[iRow])
        return(strGrid)
        

class SudoBloc(rules.SudoRules):
    '''Bloc de 9 chiffres ou vides selon les r�gles de Sudoku,
    Un bloc peut �tre utilis� comme rang, colonne ou carr� de grille Sudoku
    Une case vide est indiqu�e par une valeur 0
    Le bloc peut �tre initialis� � sa cr�ation avec une liste de 9 chiffres.
    Toutes les m�thodes v�rifient que les r�gles d'unicit� sont respect�es.
    '''

    def __init__(self, aList=None):
        '''Instancie un nouveau bloc, soit vide soit avec le contenu de la
        liste de chiffres pass�e en param�tre.
        '''
        self.__values = list()
        if aList==None:
            self.__values.extend(0 for i in range(9))
        else:
            self.fill(aList)

    def fill(self, aList):
        '''Remplit un bloc avec le contenu de la liste indiqu�e.'''
        self.__values = [aList[i] for i in range(9)]
        return self

    def place(self, idx, val):
        '''Place un chiffre dans un bloc � la place indiqu�e.'''
        self.__values[idx-1] = val
        return self

    def val(self, idx):
        '''Retourne la valeur contenue � l'index indiqu�.'''
        return self.__values[idx-1]
    
    def contains(self,val):
        '''Indique si un bloc contient le chiffre indiqu� (True/False)
        Retourne toujours 'False' pour la valeur 0. Utiliser isFull() pour
        savoir si un Bloc contient une valeur 0 = case vide.
        '''
        if val==0:
            return False
        for i in self.__values:
            if i==val :
                return True
        return False

    def containsExcept(self,val,idx):
        '''indique si un bloc contient le chiffre indiqu� ailleurs qu'�
        la case indiqu�e (True,False).
        Retourne toujours 'False' pour la valeur 0. Utiliser isFull() pour
        savoir si un Bloc contient une valeur 0 = case vide.
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
        '''Indique si un bloc est vide (True/False).'''
        for i in self.__values:
            if i>0: return False
        return True

    def isFull(self):
        '''Indique si un bloc est rempli, donc 9 chiffres (True/False).'''
        for i in self.__values:
            if i == 0:
                return False
            return True

    def nbVal(self):
        '''Retourne le nombre de chiffres pr�sents = valeurs non nulles.'''
        nb = 0
        for v in self.__values:
            if v != 0:
                nb += 1
        return nb

    def nbEmpty(self):
        '''Retourne le nombre de cases vides dans le bloc.'''
        return (9 - self.nbVal())
        
    def listPresent(self):
        '''Retourne la liste des chiffres pr�sents dans le bloc.'''
        lp = list()
        for i in range(9):
            v = self.__values[i]
            if v != 0:
                lp.append(v)
        return lp                

    def listAbsent(self):
        '''Retourne la liste des chiffres absents du bloc.'''
        la = list()
        for ch in range(1,10):
            if ch not in self.__values:
                la.append(ch)
        return la

    def listEmpty(self):
        '''Retourne la liste des positions des cases vides du bloc.'''
        return [i for i in range(1,10) if self.__values[i-1] == 0]

    def show(self):
        '''Affiche une repr�sentation du bloc.'''
        s = ""
        s_3 = 0
        for c in self.values:
            s = s + "." if c==0 else s+str(c)
            s_3 += 1
            if s_3 == 3:
                s = s + " "
                s_3 = 0
        print(s)

    @property
    def values(self):
        '''Retourne une liste du contenu du bloc sous forme de propri�t�.'''
        return [self.__values[i] for i in range(9)]

    def __str__(self):
        '''Retourne le contenu du bloc en format texte.'''
        print("Classe SudoBloc : un bloc Sudoku de 9 valeurs uniques,\n" \
              "en ligne, colonne ou carr� 3x3")
        print("Contenu du bloc :")
        return str(self.values) #une liste contenant les valeurs
    

##def sudotest():
##    gr = SudoGrid()
##    bl = SudoBloc()
##    list9 = [2,5,0,6,8,0,0,3,4]
##    import sudoio
##    vals = sudoio.sudoFichReadLines("grille_easy1.sudo")
##    print ("fichier lu :\n", vals)
##    gr.fillByRowLines(vals)
##    print(gr)
    
if __name__ == "__main__":
#    from sudorules import SudoRules as Rules
    print("Test du module sudogrid")
    print("-----------------------")
    gr = SudoGrid()
    bl = SudoBloc()
    vals = ['800500130', '502000007', '000008645', \
            '700064200', '081250094', '403009850', \
            '975486320', '008305479', '310702568']
    print("Contenu de la grille, par lignes de valeurs :\n" + str(vals))
    gr.fillByRowLines(vals)
    print("\nTest avec les objets : \ngr = instance SudoGrid, "\
          "avec gr.fillByRowLines( <lignes de valeurs> )"\
          "\nbl = instance SudoBloc, bl = gr.row(6)")
    print("\nConversion de SudoGrid en cha�ne de caract�res : str(gr) =")
    print(gr)
    print("\nm�thode SudoGrid.show() : ")
    gr.show()
    bl = gr.row(6)
    print("\nConversion de SudoBloc en cha�ne de caract�res : str(bl) = ")
    print(bl)
    print("\nm�thode SudoBloc.show() : ")
    bl.show()

        
