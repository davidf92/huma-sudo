'''SudoSimu - Module techlplcs - Technique de résolution "dernier placement"
locale sur un carré.

Ce module contient la classe TechLastPlcSqr qui applique la technique
de résolution "dernier placement" localement sur un carré.
Cette technique locale peut être exécutée soit par AI directement, soit par
une technique globale (par exemple TechLastPlcPlace).
Elle peut aussi être exécutée avec répétition sur la grille ou sur une zone
globale intermédiaire (par exemple SudoLastPlcGrid). Dans cd cas il faut créer
une nouvelle instance de la technique à chaque itération de répétition.

Instanciation :
---------------
   TechLastPlcSqr(mem, args)
   args est un tuple qui contient le carré sur lequel appliquer la technique

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
Clé commune = "techlplcsqr_............."
"techlplcsqr_encours"   -> indique si la technique est en cours d'application
"techlplcsqr_finished"  -> indique si la technique est terminée
"techlplcsqr_nbplcsqr"  -> le nombre de placements faits sur le carré
"techlplcsqr_isqr"      -> le numéro du carré auquel s'applique la technique
"techlplcsqr_stepsqr"   -> étape suivante de résolution
"techlplcsqr_action_suivante" -> pointeur d'action pour l'itération suivante
"techlplcsqr_index_obs" -> index d'observations
"techlplcsqr_obspattern"   -> le tuple de codification de l'observation demandée
"techlplcsqr_obsfound"  -> résultat d'observation
"techlplcsqr_coordplc"  -> place de l'emplacement libre trouvé dans le carré

change.log
----------
11/10/2017
Suppression des paramètres 'mem' inutiles dans toutes les méthodes
19/09/2017
Cette version est une mise à jour majeure dans le cadre de la simulation des
techniques avec distinction local/global et avec les répétitions
Le code est copié directement du module techlplcr et adapté aux blocs
'sqr' en remplacement de 'row'. Toute la logique est la même. 

'''

if __name__ in ("__main__", "techlplcs", "techlplc.techlplcs"):
    import sudoui as ui
    import sudorules as rules
    from sudorules import Sudoku_Error
    from sudomemory import SudoMemory
    import sudogridview as gridview
    from sudotest import *
elif __name__ == "sudosimu.techlplc.techlplcs":
    from sudosimu import sudoui as ui
    from sudosimu import sudorules as rules
    from sudosimu.sudorules import Sudoku_Error
    from sudosimu.sudomemory import SudoMemory
    from sudosimu import sudogridview as gridview
    from sudosimu.sudotest import *
else:
    raise Exception("Impossible de faire les imports dans le module techlplcs.")


class TechLastPlcSqr():
    '''Classe qui encapsule la technique de résolution 'Dernier placement'
    sur un seul carré. Pour chaque occurence d'application de la technique,
    une instance est créée.
    Concernant les données en mémoire de l'application, l'utilisation de la
    clé secondaire 'self' évite tout mélange entre deux instances qui seraient
    appliquées simultanément (imbrications).
    '''

    def __init__(self, mem, args):
        '''Initialise l'instance pour appliquer la technique au carré indiqué
        en utilisant la mémoire du joueur 'mem'.
        '''
        TEST.display("techlplcsqr", 3, "TechLastPlcSqr - Dans __init__()")
        #l'id du carré est passé en argument
        isqr = args[0]
        TEST.display("techlplcsqr", 2, \
                     "Nouvelle instance de la technique TechLastPlcSqr "\
                     "appliquée au carré {0}".format(isqr))
        self._mem = mem
        mem.memorize("techlplcsqr_isqr", isqr, self)
        self._clear_tech_mem()
        self._finished = False
        self._encours = False
        self._initOk = True
        return

    def _clear_tech_mem(self):
        '''Initialise les données mémorisées pour le déroulement de la
        techniques étape par étape.
        '''
        TEST.display("techlplcsqr", 3,
                     "TechLastPlcSqr - Dans _clear_tech_mem()- Remise à zéro "\
                     "de toutes les variables d'exécution")
        mem = self._mem
        mem.memorize("techlplcsqr_finished", False, self)
        mem.memorize("techlplcsqr_encours", False, self)
        mem.memorize("techlplcsqr_index_obs", None, self)
        mem.memorize("techlplcsqr_coordcol", None, self)
        mem.memorize("techlplcsqr_stepsqr", None, self)
        mem.memorize("techlplcsqr_action_suivante", None, self)
        mem.memorize("techlplcsqr_nbplcsqr", 0, self)
        
    def apply(self):
        '''Méthode d'application de cette technique. Elle est appelée
        répétitivement pour faire progresser la technique étape par étape.
        '''
        TEST.display("techlplcsqr", 3, "TechLastPlcSqr - Dans apply()")
        assert self._initOk
        #si la technique est terminée, sortir tout de suite
        if self._finished is True:
            TEST.display("techlplcsqr", 3,
                         "Technique déjà terminée, sortie immédiate.")
            return ("end", ("finished", None))
        mem = self._mem

        #selon qu'une résolution est déjà en cours ou pas
        if mem.recall("techlplcsqr_encours", self) is False:
            #pas de résolution en cours : débuter la technique
            TEST.display("techlplcsqr", 2, \
                         "Technique de résolution \"Dernier placement sur "+
                         "un carré\"")
            try:
                r = self._start_apply()
            except:
                ui.displayError("Erreur", "Echec de la méthode de résolution.")
                TEST.display("techlplcsqr", 1, \
                             "ERREUR FATALE : échec de la technique 'dernier "\
                             "placement sur les carrés.\n"\
                             "la résolution est abandonnée.")
                mem.memorize("techlplcsqr_encours", None, self)
                r = ("fail", "Erreur d'exécution du programme TechLastPlc.")
        else:
            #déjà une résolution en cours, la continuer
            TEST.display("techlplcsqr", 2, "LastPlcSqr suite de la résolution")
            methode = mem.recall("techlplcsqr_action_suivante", self)
            TEST.display("techlplcsqr", 3, \
                         "Méthode à exécuter : {0}".format(methode))
            try:
                r = methode()
            except:
                ui.displayError("Erreur", "Echec de la méthode de résolution.")
                TEST.display("techlplcsqr", 2, \
                             "ERREUR FATALE : échec de la technique 'dernier "\
                             "placement sur les carrés.\n"\
                             "la résolution est abandonnée.")
                mem.memorize("techlplcsqr_encours", None, self)
                r = ("fail", "Erreur d'exécution du programme TechLastPlc.")
        return r

    def resume(self):
        '''Méthode de résolution alternative appelée par Thinking dans le cas
        où la technique est continuée après une mise en attente du fait
        de l'imbrication d'autres techniques. Permet de faire des vérifications
        de cohérence des données mémorisées pendant la mise en attente,
        avant de reprendre l'application.
        '''
        TEST.display("techlplcsqr", 3, "TechLastPlcSqr - dans resume()")
        assert self._initOk
        # dans cette version ne fait encore rien de particulier.
        return self.apply()

    def _start_apply(self):
        '''Début de la résolution. Initialisation des informations en mémoire
        et lancement de la résolution des carrés.
        '''
        TEST.display("techlplcsqr", 3, "TechLastPlcSqr - dans _start_apply()")
        TEST.display("techlplcsqr", 2, "LastPlcSqr : début de résolution.")
        assert self._initOk
        mem = self._mem
        mem.memorize("techlplcsqr_encours", True, self)
        #comptages
        mem.memorize("techlplcsqr_nbplcsqr", 0, self)
        #on commence par l'étape n°1
        mem.memorize("techlplcsqr_stepsqr", 0, self)
        #commencer la résolution des carrés
        r = self._solve_sqr()
        return r
        
    def _solve_sqr(self):
        '''Résolution pour un carré - Début, demande la 1ère observation : quelles
        sont les cases vides de ce carré.
        '''
        TEST.display("techlplcsqr", 3, "TechLastPlcSqr - dans _solve_sqr()")
        assert self._initOk
        mem = self._mem
        #à quel carré en est-on ?
        isqr = mem.recall("techlplcsqr_isqr", self)
        TEST.display("techlplcsqr", 3, \
                     "Début de résolution du carré n° {0}".format(isqr))
        #1ère étape : observer quelles sont les cases vides du carré
        obsPattern = (gridview.OBS_SQR_EMPTYPLC, (isqr,) )
        #mémoriser ce qui a été demandé, pour l'itération suivante
        mem.memorize("techlplcsqr_obspattern", obsPattern, self)
        #incrémenter l'index d'observations
        mem.increment("techlplcsqr_indexobs", 1, self)
        #memoriser l'avancement vers l'opération suivante
        mem.memorize("techlplcsqr_stepsqr", 1, self)
        mem.memorize("techlplcsqr_action_suivante", self._sqr_suite1, self)
        #réinitialiser l'indicateur de résultat d'observation
        mem.memorize("techlplcsqr_obsfound", None, self)
        #retourner en indiquant la demande d'observation
        r = ("observe", obsPattern)
        TEST.display("techlplcsqr", 3, \
                     "Demande 1ère observation : pattern = {0}".format(obsPattern))
        return r

    def _sqr_suite1(self):
        '''Résolution pour un carré - Retour 1ère observation.
        S'il y a un bon résultat d'observation, demande la 2ème observation : quel
        est le chiffre manquant sur ce carré.
        '''
        TEST.display("techlplcsqr", 3, "TechLastPlcSqr - dans _sqr_suite1()")
        assert self._initOk
        mem = self._mem
        #à quel carré en est-on ?
        isqr = mem.recall("techlplcsqr_isqr", self)
        TEST.display("techlplcsqr", 3, \
                     "carré n° {0} : retour 1ère observation".format(isqr))
        #résultat de l'observation : recherche des cases vides du carré
        #Attention : gérer les cas de retour d'observation invalide
        try:
            found = mem.recall("techlplcsqr_obsfound", self)
            assert found not in (None, False)
            (nb, listPlc) = found
            assert nb == int(nb)        #valide que c'est un nombre entier
            assert 0 <= nb <= 9
            assert 0 <= len(listPlc) <= 9
            for i in listPlc:
                assert i == int(i)      #valide que c'est un nombre entier
                assert 0 <= i <= 9
        except:     #quelle que soit l'erreur
            #La technique doit être interrompue
            self._reset_tech()
            raise Sudoku_Error("Retour d'observation invalide. " +
                               "Technique de résolution abandonnée.")
        
        if nb == 1:     #il manque un seul chiffre => opportunité de placement
            #mémoriser l'emplacement trouvé. C'est un indice de place dans le carré
            mem.memorize("techlplcsqr_coordplc", listPlc[0], self)
            #2ème étape : il manque un seul chiffre, lequel est-ce ?
            obsPattern = (gridview.OBS_SQR_MISSING, (isqr,) )
            #mémoriser ce qui a été demandé, pour l'itération suivante
            mem.memorize("techlplcsqr_obspattern", obsPattern, self)
            #memoriser l'avancement et l'opération suivante
            mem.memorize("techlplcsqr_action_suivante", self._sqr_suite2, self)
            mem.memorize("techlplcsqr_stepsqr", 2, self)
            #réinitialiser l'indicateur de résultat d'observation
            mem.memorize("techlplcsqr_obsfound", None, self)
            #retourner en indiquant la demande d'observation
            r = ("observe", obsPattern)
        elif nb == 0:       #aucune case vide
            #la technique est terminée sans rien à faire
            r = self._solve_fin("noplace")
            TEST.display("techlplcsqr", 3, \
                         "carré {0} : aucune case vide, c'est terminé" \
                         .format(isqr))
        else:            
            #nb>1 => plusieurs cases vides : 
            #dans cette version on ne le gère pas (plus compliqué)
            r = self._solve_fin("quit")
            TEST.display("techlplcsqr", 3, \
                         "carré {0} : {1} cases vide. On ne traite pas ce cas" \
                         .format(isqr, nb) + "dans la technique LastPlcSqr.")
        return r
        
    def _sqr_suite2(self):
        '''Résolution pour un carré - Retour 2ème observation = le chiffre
        manquant. Fait le placement.
        '''
        TEST.display("techlplcsqr", 3, "TechLastPlcSqr - dans _sqr_suite2()")
        assert self._initOk
        mem = self._mem
        #à quel carré en est-on ?
        isqr = mem.recall("techlplcsqr_isqr", self)
        TEST.display("techlplcsqr", 3, \
                     "carré n° {0} : retour 2ème observation".format(isqr))
        #décodage de la réponse d'observation : quel est le chiffre manquant
        #Attention : gérer les cas de retour d'observation invalide
        try:
            found = mem.recall("techlplcsqr_obsfound", self)
            assert found is not None
            chiffre = found[1][0]
            assert chiffre == int(chiffre)
            assert 0 <= chiffre <= 9
        except:
            #Quelle que soit l'erreur, la technique doit être interrompue
            raise Sudoku_Error("TechLastPlcSqr - Retour d'observation invalide. "\
                               "Technique de résolution abandonnée.")

##ATTENTION AUX COORDONNEES
        #3ème étape : prêt pour placer ce chiffre - se rappeler l'emplacement.
        #l'emplacement était un indice de place (plc) dans ce carré.
        iplc = mem.recall("techlplcsqr_coordplc", self)
        #transformer les coordonnées en RC pour faire le placement        
        (irow,icol) = Rules.ruleCoordToRC(isqr, iplc)
        TEST.display("techlplcsqr", 2, \
                     "Placement de {0} dans le carré {1} à la case {2}" \
                     .format(chiffre, isqr, iplc))
        #memoriser l'avancement et l'opération suivante
        mem.memorize("techlplcsqr_stepsqr", 3, self)
        mem.memorize("techlplcsqr_action_suivante", self._sqr_suite3, self)
        #réinitialiser l'indicateur de résultat de placement
        mem.memorize("techlplcsqr_placeok", None, self)
        #retourner en indiquant une demande de placement
        r = ("place", (irow, icol, chiffre))
        return r
    
    def _sqr_suite3(self):
        '''Résolution pour un carré - Retour de placement'''
        TEST.display("techlplcsqr", 3, "TechLastPlcSqr - dans _sqr_suite3()")
        assert self._initOk
        mem = self._mem
        #à quel carré en est-on ?
        isqr = mem.recall("techlplcsqr_isqr", self)
        #Mise à jour comptages.
        nbplcsqr = mem.increment("techlplcsqr_nbplcsqr", 1, self)
        TEST.display("techlplcsqr", 3, \
                     "Carré n° {0} : retour de placement correct.".format(isqr)\
                     + "\nNombre de placements : {0}".format(nbplcsqr))
        #Etat d'avancement - fin de la technique sur ce carré
        mem.memorize("techlplcsqr_stepsqr", 4, self)
        r = self._solve_fin("succeed")
        return r

    def _solve_fin(self, endResult="end"):
        """A la fin de résolution de la technique, la marque comme terminée.
        Il faudra appeler 'reset()' avant de la relancer.
        """
        TEST.display("techlplcsqr", 3, "TechLastPlcSqr - dans _solve_fin()")
        assert self._initOk
        mem = self._mem
        nbplcsqr = mem.recall("techlplcsqr_nbplcsqr", self)
        TEST.display("techlplcsqr", 2, \
                     "Fin de la technique \'Dernier placement sur un carré\'. "\
                     "\nNombre de chiffres placés : {0}".format(nbplcsqr))
        self._finish_apply()
        #construire le tuple de détail de résultats
        endDetails = (endResult, nbplcsqr)
        TEST.display("techlplcsqr", 2, "La technique se termine avec le "\
                     "résultat : '{0}'".format(endDetails))
        #retourne à SudoThinking en renvoyant les comptages
        return ("end", endDetails)

    def _finish_apply(self):
        '''Marque la technique comme terminée. Il faudra appeler 'reset()'
        pour la relancer.
        '''
        TEST.display("techlplcsqr", 3, "TechLastPlcSqr - dans _finish_apply()")
        assert self._initOk
        mem = self._mem
        self._mem.memorize("techlplcsqr_isqr", None, self)
        self._mem.memorize("techlplcsqr_finished", True, self)
        self._mem.memorize("techlplcsqr_encours", False, self)
        self._finished = True
        return

    def obsFound(self, found):
        '''Prend connaissance du résultat de l'observation demandée par la
        technique.
        '''
        TEST.display("techlplcsqr", 3, "TechLastPlcSqr - dans obsFound()")
        assert self._initOk
        #si la technique est déjà terminée, retourne "end"
        if self._finished is True:
            return ("end", ("finished", None))
        self._mem.memorize("techlplcsqr_obsfound", found, self)
        return ("continue", None)

    def placeOk(self, placed=True):
        '''Prend connaissance du succès d'un placement par la technique.'''
        TEST.display("techlplcsqr", 3, "TechLastPlcSqr - dans placeOk()")
        assert self._initOk
        #si la technique est déjà terminée, retourne "end"
        if self._finished is True:
            return ("end", ("finished", None))
        self._mem.memorize("techlplcsqr_placeok", placed, self)        
        return ("continue", None)
        
    def abort(self):
        '''Arrêt d'exécution de la technique avant sa fin et marque la technique
        comme terminée. Il faudra appeler 'reset()' avant de la relancer.
        Retourne le nombre d'actions effectuées avant l'arrêt
        '''
        TEST.display("techlplcsqr", 3, "TechLastPlcSqr - dans abort()")
        TEST.display("techlplcsqr", 1, "Abandon de la technique en cours")
        mem = self._mem
        nbplcsqr = mem.recall("techlplcsqr_nbplcsqr", self)
        TEST.display("techlplcsqr", 2, \
                     "Nombre total de chiffres placés : {0}" \
                     .format(nbplcsqr))
        mem.memorize("techlplcsqr_encours", False, self)
        self._finish_apply()
        return ("end", ("abort", nbplcsqr))

    def reset(self):
        self._clear_tech_mem()
        self._finished = False
        return ("reset", None)

    def status(self):
        """Retourne l'état d'avancement de la technique"""
        TEST.display("techlplcsqr", 3, "TechLastPlcSqr - Dans status()")
        mem = self._mem
        finished = mem.recall("techlplcsqr_finished", self)
        if finished is True:
            r = ("end", ("finished", None))
        else:
            encours = mem.recall("techlplcsqr_encours", self)
            if encours is False:
                r = ("inactive", None)
            else:
                isqr = mem.recall("techlplcsqr_isqr", self)
                step = mem.recall("techlplcsqr_stepsqr", self)
                r = ("active", ("sqr", isqr, step))
        TEST.display("techlplcsqr", 3,
                     "Statut de la résolution : {0}".format(r))
        return r

    def techName(self):
        return "TechLastPlcSqr"

    def techClassName():
        return "TechLastPlcSqr"
    
    def instName(self):
        return "instance de {0}".format(self.techName())

    def __str__(self):
        return "Technique de résolution 'Dernier placement' sur un carré"


##TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 
##TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 

if __name__ == "__main__":

    import sudotestall
    testlevel = 3
    TEST.levelAll(testlevel)
    ui.display("Tous les niveaux de test sont à {0}".format(testlevel))

    import sudogrid
    
    ui.display("\nTest du module techlplcr")
    ui.display("Test de la technique de résolution LastPlcSqr")
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
    ui.display("Création de 2 instances de technique de résolution.")
    ui.display("Instance de technique TechLastPlc : tech1 et tech2")
    tech1 = TechLastPlcSqr(mem, (1,))
    tech2 = TechLastPlcSqr(mem, (1,))
    ui.display("\nTEST au niveau 3\n")
    TEST.test("techlplcsqr",3)
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
