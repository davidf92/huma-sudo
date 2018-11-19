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

TEST :
Ce module importe le module 'sudotest' et utilise l'objet global sudoTest de
classe SudoTest pour gérer de manière paramétrable les I/O de test du code.


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
'''

#exécution interne au package
if __name__ in ("__main__", "sudoai"):
    import sudobaseclass as base
    import sudoenv
    import sudoui as ui
    import sudorules as rules
    from sudorules import Sudoku_Error
    from sudomemory import SudoMemory
    from sudoainode import SudoAInode
#exécution depuis l'extérieur du package sudosimu
elif __name__ == "sudosimu.sudoai":
    from sudosimu import sudobaseclass as base
    from sudosimu import sudoenv
    from sudosimu import sudoui as ui
    from sudosimu import sudorules as rules
    from sudosimu.sudorules import Sudoku_Error
    from sudosimu.sudomemory import SudoMemory
    from sudosimu.sudoainode import SudoAInode
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
        self._crits = SudoAIcritSet(self._mem, ai=self, env=self._env)
        self._rules = SudoAIruleSet(self._mem, ai=self, env=self._env)
        #évaluer les critères et règles avec les données initiales
        TEST.display("ai", 3, "Première évaluation du système décionnel avec " \
                              "données d'initialisation.")
        self._evaluate()
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
        self._evaluate()
        r = self._makeAIsuggestion()
        TEST.display("ai", 2, "AIsuggest - suggestion AI : {0}".format(r))
        return r
        
        
    def _evaluate(self):
        '''Met à jour les évaluations des critères et règles. Cette méthode est
        appelée si les données (attribut _data) sont susceptibles d'avoir été
        modifiées.
        '''
        TEST = self.env.TEST
        TEST.display("ai", 3, "SudoAI - Dans _evaluate()")
        self._crits.evalAll()
        self._rules.evalAll()
        return

    def _makeAIsuggestion(self):
        '''Elabore la suggestion d'action du système de décision, à partir de
        l'évaluation des règles et l'application des tactiques de jeu.
        Retourne un tuple qui décrit la suggestion.
        '''
        TEST = self.env.TEST
        TEST.display("ai", 3, "SudoAI - Dans _makeAIsuggestion()")
        #Examine les règles et retourne la première trouvée dont la valeur
        #est non nulle.
        if TEST.ifLevel("ai", 3) is True:
            TEST.display("ai", 3, "AIsuggestion - Evaluation des règles :")
            self.rules.disp()
        for ru in self._rules.rules.values():
            if ru.val > 0:
                #C'est la règle à utiliser pour la suggestion
                TEST.display("ai", 2, "AIsuggestion - Règle sélectionnée : "\
                             "{0}.".format(ru.name))
                r = self._makeAIanswer(ru)
                return r
        #aucune règle n'a de valeur non nulle, décision impossible.
        #seule solution = revenir au niveau le plus bas de résolution
        return ("abort_all", None)
            
    def _makeAIanswer(self, rule):
        '''Construit le retour du système AI = un tuple contenant une
        suggestion d'action et des arguments.
        '''
        TEST = self.env.TEST
        TEST.display("ai", 3, "SudoAI - Dans _makeAIanswer()")
        if rule.name == RULE_TECHCONT:
            ans = ("continue", None)
        elif rule.name == RULE_TECHABORT:
            ans = ("abort_tech", None)
        elif rule.name == RULE_CHRC:
            TEST.display("ai", 1, "Nouvelle technique de résolution : "\
                         "Ch/RC.")
            ans = ("start_tech", "techchrcga")
        elif rule.name == RULE_LPLC:
            TEST.display("ai", 1, "Nouvelle technique de résolution : "\
                         "LastPlc")
            ans = ("start_tech", "techlplcg")
        elif rule.name == RULE_DISCARD:
            ans = ("discard_tech", None)
        elif rule.name == RULE_DISCARDALL:
            ans = ("discard_all", None)
        else:
            ans = ("abort_all", None)
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

    
##DONNEES D'ENTREE DU SYSTEME DE DECISION
##---------------------------------------    
'''Les données d'entrée alimentent le système logique. Elles sont utilisées
pour évaluer des critères de décision, lesquels serviront à leur tour à
l'évaluation de règles. Les données sont fournies au système AI sous la forme
d'un dictionnaire.
En pratique ces données représentent l'état d'avancement de la résolution, et
vont donc servir à décider la prochaine action de cette résolution.
'''

#Noms des données
DATA_BEGIN = "data_begin"           #début de résolution
DATA_NIV = "data_niv"               #niveau d'imbrication de techniques
DATA_NIVMAX = "data_nivmax"         #niveau max possible
DATA_INTECH = "data_intech"         #en train d'exécuter une technique
DATA_OPPORT = "data_opport"         #technique d'opportunité en cours
DATA_TECH = "data_tech"             #nom de la technique en cours
DATA_LTECH = "data_ltech"           #nom de la dernière/précédente technique
DATA_LACT = "data_lact"             #dernière action de pensée, technique ou AI
DATA_LTECHACT = "data_ltechact"     #dernière action d'une technique
DATA_LAIACT = "data_laiact"         #dernière action du système AI

#Dictionnaire des données du système
class SudoAIdata(dict, base.SudoBaseClass):
    '''C'est une classe qui représente l'état de réflexion de la résolution
    en cours : qu'est-ce qui est en train d'être fait, quelles techniques sont
    appliquées et quelles actions sont faites.
    SudoAIdata est juste un dictionnaire et hérite de la classe Python dict.
    '''
    def __init__(self, mem, env=None, testlevel=sudoenv.TEST_THINKAILEVEL):
        #init de la classe racine Sudosimu
        assert isinstance(env, sudoenv.SudoEnv) or env is None
        assert isinstance(testlevel, int) and testlevel>=0 \
                or testlevel is None
        base.SudoBaseClass.__init__(self, env=env, \
                                    testlabel="ai", testlevel=testlevel)
        #ok init de cette classe
        TEST = self.env.TEST
        TEST.display("ai", 3, "SudoAIdata - Dans __init__()")
        assert isinstance(mem, SudoMemory)
        self._mem = mem
        '''Initialise l'instance dans l'état de début de résolution.'''
        self[DATA_BEGIN] = True
        self[DATA_NIV] = 0
        self[DATA_NIVMAX] = 2
        self[DATA_INTECH] = False
        self[DATA_OPPORT] = False
        self[DATA_TECH] = None
        self[DATA_LTECH] = None
        self[DATA_LACT] = None
        self[DATA_LTECHACT] = None
        self[DATA_LAIACT] = None
        return

    @property
    def nb(self):
        return len(self)
    
    def disp(self):
        for item in self.keys():
            ui.display( "{0} = {1}".format(item, self[item]))
        return

    def show(self):
        ui.display("Le système contient {0} données. Valeurs :" \
                   .format(self.nb))
        self.disp()
        return

    
##GESTION DES CRITERES DU SYSTEME DE DECISION
##-------------------------------------------
'''Les critères AI sont des évaluations logiques calculées avec des informations
de situation du système, donc de situation de la résolution en cours.
Par exemple : "je suis en train d'exécuter une technique de résolution."
'''

#Noms des critères
CRIT_BEGIN = "crit_begin"           #début de la résolution
CRIT_NIV0 = "crit_niv0"             #le niveau d'imbrication = 0
CRIT_NIV1 = "crit_niv1"             #le niveau d'imbrication = 1
CRIT_NIV2SUP = "crit_niv2sup"       #le niveau d'imbrication = 2 ou plus
CRIT_NIVMAX = "crit_nivmax"         #le niveau d'imbrication = niveau max
CRIT_INTECH = "crit_intech"             #technique en cours
CRIT_NOTECH = "crit_notech"             #aucune technique en cours
CRIT_INOPPORT = "crit_inopport"         #dans une technique d'opportunité
CRIT_INTECHCHRC = "crit_intechchrc"     #la technique en cours est TechChRC
CRIT_INTECHLPLC = "crit_intechlplc"     #la technique en cours est TechLplc
CRIT_LTECHCHRC = "crit_lastchrc"        #dernière technique = TechChRC
CRIT_LTECHLPLC = "crit_lastlplc"        #dernière technique = TechLplc
CRIT_LASTPLACE = "crit_lastplace"       #dernière action = 'place'
CRIT_LASTEND = "crit_lastend"           #dernière action = 'end'

####pas encore utilisés, à faire
CRIT_LASTTECHPLACE = "crit_lastplace"   #dernière action technique = 'place'
CRIT_LASTTECHEND = "crit_lastend"       #dernière action technique = 'end'
CRIT_LASTAIPLACE = "crit_lastplace"     #dernière action AI = 'place'
CRIT_LASTAIEND = "crit_lastend"         #dernière action AI = 'end'
######

#Création du dictionnaire des critères
def createCriteria(mem, data, env):
    '''Crée et retourne un dictionnaire des critères d'analyse AI.'''
    crits = {
        CRIT_BEGIN : \
            SudoAIcrit(mem, CRIT_BEGIN, fEvalCritBegin, data, env=env), \
        CRIT_NIV0 : \
            SudoAIcrit(mem, CRIT_NIV0, fEvalCritNiv0, data, env=env), \
        CRIT_NIV1 : \
            SudoAIcrit(mem, CRIT_NIV1, fEvalCritNiv1, data, env=env), \
        CRIT_NIV2SUP : \
            SudoAIcrit(mem, CRIT_NIV2SUP, fEvalCritNiv2Sup, data, env=env), \
        CRIT_NIVMAX : \
            SudoAIcrit(mem, CRIT_NIVMAX, fEvalCritNivMax, data, env=env), \
        CRIT_INTECH : \
            SudoAIcrit(mem, CRIT_INTECH, fEvalCritInTech, data, env=env), \
        CRIT_NOTECH : \
            SudoAIcrit(mem, CRIT_NOTECH, fEvalCritNoTech, data, env=env), \
        CRIT_INOPPORT : \
            SudoAIcrit(mem, CRIT_INOPPORT, fEvalCritInOpport, data, env=env), \
        CRIT_INTECHCHRC : \
            SudoAIcrit(mem, CRIT_INTECHCHRC, fEvalCritInTechChrc, data, env=env), \
        CRIT_INTECHLPLC : \
            SudoAIcrit(mem, CRIT_INTECHLPLC, fEvalCritInTechLplc, data, env=env), \
        CRIT_LTECHCHRC : \
            SudoAIcrit(mem, CRIT_LTECHCHRC, fEvalCritLastTechChrc, data, env=env), \
        CRIT_LTECHLPLC : \
            SudoAIcrit(mem, CRIT_LTECHLPLC, fEvalCritLastTechLplc, data, env=env), \
        CRIT_LASTPLACE : \
            SudoAIcrit(mem, CRIT_LASTPLACE, fEvalCritLastActionPlace, data, env=env), \
        CRIT_LASTEND : \
            SudoAIcrit(mem, CRIT_LASTEND, fEvalCritLastActionEnd, data, env=env) \
        }
    return crits

        
#Fonctions d'évaluation des critères
def fEvalCritBegin(data):
    '''Retourne 1 si la résolution commence.'''
    return (1 if data.get(DATA_BEGIN) is True else 0)

def fEvalCritNiv0(data):
    '''Retourne 1 si le niveau d'exécution est 0.'''
    return (1 if data.get(DATA_NIV) == 0 else 0)

def fEvalCritNiv1(data):
    '''Retourne 1 si le niveau d'exécution est 1.'''
    return (1 if data.get(DATA_NIV) == 1 else 0)

def fEvalCritNiv2Sup(data):
    '''Retourne 1 si le niveau d'exécution est 2 ou plus.'''
    return (1 if data.get(DATA_NIV) >= 2 else 0)

def fEvalCritNivMax(data):
    '''Retourne 1 si le niveau d'exécution est le niveau maximum ou plus.'''
    return (1 if data.get(DATA_NIV) >= data.get(DATA_NIVMAX) else 0)

def fEvalCritInTech(data):
    '''Retourne 1 si une technique est en cours.'''
    return (1 if data.get(DATA_INTECH) is True else 0)

def fEvalCritNoTech(data):
    '''Retourne 1 si aucune technique n'est en cours.'''
    return (1 if data.get(DATA_INTECH) is not True else 0)

def fEvalCritInOpport(data):
    '''Retourne 1 si une technique d'opportunité est en cours.'''
    return (1 if data.get(DATA_OPPORT) is True else 0)

def fEvalCritInTechChrc(data):
    '''Retourne 1 si la technique en cours est CHRC.'''
    return (1 if data.get(DATA_INTECH) is True \
                 and data.get(DATA_TECH) == "techchrcga" else 0)

def fEvalCritInTechLplc(data):
    '''Retourne 1 si la technique en cours est LPLC.'''
    return (1 if data.get(DATA_INTECH) is True \
                 and data.get(DATA_TECH) == "techlplcg" else 0)

def fEvalCritLastTechChrc(data):
    '''Retourne 1 si la dernière technique appliquée est CHRC.'''
    return (1 if data.get(DATA_LTECH) == "techchrcga" else 0)

def fEvalCritLastTechLplc(data):
    '''Retourne 1 si la dernière technique appliquée est LPLC.'''
    return (1 if data.get(DATA_LTECH) == "techlplcg" else 0)

def fEvalCritLastActionPlace(data):
    '''Retourne 1 si la dernière action de pensée dans l'exécution d'une
    technique est 'place'.
    '''
    return (1 if data.get(DATA_LACT) == "place" else 0)

def fEvalCritLastActionEnd(data):
    '''Retourne 1 si la dernière action de pensée dans l'exploration AI
    est 'end'.
    '''
    return (1 if data.get(DATA_LACT) == "end" else 0)

#Implémentation des critères : classe de critère et classe de leur ensemble
class SudoAIcrit(base.SudoBaseClass):
    '''Représente un critère de décision dans un système AI, qui associe une
    valeur et une fonction d'évaluation basée sur des informations du système.
    Evaluer le critère se fait en exécutant la fonction. La valeur peut être
    réintialisée, ce qui est réalisé au début du processus de prise de décision.
    '''
    def __init__(self, mem, name, funcEval, data, \
                 env=None, testlevel=sudoenv.TEST_AILEVEL):
        '''Initialisation de la règle. Il n'a pas de valeur tant qu'il n'a
        pas été explicitement évalué.'''
        #init de la classe racine
        assert isinstance(env, sudoenv.SudoEnv) or env is None
        assert isinstance(testlevel, int) and testlevel>=0 \
                or testlevel is None
        base.SudoBaseClass.__init__(self, env=env, \
                                    testlabel="ai", testlevel=testlevel)
        #ok init de cette classe
        TEST = self.env.TEST
        TEST.display("ai", 3, "SudoAI - dans SudoAIcrit.__init__()")
        assert isinstance(mem, SudoMemory)
        self._mem = mem
        assert isinstance(data, SudoAIdata)
        self._data = data
        self._name = name
        self._func = funcEval
        self._val = None

    def eval(self):
        '''Evalue le critère et retourne sa valeur. Un critère peut toujours
        être évaluée. Si la fonction d'évaluation échoue alors le critère
        n'a plus de valeur.
        '''
        TEST = self.env.TEST
        TEST.display("ai", 3, "SudoAI - dans SudoAIcrit.eval()")
        try:
            self._val = self._func(self._data)
        except:
            self._val = None
            raise
        return self._val

    def clear(self):
        '''Réinitialise le critère, c'est-à-dire qu'il n'a plus de valeur.'''
        TEST = self.env.TEST
        TEST.display("ai", 3, "SudoAI - dans SudoAIcrit.clear()")
        self._val = None

    @property
    def name(self):
        return self._name
    
    @property
    def val(self):
        '''Valeur actuelle du critère sans réévaluation.'''
        return self._val
    
    def __str__(self):
        return "Critère de décision \'{0}\'".format(self._name)


class SudoAIcritSet(base.SudoBaseClass):
    '''Représente l'ensemble des critères d'évaluation de règles, dans le
    système de décision AI, dans leur état actuel d'évaluation. Les critères
    sont basés sur les données d'état de la résolution en cours.
    L'évalution de cet ensemble se fait au début du processus de prise de
    décision AI, elle déclenche l'évaluation de chaque critère en fonction
    de l'avancement de la résolution.
    '''
    def __init__(self, mem, ai, \
                 env=None, testlevel=sudoenv.TEST_AILEVEL):
        '''Crée le dictionnaire de règles.'''
        #init de la classe racine
        assert isinstance(env, sudoenv.SudoEnv) or env is None
        assert isinstance(testlevel, int) and testlevel>=0 \
                or testlevel is None
        base.SudoBaseClass.__init__(self, env=env, \
                                    testlabel="ai", testlevel=testlevel)
        #ok init de cette classe
        TEST = self.env.TEST
        TEST.display("ai", 3, "SudoAI - dans SudoAIcritSet.__init__()")
        TEST.display("ai", 1, "SudoAI - Initialisation de l'ensemble de "\
                             "critères du système de décision AI.")
        assert isinstance(mem, SudoMemory)
        self._mem = mem
        assert isinstance(ai, SudoAI)
        self._ai = ai
        #Création du dictionnaire de critères
        TEST.display("ai", 3, "SudoAIruleSet - Création du dictionnaire "\
                              "de critères.")
        self._crits = createCriteria(self._mem, ai.data, self.env)
        return

    def add(self, crit):
        '''Ajoute une nouvelle règle. Sa clé dans le dictionnaire est son nom.
        '''
        TEST = self.env.TEST
        TEST.display("ai", 3, "SudoAI - dans SudoAIcritSet.add()")
        assert isinstance(crit, AIcrit)
        self._crits[crit.name] = crit
        return
    
    def clear(self):
        '''Efface la valeur de tous les critères.'''
        TEST = self.env.TEST
        TEST.display("ai", 3, "SudoAI - dans SudoAIcritSet.clear()")
        for crit in self._crits.values():
            crit.clear()
        return

    def crit(self, critName):
        '''Retourne l'instance de critère indiqué par son nom, ou déclenche
        une exception s'il n'y a pas de critère de ce nom.
        '''
        TEST = self.env.TEST
        TEST.display("ai", 3, "SudoAI - dans SudoAIcritSet.crit()")
        cr = self._crits.get(critName, False)
        if cr is False:  #erreur, pas de critère de ce nom
            raise Sudoku_Error("Pas de critère nommée {0}".format(critName))
        return cr

    def critEval(self, critName):
        '''Retourne la valeur du critère indiqué par son nom. Au besoin
        fait l'évaluation de ce critère. Retourne False s'il n'y a pas de
        critère du nom indiqué. Propage une éventuelle exception.
        '''
        TEST = self.env.TEST
        TEST.display("ai", 3, "SudoAI - dans SudoAIcritSet.critEval()")
        cr = self._crits.get(critName, False)
        if cr is False:      #inconnu dans le dictionnaire
            raise Sudoku_Error("Pas de critère nommée {0}".format(critName))
        return cr.eval()

    def evalAll(self):
        '''Evalue tous les critères. Retourne toujours True.'''
        TEST = self.env.TEST
        TEST.display("ai", 3, "SudoAI - dans SudoAIcritSet.evalAll()")
        for cr in self._crits.values():
            cr.eval()
        return True

    @property
    def nb(self):
        return len(self._crits)
    

    def disp(self):
        '''Liste la valeur actuelle de tous les critères.'''
        for cr in self._crits.values():
            ui.display("{0} = {1}".format(cr.name, cr.val))
        return
        
    def show(self):
        '''Liste la valeur actuelle de tous les critères.'''
        ui.display("Le système contient {0} critères. Valeurs :" \
                           .format(self.nb))
        self.disp()
        return

        


##GESTION DES REGLES DU SYSTEME DE DECISION
##-----------------------------------------
'''Les règles AI sont des évaluations logiques calculées avec les critères AI.
Elles représentent les bases de décision, par exemple les actions possibles.
Une règle associe une valeur et une fonction de calcul de cette valeur.
'''

#Noms des règles
RULE_TECHCONT = "rule_techcont"     #continuer la technique en cours
RULE_TECHABORT = "rule_techabort"   #abandonner la technique en cours
RULE_CHRC = "rule_chrc"             #commencer la technique Chrc (niv1)
RULE_LPLC = "rule_lplc"             #commerncer la technique Lplc (niv1)
RULE_DISCARD = "rule_discard"       #arrêter la technique en cours
RULE_DISCARDALL = "rule_niv0"       #arrêter toutes les techniques en cours

#Création du dictionnaire des règles
def createRules(mem, ai, env):
    '''Crée et retourne le dictionnaire de règles du système de décision AI
    indiqué en paramètre. La clé d'une règle dans ce dictionnaire est son nom.
    '''
    rules = {
        RULE_TECHCONT : \
            SudoAIrule(mem, RULE_TECHCONT, fEvalRuleTechCont, ai, env=env), \
        RULE_TECHABORT : \
            SudoAIrule(mem, RULE_TECHABORT, fEvalRuleTechAbort, ai, env=env), \
        RULE_CHRC : \
            SudoAIrule(mem, RULE_CHRC, fEvalRuleChrc, ai, env=env), \
        RULE_LPLC : \
            SudoAIrule(mem, RULE_LPLC, fEvalRuleLplc, ai, env=env), \
        RULE_DISCARD : \
            SudoAIrule(mem, RULE_DISCARD, fEvalRuleDiscard, ai, env=env), \
        RULE_DISCARDALL : \
            SudoAIrule(mem, RULE_DISCARDALL, fEvalRuleDiscardAll, ai, env=env) \
        }
    return rules

## A TESTER : FORME DECLARATIVE
def fEvalRuleTechCont_Test():
    '''Règle de continuation d'une technique en cours.'''
    TEST.display("ai", 3, "SudoAI - dans fEvalRuleTechCont.")
    val = ( \
        (CRIT_INTECH,),     #impératifs
        (CRIT_LASTEND, CRIT_NOTECH),    #exclusifs
        ((CRIT_INTECH, 1),), #contributifs avec facteur
        0)      #valeur par défaut
    return val

#Fonctions d'évaluation des règles
def fEvalRuleTechCont(ai, env):
    '''Règle de continuation d'une technique en cours.'''
    TEST = env.TEST
    TEST.display("ai", 3, "SudoAI - dans fEvalRuleTechCont.")
    assert isinstance(ai, SudoAI)
    crits = ai.crits
    #les critères impératifs (dont l'évaluation DOIT être 1)
    if crits.crit(CRIT_INTECH).val < 1:
        return 0
    #les critères exclusifs (dont l'évaluation DOIT être 0)
    if crits.crit(CRIT_LASTEND).val > 0 \
       or crits.crit(CRIT_NOTECH).val > 0:
        return 0
    #évaluation
    val = 1.0 * crits.crit(CRIT_INTECH).val
    val = min(val, 1.0) #saturation
    return val

def fEvalRuleTechAbort(ai, env):
    '''Règle d'abandon d'une technique en cours. L'abandon n'a plus de sens
    après la fin de la règle, donc la dernière action ne doit pas être "end".
    Dans le système AI actuel, il n'y a aucun critère qui contribue à une
    décision d'abandon.
    '''
    TEST = env.TEST
    TEST.display("ai", 3, "SudoAI - dans fEvalRuleTechAbort.")
    assert isinstance(ai, SudoAI)
#### ACTUELLEMENT REGLE INUTILISEE ##
    return 0
######
##    crits = ai.crits
##    #les critères impératifs (dont l'évaluation DOIT être 1)
##    if crits.crit(CRIT_INTECH).val < 1:
##        return 0
##    #les critères exclusifs (dont l'évaluation DOIT être 0)
##    if crits.crit(CRIT_LASTEND).val > 0 \
##       or crits.crit(CRIT_NOTECH).val > 0:
##        return 0
##    #évaluation
##    val = 0 #actuellement aucun critère n'y contribue.
##    val = min(val, 1.0) #saturation
##    return val
    
def fEvalRuleChrc(ai, env):
    '''Règle de commencement de la technique ChRC dans le système de décision
    indiqué en paramètre.
    ChRC peut être appliquée en alternance avec Lplc et pas deux fois de suite.
    De plus c'est la technique choisie en début de résolution.
    Il faut au préalable qu'il n'y ait aucune technique en cours.
    '''
    TEST = env.TEST
    TEST.display("ai", 3, "SudoAI - dans fEvalRuleChrc()")
    assert isinstance(ai, SudoAI)
    crits = ai.crits
    #critères impératifs (dont l'évaluation DOIT être 1)
    if crits.crit(CRIT_NIV0).val < 1 \
           or crits.crit(CRIT_NOTECH).val < 1:
        return 0
    #critères exclusifs (dont l'évaluation doit être 0)
    if crits.crit(CRIT_LTECHCHRC).val > 0 \
            or crits.crit(CRIT_INTECH).val > 0:
        return 0
    #évaluation
    val = 1.0 * crits.crit(CRIT_BEGIN).val + \
          1.0 * crits.crit(CRIT_LTECHLPLC).val
    val = min(val, 1.0) #saturation
    return val

def fEvalRuleLplc(ai, env):
    '''Règle de commencement de la technique Lplc dans le système de décision
    indiqué en paramètre.
    Lplc peut être appliquée en alternance avec ChRC et pas deux fois de suite.
    Il faut au préalable qu'il n'y ait aucune technique en cours.
    '''
    TEST = env.TEST
    TEST.display("ai", 3, "SudoAI - dans fEvalRuleLplc()")
    assert isinstance(ai, SudoAI)
    crits = ai.crits
    #critères impératifs (dont l'évaluation DOIT être 1)
    if crits.crit(CRIT_NIV0).val < 1 \
       or crits.crit(CRIT_NOTECH).val < 1 :
        return 0
    #critères exclusifs (dont l'évaluation doit être 0)
    if crits.crit(CRIT_LTECHLPLC).val > 0 \
       or crits.crit(CRIT_INTECH).val > 0:
        return 0
    #évaluation
    val = 1.0 * crits.crit(CRIT_LTECHCHRC).val
    val = min(val, 1.0) #saturation
    return val

def fEvalRuleDiscard(ai, env):
    '''Règle de suppression de la technique en cours et deretour au niveau
    d'imbrication inférieur. Cela est possible à tout moment dès lors qu'il
    y a au moins un niveau d'imbrication.
    Dans cette stratégie, le retour se fait dès la fin de la technique
    technique en cours (dernière action = "end") mais dans aucun autre cas.
    '''
    TEST = env.TEST
    TEST.display("ai", 3, "SudoAI - dans fEvalRuleDiscard().")
    assert isinstance(ai, SudoAI)
    crits = ai.crits
    #critères impératifs (dont l'évaluation DOIT être 1)
    if crits.crit(CRIT_INTECH).val < 1 :
        return 0
    #critères exclusifs (dont l'évaluation doit être 0)
    if crits.crit(CRIT_NIV0).val > 0:
        return 0
    #critères contributifs
    val = 1.0 * crits.crit(CRIT_LASTEND).val
    val = min(val, 1.0) #saturation
    return val

def fEvalRuleDiscardAll(ai, env):
    '''Règle de retour direct au niveau 0. Cela est possible à tout moment
    dès lors qu'il y a au moins 2 niveaux d'imbrication. 
    '''
    TEST = env.TEST
    TEST.display("ai", 3, "SudoAI - dans fEvalRuleDiscardAll().")
    assert isinstance(ai, SudoAI)

#### ACTUELLEMENT ON N'UTILISE PAS CETTE REGLE
    return 0
######

    crits = ai.crits
    #critères impératifs (dont l'évaluation DOIT être 1)
    if crits.crit(CRIT_NIV2SUP).val < 1 \
       or crits.crit(CRIT_INTECH).val < 1 :
        return 0
    #critères exclusifs (dont l'évaluation doit être 0)
    if crits.crit(CRIT_NIV1).val < 1 \
       or crits.crit(CRIT_NIV0).val > 0:
        return 0
    #critères contributifs
    val = 1.0 * crits.crit(CRIT_LASTEND).val
    val = min(val, 1.0) #saturation
    return val

#Implémentation des règles : classe de règle et classe d'ensemble des règles
class SudoAIrule(base.SudoBaseClass):
    '''Représente une règle de décision AI, qui associe une valeur et une
    fonction d'évaluation basée sur des critères. Lors de sa création la règle
    n'a pas de valeur. Evaluer la règle se fait en exécutant la fonction. La
    valeur peut être réintialisée, ce qui est fait au début du processus de
    prise de décision AI.
    '''
    def __init__(self, mem, name, funcEval, ai, \
                 env=None, testlevel=sudoenv.TEST_AILEVEL):
        '''Initialisation de la règle. Elle n'a pas de valeur.'''
        #init de la classe racine
        assert isinstance(env, sudoenv.SudoEnv) or env is None
        assert isinstance(testlevel, int) and testlevel>=0 \
                or testlevel is None
        base.SudoBaseClass.__init__(self, env=env, \
                                    testlabel="ai", testlevel=testlevel)
        #ok init de cette classe
        TEST = self.env.TEST
        TEST.display("ai", 3, "SudoAI - dans AIrule.__init__()")
        assert isinstance(mem, SudoMemory)
        self._mem = mem
        assert isinstance(ai, SudoAI)
        self._ai = ai
        self._name = name
        self._func = funcEval
        self._val = None

    def eval(self):
        '''Evalue la règle et retourne sa valeur. Si la fonction d'évaluation
        déclenche une exception, supprime la valeur de la rège et propage
        l'exception.
        '''
        TEST = self.env.TEST
        TEST.display("ai", 3, "SudoAI - dans AIrule.getEval()")
        try:
            self._val = self._func(self._ai, self.env)
        except:
            self._val = None
            raise
        return self._val

    def clear(self):
        '''Réinitialise une règle, c'est-à-dire qu'elle n'a plus de valeur.'''
        TEST = self.env.TEST
        TEST.display("ai", 3, "SudoAI - dans AIrule.setEval()")
        self._val = None

    @property
    def name(self):
        return self._name
    
    @property
    def val(self):
        '''Valeur actuelle de la règle sans réévaluation.'''
        return self._val

    def __str__(self):
        return "Règle de décision \'{0}\'".format(self._name)
    
class SudoAIruleSet(base.SudoBaseClass):
    '''Représente l'ensemble des règles du système de décision AI, dans leur
    état actuel d'évaluation. L'évalution de cet ensemble se fait au début
    du processus de prise de décision AI, elle déclenche l'évaluation de chaque
    règle et indirectement des critères utilisés.
    '''
    def __init__(self, mem, ai, \
                 env=None, testlevel=sudoenv.TEST_AILEVEL):
        '''Crée le dictionnaire de règles.'''
        #init de la classe racine
        assert isinstance(env, sudoenv.SudoEnv) or env is None
        assert isinstance(testlevel, int) and testlevel>=0 \
                or testlevel is None
        base.SudoBaseClass.__init__(self, env=env, \
                                    testlabel="ai", testlevel=testlevel)
        #ok init de cette classe
        TEST = self.env.TEST
        TEST.display("ai", 3, "SudoAI - dans SudoAIruleSet.__init__()")
        TEST.display("ai", 2, "SudoAI - Initialisation de l'ensemble de règles "\
                             "du système de décision AI.")
        assert isinstance(mem, SudoMemory)
        self._mem = mem
        assert isinstance(ai, SudoAI)
        self._ai = ai
        #Création du dictionnaire de règles
        TEST.display("ai", 3, "SudoAIruleSet - Création du dictionnaire de règles.")
        self._rules = createRules(self._mem, self._ai, self.env)
        return

    def add(self, rule):
        '''Ajoute une nouvelle règle. Sa clé dans le dictionnaire est son nom.
        '''
        TEST = self.env.TEST
        TEST.display("ai", 3, "SudoAI - dans AIruleSet.add()")
        assert isinstance(rule, SudoAIrule)
        self._rules[rule.name] = rule
        return
    
    def clear(self):
        '''Efface la valeur de toutes les règles.'''
        TEST = self.env.TEST
        TEST.display("ai", 3, "SudoAI - dans AIruleSet.clear()")
        for rule in self._rules.values():
            rule.clear()
        return

    def rule(self, ruleName):
        '''Retourne l'instance de règle indiquée par son nom, ou déclenche
        une exception s'il n'y a pas de règle de ce nom.
        '''
        TEST = self.env.TEST
        TEST.display("ai", 3, "SudoAI - dans AIruleSet.rule()")
        r = self._rules.get(ruleName, False)
        if r is False:  #erreur, pas de règle de ce nom
            raise Sudoku_Error("Pas de règle nommée {0}".format(ruleName))
        return r

    def ruleEval(self, ruleName):
        '''Retourne la valeur de la règle indiquée par son nom. Au besoin
        fait l'évaluation de la règle. Déclenche une exception s'il n'y a pas
        de règle de ce nom et propage une exception d'évaluation de la règle.
        '''
        TEST = self.env.TEST
        TEST.display("ai", 3, "SudoAI - dans AIruleSet.ruleEval()")
        r = self._rules.get(ruleName, False)
        if r is False:  #erreur, nom de règle inconnu
            raise Sudoku_Error("Pas de règle nommée {0}".format(ruleName))
        return r.eval()

    def evalAll(self):
        '''Evalue toutes les règles.'''
        TEST = self.env.TEST
        TEST.display("ai", 3, "SudoAI - dans AIruleSet.evalAll()")
        for r in self._rules.values():
            r.eval()
        return True

    @property
    def nb(self):
        return len(self._rules)

    @property
    def rules(self):
        return self._rules
    
    def disp(self):
        '''Liste la valeur actuelle de toutes les règles.'''
        for r in self._rules.values():
            ui.display("{0} = {1}" 
                  .format(r.name, r.val))
        return

    def show(self):
        '''Affiche le contenu de s'ensemble de règles.'''
        TEST.display("ai", 3, "SudoAI - dans AIruleSet.show()")
        ui.display("Le système contient {0} règles. Valeurs :" \
                           .format(self.nb))
        self.disp()
        return
        

#TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 
#TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 

if __name__ == "__main__":
    env = sudoenv.SudoEnv()
    TEST = env.TEST
    TEST.test("ai", 3)

    mem = SudoMemory()
    sai = SudoAI(mem, env=env)
    data = sai.data
    
