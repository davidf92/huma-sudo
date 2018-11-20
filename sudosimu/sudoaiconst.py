''' Le module sudoaiconst rassemble les constantes et labels utilisés dans
l'ensemble du système décisionnel AI. Il peut être importé directement dans
chaque module AI avec un import *
'''

##DONNEES D'ENTREE DU SYSTEME DE DECISION
##---------------------------------------    
'''Les données d'entrée alimentent le système logique. Elles sont utilisées
pour évaluer des critères de décision, lesquels serviront à leur tour à
l'évaluation de règles. Les données sont fournies au système AI sous la forme
d'un dictionnaire.
En pratique ces données représentent l'état d'avancement de la résolution, et
vont donc servir à décider la prochaine action de cette résolution.
Exemple : "dernière action = "place"
'''
AIDATA_BEGIN = "aidata_begin"           #début de résolution
AIDATA_NIV = "aidata_niv"               #niveau d'imbrication de techniques
AIDATA_NIVMAX = "aidata_nivmax"         #niveau max possible
AIDATA_INTECH = "aidata_intech"         #en train d'exécuter une technique
AIDATA_OPPORT = "aidata_opport"         #technique d'opportunité en cours
AIDATA_GRIDCHECKED = "aidata_gridchecked"   #la grille est vérifiée non finie
AIDATA_TECH = "aidata_tech"             #nom de la technique en cours
AIDATA_LTECH = "aidata_ltech"           #nom de la dernière/précédente technique
AIDATA_LACT = "aidata_lact"             #dernière action de pensée, technique ou AI
AIDATA_LTECHACT = "aidata_ltechact"     #dernière action d'une technique
AIDATA_LAIACT = "aidata_laiact"         #dernière action du système AI
AIDATA_LNIV1TECH = "aidata_lniv1tech"   #dernière technique de niveau 1
AIDATA_LOPPTECH = "aidata_lopptech"     #dernière technique d'opportunité (niv>1)


##CRITERES DU SYSTEME DE DECISION
##-------------------------------
'''Les critères AI sont des évaluations logiques calculées avec des informations
de situation du système, donc de situation de la résolution en cours.
Par exemple : valeur("La dernière action est "place") = Vrai
'''
AICRIT_BEGIN = "aicrit_begin"           #début de la résolution
AICRIT_NIV0 = "aicrit_niv0"             #le niveau d'imbrication = 0
AICRIT_NIV1 = "aicrit_niv1"             #le niveau d'imbrication = 1
AICRIT_NIV2SUP = "aicrit_niv2sup"       #le niveau d'imbrication = 2 ou plus
AICRIT_NIVMAX = "aicrit_nivmax"         #le niveau d'imbrication = niveau max
AICRIT_INTECH = "aicrit_intech"         #technique en cours
AICRIT_NOTECH = "aicrit_notech"         #aucune technique en cours
AICRIT_CANTAKEOPP = "critcantakeopp"    #possibilité de chercher une opport.
AICRIT_FIRSTOPP = "aicrit_firstopp"     #dans la première tech de séquence opport.
AICRIT_INOPPORT = "aicrit_inopport"     #dans une technique d'opportunité
AICRIT_INOPPSEQ = "aicrit_inoppseq"     #dans une séquence de techs d'opportunité
AICRIT_GRIDCHECKED = "aicrit_gridchecked"   #la grille est vérifiée non finie

AICRIT_INTECHCHRCGA = "aicrit_intechchrcga" #la technique en cours est TechChRCga
AICRIT_INTECHLPLCG = "aicrit_intechlplcg"   #la technique en cours est TechLplcg
AICRIT_INTECHLPLCP = "aicrit_intechlplcp"   #la technique en cours est TechLplcp
AICRIT_LTECHCHRCGA = "aicrit_ltechchrcga"   #dernière technique = TechChRCga
AICRIT_LTECHLPLCG = "aicrit_ltechlplcg"     #dernière technique = TechLplcg
AICRIT_LTECHLPLCP = "aicrit_ltechlplcp"     #dernière technique = TechLplcp
AICRIT_LTECHNONE = "aicrit_ltechnone"       #pas de dernière technique (= none)
AICRIT_LASTACTPLACE = "aicrit_lastactplace"       #dernière action = 'place'
AICRIT_LASTACTEND = "aicrit_lastactend"           #dernière action = 'end'

####pas encore utilisés, à faire
AICRIT_LASTTECHPLACE = "aicrit_lasttechplace"   #dernière action technique = 'place'
AICRIT_LASTTECHEND = "aicrit_lasttechend"       #dernière action technique = 'end'
AICRIT_LASTAIPLACE = "aicrit_lastaiplace"     #dernière action AI = 'place'
AICRIT_LASTAIEND = "aicrit_lastaiend"         #dernière action AI = 'end'
######


##GESTION DES REGLES DU SYSTEME DE DECISION
##-----------------------------------------
'''Les règles AI sont des évaluations logiques calculées avec les critères AI.
Elles représentent les bases de décision, par exemple les actions possibles.
Une règle associe une valeur et une fonction de calcul de cette valeur.
'''
AIRULE_CHECKGRID = "airule_checkgrid"   #vérifier si la grille est complète
AIRULE_TECHCONT = "airule_techcont"     #continuer la technique en cours
AIRULE_OPPORT = "airule_opport"         #chercher une opportunité
AIRULE_CHRCGA = "airule_chrcga"         #commencer la technique ChRCga (niv1)
AIRULE_LPLCG = "airule_lplcg"           #commerncer la technique Lplcg (niv1)
AIRULE_LPLCP = "airule_lplcp"           #commerncer la technique Lplcp (niv>=2)
AIRULE_DISCARD = "airule_discard"       #arrêter la technique en cours
AIRULE_DISCARDALL = "airule_discardall" #arrêter toutes les techniques en cours
AIRULE_TECHABORT = "airule_techabort"   #abandonner la technique en cours

#texte descriptif des règles
AIRULETEXT_CHECKGRID = "Vérifier si la grille est terminée."
AIRULETEXT_TECHCONT = "Continuer la même technique de résolution."
AIRULETEXT_OPPORT = "Lancer une technique de recherche d'opportunité."
AIRULETEXT_CHRCGA = "Commencer une technique \"ChRC/grille\"."
AIRULETEXT_LPLCG = "Commencer technique \"LastPlace/grille\"."
AIRULETEXT_LPLCP = "Commencer une technique \"LastPlace/case\"."
AIRULETEXT_DISCARD = "Arrêter la technique en cours."
AIRULETEXT_DISCARDALL = "Arrêter toutes les techniques en cours."
AIRULETEXT_TECHABORT = "Abandonner l'exécution de la technique en cours."




