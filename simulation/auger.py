"""
Module with functions that prepare auger transtion data.
"""
from __future__ import annotations


import data.variables as generalVars

import interface.variables as guiVars

from interface.plotters import stem_ploter

from simulation.shake import calculateTotalShake

from simulation.mults import get_cascadeBoost

from data.definitions import Line, processLine

from typing import List

#GUI Imports for warnings
from tkinter import messagebox

from matplotlib.pyplot import Axes

# ---------------------------------------------------------------------- #
#                                                                        #
#             FUNCTIONS TO PREPARE THE AUGER TRANSITION DATA             #
#                                                                        #
# ---------------------------------------------------------------------- #


def stick_auger(graph_area: Axes | None, aug_stick_val: List[Line], transition: str, bad_selection: int, cs: str = ''):
    """
    Function to check and send the data to the stick plotter function for auger transitions.
    
        Args:
            aug_stick_val: array with the rates data from the selected auger transition
            transition: selected transition key
            bad_selection: total number of transitions that had no data
            cs: charge state value for when simulating various charge states
        
        Returns:
            bad: updated value of the total number of transitions that had no data
    """
    bad = bad_selection
    
    # Check if there is no data for the selected transition
    if not aug_stick_val:
        # Make a 0 vector to still have data to plot
        aug_stick_val = [processLine() for i in range(16)]
        # Show a warning that this transition has no data and add it to the bad selection count
        if len(generalVars.jj_vals) == 0:
            messagebox.showwarning("Wrong Transition", "Auger info. for " + transition + " is not Available")
        else:
            messagebox.showwarning("Wrong Transition", "Auger info. for " + transition + " is not Available for the selected jj values")
        bad += 1
        
        return bad, graph_area
    
    # Extract the energy values
    x = [row.energy for row in aug_stick_val]
    """
    Energy values for the selected transition
    """
    
    if guiVars.include_cascades.get(): # type: ignore
        if len(generalVars.augBoostMatrixDict) == 0:
            get_cascadeBoost('auger')
    
    
    # Plot the transition
    y = [row.effectiveIntensity(-1.0, 1.0, 1.0, guiVars.include_cascades.get(), 'auger') for row in aug_stick_val] # type: ignore
    """
    Intensity values for the selected diagram or auger transition
    """
    
    JJ = [row.jji for row in aug_stick_val]
    
    if graph_area:
        graph_area = stem_ploter(graph_area, x, y, JJ,
                    transition if cs == '' else cs + '' + transition,
                    'Auger' if cs == '' else 'Auger_CS')
    
    return bad, graph_area


def simu_auger(aug_sim_val: List[Line], beam: float, FWHM: float, shake_amps: dict = {}):
    """
    Function to organize the data to be sent to the plotter function for diagram transitions.
    
        Args:
            aug_sim_val: array with the rates data from the selected auger transition
            beam: beam energy value from the interface to control if we need to multiply by the overlap
            cs: charge state flag to know if we need to multiply by the mixing fraction
        
        Returns:
            x1: energy values for every line possible within the selected transition
            y1: intensity values for every line possible within the selected transition
            w1: width values for every line possible within the selected transition
    """
    # Extract the energies, intensities and widths of the transition (different j and eigv)
    x1 = [row.energy for row in aug_sim_val]
    w1 = [row.totalWidth for row in aug_sim_val]
    
    if guiVars.include_cascades.get(): # type: ignore
        if len(generalVars.augBoostMatrixDict) == 0:
            get_cascadeBoost('auger')
    
    if guiVars.exc_mech_var.get() == 'EII': # type: ignore
        crossSection = generalVars.elementMRBEB
    elif guiVars.exc_mech_var.get() == 'PIon': # type: ignore
        #We have the elam photospline but it would make no diference as it would be the same value for all orbitals of the same element
        #TODO: Find a way to calculate this for every orbital, maybe R-matrix
        crossSection = 1.0
    else:
        crossSection = 1.0
    
    y1 = [row.effectiveIntensity(beam, FWHM, crossSection, guiVars.include_cascades.get(), 'auger', shake_amps = shake_amps) for row in aug_sim_val] # type: ignore
    
    return x1, y1, w1

