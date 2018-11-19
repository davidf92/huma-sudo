'''SudoSimu - Module techchrcga - technique de résolution "chiffre/rang-colonne"
globale sur la grille entière pour tous les chiffres.

Ce module contient la classe TechChRCgridAll, qui applique par répétition les
techniques de résolution "chiffre/rang-colonne" sur toute la grille et pour
tous les chiffres. TechChRCgridAll enchaîne pour chaque chiffre de 1 à 9 la
technique semi-globale réalisée par la classe TechChRCgrid.

Les instances de cette classe représentent des raisonnement systématiques
et itératifs de résolution, qui font globalement partie de la pensée du joueur,
tout en étant autonomes par leur côté systématique. Le raisonnement évolue étape
par étape à chaque appel de la méthode apply(), et retourne des demandes
d'observation de la grille et de placement de chiffres. Au niveau global de la
pensée, c'est la partie AI (classe SudoThinkAI) qui décide d'appliquer une
technique et qui instancie la classe, puis c'est la partie pensée logique
(classe SudoThinking) qui organise l'enchaînement et appelle la méthode apply().

Dernière mise à jour : 11/10/2017
Vérification de complétude des modifications -suppr-mem- et -split-
'''

if __name__ in ("__main__", "techchrcga", "techchrc.techchrcga"):
    #imports des modules de la simulation
    import sudoui as ui
    import sudorules as rules
    from sudorules import Sudoku_Error
    from sudomemory import SudoMemory
    import sudogridview as gridview
    from sudotest import *
    #import des modules de techniques locales de résolution
    from techchrc.techchrcg import TechChRCgrid
elif __name__ == "sudosimu.techchrc.techchrcga":
    #imports des modules de la simulation
    from sudosimu import sudoui as ui
    from sudosimu import sudorules as rules
    from sudosimu.sudorules import Sudoku_Error
    from sudosimu.sudomemory import SudoMemory
    from sudosimu import sudogridview as gridview
    from sudosimu.sudotest import *
    #import des modules de techniques locales de résolution
    from sudosimu.techchrc.techchrcg import TechChRCgrid
else:
    raise Exception("Impossible de faire les imports dans le module techchrcga.")


class TechChRCgridAll():
    '''Classe qui encapsule la technique de résolution "chiffre/rang-colonne"
    sur la grille entière et pour tous les chiffres.
    '''

    def __init__(self, mem, args=None):
        '''Initialise l'instance en utilisant la mémoire du joueur 'mem'.
        Le paramètre 'args' est inutilisé.
        '''
        TEST.display("techchrcgridall", 3, "TechChRCgridAll - Dans __init__()")
        TEST.display("techchrcgridall", 2, \
                     "\nNouvelle instance de la technique TechChRCgridAll.")
        self._mem = mem
        #Initialiser les données en mémoire de la résolution
        self._clear_tech_mem()
        #init contrôle d'exécution (en_cours, finished etc.)
        self._finished = False  #uniquement pour éviter une erreur de code
        self._resume = False    #indique appel de resume() au lieu de apply()
        self._encours = False
        self._initOk = True
        return

    def _clear_tech_mem(self):
        '''Initialise les données d'application de la technique par le joueur
        dans sa mémoire.
        '''
        TEST.display("techchrcgridall", 3, "TechChRCgridAll - "\
                                            "Dans _clear_tech_mem()")
        mem = self._mem
        mem.memorize("techchrcgridall_chiffre", 0, self)
#        mem.memorize("techchrcgridall_isqrow", 0, self)
#        mem.memorize("techchrcgridall_isqcol", 0, self)
        mem.memorize("techchrcgridall_techclass", None, self)
        mem.memorize("techchrcgridall_techloc", None, self)
        mem.memorize("techchrcgridall_techlocname", "<inconnue>", self)
        mem.memorize("techchrcgridall_nbplctot", 0, self)
        mem.memorize("techchrcgridall_finished", False, self)
        return True

#### import des fonctions d'étapes successives de l'algorithme d'application
    if __name__ in ("__main__", "techchrcg", "techchrc.techchrcga"):
        from techchrc.techchrcga2 import _start_apply
        from techchrc.techchrcga2 import _apply_techloc
        from techchrc.techchrcga2 import _techloc_end
        from techchrc.techchrcga2 import _next_techloc
        from techchrc.techchrcga2 import _finish_apply
        from techchrc.techchrcga2 import _newGridTechInst
    elif __name__ == "sudosimu.techchrc.techchrcga":
        from sudosimu.techchrc.techchrcga2 import _start_apply
        from sudosimu.techchrc.techchrcga2 import _apply_techloc
        from sudosimu.techchrc.techchrcga2 import _techloc_end
        from sudosimu.techchrc.techchrcga2 import _next_techloc
        from sudosimu.techchrc.techchrcga2 import _finish_apply
        from sudosimu.techchrc.techchrcga2 import _newGridTechInst
    else:
        raise Exception("Impossible de faire les imports dans le module techchrcga.")
####
    
    def apply(self):
        '''Méthode d'application de cette technique. Elle est appelée
        répétitivement pour faire progresser la technique étape par étape.
        '''
        TEST.display("techchrcgridall", 3, "TechChRCgridAll - Dans apply()")
        assert self._initOk
        mem = self._mem
        #si la technique est terminée, sortir tout de suite
        if self._finished is True:
            TEST.display("techchrcgridall", 2,
                         "Technique déjà terminée.")
            return ("end", None)

        #gérer la répétition de l'exécution
        if self._encours is not True:
            self._encours = True
            TEST.display("techchrcgridall", 1, "Technique de résolution "\
                         "\'Chiffre/rang-colone\' sur la grille entière ")
            r = self._start_apply()
        else:
            #déjà une résolution en cours, la continuer
            TEST.display("techchrcgridall", 2, \
                         "TechChRCgridAll - suite de la même technique")
            r = self._apply_techloc()
        TEST.display("techchrcgridall", 2, "TechChRCgridAll  - apply() retourne : {0}" \
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

        TEST.display("techchrcgridall", 3, "TechChRCgridAll - dans resume()")
        assert self._initOk
        assert self._encours    #la première itération doit avoir été apply()
        #indique l'état "resume" avant de passer à la résolution normale
        self._resume = True
        r = self.apply()
        TEST.display("techchrcgridall", 3, "TechChRCgridAll - retour à resume()")
        #remet l'indicateur à zéro pour les prochaines fois
        self._resume = False
        return r


    def obsFound(self, found):
        '''Transmet le résultat d'observation à la technique locale en cours
        qui a demandé cette observation. Traite le cas particulier où la
        tech. locale retourne "end", qu'il faut gérer globalement.
        '''
        TEST.display("techchrcgridall", 3, "TechChRCgridAll - dans obsFound()")
        assert self._initOk
        mem = self._mem
        #si la technique est déjà terminée, retourne "end"
        if self._finished is True:
            return ("end", None)
        TEST.display("techchrcgridall", 3, "Résultat d'observation : {0}"\
                                         .format(found))
        #transmettre le résultat à la technique locale en cours
        techloc = mem.recall("techchrcgridall_techloc", self)
        r = techloc.obsFound(found)
        TEST.display("techchrcgridall", 3, "TechChRCgridAll - retour à obsFound()")
        TEST.display("techchrcgridall", 3, "TechChRCgridAll - retour de "\
                                    "obsFound() de la technique {0} : {1}"\
                                    .format(techloc.techName(), r))
        #si la technique locale retourne "end", traiter ce cas tout de suite
        if r[0] == "end":
            endDetails = r[1]
            TEST.display("techchrcgridall", 3, "obsFound : la technique locale "\
                         "a renvoyé 'end' ")
            r = self._techloc_end(mem, endDetails)
        return r
    
    def placeOk(self, placed=None):
        '''Prend connaissance du succès d'un placement par la technique. Traite
        le cas particulier où la tech. locale retourne "end", qu'il faut
        gérer au niveau de cette technique globale
        '''
        TEST.display("techchrcgridall", 3, "TechChRCgridAll - dans placeOk()")
        assert self._initOk
        mem = self._mem
        #si la technique est déjà terminée, retourne "end"
        if self._finished is True:
            return ("end", None)
        TEST.display("techchrcgridall", 3, "Résultat de placement : {0}"\
                                         .format(placed))
        #transmettre le résultat à la technique locale en cours
        techloc = mem.recall("techchrcgridall_techloc", self)
        r = techloc.placeOk(placed)
        TEST.display("techchrgridall", 3, "TechChRCgridAll - retour à placeOk()")
        TEST.display("techchrcgridall", 3, "TechChRCgridAll - retour de "\
                                     "placeOk() de la technique {0} : {1}"\
                                     .format(techloc.techName(), r))
        #si la technique locale retourne "end", traiter ce cas tout de suite
        if r[0] == "end":
            endDetails = r[1]
            TEST.display("techchrcgridall", 3, "placeOk : la technique locale "\
                         "{0} a renvoyé 'end' ".format(techloc.techName()))
            r = self._techloc_end(mem, endDetails)
        return r
        
    def abort(self):
        '''Arrêt d'exécution de la technique avant sa fin et marque la technique
        comme terminée. Il faudra appeler 'reset()' avant de la relancer.
        Retourne le nombre d'actions effectuées avant l'arrêt
        '''
        TEST.display("techchrcgridall", 3, "TechChRCgridAll - dans abort()")
        assert self._initOk
        mem = self._mem
        TEST.display("techchrcgridall", 1, "Abandon de la technique en cours")
        plctot = mem.recall("techchrcgridall_nbplctot", self)
        TEST.display("techchrcgridall", 1, \
                     "Nombre total de chiffres placés : {0}" \
                     .format(plctot))
        self._finish_apply()
        self._finished = True
        self._encours = False
        return ("abort", plctot)

    def reset(self):
        '''Rénitialise l'instance la technique. Ne devrait pas être utilisé
        en version de production car il faut utiliser à chaque fois une
        nouvelle instance de technique.
        Mais utile en débuggage et tests.
        '''
        TEST.display("techchrcgrid", 3, "TechChRCgrid - dans reset()")
        mem = self._mem
        self._clear_tech_mem(mem)   #la mémoire du joueur
        self._init_tech(mem)        #variables d'exécution de la technique
        self._initOk = True
        return True
        
    def status(self):
        '''Retourne l'état d'avancement de la technique'''
        TEST.display("techchrcgridall", 3, "Fonction status()")
        assert self._initOk
        mem = self._mem
        if self._finished is True:
            r = ("end", None)
        else:
            if self._encours is False:
                r = ("inactive",)
            else:
                chiffre = mem.recall("techchrcgridall_chiffre", self)
                rcs = mem.recall("techchrcgridall_rcs", self)
                isqrow = mem.recall("techchrcgridall_isqrow", self)
                isqcol = mem.recall("techchrcgridall_isqcol", self)
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
        TEST.display("techchrcgridall", 3, "Statut de la résolution : {0}" \
                                         .format(r) )
        return r

    def techName(self):
        return "TechChRCgridAll"

    @property
    def name(self):
        return self.techName()

    def techClassName():
        return "TechChRCgridAll"
    
    def instName(self):
        return "instance de {0}".format(self.techName())

    def __str__(self):
        return "Technique de résolution 'Chiffre/rang-colonne' sur toute la "\
               "grille et pour tous les chiffres."


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
    from sudogridview import SudoGridView
    
    ui.display("\nTest du module techrcg.py")
    ui.display("Technique de résolution TechChRCgridAll")
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
    ui.display("Grille test choisie : gr = ")
    gr.show()
    ui.displayGridAll(grid)
    
    ui.display("\nVariable SudoMemory : mem")
    mem = SudoMemory()
    ui.display("Variable SudoGridView : view")
    view = SudoGridView(grid)
    ui.display("Création de 2 instances de technique de résolution.")
    ui.display("Instance de technique TechChRCgridAll : tech1 et tech2")
    tech1 = TechChRCgridAll(mem)
    tech2 = TechChRCgridAll(mem)
    ui.display("\nTEST au niveau 3\n")
    TEST.test("techchrcgridall",3)
    TEST.test("loop", 3)
    ui.sudoPause()

def reset():
    '''remet la grille de test dans son état initial et renouvelle les
    instances 'mem' et 'tech'.
    '''
    global mem
    mem = SudoMemory()
    global tech1
    tech1 = TechChRCgridAll(mem)
    global tech2
    tech2 = TechChRCgridAll(mem)
    gr.fillByRowLines(vals)
    gr.fillByRowLines(vals)
    ui.displayGridClear()
    ui.displayGridAll(grid)

def loopStep(tech):
    '''Exécute une itération de la boucle de pensée ROMA avec  l'instance
    de TechChRCgridAll indiquée en argument.
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
                 "Boucle de résolution de TechChRCgridAll sur la grille "\
                 "entière et pour tous les chiffres.")
    global grid
    iter = 0
    while True:

        TEST.display("loop", 2, "\nloopTech - Début de boucle")
        if view.isCompleted():
            ui.display("loopTech - Grille terminée, c'est gagné !")
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
            if r:
                ui.displaySTD("")
            else:   #Ctrl-C ou Ctrl-D
                ui.display("Interruption clavier")
                break
        continue

    if view.isCompleted():
        ui.display("loopTech - Grille terminée, c'est gagné !")
    return

