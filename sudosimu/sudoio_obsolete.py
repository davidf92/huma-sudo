# -*- coding: cp1252 -*-

# programme HumaSudo
# résolution humaine simulée de Sudoku 

import fileinput
from sudosimu import sudorules
from sudosimu.sudorules import Sudoku_Error
from sudosimu import sudogrid
from sudosimu import sudogui as gui

STD = 1
GUI = 10
__uimode = STD    #le mode d'interface : standard ou graphique (défaut standard)
__gui = None        #l'objet d'interface graphique


##def UImode(mode=None, restoreGrid=True, grid=aGrid):
def UImode(mode=None):
    '''Fixe le nouveau mode d'interface utilisateur. S'il n'y a pas d'argument,
    retourne simplement le mode actif. Si le mode est GUI, affiche optionnellement
    le contenu actuel de la grille indiquée.
    '''
    global __gui
    global __uimode
    if mode is None:
        return __uimode
    elif mode == GUI:
        #créer l'interface graphique si ça n'est pas déjà fait
        if openGUI():
            __gui.activate()
            __uimode = GUI
##            if restoreGrid==True:
##                __gui._grid.displayAllGrid(aGrid)
    elif mode == STD:
        if isinstance(__gui, gui.SudoGUI):
            __gui.activate(False)
        __uimode = STD
    else:
        raise Sudoku_Error("Valeur de mode UI incorrecte")
    return

def openGUI(grid=None):
    '''Crée et ouvre la fenêtre l'interface GUI sans la rendre active. Si une
    grille est indiquée optionnellement, affiche son contenu.
    Retourne 'True' si la fenêtre est ouverte ou l'était déjà, sinon 'False'.
    '''
    global __gui
    if not isinstance(__gui, gui.SudoGUI):
        try:
            __gui = gui.SudoGUI()
        except:
            __gui = None
            __uimode = STD
            displayError("Interface utilisateur", \
                         "Impossible d'activer le mode graphique")
            return False
    if isinstance(grid, sudogrid.SudoGrid):
        __gui._grid.displayAllGrid(grid)

    return True
    
def closeGUI():
    '''Ferme la fenêtre graphique et repasse en mode d'interface texte.
    Il est possible de rouvrir une autre interface graphique plus tard mais
    le contenu de la précédente est perdu.
    '''
    global __gui
    global __uimode
    if isinstance(__gui, gui.SudoGUI):
        __gui.close()
        del(__gui)
        __gui = None
        __uimode = STD
    return
        
def display(text=None):
    '''Affiche du texte. Si le mode GUI est activé, affiche dans la fenêtre
    graphique, sinon affiche dans la sortie standard 'stdout'.
    '''
    if __uimode == GUI:
        #attention à ce que l'objet __gui n'ait pas été modifié        
        assert isinstance(__gui, gui.SudoGUI)
        __gui.activate()
        if text is None:
            __gui.displayText("\n")
        else:
            __gui.displayText(text+"\n")
    else:
        print(text)
    return

def displaySTD(text=None):
    '''Affiche du texte toujours dans la console STD quel que soit le mode UI.'''
    print(text)
    return
    
def displayError(title, text=None):
    display("Erreur : {0}".format(title))
    if text is not None:
        display(text)
    return

def displayGridValue(row, col, val):
    '''Affiche une valeur sur la grille graphique, si le mode GUI est actif.'''
    global __gui
    global __uimode
    if __uimode == GUI and isinstance(__gui._grid, gui.SudoGuiGrid):
        if not val==0:
            __gui._grid.place(row, col, val)
    return
    
def displayGridPlace(grid, row, col):
    '''Affiche une valeur de la grille sudo sur la grille GUI, si le mode GUI
    est actif.
    '''
    assert isinstance(grid, sudogrid.SudoGrid)
    global __gui
    global __uimode
    if __uimode == GUI and isinstance(__gui._grid, gui.SudoGuiGrid):
        val = grid.valRC(row, col)
        if not val==0:
            __gui._grid.place(row, col, val)
    return

def displayGridAll(grid):
    '''Affiche la totalité d'une grille sur le canvas GUI.'''
    assert isinstance(grid, sudogrid.SudoGrid)
    global __uimode
    if __uimode == GUI and isinstance(__gui._grid, gui.SudoGuiGrid):
        for row in range(1,10):
            for col in range(1,10):
                displayGridPlace(grid, row, col)
    return

def displayGridRemove(row, col):
    '''Efface une valeur de la grille sur le canvas GUI, si le mode GUI
    est actif.
    '''
    global __gui
    global __uimode
    if __uimode == GUI:
        __gui._grid.remove(row, col)
    return

def displayGridClear():
    '''Efface toutes les valeurs de la grille du canvas GUI.'''
    global __gui
    global __uimode
    if __uimode == GUI and isinstance(__gui._grid, gui.SudoGuiGrid):
        __gui._grid.clear()
    
def sudoFichReadLines(nomFich, pr=False):
    '''Lecture d'un fichier texte de grille dans le répertoire courant.
    Le fichier doit contenir exactement 9 lignes de caractères numériques.
    Le texte doit être présenté ligne par ligne en 9 x 9 chiffres. Les
    cases vides doivent être représentées par des zéros.
    Retourne une liste de 9 chaînes de 9 caractères numériques.
    '''
    return _sudoFichGrid_(nomFich, 1, pr)

def sudoFichReadLists(nomFich, pr=False):
    '''Lecture d'un fichier texte de grille dans le répertoire courant.
    Le fichier doit contenir exactement 9 lignes de caractères numériques.
    Le texte doit être présenté ligne par ligne en 9 x 9 chiffres. Les
    cases vides doivent être représentées par des zéros.
    Retourne une liste de 9 listes de 9 caractères numériques.
    '''
    return _sudoFichGrid_(nomFich, 2, pr)

def _sudoFichGrid_(nomFich, mode, pr=False):
    '''Lit le fichier de caractères et fait les vérifications.
    Si mode = 1 (défaut) : retourne une liste de lignes
    Si mode = 2 : retourne une liste de listes
    '''
    if nomFich == None:
        raise Sudoku_Error \
              ("Pas de nom de fichier - Abandon")
    if mode not in (1,2):
        raise Sudoku_Error ("Mode de lecture de fichier invalide")
    
    if pr:
        display("Lecture du fichier ", nomFich, " :")
    listLines = list()
    lineno = 0
    try:
        for line in fileinput.input(nomFich):
            #si la ligne commence par # l'ignorer
            if line[0] == '#':
                continue
            #erreur s'il y a plus de 9 lignes valides dans le fichier
            if lineno > 9:
                raise Sudoku_Error \
                      ("Le fichier contient trop de données. Lecture "\
                       "interrompue. La grille a été remplie.")
            #vérifier les caractères et rectifier les vides
            line2 = ""
            for c in line:
                #ignorer les espaces
                if c == ' ':
                    continue
                #traiter les équivalents à l'absence de chiffre
                if c in ('0', '.', '-', '_'):
                    line2 = line2 + '0'
                #accepter uniquement de '1' à '9'
                elif str(0) <= str(c) <= str(9):
                    line2 = line2 + str(c)
                #fin de la ligne ignorer le '\n' final
                elif c == '\n':
                    break
                else:
                    raise Sudoku_Error \
                          ("caractère invalides dans la ligne : " + line)
            #si la ligne est complètement blanche passer à la suivante
            #sans la compter
            if len(line2) == 0:
                continue
            #erreur si la ligne contient plus ou moins de 9 chiffres
            if len(line2) != 9:
                raise Sudoku_Error \
                      ("la ligne" + str(lineno) + " : " + line2 + \
                       " ne contient pas exactement 9 chiffres. ")
            #ok, la ligne est valide - Ajout à la liste
            if mode == 1:                   #mode liste de lignes
                listLines.append(line2)
            elif mode == 2:                 #mode liste de listes
                listeval = list()
                for c in line2:
                    listeval.append(int(c))
                listLines.append(listeval)
            else:
                raise Sudoku_Error ("Mode de lecture de fichier invalide")

            lineno = lineno + 1
            if pr:
                display("ligne" + str(lineno) + " : " + line2)
        #end for
    except FileNotFoundError:
        raise Sudoku_Error ("Fichier invalide ou n'existe pas")
        return None
    finally:
        fileinput.close()
        
    #erreur s'il y a eu moins de 9 lignes valides dans le fichier
    if lineno < 9:
        raise Sudoku_Error \
              ("Erreur de lecture, le fichier contient moins de 9 lignes "\
               "de chiffres.")

    #ok, retourne la liste des 9 lignes de 9 chiffres
    if pr:
        display("Ok, 9 lignes de 9 chiffres.")
    return listLines
    

def sudoNomTestFich():

    try:
        nomFich = input("Nom du fichier de grille de test ?")
    except KeyboardInterrupt:
        display("Abandon.")
        return
    if nomFich == "":
        nomFich = "grille_test.sudo"
    return nomFich
    
def sudoNumTestFich(racine="grille_test"):
    '''Demande sur la console un numéro de fichier et retourne
    un nom de fichier formé d'une racine fixe et du numéro donné.
    Gère les erreurs d'input. Abandon avec Ctrl-C
    '''
    while True:
        try:
            inpNum = input("Entrer le numéro du fichier de grille de test" \
                            + " (Ctrl-C pour quitter) ?")
        except KeyboardInterrupt:
            return None
        if inpNum == "":
            strNum = ""
        else:
            try:
                num = int(inpNum)
            except ValueError:
                display("Erreur. Entrer un numéro entier positif ou <vide> " \
                        "pour le fichier par défaut.")
                continue
            if num < 0:
                display("Erreur. Entrer un numéro positif")
                continue
            elif num == 0:
                strNum = ""
            else:
#                strNum = "_" + str(num)
                strNum = "_" + inpNum
        break
    fich = racine + strNum + ".sudo"
    return fich    

def sudoPause(continuer=False):
    '''Interrompt l'exécution jusqu'à une confirmation de l'utilisateur.
    (utilise la console stdin)
    '''
    try:
        s = input("Tapez ENTREE pour continuer...")
        return(True)
    except EOFError:
        if continuer:
            return(None)
        else:
            raise Sudoku_Error("Exécution interrompue volontairement.")
    except KeyboardInterrupt:
        if continuer:
            return(False)
        else:
            raise Sudoku_Error("Exécution interrompue volontairement.")



#TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST


def testIO():
    
    #test de sudoPause
    print("Test de la fonction sudoio.sudoPause()")
    for i in range(10):
        r = sudoPause()
        if r==True:
            print("ok pour continuer")
            continue
        elif r==False:
            print("Ctrl-C, interruption")
            break
        elif r==None:
            print("Ctrl-D, fin de l'essai")
            break
        else:
            print("...?")
            break

#test noms de fichiers
def testFich():
    '''test lecture fichier avec input simple sans contrôle
    '''
    while True:
        try:
            nomFich = input("Nom du fichier de grille ?")
        except KeyboardInterrupt:
            print("Fin")
            break
        if nomFich == "":
            continue
        sudoFichReadLines(nomFich, True)
#end def testFich() 

#test complet nom de fichier + lecture
def testFich2():
    '''test complet nom de fichier contrôlé + lecture du fichier
    '''
    while True:
        fich = sudoNumTestFich()
        if not fich:
            break
        print("Fichier choisi : " + fich)
        try:
            l = sudoFichReadLines(fich, True)
##        except Sudoku_Error:
##            print("Erreur de lecture ou fichier n'existe pas. Recommencer...")
##            continue
        finally:
            pass
        print(l)
        if not sudoPause(): print("Fin"); break
#end def testFich2()
    
if __name__ == "__main__":
    #testIO()
    #testFich()
    #testFich2()
    pass
