# -*- coding: cp1252 -*-

'''Programme SudoSimu
Simulation de résolution humaine du jeu de Sudoku
Module sudotest : support d'I/O pour le test du code.

Principales méthodes :
    test(): ajoute une clé de gestion de test
    untest() : retire une clé
    level() : retourne ou modifie le niveau de gestion d'une clé
    clear() : vide le dictionnaire des clés de test gérées

Les méthodes suivantes exécutent des actions selon le niveau de la clé
fournie en argument et le niveau demandé
    display() : affiche un texte 
    showgrid() : affiche la grille 
    pause() : fait une pause console avec gestion des interruptions (Ctrl-c)
    iftest() : return True ou False suivant la validation du niveau de la clé
    raiseArgs() : déclenche une exception suivant le niveau de la clé
'''
'''
Dernière mise à jour : 11/10/2017
14/11/2017 - Ajout de la méthode 'beQuiet' pour supprier tous les outputs.
    Permet de faire des environnements silencieux. Mais les autres
    fonctionnalités sont concervées.
04/10/2017 - Ajout de la méthode raiseArgs
    Mise-à-jour de l'en-tête et de commentaires
'''

#Imports suivant que l'exécution est intérieure ou extérieure au package
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
    '''Classe utilisée pour gérer des paramètres et des interactions UI
    lors du test du code.
    '''

    def __init__(self):
        '''Crée le dictionnaire pour contenir les clés et niveaux '''
        self._tstdict = dict()
        #Modes d'affichage par défaut = console + GUI
        self._modeUI = MODE_BOTH
        self._modeUIlevel = 1
        self._beQuiet = False #variable privée de mode sans output

    def beQuiet(self, choice=True):
        assert choice in (True, False)
        self._beQuiet = choice
        return
    
    def exceptQuiet(self, text):
        '''Ne retourne pas le texte en paramètre si le mode 'quiet' est actif.
        '''
        return (text if self._beQuiet is not True else None)

    def test(self, key, level=0):
        '''Ajoute la clé indiquée avec son niveau. La clé est transformée
        en chaîne de caractères, donc la clé 1 est stockée comme "1".
        Permet aussi de changer le niveau de la clé si elle existe déjà.
        '''
        assert isinstance(level, int) or level is None
##        if level == 0:
##            self.unTest(key)
##        else:
##            self._tstdict[str(key)] = level
        self._tstdict[str(key)] = level
        return

    def unTest(self, key):
        '''Retire la clé indiquée. '''
        self._tstdict.pop(str(key),None)
        return

    def level(self,key, newlevel=None):
        '''Retourne le niveau d'une clé existante ou fixe un nouveau niveau
        s'il est indiqué. Si le nouveau niveau est 0, retire la clé.
        Retourne None si la clé n'existe pas.
        '''
        assert isinstance(newlevel, int) or newlevel is None
        level = self._tstdict.get(str(key), None)
        if level is not None:    #si la clé existe déjà
            if newlevel is not None:
                self.test(key, newlevel)
                level = newlevel
        return level

    def levelAll(self, newlevel=None):
        '''Met toutes les clés au niveau indiqué. Si le niveau est 0, retire
        toutes les clés. S'il n'est pas indiqué (None), ne fait rien.
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
        '''Affiche le texte si la clé est dans le dict et si son niveau
        est >= à celui demandé.
        Par exception, le texte n'est pas affiché si le niveau demandé
        est 0 (zéro) même si le niveau de la clé est 0.
        Le texte est affichée dans l'interface STD ou GUI suivant le mode actif.
        '''
        #ne fait rien en mode 'quiet'
        if self._beQuiet is True:
            return None
        
        keylev = self._tstdict.get(str(key), None)  #None si clé absente
        if keylev != None and keylev >= level:
            if self._modeUI == MODE_GUI \
                or (self._modeUI in (MODE_SELECT, MODE_BOTH) \
                    and level <= self._modeUIlevel):
                ui.display(txt)        #dans l'interface active STD ou GUI
            if self._modeUI == MODE_STD \
                or (self._modeUI == MODE_SELECT and level > self._modeUIlevel) \
                or self._modeUI == MODE_BOTH:
                ui.displaySTD(txt)     #dans la console STD
            #s'il y a un affichage graphique, mettre à jour la fenêtre
            if self._modeUI in (MODE_GUI, MODE_BOTH):
                ui.updateGUI()
                pass
        return

    def displayError(self, key, level, txt):
        '''Affiche un texte de type Erreur, donc avec des supports d'affichage
        éventuellement différents.
        '''
## Pour le moment ne fait rien de différent de display(). A upgrader plus tard
        return self.display(key, level, txt)
        
    def displayUImode(self, mode, level=1):
        '''Définit le mode d'affichage de test : soit dans l'interface
        utilisateur active (STD ou GUI), soit toujours dans la console.
        Si mode est SELECT l'affichage est déterminé par le niveau limite
        indiqué :
        <= level  --> affichage interface active STD ou GUI,
        > level  --> affichage STD forcé.
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
        '''Affiche la grille si la clé est dans le dict et si son niveau
        est >= à celui demandé. La grille est toujours affichée dans la console.
        En mode 'quiet' aucun affichage de grille.
        '''
        #ne fait rien en mode 'quiet'
        if self._beQuiet is True:
            return None

        keylev = self._tstdict.get(str(key), None)  #None si clé absente
        if keylev != None and keylev >= level:
            if txt == None:
                txt = "Etat de la grille:"
            if len(txt) >0:     #permet d'utiliser "" pour ne rien afficher
                ui.displaySTD(txt)
            grid.show(style)
        return
        
    def pause(self, key, level, pausearg=None):
        '''pause conditionnelle suivant le niveau de test.
        Voir sudoio.sudoPause() pour les détails d'exécution de la pause.
        Cette méthode n'est pas affectée par le mode 'quiet'.
        '''
        keylev = self._tstdict.get(str(key), None)  #None si clé absente
        if keylev != None and keylev >= level:
            #faire la pause 
            r = ui.sudoPause(pausearg)
            #si le mode graphique est actif, mettre à jour la fenêtre
            if self._modeUI in (MODE_GUI, MODE_BOTH):
                ui.updateGUI()
            return r
        else:
            return True

    def ifLevel(self, key, level):
        '''retourne True si la clé et le niveau activent le test, retourne
        False si la clé n'existe pas ou si le niveau est insuffisant.
        Cette méthode n'est pas affectée par le mode 'quiet'.
        '''
        keylev = self._tstdict.get(str(key), None)  #None si clé absente
        if keylev != None and keylev >= level:
            return True
        else:
            return False

    def raiseArgs(self, key, level, exceptClass=rules.Sudoku_Error,
                                    exceptArgs=None):
        '''Déclenche une exception de la classe et avec les arguments indiqués,
        si la clé est dans le dictionnaire et si sa valeur est supérieure
        au niveau indiqué. 
        Cette méthode n'est pas affectée par le mode 'quiet'.
        '''
        keylev = self._tstdict.get(str(key), None)  #None si clé absente
        if keylev != None and keylev >= level:
            raise exceptClass(exceptArgs)
        
    @property
    def keys(self):
        '''Retourne le dictionnaire des clés de test enregistrées.
        Cette méthode n'est pas affectée par le mode 'quiet'.
        '''
        return self._tstdict.copy()
    
    def __str__(self):
        '''Retourne une forme de texte le contenu du dictionnaire des clés.
        Le texte est la suite des clés, chacune sur une ligne.
        '''
        strkeys = ""
        i = False
        for key in self._tstdict:
            if not i:                #pour éviter le \n au début
                strkeys = "{0} : {1}".format(key,self._tstdict[key])
                i = True
            else:
                strkeys = strkeys + \
                          "\n{0} : {1}".format(key,self._tstdict[key])
        if i == False:
            strkeys = None
        return strkeys
    

    
#On crée une instance de SudoTest pour être utilisée dans tout le programme
sudoTest = SudoTest()
#alias = même objet
TEST = sudoTest


if __name__ == "__main__":
    
##    TEST.test(1)
##    TEST.test(2)
##    print(TEST.keys)    #doit imprimer {'2': 1, '1': 1} ou équivalent
##    TEST.test("pause")
##    print("Pause #1 sans arg continuer")
##    TEST.pause("pause",1)
##    TEST.test("2",4)    #"2" = même clé que 2 déjà ajouté
##    print(TEST.keys)          #doit imprimer {'2': 4, '1': 1} ou équivalent
##    print(TEST)             #doit imprimer  2 : 4 (newline) 1 : 1 ou équivalent
##    print(TEST.level(5))    #doit imprimer None
##    print(TEST.level(1,0))
##    print("Pause #2 avec arg continuer")
##    r = TEST.pause("pause",1,True)
##    while r == True:
##        r = TEST.pause("pause",3,True)
    
    #test en mode graphique
    TEST.test("", 3)
    print("Début du test graphique")
    TEST.pause("", 1, True)

    TEST.display("", 1, "Ouverture de la fenêtre...")
    TEST.pause("", 1, True)
    ui.UImode(ui.GUI)
    TEST.displayUImode(MODE_BOTH, 2)
    TEST.display("", 1, "Fenêtre ouverte.")
    TEST.pause("", 1, True)

    TEST.display("", 1, "Hello1")
    TEST.pause("", 1, True)
    TEST.display("", 2, "Hello2")
    TEST.pause("", 1, True)
    TEST.display("", 3, "Hello3")
    TEST.pause("", 1, True)
    TEST.display("", 4, "Hello4")
    TEST.pause("", 1, True)

    TEST.display("", 1, "Test en cachant la fenêtre principale")
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
    
    
