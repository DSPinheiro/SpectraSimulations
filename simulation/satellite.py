"""
Module with functions that prepare satellite transtion data.
"""
from __future__ import annotations


import interface.variables as guiVars

import data.variables as generalVars

from simulation.lineUpdater import updateSatTransitionVals

from interface.plotters import stem_ploter

from simulation.mults import get_cascadeBoost

from simulation.shake import calculateTotalShake, get_shakeoff, get_shakeup

from data.definitions import Line, processLine

from typing import List

#GUI Imports for warnings
from tkinter import messagebox, Toplevel

from matplotlib.pyplot import Axes

import copy

# ---------------------------------------------------------------------- #
#                                                                        #
#           FUNCTIONS TO PREPARE THE SATELLITE TRANSITION DATA           #
#                                                                        #
# ---------------------------------------------------------------------- #

def stick_satellite(sim: Toplevel | None, graph_area: Axes | None, sat_stick_val: List[Line], transition: str, low_level: str, high_level: str, bad_selection: int, cs: str = ''):
    """
    Function to check and send the data to the stick plotter function for sattelite transitions.
    
        Args:
            sim: tkinter simulation window to update the progress bar
            sat_stick_val: array with the rates data from the selected sattelite transition
            transition: selected transition key
            low_level: low level of the selected transition
            high_level: high level of the selected transition
            bad_selection: total number of transitions that had no data
            beam: beam energy user value from the interface
            FWHM: beam energy FWHM user value from the interface
            cs: charge state value for when simulating various charge states
        
        Returns:
            bad: updated value of the total number of transitions that had no data
    """
    bad = bad_selection
    
    # Check if there is no data for the selected transition
    if not sat_stick_val:
        # Make a 0 vector to still have data to plot
        sat_stick_val = [processLine() for i in range(16)]
        # Show a warning that this transition has no data and add it to the bad selection count
        if len(generalVars.jj_vals) == 0:
            messagebox.showwarning("Wrong Transition", transition + " is not Available")
        else:
            messagebox.showwarning("Wrong Transition", transition + " is not Available for the selected jj values")
        bad += 1

        return bad, graph_area

    # Initialize a variable to control the progress bar
    b1 = 0
    
    # Extract the energy values
    x = [row.energy for row in sat_stick_val if len(row.Shelli) <= 4]
    """
    Energy values for the selected transition (shake-off)
    """
    # Extract the energy values
    x_up = [row.energy for row in sat_stick_val if len(row.Shelli) > 4]
    """
    Energy values for the selected transition (shake-up)
    """
    
    if guiVars.include_cascades.get(): # type: ignore
        if len(generalVars.satBoostMatrixDict) == 0:
            get_cascadeBoost('satellite')
        
    
    # Loop all shake levels read in the shake weights file
    for ind, key in enumerate(generalVars.label1):
        # Filter the specific combination of radiative transition and shake level (key) to simulate
        sat_stick_val_ind = updateSatTransitionVals(low_level, high_level, key, sat_stick_val)

        # Check for at least one satellite transition
        if len(sat_stick_val_ind) > 0:
            sy_points = [row.effectiveIntensity(-1.0, 1.0, 1.0, guiVars.include_cascades.get(), 'satellite', key) for row in sat_stick_val if len(row.Shelli) <= 4] # type: ignore
            """
            Intensity values for the selected satellite transition
            """    
            
            # SHAKE-UP
            sy_points_up = [row.effectiveIntensity(-1.0, 1.0, 1.0, guiVars.include_cascades.get(), 'shakeup', key) for row in sat_stick_val if len(row.Shelli) > 4] # type: ignore
            """
            Intensity values for the selected satellite transition
            """
            
            JJ = [row.jji for row in sat_stick_val if len(row.Shelli) <= 4]
            JJ_up = [row.jji for row in sat_stick_val if len(row.Shelli) > 4]
            
            if generalVars.verbose >= 3:
                print(x_up)
                print(sy_points_up)
                print(JJ_up)
                
                print(sat_stick_val)
            
            if graph_area:
                graph_area = stem_ploter(graph_area, x, sy_points, JJ,
                                        transition if cs == '' else cs + ' ' + transition,
                                        'Satellites' if cs == '' else 'Satellites_CS',
                                        ind, key, x_up, sy_points_up, JJ_up)
        
        # Update the progress bar
        b1 += 100 / len(generalVars.label1)
        guiVars.progress_var.set(b1) # type: ignore
        if sim:
            sim.update_idletasks()
    
    return bad, graph_area


def simu_sattelite(sat_sim_val: List[Line], low_level: str, high_level: str,
                   beam: float, FWHM: float, shake_amps: dict = {}, element: str = '',
                   exc_index: int = -1, calc_int: bool = True,
                   include_cascades: bool | None = None, exc_mech_var: str = ''):
    """
    Function to check and send the data to the stick plotter function for sattelite transitions.
    
        Args:
            sat_sim_val: array with the rates data from the selected sattelite transition
            low_level: low level of the selected transition
            high_level: high level of the selected transition
            beam: beam energy user value from the interface
            FWHM: beam energy FWHM user value from the interface
            cs: charge state flag to know if we need to multiply by the mixing fraction
        
        Returns:
            xs_inds: nested list with the energy values of each satellite transition possible for the selected diagram transition
            ys_inds: nested list with the intensity values of each satellite transition possible for the selected diagram transition
            ws_inds: nested list with the width values of each satellite transition possible for the selected diagram transition
    """
    # Temporary arrays to store the satellite data for this transition
    xs_inds: List[List[float]] = []
    ys_inds: List[List[float]] = []
    ws_inds: List[List[float]] = []
    
    if include_cascades is None:
        casc: bool = guiVars.include_cascades.get() # type: ignore
    else:
        casc: bool = include_cascades
    
    if exc_mech_var == '':
        exc_mech: str = guiVars.exc_mech_var.get() # type: ignore
    else:
        exc_mech: str = exc_mech_var
    
    if casc:
        if len(generalVars.satBoostMatrixDict) == 0:
            get_cascadeBoost('satellite')
    
    # SHAKE-OFF
    # Loop the shake labels read from the shake weights file
    for ind, key in enumerate(generalVars.label1):
        # Filter the specific combination of radiative transition and shake level (key) to simulate
        sat_sim_val_ind = updateSatTransitionVals(low_level, high_level, key, sat_sim_val, True)
        
        # Check if there is at least one satellite transition
        if len(sat_sim_val_ind) > 0:
            # Extract the energies, intensities and widths of the transition (different j and eigv)
            x1s = [row.energy for row in sat_sim_val_ind if len(row.Shelli) <= 4]
            w1s = [row.totalWidth for row in sat_sim_val_ind if len(row.Shelli) <= 4]
            
            if calc_int:
                if exc_mech == 'EII':
                    crossSection = generalVars.elementMRBEB
                elif exc_mech == 'PIon':
                    #We have the elam photospline but it would make no diference as it would be the same value for all orbitals of the same element
                    #TODO: Find a way to calculate this for every orbital, maybe R-matrix
                    crossSection = 1.0
                else:
                    crossSection = 1.0
                
                if element == '':
                    y1s = [row.effectiveIntensity(beam, FWHM, crossSection, casc, 'satellite',
                                                  key, shake_amps, exc_index=exc_index) for row in sat_sim_val_ind if len(row.Shelli) <= 4]
                else:
                    y1s = [row.effectiveIntensity(beam, FWHM, crossSection, casc, 'satellite',
                                                key, shake_amps,
                                                shakeoff_lines=generalVars.shakeoff_quant[element],
                                                shakeup_lines=generalVars.shakeup_quant[element],
                                                shakeup_splines=generalVars.shakeUPSplines_quant[element],
                                                shake_missing=generalVars.missing_shakeup_quant[element]) for row in sat_sim_val_ind if len(row.Shelli) <= 4]
                
                ys_inds.append(y1s)
            
            xs_inds.append(x1s)
            ws_inds.append(w1s)
        else:
            xs_inds.append([])
            ys_inds.append([])
            ws_inds.append([])
    
    # SHAKE-UP
    if generalVars.Shakeup_exists:
        # Loop the shake labels read from the shake weights file
        for ind, key in enumerate(generalVars.label1):
            # Filter the specific combination of radiative transition and shake level (key) to simulate
            sat_sim_val_ind = updateSatTransitionVals(low_level, high_level, key, sat_sim_val, True)
            # sat_sim_val_ind = updateSatTransitionVals(low_level, high_level, key, sat_sim_val)
            
            # Check if there is at least one satellite transition
            if len(sat_sim_val_ind) > 0:
                # Extract the energies, intensities and widths of the transition (different j and eigv)
                x1s = [row.energy for row in sat_sim_val_ind if len(row.Shelli) > 4]
                w1s = [row.totalWidth for row in sat_sim_val_ind if len(row.Shelli) > 4]
                
                if calc_int:
                    if exc_mech == 'EII':
                        crossSection = generalVars.elementMRBEB
                    elif exc_mech == 'PIon':
                        #We have the elam photospline but it would make no diference as it would be the same value for all orbitals of the same element
                        #TODO: Find a way to calculate this for every orbital, maybe R-matrix
                        crossSection = 1.0
                    else:
                        crossSection = 1.0
                    
                    if element == '':
                        y1s = [row.effectiveIntensity(beam, FWHM, crossSection, False,
                                                    'shakeup', key, shake_amps) for row in sat_sim_val_ind if len(row.Shelli) > 4]
                    else:
                        y1s = [row.effectiveIntensity(beam, FWHM, crossSection, False,
                                                    'shakeup', key, shake_amps,
                                                    shakeoff_lines=generalVars.shakeoff_quant[element],
                                                    shakeup_lines=generalVars.shakeup_quant[element],
                                                    shakeup_splines=generalVars.shakeUPSplines_quant[element],
                                                    shake_missing=generalVars.missing_shakeup_quant[element]) for row in sat_sim_val_ind if len(row.Shelli) > 4]
                    
                    ys_inds.append(y1s)
                
                xs_inds.append(x1s)
                ws_inds.append(w1s)
            else:
                xs_inds.append([])
                ys_inds.append([])
                ws_inds.append([])
        
    return xs_inds, ys_inds, ws_inds
