'''Module de déclarations pour le namesace du package 'sudosimu'.
Donne un accès direct à toutes les classes du simulateur, à tout le système
d'environnement, ainsi qu'aux classes d'intégration applicative.
Reprend également les constantes des modules du package.
'''
from sudosimu.sudoapp import *

#Classes et constantes de l'intégration applicative
from sudosimu.sudoapp import SudoApp as App
from sudosimu.sudosimpleapp import SudoSimpleApp as SimpleApp
from sudosimu.sudogrid import SudoGrid as Grid
from sudosimu.sudoplayer import SudoPlayer as Player

#Classes et constantes dy système d'environnement et de test
from sudosimu.sudoenv import SudoEnv as Env
from sudosimu.sudoenv import SudoEnvQuiet as EnvQuiet
from sudosimu import sudoui
from sudosimu import sudotest
from sudosimu.sudotest import SudoTest as Test
UI_STD = sudoui.UI_STD
UI_GUI = sudoui.UI_GUI
UI_BOTH = sudoui.UI_BOTH
TEST_STD = sudotest.MODE_STD
TEST_GUI = sudotest.MODE_GUI
TEST_SELECT = sudotest.MODE_SELECT
TEST_BOTH = sudotest.MODE_BOTH
##STD =           sudoui.STD
##GUI =           sudoui.GUI
##MODE_STD =      sudoui.STD
##MODE_GUI =      sudoui.GUI
##MODE_SELECT =   sudotest.MODE_SELECT
##MODE_BOTH =     sudotest.MODE_BOTH

#### NOTE (15/11/2017): DEVIENDRA OBSOLETE APRES INTEGRATION DE SUDOENV ####
from sudosimu.sudotest import *
#Voir si cet import aussi devient obsolète (15/11/2017)
from sudosimu import sudotestall

#Classes et constantes du contrôle d'avancement de simulation (sudogame)
from sudosimu.sudogame import SudoGame as Game
from sudosimu import sudogame
STEP =          sudogame.STEP
OBS =           sudogame.OBS
OBSERVE =       sudogame.OBSERVE
PLACE =         sudogame.PLACE
FAIL =          sudogame.FAIL
END =           sudogame.END
EXCEPT =        sudogame.EXCEPT
NOEXCEPT =      sudogame.NOEXCEPT

#Accès direct (bas niveau) aux modules du simulateur
from sudosimu import sudogridview
from sudosimu import sudomemory
from sudosimu import sudothinking
from sudosimu import sudothinkai
from sudosimu import sudoai
from sudosimu import sudomemprofile
from sudosimu import sudothinkprofile

