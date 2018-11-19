'''SudoSimu - Module techlplcr - Technique de résolution "dernier placement"
locale sur un rang.

Ce module contient la classe SudoTechLastPlcRow qui applique la technique
de résolution "dernier placement" localement sur un rang.
Cette technique locale peut être exécutée soit par AI directement, soit par
une technique globale (par exemple SudoTechLastPlcPlace).
Elle peut aussi être exécutée avec répétition sur la grille ou sur une zone
globale intermédiaire (par exemple SudoLastPlcGrid). Dans cd cas il faut créer
une nouvelle instance de la technique à chaque itération de répétition.

Instanciation :
---------------
   TechLastPlcRow(mem, args)
   args est un tuple qui contient le rang sur lequel appliquer la technique

Méthodes publiques :
--------------------
   apply():            Méthode principale d'application de la technique
   resume():           Application quand la technique a été suspendue par l'AI
   obsFound(found):    Prise en compte d'un résultat d'observation
   placeOk(placed):    Prise en compte d'une confirmation de placement
   abort():            Demande d'abandon de la technique par l'AI
   reset():            Réinitialisation de la technique
   status():           Demande du statut (initialisée, en cours, terminée, etc.)

Données mémoire utilisées :
---------------------------
Racine commune = "techlplcrow_............."
"techlplcrow_encours"   -> indique si la technique est en cours d'application
"techlplcrow_finished"  -> indique si la technique est terminée
"techlplcrow_nbplcrow"  -> le nombre de placements faits sur le rang
"techlplcrow_irow"      -> le numéro du rang auquel s'applique la technique
"techlplcrow_steprow"   -> étape suivante de résolution
"techlplcrow_action_suivante" -> pointeur d'action pour l'itération suivante
"techlplcrow_index_obs" -> index d'observations
"techlplcrow_obspattern"   -> le tuple de codification de l'observation demandée
"techlplcrow_obsfound"  -> résultat d'observation
"techlplcrow_coordcol"  -> colonne de l'emplacement libre trouvé dans le rang

change.log
----------
11/10/2017
Suppression des paramètres 'mem' inutiles dans toutes les méthodes
19/09/2017
Cette version est une mise à jour majeure dans le cadre de la simulation des
techniques avec distinction local/global et avec les répétitions

'''

if __name__ in ("__main__", "techlplcr", "techlplc.techlplcr"):
    import sudoui as ui
    import sudorules as rules
    from sudorules import Sudoku_Error
    from sudomemory import SudoMemory
    import sudogridview as gridview
    from sudotest import *
elif __name__ == "sudosimu.techlplc.techlplcr":
    from sudosimu import sudoui as ui
    from sudosimu import sudorules as rules
    from sudosimu.sudorules import Sudoku_Error
    from sudosimu.sudomemory import SudoMemory
    from sudosimu import sudogridview as gridview
    from sudosimu.sudotest import *
else:
    raise Exception("Impossible de faire les imports dans le module techlplcr.")


class TechLastPlcRow():
    '''Classe qui encapsule la technique de résolution 'Dernier placement'
    sur un seul rang. Pour chaque occurence d'application de la technique,
    une instance est créée.
    Concernant les données en mémoire de l'application, l'utilisation de la
    clé secondaire 'self' évite tout mélange entre deux instances qui seraient
    appliquées simultanément (imbrications).
    '''

    def __init__(self, mem, args):
        '''Initialise l'instance pour appliquer la technique au rang indiqué
        en utilisant la mémoire du joueur 'mem'.
        '''
        TEST.display("techlplcrow", 3, "TechLastPlcRow - Dans __init__()")
        #vérifier la validité des arguments de l'instanciation
        try:
            irow = args[0]
            assert isinstance(irow, int) and 1<= irow <= 9
        except:
            raise Sudoku_Error("TechLastPlcRow instanciée avec des arguments "\
                               "invalides : {0}".format(args))
        TEST.display("techlplcrow", 2, \
                     "Nouvelle instance de la technique TechLastPlcRow"\
                     "appliquée au rang {0}".format(irow))
        self._mem = mem
        self._irow = irow
        mem.memorize("techlplcrow_irow", irow, self)
        self._clear_tech_mem()
        self._finished = False  #uniquement pour éviter une erreur de code
        self._initOk = True     #n'est plus utilisé si disparition de init()
        return

    def _clear_tech_mem(self):
        '''Initialise les données mémorisées pour le déroulement de la
        techniques étape par étape.
        '''
        TEST.display("techlplcrow", 3, "TechLastPlcRow - Dans _clear_tech_mem()"\
                     +"Remise à zéro de toutes les variables d'exécution")
        mem = self._mem
        mem.memorize("techlplcrow_finished", False, self)
        mem.memorize("techlplcrow_encours", False, self)
        mem.memorize("techlplcrow_index_obs", None, self)
        mem.memorize("techlplcrow_coordcol", None, self)
        mem.memorize("techlplcrow_steprow", None, self)
        mem.memorize("techlplcrow_action_suivante", None, self)
        mem.memorize("techlplcrow_nom_action", "", self)
        mem.memorize("techlplcrow_nbplcrow", 0, self)
        return
        
    def apply(self):
        '''Méthode d'application de cette technique. Elle est appelée
        répétitivement pour faire progresser la technique étape par étape.
        '''
        TEST.display("techlplcrow", 3, "TechLastPlcRow - Dans apply()")
        assert self._initOk
        #si la technique est terminée, sortir tout de suite
        if self._finished is True:
            TEST.display("techlplcrow", 3,
                         "Technique déjà terminée, sortie immédiate.")
            return ("end", ("finished", None))
        mem = self._mem
        
        #quand apply() est appelée la première fois, la technique n'est pas
        #encore en cours. Il faut commencer son application.
        if mem.recall("techlplcrow_encours", self) is False:
            TEST.display("techlplcrow", 3, \
                         "TechLastPlcRow - Début de résolution.")
            TEST.display("techlplcrow", 2, \
                         "Technique de résolution \"Dernier placement sur "+
                         "un rang\" pour le rang {0}".format(self._irow))
            TEST.display("techlplcrow", 3, "TechLastPlcRow - Etape à exécuter : "\
                         "première étape.")
            try:
                r = self._start_apply()
                TEST.display("techlplcrow", 3, "TechCLastPlcRow - retour à apply()")
                mem.memorize("techlplcrow_encours", True, self)
            except:
                TEST.display("techlplcrow", 1, \
                        "Erreur : échec de la technique 'dernier "\
                        "placement' sur le rang {0}.\n"\
                        .format(self.irow) + "La résolution est abandonnée.")
                mem.memorize("techlplcrow_encours", False, self)
                mem.memorize("techlplcrow_finished", False, self)
                self._finished = True
                r = ("fail", "Erreur d'exécution du programme TechLastPlc.")
                raise Sudoku_Error("TechLastPlcRow - Erreur dans apply()")

        #quand il y a déjà une résolution en cours
        else:
            TEST.display("techlplcrow", 2, "LastplcRow suite de la résolution")
            methode = mem.recall("techlplcrow_action_suivante", self)
            nom = mem.recall("techlplcrow_nom_action", self)
            TEST.display("techlplcrow", 3, "TechLastPlcRow - Etape à exécuter "\
                         " : {0}".format(nom))
            try:
                r = methode()
                TEST.display("techlplcrow", 2, "LastplcRow - retour à apply()")
            except:
                TEST.display("techlplcrow", 1, \
                        "Erreur : échec de la technique 'dernier "\
                        "placement' sur le rang {0}.\n"\
                        .format(self._irow) + "La résolution est abandonnée.")
                mem.memorize("techlplcrow_encours", False, self)
                mem.memorize("techlplcrow_finished", True, self)
                self._finished = True
                r = ("fail", "Erreur d'exécution de la technique "\
                              "TechLastPlcRow.")
                raise Sudoku_Error("TechlastPlcRow - Erreur dans apply()")
        return r

    def resume(self):
        '''Méthode de résolution alternative appelée par Thinking dans le cas
        où la technique est continuée après une mise en attente du fait
        de l'imbrication d'autres techniques. Permet de faire des vérifications
        de cohérence des données mémorisées pendant la mise en attente,
        avant de reprendre l'application.
        '''
        TEST.display("techlplcrow", 3, "TechLastPlcRow - dans resume()")
        assert self._initOk
        # dans cette version ne fait encore rien de particulier.
        return self.apply()

    def _start_apply(self):
        '''Début de la résolution. Initialisation des informations en mémoire
        et lancement de la résolution des rangs.
        '''
        TEST.display("techlplcrow", 3, "TechLastPlcRow - dans _start_apply()")
        TEST.display("techlplcrow", 2, "LastPlcRow : début de résolution.")
        assert self._initOk
        mem = self._mem
        mem.memorize("techlplcrow_encours", True, self)
        #comptages
        mem.memorize("techlplcrow_nbplcrow", 0, self)
        #on commence par l'étape n°1
        mem.memorize("techlplcrow_steprow", 0, self)
        #commencer la résolution des rangs
        r = self._solve_debut()
        return r
        
    def _solve_debut(self):
        '''Résolution pour un rang - Début, demande la 1ère observation : quelles
        sont les cases vides de ce rang.
        '''
        TEST.display("techlplcrow", 3, "TechLastPlcRow - dans _solve_debut()")
        assert self._initOk
        mem = self._mem
        #à quel rang en est-on ?
        irow = mem.recall("techlplcrow_irow", self)
        TEST.display("techlplcrow", 3, "_solve_debut() - "\
                     "Début de résolution du rang n° {0}".format(irow))
        #1ère étape : observer quelles sont les cases vides du rang
        obsPattern = (gridview.OBS_ROW_EMPTYPLC, (irow,) )
        #mémoriser ce qui a été demandé, pour l'itération suivante
        mem.memorize("techlplcrow_obspattern", obsPattern, self)
        #incrémenter l'index d'observations
        mem.increment("techlplcrow_indexobs", 1, self)
        #memoriser l'avancement vers l'opération suivante
        mem.memorize("techlplcrow_steprow", 1, self)
        mem.memorize("techlplcrow_action_suivante", self._solve_suite1, self)
        mem.memorize("techlplcrow_nom_action", "suite 1", self)
        #réinitialiser l'indicateur de résultat d'observation
        mem.memorize("techlplcrow_obsfound", None, self)
        #retourner en indiquant la demande d'observation
        TEST.display("techlplcrow", 3, "_solve_debut() - Demande 1ère "\
                     "observation : pattern = {0}".format(obsPattern))
        r = ("observe", obsPattern)
        return r

    def _solve_suite1(self):
        '''Résolution pour un rang (Row) - Retour 1ère observation.
        S'il y a un bon résultat d'observation, demande la 2ème observation :
        quel est le chiffre manquant sur ce rang.
        '''
        TEST.display("techlplcrow", 3, "TechLastPlcRow - dans _solve_suite1()")
        assert self._initOk
        mem = self._mem
        #à quel rang en est-on ?
        irow = mem.recall("techlplcrow_irow", self)
        TEST.display("techlplcrow", 3, "_solve_suite1() - rang n° {0} : "\
                     "retour 1ère observation".format(irow))
        #résultat de l'observation : recherche des cases vides du rang
        #gérer les cas de retour d'observation invalide  
        try:
            found = mem.recall("techlplcrow_obsfound", self)
            assert found is not None
            (nb, listPlc) = found
            assert isinstance(nb, int) and 0 <= nb <= 9
               #on ne va pas tout vérifier non plus, ne pas exagérer.
        except:
            #quelle que soit l'erreur la technique doit être interrompue.
            raise Sudoku_Error("Retour d'observation invalide. " +
                               "Technique de résolution abandonnée.")
        #cas où il y a une seule case vide dans le rang
        if nb == 1:
            TEST.display("techlplcrow", 3, "_solve_suite1() - "\
                         "Rang {0} : il y a une case vide, ".format(irow)\
                         +"la technique passe à l'étape suivante.")
            #mémoriser l'emplacement trouvé. C'est un indice de colonne
            mem.memorize("techlplcrow_coordcol", listPlc[0], self)
            #Passer à la 2ème étape : quel est le chiffre manquant ?
            obsPattern = (gridview.OBS_ROW_MISSING, (irow,) )
            #mémoriser ce qui a été demandé, pour l'itération suivante
            mem.memorize("techlplcrow_obspattern", obsPattern, self)
            #memoriser l'avancement et l'opération suivante
            mem.memorize("techlplcrow_action_suivante", self._solve_suite2, self)
            mem.memorize("techlplcrow_nom_action", "suite 2", self)
            mem.memorize("techlplcrow_steprow", 2, self)
            #réinitialiser l'indicateur de résultat d'observation
            mem.memorize("techlplcrow_obsfound", None, self)
            #retourner en indiquant la demande d'observation
            r = ("observe", obsPattern)
        #cas où il n'y a aucune case vide
        elif nb == 0:       
            #la technique est terminée sans rien à faire
            TEST.display("techlplcrow", 3, "_solve_suite1() - "\
                         "Rang {0} : aucune case vide, c'est terminé"\
                         .format(irow))
            r = self._solve_fin("noplace")
        else:            
            #nb>1 => plusieurs cases vides : 
            #dans cette version on ne le gère pas (plus compliqué)
            TEST.display("techlplcrow", 3, "_solve_suite1() - "\
                         "Rang {0} : {1} cases vide. On ne traite pas ce cas"\
                         .format(irow, nb) + "dans la technique LastPlcRow.")
            r = self._solve_fin("quit")
        return r
        
    def _solve_suite2(self):
        '''Résolution pour un rang (Row) - Retour 2ème observation = le chiffre
        manquant. Fait le placement.
        '''
        TEST.display("techlplcrow", 3, "TechLastPlcRow - dans _solve_suite2()")
        assert self._initOk
        mem = self._mem
        #à quel rang en est-on ?
        irow = mem.recall("techlplcrow_irow", self)
        TEST.display("techlplcrow", 3, "_solve_suite2() - "\
                     "Rang n° {0} : retour 2ème observation".format(irow))
        #décodage de la réponse d'observation : quel est le chiffre manquant
        #Attention : gérer les cas de retour d'observation invalide
        try:
            found = mem.recall("techlplcrow_obsfound", self)
            assert found is not None
            chiffre = found[1][0]
            assert isinstance(chiffre, int) and 0 <= chiffre <= 9
        except:
            #Quelle que soit l'erreur, la technique doit être interrompue
            raise Sudoku_Error("TechLastPlcRow - Retour d'observation invalide. "\
                               "Technique de résolution abandonnée.")

        #3ème étape : prêt pour placer ce chiffre - se rappeler l'emplacement.
        #l'emplacement était un indice de colonne dans ce rang.
        icol = mem.recall("techlplcrow_coordcol", self)
        TEST.display("techlplcrow", 2, "_solve_suite2() - "\
                     "Placement de {0} dans le rang {1} en colonne {2}" \
                     .format(chiffre, irow, icol))
        #memoriser l'avancement et l'opération suivante
        mem.memorize("techlplcrow_steprow", 3, self)
        mem.memorize("techlplcrow_action_suivante", self._solve_suite3, self)
        mem.memorize("techlplcrow_nom_action", "suite 3", self)
        #réinitialiser l'indicateur de retour de placement
        mem.memorize("techoplcrow_placeok", None, self)
        #retourner en indiquant une demande de placement
        r = ("place", (irow, icol, chiffre))
        return r
    
    def _solve_suite3(self):
        '''Résolution pour un rang (Row) - Retour de placement
        Vérifier que la placement a été correct et terminer la technique
        avec succès.'''
        TEST.display("techlplcrow", 3, "TechLastPlcRow - dans _solve_suite3()")
        assert self._initOk
        mem = self._mem
        #à quel rang en est-on ?
        irow = mem.recall("techlplcrow_irow", self)
        #vérifier que le placement a été bien réalisé. Sinon c'est une erreur
        #de mémoire, d'algorithme ou de cohérence de la grille.
        try:
            plcOk = mem.recall("techlplcrow_placeok", self)
            assert plcOk is True
        except:
            raise Sudoku_Error ("Résultat de placement invalide "\
                                "dans TechLastPlcRow._solve_suite3()")
        #Mise à jour comptages.
        nbplcrow = mem.increment("techlplcrow_nbplcrow", 1, self)
        TEST.display("techlplcrow", 3, "_solve_suite3() - "\
                     "Rang n° {0} : retour de placement correct.".format(irow)\
                     + "\nNombre de placements : {0}".format(nbplcrow))
        #Etat d'avancement - fin de la technique sur ce rang
        mem.memorize("techlplcrow_steprow", 4, self)
        r = self._solve_fin("succeed")
        return r

    def _solve_fin(self, endResult="end"):
        """A la fin de résolution de la technique, la marque comme terminée.
        Il faudra appeler 'reset()' avant de la relancer.
        """
        TEST.display("techlplcrow", 3, "TechLastPlcRow - dans _solve_fin()")
        assert self._initOk
        mem = self._mem
        nbplcrow = mem.recall("techlplcrow_nbplcrow", self)
        TEST.display("techlplcrow", 2, \
                     "Fin de la technique \'Dernier placement sur un rang\'. "\
                     "\nNombre de chiffres placés : {0}".format(nbplcrow))
        self._finish_apply()
        #construire le tuple de détail de résultats
        endDetails = (endResult, nbplcrow)
        TEST.display("techlplcrow", 2, "TechLastPlcRow - La technique "\
                     "se termine avec le résultat : '{0}'".format(endDetails))
        #retour vers SudoThinking ou une technique globale
        return ("end", endDetails)

    def _finish_apply(self):
        '''Marque la technique comme terminée. Il faudra appeler 'reset()'
        pour la relancer.
        '''
        TEST.display("techlplcrow", 3, "TechLastPlcRow - dans _finish_apply()")
        assert self._initOk
        mem = self._mem
        mem.memorize("techlplcrow_irow", None, self)
        mem.memorize("techlplcrow_finished", True, self)
        mem.memorize("techlplcrow_encours", False, self)
        self._finished = True
        return

    def obsFound(self, found):
        '''Prend connaissance du résultat de l'observation demandée par la
        technique.
        '''
        TEST.display("techlplcrow", 3, "TechLastPlcRow - dans obsFound()")
        assert self._initOk
        #si la technique est déjà terminée, retourne "end"
        if self._finished is True:
            return ("end", ("finished", None))
        self._mem.memorize("techlplcrow_obsfound", found, self)
        return ("continue", None)

    def placeOk(self, placed=True):
        '''Prend connaissance du succès d'un placement par la technique.'''
        TEST.display("techlplcrow", 3, "TechLastPlcRow - dans placeOk()")
        assert self._initOk
        #si la technique est déjà terminée, retourne "end"
        if self._finished is True:
            return ("end", ("finished", None))
        self._mem.memorize("techlplcrow_placeok", placed, self)        
        return ("continue", None)
        
    def abort(self):
        '''Arrêt d'exécution de la technique avant sa fin et marque la technique
        comme terminée. Il faudra appeler 'reset()' avant de la relancer.
        Retourne le nombre d'actions effectuées avant l'arrêt
        '''
        TEST.display("techlplcrow", 3, "TechLastPlcRow - dans abort()")
        TEST.display("techlplcrow", 1, "Abandon de la technique en cours")
        nbplcrow = self._mem.recall("techlplcrow_nbplcrow", self)
        TEST.display("techlplcrow", 2, \
                     "Nombre total de chiffres placés : {0}" \
                     .format(nbplcrow))
        self._mem.memorize("techlplcrow_encours", False, self)
        self._finish_apply()
        return ("end", ("abort", nbplcrow))

    def reset(self):
        self._clear_tech_mem()
        self._finished = False
        return ("reset", None)

    def status(self):
        """Retourne l'état d'avancement de la technique"""
        TEST.display("techlplcrow", 3, "TechLastPlcRow - Dans status()")
        mem = self._mem
        finished = mem.recall("techlplcrow_finished", self)
        if finished is True:
            r = ("end", ("finished", None))
        else:
            encours = mem.recall("techlplcrow_encours", self)
            if encours is False:
                r = ("inactive", None)
            else:
                irow = mem.recall("techlplcrow_irow", self)
                step = mem.recall("techlplcrow_steprow", self)
                r = ("active", ("row", irow, step))
        TEST.display("techlplcrow", 3,
                     "Statut de la résolution : {0}".format(r))
        return r
        
    def techName(self):
        return "TechLastPlcRow"

    def techClassName():
        return "TechLastPlcRow"
    
    def instName(self):
        return "instance de {0}".format(self.techName())

    def __str__(self):
        return "Technique de résolution 'Dernier placement' sur un rang"


##TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 
##TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 

def readGridFile():
    ui.display("Choisir un fichier de test")
    fich = ui.sudoNumTestFich()
    if not fich:
        ui.display("Abandon")
        exit()
    ui.display("Fichier choisi : {0}\n".format(fich))
    vals = ui.sudoFichReadLines(fich)
    return vals

def newGrid():
    vals = readGridFile()
    grid.fillByRowLines(vals)
    gridInit.copyFrom(grid)
    ui.display("Grille test choisie : grid = ")
    grid.show()
    ui.displayGridAll(grid)

def level(lev):
    TEST.levelAll(lev)


if __name__ == "__main__":

    import sudogrid

    #TEST
    import sudotestall
    testlevel = 3
    TEST.levelAll(testlevel)
    ui.display("Tous les niveaux de test sont à {0}".format(testlevel))

    #mode GUI
    ui.UImode(ui.GUI)
    TEST.displayUImode(MODE_BOTH, 1)

    #Grille
    TEST.display("main", 1, "\nCréation de la grille")
    grid = sudogrid.SudoGrid()
    gridInit = sudogrid.SudoGrid()
    newGrid()
    
    ui.display("\nTest du module techlplcr")
    ui.display("Test de la technique de résolution LastPlcRow")
    ui.display("------------------------------------------\n")

    ui.display("\nVariable SudoMemory : mem")
    mem = SudoMemory()
    ui.display("Variable SudoObserver : obs")
    ui.display("Instance de la technique de résolution : tech")
    tech = TechLastPlcRow(mem, (1,))
    ui.display("\nTEST au niveau 3\n")
    TEST.test("loop", 0)
    ui.sudoPause()

def reset():
    '''remet la grille de test dans son état initial et crée de nouvelles
    instances de la technique de résolution.
    '''
    del(mem)
    del(tech1)
    del(tech2)
    mem = SudoMemory
    tech1 = TechLastPlcRow(mem, (1,))
    tech2 = TechLastPlcRow(mem, (1,))
    gr.fillByRowLines(vals)
