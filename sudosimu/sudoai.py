'''Le module sudothinkAI contient la classe ThinkAI.
ThinkAI est une classe qui encapsule la simulation d'intelligence. Celle-ci va
permettre au joueur simulé de choisir comment il poursuit sa résolution, en
cherchant de l'information dans la grille et en sélectionnant les techniques
les plus appropriées en fonction de l'état présent de la grille et d'un
"savoir-faire" de résolution, éventuellement sujet à de l'apprentissage.
C'est ici que sera évalué la décision d'abandon si aucune technique ne permet
de faire de nouveau placement.

Dans la classe SudoAI, contrairement à toutes les autres classes du programme,
l'information utilisée dans la résolution est considérée comme un savoir
permanent, non sujet à l'obsolescence de la mémoire de travail. C'est le
savoir-faire du joueur, sa capacité globale à "jouer au Sudoku".
'''
#### A REECRIRE ENTIEREMENT ####
'''
A REVOIR
22/11/2017
Gestion des exceptions. Pour le moment, l'évaluation des critères et des
règle n'échoue jamais, s'il y a une exception dans la fonction alors la règle
ou le critère n'a tout simplement plus de valeur mais l'exception n'est pas
propagée.
Il faudrait voir comment non seulement supprimer la valeur mais aussi propager
l'exception. Cela permettrai d'introduire un mode dégradé de la gestion AI qui
pourrait aboutir proprement à l'échec de décision et éventuellement l'abandon.
Le passage dans ce mode dégradé pourrait se faire selon des caractéristiques
du profil de réflexion du joueur. Par exemple abort() de toutes les techniques
en cours, et reprendre au niveau 0 la tentative de résolution, mais abandon
quand même si cette manoeuvre échoue plusieurs fois de suite.

Historique des modifications
11/12/2017
Séparation en plusieurs modules :
- Tous les labels constants dans le module 'sudoaiconst'
- Les data, critères et règles dans 'sudoairules'
'''

#exécution interne au package
if __name__ in ("__main__", "sudoai"):
    import sudobaseclass as base
    import sudoenv
    import sudoui as ui
    import sudorules as rules
    from sudorules import Sudoku_Error
    from sudomemory import SudoMemory
    from sudoaiconst import *
    from sudoairules import SudoAIdata, SudoAIcritSet, SudoAIruleSet
    from sudoaitact import SudoAItactics
#exécution depuis l'extérieur du package sudosimu
elif __name__ == "sudosimu.sudoai":
    from sudosimu import sudobaseclass as base
    from sudosimu import sudoenv
    from sudosimu import sudoui as ui
    from sudosimu import sudorules as rules
    from sudosimu.sudorules import Sudoku_Error
    from sudosimu.sudomemory import SudoMemory
    from sudosimu.sudoaiconst import *
    from sudosimu.sudoairules import SudoAIdata, SudoAIcritSet, SudoAIruleSet
    from sudosimu.sudoaitact import SudoAItactics
else:
    raise Exception("Impossible de faire les imports dans le module sudoai.")

class SudoAI(base.SudoBaseClass):
    '''SudoAI contient le système de décision pour la résolution. Celui-ci est
    implémenté sous forme de programmation logique, avec des critères et des
    règles, dont l'évaluation permet de prendre une décision : choisir une
    technique à appliquer, la commencer, la continuer ou l'interrompre, chercher
    une opportunité après un placement, etc.
    Les évaluations sont basées sur un jeu de données (attribut _data) qui
    représentent l'état présent de la résolution en cours.
    '''
    
    def __init__(self, mem, know=None, \
                 env=None, testlevel=sudoenv.TEST_AILEVEL):
        '''Initialisation du système de décision. Celui-ci a initialement
        un dictionnaire de données avec des valeurs de début de résolution.
        Le code qui crée l'instance SudoAI doit appeler <instance>.data pour
        récupérer ce dictionnaire et mettre à jour les données au fur et à
        mesure de l'avancement de la résolution.
        '''
        #init de la classe racine
        assert isinstance(env, sudoenv.SudoEnv) or env is None
        assert isinstance(testlevel, int) and testlevel>=0 \
                or testlevel is None
        #reprendre un précédente niveau de test s'il existe déjà
        oldlev = env.testLevel("ai")
        if oldlev is not None and testlevel != oldlev:
            testlevel = oldlev
        base.SudoBaseClass.__init__(self, env=env, \
                                    testlabel="ai", testlevel=testlevel)
        #ok init de cette classe
        TEST = self.env.TEST
        TEST.display("ai", 3, "SudoAI - Dans __init__()")
        TEST.display("ai", 1, "Création du système décisionnel AI")
        assert isinstance(mem, SudoMemory)
        assert know is None or isinstance(know, SudoKnowledge)
        self._mem = mem
        self._know = know
        #créer un dictionnaire de données initiales
        self._data = SudoAIdata(self._mem, env=self._env)
        #création de l'ensemble des règles et critères
        self._crits = SudoAIcritSet(self._mem, self._data, env=self._env)
        self._rules = SudoAIruleSet(self._mem, self._crits, env=self._env)
        #création du système de décision tactique
        self._tacts = SudoAItactics(self._mem, self._rules, env=self._env)
##        #évaluer les critères et règles avec les données initiales
##        TEST.display("ai", 3, "Première évaluation du système décionnel avec " \
##                              "données d'initialisation.")
##        self._evaluate()
        return

    def suggest(self):
        '''Retourne la décision d'action du système AI. Cette décision est une
        information unique : continuer la technique, abandonner, chercher une
        opportunité, etc. Elle représente la meilleur choix évalué par le
        système expert dans la situation actuelle de résolution.
        '''
        TEST = self.env.TEST
        TEST.display("ai", 3, "SudoAI - Dans suggest()")
        if TEST.ifLevel("ai", 2) is True:
            TEST.display("ai", 2, "Données d'avancement de la résolution : ")
            self.data.disp()
        TEST.display("ai", 2, "Interrogation du système expert AI.")
        TEST.display("ai", 3, "AIsuggest - itération du système de décision")

        #première étape = évaluer les règles de jeu applicables
        TEST.display("ai", 3, "AIsuggest - Evaluation des critères et règles.")
        self.evaluateRules()
        #deuxième étape = faire les choix tactiques
        TEST.display("ai", 3, "AIsuggest - Demande de choix tactique.")
        rulename = self._tacts.ruleSelection()
        TEST.display("ai", 3, "AIsuggest - Choix tactique retourné : "\
                     "règle \"{0}\"".format(rulename))
        #mise en forme de la réponse = action suggérée
        r = self._makeAIanswer(rulename)
        TEST.display("ai", 2, "AIsuggest - suggestion AI : {0}".format(r))
        return r
        
        
    def evaluateRules(self):
        '''Met à jour les évaluations des critères et règles. Cette méthode est
        appelée si les données (attribut _data) sont susceptibles d'avoir été
        modifiées.
        '''
        TEST = self.env.TEST
        TEST.display("ai", 3, "SudoAI - Dans evaluateRules()")
        self._crits.evalAll()
        self._rules.evalAll()
        return

    def _makeAIanswer(self, rulename):
        '''Elabore la suggestion d'action du système de décision, à partir de
        l'évaluation des règles et l'application des tactiques de jeu.
        Retourne un tuple qui décrit la suggestion pour ThinkAI.
        '''
        TEST = self.env.TEST
        TEST.display("ai", 3, "SudoAI - Dans _makeAIanswer()")

        #Mise en forme de la réponse pour la règle choisie
        if rulename == AIRULE_CHECKGRID:
            TEST.display("ai", 1, "AI : Vérification de grille terminée.")
            ans = ("check", None)
        elif rulename == AIRULE_TECHCONT:
            TEST.display("ai", 2, "AI : Continuation de la même technique.")
            ans = ("continue", None)
        elif rulename == AIRULE_CHRCGA:
            TEST.display("ai", 1, "AI : Nouvelle technique de résolution : "\
                         "ChRCga.")
            ans = ("start_tech", "techchrcga")
        elif rulename == AIRULE_LPLCG:
            TEST.display("ai", 1, "AI : Nouvelle technique de résolution : "\
                         "LastPlcg")
            ans = ("start_tech", "techlplcg")
        elif rulename == AIRULE_LPLCP:
            TEST.display("ai", 1, "AI : Nouvelle technique de résolution : "\
                         "LastPlcp")
            ans = ("start_tech", "techlplcp")
        elif rulename == AIRULE_DISCARD:
            TEST.display("ai", 1, "AI : Arrêt de la technique en cours.")
            ans = ("discard_tech", None)
        elif rulename == AIRULE_DISCARDALL:
            TEST.display("ai", 1, "AI : Arrêt de toutes les techniques en cours.")
            ans = ("discard_all", None)
        else:
            #ne devrait jamais se produire car l'AI DOIT TOUJOURS suggérer
            raise Sudoku_Error("AI - Erreur fatale AI, impossible de faire "\
                               "une suggestion d'action valable.")
        TEST.display("ai", 3, "AIanswer - Réponse = {0}.".format(ans))
        return ans
        
    @property
    def data(self):
        return self._data
    
    @property
    def crits(self):
        return self._crits

    @property
    def rules(self):
        return self._rules

    @property
    def tacts(self):
        return self._tacts
    
    def dispcrits(self):
        self._crits.dispval()
        return

    def disprules(self):
        self._rules.dispval()
        return

    def disp(self):
        self.data.disp()
        self.crits.disp()
        self.rules.disp()
        self.tacts.disp()
        return
    
    def show(self):
        '''Affiche toutes les valeurs du système de décision AI.'''
        ui.display("Le système contient {0} données, {1} critères et " \
                   "{2} règles.\nValeurs des données :" \
                   .format(self.data.nb, self.crits.nb, self.rules.nb))
        self.data.disp()
        ui.display("Valeurs des critères :")
        self.crits.disp()
        ui.display("Valeurs des règles :")
        self.rules.disp()
        return

        

#TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 
#TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 

if __name__ == "__main__":
    env = sudoenv.SudoEnv()
    TEST = env.TEST
    TEST.test("ai", 3)
    env.testLabel("aidata", 4)
    env.testLabel("airule", 3)

    mem = SudoMemory()
    sai = SudoAI(mem, env=env)
    data = sai.data
    
