'''SudoSimu - Module techchrcga - technique de résolution "chiffre/rang-colonne"
globale sur la grille entière pour tous les chiffres.

Script d'import dans techchrcga.py de fonctions privées de la classe
TechChRCgridAll. Il s'agit des fonctions qui gèrent les états d'avancement
d'application de la technique globale, en particulier instanciations successives
des techniques locales.

Dernière mise à jour : 11/10/2017
Vérification de complétude des modifications -suppr-mem- et -split-,
parallèlement à la mise à jour de techchrcga.py.
'''


if __name__ in ("__main__", "techchrcga", "techchrc.techchrcga2"):
    #imports des modules de la simulation
    import sudoui as ui
    import sudorules as rules
    from sudorules import Sudoku_Error
    from sudomemory import SudoMemory
    import sudogridview as gridview
    from sudotest import *
    #import des modules de techniques locales de résolution
    from techchrc.techchrcg import TechChRCgrid
elif __name__ == "sudosimu.techchrc.techchrcga2":
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
    raise Exception("Impossible de faire les imports dans le module techchrcga2.")


def _start_apply(self):
    '''Début de la résolution. La première technique locale à appliquer
    va être sur la grille pour chiffre = 1
    '''
    TEST.display("techchrcgridall", 3, "TechChRCgridAll - dans _start_apply()")
    assert self._initOk
    assert self._encours
    mem = self._mem
    #Instancier la technique de résolution locale pour le chiffre 1
    TEST.display("techchrcgridall", 2, "Début de la résolution. "\
                 "Placement des chiffres 1.")
    techloc = self._newGridTechInst(1)
    if techloc is None:
        #l'instanciation n'a pas réussi, retourner "fail"
        mem.memorize("techchrccol_encours", False, self)
        mem.memorize("techchrccol_finished", True, self)
        self._finished = True
        self._encours = False
        return ("end", ("fail",
                    "Erreur d'exécution de la technique TechChRCgridAll :"\
                    "impossible de créer une instance de TechChRCgrid."))
    #ok, appliquer la nouvelle instance
    #mémorise les données pour la suite de la technique
    mem.memorize("techchrcgridall_chiffre", 1, self)
    mem.memorize("techchrcgridall_techclass", TechChRCgrid, self)
    mem.memorize("techchrcgridall_techloc", techloc, self)
    mem.memorize("techchrcgridall_techlocname", techloc.techName(), self)
    self._encours = True
    #appliquer la technique locale
    r = self._apply_techloc()
    TEST.display("techchrgridall", 3, "TechChRCgridAll - retour à _start_apply()")
    return r

def _apply_techloc(self):
    '''Transmet l'exécution à la technique locale en cours d'application.
    La technique locale sera appelée avec sa méthode apply() ou resume()
    suivant l'appel qui a été utilisé pour la technique globale.
    '''
    TEST.display("techchrcgridall", 3, "TechChRCgridAll - dans "\
                                         "_apply_techloc()")
    assert self._initOk
    assert self._encours
    mem = self._mem
    #applique la technique locale en cours
    techloc = mem.recall("techchrcgridall_techloc", self)
    techlocName = mem.recall("techchrcgridall_techlocname", self)
    try:
        if self._resume is True:
            TEST.display("techchrcgridall", 3, "appel de resume() de la technique "\
                         "locale {0}".format(techlocName))
            TEST.display("techchrcgridall", 3, "appel de {0}".format(techloc.resume))
            r = techloc.resume()
            TEST.display("techchrgridall", 3, "TechChRCgridAll - retour à "\
                                                 "_apply_techloc()")
        else:
            TEST.display("techchrcgridall", 3, "appel de apply() de la technique "\
                         "locale {0}".format(techlocName))
            TEST.display("techchrcgridall", 3, "appel de {0}".format(techloc.apply))
            r = techloc.apply()
            TEST.display("techchrgridall", 3, "TechChRCgridAll - retour à "\
                                                 "_apply_techloc()")
        #en plus d'une exception de apply() ou resume(), gérer un retour
        #invalide
        if not r[0] in ("continue", "observe", "place", "end", "fail"):
            raise Sudoku_Error()
    except:
        #Erreur dans l'application de la technique locale
        failTxt = "TechChRCgridAll - FAIL dans _apply_techloc()\n"\
            "Impossible d'appliquer la technique {0}. La technique "\
            "de résolution TechChRCgridAll est abandonnée."\
            .format(techlocName)
        TEST.raiseArgs("techchrcgrid", 1, Sudoku_Error, failTxt)
        self._encours = False
        self._finished = True
        return ("end", ("fail", "Erreur d'exécution de la technique "\
                             "TechChRCgridAll."))
    #si la technique locale est terminée, gérer sa fin et l'exploitation
    #des données de fin et éventuellement le passage à la technique locale
    #suivante.
    if r[0] == "end":
        TEST.display("techchrcgridall", 3, "TechChRCgridAll : la technique "\
                     "{0} a retourné \"end\".".format(techlocName))
        endDetails = r[1]
        r = self._techloc_end(endDetails)
    #ok    
    return r

def _techloc_end(self, endDetails):
    '''Traite la fin de la technique locale. Récupère le nombre de
    placements faits et passe à la technique suivante.
    '''
    TEST.display("techchrcgridall", 3, "TechChRCgridAll - dans _techloc_end()")
    assert self._initOk
    assert self._encours
    #récupère le nombre de placements, transmis avec le "end" de la technique
    #locale, et incrémente le total de placements de la technique globale
    (endtype, nbplc) = endDetails
    self._mem.increment("techchrcgridall_nbplctot", nbplc, self)
    #passe à la technique locale suivante
    TEST.display("techchrcgridall", 3, "Passage à la technique locale suivante")
    r = self._next_techloc()
    TEST.display("techchrgridall", 3, "TechChRCgridAll - retour à "\
                                         "_techloc_end()")
    return r
                 
def _next_techloc(self):
    '''Passe à la technique locale suivante et instancie cette technique.
    Après le dernier passage sur le chiffre 9, appelle la fin de la
    technique globale.
    '''
    TEST.display("techchrcgridall", 3, "TechChRCgridAll - dans _next_techloc()")
    assert self._initOk
    assert self._encours
    mem = self._mem
    #se rappeler les données de la résolution en cours
    chiffre = mem.recall("techchrcgridall_chiffre", self)
    
    #créer l'instance de la technique suivante
    #enchaîner Ch/RC à l'identique pour les chiffres 1 à 8 => 2 à 9
    if 1 <= chiffre <= 8:
        
        chiffre += 1
        TEST.display("techchrcgridall", 2, "Suite de la résolution. "\
                     "Placement des chiffres {0}.".format(chiffre))
        TEST.display("techchrcgridall", 3, "TechChRCgridAll, - "\
                     "Nouvelle instance de TechChRCgrid.")
        techloc = self._newGridTechInst(chiffre)
        if techloc is None:
            #l'instanciation n'a pas réussi, retourner "fail"
            mem.memorize("techchrccol_encours", False, self)
            mem.memorize("techchrccol_finished", True, self)
            self._finished = True
            return ("end", ("fail",
                    "Erreur d'exécution de la technique TechChRCgridAll :"\
                    "impossible de créer une nouvelle instance de "\
                    "TechChRCgrid pour le chiffre {0}.".format(chiffre)))
        #ok instanciation réussie
        TEST.display("techchrgridall", 3, "TechChRCgridAll - retour à "\
                                         "_next_techloc()")
        mem.memorize("techchrcgridall_techloc", techloc, self)
        mem.increment("techchrcgridall_chiffre", 1, self)
        r = ("continue", None)

    #après la technique locale sur le chiffre 9, c'est terminé
    else:
        TEST.display("techchrcgridall", 1, "TechChRCgridAll - Fin des "\
                     "techniques locales,toute la grille a été traitée "\
                     "pour tous les chiffres.")
        r = self._finish_apply()

    return r

def _newGridTechInst(self, chiffre):
    '''Crée une instance de la technique de résolution locale 'grid' pour
    le chiffre indiqué.
    Gère l'exception en cas d'échec. Retourne l'instance ou None
    '''
    TEST.display("techchrcgridall", 3, "TechChRCgridAll - dans "\
                                     "_newGridTechInst()")
    assert self._initOk
    assert self._encours
    TEST.display("techchrcgridall", 3, "nouvelle instance de la classe "\
                 "TechChRCgrid pour le chiffre {0}".format(chiffre))
    try:
        techloc = TechChRCgrid(self._mem, (chiffre,))
        TEST.display("techchrgridall", 3, "TechChRCgridAll - retour à "\
                            "_start_instanciateTech()")
        return techloc
    except:
        TEST.display("techchrgridall", 3, "TechChRCgridAll - retour à "\
                            "_start_instanciateTech()")
        failTxt = "TechChRCgridAll - FAIL dans _newGridTechInst()\n"\
            "Impossible d'instancier la technique TechChRCgrid."
        #exception suivant le niveau de test
        TEST.raiseArgs("techchrcgridall", 1, Sudoku_Error, failTxt)
        #si l'exception est gérée, message d'erreur
        TEST.displayError("techchrcgridall", 1, failTxt)
        return None
    
def _finish_apply(self):
    '''Termine l'application de cette technique globale après que toutes
    les techniques locales ont été exécutées et retourne le résultat
    global.
    '''
    TEST.display("techchrcgridall", 3, "TechChRCgridAll - dans _finish_apply()")
    assert self._initOk
    assert self._encours
    #nombre de placements faits
    totplc = self._mem.recall("techchrcgridall_nbplctot", self)
    TEST.display("techchrcgridall", 1, "Technique TechChRCgridAll : {0} " \
                                     "placements fait(s).".format(totplc))
    #fait la réponse qui correspond au résultat des placements
    if totplc == 0:
        endDetails = ("noplace", 0)
    elif totplc >0:
        endDetails = ("succeed", totplc)
    else:
        r = ("end",
             ("fail", "Erreur d'exécution de la technique TechChRCgridAll"))
        raise Sudoku_Error("TechChRCgridAll._finish_apply() : valeur de "\
                           "totplc invalide.")
    self._finished = True
    self._encours = False
    #retourner "end" avec les détails
    return ("end", endDetails)

