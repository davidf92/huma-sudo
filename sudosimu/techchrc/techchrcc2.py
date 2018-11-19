'''SudoSimu - Module techchrcc - Technique de résolution "chiffre/rang-colonne"
locale pour un certain chiffre et sur une certaine colonne de carrés.

Script d'import dans techchrcc.py de fonctions et méthodes privées de la classe
TechChRCcol. Il s'agit des fonctions qui gèrent les états d'avancement
d'application de la technique.

Dernière mise à jour : 11/10/2017
Vérification de complétude des modifications -suppr-mem- et -split-,
parallèlement à la mise à jour de techchrcg.py.
Complément d'harmonisation du nommage pour _finish_apply()
'''


#imports des modules de la simulation
if __name__ in ("__main__", "techchrcc2", "techchrc.techchrcc2"):
    import sudoui as ui
    import sudorules as rules
    from sudorules import Sudoku_Error
    from sudomemory import SudoMemory
    import sudogridview as gridview
    from sudotest import *
elif __name__ == "sudosimu.techchrc.techchrcc2":
    from sudosimu import sudoui as ui
    from sudosimu import sudorules as rules
    from sudosimu.sudorules import Sudoku_Error
    from sudosimu.sudomemory import SudoMemory
    from sudosimu import sudogridview as gridview
    from sudosimu.sudotest import *
else:
    raise Exception("Impossible de faire les imports dans le module techchrcc2.")


def _start_apply(self):
    '''Début de la résolution. Initialisation des informations en mémoire
    et lancement de la résolution des colonnes.
    '''
    TEST.display("techchrccol", 3, "TechChRCcol - dans _start_apply()")
    TEST.display("techchrccol", 2, "TechChRCcol : début de résolution.")
    assert self._initOk
    mem = self._mem
    mem.memorize("techchrccol_encours", True, self)
    mem.memorize("techchrccol_stepcol", 0, self)
    
    #comptages
    mem.memorize("techchrccol_nbplccol", 0, self)
    #étape #0
    r = self._solve_debut()
    return r
    
def _solve_debut(self):
    '''Résolution pour une colonne de carrés - Début, et demande de la 1ère
    observation : quelles sont les carrés de cette colonne qui ne contiennent
    pas le chiffre.
    '''
    TEST.display("techchrccol", 3, "TechChRCcol - dans _solve_debut()")
    assert self._initOk
    mem = self._mem
    #se rappeler le chiffre à placer et dans quelle colonne de carrés
    chiffre = mem.recall("techchrccol_chiffre", self)
    icol = mem.recall("techchrccol_icol", self)
    isqcol = mem.recall("techchrccol_isqcol", self)
    TEST.display("techchrccol", 3, "_solve_debut() - "\
                 "Début de résolution de la colonne n° {0}".format(icol))
    #1ère étape : dans quels carrés est-ce que <chiffre> est absent
    obsPattern = (gridview.OBS_SQRSINSQRCOL_NOTCONTAIN, (isqcol, chiffre) )
    #mémoriser les informations pour l'itération suivante
    mem.memorize("techchrccol_result", "observe", self)
    mem.memorize("techchrccol_obspattern", obsPattern, self)
    #incrémenter l'index d'observations
    mem.increment("techchrccol_indexobs", self)
    #memoriser l'avancement et la fonction pour l'opération suivante
    mem.memorize("techchrccol_stepcol", 1, self)
    mem.memorize("techchrccol_action_suivante", self._solve_suite1, self)
    mem.memorize("techchrccol_nom_action", "suite 1", self)
    #retourner en indiquant la demande d'observation
    TEST.display("techchrccol", 3, "_solve_debut() - Demande 1ère "\
                 "observation : pattern = {0}".format(obsPattern))
    r = ("observe", obsPattern)
    return r

def _solve_suite1(self):
    '''Résolution pour une colonne (Col) - Retour 1ère observation = les
    carrés qui ne contiennent pas le chiffre traité.
    S'il y a 1 carré sans le chiffre, passe à l'observation suivante = quel
    est la colonne sur lequel le chiffre n'est pas.
    Dans les autre cas, fin avec succès ou échec.
    '''
    TEST.display("techchrccol", 3, "TechChRCcol - dans _solve_suite1()")
    assert self._initOk
    mem = self._mem
    #se rappeler le chiffre à placer et dans quelle colonne de carrés
    chiffre = mem.recall("techchrccol_chiffre", self)
    icol = mem.recall("techchrccol_icol", self)
    TEST.display("techchrccol", 3, "_solve_suite1() - Colonne de carrés "\
                 "n° {0} : retour 1ère observation".format(icol))
    #récupérer le résultat de l'observation et l'analyser
    #c'est un tuple de nombre et liste de carrés
    found = mem.recall("techchrccol_obsfound", self)
    (nbSqr, listSqr) = found
    
    #si tous les carrés de la colonne ont le chiffre, il n'y a rien d'autre
    #à faire et la technique est terminée
    if nbSqr <= 0:
        TEST.display("techchrccol", 3, "_solve_suite1 - Pas de carré à "\
                     "remplir, fin de la technique locale avec succès.")
        r = self._solve_fin("noplace")
        
    #s'il y a 2 ou 3 carrés, on ne le fait pas pour le moment (complexité)
    #donc le résultat de la technique = abandon
    elif nbSqr > 1:
        TEST.display("techchrccol", 3, "_solve_suite1() - Plus d'1 carré à "\
                     "remplir, trop complexe. La technique locale est "\
                     "abandonnée.")
        r = self._solve_fin("quit")

    #1 carré où le chiffre manque => la technique continue
    #algorithme : on cherche maintenant une seule colonne où le chiffre manque
    else:   #sbSqr==1
        isqr = listSqr[0]    #le carré en question
        TEST.display("techchrccol", 3, "_solve_suite1 - 1 carré à "\
                     "remplir, la technique passe à l'étape suivante.")
        #observation suivante : dans quelles colonnes de ce carré est-ce que
        #<chiffre> n'est pas ?
        obsPattern = (gridview.OBS_COLSBYSQR_NOTCONTAIN, (isqr, chiffre))
        #mémoriser les informations pour l'étape suivante
        mem.memorize("techchrccol_obspattern", obsPattern, self)
        mem.memorize("techchrccol_isqr", isqr, self)
        #incrémenter l'index d'observations
        mem.increment("techchrccol_indexobs", self)
        #état d'avancement et fonction pour l'opération suivante
        mem.memorize("techchrccol_result", "observe", self)
        mem.memorize("techchrccol_stepcol", 2, self)
        mem.memorize("techchrccol_action_suivante", self._solve_suite2, self)
        mem.memorize("techchrccol_nom_action", "suite 2", self)
        #retourner en indiquant la demande d'observation à faire
        TEST.display("techchrccol", 3, "_solve_suite1() : demande de 2ème "\
                     "observation : pattern = {0}".format(obsPattern))
        r = ("observe", obsPattern)
    return r

def _solve_suite2(self):
    '''Résolution pour une colonne (Col) - Retour 2ème observation = la
    colonne où le chiffre n'est pas. Il y en a forcément exactement 1.
    3ème observation à faire = les rangs de ce carré où le chiffre
    n'est pas.
    La seule cause possible d'échec est un fail mémoire, en particulier
    un fail de mémoire du résultat d'observation.
    '''
    TEST.display("techchrccol", 3, "TechChRCcol - dans _solve_suite2()")
    assert self._initOk
    mem = self._mem
    #se rappeler les infos en mémoire de l'étape précédente
    chiffre = mem.recall("techchrccol_chiffre", self)
    icol = mem.recall("techchrccol_icol", self)
    isqr = mem.recall("techchrccol_isqr", self)
    TEST.display("techchrccol", 3, "_solve_suite1() - Colonne de carrés "\
                 "n° {0} : retour 2ème observation".format(icol))
    #récupérer le résultat de l'observation et l'analyser
    #c'est un tuple de nombre et liste de colonnes
    found = mem.recall("techchrccol_obsfound", self)
    (nbCol, listCol) = found
    #détection d'erreur : il doit y avoir une seule colonne
    if not nbCol == 1:
        raise(Sudoku_Error, "Erreur d'observation dans TechChRCcol"\
              "._solve_suite2(), nombre de colonnes invalide.")
    colmiss = listCol[0]
    TEST.display("techchrccol", 3, "_solve_suite2() - Le chiffre {0}"\
                 .format(chiffre) + "n'est pas dans la colonne {0}."\
                 .format(colmiss))
    
    #algorithme : on cherche maintenant dans quelles rangs du même carré
    #le chiffre n'est pas
    obsPattern = (gridview.OBS_ROWSBYSQR_NOTCONTAIN, (isqr, chiffre))
    r = ("observe", obsPattern)
    #mémoriser les informations pour l'itération suivante
    mem.memorize("techchrccol_obspattern", obsPattern, self)
    mem.memorize("techchrccol_colmiss", colmiss, self)
    #incrémenter l'index d'observations
    mem.increment("techchrccol_indexobs", self)
    #avancement de la technique et fonction pour l'opération suivante
    mem.memorize("techchrccol_result", "observe", self)
    mem.memorize("techchrccol_stepcol", 3, self)
    mem.memorize("techchrccol_action_suivante", self._solve_suite3, self)
    mem.memorize("techchrccol_nom_action", "suite 3", self)
    #retourner en indiquant la demande d'observation à faire
    TEST.display("techchrccol", 3, "_solve_suite2() : demande de 3ème "\
                 "observation : pattern = {0}".format(obsPattern))
    r = ("observe", obsPattern)
    return r

def _solve_suite3(self):
    '''Résolution pour une colonne (Col) - Retour 3ème observation = les
    rangs du carré où le chiffre n'est pas. Il y en a forcément au moins
    un (puisqu'il y a un chiffre à mettre dans ce carré.
    4ème observation à faire = les cases vides à l'intersection des rangs et
    de la colonne sans le chiffre.
    La seule cause possible d'échec est un fail mémoire.
    '''
    TEST.display("techchrccol", 3, "TechChRCcol - dans _solve_suite3()")
    assert self._initOk
    mem = self._mem
    #se rappeler les infos en mémoire de l'étape précédente
    chiffre = mem.recall("techchrccol_chiffre", self)
    icol = mem.recall("techchrccol_icol", self)
    isqr = mem.recall("techchrccol_isqr", self)
    colmiss = mem.recall("techchrccol_colmiss", self)
    TEST.display("techchrccol", 3, "_solve_suite3() - Colonne de carrés "\
                 "n° {0} : retour 3ème observation".format(icol))
    #récupérer le résultat de l'observation et l'analyser
    #c'est un tuple de nombre et liste de rangs
    found = mem.recall("techchrccol_obsfound", self)
    (nbRow, listRow) = found
    TEST.display("techchrccol", 3, "_solve_suite3() - Le chiffre {0}"\
                 .format(chiffre) + "est absent des {0} rang(s) : {1}."\
                 .format(nbRow, listRow))
    
    #algorithme : on cherche maintenant les cases vides à l'intersection
    #des rangs et de la colonne libres
    argRowCol =(listRow, (colmiss,))
    obsPattern = (gridview.OBS_EMPTYPLACES_RC, argRowCol)
    #mémoriser les informations pour l'itération suivante
    mem.memorize("techchrccol_rowsmiss", listRow, self)
    mem.memorize("techchrccol_obspattern", obsPattern, self)
    #incrémenter l'index d'observations
    mem.increment("techchrccol_indexobs", self)
    #avancement de la technique et fonction pour l'opération suivante
    mem.memorize("techchrccol_result", "observe", self)
    mem.memorize("techchrccol_stepcol", 4, self)
    mem.memorize("techchrccol_action_suivante", self._solve_suite4, self)
    mem.memorize("techchrccol_nom_action", "suite 4", self)
    #retourner en indiquant la demande d'observation à faire
    TEST.display("techchrccol", 3, "_solve_suite3() - Demande 4ème "\
                 "observation : pattern = {0}".format(obsPattern))
    r = ("observe", obsPattern)
    return r

def _solve_suite4(self):
    '''Résolution pour une colonne (Col) - Retour 4ème observation = les
    cases vides à l'intersection des lignes et colonnes disponibles.
    S'il y en a une seule, faire le placement. S'il y en a plusieurs, on
    considère que d'est trop complexe -> fin de la technique
    La seule cause possible d'échec est un fail mémoire.
    '''
    TEST.display("techchrccol", 3, "TechChRCcol - dans _solve_suite4()")
    assert self._initOk
    mem = self._mem
    #se rappeler les infos en mémoire de l'étape précédente
    chiffre = mem.recall("techchrccol_chiffre", self)
    icol = mem.recall("techchrccol_icol", self)
    isqr = mem.recall("techchrccol_isqr", self)
    colmiss = mem.recall("techchrccol_colmiss", self)
    colsmiss = mem.recall("techchrccol_colsmiss", self)
    TEST.display("techchrccol", 3, "_solve_suite4() - Colonne de carrés "\
                 "n° {0} : retour 4ème observation".format(icol))
    #récupérer le résultat de l'observation et l'analyser.
    #c'est un tuple de nombre et liste de cases
    found = mem.recall("techchrccol_obsfound", self)
    (nbPlc, listPlc) = found
    TEST.display("techchrccol", 3, "_solve_suite4() - Les cases {0}"\
                 .format(listPlc) + "sont disponibles pour placer le {0}."\
                 .format(chiffre))
    #algorithme : il doit y a au moins une case libre, s'il y a une seule
    #c'est celle ou se fait le placement
    if nbPlc < 1:
        raise(Sudoku_Error, "Erreur d'observation dans TechChRCcol"\
              "._solve_suite4(), nombre de cases libres invalide.")
    #s'il y en a plus d'une, trop complexe pour le moment -> abandon
    elif nbPlc > 1:
        TEST.display("techchrccol", 3, "_solve_suite4() - Plus d'1 case à "\
                     "remplir, trop complexe. La technique locale est "\
                     "abandonnée.")
        r = self._solve_fin("quit")
    # ok 1 case, on fait le placement
    else:
        placement = (listPlc[0][0], listPlc[0][1], chiffre)
        #mémoriser les informations pour l'itération suivante
        mem.memorize("techchrccol_availplc", listPlc, self)
        mem.memorize("techchrccol_result", "place", self)
        mem.memorize("techchrccol_placement", placement, self)
        #avancement de la technique et fonction pour l'opération suivante
        mem.memorize("techchrccol_stepcol", 5, self)
        mem.memorize("techchrccol_action_suivante", self._solve_suite5, self)
        mem.memorize("techchrccol_nom_action", "suite 5", self)
        #retourner en indiquant la demande de placement à faire
        TEST.display("techchrccol", 3, "_solve_suite4() - Demande de "\
                     "placement de {0} en {1}".format(chiffre, listPlc[0]))
        r = ("place", placement)
    return r

def _solve_suite5(self):
    '''Résolution pour une colonne (Col) - Retour de placement.
    Vérifier que le placement a été correct et terminer la technique.
    '''
    TEST.display("techchrccol", 3, "TechChRCcol - dans _solve_suite5()")
    assert self._initOk
    mem = self._mem
    #se rappeler les infos en mémoire de l'étape précédente
    chiffre = mem.recall("techchrccol_chiffre", self)
    placement = mem.recall("techchrccol_placement", self)
    nbplc = mem.recall("techchrccol_nbplccol", self)
    #vérifier que le placement a été bien réalisé. Sinon c'est une erreur
    #de mémoire, d'algorithme ou de cohérence de la grille.
    plcValid = mem.recall("techchrccol_placeok", self)
    if plcValid is not True:
        raise Sudoku_Error ("Erreur de placement dans TechChRCcol"\
              "._solve_suite5(), le placement a échoué.")
    #incrémenter le compteur de placement puis passer à la fin
    mem.increment("techchrccol_nbplccol", 1, self)
    (row, col) = (placement[0], placement[1])
    TEST.display("techchrccol", 3, "_solve_suite5() - Le placement "\
                 "de {0} en {1} est validé.".format(chiffre, (row, col)))
    #fin de la technique avec succès
    r = self._solve_fin("succeed")
    return r

def _solve_fin(self, endResult="end"):
    """A la fin des étapes de résolution, commande la fin de la technique
    et construit la réponse à retourner à apply() - et donc à la fonction
    appelante du programme.
    """
    TEST.display("techchrccol", 3, "TechChRCcol - dans _solve_fin()")
    assert self._initOk
    mem = self._mem
    nbplccol = mem.recall("techchrccol_nbplccol", self)
    TEST.display("techchrccol", 2, \
                 "Fin de la technique \"Chiffre-rang-colonne\" sur une "\
                 "colonne.\nNombre de chiffres placés : {0}" \
                 .format(nbplccol))
    #mettre à jour les données d'avancement
    self._finish_apply()
    #construire le tuple de détail de résultats
    endDetails = (endResult, nbplccol)
    TEST.display("techlplccol", 2, "La technique se termine avec le "\
                 "résultat : '{0}'".format(endDetails))
    #retour à SudoThinking
    return ("end", endDetails)

def _finish_apply(self):
    '''Marque la technique comme terminée. Il faudra appeler 'reset()'
    pour la relancer.
    '''
    TEST.display("techchrccol", 3, "TechChRCcol - dans _finish_tech()")
    assert self._initOk
    mem = self._mem
    mem.memorize("techchrccol_chiffre", None, self)
    mem.memorize("techchrccol_icol", None, self)
    mem.memorize("techchrccol_isqcol", None, self)
    mem.memorize("techchrccol_finished", True, self)
    mem.memorize("techchrccol_encours", False, self)
    self._finished = True
    return 
