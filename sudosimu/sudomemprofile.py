'''Jeu de Sudoku : profil de capacité mémoire des joueurs
'''

if __name__ in ("__main__", "sudomemprofile"):
    import sudoui
    import sudorules as rules
    from sudorules import Sudoku_Error
    import sudoui as ui
    from sudotest import *
elif __name__ == "sudosimu.sudomemprofile":
    from sudosimu import sudoui
    from sudosimu import sudorules as rules
    from sudosimu.sudorules import Sudoku_Error
    from sudosimu import sudoui as ui
    from sudosimu.sudotest import *
else:
    raise Exception("Impossible de faire les imports dans le module sudomemprofile.")


class SudoMemProfile():
    '''Profil mémoire pour un joueur de Sudoku. Le profil mémoire définit
    une capacité en terme de quantité, la notion d'oubli, d'erreur et de
    confusion.
    Un profil mémoire peut être sérialisé, sauvegardé et lu avec un fichier
    de données.
    '''

#Au stade actuel le profile mémoire de fait rien, mais la structure de code
#est prête.
    
    def __init__(self, profName=None):
        '''Initialise avec un nom de profile 'None' par défaut'''
        if profName is not None:
            self.init(profName)
        else:
            self._profName = None
            self._initOk = False
        return

    def init(self, profName=None):
        self._profName = profName
        self._initOk = True
        return True
        
    def name(self, profName=None):
        '''Définit ou retourne le nom du profile'''
        assert self._initOk
        if profName is not None:
            self._profName = profName
        return self._profName
    
    def __str__(self):
        '''retourne comme forme imprimable le nom du profile ou un nom
        par défaut
        '''
        txt = self._profName
        if txt is None or str(txt) == "":
            txt = "Un profil mémoire par défaut"
        return txt
    
    
