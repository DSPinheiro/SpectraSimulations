"""
Module with functions to bind backend functions to GUI elements.
"""

import interface.variables as guiVars

from simulation.simulation import simulate

from matplotlib.backend_bases import key_press_handler, KeyEvent

# --------------------------------------------------------- #
#                                                           #
#                     KEYBIND FUNCTIONS                     #
#                                                           #
# --------------------------------------------------------- #

# Function to bind the default matplotlib hotkeys
def on_key_event(event: KeyEvent):
    """
    Function to bind the default matplotlib hotkeys
        
        Args:
            event: which key event was triggered
        
        Returns:
            Nothing, the key event is passed to the default matplotlib key handler and the correct action is performed
    """
    print('you pressed %s' % event.key)
    key_press_handler(event, guiVars._canvas, guiVars._toolbar) # type: ignore

# Function to bind the simulation function to the enter key
def enter_function(event: KeyEvent):
    """
    Function to bind the simulation function to the enter key
        
        Args:
            event: which key event was triggered
        
        Returns:
            Nothing, the simulation function is executed
    """
    simulate(guiVars._sim, guiVars._f, guiVars._a) # type: ignore
