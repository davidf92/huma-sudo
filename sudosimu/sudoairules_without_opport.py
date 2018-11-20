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
'''

#exécution interne au package
if __name__ in ("__main__", "sudoairules"):
    import sudobaseclass as base
    import sudoenv
    import sudoui as ui
    import sudorules as rules
    from sudorules import Sudoku_Error
    from sudomemory import SudoMemory
    from sudoaiconst import *
#exécution depuis l'extérieur du package sudosimu
elif __name__ == "sudosimu.sudoairules":
    from sudosimu import sudobaseclass as base
    from sudosimu import sudoenv
    from sudosimu import sudoui as ui
    from sudosimu import sudorules as rules
    from sudosimu.sudorules import Sudoku_Error
    from sudosimu.sudomemory import SudoMemory
    from sudosimu.sudoaiconst import *
else:
    raise Exception("Impossible de faire les imports dans le module sudoai.")

    
##DONNEES D'ENTREE DU SYSTEME DE DECISION
##---------------------------------------    
'''Les données d'entrée alimentent le système logique. Elles sont utilisées
pour évaluer des critères de décision, lesquels serviront à leur tour à
l'évaluation de règles. Les données sont fournies au système AI sous la forme
d'un dictionnaire.
En pratique ces données représentent l'état d'avancement de la résolution, et
vont donc servir à décider la prochaine action de cette résolution.
'''
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
        self[AIDATA_BEGIN] = True
        self[AIDATA_NIV] = 0
        self[AIDATA_NIVMAX] = 2
        self[AIDATA_INTECH] = False
        self[AIDATA_OPPORT] = False
        self[AIDATA_TECH] = None
        self[AIDATA_LTECH] = None
        self[AIDATA_LACT] = None
        self[AIDATA_LTECHACT] = None
        self[AIDATA_LAIACT] = None
        self[AIDATA_LNIV1TECH] = None
        self[AIDATA_LOPPTECH] = None
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
#Implémentation des critères : classe de critère et classe de leur ensemble
class SudoAIcritSet(base.SudoBaseClass):
    '''Représente l'ensemble des critères d'évaluation de règles, dans le
    système de décision AI, dans leur état actuel d'évaluation. Les critères
    sont basés sur les données d'état de la résolution en cours.
    L'évalution de cet ensemble se fait au début du processus de prise de
    décision AI, elle déclenche l'évaluation de chaque critère en fonction
    de l'avancement de la résolution.
    '''
    def __init__(self, mem, aidata, \
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
        assert isinstance(aidata, SudoAIdata)
        self._aidata = aidata
        #Création du dictionnaire de critères
        TEST.display("ai", 3, "SudoAIruleSet - Création du dictionnaire "\
                              "de critères.")
        self._crits = createCriteria(self._mem, aidata, self.env)
        return

    def add(self, crit):
        '''Ajoute une nouvelle règle. Sa clé dans le dictionnaire est son nom.
        '''
        TEST = self.env.TEST
        TEST.display("ai", 3, "SudoAI - dans SudoAIcritSet.add()")
        assert isinstance(crit, SudoAIcrit)
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
        TEST.display("ai", 2, "Evaluation de l'ensemble des critères AI")
        for cr in self._crits.values():
            cr.eval()
        return True

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

    @property
    def nb(self):
        return len(self._crits)
    @property
    def crits(self):
        return self._crits


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
        TEST.display("ai", 4, "SudoAI - dans SudoAIcrit.eval() -" \
                     "Evaluation du critère \'{0}\'.".format(self._name))
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

#Création du dictionnaire des critères
def createCriteria(mem, data, env):
    '''Crée et retourne un dictionnaire des critères d'analyse AI.'''
    crits = {
        AICRIT_BEGIN : \
            SudoAIcrit(mem, AICRIT_BEGIN, fEvalAIcritBegin, data, env=env), \
        AICRIT_NIV0 : \
            SudoAIcrit(mem, AICRIT_NIV0, fEvalAIcritNiv0, data, env=env), \
        AICRIT_NIV1 : \
            SudoAIcrit(mem, AICRIT_NIV1, fEvalAIcritNiv1, data, env=env), \
        AICRIT_NIV2SUP : \
            SudoAIcrit(mem, AICRIT_NIV2SUP, fEvalAIcritNiv2Sup, data, env=env), \
        AICRIT_NIVMAX : \
            SudoAIcrit(mem, AICRIT_NIVMAX, fEvalAIcritNivMax, data, env=env), \
        AICRIT_INTECH : \
            SudoAIcrit(mem, AICRIT_INTECH, fEvalAIcritInTech, data, env=env), \
        AICRIT_NOTECH : \
            SudoAIcrit(mem, AICRIT_NOTECH, fEvalAIcritNoTech, data, env=env), \
        AICRIT_CANTAKEOPP : \
            SudoAIcrit(mem, AICRIT_CANTAKEOPP, fEvalAIcritCanTakeOpp, data, env=env), \
        AICRIT_FIRSTOPP : \
            SudoAIcrit(mem, AICRIT_FIRSTOPP, fEvalAIcritFirstOpp, data, env=env), \
        AICRIT_INOPPORT : \
            SudoAIcrit(mem, AICRIT_INOPPORT, fEvalAIcritInOpport, data, env=env), \
        AICRIT_INOPPSEQ : \
            SudoAIcrit(mem, AICRIT_INOPPSEQ, fEvalAIcritInOppSeq, data, env=env), \
        AICRIT_INTECHCHRCGA : \
            SudoAIcrit(mem, AICRIT_INTECHCHRCGA, fEvalAIcritInTechChrcga, data, env=env), \
        AICRIT_INTECHLPLCG : \
            SudoAIcrit(mem, AICRIT_INTECHLPLCG, fEvalAIcritInTechLplcg, data, env=env), \
        AICRIT_INTECHLPLCP : \
            SudoAIcrit(mem, AICRIT_INTECHLPLCP, fEvalAIcritInTechLplcp, data, env=env), \
        AICRIT_LTECHCHRCGA : \
            SudoAIcrit(mem, AICRIT_LTECHCHRCGA, fEvalAIcritLastTechChrcga, data, env=env), \
        AICRIT_LTECHLPLCG : \
            SudoAIcrit(mem, AICRIT_LTECHLPLCG, fEvalAIcritLastTechLplcg, data, env=env), \
        AICRIT_LTECHLPLCP : \
            SudoAIcrit(mem, AICRIT_LTECHLPLCP, fEvalAIcritLastTechLplcp, data, env=env), \
        AICRIT_LTECHNONE : \
            SudoAIcrit(mem, AICRIT_LTECHNONE, fEvalAIcritLastTechNone, data, env=env), \
        AICRIT_LASTACTPLACE : \
            SudoAIcrit(mem, AICRIT_LASTACTPLACE, fEvalAIcritLastActionPlace, data, env=env), \
        AICRIT_LASTACTEND : \
            SudoAIcrit(mem, AICRIT_LASTACTEND, fEvalAIcritLastActionEnd, data, env=env) \
        }
    return crits
        
#Fonctions d'évaluation des critères (sont implémentées comme fonctions du
#module mais pourraient aussi être des méthodes de classe de SudoAIcrit)
def fEvalAIcritBegin(data):
    '''Retourne 1 si la résolution commence.'''
    return (1 if data.get(AIDATA_BEGIN) is True else 0)

def fEvalAIcritNiv0(data):
    '''Retourne 1 si le niveau d'exécution est 0.'''
    return (1 if data.get(AIDATA_NIV) == 0 else 0)

def fEvalAIcritNiv1(data):
    '''Retourne 1 si le niveau d'exécution est 1.'''
    return (1 if data.get(AIDATA_NIV) == 1 else 0)

def fEvalAIcritNiv2Sup(data):
    '''Retourne 1 si le niveau d'exécution est 2 ou plus.'''
    return (1 if data.get(AIDATA_NIV) >= 2 else 0)

def fEvalAIcritNivMax(data):
    '''Retourne 1 si le niveau d'exécution est le niveau maximum ou plus.'''
    return (1 if data.get(AIDATA_NIV) >= data.get(AIDATA_NIVMAX) else 0)

def fEvalAIcritInTech(data):
    '''Retourne 1 si une technique est en cours.'''
    return (1 if data.get(AIDATA_INTECH) is True else 0)

def fEvalAIcritNoTech(data):
    '''Retourne 1 si aucune technique n'est en cours.'''
    return (1 if data.get(AIDATA_INTECH) is not True else 0)

def fEvalAIcritCanTakeOpp(data):
    '''Retourne 1 si une technique d'opportunité est possible.'''
    return (1 if data.get(AIDATA_NIV) >= 1 and data.get(AIDATA_LACT) =="place" \
            else 0)

def fEvalAIcritFirstOpp(data):
    '''Retourne 1 si c'est la première technique de ce niveau d'opportunité.'''
    return (1 if data.get(AIDATA_LTECH) is None else 0)

def fEvalAIcritInOpport(data):
    '''Retourne 1 si une technique d'opportunité est en cours.'''
    return (1 if data.get(AIDATA_OPPORT) is True else 0)

def fEvalAIcritInOppSeq(data):
    '''Retourne 1 si une technique d'opportunité est en cours.'''
    #Inutilisée pour le moment
    return 0

def fEvalAIcritInTechChrcga(data):
    '''Retourne 1 si la technique en cours est CHRC.'''
    return (1 if data.get(AIDATA_INTECH) is True \
                 and data.get(AIDATA_TECH) == "techchrcga" \
            else 0)

def fEvalAIcritInTechLplcg(data):
    '''Retourne 1 si la technique en cours est LPLC.'''
    return (1 if data.get(AIDATA_INTECH) is True \
                 and data.get(AIDATA_TECH) == "techlplcg" else 0)

def fEvalAIcritInTechLplcp(data):
    '''Retourne 1 si la technique en cours est LPLC.'''
    return (1 if data.get(AIDATA_INTECH) is True \
                 and data.get(AIDATA_TECH) == "techlplcp" else 0)

def fEvalAIcritLastTechChrcga(data):
    '''Retourne 1 si la dernière technique appliquée est ChRC.'''
    return (1 if data.get(AIDATA_LTECH) == "techchrcga" else 0)

def fEvalAIcritLastTechLplcg(data):
    '''Retourne 1 si la dernière technique appliquée est Lplc'''
    return (1 if data.get(AIDATA_LTECH) == "techlplcg" else 0)

def fEvalAIcritLastTechLplcp(data):
    '''Retourne 1 si la dernière technique appliquée est LastPlcp.'''
    return (1 if data.get(AIDATA_LTECH) == "techlplcp" else 0)

def fEvalAIcritLastTechNone(data):
    '''Retourne 1 si la dernière technique appliquée est absente (none).'''
    return (1 if data.get(AIDATA_LTECH) is None else 0)

def fEvalAIcritLastActionPlace(data):
    '''Retourne 1 si la dernière action de pensée dans l'exécution d'une
    technique est 'place'.
    '''
    return (1 if data.get(AIDATA_LACT) == "place" else 0)

def fEvalAIcritLastActionEnd(data):
    '''Retourne 1 si la dernière action de pensée dans l'exploration AI
    est 'end'.
    '''
    return (1 if data.get(AIDATA_LACT) == "end" else 0)


##GESTION DES REGLES DU SYSTEME DE DECISION
##-----------------------------------------
'''Les règles AI sont des évaluations logiques calculées avec les critères AI.
Elles représentent les bases de décision, par exemple les actions possibles.
Une règle associe une valeur et une fonction de calcul de cette valeur.
'''
#Implémentation des règles : classe d'ensemble des règles et classe de règle
class SudoAIruleSet(base.SudoBaseClass):
    '''Représente l'ensemble des règles du système de décision AI, dans leur
    état actuel d'évaluation. L'évalution de cet ensemble se fait au début
    du processus de prise de décision AI, elle déclenche l'évaluation de chaque
    règle et indirectement des critères utilisés.
    '''
    def __init__(self, mem, aicrits, \
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
        assert isinstance(aicrits, SudoAIcritSet)
        self._aicrits = aicrits
        #Création du dictionnaire de règles
        TEST.display("ai", 3, "SudoAIruleSet - Création du dictionnaire de règles.")
        self._rules = createRules(self._mem, self._aicrits, self.env)
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

    def disp(self):
        '''Liste la valeur actuelle de toutes les règles.'''
        for r in self._rules.values():
            ui.display("{0} = {1}" 
                  .format(r.name, r.val))
        return

    def show(self):
        '''Affiche le contenu de s'ensemble de règles.'''
        TEST = self.env.TEST
        TEST.display("ai", 3, "SudoAI - dans AIruleSet.show()")
        ui.display("Le système contient {0} règles. Valeurs :" \
                           .format(self.nb))
        self.disp()
        return
        
    @property
    def nb(self):
        return len(self._rules)

    @property
    def rules(self):
        return self._rules

    @property
    def crits(self):
        return self._aicrits
    

class SudoAIrule(base.SudoBaseClass):
    '''Représente une règle de décision AI, qui associe une valeur et une
    fonction d'évaluation basée sur des critères. Lors de sa création la règle
    n'a pas de valeur. Evaluer la règle se fait en exécutant la fonction. La
    valeur peut être réintialisée, ce qui est fait au début du processus de
    prise de décision AI.
    '''
    def __init__(self, mem, name, funcEval, aicrits, \
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
        assert isinstance(aicrits, SudoAIcritSet)
        self._aicrits = aicrits
        self._name = name
        self._func = funcEval
        self._val = None

    def eval(self):
        '''Evalue la règle et retourne sa valeur. Si la fonction d'évaluation
        déclenche une exception, supprime la valeur de la rège et propage
        l'exception.
        '''
        TEST = self.env.TEST
        TEST.display("ai", 4, "SudoAI - dans AIrule.getEval()")
        try:
            self._val = self._func(self._aicrits, self.env)
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
    def crits(self):
        return self._aicrits
    
    @property
    def val(self):
        '''Valeur actuelle de la règle sans réévaluation.'''
        return self._val

    def __str__(self):
        return "Règle de décision \'{0}\'".format(self._name)
    
#Création du dictionnaire des règles
def createRules(mem, crits, env):
    '''Crée et retourne le dictionnaire de règles du système de décision AI
    indiqué en paramètre. La clé d'une règle dans ce dictionnaire est son nom.
    '''
    rules = {
        AIRULE_TECHCONT : \
            SudoAIrule(mem, AIRULE_TECHCONT, fEvalAIruleTechCont, crits, env=env), \
        AIRULE_TECHABORT : \
            SudoAIrule(mem, AIRULE_TECHABORT, fEvalAIruleTechAbort, crits, env=env), \
        AIRULE_CHRCGA : \
            SudoAIrule(mem, AIRULE_CHRCGA, fEvalAIruleChrcga, crits, env=env), \
        AIRULE_LPLCG : \
            SudoAIrule(mem, AIRULE_LPLCG, fEvalAIruleLplcg, crits, env=env), \
        AIRULE_LPLCP : \
            SudoAIrule(mem, AIRULE_LPLCP, fEvalAIruleLplcp, crits, env=env), \
        AIRULE_DISCARD : \
            SudoAIrule(mem, AIRULE_DISCARD, fEvalAIruleDiscard, crits, env=env), \
        AIRULE_DISCARDALL : \
            SudoAIrule(mem, AIRULE_DISCARDALL, fEvalAIruleDiscardAll, crits, env=env) \
        }
    return rules

#Fonctions d'évaluation des règles(sont implémentées comme fonctions du
#module mais pourraient aussi être des méthodes de classe de SudoAIrule)

## A TESTER : FORME DECLARATIVE
def fEvalAIruleTechCont_Test():
    '''Règle de continuation d'une technique en cours.'''
    TEST.display("ai", 3, "SudoAI - dans fEvalAIruleTechCont.")
    val = ( \
        (AICRIT_INTECH,),     #impératifs
        (AICRIT_LASTACTEND, AICRIT_NOTECH),    #exclusifs
        ((AICRIT_INTECH, 1),), #contributifs avec facteur
        0)      #valeur par défaut
    return val

def fEvalAIruleTechCont(crits, env):
    '''Règle de continuation d'une technique en cours.'''
    TEST = env.TEST
    TEST.display("ai", 3, "SudoAI - dans fEvalAIruleTechCont.")
    assert isinstance(crits, SudoAIcritSet)
    #les critères impératifs (dont l'évaluation DOIT être 1)
    if crits.crit(AICRIT_INTECH).val == 0:
        return 0
    #les critères exclusifs (dont l'évaluation DOIT être 0)
    if crits.crit(AICRIT_LASTACTEND).val > 0 \
       or crits.crit(AICRIT_NOTECH).val > 0:
        return 0
    #évaluation
    val = 1.0 * crits.crit(AICRIT_INTECH).val
    val = min(val, 1.0) #saturation
    TEST.display("ai", 2, "AI - Règle AIRULE_TECHCONT : valeur = %i" % (val))
    return val

def fEvalAIruleTechAbort(crits, env):
    '''Règle d'abandon d'une technique en cours. L'abandon n'a plus de sens
    après la fin de la règle, donc la dernière action ne doit pas être "end".
    Dans le système AI actuel, il n'y a aucun critère qui contribue à une
    décision d'abandon.
    '''
    TEST = env.TEST
    TEST.display("ai", 3, "SudoAI - dans fEvalAIruleTechAbort.")
    assert isinstance(crits, SudoAIcritSet)
#### ACTUELLEMENT REGLE INUTILISEE ##
    TEST.display("ai", 2, "AI - Règle AIRULE_TECHABORT : valeur = %i" % (0))
    return 0
######
##    crits = ai.crits
##    #les critères impératifs (dont l'évaluation DOIT être 1)
##    if crits.crit(AICRIT_INTECH).val < 1:
##        return 0
##    #les critères exclusifs (dont l'évaluation DOIT être 0)
##    if crits.crit(AICRIT_LASTACTEND).val > 0 \
##       or crits.crit(AICRIT_NOTECH).val > 0:
##        return 0
##    #évaluation
##    val = 0 #actuellement aucun critère n'y contribue.
##    val = min(val, 1.0) #saturation
##    TEST.display("ai", 2, "AI - Règle AIRULE_TECHABORT : valeur = %i" % (val))
##    return val
    
def fEvalAIruleChrcga(crits, env):
    '''Règle de commencement de la technique globale ChRCga.
    ChRCga peut être appliquée au premier niveau en alternance avec Lplcg,
    mais pas deux fois consécutives. De plus c'est la technique choisie en
    début de résolution.
    Il faut au préalable qu'il n'y ait aucune technique en cours.
    '''
    TEST = env.TEST
    TEST.display("ai", 3, "SudoAI - dans fEvalAIruleChrcga()")
    assert isinstance(crits, SudoAIcritSet)
    #critères impératifs (dont l'évaluation DOIT être 1)
    if crits.crit(AICRIT_NIV0).val == 0 \
           or crits.crit(AICRIT_NOTECH).val == 0 :
        return 0
    #critères exclusifs (dont l'évaluation doit être 0)
    if crits.crit(AICRIT_LTECHCHRCGA).val > 0 \
            or crits.crit(AICRIT_INTECH).val > 0:
        return 0
    #évaluation
    val = 1.0 * crits.crit(AICRIT_BEGIN).val + \
          1.0 * crits.crit(AICRIT_LTECHLPLCG).val
    val = min(val, 1.0) #saturation
    TEST.display("ai", 2, "AI - Règle AIRULE_CHRCGA : valeur = %i" % (val))
    return val

def fEvalAIruleLplcg(crits, env):
    '''Règle de commencement de la technique Lplcg.
    Lplcg peut être appliquée au premier niveau en alternance avec ChRCga,
    mais pas deux fois consécutives.
    Il faut au préalable qu'il n'y ait aucune technique en cours.
    '''
    TEST = env.TEST
    TEST.display("ai", 3, "SudoAI - dans fEvalAIruleLplcg()")
    assert isinstance(crits, SudoAIcritSet)
    #critères impératifs (dont l'évaluation DOIT être 1)
    if crits.crit(AICRIT_NIV0).val == 0 \
       or crits.crit(AICRIT_NOTECH).val == 0 :
        return 0
    #critères exclusifs (dont l'évaluation doit être 0)
    if crits.crit(AICRIT_LTECHLPLCG).val > 0 \
       or crits.crit(AICRIT_INTECH).val > 0:
        return 0
    #évaluation
    val = 1.0 * crits.crit(AICRIT_LTECHCHRCGA).val
    val = min(val, 1.0) #saturation
    TEST.display("ai", 2, "AI - Règle AIRULE_LPLCG: valeur = %i" % (val))
    return val

def fEvalAIruleLplcp(crits, env):
    '''Règle de commencement de la technique locale Lplcp.
    Lplc peut être appliquée en première technique de recherche d'opportunité,
    juste après un placement. Il doit donc y avoir une technique en cours. Mais
    elle n'est pas appliquée deux fois de suite.
    '''
    TEST = env.TEST
    TEST.display("ai", 3, "SudoAI - dans fEvalAIruleLplcp()")
    assert isinstance(crits, SudoAIcritSet)
    
#### REPRENDRE ICI
## Règle non utilisée dans l'immédiat => retourne 0
    TEST.display("ai", 2, "AI - Règle AIRULE_LPLCP : valeur = %i" % (0))
    return 0

##################
##    #critères impératifs (dont l'évaluation DOIT être 1)
##    if crits.crit(AICRIT_NIV1).val == 0 \
##       or crits.crit(AICRIT_INTECH).val == 0 :
##        return 0
##    #critères exclusifs (dont l'évaluation doit être 0)
##    if crits.crit(AICRIT_LTECHLPLCP).val > 0 \
##       or crits.crit(AICRIT_NOTECH).val > 0 :
##        return 0
##    #évaluation
##    val = 1.0 * crits.crit(AICRIT_LASTACTPLACE).val + \
##          1.0 * crits.crit(AICRIT_LTECHNONE).val
##    val = min(val, 1.0) #saturation
##    TEST.display("ai", 2, "AI - Règle AIRULE_LPLCP : valeur = %i" % (val))
##    return val

def fEvalAIruleDiscard(crits, env):
    '''Règle de suppression de la technique en cours et deretour au niveau
    d'imbrication inférieur. Cela est possible à tout moment dès lors qu'il
    y a au moins un niveau d'imbrication.
    Dans cette stratégie, le retour se fait dès la fin de la technique
    technique en cours (dernière action = "end") mais dans aucun autre cas.
    '''
    TEST = env.TEST
    TEST.display("ai", 3, "SudoAI - dans fEvalAIruleDiscard().")
    assert isinstance(crits, SudoAIcritSet)
    #critères impératifs (dont l'évaluation DOIT être 1)
    if crits.crit(AICRIT_INTECH).val == 0 :
        return 0
    #critères exclusifs (dont l'évaluation doit être 0)
    if crits.crit(AICRIT_NIV0).val > 0:
        return 0
    #critères contributifs
    val = 1.0 * crits.crit(AICRIT_LASTACTEND).val
    val = min(val, 1.0) #saturation
    TEST.display("ai", 2, "AI - Règle AIRULE_DISCARD : valeur = %i" % (val))
    return val

def fEvalAIruleDiscardAll(crits, env):
    '''Règle de retour direct au niveau 0. Cela est possible à tout moment
    dès lors qu'il y a au moins 2 niveaux d'imbrication. 
    '''
    TEST = env.TEST
    TEST.display("ai", 3, "SudoAI - dans fEvalAIruleDiscardAll().")
    assert isinstance(crits, SudoAIcritSet)

#### ACTUELLEMENT ON N'UTILISE PAS CETTE REGLE
    val = 0
    TEST.display("ai", 2, "AI - Règle AIRULE_DISCARDALL : valeur = %i" % (val))
    return val
######
    #critères impératifs (dont l'évaluation DOIT être 1)
    if crits.crit(AICRIT_NIV2SUP).val == 0 \
       or crits.crit(AICRIT_INTECH).val == 0 :
        return 0
    #critères exclusifs (dont l'évaluation doit être 0)
    if crits.crit(AICRIT_NIV0).val > 0 :
        return 0
    #critères contributifs
    val = 1.0 * crits.crit(AICRIT_LASTACTEND).val
    val = min(val, 1.0) #saturation
    TEST.display("ai", 2, "AI - Règle AIRULE_DISCARDALL : valeur = %i" % (val))
    return val


#TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 
#TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 

if __name__ == "__main__":
    env = sudoenv.SudoEnv()
    TEST = env.TEST
    TEST.test("ai", 3)
    mem = SudoMemory()
    dataSet = SudoAIdata(mem, env=env)
    critSet = SudoAIcritSet(mem, dataSet, env=env)
    ruleSet = SudoAIruleSet(mem, critSet, env=env)
