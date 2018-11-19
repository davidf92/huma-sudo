'''SudoSimu - Module techlplcc - Technique de résolution "dernier placement"
locale sur une colonne.

Ce module contient la classe SudoTechLastPlcCol qui applique la technique
de résolution "dernier placement" localement sur une colonne.
Cette technique locale peut être exécutée soit par AI directement, soit par
une technique globale (par exemple SudoTechLastPlcPlace).
Elle peut aussi être exécutée avec répétition sur la grille ou sur une zone
globale intermédiaire (par exemple SudoLastPlcGrid). Dans cd cas il faut créer
une nouvelle instance de la technique à chaque itération de répétition.

Instanciation :
---------------
   TechLastPlcCol(mem, args)
   args est un tuple qui contient la colonne sur laquelle appliquer la technique

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
Racine commune = "techlplccol_............."
"techlplccol_encours"   -> indique si la technique est en cours d'application
"techlplccol_finished"  -> indique si la technique est terminée
"techlplccol_nbplccol"  -> le nombre de placements faits sur la colonne
"techlplccol_icol"      -> le numéro de la colonne à laquelle s'applique la tech.
"techlplccol_stepcol"   -> étape suivante de résolution
"techlplccol_action_suivante" -> pointeur d'action pour l'itération suivante
"techlplccol_index_obs" -> index d'observations
"techlplccol_obspattern"   -> le tuple de codification de l'observation demandée
"techlplccol_obsfound"  -> résultat d'observation
"techlplccol_coordrow"  -> rang de l'emplacement libre trouvé dans la colonne

change.log
----------
11/10/2017
Suppression des paramètres 'mem' inutiles dans toutes les méthodes
19/09/2017
Cette version est une mise à jour majeure dans le cadre de la simulation des
techniques avec distinction local/global et avec les répétitions
Le code est copié directement du module techlplcr et adapté aux blocs
'col' en remplacement de 'row'. Toute la logique est la même. 

'''

if __name__ in ("__main__", "techlplcc", "techlplc.techlplcc"):
    import sudoui as ui
    import sudorules as rules
    from sudorules import Sudoku_Error
    from sudomemory import SudoMemory
    import sudogridview as gridview
    from sudotest import *
elif __name__ == "sudosimu.techlplc.techlplcc":
    from sudosimu import sudoui as ui
    from sudosimu import sudorules as rules
    from sudosimu.sudorules import Sudoku_Error
    from sudosimu.sudomemory import SudoMemory
    from sudosimu import sudogridview as gridview
    from sudosimu.sudotest import *
else:
    raise Exception("Impossible de faire les imports dans le module techlplcc.")


class TechLastPlcCol():
    '''Classe qui encapsule la technique de résolution 'Dernier placement'
    sur une seule colonne. Pour chaque occurence d'application de la technique,
    une instance est créée.
    Concernant les données en mémoire de l'application, l'utilisation de la
    clé secondaire 'self' évite tout mélange entre deux instances qui seraient
    appliquées simultanément (imbrications).
    '''

    def __init__(self, mem, args):
        '''Initialise l'instance pour appliquer la technique à la colonne
        indiquée en utilisant la mémoire du joueur 'mem'.
        '''
        TEST.display("techlplccol", 3, "TechLastPlcCol - Dans __init__()")
        #l'id de la colonne est passé en argument
        icol = args[0]
        TEST.display("techlplccol", 2, \
                     "Nouvelle instance de la technique TechLastPlcCol"\
                     "appliquée à la colonne {0}".format(icol))
        self._mem = mem
        mem.memorize("techlplccol_icol", icol, self)
        self._clear_tech_mem()
        self._finished = False  #uniquement pour éviter une erreur de code
        self._initOk = True     #n'est plus utilisé si disparition de init()
        return

    def _clear_tech_mem(self):
        '''Prépare toutes les données en mémoire pour la résolution.'''
        TEST.display("techlplccol", 3, "TechLastPlcCol - Dans _clear_tech_mem()"\
                     +"Remise à zéro de toutes les variables d'exécution")
        mem = self._mem
        mem.memorize("techlplccol_finished", False, self)
        mem.memorize("techlplccol_encours", False, self)
        mem.memorize("techlplccol_index_obs", None, self)
        mem.memorize("techlplccol_coordrow", None, self)
        mem.memorize("techlplccol_stepcol", None, self)
        mem.memorize("techlplccol_action_suivante", None, self)
        mem.memorize("techlplccol_nom_action", "", self)
        mem.memorize("techlplccol_nbplccol", 0, self)
        return
        
    def apply(self):
        '''Méthode d'application de cette technique. Elle est appelée
        répétitivement pour faire progresser la technique étape par étape.
        '''
        TEST.display("techlplccol", 3, "TechLastPlcCol - Dans apply()")
        assert self._initOk
        #si la technique est terminée, sortir tout de suite
        if self._finished is True:
            TEST.display("techlplccol", 3,
                         "Technique déjà terminée, sortie immédiate.")
            return ("end", ("finished", None))
        mem = self._mem
        #selon qu'une résolution est déjà en cours ou pas
        if mem.recall("techlplccol_encours", self) is False:
            #pas de résolution en cours : débuter la technique
            TEST.display("techlplccol", 2, \
                         "Technique de résolution \"Dernier placement sur "+
                         "une colonne\"")
            try:
                r = self._start_apply()
            except:
                ui.displayError("Erreur", "Echec de la méthode de résolution.")
                TEST.display("techlplccol", 1, \
                             "ERREUR FATALE : échec de la technique 'dernier "\
                             "placement sur les colonnes.\n"\
                             "la résolution est abandonnée.")
                mem.memorize("techlplccol_encours", None, self)
                r = ("fail", "Erreur d'exécution du programme TechLastPlc.")
        else:
            #déjà une résolution en cours, la continuer
            TEST.display("techlplccol", 2, "LastplcCol suite de la résolution")
            methode = mem.recall("techlplccol_action_suivante", self)
            TEST.display("techlplccol", 3, \
                         "Méthode à exécuter : {0}".format(methode))
            try:
                r = methode()
            except:
                ui.displayError("Erreur", "Echec de la méthode de résolution.")
                TEST.display("techlplccol", 2, \
                             "ERREUR FATALE : échec de la technique 'dernier "\
                             "placement sur les colonnes.\n"\
                             "la résolution est abandonnée.")
                mem.memorize("techlplccol_encours", None, self)
                r = ("fail", "Erreur d'exécution du programme TechLastPlc.")
        return r

    def resume(self):
        '''Méthode de résolution alternative appelée par Thinking dans le cas
        où la technique est continuée après une mise en attente du fait
        de l'imbrication d'autres techniques. Permet de faire des vérifications
        de cohérence des données mémorisées pendant la mise en attente,
        avant de reprendre l'application.
        '''
        TEST.display("techlplccol", 3, "TechLastPlcCol - dans resume()")
        assert self._initOk
        # dans cette version ne fait encore rien de particulier.
        return self.apply()

    def _start_apply(self):
        '''Début de la résolution. Initialisation des informations en mémoire
        et lancement de la résolution des colonnes.
        '''
        TEST.display("techlplccol", 3, "TechLastPlcCol - dans _start_apply()")
        assert self._initOk
        mem = self._mem
        TEST.display("techlplccol", 2, "LastPlcCol : début de résolution.")
        mem.memorize("techlplccol_encours", True, self)
        #comptages
        mem.memorize("techlplccol_nbplccol", 0, self)
        #on commence par l'étape n°1
        mem.memorize("techlplccol_stepcol", 0, self)
        #commencer la résolution des colonnes
        r = self._solve_col()
        return r
        
    def _solve_col(self):
        '''Résolution pour une colonne - Début, demande la 1ère observation :
        quelles sont les cases vides de cette colonne.
        '''
        TEST.display("techlplccol", 3, "TechLastPlcCol - dans _solve_col()")
        assert self._initOk
        mem = self._mem
        #à quelle colonne en est-on ?
        icol = mem.recall("techlplccol_icol", self)
        TEST.display("techlplccol", 3, \
                     "Début de résolution de la colonne n° {0}".format(icol))
        #1ère étape : observer quelles sont les cases vides de la colonne
        obsPattern = (gridview.OBS_COL_EMPTYPLC, (icol,) )
        #mémoriser ce qui a été demandé, pour l'itération suivante
        mem.memorize("techlplccol_obspattern", obsPattern, self)
        #incrémenter l'index d'observations
        mem.increment("techlplccol_indexobs", 1, self)
        #memoriser l'avancement vers l'opération suivante
        mem.memorize("techlplccol_stepcol", 1, self)
        mem.memorize("techlplccol_action_suivante", self._col_suite1, self)
        #réinitialiser l'indicateur de résultat d'observation
        mem.memorize("techlplccol_obsfound", None, self)
        #retourner en indiquant la demande d'observation
        r = ("observe", obsPattern)
        TEST.display("techlplccol", 3, \
                     "Demande 1ère observation : pattern = {0}".format(obsPattern))
        return r

    def _col_suite1(self):
        '''Résolution pour une colonne - Retour 1ère observation.
        S'il y a un bon résultat d'observation, demande la 2ème observation :
        quel est le chiffre manquant sur cette colonne.
        '''
        TEST.display("techlplccol", 3, "TechLastPlcCol - dans _col_suite1()")
        assert self._initOk
        mem = self._mem
        #à quelle colonne en est-on ?
        icol = mem.recall("techlplccol_icol", self)
        TEST.display("techlplccol", 3, \
                     "colonne n° {0} : retour 1ère observation".format(icol))
        #résultat de l'observation : recherche des cases vides de la colonne
        #Attention : gérer les cas de retour d'observation invalide
        try:
            found = mem.recall("techlplccol_obsfound", self)
            assert found is not None
            (nb, listPlc) = found
            assert isinstance(nb, int) and 0 <= nb <= 9
               #on ne va pas tout vérifier non plus, ne pas exagérer.
        except:
            #quelle que soit l'erreur La technique doit être interrompue
            raise Sudoku_Error("Retour d'observation invalide. " +
                               "Technique de résolution abandonnée.")

        #cas où il y a une seule case vide dans la colonne => continuer
        if nb == 1: 
            TEST.display("techlplccol", 3, "_col_suite1() - "\
                         "Colonne {0} : il y a une case vide, ".format(icol)\
                         +"la technique passe à l'étape suivante.")
            #mémoriser l'emplacement trouvé. C'est un indice de rang
            mem.memorize("techlplccol_coordrow", listPlc[0], self)
            #2ème étape : il manque un seul chiffre, lequel est-ce ?
            obsPattern = (gridview.OBS_COL_MISSING, (icol,) )
            #mémoriser ce qui a été demandé, pour l'itération suivante
            mem.memorize("techlplccol_obspattern", obsPattern, self)
            #memoriser l'avancement et l'opération suivante
            mem.memorize("techlplccol_action_suivante", self._col_suite2, self)
            mem.memorize("techlplccol_stepcol", 2, self)
            #réinitialiser l'indicateur de résultat d'observation
            mem.memorize("techlplccol_obsfound", None, self)
            #retourner en indiquant la demande d'observation
            r = ("observe", obsPattern)
        elif nb == 0:       #aucune case vide
            #la technique est terminée sans rien à faire
            r = self._solve_fin("noplace")
            TEST.display("techlplccol", 3, \
                         "Colonne {0} : aucune case vide, c'est terminé" \
                         .format(icol))
        else:            
            #nb>1 => plusieurs cases vides : 
            #dans cette version on ne le gère pas (plus compliqué)
            r = self._solve_fin("quit")
            TEST.display("techlplccol", 3, \
                         "Colonne {0} : {1} cases vide. On ne traite pas ce cas" \
                         .format(icol, nb) + "dans la technique LastPlcCol.")
        return r
        
    def _col_suite2(self):
        '''Résolution pour une colonne - Retour 2ème observation = le chiffre
        manquant. Fait le placement.
        '''
        TEST.display("techlplccol", 3, "TechLastPlcCol - dans _col_suite2()")
        assert self._initOk
        mem = self._mem
        #à quelle colonne en est-on ?
        icol = mem.recall("techlplccol_icol", self)
        TEST.display("techlplccol", 3, \
                     "Colonne n° {0} : retour 2ème observation".format(icol))
        #décodage de la réponse d'observation : quel est le chiffre manquant
        #Attention : gérer les cas de retour d'observation invalide
        try:
            found = mem.recall("techlplccol_obsfound", self)
            assert found is not None
            chiffre = found[1][0]
            assert isinstance(chiffre, int) and 0 <= chiffre <= 9
        except:
            #Quelle que soit l'erreur, la technique doit être interrompue
            raise Sudoku_Error("TechLastPlcCol - Retour d'observation invalide. "\
                               "Technique de résolution abandonnée.")

        #3ème étape : prêt pour placer ce chiffre - se rappeler l'emplacement.
        #l'emplacement était un indice de rang dans cette colonne.
        irow = mem.recall("techlplccol_coordrow", self)
        TEST.display("techlplccol", 2, "_col_suite2() - "\
                     "Placement de {0} dans le rang {1} en colonne {2}" \
                     .format(chiffre, irow, icol))
        #memoriser l'avancement et l'opération suivante
        mem.memorize("techlplccol_stepcol", 3, self)
        mem.memorize("techlplccol_action_suivante", self._col_suite3, self)
        mem.memorize("techlplccol_nom_action", "suite 3", self)
        #réinitialiser l'indicateur de retour de placement
        mem.memorize("techoplccol_placeok", None, self)
        #retourner en indiquant une demande de placement
        r = ("place", (irow, icol, chiffre))
        return r
    
    def _col_suite3(self):
        '''Résolution pour une colonne (Col) - Retour de placement
        Vérifier que la placement a été correct et terminer la technique
        avec succès.'''
        TEST.display("techlplccol", 3, "TechLastPlcCol - dans _col_suite3()")
        assert self._initOk
        mem = self._mem
        #à quelle colonne en est-on ?
        icol = mem.recall("techlplccol_icol", self)
        #vérifier que le placement a été bien réalisé. Sinon c'est une erreur
        #de mémoire, d'algorithme ou de cohérence de la grille.
        try:
            plcOk = mem.recall("techlplccol_placeok", self)
            assert plcOk is True
        except:
            raise Sudoku_Error ("Résultat de placement invalide "\
                                "dans TechLastPlcCol._col_suite3()")
        #Mise à jour comptages.
        nbplccol = mem.increment("techlplccol_nbplccol", 1, self)
        TEST.display("techlplccol", 3, "Colonne n° {0} : retour de placement"\
                     "correct.".format(icol) + "\nNombre de placements : {0}"
                     .format(nbplccol))
        #Etat d'avancement - fin de la technique sur cette colonne
        mem.memorize("techlplccol_stepcol", 4, self)
        r = self._solve_fin("succeed")
        return r

    def _solve_fin(self, endResult="end"):
        """A la fin de résolution de la technique, la marque comme terminée.
        Il faudra appeler 'reset()' avant de la relancer.
        """
        TEST.display("techlplccol", 3, "TechLastPlcCol - dans _solve_fin()")
        assert self._initOk
        mem = self._mem
        nbplccol = mem.recall("techlplccol_nbplccol", self)
        TEST.display("techlplccol", 2, "Fin de la technique \'Dernier placement "\
                     "sur une colonne\'.\nNombre de chiffres placés : {0}"
                     .format(nbplccol))
        self._finish_apply()
        #construire le tuple de détail de résultats
        endDetails = (endResult, nbplccol)
        TEST.display("techlplccol", 2, "TechLastPlcCol - La technique "\
                     "se termine avec le résultat : '{0}'".format(endDetails))
        #retour vers SudoThinking ou une technique globale
        return ("end", endDetails)

    def _finish_apply(self):
        '''Marque la technique comme terminée. Il faudra appeler 'reset()'
        pour la relancer.
        '''
        TEST.display("techlplccol", 3, "TechLastPlcCol - dans _finish_apply()")
        assert self._initOk
        mem = self._mem
        mem.memorize("techlplccol_icol", None, self)
        mem.memorize("techlplccol_finished", True, self)
        mem.memorize("techlplccol_encours", False, self)
        self._finished = True
        return

    def obsFound(self, found):
        '''Prend connaissance du résultat de l'observation demandée par la
        technique.
        '''
        TEST.display("techlplccol", 3, "TechLastPlcCol - dans obsFound()")
        assert self._initOk
        #si la technique est déjà terminée, retourne "end"
        if self._finished is True:
            return ("end", ("finished", None))
        self._mem.memorize("techlplccol_obsfound", found, self)
        return ("continue", None)

    def placeOk(self, placed=True):
        '''Prend connaissance du succès d'un placement par la technique.'''
        TEST.display("techlplccol", 3, "TechLastPlcCol - dans placeOk()")
        assert self._initOk
        #si la technique est déjà terminée, retourne "end"
        if self._finished is True:
            return ("end", ("finished", None))
        self._mem.memorize("techlplccol_placeok", placed, self)        
        return ("continue", None)
        
    def abort(self):
        '''Arrêt d'exécution de la technique avant sa fin et marque la technique
        comme terminée. Il faudra appeler 'reset()' avant de la relancer.
        Retourne le nombre d'actions effectuées avant l'arrêt
        '''
        TEST.display("techlplccol", 3, "TechLastPlcCol - dans abort()")
        TEST.display("techlplccol", 1, "Abandon de la technique en cours")
        nbplccol = self._mem.recall("techlplccol_nbplccol", self)
        TEST.display("techlplccol", 2, \
                     "Nombre total de chiffres placés : {0}" \
                     .format(nbplccol))
        self._mem.memorize("techlplccol_encours", False, self)
        self._finish_apply()
        return ("end", ("abort", nbplccol))

    def reset(self):
        self._clear_tech_mem()
        self._finished = False
        return ("reset", None)

    def status(self):
        """Retourne l'état d'avancement de la technique"""
        TEST.display("techlplccol", 3, "TechLastPlcCol - Dans status()")
        mem = self._mem
        finished = mem.recall("techlplccol_finished", self)
        if finished is True:
            r = ("end",("finished", None))
        else:
            encours = mem.recall("techlplccol_encours", self)
            if encours is False:
                r = ("inactive", None)
            else:
                icol = mem.recall("techlplccol_icol", self)
                step = mem.recall("techlplccol_stepcol", self)
                r = ("active", ("col", icol, step))
        TEST.display("techlplccol", 3,
                     "Statut de la résolution : {0}".format(r))
        return r

        
    def techName(self):
        return "TechLastPlcCol"

    def techClassName():
        return "TechLastPlcCol"
    
    def instName(self):
        return "instance de {0}".format(self.techName())

    def __str__(self):
        return "Technique de résolution 'Dernier placement' sur une colonne"


##TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 
##TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 

if __name__ == "__main__":

    import sudotestall
    testlevel = 3
    TEST.levelAll(testlevel)
    ui.display("Tous les niveaux de test sont à {0}".format(testlevel))

    import sudogrid
#    from sudoobserver import SudoObserver
    
    ui.display("\nTest du module techlplcr")
    ui.display("Test de la technique de résolution LastPlcCol")
    ui.display("------------------------------------------\n")
    list9 = [2,5,0,6,8,0,0,3,4]
    ui.display("Choisir un fichier de test")
    fich = ui.sudoNumTestFich()
    if not fich:
        ui.display("Abandon")
        exit()
    ui.display("Fichier choisi : {0}\n".format(fich))
    vals = ui.sudoFichReadLines(fich)
    ui.display("Variable SudoBloc : bl")
    bl = sudogrid.SudoBloc()
    ui.display("Variable SudoGrid : gr")
    gr = sudogrid.SudoGrid()
    gr.fillByRowLines(vals)
    grid = gr
    ui.display("Grille test choisie : gr = ")
    gr.show()
    
    ui.display("\nVariable SudoMemory : mem")
    mem = SudoMemory()
    ui.display("Variable SudoObserver : obs")
    view = gridview.SudoGridView(gr)
    #obs = SudoObserver()
    ui.display("Création de 2 instances de technique de résolution.")
    ui.display("Instance de technique TechLastPlc : tech1 et tech2")
    tech1 = TechLastPlcCol(mem, (1,))
    tech2 = TechLastPlcCol(mem, (1,))
    ui.display("\nTEST au niveau 3\n")
    TEST.test("techlplccol",3)
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
    tech1 = TechLastPlcCol(mem, (1,))
    tech2 = TechLastPlcCol(mem, (1,))
    gr.fillByRowLines(vals)
