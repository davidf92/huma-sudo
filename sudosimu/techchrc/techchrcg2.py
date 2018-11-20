'''SudoSimu - Module techchrcg - technique de résolution "chiffre/rang-colonne"
globale sur la grille entière pour un chiffre donné.
Script d'import dans techchrcg.py de fonctions privées de la classe
TechChRCgrid. Il s'agit des fonctions qui gèrent les états d'avancement
d'application de la technique globale, en particulier instanciations successives
des techniques locales.

Dernière mise à jour : 11/10/2017
Vérification de complétude des modifications -suppr-mem- et -split-,
parallèlement à la mise à jour de techchrcg.py.
'''


if __name__ in ("__main__", "techchrcg", "techchrc.techchrcg2"):
    #imports des modules de la simulation
    import sudoui as ui
    import sudorules as rules
    from sudorules import Sudoku_Error
    from sudomemory import SudoMemory
    import sudogridview as gridview
    #import des modules de techniques locales de résolution
    from techchrc.techchrcr import TechChRCrow
    from techchrc.techchrcc import TechChRCcol
    #imports pour le code de test et d'affichage de debuggage
    from sudotest import *
elif __name__ == "sudosimu.techchrc.techchrcg2":
    #imports des modules de la simulation
    from sudosimu import sudoui as ui
    from sudosimu import sudorules as rules
    from sudosimu.sudorules import Sudoku_Error
    from sudosimu.sudomemory import SudoMemory
    from sudosimu import sudogridview as gridview
    #import des modules de techniques locales de résolution
    from sudosimu.techchrc.techchrcr import TechChRCrow
    from sudosimu.techchrc.techchrcc import TechChRCcol
    #imports pour le code de test et d'affichage de debuggage
    from sudosimu.sudotest import *
else:
    raise Exception("Impossible de faire les imports dans le module techchrcg2.")


def _start_apply(self):
    '''Début de la résolution. La première technique locale à appliquer
    va être sur le premier carré rang de carrés
    '''
    TEST.display("techchrcgrid", 3, "TechChRCgrid - dans _start_apply()")
    assert self._initOk
    mem = self._mem
    chiffre = mem.recall("techchrcgrid_chiffre", self)
    #Instancier la technique de résolution locale pour le premier rang
    #de carrés
    try:
        techloc = TechChRCrow(mem, (chiffre,1))
        TEST.display("techchrgrid", 3, "TechChRCgrid - retour à "\
                                         "_start_apply()")
    except:
        ui.DisplayError("Erreur", "Impossible de lancer une technique de"+
                                 "résolution TechChRCrow.")
        raise Sudoku_Error("TechChRCgrid - erreur instanciation tech sqr")
    #mémorise les données pour la suite de la technique
    mem.memorize("techchrcgrid_rcs", "row", self)
    mem.memorize("techchrcgrid_isqrow", 1, self)
    mem.memorize("techchrcgrid_techclass", TechChRCrow, self)
    mem.memorize("techchrcgrid_techloc", techloc, self)
    mem.memorize("techchrcgrid_techlocname", "TechChRCrow", self)
    mem.memorize("techchrcgrid_encours", True, self)
    self._encours = True
    #appliquer la technique locale
    r = self._apply_techloc()
    TEST.display("techchrgrid", 3, "TechChRCgrid - retour à _start_apply()")
    return r

def _apply_techloc(self):
    '''Transmet l'exécution à la technique locale en cours d'application.
    La technique locale sera appelée avec sa méthode apply() ou resume()
    suivant l'appel qui a été utilisé pour la technique globale.
    '''
    TEST.display("techchrcgrid", 3, "TechChRCgrid - dans _apply_techloc()")
    assert self._initOk
    assert self._encours
    mem = self._mem
    #applique la technique locale en cours
    techloc = mem.recall("techchrcgrid_techloc", self)
    if self._resume is True:
        TEST.display("techchrcgrid", 3, "appelle de resume() de la technique "\
                     "locale {0}".format(techloc.techName()))
        r = techloc.resume()
        TEST.display("techchrgrid", 3, "TechChRCgrid - retour à "\
                                             "_apply_techloc()")
    else:
        TEST.display("techchrcgrid", 3, "appelle de apply() de la technique "\
                     "locale {0}".format(techloc.techName()))
        r = techloc.apply()
        TEST.display("techchrgrid", 3, "TechChRCgrid - retour à "\
                                             "_apply_techloc()")
    #si la technique locale est terminée, passe à la suivante pour la
    #prochaine itération
    if r[0] == "end":
        TEST.display("techchrcgrid", 3, "TechChRCgrid : la technique "\
                     "{0} a retourné \"end\" avec {1}."\
                     .format(techloc.techName(), r[1]))
        endDetails = r[1]
        r = self._techloc_end(endDetails)
        TEST.display("techchrgrid", 3, "TechChRCgrid - retour à "\
                                             "_apply_techloc()")
    #si la technique locale s'est interrompue, passer quand même à la
    #suivante
    elif r[0] == "fail":
        TEST.display("techchrcgrid", 3, "TechChRCGrid : la technique "+\
                     "{0} a retourné \"fail\".".format(tech.techName()))
        failDetails = r[1]
        r = self._techloc_fail(failDetails)
        
    #ok    
    return r

def _techloc_end(self, endDetails):
    '''Traite la situation où la technique locale en cours a retourné
    "end". Incrémente le compteur total de placements.
    '''
    TEST.display("techchrcgrid", 3, "TechChRCgrid - dans _techloc_end()")
    assert self._initOk
    assert self._encours
    #récupère le nombre de placements, transmis avec le "end" de la technique
    #locale, et incrémente le total de placements de la technique globale
    (endtype, nbplc) = endDetails
    self._mem.increment("techchrcgrid_nbplctot", nbplc, self)
    #passe à la technique locale suivante
    r = self._next_techloc()
    TEST.display("techchrcgrid", 3, "TechChRCgrid - retour à _techloc_end()")
    return r

def _techloc_fail(self, endDetails):
    '''Traite la situation où la technique locale en cours a retourné
    "fail".
    '''
    TEST.display("techchrcgrid", 3, "TechChRCgrid - dans _techloc_fail()")
    assert self._initOk
    assert self._encours
    mem = self._mem

    ### Dans la version actuelle, "fail" ne transmet pas de nombre de
    ### placements déjà effectués avant l'échec

    #passe à la technique locale suivante
    TEST.display("techchrcgrid", 3, "Passage à la technique locale suivante")
    r = self._next_techloc()
    return r

def _next_techloc(self):
    '''Passe à la technique locale suivante et instancie cette technique.
    Enchaîne les techniques locales Ch/RC sur les 3 rangs puis sur les
    3 colonnes de carrés.
    '''
    TEST.display("techchrcgrid", 3, "TechChRCgrid - dans _next_techloc()")
    assert self._initOk
    assert self._encours
    mem = self._mem
    #se rappeler les données de la résolution en cours
    chiffre = mem.recall("techchrcgrid_chiffre", self)
    rcs = mem.recall("techchrcgrid_rcs", self)
    techClass = mem.recall("techchrcgrid_techclass", self)
    #créer l'instance de la technique suivante
    #si l'étape de résolution en cours est sur les rangs de carrés
    if rcs == "row":
        isqrow = mem.recall("techchrcgrid_isqrow", self)
        if isqrow in (1,4):
            #passage au rang de carrés suivant
            isqrow += 3
            TEST.display("techchrcgrid", 2, "TechChRCgrid - Suite de la "\
                         "résolution. Application au rang de carrés {0}."\
                         .format(isqrow))
            TEST.display("techchrcgrid", 3, "TechChRCgrid - Nouvelle "\
                         "instance de TechChRCrow.")
            try:
                techloc = TechChRCrow(mem, (chiffre, isqrow))
                TEST.display("techchrgrid", 3, "TechChRCgrid - retour à "\
                                                 "_next_techloc()")
                mem.memorize("techchrcgrid_isqrow", isqrow, self)
                mem.memorize("techchrcgrid_techloc", techloc, self)
                r = ("continue", None)
            except:
                TEST.display("techchrcgrid", 1, "Erreur dans _next_techloc()"\
                        " : échec d'instanciation de TechChRCrow pour "\
                        "chiffre = {0} et irow = {1}".format(chiffre, irow))
                r = ("end",
                     ("fail",
                      "Erreur d'exécution de la technique TechChRCgrid"))
                raise Sudoku_Error("TechChRCgrid - Erreur dans "\
                                   "_next_techloc()")
        elif isqrow == 7:
            #passage à la première colonne de carrés
            TEST.display("techchrcgrid", 2, "TechChRCgrid - Suite de la "\
                         "résolution. Application à la première "\
                         "colonne de carrés.")
            try:
                techloc = TechChRCcol(mem, (chiffre, 1))
                TEST.display("techchrgrid", 3, "TechChRCgrid - retour à "
                                             "_next_techloc()")
                mem.memorize("techchrcgrid_isqcol", 1, self)
                mem.memorize("techchrcgrid_rcs", "col", self)
                mem.memorize("techchrcgrid_techloc", techloc, self)
                mem.memorize("techchrcgrid_techlocname", "TechChRCcol", self)
                mem.memorize("techchrcgrid_techclass", TechChRCcol, self)
                r = ("continue", None)
            except:
                TEST.display("techchrcgrid", 1, "Erreur dans _next_techloc()"\
                        " : échec d'instanciation de TechChRCcol pour "\
                        "chiffre = {0} et icol = 1".format(chiffre))
                r = ("end",
                     ("fail",
                      "Erreur d'exécution de la technique TechChRCgrid"))
                raise Sudoku_Error("TechChRCgrid - Erreur dans "\
                                   "_next_techloc()")
        else:
            #indice invalide, ne devrait jamais arriver
            TEST.display("techchrcgrid", 1, "Erreur dans _next_techloc() : "\
                         "valeur de 'isqcol' invalide.")
            r = ("end",
                 ("fail",
                  "Erreur d'exécution de la technique TechChRCgrid"))
            raise Sudoku_Error("TechChRCgrid._next_techloc() : valeur "\
                               "de 'isqrow' invalide.")
    #si l'étape de résolution en cours est sur les colonnes de carrés
    elif rcs == "col":
        isqcol = mem.recall("techchrcgrid_isqcol", self)
        if isqcol in (1,4):
            #passage à la colonne de carrés suivant
            isqcol += 3
            TEST.display("techchrcgrid", 2, "TechChRCgrid - Suite de la "\
                         "résolution. Application à la colonne de carrés "\
                         "{0}.".format(isqcol))
            TEST.display("techchrcgrid", 3, "TechChRCgrid - Nouvelle "\
                         "instance de TechChRCcol.")
            try:
                techloc = TechChRCcol(mem, (chiffre, isqcol))
                TEST.display("techchrgrid", 3, "TechChRCgrid - retour à "\
                                                 "_next_techloc()")
                mem.memorize("techchrcgrid_isqcol", isqcol, self)
                mem.memorize("techchrcgrid_techloc", techloc, self)
                r = ("continue", None)
            except:
                r = ("end",
                     ("fail",
                      "Erreur d'exécution de la technique TechChRCgrid"))
                TEST.display("techchrcgrid", 1, "Erreur dans _next_techloc()"\
                        " : échec d'instanciation de TechChRCcol pour "\
                        "chiffre = {0} et icol = {1}".format(chiffre, icol))
                raise Sudoku_Error("TechChRCgrid - Erreur dans "\
                                   "_next_techloc()")
        elif isqcol == 7:
            #rangs et colonne terminés, fin de la technique globale
            TEST.display("techchrcgrid", 1, "Fin de la résolution. "\
                         "Toute la grille a été traitée pour le "
                         "chiffre {0}.".format(chiffre))
            r = self._finish_apply()
        else:
            #indice invalide, ne devrait jamais arriver
            TEST.display("techchrcgrid", 1, "Erreur dans _next_techloc() : "\
                         "valeur de 'isqcol' invalide.")
            r = ("end",
                 ("fail",
                  "Erreur d'exécution de la technique TechChRCgrid"))
            raise Sudoku_Error("TechChRCgrid._next_techloc() : valeur "\
                               "de 'isqcol' invalide.")
    else:
        #'rcs' invalide, ne devrait jamais arriver
        TEST.display("techchrcgrid", 1, "Erreur dans _next_techloc() : "\
                     "valeur de 'rcs' invalide.")
        r = ("end",
             ("fail",
              "Erreur d'exécution de la technique TechChRCgrid"))
        raise Sudoku_Error("TechChRCgrid._next_techloc() : valeur "\
                               "de 'rcs' invalide.")

    return r

def _newLocalTechInst(self, techClass, args):
    '''Crée une instance de la technique de résolution locale indiquée.
    Gère l'exception en cas d'échec. Retourne l'instance ou None
    '''
    TEST.display("techchrcgrid", 3, "TechChRCgrid - dans "\
                                     "_newLocalTechInst()")
    assert self._initOk
    assert self._encours
    TEST.display("techchrcgrid", 3, "nouvelle instance de la classe "\
                 "{0} avec les arguments {1}".format(techClass, args))
    try:
        techloc = techClass(self._mem, args)
        TEST.display("techchrgrid", 3, "TechChRCgrid - retour à "\
                            "_newLocalTechInst()")
        return techloc
    except:
        TEST.display("techchrgrid", 3, "TechChRCgrid - retour à "\
                            "_newLocalTechInst()")
        failTxt = "TechChRCgrid - FAIL dans _newLocalTechInst()\n"\
                            "Impossible d'instancier la technique {0}."\
                            .format(techClass)
        #exception suivant le niveau de test
        TEST.raiseArgs("techchrcgrid", 1, Sudoku_Error, failTxt)
        #si l'exception est gérée, message d'erreur
        TEST.displayError("techchrcgrid", 1, failTxt)
        return None
    
def _finish_apply(self):
    '''Termine l'application de cette technique globale après que toutes
    les techniques locales ont été exécutées et retourne le résultat
    global.
    '''
    TEST.display("techchrcgrid", 3, "TechChRCgrid - dans _finish_apply()")
    assert self._initOk
    assert self._encours
    #nombre de placements faits
    totplc = self._mem.recall("techchrcgrid_nbplctot", self)
    TEST.display("techchrcgrid", 1, "Technique TechChRCgrid : {0} " \
                                     "placements fait(s).".format(totplc))
    self._finished = True
    self._encours = False
    #fait la réponse qui correspond au résultat des placements
    if totplc == 0:
        endDetails = ("noplace", 0)
    elif totplc >0:
        endDetails = ("succeed", totplc)
    else:
        r = ("end",
             ("fail", "Erreur d'exécution de la technique TechChRCgrid"))
        raise Sudoku_Error("TechChRCgrid._finish_apply() : valeur de "\
                           "totplc invalide.")
    #retourner "end" avec les détails
    return ("end", endDetails)

