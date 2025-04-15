"""
Module with functions to setup the detector to use the simulation
"""

from __future__ import annotations

#Import file namer function
from utils.misc.fileIO import loadEfficiency

from typing import List

from scipy.interpolate import interp1d

import numpy as np
import numpy.typing as npt

#GUI Imports for warnings
from tkinter import messagebox

# --------------------------------------------------------- #
#                                                           #
#                     DETECTOR FUNCTIONS                    #
#                                                           #
# --------------------------------------------------------- #

# Initialize the detector efficiency values from the file
def initialize_detectorEfficiency(effic_file_name: str):
    """
    Function to read and initialize the detector efficiency values.
        
        Args:
            effic_file_name: name of the file with the detector efficiency
        
        Returns:
            energy_values: list of energy values in the efficiency file
            efficiency_values: list of efficiency values in the efficiency file
    """
    energy_values: List[float] = []
    efficiency_values: List[float] = []
    
    try:
        # Read and load the file
        efficiency = loadEfficiency(effic_file_name)
        # Convert to floats
        for pair in efficiency:
            energy_values.append(float(pair[0]))
            efficiency_values.append(float(pair[1]))
    except FileNotFoundError:
        messagebox.showwarning("Error", "Efficiency File is not Avaliable")
    
    return energy_values, efficiency_values


# Interpolate detector efficiency on the simulation xfinal
def detector_efficiency(energy_values: List[float], efficiency_values: List[float],
                        xfinal: List[float] | npt.NDArray[np.float64], enoffset: float,
                        sat_enoffset: float, shkoff_enoffset: float, shkup_enoffset: float):
    """ 
    Function to interpolate the detector efficiency to the simulated x values
        
        Args:
            energy_values: list of the energy values provided in the detector efficiency data
            efficiency_values: list of the efficiency values provided in the detector efficiency data
            xfinal: list of the simulated x values
            enoffset: value of the simulated x offset
            sat_enoffset: value of the simulated satellite x offset
            shkoff_enoffset: value of the simulated shake-off x offset
            shkup_enoffset: value of the simulated shake-up x offset
            
        Returns:
            interpolated_effic: list of efficiency values interpolated for the simulated x values
    """
    # Initialize interpolated y values
    interpolated_effic = [0.0 for i in range(len(xfinal))]
    # Initialize interpolated satellite y values
    interpolated_effic_sat = [0.0 for i in range(len(xfinal))]
    # Initialize interpolated shake-off y values
    interpolated_effic_shkoff = [0.0 for i in range(len(xfinal))]
    # Initialize interpolated shake-up y values
    interpolated_effic_shkup = [0.0 for i in range(len(xfinal))]
    # Interpolate data
    effic_interpolation = interp1d(energy_values, np.array(efficiency_values)/100)
    """
    Interpolation function initialized from the efficiency data, normalized to 1
    """
    # Loop the energy values with the simulated offset and store the efficiency
    for i, energy in enumerate(np.array(xfinal)+enoffset):
        interpolated_effic[i] = effic_interpolation(energy)
        interpolated_effic_sat[i] = effic_interpolation(energy + sat_enoffset)
        interpolated_effic_shkoff[i] = effic_interpolation(energy + shkoff_enoffset)
        interpolated_effic_shkup[i] = effic_interpolation(energy + shkup_enoffset)
    
    return interpolated_effic, interpolated_effic_sat, interpolated_effic_shkoff, interpolated_effic_shkup

