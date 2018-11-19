# -*- coding: cp1252 -*-

'''Programme SudoSimu
Simulation de r�solution humaine du jeu de Sudoku
Module sudotest : support d'I/O pour le test du code.

Principales m�thodes :
    test(): ajoute une cl� de gestion de test
    untest() : retire une cl�
    level() : retourne ou modifie le niveau de gestion d'une cl�
    clear() : vide le dictionnaire des cl�s de test g�r�es

Les m�thodes suivantes ex�cutent des actions selon le niveau de la cl�
fournie en argument et le niveau demand�
    display() : affiche un texte 
    showgrid() : affiche la grille 
    pause() : fait une pause console avec gestion des interruptions (Ctrl-c)
    iftest() : return True ou False suivant la validation du niveau de la cl�
    raiseArgs() : d�clenche une exception suivant le niveau de la cl�
'''
'''
Derni�re mise � jour : 11/10/2017
14/11/2017 - Ajout de la m�thode 'beQuiet' pour supprier tous les outputs.
    Permet de faire des environnements silencieux. Mais les autres
    fonctionnalit�s sont concerv�es.
04/10/2017 - Ajout de la m�thode raiseArgs
    Mise-�-jour de l'en-t�te et de commentaires
'''

#Imports suivant que l'ex�cution est int�rieure ou ext�rieure au package
if __name__ in ("__main__", "sudotest"):
    import sudoui as ui
    import sudorules as rules
    import sudogrid
elif __name__ == "sudosimu.sudotest":
    from sudosimu import sudoui as ui
    from sudosimu import sudorules as rules
    from sudosimu import sudogrid
else:
    raise Exception("Impossible de faire les imports dans le module sudotest.")

#modes d'affichage
MODE_GUI = ui.GUI      #affiche toujours dans l'interface active
MODE_STD = ui.STD      #affiche toujours dans l'interface standard (console)
MODE_SELECT = -1    #affiche dans l'une ou l'autre suivant le niveau
MODE_BOTH = -2      #affiche dans les deux, dont GUI suivant le niveau


class SudoTest():
    '''Classe utilis�e pour g�rer des param�tres et des interactions UI
    lors du test du code.
    '''

    def __init__(self):
        '''Cr�e le dictionnaire pour contenir les cl�s et niveaux '''
        self._tstdict = dict()
        #Modes d'affichage par d�faut = console + GUI
        self._modeUI = MODE_BOTH
        self._modeUIlevel = 1
        self._beQuiet = False #variable priv�e de mode sans output

    def beQuiet(self, choice=True):
        assert choice in (True, False)
        self._beQuiet = choice
        return
    
    def exceptQuiet(self, text):
        '''Ne retourne pas le texte en param�tre si le mode 'quiet' est actif.
        '''
        return (text if self._beQuiet is not True else None)

    def test(self, key, level=0):
        '''Ajoute la cl� indiqu�e avec son niveau. La cl� est transform�e
        en cha�ne de caract�res, donc la cl� 1 est stock�e comme "1".
        Permet aussi de changer le niveau de la cl� si elle existe d�j�.
        '''
        assert isinstance(level, int) or level is None
##        if level == 0:
##            self.unTest(key)
##        else:
##            self._tstdict[str(key)] = level
        self._tstdict[str(key)] = level
        return

    def unTest(self, key):
        '''Retire la cl� indiqu�e. '''
        self._tstdict.pop(str(key),None)
        return

    def level(self,key, newlevel=None):
        '''Retourne le niveau d'une cl� existante ou fixe un nouveau niveau
        s'il est indiqu�. Si le nouveau niveau est 0, retire la cl�.
        Retourne None si la cl� n'existe pas.
        '''
        assert isinstance(newlevel, int) or newlevel is None
        level = self._tstdict.get(str(key), None)
        if level is not None:    #si la cl� existe d�j�
            if newlevel is not None:
                self.test(key, newlevel)
                level = newlevel
        return level

    def levelAll(self, newlevel=None):
        '''Met toutes les cl�s au niveau indiqu�. Si le niveau est 0, retire
        toutes les cl�s. S'il n'est pas indiqu� (None), ne fait rien.
        '''
        assert isinstance(newlevel, int) or newlevel is None
        if newlevel is None or newlevel<0:
            return None
        else:
            for key in self._tstdict:
                self.test(key, newlevel)
        return

        
    def clearAll(self):
        '''Vide le dictionnaire de test.'''
        self._tstdict.clear()
        return
        
    def display(self, key, level, txt):
        '''Affiche le texte si la cl� est dans le dict et si son niveau
        est >= � celui demand�.
        Par exception, le texte n'est pas affich� si le niveau demand�
        est 0 (z�ro) m�me si le niveau de la cl� est 0.
        Le texte est affich�e dans l'interface STD ou GUI suivant le mode actif.
        '''
        #ne fait rien en mode 'quiet'
        if self._beQuiet is True:
            return None
        
        keylev = self._tstdict.get(str(key), None)  #None si cl� absente
        if keylev != None and keylev >= level:
            if self._modeUI == MODE_GUI \
                or (self._modeUI in (MODE_SELECT, MODE_BOTH) \
                    and level <= self._modeUIlevel):
                ui.display(txt)        #dans l'interface active STD ou GUI
            if self._modeUI == MODE_STD \
                or (self._modeUI == MODE_SELECT and level > self._modeUIlevel) \
                or self._modeUI == MODE_BOTH:
                ui.displaySTD(txt)     #dans la console STD
            #s'il y a un affichage graphique, mettre � jour la fen�tre
            if self._modeUI in (MODE_GUI, MODE_BOTH):
                ui.updateGUI()
                pass
        return

    def displayError(self, key, level, txt):
        '''Affiche un texte de type Erreur, donc avec des supports d'affichage
        �ventuellement diff�rents.
        '''
## Pour le moment ne fait rien de diff�rent de display(). A upgrader plus tard
        return self.display(key, level, txt)
        
    def displayUImode(self, mode, level=1):
        '''D�finit le mode d'affichage de test : soit dans l'interface
        utilisateur active (STD ou GUI), soit toujours dans la console.
        Si mode est SELECT l'affichage est d�termin� par le niveau limite
        indiqu� :
        <= level  --> affichage interface active STD ou GUI,
        > level  --> affichage STD forc�.
        Si mode est BOTH, l'affichage est fait dans l'interface active  suivant
        le niveau, ainsi que toujours fait dans l'interface STD
        '''
        #ne fait rien en mode 'quiet'
        if self._beQuiet is True:
            return None
        
        if mode in (MODE_STD, MODE_GUI):
            self._modeUI = mode
        elif mode in (MODE_SELECT, MODE_BOTH):
            self._modeUI = mode
            self._modeUIlevel = level
        return

    def showgrid(self, key, level, grid, txt=None, style=None):
        '''Affiche la grille si la cl� est dans le dict et si son niveau
        est >= � celui demand�. La grille est toujours affich�e dans la console.
        En mode 'quiet' aucun affichage de grille.
        '''
        #ne fait rien en mode 'quiet'
        if self._beQuiet is True:
            return None

        keylev = self._tstdict.get(str(key), None)  #None si cl� absente
        if keylev != None and keylev >= level:
            if txt == None:
                txt = "Etat de la grille:"
            if len(txt) >0:     #permet d'utiliser "" pour ne rien afficher
                ui.displaySTD(txt)
            grid.show(style)
        return
        
    def pause(self, key, level, pausearg=None):
        '''pause conditionnelle suivant le niveau de test.
        Voir sudoio.sudoPause() pour les d�tails d'ex�cution de la pause.
        Cette m�thode n'est pas affect�e par le mode 'quiet'.
        '''
        keylev = self._tstdict.get(str(key), None)  #None si cl� absente
        if keylev != None and keylev >= level:
            #faire la pause 
            r = ui.sudoPause(pausearg)
            #si le mode graphique est actif, mettre � jour la fen�tre
            if self._modeUI in (MODE_GUI, MODE_BOTH):
                ui.updateGUI()
            return r
        else:
            return True

    def ifLevel(self, key, level):
        '''retourne True si la cl� et le niveau activent le test, retourne
        False si la cl� n'existe pas ou si le niveau est insuffisant.
        Cette m�thode n'est pas affect�e par le mode 'quiet'.
        '''
        keylev = self._tstdict.get(str(key), None)  #None si cl� absente
        if keylev != None and keylev >= level:
            return True
        else:
            return False

    def raiseArgs(self, key, level, exceptClass=rules.Sudoku_Error,
                                    exceptArgs=None):
        '''D�clenche une exception de la classe et avec les arguments indiqu�s,
        si la cl� est dans le dictionnaire et si sa valeur est sup�rieure
        au niveau indiqu�. 
        Cette m�thode n'est pas affect�e par le mode 'quiet'.
        '''
        keylev = self._tstdict.get(str(key), None)  #None si cl� absente
        if keylev != None and keylev >= level:
            raise exceptClass(exceptArgs)
        
    @property
    def keys(self):
        '''Retourne le dictionnaire des cl�s de test enregistr�es.
        Cette m�thode n'est pas affect�e par le mode 'quiet'.
        '''
        return self._tstdict.copy()
    
    def __str__(self):
        '''Retourne une forme de texte le contenu du dictionnaire des cl�s.
        Le texte est la suite des cl�s, chacune sur une ligne.
        '''
        strkeys = ""
        i = False
        for key in self._tstdict:
            if not i:                #pour �viter le \n au d�but
                strkeys = "{0} : {1}".format(key,self._tstdict[key])
                i = True
            else:
                strkeys = strkeys + \
                          "\n{0} : {1}".format(key,self._tstdict[key])
        if i == False:
            strkeys = None
        return strkeys
    

    
#On cr�e une instance de SudoTest pour �tre utilis�e dans tout le programme
sudoTest = SudoTest()
#alias = m�me objet
TEST = sudoTest


if __name__ == "__main__":
    
##    TEST.test(1)
##    TEST.test(2)
##    print(TEST.keys)    #doit imprimer {'2': 1, '1': 1} ou �quivalent
##    TEST.test("pause")
##    print("Pause #1 sans arg continuer")
##    TEST.pause("pause",1)
##    TEST.test("2",4)    #"2" = m�me cl� que 2 d�j� ajout�
##    print(TEST.keys)          #doit imprimer {'2': 4, '1': 1} ou �quivalent
##    print(TEST)             #doit imprimer  2 : 4 (newline) 1 : 1 ou �quivalent
##    print(TEST.level(5))    #doit imprimer None
##    print(TEST.level(1,0))
##    print("Pause #2 avec arg continuer")
##    r = TEST.pause("pause",1,True)
##    while r == True:
##        r = TEST.pause("pause",3,True)
    
    #test en mode graphique
    TEST.test("", 3)
    print("D�but du test graphique")
    TEST.pause("", 1, True)

    TEST.display("", 1, "Ouverture de la fen�tre...")
    TEST.pause("", 1, True)
    ui.UImode(ui.GUI)
    TEST.displayUImode(MODE_BOTH, 2)
    TEST.display("", 1, "Fen�tre ouverte.")
    TEST.pause("", 1, True)

    TEST.display("", 1, "Hello1")
    TEST.pause("", 1, True)
    TEST.display("", 2, "Hello2")
    TEST.pause("", 1, True)
    TEST.display("", 3, "Hello3")
    TEST.pause("", 1, True)
    TEST.display("", 4, "Hello4")
    TEST.pause("", 1, True)

    TEST.display("", 1, "Test en cachant la fen�tre principale")
    ui.hideGUI()
    
    TEST.display("", 1, "Hello1")
    TEST.pause("", 1, True)
    TEST.display("", 2, "Hello2")
    TEST.pause("", 1, True)
    TEST.display("", 3, "Hello3")
    TEST.pause("", 1, True)
    TEST.display("", 4, "Hello4")
    TEST.pause("", 1, True)

    TEST.display("", 1, "Fin du test.")
    TEST.pause("", 1, True)
    ui.closeGUI()
    
    
