'''SudoSimu - Module techlplcg - technique de résolution "dernier placement"
globale sur la grille.

Ce module contient la classe SudoTechLastPlcGrid qui applique par répétition les
techniques locales "dernier placement" sur toute la grille. Elle enchaîne donc
SudoTechLastPlcSqr pour isqr = 1 à 9, puis idem en rang puis colonne.

change.log
----------
11/10/2017
Suppression des paramètres 'mem' inutiles dans toutes les méthodes
19/09/2017
Note de version : test en cours avec l'enchaînement carrés puis rangs, avec
les modules carrés et rangs réécrits. Il reste à faire l'update du code pour
les colonnes.
'''

if __name__ in ("__main__", "techlplcg", "techlplc.techlplcg"):
    #imports des modules de la simulation
    import sudoui as ui
    import sudorules as rules
    from sudorules import Sudoku_Error
    from sudomemory import SudoMemory
    import sudogridview as gridview
    from sudotest import *
    #import des modules de techniques locales de résolution
    from techlplc.techlplcs import TechLastPlcSqr
    from techlplc.techlplcr import TechLastPlcRow
    from techlplc.techlplcc import TechLastPlcCol
elif __name__ == "sudosimu.techlplc.techlplcg":
    #imports des modules de la simulationfrom sudosimu import sudoui as ui
    from sudosimu import sudorules as rules
    from sudosimu.sudorules import Sudoku_Error
    from sudosimu.sudomemory import SudoMemory
    from sudosimu import sudogridview as gridview
    from sudosimu.sudotest import *
    #import des modules de techniques locales de résolution
    from sudosimu.techlplc.techlplcs import TechLastPlcSqr
    from sudosimu.techlplc.techlplcr import TechLastPlcRow
    from sudosimu.techlplc.techlplcc import TechLastPlcCol
else:
    raise Exception("Impossible de faire les imports dans le module techlplcg.")


class TechLastPlcGrid():
    '''Classe qui encapsule la technique de résolution 'Dernier placement'
    sur la grille entière.
    '''

    def __init__(self, mem, args=None):
        '''Initialise l'instance en utilisant la mémoire du joueur 'mem'.
        Le paramètre 'args' est nécessaire pour l'uniformisation du code mais il
        est inutilisé.
        '''
        TEST.display("techlplcgrid", 3, "TechLastPlcGrid - Dans __init__()")
        TEST.display("techlplcgrid", 2, \
                     "Nouvelle instance de la technique TechLastPlcGrid.")
        self._mem = mem
        #Initialisation des données en mémoire du joueur
        self._clear_tech_mem()
        #autres variables de contrôle d'exécution de la technique
        self._finished = False  #uniquement pour éviter une erreur de code
        self._resume = False    #indique appel de resume() au lieu de apply()
        self._initOk = True     #n'est plus utilisé si disparition de init()
        self._encours = False
        return

    def _clear_tech_mem(self):
        '''Complète l'initialisation des données en mémoire.'''
        TEST.display("techlplcgrid", 3, "TechLastPlcGrid - Dans "\
                     "_clear_tech_mem()")
        TEST.display("techlplcgrid", 3, "Remise à zéro de toutes les "\
                     "variables d'exécution.")
        mem = self._mem
        mem.memorize("techlplcgrid_finished", False, self)
        mem.memorize("techlplcgrid_encours", False, self)
        mem.memorize("techlplcgrid_rcs", False, self)
        mem.memorize("techlplcgrid_ibloc", False, self)
        mem.memorize("techlplcgrid_index_obs", None, self)
        mem.memorize("techlplcgrid_action_suivante", None, self)
        mem.memorize("techlplcgrid_nbplctot", 0, self)

#### import des fonctions d'étapes successives de l'algorithme d'application
    if __name__ in ("__main__", "techlplcg", "techlplc.techlplcg"):
        from techlplc.techlplcg2 import _start_apply
        from techlplc.techlplcg2 import _apply_techloc
        from techlplc.techlplcg2 import _techloc_end
        from techlplc.techlplcg2 import _techloc_fail
        from techlplc.techlplcg2 import _next_techloc
        from techlplc.techlplcg2 import _finish_apply
    elif __name__ == "sudosimu.techlplc.techlplcg":
        from sudosimu.techlplc.techlplcg2 import _start_apply
        from sudosimu.techlplc.techlplcg2 import _apply_techloc
        from sudosimu.techlplc.techlplcg2 import _techloc_end
        from sudosimu.techlplc.techlplcg2 import _techloc_fail
        from sudosimu.techlplc.techlplcg2 import _next_techloc
        from sudosimu.techlplc.techlplcg2 import _finish_apply
    else:
        raise Exception("Impossible de faire les imports dans le module techlplcg.")
####

        
    def apply(self):
        '''Méthode d'application de cette technique. Elle est appelée
        répétitivement pour faire progresser la technique étape par étape.
        '''
        TEST.display("techlplcgrid", 3, "TechLastPlcGrid - Dans apply()")
        assert self._initOk
        #si la technique est terminée, sortir tout de suite
        if self._finished is True:
            return ("end", ("finished", None))
        mem = self._mem        
        #selon qu'une résolution est déjà en cours ou pas
        if mem.recall("techlplcgrid_encours", self) is False:
            #pas de résolution en cours : débuter la technique
            TEST.display("techlplcgrid", 1, \
                         "Technique de résolution \"Dernier placement sur "+
                         "la grille\"")
            try:
                r = self._start_apply()
            except:
                #la méthode ne s'exécute pas correctement
                #abandonner l'exécution de la technique
                mem.memorize("techlplcgrid_encours", None, self)
                TEST.display("techlplcgrid", 0, \
                             "ERREUR FATALE : échec de la méthode de résolution."
                             "\nLa technique 'Dernier placement' est annulée.")
                r = ("fail", "Erreur dans le module 'techlplcg'\n"\
                     "Dans apply() exception retour de _start_apply()\n")
                raise Sudoku_Error("TechLastPlcGrid - Erreur dans apply()")

        else:
            #déjà une résolution en cours, la continuer
            TEST.display("techlplcgrid", 2, "LastPlcGrid suite de la résolution")
            methode = self._apply_techloc
            try:
                r = methode()
            except:
                #la méthode ne s'exécute pas correctement
                #abandonner l'exécution de la technique
                mem.memorize("techlplcgrid_encours", None, self)
                TEST.display("techlplcgrid", 0, \
                             "ERREUR FATALE : échec de la méthode de résolution."
                             "\nLa technique 'Dernier placement' est annulée.")
                r = ("fail", "Erreur dans le module 'techlplcg'\n"\
                     "Dans apply() exception retour de _start_apply()\n")
                raise Sudoku_Error("TechLastPlcGrid - Erreur dans apply()")
        return r

    def resume(self):
        '''Méthode de résolution alternative appelée par Thinking dans le cas
        où la technique est continuée après une mise en attente du fait
        de l'imbrication d'autres techniques. Permet de faire des vérifications
        de cohérence des données mémorisées pendant la mise en attente,
        avant de reprendre l'application.
        '''
##ATTENTION : pour le moment, ne fait que répercuter 'resume' au lieu de 'apply'
##aux appels des techniques locales.
##Il faudra plus tard modifier cette méthode pour prendre en compte
##la possibilité réelle d'oubli de l'avancement, si la technique est restée
##longtemps en standby à cause d'imbrications.

        TEST.display("techlplcgrid", 3, "TechLastPlcGrid - dans resume()")
        assert self._initOk
        assert self._encours    #la première itération doit avoir été apply()

        #indique l'état "resume" avant de passer à la résolution normale
        self._resume = True
        r = self.apply()
        #remet l'indicateur à zéro pour les prochaines fois
        self._resume = False
        return r

    def obsFound(self, found):
        '''Transmet le résultat d'observation à la technique locale en cours
        qui a demandé cette observation. Traite le cas particulier où la
        tech. locale retourne "end", qu'il faut gérer globalement.
        '''
        TEST.display("techlplcgrid", 3, "TechLastPlcGrid - dans obsFound()")
        assert self._initOk
        #si la technique est déjà terminée, retourne "end"
        if self._finished is True:
            return ("end", ("finished", None))
        mem = self._mem
        TEST.display("techlplcgrid", 3, "Résultat d'observation : {0}"\
                                         .format(found))
        techloc = mem.recall("techlplcgrid_techloc", self)
        r = techloc.obsFound(found)
        #gérer les cas de fin de la technique locale en retour d'observation
        if r[0] == "end":
            endDetails = r[1]
            r = self._techloc_end(endDetails)
        elif r[0] == "fail":
            failDetails = r[1]
            r = self._techloc_fail(failDetails)            
        return r
    
    def placeOk(self, placed=True):
        '''Prend connaissance du succès d'un placement par la technique. Traite
        le cas particulier où la tech. locale retourne "end", qu'il faut
        gérer au niveau de cette technique globale
        '''
        TEST.display("techlplcgrid", 3, "TechLastPlcGrid - dans placeOk()")
        assert self._initOk
        #si la technique est déjà terminée, retourne "end"
        if self._finished is True:
            return ("end", None)
        mem = self._mem
        techloc = mem.recall("techlplcgrid_techloc", self)
        r = techloc.placeOk(placed)
        #gérer les cas de fin de la technique locale en retour de placement
        if r[0] == "end":
            endDetails = r[1]
            r = self._techloc_end(endDetails)
        elif r[0] == "fail":
            failDetails = r[1]
            r = self._techloc_fail(failDetails)            
        return r
        
    def abort(self):
        '''Arrêt d'exécution de la technique avant sa fin et marque la technique
        comme terminée. Il faudra appeler 'reset()' avant de la relancer.
        Retourne le nombre d'actions effectuées avant l'arrêt
        '''
        TEST.display("techlplcgrid", 3, "TechLastPlcGrid - dans abort()")
        TEST.display("techlplcgrid", 1, "Abandon de la technique en cours")
        plctot = self._mem.recall("techlplcgrid_nbplctot", self)
        TEST.display("techlplcgrid", 1, \
                     "Nombre total de chiffres placés : {0}" \
                     .format(plctot))
        self._mem.memorize("techlplcgrid_encours", False, self)
        self._finish_tech()
        return ("end", ("abort", plctot))

    def reset(self):
        '''Réinitialise la technique dans l'état de l'instanciation.'''
        TEST.display("techchrcrow", 3, "TechLastPlcGrid - Dans reset()")
        self._clear_tech_mem()
        self._finished = False
        self._initOk = True
        return ("reset", None)

    def status(self):
        """Retourne l'état d'avancement de la technique"""
        TEST.display("techlplcgrid", 3, "Fonction status()")
        mem = self._mem
        finished = mem.recall("techlplcgrid_finished", self)
        if finished is True:
            return ("end", ("finished", None))
        else:
            encours = mem.recall("techlplcgrid_encours", self)
            if encours is False:
                r = ("inactive", None)
            else:
                isqr = mem.recall("techlplcgrid_isqr", self)
                step = mem.recall("techlplcgrid_stepsqr", self)
                r = ("active", ("sqr", isqr, step))
        TEST.display("techlplcgrid", 3,
                     "Statut de la résolution : {0}".format(r))
        return r

    def techName(self):
        return "TechLastPlcGrid"

    def techClassName():
        return "TechLastPlcGrid"
    
    def instName(self):
        return "instance de {0}".format(self.techName())

    def __str__(self):
        return "Technique de résolution 'Dernier placement' sur toute la grille"


##TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 
##TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 

if __name__ == "__main__":

    import sudotestall
    testlevel = 3
    TEST.levelAll(testlevel)
    ui.display("Tous les niveaux de test sont à {0}".format(testlevel))

    #mode GUI
    ui.UImode(ui.GUI)
    TEST.displayUImode(MODE_BOTH, 1)

    import sudogrid
    #from sudoobserver import SudoObserver
    
    ui.display("\nTest du module sudotechlastp")
    ui.display("Test de la technique de résolution LastPlc")
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
    #obs = SudoObserver()
    ui.display("Création de 2 instances de technique de résolution.")
    ui.display("Instance de technique TechLastPlc : tech1 et tech2")
    tech1 = TechLastPlcSqr(mem, (1,))
    tech2 = TechLastPlcSqr(mem, (1,))
    ui.display("\nTEST au niveau 3\n")
    TEST.test("techlplcgrid",3)
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
    tech1 = TechLastPlcSqr(mem, (1,))
    tech2 = TechLastPlcSqr(mem, (1,))
    gr.fillByRowLines(vals)
    

def testLoop1():
    loopTech(tech1, gr, mem, obs)

def testLoop2():
    loopTech(tech2, gr, mem, obs)
    
def loopTechOld(tech, grid, mem, obs):
    if grid.isCompleted():
        ui.display("Grille terminée")
        return
    TEST.display("loop", 2, "Début de boucle")
    r = tech.apply(mem)
    action = r[0]
    TEST.display("loop", 2,
                 "Résultat de tech.solve() : {0}".format(r))
    TEST.display("loop", 2,
                 "statut d'avancement de tech: {0}".format(tech.status(mem)))
    if action == "observe":
        pattern = r[1]
        found = obs.lookup(grid, pattern)
        TEST.display("loop", 1,
                     "Résultat de obs.lookup() : {0}".format(found))
        mem.memorizeObs(found, tech)
    elif action == "place":
        placement = r[1]
        (row, col, chiffre) = placement
        r = grid.placeRC(row, col, chiffre, True)
        TEST.display("loop", 1,
                     "Résultat de grid.place() : {0}".format(r))
    elif action == "continue":
        pass
    else:
        TEST.display("loop", 2,
                     "action retournée par solve() : {0}".format(action))
    return


def loopTech(tech, pause=False):
    '''Cette fonction applique répétitivement la technique 'LastPlc' sur la
    grille 'grid' jusqu'à un certain état d'avancement. Par exemple faire tous
    les carrés, ou tous les carrés et rangs, etc.
    '''
    TEST.display("loop", 1,
                 "Boucle de résolution de TechLastPlc sur tous les carrés")
    tech.reset(mem)
    grid = gr
    iter = 0
    while True:

        if grid.isCompleted():
            ui.display("\nGrille terminée.")
            return

        status = loopStep(tech)

        #contrôler fin du while
        iter +=1
        if iter > 100:
            TEST.display("loop", 0,
                         "Plus de 100 itérations de boucle !!! Stop.")
            break
#        if status[0] not in ("sqr", "row", "col"):
        if status[0] not in ("sqr", "row"):
            TEST.display("loop", 1,
                         "Boucle : les carrés, rangs et colonnes sont terminés.")
            break
        if pause:
            r = ui.sudoPause(True)
            if r:
                ui.display("")
            else:   #Ctrl-C ou Ctrl-D
                ui.display("Interruption clavier")
                break
        continue

#    tech.abort(mem)
    return

def loopStep(tech):
    '''Cette fonction exécute une seule itération de boucle ROMA sur la grille
    'grid' avec la technique de résolution 'LastPlc'.
    '''
    TEST.display("loop", 1, "\nDébut de boucle")
    r = tech.apply(mem)
    action = r[0]
    TEST.display("loop", 2,
                 "Résultat de tech.solve() : {0}".format(r))
    status = tech.status(mem)
    TEST.display("loop", 2,
                 "statut d'avancement de tech: {0}".format(status))
    if action == "observe":
        pattern = r[1]
        found = obs.lookup(grid, pattern)
        mem.memorizeObs(found, tech)
        TEST.display("loop", 1,
                     "Résultat de obs.lookup() : {0}".format(found))
        #mem.memorizeObs(found, tech)
        tech.obsFound(mem, found)
    elif action == "place":
        placement = r[1]
        (row, col, chiffre) = placement
        r = grid.placeRC(row, col, chiffre, True)
        TEST.display("loop", 1,
                     "Résultat de grid.place() : {0}".format(r))
    elif action == "continue":
        pass
    else:
        TEST.display("loop", 2,
                     "action retournée par solve() : {0}".format(action))
    return status
        
