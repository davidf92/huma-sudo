# -*- coding: cp1252 -*-

# programme HumaSudo
# résolution humaine simulée de Sudoku 

import fileinput
import sudorules
from sudorules import Sudoku_Error

def display(text):
    print(text)


def sudoFichReadLines(nomFich, pr=False):
    '''Lecture d'un fichier texte de grille dans le répertoire courant.
    Le fichier doit contenir exactement 9 lignes de caractères numériques.
    Le texte doit être présenté ligne par ligne en 9 x 9 chiffres. Les
    cases vides doivent être représentées par des zéros.
    Retourne une liste de 9 chaînes de 9 caractères numériques.
    '''
    return _sudoFichGrid_(nomFich, 1, pr)

def sudoFichReadLists(nomFich, pr=False):
    '''Lecture d'un fichier texte de grille dans le répertoire courant.
    Le fichier doit contenir exactement 9 lignes de caractères numériques.
    Le texte doit être présenté ligne par ligne en 9 x 9 chiffres. Les
    cases vides doivent être représentées par des zéros.
    Retourne une liste de 9 listes de 9 caractères numériques.
    '''
    return _sudoFichGrid_(nomFich, 2, pr)

def _sudoFichGrid_(nomFich, mode, pr=False):
    '''Lit le fichier de caractères et fait les vérifications.
    Si mode = 1 (défaut) : retourne une liste de lignes
    Si mode = 2 : retourne une liste de listes
    '''
    if nomFich == None:
        raise Sudoku_Error \
              ("Pas de nom de fichier - Abandon")
    if mode not in (1,2):
        raise Sudoku_Error ("Mode de lecture de fichier invalide")
    
    if pr: print "Lecture du fichier ", nomFich, " :"
    listLines = list()
    lineno = 0
    try:
        for line in fileinput.input(nomFich):
            lineno = lineno+1
            #erreur s'il y a plus de 9 lignes dans le fichier
            if lineno > 9:
                raise Sudoku_Error \
                      ("Le fichier contient trop de données. Lecture interrompue. "\
                       "La grille a été remplie.")
            #enlever le caractère final '\n' de la ligne lue dans le fichier
            line = line[:9]
            #erreur si la ligne ne fait pas 9 caractères
            if len(line) != 9:
                raise Sudoku_Error \
                      ("la ligne" + str(lineno) + " : " + line + \
                       " ne fait pas exactement 9 chiffres. ")
            #erreur s'il y a des caractères non numériques
            for c in line:
                if not str(0)<=str(c)<=str(9):
                    raise Sudoku_Error \
                          ("caractère non numérique dans la ligne : " + line)

            #ok, la ligne est valide - Ajout à la liste
            if mode == 1:                   #mode liste de lignes
                listLines.append(line)
            elif mode == 2:                 #mode liste de listes
                listeval = list()
                for c in line:
                    listeval.append(int(c))
                listLines.append(listeval)
            else:
                raise Sudoku_Error ("Mode de lecture de fichier invalide")

            if pr: print "ligne" + str(lineno) + " : " + line
    finally:
        fileinput.close()
        
    #erreur s'il y a eu moins de 9 lignes lues dans le fichier
    if lineno < 9:
        raise Sudoku_Error \
              ("Erreur de lecture, le fichier contient moins de 9 lignes "\
               "de chiffres.")

    #ok, retourne la liste des 9 lignes de 9 chiffres
    if pr: print "Ok, 9 lignes de 9 chiffres."
    return listLines
    

            
