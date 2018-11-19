'''SudoSimu - Module techchrcr - Technique de résolution "chiffre/rang-colonne"
locale pour un certain chiffre et sur un certain rang de carrés.

Ce module contient la classe TechChRCrow qui applique localement la
technique de résolution "chiffre/rang-colonne" sur un chiffre et un rang de
carrés (123 ou 456 ou 789).
Cette technique locale peut être exécutée soit par AI directement, soit par
la technique locale TechChRCsqr sur un seul carré. Elle peut aussi être
exécutée par une technique globale de répétition sur la grille. Dans ce cas
il faut créer une nouvelle instance de la technique à chaque itération de
répétition.

Instanciation :
---------------
   TechChRCrow(mem, args) - avec  args = (chiffre, rang) 
   Le rang est l'un des trois rangs du rang de carrés sur lequel va être
   faite l'application de la technique.
   
Méthodes publiques :
--------------------
   init(mem):       OBSOLETE
   apply(mem):      Méthode principale d'application de la technique
   resume(mem):  Application quand la technique a été suspendue par l'AI
   obsFound(mem, found):    Prise en compte d'un résultat d'observation
   placeOk(mem, placed):    Prise en compte d'une confirmation de placement
   abort(mem):      Demande d'abandon de la technique (par l'AI)
   reset(mem):      Réinitialisation de la technique 
   status(mem):     Demande du statut (initialisée, en cours, terminée, etc.)
   __str__()

Données mémoire utilisées :
---------------------------
Racine commune = "techchrcrow_xxxxxxxxxxx"
"techchrcrow_encours"   -> indique si la technique est en cours d'application
"techchrcrow_finished"  -> indique si la technique est terminée
"techchrcrow_nbplcrow"  -> le nombre de placements faits sur le rang
"techchrcrow_chiffre"   -> chiffre pour lequel est appliquée la technique
"techchrcrow_irow"      -> rang auquel s'applique la technique
"techchrcrow_isqrow"    -> rang de carrés auquel s'applique la technique
"techchrcrow_isqr"  -> carré où le chiffre manque
"techchrcrow_rowmiss"   -> rang où le chiffre manque
"techchrcrow_colsmiss"  -> colonnes où le chiffre manque
"techchrcrow_availplc   -> cases disponibles pour un placement
"techchrcrow_steprow"   -> étape suivante de résolution
"techchrcrow_action_suivante" -> pointeur d'action pour l'itération suivante
"techchrcrow_index_obs" -> index d'observations
"techchrcrow_obspattern"   -> le tuple de codification de l'observation demandée
"techchrcrow_placement" -> le tuple de codification du placement demandé
"techchrcrow_obsfound"  -> résultat d'observation
"techchrcrow_placeok"   -> résultat de placement
"techchrcrow_result"    -> résultat de l'itération de la technique

change.log
----------
11/10/2017
Fin de suppression des paramètres 'mem' dans toutes les méthodes publiques
et privées.
04/10/2017
Séparation du code avec un fichier 'techchrcr2.py' dont les méthodes privées
sont importées une à une.
Suppression du paramètre 'mem' des méthodes publiques
01/10/2017
La méthode init() devient obsolète. L'instanciation suffit à initialiser
l'avancement de la technique.
Reset() remet l'instance dans l'état initial de son instanciation.
03/05/2017
Adaptation au remplacement de la classe SudoObserver par SudoGridView
et placement fait avec cette classe.
04/04/2017
Version initiale

'''

#imports des modules de la simulation
if __name__ in ("__main__", "techchrcr", "techchrc.techchrcr"):
    import sudoui as ui
    import sudorules as rules
    from sudorules import Sudoku_Error
    from sudomemory import SudoMemory
    import sudogridview as gridview
    from sudotest import *
elif __name__ == "sudosimu.techchrc.techchrcr":
    from sudosimu import sudoui as ui
    from sudosimu import sudorules as rules
    from sudosimu.sudorules import Sudoku_Error
    from sudosimu.sudomemory import SudoMemory
    from sudosimu import sudogridview as gridview
    from sudosimu.sudotest import *
else:
    raise Exception("Impossible de faire les imports dans le module techchrcr.")


class TechChRCrow():
    '''Classe qui encapsule la technique de résolution 'Chiffre rang/colonne'
    sur un seul rang de carrés. Pour chaque occurence d'application de la
    technique, une instance est créée.
    Concernant les données en mémoire de l'application, l'utilisation de la
    clé secondaire 'self' évite tout mélange entre deux instances qui seraient
    appliquées simultanément (imbrications).
    '''

    def __init__(self, mem, args):
        '''Initialise l'instance pour appliquer la technique au rang de carrés
        indiqué en utilisant la mémoire du joueur 'mem'.
        '''
        TEST.display("techchrcrow", 3, "TechChRCrow - Dans __init__()")
        #arguments de l'instanciation - vérifier leur validité
        try:
            chiffre = args[0]
            assert isinstance(chiffre, int) and 1 <= chiffre <= 9
            irow = args[1]
            assert isinstance(irow, int) and 1 <= irow <= 9
        except:
            raise Sudoku_Error("TechChRCgrid instanciée avec des arguments "\
                               "invalides : {0}".format(args))
        TEST.display("techchrcrow", 3, \
                     "Nouvelle instance de la technique TechChRCrow "\
                     "appliquée au rang {0} pour le chiffre {1}"
                     .format(irow, chiffre))
        self._mem = mem
        self._chiffre = chiffre
        self._irow = irow
        mem.memorize("techchrcrow_chiffre", chiffre, self)
        mem.memorize("techchrcrow_irow", irow, self)
        #déterminer le rang de carrés. on utilise le premier rang = 1,4,7
        isqrow = 1 + 3*( (irow-1)//3 )
        TEST.display("techchrcrow", 3, "Le rang {0} correspond ".format(irow)\
                     + "au rang de carrés {0}".format(isqrow))
        mem.memorize("techchrcrow_isqrow", isqrow, self)
        self._clear_tech_mem()
        self._finished = False  #uniquement pour éviter une erreur de code
        self._initOk = True
        return

    def _clear_tech_mem(self):
        '''Prépare toutes les données en mémoire pour la résolution.'''
        TEST.display("techchrcrow", 3, "TechChRCrow - Dans _clear_tech_mem()\n"\
                     "Mise à zéro de toutes les données de la résolution.")
        mem = self._mem
        mem.memorize("techchrcrow_rowmiss", None, self)
        mem.memorize("techchrcrow_finished", False, self)
        mem.memorize("techchrcrow_encours", False, self)
        mem.memorize("techchrcrow_index_obs", None, self)
        mem.memorize("techchrcrow_steprow", None, self)
        mem.memorize("techchrcrow_action_suivante", None, self)
        mem.memorize("techchrcrow_nom_action", None, self)
        mem.memorize("techchrcrow_nbplcrow", 0, self)

#### import des fonctions d'étapes successives de l'algorithme d'application
    if __name__ in ("__main__", "techchrcr", "techchrc.techchrcr"):
        from techchrc.techchrcr2 import _start_apply
        from techchrc.techchrcr2 import _solve_debut
        from techchrc.techchrcr2 import _solve_suite1
        from techchrc.techchrcr2 import _solve_suite2
        from techchrc.techchrcr2 import _solve_suite3
        from techchrc.techchrcr2 import _solve_suite4
        from techchrc.techchrcr2 import _solve_suite5
        from techchrc.techchrcr2 import _solve_fin
        from techchrc.techchrcr2 import _finish_apply
    elif __name__ == "sudosimu.techchrc.techchrcr":
        from sudosimu.techchrc.techchrcr2 import _start_apply
        from sudosimu.techchrc.techchrcr2 import _solve_debut
        from sudosimu.techchrc.techchrcr2 import _solve_suite1
        from sudosimu.techchrc.techchrcr2 import _solve_suite2
        from sudosimu.techchrc.techchrcr2 import _solve_suite3
        from sudosimu.techchrc.techchrcr2 import _solve_suite4
        from sudosimu.techchrc.techchrcr2 import _solve_suite5
        from sudosimu.techchrc.techchrcr2 import _solve_fin
        from sudosimu.techchrc.techchrcr2 import _finish_apply
    else:
        raise Exception("Impossible de faire les imports dans le module techchrcc.")

##    from sudosimu.techchrc.techchrcr2 import _start_apply  #def _start_apply(self)
##    from sudosimu.techchrc.techchrcr2 import _solve_debut  #def _solve_debut(self)
##    from sudosimu.techchrc.techchrcr2 import _solve_suite1 #def _solve_suite1(self, mem)
##    from sudosimu.techchrc.techchrcr2 import _solve_suite2 #def _solve_suite2(self, mem)
##    from sudosimu.techchrc.techchrcr2 import _solve_suite3 #def _solve_suite3(self, mem)
##    from sudosimu.techchrc.techchrcr2 import _solve_suite4 #def _solve_suite4(self, mem)
##    from sudosimu.techchrc.techchrcr2 import _solve_suite5 #def _solve_suite5(self, mem)
##    from sudosimu.techchrc.techchrcr2 import _solve_fin    #def _solve_fin(self)
##    from sudosimu.techchrc.techchrcr2 import _finish_apply #def _finish_apply(self)
####
        
    def apply(self):
        '''Méthode d'application de cette technique. Elle est appelée
        répétitivement pour faire progresser la technique étape par étape.
        '''
        TEST.display("techchrcrow", 3, "TechChRCrow - Dans apply()")
        assert self._initOk
        #si la technique est terminée, sortir tout de suite
        if self._finished is True:
            TEST.display("techchrcrow", 3,
                         "Technique terminée, sortie immédiate.")
            return ("end", ("finished", None))
        
        #quand apply() est appelée la première fois, la technique n'est pas
        #encore en cours. Il faut commencer son application.
        mem = self._mem
        if mem.recall("techchrcrow_encours", self) is False:
            TEST.display("techchrcrow", 3, "TechChRCrow - Début de résolution.")
            TEST.display("techchrcrow", 2, \
                         "Technique de résolution \"Chiffre/rang-colonne\" "\
                         "sur le rang {0} pour le chiffre {1}."\
                         .format(self._irow, self._chiffre))
            TEST.display("techchrcrow", 3, "TechChRCrow - Etape à exécuter : "\
                                             "première étape.")
            try:
                r = self._start_apply()
                TEST.display("techchrcrow", 3, "TechChRCrow - retour à apply()")
                mem.memorize("techchrcrow_encours", True, self)
            except:
                TEST.display("techchrcrow", 1, \
                             "Erreur : échec de la technique 'chiffre/ "\
                             "rang-colonne'sur le rang {0}.\n"\
                             .format(self._irow)+"La résolution est abandonnée.")
                mem.memorize("techchrcrow_encours", False, self)
                mem.memorize("techchrcrow_finished", True, self)
                self._finished = True
                r = ("end",
                     ("fail",
                      "Erreur d'exécution de la technique TechChRCgrow."))
                raise Sudoku_Error("TechChRCrow - Erreur dans apply()")
        else:
            #déjà une résolution en cours, la continuer
            TEST.display("techchrcrow", 2, "TechChRCrow suite de la résolution")
            methode = mem.recall("techchrcrow_action_suivante", self)
            nom = mem.recall("techchrcrow_nom_action", self)
            TEST.display("techchrcrow", 3, "TechChRCrow - Etape à exécuter : "\
                                             "{0}.".format(nom))
            try:
                r = methode()
                TEST.display("techchrcrow", 3, "TechChRCrow - retour à apply()")
            except:
                TEST.display("techchrcrow", 1, \
                             "Erreur : échec de la technique 'chiffre / "\
                             "rang-colonne' sur le rang {0}.\n"\
                             .format(self._irow)+"La résolution est abandonnée.")
                mem.memorize("techchrcrow_encours", False, self)
                mem.memorize("techchrcrow_finished", True, self)
                self._finished = True
                r = ("end",
                     ("fail",
                      "Erreur d'exécution de la technique TechChRCgrow."))
                raise Sudoku_Error("TechChRCrow - Erreur dans Apply()")
        return r

    def resume(self):
        '''Méthode de résolution alternative appelée par Thinking dans le cas
        où la technique est continuée après une mise en attente du fait
        de l'imbrication d'autres techniques. Permet de faire des vérifications
        de cohérence des données mémorisées pendant la mise en attente,
        avant de reprendre l'application.
        '''
        TEST.display("techchrcrow", 3, "TechChRCrow - dans resume()")
        assert self._initOk
        # dans cette version ne fait encore rien de particulier.
        return self.apply()


    def obsFound(self, found):
        '''Prend connaissance du résultat de l'observation demandée par la
        technique. Fait progresser la technique dans un nouvel état stable.
        Retourne "continue" ou "end" si la technique est terminée.
        '''
        TEST.display("techchrcrow", 3, "TechChRCrow - dans obsFound()")
        assert self._initOk
        #si la technique est déjà terminée, retourne "end"
        if self._finished is True:
            r = ("end", ("finished", None))
        else:
        #mémorise le résultat d'observation et continue 
            self._mem.memorize("techchrcrow_obsfound", found, self)
            TEST.display("techchrcrow", 3, "Résultat d'observation engistré "\
                         " : {0}".format(found))
            r = ("continue", None)
        return r

    def placeOk(self, placed=None):
        '''Prend connaissance du succès d'un placement par la technique. Fait
        progresser la technique dans un nouvel état stable.
        Retourne "continue" ou "end" si la technique est terminée.
        '''
        TEST.display("techchrcrow", 3, "TechChRCrow - dans placeOk()")
        TEST.display("techchrcrow", 3, "Résultat du placement : {0}"\
                                        .format(placed))
        assert self._initOk
        #si la technique est déjà terminée, retourne "end"
        if self._finished is True:
            r = ("end", ("finished", None))
        #sinon mémorise la validité du placement et continue 
        else:
            TEST.display("techchrcrow", 3, "Résultat du placement effectué "\
                         " : {0}".format(placed))
            self._mem.memorize("techchrcrow_placeok", placed, self)
            r = ("continue", None)
        return r
        
    def abort(self):
        '''Arrêt d'exécution de la technique avant sa fin et marque la technique
        comme terminée. Il faudra appeler 'reset()' avant de la relancer.
        Retourne le nombre d'actions effectuées avant l'arrêt
        '''
        TEST.display("techchrcrow", 3, "TechChRCrow - dans abort()")
        assert self._initOk
        TEST.display("techchrcrow", 1, "Abandon de la technique en cours")
        nbplcrow = self._mem.recall("techchrcrow_nbplcrow", self)
        TEST.display("techchrcrow", 1, \
                     "Nombre total de chiffres placés : {0}" \
                     .format(nbplcrow))
        self._finish_apply()
        return ("abort", nbplcrow)

    def reset(self):
        '''Réinitialise la technique dans l'état de l'instanciation.'''
        TEST.display("techchrcrow", 3, "TechChRCrow - Dans reset()")
        self._clear_tech_mem()
        self._finished = False
        self._initOk = True
        return ("reset", None)

    def status(self):
        """Retourne l'état d'avancement de la technique"""
        TEST.display("techchrcrow", 3, "TechChRCrow - Dans status()")
        assert self._initOk
        mem = self._mem
        finished = mem.recall("techchrcrow_finished", self)
        if finished is True:
            r = ("end",)
        else:
            encours = mem.recall("techchrcrow_encours", self)
            if encours is False:
                r = ("inactive", None)
            else:
                irow = mem.recall("techchrcrow_irow", self)
                step = mem.recall("techchrcrow_steprow", self)
                r = ("row", irow, step)
        TEST.display("techchrcrow", 3,
                     "Statut de la résolution : {0}".format(r))
        return r

    def techName(self):
        return "TechChRCrow"

    def techClassName():
        return "TechChRCrow"
    
    def instName(self):
        return "instance de {0}".format(self.techName())

    def __str__(self):
        return "Technique de résolution 'Chiffre/rang-colonne' sur le rang "\
               "{0} pour le chiffre {1}".format(self._irow, self._chiffre)


##TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 
##TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 

if __name__ == "__main__":

    import sudotestall
    testlevel = 3
    TEST.levelAll(testlevel)
    ui.display("Tous les niveaux de test sont à {0}".format(testlevel))

    import sudogrid
    from sudogridview import SudoGridView
    
    print("\nTest du module techchrcr.py")
    print("Test de la technique de résolution Ch/RC - row")
    print("----------------------------------------------\n")
    list9 = [2,5,0,6,8,0,0,3,4]
    ui.display("Choisir un fichier de test")
    fich = ui.sudoNumTestFich()
    if not fich:
        ui.display("Abandon")
        exit()
    print("Fichier choisi : {0}\n".format(fich))
    vals = ui.sudoFichReadLines(fich)
    print("Variable SudoBloc : bl")
    bl = sudogrid.SudoBloc()
    print("Variable SudoGrid : gr")
    gr = sudogrid.SudoGrid()
    gr.fillByRowLines(vals)
    grid = gr
    print("Grille test choisie : gr = ")
    gr.show()
    
    print("\nVariable SudoMemory : mem")
    mem = SudoMemory()
    print("Variable SudoObserver : view")
    view = SudoGridView(grid)
    print("Création de 2 instances de technique de résolution.")
    print("Instance de technique TechLastPlc : tech1 et tech2")

    print("\nTEST au niveau 3\n")
    TEST.test("techchrcrow",3)
    TEST.test("loop", 0)
    ui.sudoPause()

    chiffre = 8
    rang = 1
    tech = TechChRCrow(mem, (chiffre, rang))


def solve(chiffre, row):
    global tech
    tech = TechChRCrow(mem, (chiffre, row))
    
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
    tech1 = TechChRCrow(mem, (1,))
    tech2 = TechChRCrow(mem, (1,))
    gr.fillByRowLines(vals)
