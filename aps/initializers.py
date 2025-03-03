"""
Module to initialize and forward necessary parameters to the correct atomic parameter simulation module
"""

from __future__ import annotations


#OS Imports for paths and files
from pathlib import Path

#GUI Imports
from tkinter import Tk

#Module Imports: Atomic Parameter Selection
from aps.Yields import fetchYields
from aps.LvlWidths import fetchWidths
from aps.XRFQuant import quantifyXRF
from aps.SpecSimu import simulateSpectra


from interface.base import clear

# ---------------------------------------------------------------------------------------------------------------
# Function to choose the type of atomic parameters we want to fetch after selecting the element
def calculate(dir_path: Path, element: tuple[int, str], ap: int, root: Tk, userLine = None):
    """
    Function that launches the correct atomic parameter simulation after selection on the interface.
        
        Args:
            element: list with the z value of the element to simulate and the name of the element
            ap: integer identifying which atomic parameter was selected in the interface
        
        Returns:
            If the function executed correctly it will return 0 (C style)
    """
    
    clear(root)
    
    if ap == 1:
        fetchYields(dir_path, element[0])
    # ---------------------------------------------------------------------------------------------------------------
    elif ap == 2:
        fetchWidths(dir_path, element[0])
    # ---------------------------------------------------------------------------------------------------------------
    elif ap == 3:
        quantifyXRF(dir_path, root)
    # ---------------------------------------------------------------------------------------------------------------
    elif ap == 4:
        simulateSpectra(dir_path, element, root, userLine)
    return 0
