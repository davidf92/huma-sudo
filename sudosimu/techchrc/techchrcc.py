'''SudoSimu - Module techchrcr - Technique de résolution "chiffre/rang-colonne"
locale pour un certain chiffre et sur une certaine colonne de carrés.

Ce module contient la classe TechChRCcol qui applique localement la
technique de résolution "chiffre/rang-colonne" sur un chiffre et une colonne de
carrés (147 ou 258 ou 369).
Cette technique locale peut être exécutée soit par AI directement, soit par
la technique locale TechChRCsqr sur un seul carré. Elle peut aussi être
exécutée par une technique globale de répétition sur la grille. Dans cd cas
il faut créer une nouvelle instance de la technique à chaque itération de
répétition.

Instanciation :
---------------
   TechChRCcol(mem, args) - avec  args = (chiffre, colonne) 
   La colonne est l'une des trois colonnes de la colonne de carrés sur lequel va
   être faite l'application de la technique.
   
Méthodes publiques :
--------------------
   apply()          Méthode principale d'application de la technique
   resume()         Application quand la technique a été suspendue par l'AI
   obsFound(found)  Prise en compte d'un résultat d'observation
   placeOk(placed)  Prise en compte d'une confirmation de placement
   abort()          Demande d'abandon de la technique par l'AI
   reset()          Réinitialisation de l'application ##ATTENTION: voir init()
   status()         Retourne le statut (initialisée, en cours, terminée, etc.)
   techName()       Retourne le nom de la technique de résolution
   techClassName    Retourne le nom de la classe 
   techInstName     Retourne le nom de l'instance
   __str__()

Données mémoire utilisées :
---------------------------
Clé commune = "techchrccol_xxxxxxxx"
"techchrccol_encours"   -> indique si la technique est en cours d'application
"techchrccol_finished"  -> indique si la technique est terminée
"techchrccol_nbplccol"  -> le nombre de placements faits sur la colonne
"techchrccol_chiffre"   -> chiffre pour lequel est appliquée la technique
"techchrccol_icol"      -> colonne à laquelle s'applique la technique
"techchrccol_isqcol"    -> colonne de carrés à laquelle s'applique la technique
"techchrccol_isqr"  -> carré où le chiffre manque
"techchrccol_colmiss"   -> colonne où le chiffre manque
"techchrccol_colsmiss"  -> rangs où le chiffre manque
"techchrccol_availplc   -> cases disponibles pour un placement
"techchrccol_stepcol"   -> étape suivante de résolution
"techchrccol_action_suivante" -> pointeur d'action pour l'itération suivante
"techchrccol_index_obs" -> index d'observations
"techchrccol_obspattern"   -> le tuple de codification de l'observation demandée
"techchrccol_placement" -> le tuple de codification du placement demandé
"techchrccol_obsfound"  -> résultat d'observation
"techchrccol_placeok"   -> résultat de placement
"techchrccol_result"    -> résultat de l'itération de la technique

change.log
----------
03/05/2017
Adaptation au remplacement de la classe SudoObserver par SudoGridView
et placement fait avec cette classe.
04/04/2017
Version initiale

'''

#imports des modules de la simulation
if __name__ in ("__main__", "techchrcc", "techchrc.techchrcc"):
    import sudoui as ui
    import sudorules as rules
    from sudorules import Sudoku_Error
    from sudomemory import SudoMemory
    import sudogridview as gridview
    from sudotest import *
elif __name__ == "sudosimu.techchrc.techchrcc":
    from sudosimu import sudoui as ui
    from sudosimu import sudorules as rules
    from sudosimu.sudorules import Sudoku_Error
    from sudosimu.sudomemory import SudoMemory
    from sudosimu import sudogridview as gridview
    from sudosimu.sudotest import *
else:
    raise Exception("Impossible de faire les imports dans le module techchrcc.")


class TechChRCcol():
    '''Classe qui encapsule la technique de résolution 'Chiffre rang/colonne'
    sur une seule colonne de carrés. Pour chaque occurence d'application de la
    technique, une instance est créée.
    Concernant les données en mémoire de l'application, l'utilisation de la
    clé secondaire 'self' évite tout mélange entre deux instances qui seraient
    appliquées simultanément (imbrications).
    '''

    def __init__(self, mem, args):
        '''Initialise l'instance pour appliquer la technique à la colonne
        de carrés indiquée en utilisant la mémoire du joueur 'mem'.
        '''
        TEST.display("techchrccol", 3, "TechChRCcol - Dans __init__()")
        #arguments de l'instanciation - vérifier leur validité
        try:
            chiffre = args[0]
            assert isinstance(chiffre, int) and 1 <= chiffre <= 9
            icol = args[1]
            assert isinstance(icol, int) and 1 <= icol <= 9
        except:
            raise Sudoku_Error("TechChRCcol instanciée avec des arguments "\
                               "invalides : {0}".format(args))
        TEST.display("techchrccol", 2, \
                     "Nouvelle instance de la technique TechChRCcol "\
                     "appliquée à la colonne {0} pour le chiffre {1}"
                     .format(icol, chiffre))
        self._mem = mem
        self._chiffre = chiffre
        self._icol = icol
        mem.memorize("techchrccol_chiffre", chiffre, self)
        mem.memorize("techchrccol_icol", icol, self)
        #déterminer la colonne de carrés. on utilise la première colonne = 1,2,3
        isqcol = 1 + (icol-1)//3
        TEST.display("techchrccol", 3, "La colonne {0} correspond ".format(icol)\
                     + "à la colonne de carrés {0}".format(isqcol))
        mem.memorize("techchrccol_isqcol", isqcol, self)
        self._clear_tech_mem()
        self._finished = False  #uniquement pour éviter une erreur de code
        self._initOk = True     #n'est plus utilisé si disparition de init()
        return

    def _clear_tech_mem(self):
        '''Prépare toutes les données en mémoire pour la résolution.'''
        TEST.display("techchrccol", 3, "TechChRCcol - Dans _clear_tech_mem() "\
                     "Remise à zéro de toutes les variables d'exécution.")
        mem = self._mem
        mem.memorize("techchrccol_colmiss", None, self)
        mem.memorize("techchrccol_finished", False, self)
        mem.memorize("techchrccol_encours", False, self)
        mem.memorize("techchrccol_index_obs", None, self)
        mem.memorize("techchrccol_stepcol", None, self)
        mem.memorize("techchrccol_action_suivante", None, self)
        mem.memorize("techchrccol_nom_action", None, self)
        mem.memorize("techchrccol_nbplccol", 0, self)
        
#### import des fonctions d'étapes successives de l'algorithme d'application
    if __name__ in ("__main__", "techchrcc", "techchrc.techchrcc"):
        from techchrc.techchrcc2 import _start_apply
        from techchrc.techchrcc2 import _solve_debut
        from techchrc.techchrcc2 import _solve_suite1
        from techchrc.techchrcc2 import _solve_suite2
        from techchrc.techchrcc2 import _solve_suite3
        from techchrc.techchrcc2 import _solve_suite4
        from techchrc.techchrcc2 import _solve_suite5
        from techchrc.techchrcc2 import _solve_fin
        from techchrc.techchrcc2 import _finish_apply
    elif __name__ == "sudosimu.techchrc.techchrcc":
        from sudosimu.techchrc.techchrcc2 import _start_apply
        from sudosimu.techchrc.techchrcc2 import _solve_debut
        from sudosimu.techchrc.techchrcc2 import _solve_suite1
        from sudosimu.techchrc.techchrcc2 import _solve_suite2
        from sudosimu.techchrc.techchrcc2 import _solve_suite3
        from sudosimu.techchrc.techchrcc2 import _solve_suite4
        from sudosimu.techchrc.techchrcc2 import _solve_suite5
        from sudosimu.techchrc.techchrcc2 import _solve_fin
        from sudosimu.techchrc.techchrcc2 import _finish_apply
    else:
        raise Exception("Impossible de faire les imports dans le module techchrcc.")
####

    def apply(self):
        '''Méthode d'application de cette technique. Elle est appelée
        répétitivement pour faire progresser la technique étape par étape.
        '''
        TEST.display("techchrccol", 3, "TechChRCcol - Dans apply()")
        assert self._initOk
        mem = self._mem
        #si la technique est terminée, sortir tout de suite
        if self._finished is True:
            TEST.display("techchrccol", 3,
                         "Technique terminée, sortie immédiate.")
            return ("end", ("finished", None))
        
        #quand apply() est appelée la première fois, la technique n'est pas
        #encore en cours. Il faut commencer son application.
        if mem.recall("techchrccol_encours", self) is False:
            TEST.display("techchrccol", 3, "TechChRCcol - Début de résolution.")
            TEST.display("techchrccol", 2, \
                         "Technique de résolution \"Chiffre/rang-colonne\" "\
                         "sur la colonne {0} pour le chiffre {1}."
                         .format(self._icol, self._chiffre))
            TEST.display("techchrccol", 3, "TechChRCcol - Etape à exécuter : "\
                                             "première étape.")
            try:
                r = self._start_apply()
                TEST.display("techchrccol", 3, "TechChRCcol - retour à apply()")
                mem.memorize("techchrccol_encours", True, self)
            except:
                TEST.display("techchrccol", 1, \
                             "Erreur : échec de la technique 'chiffre/ "\
                             "rang-colonne'sur la colonne {0}.\n"\
                             .format(self_icol)+"La résolution est abandonnée.")
                mem.memorize("techchrccol_encours", False, self)
                mem.memorize("techchrccol_finished", True, self)
                self._finished = True
                r = ("end",
                     ("fail",
                      "Erreur d'exécution de la technique TechChRCcol."))
                raise Sudoku_Error("TechChRCcol - Erreur dans apply()")
        else:
            #déjà une résolution en cours, la continuer
            TEST.display("techchrccol", 2, "ChRCcol suite de la résolution")
            methode = mem.recall("techchrccol_action_suivante", self)
            nom = mem.recall("techchrccol_nom_action", self)
            TEST.display("techchrccol", 3, "TechChRCcol - Etape à exécuter : "\
                                             "{0}.".format(nom))
            try:
                r = methode()
                TEST.display("techchrccol", 3, "TechChRCcol - retour à apply()")
            except:
                ui.displayError("Erreur", "Echec de la méthode de résolution.")
                TEST.display("techchrccol", 1, \
                             "ERREUR FATALE : échec de la technique 'chiffre / "\
                             "rang-colonne' sur la colonne {0}.\n"\
                             .format(self._icol)+"La résolution est abandonnée.")
                mem.memorize("techchrccol_encours", False, self)
                mem.memorize("techchrccol_finished", True, self)
                self._finished = True
                r = ("end",
                     ("fail",
                      "Erreur d'exécution de la technique TechChRCcol."))
                raise Sudoku_Error("TechChRCcol - Erreur dans Apply()")
        return r

    def resume(self):
        '''Méthode de résolution alternative appelée par Thinking dans le cas
        où la technique est continuée après une mise en attente du fait
        de l'imbrication d'autres techniques. Permet de faire des vérifications
        de cohérence des données mémorisées pendant la mise en attente,
        avant de reprendre l'application.
        '''
        TEST.display("techchrccol", 3, "TechChRCcol - dans resume()")
        assert self._initOk
        # dans cette version ne fait encore rien de particulier.
        return self.apply()


    def obsFound(self, found):
        '''Prend connaissance du résultat de l'observation demandée par la
        technique. Fait progresser la technique dans un nouvel état stable.
        Retourne "continue" ou "end" si la technique est terminée.
        '''
        TEST.display("techchrccol", 3, "TechChRCcol - dans obsFound()")
        assert self._initOk
        #si la technique est déjà terminée, retourne "end"
        if self._finished is True:
            r = ("end", ("finished", None))
        else:
        #mémorise le résultat d'observation et continue 
            self._mem.memorize("techchrccol_obsfound", found, self)
            TEST.display("techchrccol", 3, "Résultat d'observation engistré "\
                         " : {0}".format(found))
            r = ("continue", None)
        return r

    def placeOk(self, placed):
        '''Prend connaissance du succès d'un placement par la technique. Fait
        progresser la technique dans un nouvel état stable.
        Retourne "continue" ou "end" si la technique est terminée.
        '''
        TEST.display("techchrccol", 3, "TechChRCcol - dans placeOk()")
        assert self._initOk
        #si la technique est déjà terminée, retourne "end"
        if self._finished is True:
            r = ("end", ("finished", None))
        #sinon mémorise la validité du placement et continue 
        else:
            TEST.display("techchrccol", 3, "Résultat du placement effectué "\
                         " : {0}".format(placed))
            self._mem.memorize("techchrccol_placeok", placed, self)
            r = ("continue", None)
        return r
        
    def abort(self):
        '''Arrêt d'exécution de la technique avant sa fin et marque la technique
        comme terminée. Il faudra appeler 'reset()' avant de la relancer.
        Retourne le nombre d'actions effectuées avant l'arrêt
        '''
        TEST.display("techchrccol", 3, "TechChRCcol - dans abort()")
        assert self._initOk
        TEST.display("techchrccol", 1, "Abandon de la technique en cours")
        nbplccol = self._mem.recall("techchrccol_nbplccol", self)
        TEST.display("techchrccol", 1, \
                     "Nombre total de chiffres placés : {0}" \
                     .format(nbplccol))
        self._finish_apply()
        return ("abort", nbplccol)

    def reset(self):
        '''Réinitialise la technique dans l'état de l'instanciation.'''
        TEST.display("techchrccol", 3, "TechChRCcol - Dans reset()")
        self._clear_tech_mem()
        self._finished = False
        self._initOk = True
        return ("reset", None)

    def status(self):
        """Retourne l'état d'avancement de la technique"""
        TEST.display("techchrccol", 3, "TechChRCcol - Dans status()")
        assert self._initOk
        mem = self._mem
        finished = mem.recall("techchrccol_finished", self)
        if finished is True:
            r = ("end",)
        else:
            encours = mem.recall("techchrccol_encours", self)
            if encours is False:
                r = ("inactive", None)
            else:
                icol = mem.recall("techchrccol_icol", self)
                step = mem.recall("techchrccol_stepcol", self)
                r = ("col", icol, step)
        TEST.display("techchrccol", 3,
                     "Statut de la résolution : {0}".format(r))
        return r
        
    def techName(self):
        return "TechChRCcol"

    def techClassName():
        return "TechChRCcol"
    
    def instName(self):
        return "instance de {0}".format(self.techName())

    def __str__(self):
        return "Technique de résolution 'Chiffre/rang-colonne' sur la colonne "\
               "{0} pour le chiffre {1}".format(self._icol, self._chiffre)


##TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 
##TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 

if __name__ == "__main__":

##    env = sudoenv.SudoEnv()
##    TEST = env.TEST
    import sudotestall
    
    testlevel = 3
    TEST.levelAll(testlevel)
    ui.display("Tous les niveaux de test sont à {0}".format(testlevel))

    #mode GUI
    ui.UImode(ui.GUI)
    TEST.displayUImode(MODE_BOTH, 1)

    import sudogrid
    from sudogridview import SudoGridView
    
    ui.displaySTD("\nTest du module techchrcr.py")
    ui.displaySTD("Test de la technique de résolution Ch/RC - col")
    ui.displaySTD("----------------------------------------------\n")
    list9 = [2,5,0,6,8,0,0,3,4]
    ui.displaySTD("Choisir un fichier de test")
    fich = ui.sudoNumTestFich()
    if not fich:
        ui.displaySTD("Abandon")
        exit()
    ui.displaySTD("Fichier choisi : {0}\n".format(fich))
    vals = ui.sudoFichReadLines(fich)
    ui.displaySTD("Variable SudoBloc : bl")
    bl = sudogrid.SudoBloc()
    ui.displaySTD("Variable SudoGrid : gr")
    gr = sudogrid.SudoGrid()
    gr.fillByRowLines(vals)
    grid = gr
    ui.displaySTD("Grille test choisie : gr = ")
    gr.show()
    ui.displayGridAll(grid)
    
    ui.displaySTD("\nVariable SudoMemory : mem")
    mem = SudoMemory()
    ui.displaySTD("Variable SudoObserver : obs")
    #obs = SudoObserver()
    view = SudoGridView(grid)
    ui.displaySTD("Création d'une instance de technique de résolution : tech")

    ui.displaySTD("\nTEST au niveau 3\n")
    TEST.test("techchrccol",3)
    TEST.test("loop", 0)
    ui.sudoPause()

    ui.displaySTD("tech : technique Ch/RC pour le chiffre 1 et la colonne 1")
    chiffre = 1
    colonne = 1
    tech = TechChRCcol(mem, (chiffre, colonne))


def solve(chiffre, col):
    global tech
    tech = TechChRCcol(mem, (chiffre, col))
    
def step():
    res = tech.apply(mem)
    action = res[0]
    print("Action demandée : {0}".format(res))
    if action == "observe":
        pat = res[1]
        print("Observer : demande d'observation : {0}".format(pat))
        ui.sudoPause()
        found = view.lookup(pat)
        tech.obsFound(mem, found)
        print("résultat d'observation : {0}".format(found))
    elif action == "place":
        placement = res[1]
        print("Grid : demande de placement : {0}".format(placement))
        ui.sudoPause()
        valid = view.place(placement)
        tech.placeOk(mem, valid)
        print("résultat de placement : {0}".format(valid))
        ui.displayGridPlace(grid, placement[0], placement[1])
    else:
        print(res)
        

def reset():
    '''remet la grille de test dans son état initial et crée de nouvelles
    instances de la technique de résolution.
    '''
    del(mem)
    del(tech1)
    del(tech2)
    mem = SudoMemory
    tech1 = TechChRCcol(mem, (1,))
    tech2 = TechChRCcol(mem, (1,))
    gr.fillByRowLines(vals)
