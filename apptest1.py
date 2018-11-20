'''apptest1.py : appli de test du package SudoSimu en mode console.
Le code est structuré pour une exécution événementielle, donc peut être
réutilisé avec une interaction console ou dans une appli fenêtrée
événementielle.
'''

import sudosimu as sudo

#globales
app = None  #l'application de simulation

def cmdOpen():
    '''Commande exécutée au lancement de l'application, met en place
    l'interface utilisateur et fait les initialisations nécessaires.
    '''
    global app
    #démarre une simulation de sudoku
    app = sudo.App()
    #définit l'interface GUI et affiche
    app.makeUI()

####REFLECHIR A CETTE COMMANDE
    #app.show()

def cmdNewGridFile():
    '''Charge une nouvelle grille depuis un fichier.
    global app
    app.readGridFile()
    

def cmdRandomGrid():
    pass


def main():
    '''Démarre l'appli de simulation de Sudoku.'''
    #commmencer par ouvrir une instance de simulation
    cmdOpen()
    #charger un fichier de grille
    cmdNewGridFile()
    return



if __name__ == "__main__":
    main()
