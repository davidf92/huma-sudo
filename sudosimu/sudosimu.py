# -*- coding: cp1252 -*-

'''Module sudosimu (sudosimu.sudosimu.py)
Script de la classe SudoSimu, qui encapsule la totalit� de la simulation de
r�solution de Sudoku. C'est ici qu'est la boucle de simulation ROMA : R�fl�chir,
Observer, M�moriser, Apprendre.

La classe SudoSimu est instanci�e avec les capacit�s cognitives du joueur,
SudoMemory et SudoThinking, ainsi qu'avec la vue sur la grille SudoGridView.
En revanche elle n'a aucun acc�s direct � la grille.
Comme le reste du programme, SudoSimu utilise l'environnement SudoEnv et
interagit avec l'interface utilisateur via SudoUI.
'''

'''
Derni�re mise � jour : 14/11/2018
Historique des modifications :
14/11/2018 - Version initiale
    Reprise du code de sudogame.py et adaptation de l'ancienne classe SudoGame
    renomm�e en SudoSimu. Adaptation du code de test et des displays.
'''

if __name__ in ("__main__", "sudosimu"):
    import sudobaseclass as base
    import sudoenv
    import sudoui as ui
    import sudorules as rules
    from sudorules import Sudoku_Error
    from sudogridview import SudoGridView
    from sudomemory import SudoMemory
    from sudothinking import SudoThinking
elif __name__ == "sudosimu.sudosimu":
    from sudosimu import sudobaseclass as base
    from sudosimu import sudoenv
    from sudosimu import sudoui as ui
    from sudosimu import sudorules as rules
    from sudosimu.sudorules import Sudoku_Error
    from sudosimu.sudogridview import SudoGridView
    from sudosimu.sudomemory import SudoMemory
    from sudosimu.sudothinking import SudoThinking
else:
    raise Exception("Impossible de faire les imports dans le module sudosimu.")

#constantes utilis�es pour les pauses de boucle de r�solution
STEP = "step"       #pause � chaque it�ration
OBS = "obs"         #pause � chaque observation et chaque placement
OBSERVE = OBS       #synonyme
PLACE = "place"     #pause uniquement � chaque placement
FAIL = "fail"       #pause � chaque difficult� ou erreur de jeu
END = "end"         #explicitement jusqu'� la fin (�quivalent � 'None')
                    #END s'impose contre les autres param�tres.
EXCEPT = "except"   #pause � chaque d�clenchement d'un exception. C'est plut�t
                    #destin� au d�buggage, �a n'a pas de sens pour un joueur.
NOEXCEPT = "noexcept" #pour annuler explicitement la pause sur exception.
PAUSEPARLIST = (STEP, OBS, PLACE, FAIL, END, EXCEPT, NOEXCEPT)

#constance utilis�e pour contr�ler la boucle
STOP = "stop"
LOOP = "loop"

#gestion initiale des exceptions dans toute la partie
#Mode debug : d�clencher et propager les exceptions
EXCEPT_MODE = EXCEPT
#Mode release : g�rer les exceptions
#EXCEPT_MODE = NOEXCEPT

class SudoSimu(base.SudoBaseClass):
    ''' Encapsule la simulation de r�solution avec la cognition du joueur et
    la vue sur la grille (mais pas la grille elle-m�me). Contient la boucle
    de r�solution it�rative.
    '''
#class SudoGame(base.SudoBaseClass):
#    '''Ex�cute la r�solution d'une grille par un joueur'''

    def __init__(self, mem, think, view, env=None, \
                                         testlevel=sudoenv.TEST_SIMULEVEL):
        '''Initialisation de la nouvelle instance de jeu. Les param�tres sont
        les capacit�s que le joueur attribue � ce jeu (mem, think) et la vue
        de la grille (view).
        '''
        #init de la classe racine
        assert isinstance(env, sudoenv.SudoEnv) or env is None
        assert isinstance(testlevel, int) and testlevel>=0 \
                or testlevel is None
        #reprendre un pr�c�dente niveau de test s'il existe d�j�
        oldlev = env.testLevel("simu")
        if oldlev is not None and testlevel != oldlev:
            testlevel = oldlev
        base.SudoBaseClass.__init__(self, env=env, \
                                    testlabel="simu", testlevel=testlevel)
        #ok init de cette classe
        TEST = self.env.TEST
        TEST.display("simu", 3, "SudoSimu - Dans __init__()")
        assert isinstance(mem, SudoMemory)
        assert isinstance(think, SudoThinking)
        assert isinstance(view, SudoGridView)
        self._mem = mem
        self._think = think
        self._view = view
        #initialiser le contr�le de la partie
        self._modeExcept = EXCEPT_MODE #voir les globales au d�but
        self._initSimu()
        return

    def _initSimu(self):
        '''Pr�pare les donn�es de contr�le d'ex�cution.'''
        self._pauseParams = None
        self._solveResult = None
        self._lastAction = None
        self._lastActionDetails = None
        self._solving = False
        self._finished = False
        self._initOk = True # A SUPPRIMER du code, inutile maintenant
        return

    def solve(self, pauseParams=None, pauseMem=True):
        '''Joue la partie et r�sout la grille. Peut �tre appel�e r�p�titivement
        jusqu'� la fin de la partie. Le param�tre 'pauseParams' permet de 
        sp�cifier des r�gles d'interruption (pause) p�riodique de la partie
        (chaque it�ration, observation, placement, etc.) et � chaque appel de
        solve() la consigne de pause peut �tre modifi�e. solve() sans arguments
        commence ou continue la r�solution avec les param�tres de pause
        pr�c�dents. Le param�tre 'pauseMem' indique si le param�tre de pause
        indiqu� doit �tre m�moris� (Oui par d�faut).
        Retourne "pause", "end" ou "fail" suivant le cas. Retourne avec "end"
        le r�sultat de la partie ("win", "quit", etc.). Retourne avec "pause"
        le r�sultat de la derni�re it�ration jou�e ("observe", "place", etc.)
        Retourne avec "fail" les �ventuelles exceptions g�r�es. Retourne
        None si la partie est d�j� termin�e.
        '''
        TEST = self.env.TEST
        TEST.display("simu", 3, "SudoSimu - dans solve()")
        assert self._initOk
        self._lastAction = None
        self._lastActionDetails = None

        #partie d�j� termin�e ?
        if self._finished is True:
            TEST.display("simu", 3, "SudoSimu - appel de solve() alors que la "\
                                         "partie est d�j� termin�e.")
            TEST.display("simu", 1, "La partie est d�j� termin�e.")
            return None
        #d�but de partie
        if self._solving is False:
            #ok pour commencer la r�solution
            TEST.display("simu", 3, "SudoSimu - D�but de r�solution.")
            TEST.display("simu", 1, "D�but de la partie de Sudoku.")
            self._solving = True
####Des actions particuli�res de d�but de partie ?
####Mettre des compteurs, etc.
######################################
            
        #m�morise le param�tre de pause indiqu� si c'est demand�
        if pauseParams is not None and pauseMem is True:
            self._pauseParams = pauseParams
        #r�solution avec le param�tre indiqu� ou celui d�j� m�moris�
        if pauseParams is None:
            pause = self._pauseParams
        else:
            pause = pauseParams
        TEST.display("simu", 3, "Avancement de r�solution avec le "\
                         "param�tre de pause : {0}".format(pause))
        #r�solution
        solveResult = self._solveLoop(pause)
        TEST.display("simu", 3, "Simu - Retour � solve(). \nR�sultat retourn� "\
                                 ": {0}".format(solveResult))

        #Si la partie s'est mise en pause, indique la cause de cette pause.
        if solveResult[0] == "pause":
            TEST.display("simu", 1, "Pause de jeu. D�tails : {0}"\
                                     .format(solveResult[1]))

        #Si la partie est termin�e, indiquer le r�sultat de la partie et
        #mettre � jour les indicateurs d'avancement
        elif solveResult[0] == "end":
            self._solving = False
            self._finished = True
            TEST.display("simu", 1, "Partie termin�. D�tails : {0}"\
                                     .format(solveResult[1]))

        #Si la partie rencontre une erreur non fatale :
        elif solveResult[0] == "fail":
            TEST.display("simu", 1, "La partie rencontre une erreur. "\
                                     "D�tail : {0}".format(solveResult[1]))
        #tout autre r�sultas -> Fin de partie forc�e
        else:
            self._solving = False
            self._finished = True
            TEST.display("simu", 1, "ATTENTION : r�sultat de jeu anormal : {0}"\
                                 .format(solveResult))
            TEST.display("simu", 1, "La partie est abandonn�e.")
            return ("end", ("Erreur fatale", solveResult))
        #ok retour normal
        return solveResult

    def setPauseParams(self, pauseParams):
        '''D�finit les options de pause. L'argument doit �tre explicite, donc
        pour annuler toutes les pauses il faut appeler setPauseParams(None).
        '''
        TEST = self.env.TEST
        self._pauseParams = pauseParams
        return
    
    def solveOnce(self, pauseParams=None):
        '''Avance la r�solution jusqu'� la fin ou jusqu'� la pause param�tr�e.
        La r�solution doit �tre d�j� en cours. Ne m�morise pas le param�tre
        'pauseParams' pour les appels suivants. Voir aussi la m�thode solve().
        '''
        TEST = self.env.TEST
        TEST.display("simu", 3, "Simu - dans playOnce()")
        if not self._checkPlaying():
            return None
        else:
            return self.solve(pauseParams, False)

    def next(self, pauseParams=None):
        '''Continue la partie jusqu'� la prochaine pause indiqu�e en argument
        et m�morise l'argument de pause pour la suite.
        Equivalent � solve une fois que la partie est commenc�e.
        '''
        TEST = self.env.TEST
        TEST.display("simu", 3, "Simu - dans again()")
        assert self._initOk
        if not self._checkPlaying():
            return None
        else:
            return self.solve(pauseParams, True)
        
    def again(self):
        '''Continue la partie jusqu'� une prochaine pause selon le m�me
        param�tre que la fois pr�c�dente. La partie doit d�j� �tre en cours.
        '''
        TEST = self.env.TEST
        TEST.display("simu", 3, "Simu - dans again()")
        assert self._initOk
        if not self._checkPlaying():
            return None
        else:
            return self.solve()
        
    def resume(self):
        '''Poursuit la partie jusqu'� sa fin. Equivalent � solve(END). La
        r�solution doit �tre d�j� en cours. 
        '''
        TEST = self.env.TEST
        TEST.display("simu", 3, "Simu - dans resume()")
        assert self._initOk
        if not self._checkPlaying():
            return None
        else:
            return self.solveToEnd()
        
    def solveToEnd(self):
        '''Fait la r�solution compl�te sans pause. La r�solution doit �tre d�j�
        en cours. '''
        TEST = self.env.TEST
        TEST.display("simu", 3, "Simu - dans solveToEnd()")
        if not self._checkPlaying():
            return None
        else:
            return self.solve(END)

    def step(self):
        '''Fait une seule it�ration, quel que soit le param�tre de pause
        pr�c�demment utilis�. La r�solution doit �tre d�j� en cours. 
        '''
        TEST = self.env.TEST
        TEST.display("simu", 3, "Simu - dans step()")
        assert self._initOk
        if not self._checkPlaying():
            return None
        else:
            return self.solve(STEP, False)

    def observe(self):        
        '''Commence ou continue la partie jusqu'� la prochaine observation.
        La r�solution doit �tre d�j� en cours.
        '''
        TEST = self.env.TEST
        TEST.display("simu", 3, "Simu - dans observe()")
        assert self._initOk
        if not self._checkPlaying():
            return None
        else:
            return self.solve(OBSERVE, False)

    def place(self):
        '''Commence ou continue la partie jusqu'au prochaine placement.
        La r�solution doit �tre d�j� en cours.
        '''
        TEST = self.env.TEST
        TEST.display("simu", 3, "Simu - dans place()")
        assert self._initOk
        if not self._checkPlaying():
            return None
        else:
            return self.solve(PLACE, False)

    def abort(self):
        '''Interrompt une partie en cours.'''
        TEST = self.env.TEST
        TEST.display("simu", 3, "Simu - dans abort()")
        assert self._initOk
        if not self._checkPlaying():
            return None
        else:
            r = self._abort()
        return r

    def _checkPlaying(self):
        '''Fait une v�rification de partie en cours avant d'appeler solve().
        Utilis� par les m�thodes de continuation de r�solution.
        Retourne le r�sultat du jeu ou False si la partie n'est pas en cours
        '''
        TEST = self.env.TEST
        TEST.display("simu", 3, "Simu - dans _checkPlaying()")
        if self._finished is True:
            TEST.display("simu", 3, "Simu - Erreur, commande de suite de "\
                         "r�solution alors que la partie d�j� termin�e.")
            ui.displayError("Erreur", "La partie est d�j� termin�e.")
            r = False
        elif self._solving is False:
            TEST.display("simu", 3, "Simu - Erreur, commande de suite de "\
                         "r�solution alors que la partie n'est pas commenc�e.")
            ui.displayError("Erreur", "La partie n'est pas encore commenc�e.")
            r = False
        else:
            r = True
        return r
        
    def _solveLoop(self, pauseParams):
        '''Ex�cute la boucle it�rative d'analyse et action de jeu. La boucle
        s'interrompt selon les param�tres re�us du joueur.
        Retourne "pause", "end" ou "fail" suivant le param�trage de pause.
        Retourne avec "pause" le r�sultat de la derni�re it�ration jou�e.
        En cas d'erreur ou d'exception g�r�e, retourne un message sp�cifique.
        '''
        TEST = self.env.TEST
        TEST.display("simu", 3, "Simu - dans _solveLoop()")

        #mode de gestion des exceptions : il reste inchang� � moins qu'il y
        #ait un argument explicite.
        if pauseParams is not None:
            if EXCEPT in pauseParams:
                self._modeExcept = EXCEPT
            elif NOEXCEPT in pauseParams:
                self._modeExcept = NOEXCEPT

        #Boucle ROMA - R�fl�chir/Observer/M�moriser/Apprendre
        while True:
            try:
                TEST.display("simu", 2, "SudoSimu - lance une it�ration de jeu.")

                #it�ration de jeu avec indication de gestion des exceptions
                #(cet argument est transmis dans tout le code sous-jacent)
                #est enregistr� dans un attribut de l'objet
                solveResult = self._iterate(self._pauseExcept)
                TEST.display("simu", 3, "SudoSimu - retour � _solveLoop \n"\
                             "L'it�ration de r�flexion a retourn� : {0}"\
                             .format(solveResult))

                #sortir de la boucle dans tous les cas de pause de jeu
                #indiqu�s par 'player' en param�tre.
                action = solveResult[0]
                if pauseParams is None:
                    #ne s'arr�te qu'� la fin du jeu
                    if action == "end":
                        r = self._endSimu(solveResult)
                        break
                    else:
                        continue
                if action == "continue" and STEP in pauseParams:
                    r = ("pause", self._pauseContinue(solveResult))
                    break
                elif action == "observe" and OBS in pauseParams:
                    r = ("pause", self._pauseObserve(solveResult))
                    break
                elif action == "place" and (OBS in pauseParams
                                                or PLACE in pauseParams):
                    r = ("pause", self._pausePlace(solveResult))
                    break
                elif action == "fail" and FAIL in pauseParams:
                    r = ("pause", self._pauseFail(solveResult))
                    break
                elif action == "end":
                    r = self._endSimu(solveResult)
                    break
                #si le r�sultat n'est pas un r�sultat normal de jeu :
                elif action not in ("continue", "observe", "place",\
                                    "end", "fail"):
                    #pourrait �tre g�r� avec une exception...
                    TEST.display("simu", 1, "ATTENTION : r�sultat de jeu anormal : {0}"\
                                         .format(solveResult))
                    TEST.display("simu", 1, "La partie est abandonn�e.")
                    return ("end", ("Erreur fatale", solveResult))
                    
                #tous les cas autres que "continue" o� il y a STEP
                elif STEP in pauseParams:
                    r = ("pause", solveResult)
                    break
                #s'il n'y a aucune de ces combinaisons, la boucle continue.
                continue
            except:
                #G�re l'exception suivant le param�trage
                exceptMsg = "Exception dans SudoSimu._solveLoop()"
                if self._pauseExcept is True:
                    ui.displayError("Exception", exceptMsg)
                    r = ("fail", ("except", exceptMsg))
                    break
                else:
                    raise Sudoku_Error(exceptMsg)
        #end loop
        TEST.display("simu", 3, "_solveLoop - Fin de la boucle d'it�rations.")
        return r

    def _iterate(self, pauseExcept):
        '''Joue une it�ration de boucle ROMA (R�fl�chir-Observer/Placer
        -M�moriser-Apprendre). Retourne le r�sultat du coup.
        '''
        TEST = self.env.TEST
        TEST.display("simu", 3, "SudoSimu - dans _iterate()")
        assert self._initOk
        assert self._solving

        try:
            thinkResult = self._think.analyse()
            #diff�rents r�sultats possibles de la r�flexion
            TEST.display("simu", 3, "SudoSimu - Retour � Simu - Action : {0}"\
                                     .format(thinkResult))
            TEST.display("simu", 2, "R�sultat de l'it�ration d'analyse "\
                         ": {0}".format(thinkResult))
            action = thinkResult[0]
            if action == "continue":
                TEST.display("simu", 2, "R�flexion : la r�solution continue.")
            elif action == "observe":
##                nb_stats[1] +=1   #stats
                pattern = thinkResult[1]
                TEST.display("simu", 2, "Observation demand�e: {0}"\
                                        .format(pattern))
                found = self._view.lookup(pattern)
                TEST.display("simu", 1, "R�sultat de l'observation : {0}"\
                                         .format(found))
                self._mem.memorizeObs(found)
            elif action == "place":
##                nb_stats[2] += 1   #stats
                placement = thinkResult[1]
                TEST.display("simu", 1, "Placement demand� : {0}"\
                                        .format(placement))
                valid = self._view.place(placement)
####
#### A FAIRE ICI : transmission du r�sultat de validit� du placement.
#### En utilisant une fonction mem.memorizePlace (� �crire)
####                
                (row, col, chiffre) = placement
                ui.displayGridValue(row, col, chiffre)
            elif action == "end":
                endDetails = thinkResult[1]
                TEST.display("simu", 1, "Fin de la partie")
                TEST.display("simu", 1, "La partie se termine avec le r�sultat "\
                                        ": {0}".format(endDetails))
            elif action =="fail":
                failDetails = thinkResult[1]
                msg = "Le jeu rencontre une difficult� : retour d'erreur (fail)"\
                      " dans le module \'Thinking\', m�thode analyse().\n"\
                      "D�tail : {0}".format(failDetails)
                
                TEST.display("simu", 1, msg)
            else:
                #ne devrait jamais arriver
                TEST.display("simu", 3, "Simu - valeur erron�e retourn�e par "\
                             "think.analyse() dans _iterate().")
                ui.displayError("Erreur", "Module SudoSimu dans _iterate(): "\
                                "valeur invalide retourn�e par think.analyse()")
                raise Sudoku_Error()
        except:
            #G�re les exceptions suivant le param�trage
            exceptMsg = "Exception dans SudoSimu._iterate()"
            if self._pauseExcept is True:
                ui.displayError("Exception", exceptMsg)
                thinkResult = ("except", exceptMsg)
            else:
                raise Sudoku_Error(exceptMsg)
        
        #garder les r�sultats de l'it�ration de r�flexion
        self._lastAction = thinkResult[0]
        self._lastActionDetails = thinkResult[1]
        return thinkResult

    def _pauseContinue(self, solveResult):
        TEST = self.env.TEST
        TEST.display("simu", 1, "Le jeu fait une pause apr�s une it�ration "\
                     "de r�flexion.")
        #� traiter plus compl�tement si besoin
        return solveResult
    
    def _pauseObserve(self, solveResult):
        '''Affiche un message sp�cifique si la boucle de jeu s'est arr�t�e
        sur une observation de la grille.
        '''
        TEST = self.env.TEST
        TEST.display("simu", 1, "Le jeu fait une pause apr�s une observation.")
        #� traiter plus compl�tement si besoin
        return solveResult
                    
    def _pausePlace(self, solveResult):
        '''Affiche un message sp�cifique si la boucle de jeu s'est arr�t�e
        sur un placement dans la grille.
        '''
        TEST = self.env.TEST
        TEST.display("simu", 1, "Le jeu fait une pause apr�s un placement.")
        #� traiter plus compl�tement si besoin
        return solveResult
                    
    def _pauseFail(self, solveResult):
        '''Affiche un message sp�cifique si la boucle de jeu s'est arr�t�e
        sur un retour d'action "fail".
        '''
        TEST = self.env.TEST
        TEST.display("simu", 1, 'Le jeu fait une pause apr�s erreur ("fail")')
        #� traiter plus compl�tement si besoin
        return solveResult

    def _pauseExcept(self, solveResult):
        '''Affiche un message sp�cifique si la boucle de jeu s'est arr�t�e
        sur une exception g�r�e.
        '''
        TEST = self.env.TEST
        TEST.display("simu", 1, "Le jeu fait une pause apr�s exception g�r�e.")
        #� traiter plus compl�tement si besoin
        return

    def _endSimu(self, simuResult):
        ''' L'action retourn�e indique la fin de la partie ("end").
        Traitement du r�sultat de la partie et affichage d'informations
        sp�cifiques pour le joueur.
        '''
        TEST = self.env.TEST
        TEST.display("simu", 1, "Fin de la partie. D�tails des r�sultats "\
                     " : {0}".format(simuResult))
        return simuResult        

##    def reset(self):
##        '''R�initialise l'instance de jeu avec la grille initiale.'''
##        self._grid.copyFrom(self._initGrid)
##        self._initSimu()
##        return

                    
    @property
    def lastAction(self):
        return(self._lastAction, self._lastActionDetails)

##    @property
##    def solveResult(self):
##        return self._solveResult
    

    def showGrid(self, style=None):
        '''Montre la grille dans son �tat actuel, avec le style d'affichage
        indiqu�.
        '''
#        self._grid.show(style)
        return
    
    @property
    def thinkAction(self):
        assert self._initOk
        return self._lastAction

    @property
    def thinkDetails(self):
        assert self._initOk
        return self._lastActionDetails

    @property
    def pauseParams(self):
        assert self._initOk
        return self._pauseParams

    @property
    def finished(self):
        assert self._initOk
        return self._finished

    @property
    def solving(self):
        assert self._initOk
        return self._solving



#TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST
#TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST

if __name__ == "__main__":

#    import sudotestall     #OBSOLETE#

    from sudogrid import SudoGrid
    from test_main import *

    #interface
    env = sudoenv.SudoEnv()
    TEST = env.test
    ui = env.ui
    testlev(0)
    testMakeUI()
    #donn�es de jeu
    grid = None
    gridInit = None
    mem = None
    think = None
    view = None
    simu = None
    params = None
    #fonctions de jeu
    def newGrid():
        global gridInit
        gridInit = testNewGrid()
        newSimu()
        return
    def resetGrid():
        global grid
        global gridInit
        grid = gridInit.copy()
        testShowGrid(grid)
        return
    def newSimu():
        global grid
        global mem
        global think
        global view
        global simu
        resetGrid()
        mem = SudoMemory(env=env)
        think = SudoThinking(mem, env=env)
        view = SudoGridView(grid, env=env)
        simu= SudoSimu(mem, think, view, env)
        return
    def go():
        global simu
        simu.solve(params)
        return

    #Initialisation des tests et de la partie
    TEST.level("main", 1)
    TEST.display("main", 1, "\nTest du module sudosimu")
    TEST.display("main", 1, "----------------------------\n")
    newGrid()
    ui.display("Cr�ation  et initialisation de la partie")
    newSimu()
    #Niveaux de commentaires pour la partie
    TEST.level("thinkai", 1)

    #Param�tres de la partie
    params = None
    #jeu
    TEST.display("main", 1, "Pr�t � jouer.")
    print("\n...>>> simu.solve(params) \nou >>> go()")

    #ui.sudoPause()
    #go()
    

