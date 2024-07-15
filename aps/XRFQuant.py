"""
Module that implements the cross sections interface.
This interface has not yet been implemented.
"""
from __future__ import annotations


from pathlib import Path

import data.variables as generalVars

#GUI Imports
from tkinter import Tk
from tkinter import * # type: ignore


from interface.wrappers import SimulationWindow
from data.wrappers import InitializeQuantData


def quantifyXRF(dir_path: Path, root: Tk):
    """
    Function to run the XRF quantification interface
        
        Args:
            dir_path: full path to the location where the application is ran
            root: root element for the tk app
        
        Returns:
            Nothing, we just setup the interface and all commands are bound and performed through the interface
    """
    # ----------------------------------------------------------------------------------------------#
    #                                                                                               #
    #                   INITIALIZE AND READ DATA FROM THE PREDEFINED FILES                          #
    #                                                                                               #
    #-----------------------------------------------------------------------------------------------#

    InitializeQuantData(dir_path)
    
    # ----------------------------------------------------------------------------------------------#
    #                                                                                               #
    #                                  INITIALIZE GUI ELEMENTS                                      #
    #                                                                                               #
    #-----------------------------------------------------------------------------------------------#
    
    SimulationWindow(dir_path, root, quantify=True)