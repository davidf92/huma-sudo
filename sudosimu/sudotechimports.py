'''Module sudotechimports - Rassemblement des déclarations des classes et
namespaces des modules de techniques, pour faire un import unique dans les
modules du package qui en ont besoin.
'''

##IMPORTS DES MODULES DE TECHNIQUES DE RESOLUTION
if __name__ in ("__main__", "sudotechimports"):
    #Chiffre/rang-colonne
    from techchrc.techchrcr import TechChRCrow   #par rang pour un chiffre
    from techchrc.techchrcc import TechChRCcol   #par colonne pour un chiffre
    from techchrc.techchrcg import TechChRCgrid   #grille entière pour un chiffre
    from techchrc.techchrcga import TechChRCgridAll  #grille entière tous les chiffres
    #Dernier placement
    from techlplc.techlplcr import TechLastPlcRow    #sur un rang
    from techlplc.techlplcc import TechLastPlcCol    #sur une colonne
    from techlplc.techlplcs import TechLastPlcSqr    #sur un carré
    from techlplc.techlplcp import TechLastPlcPlace    #sur une case (place)
    from techlplc.techlplcg import TechLastPlcGrid   #sur la grille entière
elif __name__ == "sudosimu.sudotechimports":
    #Chiffre/rang-colonne
    from sudosimu.techchrc.techchrcr import TechChRCrow   #par rang pour un chiffre
    from sudosimu.techchrc.techchrcc import TechChRCcol   #par colonne pour un chiffre
    from sudosimu.techchrc.techchrcg import TechChRCgrid   #grille entière pour un chiffre
    from sudosimu.techchrc.techchrcga import TechChRCgridAll  #grille entière tous les chiffres
    #Dernier placement
    from sudosimu.techlplc.techlplcr import TechLastPlcRow    #sur un rang
    from sudosimu.techlplc.techlplcc import TechLastPlcCol    #sur une colonne
    from sudosimu.techlplc.techlplcs import TechLastPlcSqr    #sur un carré
    from sudosimu.techlplc.techlplcp import TechLastPlcPlace    #sur une case (place)
    from sudosimu.techlplc.techlplcg import TechLastPlcGrid   #sur la grille entière
else:
    raise Exception("Impossible de faire les imports dans le module sudothinkai.")

