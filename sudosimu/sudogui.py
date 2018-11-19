# -*- coding: cp1252 -*-

# programme HumaSudo
# résolution humaine simulée de Sudoku 

if __name__ in ("__main__", "sudogui"):
    import sudorules
    from sudorules import Sudoku_Error
elif __name__ == "sudosimu.sudogui":
    from sudosimu import sudorules
    from sudosimu.sudorules import Sudoku_Error
else:
    raise Exception("Impossible de faire les imports dans le module sudogui.")
import tkinter as tk
import tkinter.tix as tix


class SudoGUI():
    '''Classe d'interface graphique pour le programe. Cette classe fournit
    des méthodes d'affichage et d'input standardisées qui permettent la même
    interaction que dans un autre mode d'interface;
    '''
    def __init__(self):
        self._openGUI()
        self._open = True
        self._active = False
        
    def _openGUI(self):
        '''Ouvre une fenêtre graphique.
        Dans cette version ce n'est pas réellement une application Python, la
        fenêtre ne fonctionne qu'à travers un shell Python (ex: IDLE). Il n'y
        a pas d'appel de mainloop().
        '''
        #fenêtre graphique et top frame
        self._gui = tix.Tk()
        self._gui.title("HumaSudo - Sudoku humain")
        self._ftop = tix.Frame(self._gui, bg="white")
        self._ftop.pack(fill="both", expand=True)
        #construction de l'interface dans la top frame
        self._drawUI(self._ftop)
        return

    def _drawUI(self, frame):
        '''Dessine les widgets d'interface dans la frame indiquée.'''
        #canvas et dessin de la grille
        self._fgrid = tix.Frame(frame, bg="white")
        self._cnv = tix.Canvas(self._fgrid, width=280, height=280, bg="white")
        self._grid = SudoGuiGrid(self._cnv)
        #la grille est en haut de sa frame et de taille fixe
        self._cnv.pack(side="top")
        #texte déroulant
        self._ftext = tix.Frame(frame, bg="white")
        self._st = tix.ScrolledText(self._ftext, width=500, height=600)
        self._disp = self._st.subwidget("text")
        #la textbox est en haut de sa frame et la remplit
        self._st.pack(side="top", fill="both", expand=True)
        #arrangement des frames
        self._fgrid.pack(side="left", fill="y")
        self._ftext.pack(side="right", fill="both", expand=True)
        return

    def activate(self, act=True):
        '''Active l'interface, sinon toutes ses interactions sont inactives.
        Cela facilite la gestion de changements de modes dans le programme.
        '''
        if not self._open:
            raise Sudoku_Error("GUI was closed - now unusable")
        if act in (True, False):
            self._active = act
        else:
            raise Sudoku_Error("Wrong GUI activation value. "\
                               "Must be True or False.")
        return
    
    def displayText(self, text=None):
        '''Affiche du texte si l'interface est active, sinon ne fait rien.'''
        if not self._open:
            raise Sudoku_Error("GUI was closed - now unusable")
        if self._active:
            if text is None:
                self._disp.insert("end", "\n")
            else:
                self._disp.insert("end", text)
        return

    def scrollTextEnd(self):
        '''Fait défiler la fenêtre de texte pour afficher la fin du texte.'''
        self._disp.see("end")
        
    def update(self):
        if not self._open:
            raise Sudoku_Error("GUI was closed - now unusable")
        self._gui.update()
        return

    def hide(self):
        if not self._open:
            raise Sudoku_Error("GUI was closed - now unusable")
        self._gui.withdraw()
        return

    def show(self):
        if not self._open:
            raise Sudoku_Error("GUI was closed - now unusable")
        self._gui.deiconify()
        return

    def close(self):
        '''Ferme la fenêtre graphique. La fermeture est définitive, il n'y a pas
        de méthode pour remettre la variable d'instance __open à True.
        '''
        if self._open:
            self._gui.destroy()
            self._open = False
        return


class SudoGuiGrid():
    '''Classe qui représente une grille graphique sur un canevas. Les méthodes
    publiques permettent de placer les chiffres, les retirer et vider la grille.
    Chaque chiffre affiché a un tag unique "row+10xcol" qui permet de l'effacer.
    '''

    def __init__(self, canvas):
        '''Initialisation. Enregistre le canvas et dessine la grille.'''
        self._canvas = canvas
        self._initGeometry()
        self._drawGrid()
        return

    def _initGeometry(self):
        '''Définit les valeurs par défaut de géométrie d'affichage.'''
        self._xscale=30
        self._yscale=30
        self._xoffset = 5
        self._yoffset = 5
        self._linewidth1 = 1
        self._linewidth2 = 2
        self._linecol = "black"
        self._txtfontfamily = "Helvetica"
        self._txtfontsize = "12"
        self._txtfontstyle = "bold"
        self._txtfont = ("Helvetica", "12", "bold")
        return

    def _drawGrid(self):
        '''Dessine la grille vide.'''
        x0 = self._xoffset
        y0 = self._yoffset
        #les lignes horizontales
        x1 = x0
        x2 = x0 + 9*self._xscale
        for i in range(0,10):
            y = y0 + i*self._yscale
            if i%3==0:
                w = self._linewidth2
            else:
                w = self._linewidth1
            self._canvas.create_line( x1, y, x2, y, width=w, fill=self._linecol)
        #les bordures verticales
        y1 = y0
        y2 = y0 + 9*self._yscale
        for i in range(0,10):
            x = x0 + i*self._xscale
            if i%3==0:
                w = self._linewidth2
            else:
                w = self._linewidth1
            self._canvas.create_line( x, y1, x, y2, width=w, fill=self._linecol)
        #ok
        return
                                      
    def place(self, row, col, value):
        '''Place un chiffre (1 à 9) dans la case indiquée par les coordonnées.
        Le chiffre a un 'tag' qui permettra éventuellement de le supprimer.
        '''
        #attention, row = axe y et col = axe x
        x = self._xoffset + self._xscale//2 + (col-1)*self._xscale
        y = self._yoffset + self._yscale//2 + (row-1)*self._yscale
        id = self._canvas.create_text(x, y, text = str(value), \
                                      font = self._txtfont)
        self._canvas.addtag_withtag("gridvalue", id)
        self._canvas.addtag_withtag("grid"+str(10*row+col), id)
        return

    def remove(self, row, col):
        '''Enlève un chiffre de la case indiquée par les coordonnées.'''
        self._canvas.delete("grid"+str(10*row+col))
        return

    def clear(self):
        '''Enlève tous les chiffres.'''
        self._canvas.delete("gridvalue")
        return
                                    

        
        


#TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST

if __name__ == "__main__":
    pass
##    #Créer une fenêtre avec un canvas
##    wapp = tix.Tk()
##    wapp.geometry("500x500")
##    wapp.title("Test Grid GUI")
##    cnv = tix.Canvas(wapp, width=280, height=280, bg="white", relief="groove")
##    cnv.grid()
##    grid = SudoGuiGrid(cnv)

    gui=SudoGUI()
    
