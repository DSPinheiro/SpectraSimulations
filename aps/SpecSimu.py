"""
Module that implements the spectra simulations.
First we search and read all the required files to simulate the selected element, as well as all charge states if they exist.
Second we initialize the Tkinter interface. In this initialization all the functions that calculate and plot the simulated spectrum are bound to interface variables and buttons.
"""

from __future__ import annotations

#GUI message box for CS missmatch warning
from tkinter import Tk

#OS Imports for files paths
from pathlib import Path


from data.wrappers import InitializeMCDFData, InitializeDBData, CheckCS

from interface.wrappers import SimulationWindow


def simulateSpectra(dir_path: Path, element: tuple[int, str], root: Tk):
    """
    Function to run the simulations interface
        
        Args:
            dir_path: full path to the location where the application is ran
            element: list with the [z value, element name] to simulate
            root: root element for the tk app
        
        Returns:
            Nothing, we just setup the interface and all commands are bound and performed through the interface
    """
    # ----------------------------------------------------------------------------------------------#
    #                                                                                               #
    #                   INITIALIZE AND READ DATA FROM THE PREDEFINED FILES                          #
    #                                                                                               #
    #-----------------------------------------------------------------------------------------------#
    
    InitializeMCDFData(dir_path, element)
    InitializeDBData(dir_path, element)
    
    
    # Variable to activate or deactivate the charge state simulation in the interface menu
    CS_exists = CheckCS(dir_path, element)
    """
    Variable to control if this element has transition rates for different charge states
    """
    
    # ----------------------------------------------------------------------------------------------#
    #                                                                                               #
    #                                  INITIALIZE GUI ELEMENTS                                      #
    #                                                                                               #
    #-----------------------------------------------------------------------------------------------#
    
    SimulationWindow(dir_path, root, CS_exists)