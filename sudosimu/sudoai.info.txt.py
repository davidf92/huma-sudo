

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
RULE_DECNIV = "rule_decniv"         #revenir un niveau en dessous
RULE_RETNIV0 = "rule_niv0"          #revenir au niveau d'exécution 0

