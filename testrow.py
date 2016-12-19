# -*- coding: cp1252 -*-

from sudogrid import *

class CheckGrid(SudoGrid):
    
    def checkArgs(self, indx, bloc):
        '''v�rifie que les arguments index et bloc sont conformes aux r�gles
        de contruction et remplissage d'une grille.
        '''
        #indx doit �tre entre 1 et 9
        if not (1 <= indx <= 9):
            raise Exception \
                ("Grille sudo : indice doit �tre entre 1 et 9")
        #entrer des blocs de 9 chiffres exactement
        if len(bloc)!=9:
            raise Exception \
                ("Grille sudo : un rang doit faire exactement 9 cases\n")
        #v�rifier que toutes les valeurs sont entre 0 et 9 (0 = case vide)
        for i in bloc:
            if not (0<=i<=9):
                raise Exception \
                    ("Grille sudo : les valeurs doivent �tre entre 0 et 9")

                
                        
    def checkRow(self, iRow, rowBloc):
        '''v�rifie la r�gle d'unicit� pour l'insertion d'un rang entier
        '''
        pass

    def checkCol(self, iCol, colBloc):
        '''v�rifie la r�gle d'unicit� pour l'insertion d'un rang entier
        '''
        pass

    def checkSqr(self, iSqr, sqrBloc):
        '''v�rifie la r�gle d'unicit� pour l'insertion d'un rang entier
        '''
        pass

    def checkUnicity(self,bloc,otherVal=0):
        '''v�rifie la r�gle d'unicit� dans le contenu d'un bloc
        Si indiqu� v�rifie l'unicit� en incluant une nouvelle valeur
        '''
        vals=set()
        listbloc=list(bloc) #pour ne pas faire un append() interdit sur le bloc
        listbloc.append(otherVal)
        for val in listbloc:
            if val in vals:
                raise Exception \
                      ("La valeur " + str(val) + " n'est pas unique.")
            if val != 0:
                vals.add(val)
    
def test():
    bl = SudoBloc()
    print bl
    ch = CheckGrid()
    print ch


import fileinput

def sudoLireGrille(nomFich,grid):
#    with open(fich,"r") as fich:
#        read(fich)

    if not grid.isValidSudoGrid():
        raise Exception \
              ("'grid' n'est pas un objet SudoGrid valide")
    if nomFich == None:
        raise Exception \
              ('Pas de nom de fichier - Abandon')
##    except:
##        print("Lecture de fichier abandonn�e")
##        print("Fin")
##        return

#        fich = input(nomFich,'r')

    lineno = 1
    for line in fileinput.input(nomFich):
        if lineno>9:
            print("Le fichier contient trop de donn�es. Lecture interrompue.")
            print("La grille a �t� remplie.")
            break
        print "ligne", lineno,":", line
        grid.setRowLine(lineno,line,0)
        lineno = lineno+1
    

            
    

    
if __name__ == "__main__" :
    gr = SudoGrid()
    sudoLireGrille("grille_easy1.sudo", gr)
    print gr



