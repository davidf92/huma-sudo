'''SudoSimu - Module techlplcg - technique de résolution "dernier placement"
globale sur la grille.

Script d'import dans techlplcg.py de fonctions et méthodes privées de la classe
SudoTechLastPlcGrid. Il s'agit des fonctions qui gèrent les états d'avancement
d'application de la technique globale, en particulier les instanciations
successives des techniques locales.
 
change.log
----------
11/10/2017
Réalisation du split entre techlplcg.py et ce fichier.
Suppression des paramètres 'mem' inutiles dans toutes les méthodes

'''

if __name__ in ("__main__", "techlplcg", "techlplc.techlplcg2"):
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
elif __name__ == "sudosimu.techlplc.techlplcg2":
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
    raise Exception("Impossible de faire les imports dans le module techlplcg2.")


def _start_apply(self):
    '''Début de la résolution. La première technique locale à appliquer
    va être sur le premier carré.
    '''
    TEST.display("techlplcgrid", 3, "TechLastPlcGrid - dans _start_apply()")
    assert self._initOk
    mem = self._mem
    #Instancier la technique de résolution locale pour le carré 1
    try:
        tech = TechLastPlcSqr(mem, (1,))
    except:
        ui.DisplayError("Erreur", "Impossible de lancer une technique de"+
                                 "résolution TechLastPlcSqr.")
        raise Sudoku_Error("TechLastPlcGrid - erreur instanciation tech sqr")
    #mémorise les données pour la suite de la technique
    mem.memorize("techlplcgrid_techclass", TechLastPlcSqr, self)
    mem.memorize("techlplcgrid_techloc", tech, self)
    mem.memorize("techlplcgrid_rcs", "sqr", self)
    mem.memorize("techlplcgrid_ibloc", 1, self)
    mem.memorize("techlplcgrid_encours", True, self)
    self._encours = True
    #appliquer la technique locale
    r = self._apply_techloc()
    return r

def _apply_techloc(self):
    '''Transmet l'exécution à la technique locale en cours d'application.'''
    TEST.display("techlplcgrid", 3, "TechLastPlcGrid - dans _apply_techloc()")
    assert self._initOk
    assert self._encours
    mem = self._mem
    #applique la technique locale en cours
    tech = mem.recall("techlplcgrid_techloc", self)
    if self._resume is True:
        TEST.display("techlplcgrid", 3, "appelle de resume() de la "+\
                     "technique locale {0}".format(tech.techName()))
        r = tech.resume()
    else:
        TEST.display("techlplcgrid", 3, "appelle de apply() de la "+\
                     "technique locale {0}".format(tech.techName()))
        r = tech.apply()
    #si la technique locale est terminée, passe à la suivante pour la
    #prochaine itération
    if r[0] == "end":
        TEST.display("techlplcgrid", 3, "TechLastPlcGrid : la technique "+\
                     "{0} a retourné \"end\".".format(tech.techName()))
        endDetails = r[1]
        r = self._techloc_end(endDetails)
    #si la technique locale s'est interrompue, passer quand même à la
    #suivante
    elif r[0] == "fail":
        TEST.display("techlplcgrid", 3, "TechLastPlcGrid : la technique "+\
                     "{0} a retourné \"fail\".".format(tech.techName()))
        failDetails = r[1]
        r = self._techloc_fail(failDetails)
        
    #ok    
    return r

def _techloc_end(self, endDetails):
    '''Traite la situation où la technique locale en cours a retourné
    "end".
    '''
    TEST.display("techlplcgrid", 3, "TechLastPlcGrid - dans _techloc_end()")
    assert self._initOk
    assert self._encours
    mem = self._mem
    #récupère le nombre de placements, transmis avec le "end"
    #exemple : ("end", ("succeed", 1))
    nbplc = endDetails[1]
    mem.increment("techlplcgrid_nbplctot", nbplc, self)
    #passe à la technique locale suivante
    TEST.display("techlplcgrid", 3, "Passage à la technique locale suivante")
    r = self._next_techloc()
    return r


def _techloc_fail(self, endDetails):
    '''Traite la situation où la technique locale en cours a retourné
    "fail".
    '''
    TEST.display("techlplcgrid", 3, "TechLastPlcGrid - dans _techloc_fail()")
    assert self._initOk
    assert self._encours
    mem = self._mem

    ### Dans la version actuelle, "fail" ne transmet pas de nombre de
    ### placements déjà effectués avant l'échec

    #passe à la technique locale suivante
    TEST.display("techlplcgrid", 3, "Passage à la technique locale suivante")
    r = self._next_techloc()
    return r

def _next_techloc(self):
    '''Prépare la technique locale suivante quand celle en cours a
    retourné "end". Enchaîne les techniques row/col/sqr puis appelle
    la fin de technique globale après la 9° itération sur les carrés.
    '''
    TEST.display("techlplcgrid", 3, "TechLastPlcGrid - dans _next_techloc()")
    assert self._initOk
    assert self._encours
    mem = self._mem
    #se rappeler l'indice de bloc et le type de bloc
    ibloc = mem.recall("techlplcgrid_ibloc", self)
    techClass = mem.recall("techlplcgrid_techclass", self)
    #continuer jusqu'au 9° bloc du type sqr/row/col en cours
    if 1 <= ibloc <= 8:
        ibloc +=1
        TEST.display("techlplcgrid", 3, "La prochaine technique sera "\
                     "sur le bloc n°{0}".format(ibloc))
        tech = techClass(mem, (ibloc,))
        mem.memorize("techlplcgrid_techloc", tech, self)
        mem.memorize("techlplcgrid_ibloc", ibloc,self)
        r = ("continue", None)
    #après le 9° bloc passer au type row/col/sqr suivant ou terminer
    elif ibloc == 9:
        TEST.display("techlplcgrid", 2,
                     "Fin de la série de technique locale.")
        #si ce sont les carrés qui sont terminés, passer aux rangs
        if techClass is TechLastPlcSqr:
            TEST.display("techlplcgrid", 2, "Fin de la répétition sur " \
                            "les carrés - Passage aux rangs")
            tech = TechLastPlcRow(mem, (1,))
            mem.memorize("techlplcgrid_techloc", tech, self)
            mem.memorize("techlplcgrid_rcs", "row", self)
            mem.memorize("techlplcgrid_techclass", TechLastPlcRow, self)
            mem.memorize("techlplcgrid_ibloc", 1, self)
            r = ("continue", None)
            
        #si ce sont les rangs qui sont terminés, passer aux colonnes
        elif techClass is TechLastPlcRow:
            TEST.display("techlplcgrid", 2, "Fin de la répétition sur " \
                            "les rangs - Passage aux colonnes")
            tech = TechLastPlcCol(mem, (1,))
            mem.memorize("techlplcgrid_techloc", tech, self)
            mem.memorize("techlplcgrid_rcs", "col", self)
            mem.memorize("techlplcgrid_techclass", TechLastPlcCol, self)
            mem.memorize("techlplcgrid_ibloc", 1, self)
            r = ("continue", None)

        #si ce sont les colonnes qui sont terminées, fin de la technique
        elif techClass is TechLastPlcCol:
            TEST.display("techlplcgrid", 2, "Fin de la répétition sur " \
                            "les colonnes - La technique globale est" \
                            "terminée")
            r = self._finish_apply()
        else:
            #ne devrait jamais arriver
            raise Sudoku_Error("TechLastPlcGrid : erreur type de technique.")

    else:
        #ibloc <1 ou >9 ne devrait jamais arriver
        raise Sudoku_Error("TechLastPlcGrid : erreur indice de bloc.")

    return r

def _finish_apply(self):
    '''Termine l'application de cette technique globale après que toutes
    les techniques locales ont été exécutées.
    '''
    TEST.display("techlplcgrid", 3, "TechLastPlcGrid - dans _end_tech()")
    assert self._initOk
    assert self._encours
    #nombre de placements faits
    totplc = self._mem.recall("techlplcgrid_nbplctot", self)
    TEST.display("techlplcgrid", 1, "Technique LastPlcGrid : {0} " \
                                     "placements faits.".format(totplc))
    #nettoyage de la mémoire
    self._clear_tech_mem()
    self._finished = True
    #retourner à AI le nombre de placements faits
    return ("end", ("succeed", totplc))
    
            
