# -*- coding: cp1252 -*-

# programme HumaSudo
# résolution humaine simulée de Sudoku 

import fileinput
import sudorules
from sudorules import Sudoku_Error
import tkinter as tk
import tkinter.tix as tix

STD = 1
GUI = 2
__sudoGUI = None

class SudoGUI():
    '''Classe d'interface graphique pour le programe. Cette classe fournit
    des méthodes d'affichage et d'input standardisées qui permettent la même
    interaction que dans un autre mode d'interface;
    '''
    def __init__(self):
        self._startGUI()
        self.__open = True
        self.__active = False
        

    def _startGUI(self):
        '''Ouvre une fenêtre graphique.
        Dans cette version ce n'est pas réellement une application Python, la
        fenêtre ne fonctionne qu'à travers un shell Python (ex: IDLE)
        '''
        global mode
        global GUI
        self.__gui = tix.Tk()
        self.__gui.title("HumaSudo - Sudoku humain")
        self.__ftop = tix.Frame(self.__gui)
        self.__st = tix.ScrolledText(self.__ftop, width=300, height=500)
        self.__st.pack(side="top", fill="both")
        self.__ftop.pack(side="top", fill="both")
        self.__disp = self.__st.subwidget("text")
        return

    def activate(self, act=True):
        '''Active l'interface, sinon toutes ses interactions sont inactives.
        Cela facilite la gestion de changements de modes dans le programme.
        '''
        if not self.__open:
            raise Sudoku_Error("GUI was closed - now unusable")
        if act in (True, False):
            self.__active = act
        else:
            raise Sudoku_Error("Wrong GUI activation value. "\
                               "Must be True or False.")
        return
    
    def display(self, text=None):
        '''Affiche du texte si l'interface est active, sinon ne fait rien.'''
        if not self.__open:
            raise Sudoku_Error("GUI was closed - now unusable")
        if self.__active:
            if text is None:
                self.__disp.insert("end", "\n")
            else:
                self.__disp.insert("end", text)
        return

    def close(self):
        '''Ferme la fenêtre graphique. La fermeture est définitive, il n'y a pas
        de méthode pour remettre la variable d'instance __open à True.
        '''
        if self.__open:
            self.__gui.destroy()
            self.__open = False
        return
        

