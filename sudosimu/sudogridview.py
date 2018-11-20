''' SudoSimu - Module sudogridview - Interface joueur/grille pour l'observation
et les placements de chiffres.

Ce module contient la classe SudoGridView qui représente l'interface avec la
grille pour la partie de Sudoku du joueur. Chaque partie utilise une instance
de SudoGridview.
Les méthodes permettent de faire différentes observations de la grille pour y
rechercher des indices de résolution, et de faire les placements.

Instanciation :
---------------
grview = SudoGridView(grid)
L'argument 'grid' doit être une instance de SudoGrid, sinon une exception est
déclenchée.

Méthodes publiques :
--------------------
   lookup(pattern):         Fait une observation suivant le motif 'pattern'.
   place(row, col, value):  Place un chiffre sur la grille.
   isCompleted():           Retourne 'True' si la grille est terminée

   ... plus les méthodes directes d'observation sans passer par la méthode
   lookup.

change.log
----------
03/05/2017
Le module sudoobserver est renommé sudogridview, la classe SudoObserver
est remplacée par SudoGridView qui fait les placements en plus des observations.
22/01/2017
Méthode lookup : permet de demander une observation avec un
ensemble d'arguments "pattern" via une méthode unique.
Toutes les autres méthodes directes sont doublées d'un stub _lookup<xxx>
'''

if __name__ in ("__main__", "sudogridview"):
    import sudobaseclass as base
    import sudoenv
    import sudoui as ui
    import sudorules as rules
    from sudorules import Sudoku_Error
    from sudogrid import SudoGrid
elif __name__ == "sudosimu.sudogridview":
    from sudosimu import sudobaseclass as base
    from sudosimu import sudoenv
    from sudosimu import sudoui as ui
    from sudosimu import sudorules as rules
    from sudosimu.sudorules import Sudoku_Error
    from sudosimu.sudogrid import SudoGrid
else:
    raise Exception("Impossible de faire les imports dans le module sudogridview.")

##CONSTANTES D'IDENTIFIANTS DES DEMANDES D'OBSERVATION
##----------------------------------------------------
#présence/absence/cases vides dans un rang/col/carré
OBS_ROW_CONTENT = 1
OBS_ROW_MISSING = 2
OBS_ROW_EMPTYPLC = 3
OBS_COL_CONTENT = 4
OBS_COL_MISSING = 5
OBS_COL_EMPTYPLC = 6
OBS_SQR_CONTENT = 7
OBS_SQR_MISSING = 8
OBS_SQR_EMPTYPLC = 9
#présence/absence dans un rang ou une colonne de carrés
OBS_SQRSINSQRROW_CONTAIN = 11
OBS_SQRSINSQRROW_NOTCONTAIN = 12
OBS_SQRSINSQRCOL_CONTAIN = 13
OBS_SQRSINSQRCOL_NOTCONTAIN = 14
#rangs/colonnes passant par carré contenant/ne contenant pas
OBS_ROWSBYSQR_CONTAIN = 15
OBS_ROWSBYSQR_NOTCONTAIN = 16
OBS_COLSBYSQR_CONTAIN = 17
OBS_COLSBYSQR_NOTCONTAIN = 18
#cases vides à l'intersection de listes de rangs et colonnes
OBS_EMPTYPLACES_RC = 19
#nombre de cases vides de la grille / grille terminée
OBS_GRID_NBEMPTYPLACES = 20
OBS_GRID_COMPLETED = 21
#cases vides (liste limitée) de la grille - VOIR NOTE
OBS_GRID_EMPTYPLACES_LIM = 20
OBS_GRID_EMPTYPLACES_MAXLIST = 4 #(peut être adapté au profil mémoire)
#NOTE : Dans un souci de réalisme l'observation d'une liste de cases vides
#est limitée, car il n'est généralement pas possible de mémoriser en une seule
#observation une liste pouvant contenir des dizaines de coordonnées.
#Pour faire cela dans la réalité on fait 'inconsciemment) plusieurs observations.
#La limite est gérée par une constante.
#A l'inverse, compter les cases vides ne pose pas de difficulté quel que soit
#leur nombre.


class SudoGridView(base.SudoBaseClass):
    '''Classe pour la vue de la grille par le joueur, pour l'observer et y
    trouver de l'information, et pour y placer des chiffres.
    '''

    def __init__(self, grid, env=None, testlevel=sudoenv.TEST_VIEWLEVEL):
        '''Initialise l'instance pour la grille indiquée.'''
        #init de la classe racine
        assert isinstance(env, sudoenv.SudoEnv) or env is None
        assert isinstance(testlevel, int) and testlevel>=0 \
                or testlevel is None
        #reprendre un précédente niveau de test s'il existe déjà
        oldlev = env.testLevel("gridview")
        if oldlev is not None and testlevel != oldlev:
            testlevel = oldlev
        base.SudoBaseClass.__init__(self, env=env, \
                                    testlabel="gridview", testlevel=testlevel)
        TEST = self.env.TEST
        TEST.display("gridview", 3, "SudoGridView - Dans __init__() : "\
                                 "Initialisation d'une nouvelle instance.")
        #initialisation de l'instance
        if not isinstance(grid, SudoGrid):
            raise Sudoku_Error("Nouvelle instance de Viewer : la grille est "\
                               "un objet invalide.")
        self._grid = grid
        self._initLookup()
        return

    def _initEnv(self, env, level):
        '''Initialise l'environnement en paramètre, l'UI, et l'intégration
        de la classe dans le système de test de cet environnement.
        Si l'environnement n'est pas spécifié, celui par défaut est utilisé.
        '''
        assert isinstance(env, sudoenv.SudoEnv) or env is None
        assert isinstance(level, int) and level>=0
        #environnement par défaut s'il n'est pas spécifié
        if env is None:
            self._env = sudoenv.SudoEnv()
        else:
            self._env = env
        #Inscription de la classe au système de test de l'environnement
        self._testlevel = level
        self._env.testLabel("gridview", level)
        TEST = self.env.TEST
        TEST.display("gridview", 3, "SudoGame - dans _initEnv() - "\
                     "Environnement correctement initialisé.")
        return True
        
    def _initLookup(self):
        '''Initialise le dictionnaire des méthodes d'observation.'''
        self._lookupDict = {
            OBS_ROW_CONTENT : self._lookupRowContent,
            OBS_ROW_MISSING : self._lookupRowMissing,
            OBS_ROW_EMPTYPLC : self._lookupRowEmptyPlc,
            OBS_COL_CONTENT : self._lookupColContent,
            OBS_COL_MISSING : self._lookupColMissing,
            OBS_COL_EMPTYPLC : self._lookupColEmptyPlc,
            OBS_SQR_CONTENT : self._lookupSqrContent,
            OBS_SQR_MISSING : self._lookupSqrMissing,
            OBS_SQR_EMPTYPLC : self._lookupSqrEmptyPlc,
            OBS_SQRSINSQRROW_CONTAIN : self._lookupSqrsInSqrRowContain,
            OBS_SQRSINSQRROW_NOTCONTAIN :self._lookupSqrsInSqrRowNotContain,
            OBS_SQRSINSQRCOL_CONTAIN : self._lookupSqrsInSqrColContain,
            OBS_SQRSINSQRCOL_NOTCONTAIN : self._lookupSqrsInSqrColNotContain,
            OBS_ROWSBYSQR_CONTAIN : self._lookupRowsBySqrContain,
            OBS_ROWSBYSQR_NOTCONTAIN : self._lookupRowsBySqrNotContain,
            OBS_COLSBYSQR_CONTAIN : self._lookupColsBySqrContain,
            OBS_COLSBYSQR_NOTCONTAIN : self._lookupColsBySqrNotContain,
            OBS_EMPTYPLACES_RC : self._lookupEmptyPlacesRC,
            OBS_GRID_NBEMPTYPLACES : self._lookupGridNbEmptyPlaces,
            OBS_GRID_COMPLETED : self._lookupGridCompleted
            }
        return

    def lookup(self, pattern):
        '''Fait une recherche visuelle dans la grille selon les indications
        données par le tuple 'pattern' qui regroupe tous les arguments.
        Retourne un tuple contenant les valeurs correspondantes.
        '''
        TEST = self.env.TEST
        TEST.display("gridview", 3, "SudoGridView : lookup avec pattern {0}"\
                     .format(pattern))
        #chercher la méthode d'observation demandée
        obsMethod = self._lookupDict[pattern[0]]
        if not obsMethod:       #ne devrait jamais arriver !
            raise Sudoku_Error( \
                " La méthode d'observation demandée n'existe pas.")
        #exécuter la méthode d'observation
        found = obsMethod(self._grid, pattern[1])
        #transférer la valeur retournée = résultat d'observation
        return found

    def place(self, placement):
        '''Place une valeur sur la grille. Retourne 'True' ou 'False' suivant
        que le placement est valide ou non.
        '''
        TEST = self.env.TEST
        (row, col, value) = placement
        TEST.display("gridview", 3, "SudoGridView : placement de {0} "\
                         .format(value) + "en ({0},{1})".format(row,col))
        TEST.display("gridview", 1, "Placement sur la grille du {0} en {1}"\
                     .format(value, (row, col)))
        valid = self._grid.placeRC(row, col, value)
        TEST.display("gridview", 3, "SudoGridView : validité du placement :" \
                                     "{0}".format(valid))
        return valid

    def _lookupRowContent(self, grid, args):
        return self.rowContent(grid, args[0])
    
    def rowContent(self, grid, irow):
        '''Cherche les valeurs contenues dans le rang <row>
        Retourne en tuple le nombre et la liste de valeurs
        '''
        TEST = self.env.TEST
        assert isinstance(grid, SudoGrid)
        TEST.display("gridview", 1, "Observation de la grille : "\
                     "quels chiffres contient le rang #{0} ?".format(irow))
        vals = grid.row(irow).listPresent()
        TEST.display("gridview", 3, "Résultat = {0}"\
                                     .format(vals))
        return (len(vals), vals)
    
    def _lookupRowMissing(self, grid, args):
        return self.rowMissing(grid, args[0])
    
    def rowMissing(self, grid, irow):
        '''Cherche les valeurs manquantes dans le rang <row>
        Retourne en tuple le nombre et la liste de valeurs
        '''
        TEST = self.env.TEST
        assert isinstance(grid, SudoGrid)
        TEST.display("gridview", 1, "Observation de la grille : "\
                     "quels chiffres sont absents du rang #{0} ?".format(irow))
        vals = grid.row(irow).listAbsent()
        TEST.display("gridview", 3, "SudoGridView : résultat = {0}"\
                                     .format(vals))
        return (len(vals), vals)

    def _lookupRowEmptyPlc(self, grid, args):
        return self.rowEmptyPlc(grid,args[0])
    
    def rowEmptyPlc(self, grid, irow):
        '''Cherche les cases vides dans le rang <row>. Retourne le nombre
        et la liste des positions des cases vides
        '''
        TEST = self.env.TEST
        assert isinstance(grid, SudoGrid)
        TEST.display("gridview", 1, "Observation de la grille : "\
                     "quelles sont les cases vides du rang #{0} ?".format(irow))
        emp = grid.row(irow).listEmpty()
        r = (len(emp), emp)
        TEST.display("gridview", 3, "SudoGridView : résultat = {0}"\
                                     .format(r))
        return (r)

    def _lookupColContent(self, grid, args):
        return self.colContent(grid,args[0])
    
    def colContent(self, grid, icol):
        '''Cherche les valeurs contenues dans la colonne <col>
        Retourne en tuple le nombre et la liste de valeurs
        '''
        TEST = self.env.TEST
        assert isinstance(grid, SudoGrid)
        TEST.display("gridview", 1, "Observation de la grille : "\
                     "quels chiffres contient la colonne #{0} ?".format(icol))
        vals = grid.col(icol).listPresent()
        TEST.display("gridview", 3, "SudoGridView : résultat = {0}"\
                                     .format(vals))
        return (len(vals), vals)
    
    def _lookupColMissing(self, grid, args):
        return self.colMissing(grid,args[0])
    
    def colMissing(self, grid, icol):
        '''Cherche les valeurs manquantes dans la colonne <col>
        Retourne en tuple le nombre et la liste de valeurs
        '''
        TEST = self.env.TEST
        assert isinstance(grid, SudoGrid)
        TEST.display("gridview", 1, "Observation de la grille : "\
                     "quels chiffres sont absents de la colonne #{0} ?"\
                     .format(icol))
        vals = grid.col(icol).listAbsent()
        TEST.display("gridview", 3, "SudoGridView : résultat = {0}"\
                                     .format(vals))
        return (len(vals), vals)
    
    def _lookupColEmptyPlc(self, grid, args):
        return self.colEmptyPlc(grid,args[0])
    
    def colEmptyPlc(self, grid, icol):
        '''Cherche les cases vides dans la colonne <col>. Retourne le nombre
        et la liste des positions des cases vides
        '''
        TEST = self.env.TEST
        assert isinstance(grid, SudoGrid)
        TEST.display("gridview", 1, "Observation de la grille : "\
                     "quels sont les cases vides de la colonne #{0} ?"\
                     .format(icol))
        emp = grid.col(icol).listEmpty()
        TEST.display("gridview", 3, "SudoGridView : résultat = {0}"\
                                     .format(emp))
        return (len(emp), emp)

    def _lookupSqrContent(self, grid, args):
        return self.sqrContent(grid,args[0])
    
    def sqrContent(self, grid, isqr):
        '''Cherche les valeurs contenues dans le carré <sqr>
        Retourne en tuple le nombre et la liste de valeurs
        '''
        TEST = self.env.TEST
        assert isinstance(grid, SudoGrid)
        TEST.display("gridview", 1, "Observation de la grille : "\
                     "quels chiffres contient le carré #{0} ?".format(isqr))
        vals = grid.sqr(isqr).listPresent()
        TEST.display("gridview", 3, "SudoGridView : résultat = {0}"\
                                     .format(vals))
        return (len(vals), vals)

    def _lookupSqrMissing(self, grid, args):
        return self.sqrMissing(grid,args[0])
    
    def sqrMissing(self, grid, isqr):
        '''Cherche les valeurs manquantes dans le carré <sqr>
        Retourne en tuple le nombre et la liste de valeurs
        '''
        TEST = self.env.TEST
        assert isinstance(grid, SudoGrid)
        TEST.display("gridview", 1, "Observation de la grille : "\
                     "quels chiffres sont absents du carré #{0} ?".format(isqr))
        vals = grid.sqr(isqr).listAbsent()
        TEST.display("gridview", 3, "SudoGridView : résultat = {0}"\
                                     .format(vals))
        return (len(vals), vals)
    
    def _lookupSqrEmptyPlc(self, grid, args):
        return self.sqrEmptyPlc(grid,args[0])
    
    def sqrEmptyPlc(self, grid, isqr):
        '''Cherche les cases vides dans le carré <sqr>. Retourne le nombre
        et la liste des positions des cases vides
        '''
        TEST = self.env.TEST
        assert isinstance(grid, SudoGrid)
        TEST.display("gridview", 1, "Observation de la grille : "\
                     "quelles sont les cases vides du carré #{0} ?"\
                     .format(isqr))
        emp = grid.sqr(isqr).listEmpty()
        TEST.display("gridview", 3, "SudoGridView : résultat = {0}"\
                                     .format(emp))
        return (len(emp), emp)

    def _lookupSqrsInSqrRowContain(self, grid, args):
        return self.sqrsInSqrRowContain(grid, args[0], args[1])

    def sqrsInSqrRowContain(self, grid, isqr, val):
        '''Cherche quels carrés de la grille <grid> du
        même rang de carrés que <isqr> contiennent
        le chiffre <val>
        '''
        TEST = self.env.TEST
        assert isinstance(grid, SudoGrid)
        TEST.display("gridview", 1, "Observation de la grille : "\
                     "quels carrés du même rang que le carré #{0} contiennent "\
                     "le chiffre {1} ?".format(isqr, val))
        #premier carré de ce rang de carrés = 1,4 et 7
        sqr1= 1 + 3*((isqr-1)//3)
        #faire la liste
        sqrs = list()
        nb = 0
        for isqr in range(sqr1, sqr1+3):
            if grid.sqr(isqr).contains(val):
                sqrs.append(isqr)
                nb=nb+1
        TEST.display("gridview", 3, "SudoGridView : résultat = {0}"\
                                     .format( (nb, sqrs) ))
        return (nb, sqrs)

    def _lookupSqrsInSqrRowNotContain(self, grid, args):
        return self.sqrsInSqrRowNotContain(grid, args[0], args[1])

    def sqrsInSqrRowNotContain(self,grid,isqr,val):
        '''Cherche quels carrés de la grille <grid> du
        même rang de carrés que <isqr> ne contiennent
        pas le chiffre <val>
        '''
        TEST = self.env.TEST
        assert isinstance(grid, SudoGrid)
        TEST.display("gridview", 1, "Observation de la grille : "\
                     "quels carrés du même rang que le carré #{0} ne "\
                     "contiennent pas le chiffre {1} ?".format(isqr, val))
        #premier carré de ce rang de carrés
        sqr1= 1 + 3*((isqr-1)//3)
        #faire la liste
        sqrs = list()
        nb = 0
        for isqr in range(sqr1, sqr1+3):
            if not grid.sqr(isqr).contains(val):
                sqrs.append(isqr)
                nb=nb+1
        TEST.display("gridview", 3, "SudoGridView : résultat = {0}"\
                                     .format( (nb, sqrs) ))
        return (nb, sqrs)

    def _lookupSqrsInSqrColContain(self, grid, args):
        return self.sqrsInSqrColContain(grid, args[0], args[1])

    def sqrsInSqrColContain(self,grid,isqr,val):
        '''Cherche quels carrés de la grille <grid> de
        la même colonne de carrés que <isqr>
        contiennent le chiffre <val>
        '''
        TEST = self.env.TEST
        assert isinstance(grid, SudoGrid)
        TEST.display("gridview", 1, "Observation de la grille : "\
                     "quels carrés de la même colonne que le carré #{0} "\
                     .format(isqr) \
                     + "contiennent le chiffre {0} ?".format(val))
        #premier carré de cette colonne de carrés = 1,2 et 3
        sqr1 = 1 + (isqr-1)%3
        #faire la liste
        sqrs = list()
        nb = 0
        for isqr in (sqr1, sqr1+3, sqr1+6):
            if grid.sqr(isqr).contains(val):
                sqrs.append(isqr)
                nb=nb+1
        TEST.display("gridview", 3, "SudoGridView : résultat = {0}"\
                                     .format( (nb, sqrs) ))
        return (nb, sqrs)

    def _lookupSqrsInSqrColNotContain(self, grid, args):
        return self.sqrsInSqrColNotContain(grid, args[0], args[1])

    def sqrsInSqrColNotContain(self,grid,isqr,val):
        '''Cherche quels carrés de la grille <grid> de
        la même colonne de carrés que <isqr> ne
        contiennent pas le chiffre <val>
        '''
        TEST = self.env.TEST
        assert isinstance(grid, SudoGrid)
        TEST.display("gridview", 1, "Observation de la grille : "\
                     "quels carrés de la même colonne que le carré #{0} "\
                     .format(isqr) \
                     + "ne contiennent pas le chiffre {0} ?".format(val))
        #premier carré de cette colonne de carrés = 1,2 et 3
        sqr1 = 1 + (isqr-1)%3
        #faire la liste
        sqrs = list()
        nb = 0
        for isqr in (sqr1, sqr1+3, sqr1+6):
            if not grid.sqr(isqr).contains(val):
                sqrs.append(isqr)
                nb=nb+1
        TEST.display("gridview", 3, "SudoGridView : résultat = {0}"\
                                     .format( (nb, sqrs) ))
        return (nb, sqrs)
    
    def _lookupRowsBySqrContain(self, grid, args):
        return self.rowsBySqrContain(grid, args[0], args[1])

    def rowsBySqrContain(self,grid,isqr,val):
        '''Cherche quels rangs passant par le carré <sqr>
        de la grille <grid> contiennent le chiffre <val>.
        Retourne un tuple (nombre, liste des rangs)
        '''
        TEST = self.env.TEST
        assert isinstance(grid, SudoGrid)
        TEST.display("gridview", 1, "Observation de la grille : quels rangs "\
                     "passant par le carré #{0} contiennent le chiffre {1} ?"\
                     .format(isqr, val))
        #premier rang passant par ce carré
        row1 = grid.coordToRC(isqr,1)[0]
        #faire la liste
        rows = list()
        nb = 0
        for irow in range(row1,row1+3):
            if grid.row(irow).contains(val):
                rows.append(irow)
                nb = nb+1
        TEST.display("gridview", 3, "SudoGridView : résultat = {0}"\
                                     .format( (nb, rows) ))
        return (nb, rows)
    
    def _lookupRowsBySqrNotContain(self, grid, args):
        return self.rowsBySqrNotContain(grid, args[0], args[1])

    def rowsBySqrNotContain(self,grid,isqr,val):
        '''Cherche quels rangs passant par le carré <sqr>
        de la grille <grid> ne contiennent pas le chiffre
        <val>.
        Retourne un tuple (nombre, liste des rangs)
        '''
        TEST = self.env.TEST
        assert isinstance(grid, SudoGrid)
        TEST.display("gridview", 1, "Observation de la grille : "\
                     "quels rangs passant par le carré #{0} ne "\
                     "contiennent pas le chiffre {1} ?".format(isqr, val))
        #premier rang passant par ce carré
        row1 = grid.coordToRC(isqr,1)[0]
        #faire la liste
        rows = list()
        nb = 0
        for irow in range(row1,row1+3):
            if not grid.row(irow).contains(val):
                rows.append(irow)
                nb = nb+1
        TEST.display("gridview", 3, "SudoGridView : résultat = {0}"\
                                     .format( (nb, rows) ))
        return (nb, rows)

    def _lookupColsBySqrContain(self, grid, args):
        return self.colsBySqrContain(grid, args[0], args[1])

    def colsBySqrContain(self,grid,isqr,val):
        '''Cherche quelles colonnes passant par le carré
        <sqr> de la grille <grid> contiennent <val>.
        Retourne un tuple (nombre, liste des colonnes)
        '''
        TEST = self.env.TEST
        assert isinstance(grid, SudoGrid)
        TEST.display("gridview", 1, "Observation de la grille : "\
                     "quels colonnes passant par le carré #{0} contiennent "\
                     "le chiffre {1} ?".format(isqr, val))
        #première colonne passant par ce carré
        col1 = grid.coordToRC(isqr,1)[1]
        #faire la liste
        cols = list()
        nb = 0
        for icol in range(col1,col1+3):
            if grid.col(icol).contains(val):
                cols.append(icol)
                nb = nb+1
        TEST.display("gridview", 3, "SudoGridView : résultat = {0}"\
                                     .format( (nb, cols) ))
        return (nb, cols)
    
    def _lookupColsBySqrNotContain(self, grid, args):
        return self.colsBySqrNotContain(grid, args[0], args[1])

    def colsBySqrNotContain(self,grid,isqr,val):
        '''Cherche quelles colonnes passant par le carré
        <sqr> de la grille <grid> ne contiennent pas <val>.
        Retourne un tuple (nombre, liste des colonnes)
        '''
        TEST = self.env.TEST
        assert isinstance(grid, SudoGrid)
        TEST.display("gridview", 1, "Observation de la grille : "\
                     "quelles colonnes passant par le carré #{0} ne "\
                     "contiennent pas le chiffre {1} ?".format(isqr, val))
        #première colonne passant par ce carré
        col1 = grid.coordToRC(isqr,1)[1]
        #faire la liste
        cols = list()
        nb = 0
        for icol in range(col1,col1+3):
            if not grid.col(icol).contains(val):
                cols.append(icol)
                nb = nb+1
        TEST.display("gridview", 3, "SudoGridView : résultat = {0}"\
                                     .format( (nb, cols) ))
        return (nb, cols)

    def _lookupEmptyPlacesRC(self, grid, args):
        return self.emptyPlacesRC(grid, args[0], args[1])
    
    def emptyPlacesRC(self,grid,rowList,colList):
        '''Cherche quelles cases sont vides à l'intersection
        des rangs <rowList> et des colonnes <colList>.
        Les rangs et colonnes doivent correspondre à un
        seul carré.
        Retourne un tuple (nombre, liste de cases) dans
        lequel les cases sont en tuples de coordonnées RC
        '''
        TEST = self.env.TEST
        assert isinstance(grid, SudoGrid)
        TEST.display("gridview", 1, "Observation de la grille : "\
                     "quelles sont les cases vides à l'intersection des "\
                     "rangs {0}".format(rowList) +\
                     "et des colonnes {0} ?".format(colList))
        lplc = list()
        nb  = 0
        for iRow in rowList:
            for iCol in colList:
                if grid.valRC(iRow,iCol) == 0:
                    lplc.append([iRow,iCol])
                    nb = nb+1
        TEST.display("gridview", 3, "SudoGridView : résultat = {0}"\
                                     .format( (nb, lplc) ))
        return (nb, lplc)
        
    def _lookupGridNbEmptyPlaces(self, grid, args):
        return self.gridNbEmptyPlaces(grid)
    
    def gridNbEmptyPlaces(self,grid):
        '''Compte les cases vides dans la grille.'''
        TEST = self.env.TEST
        assert isinstance(grid, SudoGrid)
        TEST.display("gridview", 1, "Observation de la grille : "\
                     "combien de cases vides y a-t-il dans la grille ?")
        nb = grid.nbEmpty()
        TEST.display("gridview", 3, "SudoGridView : résultat = {0}"\
                                     .format(nb))
        return nb

    def _lookupGridCompleted(self, grid, args):
        return self.gridCompleted(grid)

    def gridCompleted(self, grid):
        '''Indique si la grille est remplie. S'il s'agit d'une partie de
        résolution, cela signifie que la partie est gagnée.
        '''
        TEST = self.env.TEST
        assert isinstance(grid, SudoGrid)
        TEST.display("gridview", 1, "Observation de la grille : "
                     "Est-ce que la grille est terminée ? ")
        r = grid.isFull()
        TEST.display("gridview", 3, "SudoGridView : résultat = {0}"\
                                     .format(r))
        return r
        
    @property
    def grid(self):
        return self._grid
    


#TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST
if __name__ == "__main__":
    env = sudoenv.SudoEnv()
    TEST = env.TEST

    print("\ntest de SudoGridView")
    print("--------------------\n")

    TEST.test("gridview", 3)
    grid = SudoGrid()
    vals = ui.sudoFichReadLines("grille_easy1.sudo")
    print ("fichier lu :\n", vals)
    grid.fillByRowLines(vals)
    print("\nGrille :")
    grid.show()
    from sudogrid import SudoBloc
    bl = SudoBloc()
    list9 = [2,5,0,6,8,0,0,3,4]

    view = SudoGridView(grid)
