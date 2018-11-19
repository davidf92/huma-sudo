'''Le module sudothinkai contient la classe SudoThinkAI.
ThinkAI est la classe qui encapsule la simulation d'intelligence. Celle-ci va
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

Fonction de stratégie de résolution : _ai_chrc_lplc_loop()
La résolution est recherchée en alternant les techniques Ch/RC et LastPlc
jusqu'à victoire ou abandon. L'abandon est décidé lorsque les deux techniques
échouent successivement à faire un placement. Dans la mesure où il n'y a dans
cette version aucune décision non certaine, toute poursuite ne pourra donner
que le même résultat de zéro placement.

Historique des mises à jour
19/10/2017 module créé en déportant ici dans une fonction le contenu de la méthode
suggestAction() de la classe SudoThinkAI. Cette fonction spécifique à une
stratégie de résolution est ensuite importée dans suggestAction()

TEST :
Ce module importe le module 'sudotest' et utilise l'objet global sudoTest de
classe SudoTest pour gérer de manière paramétrable les I/O de test du code.
'''

##IMPORTS DU MOTEUR DE SIMULATION
if __name__ in ("__main__", "aichrlploop", "ai.aichrlploop"):
    import sudoui as ui
    import sudorules as rules
    from sudorules import Sudoku_Error
    from sudomemory import SudoMemory
    #import sudoknowledge
    from sudotest import *
elif __name__ == "sudosimu.ai.aichrlploop":
    from sudosimu import sudoui as ui
    from sudosimu import sudorules as rules
    from sudosimu.sudorules import Sudoku_Error
    from sudosimu.sudomemory import SudoMemory
    #import sudosimu.sudoknowledge
    from sudosimu.sudotest import *
else:
    raise Exception("Impossible de faire les imports dans le module sudo.")

##IMPORTS DES MODULES DE TECHNIQUES DE RESOLUTION
if __name__ in ("__main__", "aichrlploop", "ai.aichrlploop"):
    #Chiffre/rang-colonne
    from techchrc.techchrcr import TechChRCrow   #par rang pour un chiffre
    from techchrc.techchrcc import TechChRCcol   #par colonne pour un chiffre
    from techchrc.techchrcg import TechChRCgrid   #grille entière pour un chiffre
    from techchrc.techchrcga import TechChRCgridAll  #grille entière tous les chiffres
    #Dernier placement
    from techlplc.techlplcr import TechLastPlcRow    #sur un rang
    from techlplc.techlplcc import TechLastPlcCol    #sur une colonne
    from techlplc.techlplcs import TechLastPlcSqr    #sur un carré
    #from techlplc.techlplcp import TechLastPlcSqr    #sur une case (place)
    from techlplc.techlplcg import TechLastPlcGrid   #sur la grille entière
elif __name__ == "sudosimu.ai.aichrlploop":
    #Chiffre/rang-colonne
    from sudosimu.techchrc.techchrcr import TechChRCrow   #par rang pour un chiffre
    from sudosimu.techchrc.techchrcc import TechChRCcol   #par colonne pour un chiffre
    from sudosimu.techchrc.techchrcg import TechChRCgrid   #grille entière pour un chiffre
    from sudosimu.techchrc.techchrcga import TechChRCgridAll  #grille entière tous les chiffres
    #Dernier placement
    from sudosimu.techlplc.techlplcr import TechLastPlcRow    #sur un rang
    from sudosimu.techlplc.techlplcc import TechLastPlcCol    #sur une colonne
    from sudosimu.techlplc.techlplcs import TechLastPlcSqr    #sur un carré
    #from sudosimu.techlplc.techlplcp import TechLastPlcSqr    #sur une case (place)
    from sudosimu.techlplc.techlplcg import TechLastPlcGrid   #sur la grille entière
else:
    raise Exception("Impossible de faire les imports dans le module aichrlploop.")


def _ai_chrc_lplc_loop(self):
    '''Méthode de résolution AI qui utilise alternativement Ch/RC et LastPlc.
    '''
    TEST.display("thinkai", 3, "ThinkAI : méthode _ai_chrc_lplc_loop()")
    assert self._initOk
    mem = self._mem
    #PRINCIPE DE RESOLUTION
    #Boucle qui enchaîne Ch/RC-grille et LastPlc-grille, avec vérification
    #de grille terminée.
    #Tant que des chiffres sont placés, la boucle reprend. Elle s'arrête
    #quand l'enchaînement des techniques ne fait plus de placements sur
    #une boucle entière.

    #PREMIERE ETAPE - Ch/RC sur toute la grille
    if self._step == 1:
        tech = mem.recall("ai_suggested_tech", self)
        #s'il n'y a pas encore de technique en cours d'exécution
        if tech is None:
            TEST.display("thinkai", 1, "AI : choix de la technique : "\
                         "TechChRCgridAll")
            TEST.display("thinkai", 3, "Thinkai - Etape #1 de suggestion "\
                         "avec la technique TechChRCgrid.")
            try:
                tech = TechChRCgridAll(mem, None)
            except:
                #on gère l'exception
                TEST.display("thinkai", 1, "La résolution s'interrompt "\
                             "sur une erreur irrécupérable.")
                TEST.display("thinkai", 3, "ThinkAI - Erreur fatale : "\
                             "L'instanciation de la technique de résolution "\
                             "a échoué.")
                raise rules.Sudoku_Error
            mem.memorize("ai_suggested_tech", tech, self)
            mem.memorize("ai_suggested_tech_end", False, self)
            #initialiser le compteur de placements de la boucle
            self._nbplcloop = 0
            TEST.display("thinkai", 1, "lancement de la technique.")
            return ("tech", (tech, "insert"))
        #si la tech est terminée => passage à l'étape suivante
        elif mem.recall("ai_suggested_tech_end", self) is True:
            endDetails = mem.recall("ai_suggested_tech_end_details", self)
            #récupérer le nombre de placements faits par la technique
            nbplc = endDetails[1]
            TEST.display("thinkai", 1, "AI : La technique {0} se termine "\
                         "avec {1} placement(s)."\
                         .format(tech.techName(), nbplc))
            self._nbtotplc += nbplc
            self._nbplcloop += nbplc
            #on termine la technique proprement
            del(tech)
            mem.memorize("ai_suggested_tech", None, self)
            #étape suivante
            self._step = 2
            TEST.display("thinkai", 3, "ThinkAI - Fin de l'étape #1")
            TEST.pause("thinkai", 1)
            return ("continue", None)
        #sinon, continuer d'appliquer la même technique
        else:

            TEST.display("thinkai", 2, "AI : Poursuite de la technique : "\
                         "{0}.".format(tech.techName()))
            return ("tech", (tech, "same"))

    #DEUXIEME ETAPE - Vérifier si la grille est terminée
    if self._step == 2:
        TEST.display("thinkai", 3, "Thinkai - Etape #2 de suggestion. "\
                     "Vérification de grille terminée.")
        if self._gridChecking is False:
            #Commencer la vérification
            self._gridChecking = True
            self._gridCompleted = False
            return ("check", None)
        else:
            #Résultat de vérification
            checked = self._gridCompleted
            self._gridChecking = False
        #Si la grille est terminée, retourner "end", sinon passer
        #à l'étape suivante
        if checked is True:
            TEST.display("thinkai", 1, "AI : Vérification : la grille "\
                         "est terminée.")
            return ("end", ("win",))
        else:
            TEST.display("thinkai", 1, "AI : Vérification : la grille "\
                         "n'est pas terminée.")
            TEST.display("thinkai", 1, "Progression de la résolution :\n"\
                         "Total placements faits : {0}\n"\
                         "Placements dans le cycle de techniques : {1}\n"\
                         .format(self._nbtotplc, self._nbplcloop))
            self._step = 3
            TEST.display("thinkai", 3, "ThinkAI - Fin de l'étape #2")
            TEST.pause("thinkai", 1)
            return ("continue", None)



    #TROISIEME ETAPE - LastPlc sur toute la grille
    if self._step == 3:
        tech = mem.recall("ai_suggested_tech", self)
        #s'il n'y a pas encore de technique en cours d'exécution
        if tech is None:
            TEST.display("thinkai", 1, "AI : choix de la technique : "\
                         "TechLastPlcGrid")
            TEST.display("thinkai", 3, "Thinkai - Etape #3 de suggestion "\
                         "avec la technique TechLastPlcGrid.")
            try:
                tech = TechLastPlcGrid(mem, None)
            except:
                #on gère l'exception
                TEST.display("thinkai", 1, "La résolution s'interrompt "\
                             "sur une erreur irrécupérable.")
                TEST.display("thinkai", 3, "ThinkAI - Erreur fatale : "\
                             "L'instanciation de la technique de résolution "\
                             "a échoué.")
                raise rules.Sudoku_Error
            mem.memorize("ai_suggested_tech", tech, self)
            mem.memorize("ai_suggested_tech_end", False, self)
            return ("tech", (tech, "insert"))
        #si la tech est terminée => recommencer ou abandon
        elif mem.recall("ai_suggested_tech_end", self) is True:
            endDetails = mem.recall("ai_suggested_tech_end_details", self)
            #récupérer le nombre de placements faits par la technique
            #le format est :("succeed", nb))
            nbplc = endDetails[1]
            TEST.display("thinkai", 1, "AI : La technique {0} se termine "\
                         "avec {1} placement(s)."\
                         .format(tech.techName(), nbplc))
            self._nbtotplc += nbplc
            self._nbplcloop += nbplc
            #on termine la technique proprement
            del(tech)
            mem.memorize("ai_suggested_tech", None, self)
            #étape suivante
            self._step = 4
            TEST.display("thinkai", 3, "ThinkAI - Fin de l'étape #3")
            TEST.pause("thinkai", 1)
            return ("continue", None)
        #sinon, continuer d'appliquer la même tech
        else:
            TEST.display("thinkai", 2, "AI : Poursuite de la technique : "\
                         "{0}.".format(tech.techName()))
            return ("tech", (tech, "same"))

    #QUATRIEME ETAPE - Vérifier si la grille est terminée
    if self._step == 4:
        TEST.display("thinkai", 3, "Thinkai - Etape #4 de suggestion. "\
                     "Vérification de grille terminée.")
        if self._gridChecking is False:
            #Commencer la vérification
            self._gridChecking = True
            self._gridCompleted = False
            return ("check", None)
        else:
            #Résultat de vérification
            checked = self._gridCompleted
            self._gridChecking = False
        #Si la grille est terminée, retourner "end", sinon passer
        #à la fin de la boucle
        if checked is True:
            TEST.display("thinkai", 1, "AI : Vérification : la grille "\
                         "est terminée.")
            return ("end", ("win",))
        else:
            TEST.display("thinkai", 1, "AI : Vérification : la grille "\
                         "n'est pas terminée.")
            TEST.display("thinkai", 1, "Progression de la résolution :\n"\
                         "Total placements faits : {0}\n"\
                         "Placements dans le cycle de techniques : {1}\n"\
                         .format(self._nbtotplc, self._nbplcloop))
            TEST.pause("thinkai", 1)

    #FIN DE LA BOUCLE DE SUGGESTIONS AI
    #continuer si des placements ont été faits au cours de la boucle
    #de techniques, sinon abandonner.
    if self._nbplcloop >0:
        #recommencer à l'étape #1
        self._step = 1
        TEST.display("thinkai", 2, "AI : Recommencer l'enchaînement de "\
                     "techniques tant qu'il y a des placements faits.")
        TEST.pause("thinkai", 1)
        return ("continue", None)
    else:
        #fin
        TEST.display("thinkai", 1, "AI : Plus de placements possibles, "\
                     "abandon après le placement de {0} chiffres."\
                     .format(self._nbtotplc))
        return ("end", ("loose", self._nbtotplc))

    return #par principe            
    
