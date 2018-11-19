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

    #temporaire
    from sudotest import *
    
#exécution depuis l'extérieur du package sudosimu
elif __name__ == "sudosimu.sudoai":
    from sudosimu import sudobaseclass as base
    from sudosimu import sudoenv
    from sudosimu import sudoui as ui
    from sudosimu import sudorules as rules
    from sudosimu.sudorules import Sudoku_Error
    from sudosimu.sudomemory import SudoMemory

    #temporaire
    from sudosimu.sudotest import *
    
else:
    raise Exception("Impossible de faire les imports dans le module sudoai.")

class SudoAI():
    '''SudoAI contient le système de décision pour la résolution. Celui-ci est
    implémenté sous forme de programmation logique, avec des critères et des
    règles, dont l'évaluation permet de prendre une décision : choisir une
    technique à appliquer, la commencer, la continuer ou l'interrompre, chercher
    une opportunité après un placement, etc.
    '''
    
    def __init__(self):
        '''Initialisation du système de décision.'''
        #données d'entrée
        self._data = None
        #création de l'ensemble des règles et critères
        self._crits = SudoAIcritSet(self)
        self._rules = SudoAIruleSet(self)
        #évaluation initiale des critères et règles
        self.update()
        #pile de techniques en cours
        self._initTechPile()

    def update(self, data):
        '''Met à jour les évaluations des critères et règles avec les données
        fournies. Celles-ci sont contenues dans un dictionnaire.
        '''
        assert isinstance(data, dict)
        self._data = data
        self._crits.evalAll(data)
        self._rules.evalAll()
        
    @property
    def rules(self):
        return self._rules

    @property
    def crits(self):
        return self._crits

    def show(self):
        '''Affiche toutes les valeurs du système de décision AI.'''
        self._crits.show()
        self._rules.show()

    ##gestion de la pile de techniques en cours
    def _techPileInit(self):
        '''Crée la pile initialement vide.'''
        self._level = 0
        self._techpile = list()

    def _techPilePush(self, tech):
        self._techpile.append(tech)
        self._level +=1

    def _techPilePop(self):
        try:
            self._techpile.pop()
        except IndexError:
            raise Sudoku_Error("SudoAI : erreur de dépilement de la pile "\
                               "des techniques en cours.")
        self._level -= 1    

##DONNEES D'ENTREE DU SYSTEME DE DECISION
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
DATA_LTECHACT = "data_ltechact"     #dernière action d'une technique
DATA_LAIACT = "data_laiact"         #dernière action du système AI


###### TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST
## Les informations utilisées sont fictives pour les tests, elles ne font
## pas partie du programme SudoSimu réel.
## Le paramètre 'ai' des fonctions est donc présent mais inutilisé.

#Situation représentée : niveau 0 après la fin de la technique ChRC
ai_begin = False
ai_niv = 0 #niveau de départ
ai_nivmax = 2
ai_intech = False
ai_tech = None
ai_ltech = "techchrc"
ai_opport = False
ai_lact = "end"
###### TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST

        
##GESTION DES CRITERES DU SYSTEME DE DECISION
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

#Création du dictionnaire des critères
def createCriteria(ai):
    '''Crée et retourne un dictionnaire des critères d'analyse AI.'''
    crits = {
        CRIT_BEGIN : SudoAIcrit(CRIT_BEGIN, fEvalCritBegin, ai), \
        CRIT_NIV0 : SudoAIcrit(CRIT_NIV0, fEvalCritNiv0, ai), \
        CRIT_NIV1 : SudoAIcrit(CRIT_NIV1, fEvalCritNiv1, ai), \
        CRIT_NIV2SUP : SudoAIcrit(CRIT_NIV2SUP, fEvalCritNiv2Sup, ai), \
        CRIT_NIVMAX : SudoAIcrit(CRIT_NIVMAX, fEvalCritNivMax, ai), \
        CRIT_INTECH : SudoAIcrit(CRIT_INTECH, fEvalCritInTech, ai), \
        CRIT_NOTECH : SudoAIcrit(CRIT_NOTECH, fEvalCritNoTech, ai), \
        CRIT_INOPPORT : SudoAIcrit(CRIT_INOPPORT, fEvalCritInOpport, ai), \
        CRIT_INTECHCHRC : SudoAIcrit(CRIT_INTECHCHRC, fEvalCritInTechChrc, ai), \
        CRIT_INTECHLPLC : SudoAIcrit(CRIT_INTECHLPLC, fEvalCritInTechLplc, ai), \
        CRIT_LTECHCHRC : SudoAIcrit(CRIT_LTECHCHRC, fEvalCritLastTechChrc, ai), \
        CRIT_LTECHLPLC : SudoAIcrit(CRIT_LTECHLPLC, fEvalCritLastTechLplc, ai), \
        CRIT_LASTPLACE : SudoAIcrit(CRIT_LASTPLACE, fEvalCritLastActionPlace, ai), \
        CRIT_LASTEND : SudoAIcrit(CRIT_LASTEND, fEvalCritLastActionEnd, ai) \
        }
    return crits

        
#Fonctions d'évaluation des critères
def fEvalCritBegin(data):
    '''Retourne 1 si la résolution commence.'''
    return (1 if ai_begin is True else 0)

def fEvalCritNiv0(data):
    '''Retourne 1 si le niveau d'exécution est 0.'''
    #return (1 if data.get(DATA_NIV) == 0 else 0)
    return (1 if ai_niv == 0 else 0)

def fEvalCritNiv1(data):
    '''Retourne 1 si le niveau d'exécution est 1.'''
    return (1 if ai_niv == 1 else 0)

def fEvalCritNiv2Sup(data):
    '''Retourne 1 si le niveau d'exécution est 2 ou plus.'''
    return (1 if ai_niv >= 2 else 0)

def fEvalCritNivMax(data):
    '''Retourne 1 si le niveau d'exécution est le niveau maximum.'''
    return (1 if ai_niv == ai_nivmax else 0)

def fEvalCritInTech(data):
    '''Retourne 1 si une technique est en cours.'''
    return (1 if ai_intech is True else 0)

def fEvalCritNoTech(data):
    '''Retourne 1 si aucune technique n'est en cours.'''
    return (1 if ai_intech is not True else 0)

def fEvalCritInOpport(data):
    '''Retourne 1 si une technique d'opportunité est en cours.'''
    return (1 if ai_opport is True else 0)

def fEvalCritInTechChrc(ai):
    '''Retourne 1 si la technique en cours est CHRC.'''
    return (1 if ai_intech is True and ai_tech == "techchrc" else 0)

def fEvalCritInTechLplc(data):
    '''Retourne 1 si la technique en cours est LPLC.'''
    return (1 if ai_intech is True and ai_tech == "techlplc" else 0)

def fEvalCritLastTechChrc(data):
    '''Retourne 1 si la dernière technique appliquée est CHRC.'''
    return (1 if ai_ltech == "techchrc" else 0)

def fEvalCritLastTechLplc(data):
    '''Retourne 1 si la dernière technique appliquée est LPLC.'''
    return (1 if ai_ltech == "techlplc" else 0)

def fEvalCritLastActionPlace(data):
    '''Retourne 1 si la dernière action de pensée est 'place'.'''
    return (1 if ai_lact == "place" else 0)

def fEvalCritLastActionEnd(data):
    '''Retourne 1 si la dernière action de pensée est 'end'.'''
    return (1 if ai_lact == "end" else 0)

#Implémentation des critères : classe de critère et classe de leur ensemble
class SudoAIcrit():
    '''Représente un critère de décision dans un système AI, qui associe une
    valeur et une fonction d'évaluation basée sur des informations du système.
    Evaluer le critère se fait en exécutant la fonction. La valeur peut être
    réintialisée, ce qui est réalisé au début du processus de prise de décision.
    '''
    def __init__(self, name, funcEval, ai):
        '''Initialisation de la règle. Elle n'a pas de valeur.'''
        TEST.display("ai", 3, "SudoAI - dans AIcrit.__init__()")
        assert isinstance(ai, SudoAI)
        self._ai = ai
        self._name = name
        self._func = funcEval
        self._val = None

    def eval(self):
        '''Evalue le critère et retourne sa valeur. Un critère peut toujours
        être évaluée. Si la fonction d'évaluation échoue alors le critère
        n'a plus de valeur.
        '''
        TEST.display("ai", 3, "SudoAI - dans AIrule.getEval()")
        try:
            self._val = self._func(self._ai)
        except:
            self._val = None
            raise
        return self._val

    def clear(self):
        '''Réinitialise le critère, c'est-à-dire qu'il n'a plus de valeur.'''
        TEST.display("ai", 3, "SudoAI - dans AIrule.setEval()")
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


class SudoAIcritSet():
    '''Représente l'ensemble des règles du système de décision AI, dans leur
    état actuel d'évaluation. L'évalution de cet ensemble se fait au début
    du processus de prise de décision AI, elle déclenche l'évaluation de chaque
    règle et indirectement des critères utilisés.
    '''
    def __init__(self, ai):
        '''Crée le dictionnaire de règles.'''
        assert isinstance(ai, SudoAI)
        self._ai = ai
        self._crits = createCriteria(ai)
        return

    def add(self, crit):
        '''Ajoute une nouvelle règle. Sa clé dans le dictionnaire est son nom.
        '''
        assert isinstance(crit, AIcrit)
        self._crits[crit.name] = crit
        return
    
    def clear(self):
        '''Efface la valeur de tous les critères.'''
        for crit in self._crits.values():
            crit.clear()
        return

    def crit(self, critName):
        '''Retourne l'instance de critère indiqué par son nom, ou déclenche
        une exception s'il n'y a pas de critère de ce nom.
        '''
        cr = self._crits.get(critName, False)
        if cr is False:  #erreur, pas de critère de ce nom
            raise Sudoku_Error("Pas de critère nommée {0}".format(critName))
        return cr

    def critEval(self, critName):
        '''Retourne la valeur du critère indiqué par son nom. Au besoin
        fait l'évaluation de ce critère. Retourne False s'il n'y a pas de
        critère du nom indiqué. Propage une éventuelle exception.
        '''
        cr = self._crits.get(critName, False)
        if cr is False:      #inconnu dans le dictionnaire
            raise Sudoku_Error("Pas de critère nommée {0}".format(critName))
        return cr.eval()

    def evalAll(self):
        '''Evalue tous les critères. Retourne toujours True.'''
        for cr in self._crits.values():
            cr.eval()
        return True

    def show(self):
        '''Liste la valeur actuelle de tous les critères.'''
        ui.display("Evaluation des critères : ")
        for cr in self._crits.values():
            ui.display("{0} : {1}" 
                  .format(cr.name, cr.val))
        return


##GESTION DES REGLES DU SYSTEME DE DECISION
'''Les règles AI sont des évaluations logiques calculées avec les critères AI.
Elles représentent les bases de décision, par exemple les actions possibles.
Une règle associe une valeur et une fonction de calcul de cette valeur.
'''

#Noms des règles
RULE_TECHCONT = "rule_techcont"     #continuer la technique en cours
RULE_TECHABORT = "rule_techabort"   #abandonner la technique en cours
RULE_CHRC = "rule_chrc"             #commencer la technique Chrc (niv1)
RULE_LPLC = "rule_lplc"             #commerncer la technique Lplc (niv1)
RULE_DECNIV = "rule_decniv"         #revenir un niveau en dessous
RULE_RETNIV0 = "rule_niv0"          #revenir au niveau d'exécution 0

#Création du dictionnaire des règles
def createRules(ai):
    '''Crée et retourne le dictionnaire de règles du système de décision AI
    indiqué en paramètre. La clé d'une règle dans ce dictionnaire est son nom.
    '''
    rules = {
        RULE_TECHCONT : SudoAIrule(RULE_TECHCONT, fEvalRuleTechCont, ai), \
        RULE_TECHABORT : SudoAIrule(RULE_TECHABORT, fEvalRuleTechAbort, ai), \
        RULE_CHRC : SudoAIrule(RULE_CHRC, fEvalRuleChrc, ai), \
        RULE_LPLC : SudoAIrule(RULE_LPLC, fEvalRuleLplc, ai), \
        RULE_DECNIV : SudoAIrule(RULE_DECNIV, fEvalRuleDecNiv, ai), \
        RULE_RETNIV0 : SudoAIrule(RULE_RETNIV0, fEvalRuleRetNiv0, ai) \
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
def fEvalRuleTechCont(ai):
    '''Règle de continuation d'une technique en cours.'''
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

def fEvalRuleTechAbort(ai):
    '''Règle d'abandon d'une technique en cours. L'abandon n'a plus de sens
    après la fin de la règle, donc la dernière action ne doit pas être "end".
    Dans le système AI actuel, il n'y a aucun critère qui contribue à une
    décision d'abandon.
    '''
    TEST.display("ai", 3, "SudoAI - dans fEvalRuleTechAbort.")
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
    val = 0 #actuellement aucun critère n'y contribue.
    val = min(val, 1.0) #saturation
    return val
    
def fEvalRuleChrc(ai):
    '''Règle de commencement de la technique ChRC dans le système de décision
    indiqué en paramètre.
    ChRC peut être appliquée en alternance avec Lplc et pas deux fois de suite.
    De plus c'est la technique choisie en début de résolution.
    Il faut au préalable qu'il n'y ait aucune technique en cours.
    '''
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

def fEvalRuleLplc(ai):
    '''Règle de commencement de la technique Lplc dans le système de décision
    indiqué en paramètre.
    Lplc peut être appliquée en alternance avec ChRC et pas deux fois de suite.
    Il faut au préalable qu'il n'y ait aucune technique en cours.
    '''
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

def fEvalRuleDecNiv(ai):
    '''Règle de retour au niveau inférieur. Cela est possible à tout moment
    dès lors qu'il y a au moins un niveau d'imbrication.
    Dans cette stratégie, le retour ne se fait qu'à la fin de la technique
    technique en cours.
    '''
    TEST.display("ai", 3, "SudoAI - dans fEvalRuleDecNiv().")
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

def fEvalRuleRetNiv0(ai):
    '''Règle de retour direct au niveau 0. Cela est possible à tout moment
    dès lors qu'il y a au moins 2 niveaux d'imbrication. 
    '''
    TEST.display("ai", 3, "SudoAI - dans fEvalRuleRetNiv0().")
    assert isinstance(ai, SudoAI)
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
class SudoAIrule():
    '''Représente une règle de décision AI, qui associe une valeur et une
    fonction d'évaluation basée sur des critères. Lors de sa création la règle
    n'a pas de valeur. Evaluer la règle se fait en exécutant la fonction. La
    valeur peut être réintialisée, ce qui est fait au début du processus de
    prise de décision AI.
    '''
    def __init__(self, name, funcEval, ai):
        '''Initialisation de la règle. Elle n'a pas de valeur.'''
        TEST.display("ai", 3, "SudoAI - dans AIrule.__init__()")
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
        TEST.display("ai", 3, "SudoAI - dans AIrule.getEval()")
        try:
            self._val = self._func(self._ai)
        except:
            self._val = None
            raise
        return self._val

    def clear(self):
        '''Réinitialise une règle, c'est-à-dire qu'elle n'a plus de valeur.'''
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
    
class SudoAIruleSet():
    '''Représente l'ensemble des règles du système de décision AI, dans leur
    état actuel d'évaluation. L'évalution de cet ensemble se fait au début
    du processus de prise de décision AI, elle déclenche l'évaluation de chaque
    règle et indirectement des critères utilisés.
    '''
    def __init__(self, ai):
        '''Crée le dictionnaire de règles.'''
        assert isinstance(ai, SudoAI)
        self._ai = ai
        self._rules = createRules(ai)
        return

    def add(self, rule):
        '''Ajoute une nouvelle règle. Sa clé dans le dictionnaire est son nom.
        '''
        assert isinstance(rule, SudoAIrule)
        self._rules[rule.name] = rule
        return
    
    def clear(self):
        '''Efface la valeur de toutes les règles.'''
        for rule in self._rules.values():
            rule.clear()
        return

    def rule(self, ruleName):
        '''Retourne l'instance de règle indiquée par son nom, ou déclenche
        une exception s'il n'y a pas de règle de ce nom.
        '''
        r = self._rules.get(ruleName, False)
        if r is False:  #erreur, pas de règle de ce nom
            raise Sudoku_Error("Pas de règle nommée {0}".format(ruleName))
        return r

    def ruleEval(self, ruleName):
        '''Retourne la valeur de la règle indiquée par son nom. Au besoin
        fait l'évaluation de la règle. Déclenche une exception s'il n'y a pas
        de règle de ce nom et propage une exception d'évaluation de la règle.
        '''
        r = self._rules.get(ruleName, False)
        if r is False:  #erreur, nom de règle inconnu
            raise Sudoku_Error("Pas de règle nommée {0}".format(ruleName))
        return r.eval()

    def evalAll(self):
        '''Evalue toutes les règles.'''
        for r in self._rules.values():
            r.eval()
        return True

    def show(self):
        '''Liste la valeur actuelle de toutes les règles.'''
        ui.display("Evaluation des règles : ")
        for r in self._rules.values():
            ui.display("{0} : {1}" 
                  .format(r.name, r.val))
        return
        

#TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 
#TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 

if __name__ == "__main__":
    env = sudoenv.SudoEnv()
    TEST = env.TEST
    TEST.test("ai", 3)

    #Variables pour les tests
    testRuleChrc = True
    testRuleLplc = False
    testai_niveau = 0
    testai_nivmax = 2
    
    #Règles
    air = AIrules()

