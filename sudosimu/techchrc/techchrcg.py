'''SudoSimu - Module techchrcg - technique de résolution "chiffre/rang-colonne"
globale sur la grille entière pour un chiffre donné.

Ce module contient la classe TechChRCgrid qui applique par répétition les
techniques locales "chiffre/rang-colonne" sur toute la grille. Elle enchaîne
donc TechChRCrow et TechChRCcol pour tous les rangs et colonnes de carrés, pour
le chiffre indiqué.

Les instances de cette classe représentent des raisonnement systématiques
et itératifs de résolution, qui font globalement partie de la pensée du joueur,
tout en étant autonomes par leur côté systématique. Le raisonnement évolue étape
par étape à chaque appel de la méthode apply(), et retourne des demandes
d'observation de la grille et de placement de chiffres. Au niveau global de la
pensée, c'est la partie AI (classe SudoThinkAI) qui décide d'appliquer une
technique et qui instancie la classe, puis c'est la partie pensée logique
(classe SudoThinking) qui organise l'enchaînement et appelle la méthode apply().

change.log
----------
11/10/2017
Suppression des paramètres 'mem' inutiles dans toutes les méthodes.
Séparation du script en 2 fichiers (techchrcg2.py) avec import des méthodes
transférées dans le second fichier.

'''

if __name__ in ("__main__", "techchrcg", "techchrc.techchrcg"):
    #imports des modules de la simulation
    import sudoui as ui
    import sudorules as rules
    from sudorules import Sudoku_Error
    from sudomemory import SudoMemory
    import sudogridview as gridview
    from sudotest import *
    #import des modules de techniques locales de résolution
    from techchrc.techchrcr import TechChRCrow
    from techchrc.techchrcc import TechChRCcol
elif __name__ == "sudosimu.techchrc.techchrcg":
    #imports des modules de la simulation
    from sudosimu import sudoui as ui
    from sudosimu import sudorules as rules
    from sudosimu.sudorules import Sudoku_Error
    from sudosimu.sudomemory import SudoMemory
    from sudosimu import sudogridview as gridview
    from sudosimu.sudotest import *
    #import des modules de techniques locales de résolution
    from sudosimu.techchrc.techchrcr import TechChRCrow
    from sudosimu.techchrc.techchrcc import TechChRCcol
else:
    raise Exception("Impossible de faire les imports dans le module techchrcg.")


class TechChRCgrid():
    '''Classe qui encapsule la technique de résolution "chiffre/rang-colonne"
    sur la grille entière.
    '''

    def __init__(self, mem, args=None):
        '''Initialise l'instance en utilisant la mémoire du joueur 'mem'.
        Le paramètre 'args' contient le chiffre pour lequel appliquer la
        technique.
        '''
        TEST.display("techchrcgrid", 3, "TechChRCgrid - Dans __init__()")
        #chiffre pour lequel appliquer la technique, vérifier la validité.
        try:
            chiffre = args[0]
            assert isinstance(chiffre, int) and 1 <= chiffre <= 9
        except:
            raise Sudoku_Error("TechChRCgrid instanciée avec des arguments "\
                               "invalides : {0}".format(args))
        TEST.display("techchrcgrid", 2, \
                     "\nNouvelle instance de la technique TechChRCgrid "\
                     "pour le chiffre {0}".format(chiffre))
        self._chiffre = chiffre
        self._mem = mem
        #Initialiser les données en mémoire de la résolution
        mem.memorize("techchrcgrid_chiffre", chiffre, self)
        self._clear_tech_mem()
        #init contrôle d'exécution (en_cours, finished etc.)
        self._init_tech()
        self._initOk = True
        TEST.display("techchrcgrid", 3, "TechChRCgrid - L'initialisation de "\
                                 "l'instance est terminée.")
        return

    def _clear_tech_mem(self):
        '''Initialise les données d'application de la technique par le joueur
        dans sa mémoire.
        '''
        mem = self._mem
        TEST.display("techchrcgrid", 3, "TechChRCgrid - Dans _clear_tech_mem()")
        mem.memorize("techchrcgrid_rcs", None, self)
        mem.memorize("techchrcgrid_isqrow", 0, self)
        mem.memorize("techchrcgrid_isqcol", 0, self)
        mem.memorize("techchrcgrid_techclass", None, self)
        mem.memorize("techchrcgrid_techloc", None, self)
        mem.memorize("techchrcgrid_techlocname", "<inconnue>", self)
        mem.memorize("techchrcgrid_nbplctot", 0, self)
        mem.memorize("techchrcgrid_encours", False, self)
        mem.memorize("techchrcgrid_finished", False, self)
        return True

    def _init_tech(self):    
        self._finished = False  #uniquement pour éviter une erreur de code
        self._resume = False    #indique appel de resume() au lieu de apply()
        self._encours = False

#### import des fonctions d'étapes successives de l'algorithme d'application
    if __name__ in ("__main__", "techchrcg", "techchrc.techchrcg"):
        from techchrc.techchrcg2 import _start_apply
        from techchrc.techchrcg2 import _apply_techloc
        from techchrc.techchrcg2 import _techloc_end
        from techchrc.techchrcg2 import _techloc_fail
        from techchrc.techchrcg2 import _next_techloc
        from techchrc.techchrcg2 import _finish_apply
        from techchrc.techchrcg2 import _newLocalTechInst
    elif __name__ == "sudosimu.techchrc.techchrcg":
        from sudosimu.techchrc.techchrcg2 import _start_apply
        from sudosimu.techchrc.techchrcg2 import _apply_techloc
        from sudosimu.techchrc.techchrcg2 import _techloc_end
        from sudosimu.techchrc.techchrcg2 import _techloc_fail
        from sudosimu.techchrc.techchrcg2 import _next_techloc
        from sudosimu.techchrc.techchrcg2 import _finish_apply
        from sudosimu.techchrc.techchrcg2 import _newLocalTechInst
    else:
        raise Exception("Impossible de faire les imports dans le module techchrcg.")
####
    

    def apply(self):
        '''Méthode d'application de cette technique. Elle est appelée
        répétitivement pour faire progresser la technique étape par étape.
        '''
        TEST.display("techchrcgrid", 3, "TechChRCgrid - Dans apply()")
        assert self._initOk
        mem = self._mem
        #si la technique est terminée, sortir tout de suite
        if self._finished is True:
            TEST.display("techchrcgrid", 2,
                         "Technique déjà terminée.")
            return ("end", None)
        
        #quand apply() est appelée la première fois, la technique n'est pas
        #encore en cours. Il faut commencer son application.
        if self._encours is not True:
            self._encours = True
            TEST.display("techchrcgrid", 1, "Technique de résolution "\
                         "\'Chiffre/rang-colone\' sur la grille entière "\
                         "pour le chiffre {0}.".format(self._chiffre))
            try:
                r = self._start_apply()
                TEST.display("techchrgrid", 3, "TechChRCgrid - retour à apply()")
                
                mem.memorize("techchrcgrid_encours", True, self)
            except:
                #la méthode ne s'exécute pas correctement - abandonner
                TEST.display("techchrcgrid", 3, "TechChRCgrid - retour à apply()")
                failTxt = "TechChRCgrid - FAIL dans apply()\n"\
                    "Impossible d'instancier la technique {0}. La technique "\
                    "de résolution TechChRCgrid est abandonnée.".format( \
                                mem.recall("techchrcgrid_techlocname", self))
                #exception suivant le niveau de test
                TEST.raiseArgs("techchrcgrid", 1, Sudoku_Error, failTxt)
                TEST.display("techchrcgrid", 1, \
                    "TechChRCgrid - FAIL dans apply()\n Impossible d'instancier "\
                    "la technique {0}. La technique de résolution TechChRCgrid "\
                    "est abandonnée.".format(
                                mem.recall("techchrcgrid_techlocname", self)))
                r = ("end",
                     ("fail",
                      "Erreur d'exécution de la technique TechChRCgrid."))
                self._encours = False 
                self._finished = True
                raise Sudoku_Error("TechChRCgrid - Erreur dans apply()")
        else:
            #déjà une résolution en cours, la continuer
            TEST.display("techchrcgrid", 2, \
                         "TechChRCgrid - suite de la résolution")
            try:
                r = self._apply_techloc()
                TEST.display("techchrgrid", 3, "TechChRCgrid - retour à apply()")
            except:
                #la méthode ne s'exécute pas correctement - abandonner
                TEST.display("techchrcgrid", 3, "TechChRCgrid - retour à apply()")
                failTxt = "TechChRCgrid - FAIL dans apply()\n"\
                    "Impossible d'instancier la technique {0}. La technique "\
                    "de résolution TechChRCgrid est abandonnée.".format( \
                                mem.recall("techchrcgrid_techlocname", self)) 
                #exception suivant le niveau de test
                TEST.raiseArgs("techchrcgrid", 1, Sudoku_Error, failTxt)
                TEST.display("techchrcgrid", 1, failTxt)
                r = ("end", 
                     ("fail",
                      "Erreur d'exécution de la technique TechChRCgrid."))
                mem.memorize("techchrcgrid_encours", False, self)
                self._encours = False
                self._finished = True
                raise Sudoku_Error("TechChRCgrid - Erreur dans apply()")
                
        TEST.display("techchrcgrid", 2, "TechChRCgrid  - apply() retourne : {0}" \
                                         .format(r))
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

        TEST.display("techchrcgrid", 3, "TechChRCgrid - dans resume()")
        assert self._initOk
        assert self._encours    #la première itération doit avoir été apply()
        #indique l'état "resume" avant de passer à la résolution normale
        self._resume = True
        r = self.apply()
        TEST.display("techchrgrid", 3, "TechChRCgrid - retour à resume()")
        #remet l'indicateur à zéro pour les prochaines fois
        self._resume = False
        return r

    def obsFound(self, found):
        '''Transmet le résultat d'observation à la technique locale en cours
        qui a demandé cette observation. Traite le cas particulier où la
        tech. locale retourne "end", qu'il faut gérer globalement.
        '''
        TEST.display("techchrcgrid", 3, "TechChRCgrid - dans obsFound()")
        assert self._initOk
        mem = self._mem
        #si la technique est déjà terminée, retourne "end"
        if self._finished is True:
            return ("end", None)
        TEST.display("techchrcgrid", 3, "TechChRCgrid - Résultat d'observation : "\
                                         "{0}".format(found))
        #transmettre le résultat à la technique locale en cours
        techloc = mem.recall("techchrcgrid_techloc", self)
        r = techloc.obsFound(found)
        TEST.display("techchrcgrid", 3, "TechChRCgrid - retour à obsFound()")
        TEST.display("techchrcgrid", 3, "TechChRCgrid - retour de obsFound() "\
                                         "de la technique {0} : {1}"\
                                         .format(techloc.techName(), r))
        #si la technique locale retourne "end", traiter ce cas tout de suite
        if r[0] == "end":
            endDetails = r[1]
            TEST.display("techchrcgrid", 3, "obsFound : la technique locale "\
                         "{0} a renvoyé 'end' ".format(techloc.TechName()))
            r = self._techloc_end(endDetails)
        return r
    
    def placeOk(self, placed=None):
        '''Prend connaissance du succès d'un placement par la technique. Traite
        le cas particulier où la tech. locale retourne "end", qu'il faut
        gérer au niveau de cette technique globale
        '''
        TEST.display("techchrcgrid", 3, "TechChRCgrid - dans placeOk()")
        assert self._initOk
        mem = self._mem
        #si la technique est déjà terminée, retourne "end"
        if self._finished is True:
            return ("end", None)
        TEST.display("techchrcgrid", 3, "TechChRCgrid - Résultat de placement : "\
                                         "{0}".format(placed))
        #transmettre le résultat à la technique locale en cours
        techloc = mem.recall("techchrcgrid_techloc", self)
        r = techloc.placeOk(placed)
        TEST.display("techchrgrid", 3, "TechChRCgrid - retour à placeOk()")
        TEST.display("techchrcgrid", 3, "TechChRCgrid - retour de placeOk() "\
                                         "de la technique {0} : {1}"
                                         .format(techloc.techName(), r))
        #si la technique locale retourne "end", traiter ce cas tout de suite
        if r[0] == "end":
            endDetails = r[1]
            TEST.display("techchrcgrid", 3, "placeOk : la technique locale "\
                         "{0} a renvoyé 'end' ".format(techloc.techName()))
            r = self._techloc_end(endDetails)
        return r
        
    def abort(self):
        '''Arrêt d'exécution de la technique avant sa fin et marque la technique
        comme terminée. Il faudra appeler 'reset()' avant de la relancer.
        Retourne le nombre d'actions effectuées avant l'arrêt
        '''
        TEST.display("techchrcgrid", 3, "TechChRCgrid - dans abort()")
        assert self._initOk
        mem = self._mem
        TEST.display("techchrcgrid", 1, "Abandon de la technique en cours")
        plctot = mem.recall("techchrcgrid_nbplctot", self)
        TEST.display("techchrcgrid", 1, \
                     "Nombre total de chiffres placés : {0}" \
                     .format(plctot))
        mem.memorize("techchrcgrid_encours", False, self)
        self._finish_apply()
        return ("abort", plctot)

    def reset(self):
        '''Rénitialise l'instance la technique. Ne devrait pas être utilisé
        en version de production car il faut utiliser à chaque fois une
        nouvelle instance de technique.
        Mais utile en débuggage et tests.
        '''
        TEST.display("techchrcgrid", 3, "TechChRCgrid - dans reset()")
        self._clear_tech_mem()   #la mémoire du joueur
        self._init_tech()        #variables d'exécution de la technique
        self._initOk = True
        return True
        
    def status(self):
        '''Retourne l'état d'avancement de la technique'''
        TEST.display("techchrcgrid", 3, "TechChRCgrid - Dans status()")
        assert self._initOk
        mem = self._mem
        if self._finished is True:
            r = ("end", None)
        else:
            if self._encours is False:
                r = ("inactive",)
            else:
                chiffre = mem.recall("techchrcgrid_chiffre", self)
                rcs = mem.recall("techchrcgrid_rcs", self)
                isqrow = mem.recall("techchrcgrid_isqrow", self)
                isqcol = mem.recall("techchrcgrid_isqcol", self)
                if rcs == "row":
                    ibloc = isqrow
                elif rcs == "col":
                    ibloc = isqcol
                else:
                    ibloc = None
                details = (("chiffre", chiffre),
                     ("rcs", rcs),
                     ("rang/colonne", ibloc))
                r = ("active", details)
        TEST.display("techchrcgrid", 3, "Statut de la résolution : {0}" \
                                         .format(r) )
        return r

    def techName(self):
        return "TechChRCgrid"

    def techClassName():
        return "TechChRCgrid"
    
    def instName(self):
        return "instance de {0}".format(self.techName())

    def __str__(self):
        return "Technique de résolution 'Chiffre/rang-colonne' sur toute la "\
               "grille pour le chiffre {0}".format(self._chiffre)


##TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 
##TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 

if __name__ == "__main__":

    import sudotestall
    testlevel = 3
    TEST.levelAll(testlevel)
    ui.display("Tous les niveaux de test sont à {0}".format(testlevel))

    #mode GUI
    ui.UImode(ui.GUI)
    TEST.displayUImode(MODE_BOTH, 2)

    import sudogrid
    from sudogridview import SudoGridView
    
    ui.display("\nTest du module techrcg.py")
    ui.display("Technique de résolution TechChRCgrid")
    ui.display("------------------------------------\n")
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
    gridInit = grid.copy()
    ui.display("Grille test choisie : gr = ")
    gr.show()
    ui.displayGridAll(grid)
    
    ui.display("\nVariable SudoMemory : mem")
    mem = SudoMemory()
    ui.display("Variable SudoGridView : view")
    view = SudoGridView(grid)
    ui.display("Création de 2 instances de technique de résolution.")
    ui.display("Instance de technique TechChRCgrid : tech1 et tech2")
    tech1 = TechChRCgrid(mem, (1,))
    tech2 = TechChRCgrid(mem, (8,))
    ui.display("\nTEST au niveau 3\n")
    TEST.test("techchrcgrid",3)
    TEST.test("loop", 3)
    ui.sudoPause()

def reset():
    '''remet la grille de test dans son état initial et renouvelle les
    instances 'mem' et 'tech'.
    '''
    global mem
    mem = SudoMemory()
    global tech1
    tech1 = TechChRCgrid(mem, (1,))
    global tech2
    tech2 = TechChRCgrid(mem, (8,))
    gr.fillByRowLines(vals)
    ui.displayGridClear()
    ui.displayGridAll(grid)
    
def loopStep(tech):
    '''Cette fonction exécute une itération de la boucle de pensée ROMA
    avec  l'instance de TechChRCgrid indiquée en argument.
    '''
    if view.isCompleted():
        ui.display("loopTech - Grille terminée, c'est gagné !")
        return "win"
    
    r = tech.apply(mem)
    action = r[0]
    TEST.display("loop", 2,
                 "loopStep - Résultat de tech.apply() : {0}".format(r))
    status = tech.status(mem)
    TEST.display("loop", 3,
                 "loopStep - statut d'avancement de tech: {0}".format(status))
    if action == "observe":
        pattern = r[1]
        found = view.lookup(pattern)
        mem.memorizeObs(found, tech)
        TEST.display("loop", 2,
                     "loopStep - Résultat de view.lookup() : {0}".format(found))
        tech.obsFound(mem, found)
    elif action == "place":
        placement = r[1]
        (row, col, val) = placement
        TEST.display("loop", 1, "loopStep - Placement de {0} en ({1}, {2})"\
                                 .format(val, row, col))
        valid = view.place(placement)
        TEST.display("loop", 2,
                     "loopStep - Résultat de view.place() : {0}".format(r))
        tech.placeOk(mem, valid)
        ui.displayGridPlace(grid, row, col)
    TEST.display("loop", 2,
                 "loopStep - Action exécutée par la tech : {0}".format(action))
    return action
        
def loopTech(tech, pause=False):
    '''Applique itérativement la technique indiquée en bouclant loopStep()
    jusqu'à ce que la technique retourne 'end' pour indiquer sa fin. Permet
    de demander une pause clavier à chaque boucle.
    '''
    TEST.display("loop", 1,
                 "Boucle de résolution de TechChRCgrid sur tous les carrés")
    global grid
    iter = 0
    while True:

        TEST.display("loop", 2, "\nloopTech - Début de boucle")
        if view.isCompleted():
            TEST.display("loop", 1, "loopTech - Grille terminée, c'est gagné !")
            return
        action = loopStep(tech)
        #éviter une boucle infinie
        iter +=1
        if iter > 200:
            ui.displaySTD("loopTech - STOP, plus de 100 itérations de boucle !!!")
            break
        #fin de la technique
        if action == "end":
            break
        #si une pause de boucle est demandée 
        if pause:
            r = ui.sudoPause(True)
            if r is True:
                TEST.display("loop", 2, "")
            else:   #Ctrl-C ou Ctrl-D
                ui.displaySTD("Interruption clavier")
                break
        continue

    if view.isCompleted():
        TEST.display("loop", 1, "loopTech - Grille terminée, c'est gagné !")
    else:
        TEST.display("loop", 1, "loopTech - Perdu, la grille n'est pas résolue.")
    return

