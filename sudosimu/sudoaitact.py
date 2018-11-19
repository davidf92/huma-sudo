'''Le module sudoaitact regroupe les concepts de tactiques de résolution du
système de décision AI. Cela représente les arbitrages qui sont faits entre
plusieurs possibilités toutes valides, par exemple privilégier une technique
de résolution plutôt qu'une autre, la manière de faire face à des passages
difficiles, etc.

Historique des modifications
----------------------------
11/12/2017 Création du module.

'''

#exécution interne au package
if __name__ in ("__main__", "sudoaitact"):
    import sudobaseclass as base
    import sudoenv
    import sudoui as ui
    import sudorules as rules
    from sudorules import Sudoku_Error
    from sudomemory import SudoMemory
    from sudoaiconst import *
    from sudoairules import SudoAIdata, SudoAIrule, SudoAIruleSet, SudoAIcritSet
#exécution depuis l'extérieur du package sudosimu
elif __name__ == "sudosimu.sudoaitact":
    from sudosimu import sudobaseclass as base
    from sudosimu import sudoenv
    from sudosimu import sudoui as ui
    from sudosimu import sudorules as rules
    from sudosimu.sudorules import Sudoku_Error
    from sudosimu.sudomemory import SudoMemory
    from sudosimu.sudoaiconst import *
    from sudosimu.sudoairules import SudoAIdata, SudoAIrule, SudoAIruleSet, SudoAIcritSet
else:
    raise Exception("Impossible de faire les imports dans le module sudoai.")


class SudoAItactics(base.SudoBaseClass):
    '''Cette classe représente les arbitrages entre règles du système de
    décision AI, qui aboutissent à réaliser un choix parmi un ensemble de
    possibilités valides. C'est le coeur le du concept AI.
    Une instance peut accéder en remontant ses attributs à toutes les infos
    du système décisionnel (règles, critères, données  d'avancement de la
    résolution).
    '''
    def __init__(self, mem, airules, \
                 env=None, testlevel=sudoenv.TEST_AILEVEL):
        '''Initialisation de l'instance.'''
        #init de la classe racine
        assert isinstance(env, sudoenv.SudoEnv) or env is None
        assert isinstance(testlevel, int) and testlevel>=0 \
                or testlevel is None
        #reprendre un précédente niveau de test s'il existe déjà
        oldlev = env.testLevel("aitact")
        if oldlev is not None and testlevel != oldlev:
            testlevel = oldlev
        base.SudoBaseClass.__init__(self, env=env, \
                                    testlabel="aitact", testlevel=testlevel)
        #ok init de cette classe
        TEST = self.env.TEST
        TEST.display("aitact", 3, "SudoAI - dans SudoAIcritSet.__init__()")
        TEST.display("aitact", 1, "SudoAI - Initialisation de l'ensemble de "\
                             "critères du système de décision AI.")
        assert isinstance(mem, SudoMemory)
        self._mem = mem
        assert isinstance(airules, SudoAIruleSet)
        self._rules = airules

        #initialisation de la tactique de jeu
        self._initTactics()
        return

    def _initTactics(self):
        '''Initialise la tactique de jeu.'''
        TEST = self.env.TEST
        TEST.display("aitact", 3, "SudoAItactics - Dans aiDecision()")
        #Tactique : vérif de grille en priorité dès que l'état est inconnu
        TEST.display("aitact", 1, "Tactique de jeu : "\
                     "Vérifier la grille en priorité sur les autres règles.")
        self._checkgridfirst = True
        #Tactique : au premier niveau, commencer par la règle ChRC
        TEST.display("aitact", 1, "Tactique de jeu : "\
                     "Commencer au niveau 1 par la technique ChRCgridAll.")
        self._nextniv1 = AIRULE_CHRCGA
        #Possibilité de tenter une fois de continuer après échec
        self._canTryContinue = True

        
    def ruleSelection(self):
        '''Elaboration de la décision AI = la règle de jeu privilégiée
        pour la prochaine action de résolution.
        '''
        TEST = self.env.TEST
        TEST.display("aitact", 3, "SudoAItactics - Dans aiDecision()")

        if TEST.ifLevel("aitact", 3) is True:
            TEST.display("aitact", 3, "ruleSuggestion - Valeur des règles :")
            self._rules.disp()

        select = None

        #sélectionner si la grille doit être vérifiée en priorité
        if select is None:
            if self._checkgridfirst is True:
                rule = self._selectGridCheck()
                if rule is not None:
                    select = rule
                    self._canTryContinue = True
        #choix de la règle au premier niveau
        if select is None:
            if self._rules.rule(AIRULE_CHRCGA).val > 0 \
               and self._rules.rule(AIRULE_LPLCG).val > 0:
                rule = self._selectFirstNiv()
                if rule is not None:
                    select = rule
                    self._canTryContinue = True
        #par défaut choisir la première règle valide trouvée
        if select is None:
            rule = self._selectFirstValid()
            if rule is not None:
                select = rule
                self._canTryContinue = True
        #aucune règle n'est valide, décision impossible.
        #La première fois, tenter une nouvelle itération, mais une seule fois.
        if select is None:
            if self._canTryContinue is True:
                TEST.display("aitact", 1, "Aucune règle tactique n'a pu être "\
                             "appliquée. Un nouvel essai va être tenté.")
                select = self._rules.rule(AIRULE_TECHCONT)
                self._canTryContinue = False
                self._canTryBeforeFatal = True
        #dernière solution = revenir au niveau le plus bas de résolution
        #mais une seule fois sinon boucle infinie
        if select is None:
            if self._canTryBeforeFatal is True:
                TEST.display("aitact", 1, "Aucune règle tactique n'a pu être "\
                             "appliquée malgré un nouvel essai. Retour au "\
                             "niveau de base de résolution.")
                self._canTryBeforeFatal = False
                select = self._rules.rule(AIRULE_DISCARDALL)
        #a ce stade boucle infinie
        if select is None:
#### GESTION D'EXCEPTION A FAIRE ICI ####            
            raise Sudoku_Error("Erreur AI : Echec répétitif à choisir une règle "\
                               "d'avancement de la résolution.")

        TEST.display("aitact", 3, "Aitactics - Règle sélectionnée : \"{0}\"."\
                                  .format(select.name))
        #TEST : contrôler l'affichage trop fréquent "continue" et "check"
        if not select.name in (AIRULE_TECHCONT, AIRULE_CHECKGRID):
            TEST.display("aitact", 1, "Règle sélectionnée par l'AI : {0}"\
                                      .format(select.text))
        return select.name

    def _selectGridCheck(self):
        '''Sélectionne la règle de vérification de grille si elle est valide.'''
        TEST = self.env.TEST
        if self._rules.rule(AIRULE_CHECKGRID).val > 0:
            TEST.display("aitact", 2, "Tactique appliquée : "\
                         "vérification de grille en priorité.")
            return self.rules.rule(AIRULE_CHECKGRID)
        else:
            return None
        
    def _selectFirstNiv(self):
        '''Tactique de jeu au premier niveau : alterner Ch/RC et LastPlc.
        Retourne l'objet 'rule' sélectionné.
        '''
        TEST = self.env.TEST
        TEST.display("aitact", 3, "SudoAItactics - Dans _selectFirstNiv()")
        TEST.display("aitact", 1, "Tactique appliquée : alternance entre "\
                     "les règles de premier niveau.")
        if self._nextniv1 == AIRULE_CHRCGA:
            rulename = AIRULE_CHRCGA
            self._nextniv1 = AIRULE_LPLCG
            TEST.display("aitact", 3, "Règle sélectionnée : "\
                         "Exécution de la technique ChRCgridAll")
        elif self._nextniv1 == AIRULE_LPLCG:
            rulename = AIRULE_LPLCG
            self._nextniv1 = AIRULE_CHRCGA
            TEST.display("aitact", 3, "Règle sélectionnée : "\
                         "Exécution de la technique LastPlaceGrid")
        else:
            return None
        return self.rules.rule(rulename)

    def _selectFirstValid(self):
        '''Tactique de jeu : parcourir les règles aléatoirement (dictionnaire)
        et retourner la première règle valide trouvée.
        '''
        TEST = self.env.TEST
        TEST.display("aitact", 3, "SudoAItactics - Dans _selectFirstValid()")
        for ru in self._rules.rules.values():
            if ru.val > 0:
                #C'est la règle à utiliser pour la suggestion
                TEST.display("aitatc", 1, "Tactique appliquée : sélection "\
                             "aléatoire parmi les règles valides.")
                TEST.display("aitact", 3, "Règle tactique sélectionnée : "\
                             "{0}.".format(ru.name))
                return ru
                     
    def eval(self):
        pass


    def disp(self):
        return
    
    @property
    def rules(self):
        return self._rules


#TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 
#TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 

if __name__ == "__main__":
    env = sudoenv.SudoEnv()
    TEST = env.TEST
    TEST.test("ai", 3)

    mem = SudoMemory(env=env)
    dataSet = SudoAIdata(mem, env=env)
    critSet = SudoAIcritSet(mem, dataSet, env=env)
    ruleSet = SudoAIruleSet(mem, critSet, env=env)
    tact = SudoAItactics(mem, ruleSet, env=env)

    ui.display("Evaluation des critères et règles.")
    critSet.evalAll()
    critSet.show()
    ruleSet.evalAll()
    ruleSet.show()
    
    
    
    
