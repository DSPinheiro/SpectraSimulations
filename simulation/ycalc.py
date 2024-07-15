"""
Module with functions to calculate the final y values for the simulation
"""

from __future__ import annotations

#GUI Imports for warnings
from tkinter import messagebox

from simulation.profiles import G, L, V
from utils.experimental.detector import detector_efficiency

import data.variables as generalVars

import interface.variables as guiVars

from typing import List, Tuple

import numpy as np
import numpy.typing as npt

from tkinter import Toplevel

# --------------------------------------------------------- #
#                                                           #
#                   INTENSITY CALCULATOR                    #
#                                                           #
# --------------------------------------------------------- #

# Calculate the simulated y values applying the selected line profile, detector efficiency, resolution and energy offset
def y_calculator(sim: Toplevel, transition_type: str, fit_type: str,
                 xfinal: npt.NDArray[np.float64], x: List[List[float]],
                 y: List[List[float]], w: List[List[float]],
                 xs: List[List[List[float]]],
                 ys: List[List[List[float]]], ws: List[List[List[float]]],
                 res: float, energy_values: List[float], efficiency_values: List[float],
                 enoffset: float, sat_enoffset: float, shkoff_enoffset: float, shkup_enoffset: float) -> \
                    Tuple[npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.float64],
                        npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.float64],
                        npt.NDArray[np.float64]]:
    """ 
    Function to calculate the simulated intensities for all the transitions requested, taking into account the simulated offsets.
    This function is used only to apply the selected profile to the already filtered x, y and width values for the transitions.
        
        Args:
            sim: tkinter simulation window required to update the progress bar
            transition_type: type of transition to be simulated (diagram data comes in the x, y, w and satellite data in the xs, ys, ws)
            fit_type: profile type selected in the interface
            xfinal: simulate x values
            x: energy values for each diagram transition to simulate
            y: intensity values for each diagram transition to simulate
            w: natural width values for each diagram transition to simulate
            xs: energy values for each satellite transition in each radiative transition to simulate
            ys: intensity values for each satellite transition in each radiative transition to simulate
            ws: natural width values for each satellite transition in each radiative transition to simulate
            res: experimental resolution to simulate
            energy_values: energy values read from the detector efficiency data
            efficiency_values: efficiency values read from the detector efficiency data
            enoffset: energy offset to simulate
            sat_enoffset: satellite energy offset to simulate
            shkoff_enoffset: shake-off energy offset to simulate
            shkup_enoffset: shake-up energy offset to simulate
        
        Returns:
            yfinal: list of simulated y values for each diagram transition we want to simulate for each of the x values in T
            ytot: list of the simulated total y values for all transitions we want to simulate for each of the x values in T
            yfinals: list of simulated y values for each satellite transition in each digram transition we want to simulate for each of the x values in T
    """
    # Initialize a list to store the final y values for each selected transition to be calulated
    generalVars.yfinal = np.array([[0.0 for _ in range(len(xfinal))] for _ in range(len(x))])
    """
    List of simulated y values for each diagrma transition we want to simulate for each of the x values in T
    """
    # Initialize a list to store the final y values summed across all selected transitions
    generalVars.ytot = np.zeros(len(xfinal))
    """
    List of the simulated total y values for all transitions we want to simulate for each of the x values in T
    """
    # Initialize a list to store the final y values summed across all extra fitting components
    if len(generalVars.extra_fitting_functions) > 0:
        generalVars.yextrastot = np.zeros(len(xfinal))
        """
        List of the simulated total y values for extra fitting components we comfigured for each of the x values in T
        """
    # Initialize a list to store the final y values summed across all selected diagram transitions
    generalVars.ydiagtot = np.zeros(len(xfinal))
    """
    List of the simulated total y values for all diagram transitions we want to simulate for each of the x values in T
    """
    # Initialize a list to store the final y values summed across all selected satellite transitions
    generalVars.ysattot = np.zeros(len(xfinal))
    """
    List of the simulated total y values for all satellite transitions we want to simulate for each of the x values in T
    """
    # Initialize a list to store the final y values summed across all selected shake-off transitions
    generalVars.yshkofftot = np.zeros(len(xfinal))
    """
    List of the simulated total y values for all shake-off transitions we want to simulate for each of the x values in T
    """
    # Initialize a list to store the final y values summed across all selected shake-up transitions
    generalVars.yshkuptot = np.zeros(len(xfinal))
    """
    List of the simulated total y values for all shake-up transitions we want to simulate for each of the x values in T
    """
    # Initialize a list to store the final y values for each satellite transition for each of the selected transitions
    generalVars.yfinals = []
    """
    List of simulated y values for each satellite transition in each digram transition we want to simulate for each of the x values in T
    """
    
    for j in range(len(xs)):
        generalVars.yfinals.append([])
        for i in generalVars.label1:
            generalVars.yfinals[-1].append([0.0 for n in range(len(xfinal))])
            generalVars.yfinals[-1].append([0.0 for n in range(len(xfinal))])
    
    generalVars.yfinals = np.array(generalVars.yfinals)
    
    profile = V
    if fit_type == 'Voigt':
        profile = V
    elif fit_type == 'Lorentzian':
        profile = L
    elif fit_type == 'Gaussian':
        profile = G
    
    b1max = 100 if '+' not in transition_type else 50
    if 'Diagram' in transition_type or 'Auger' in transition_type:
        b1 = 0
        # Loop all the diagram or auger transitions to calculate (y parameter)
        for j, k in enumerate(y):
            # For each transition (high-low levels) loop all the different rates
            # print("Diagram")
            # print(str(x[j]) + "; " + str(y[j]) + "; " + str(w[j]))
            el_idx: int = j // len(generalVars.the_dictionary)
            tr_idx: int = j % len(generalVars.the_dictionary)
            
            # print(f'{el_idx}, {tr_idx}')
            
            for i in range(len(k)):
                # Depending on the profile selected add the y values of the calculated profile to the y values of this transition
                # This profile is calculated across the entire simulated range of x values
                generalVars.yfinal[j] = np.add(generalVars.yfinal[j],
                                               profile(xfinal,
                                                       x[j][i] + enoffset,
                                                       y[j][i] * generalVars.weightFractions[el_idx][tr_idx],
                                                       res,
                                                       w[j][i]))
                
                # Add a proportionate amount of progress to the current progress value
                b1 += b1max / (len(y) * len(k))
                # Set the progress on the interface
                guiVars.progress_var.set(b1) # type: ignore
                # Update the interface to show the progress
                sim.update_idletasks()
            
            # If the transition rates list is not empty then add the y values for this transition into the total y values for all transitions
            if k != []:
                generalVars.ytot = np.add(generalVars.ytot, generalVars.yfinal[j])
                generalVars.ydiagtot = np.add(generalVars.ydiagtot, generalVars.yfinal[j])
        
        # Set and update the progress and progress bar to 100%
        b1 = b1max
        guiVars.progress_var.set(b1) # type: ignore
        sim.update_idletasks()
    
    if 'Satellites' in transition_type:
        b1 = 0 if b1max == 100 else b1max
        # Similar to the diagram transitions but we need an extra for loop to get the rates of each satellite in each diagram transition
        for j, k in enumerate(ys):
            el_idx: int = j // len(generalVars.the_dictionary)
            tr_idx: int = j % len(generalVars.the_dictionary)
            
            for l, m in enumerate(k):
                # print(str(l) + " -> " + generalVars.label1[l])
                # print(str(xs[j][l]) + "; " + str(ys[j][l]) + "; " + str(ws[j][l]))
                for i, n in enumerate(m):
                    if guiVars.separate_offsets.get(): # type: ignore
                        if l < len(generalVars.label1):
                            generalVars.yfinals[j][l] = np.add(generalVars.yfinals[j][l],
                                                                profile(xfinal,
                                                                        xs[j][l][i] + enoffset + shkoff_enoffset,
                                                                        ys[j][l][i] * generalVars.weightFractions[el_idx][tr_idx],
                                                                        res,
                                                                        ws[j][l][i]))
                        else:
                            generalVars.yfinals[j][l] = np.add(generalVars.yfinals[j][l],
                                                                profile(xfinal,
                                                                        xs[j][l][i] + enoffset + shkup_enoffset,
                                                                        ys[j][l][i] * generalVars.weightFractions[el_idx][tr_idx],
                                                                        res,
                                                                        ws[j][l][i]))
                    else:
                        generalVars.yfinals[j][l] = np.add(generalVars.yfinals[j][l],
                                                            profile(xfinal,
                                                                    xs[j][l][i] + enoffset + sat_enoffset,
                                                                    ys[j][l][i] * generalVars.weightFractions[el_idx][tr_idx],
                                                                    res,
                                                                    ws[j][l][i]))

                    b1 += b1max / (len(ys) * len(generalVars.label1) * len(m))
                    guiVars.progress_var.set(b1) # type: ignore
                    sim.update_idletasks()
                
                if m != []:
                    generalVars.ytot = np.add(generalVars.ytot, generalVars.yfinals[j][l])
                    generalVars.ysattot = np.add(generalVars.ysattot, generalVars.yfinals[j][l])
                    if l < len(generalVars.label1):
                        generalVars.yshkofftot = np.add(generalVars.yshkofftot, generalVars.yfinals[j][l])
                    else:
                        generalVars.yshkuptot = np.add(generalVars.yshkuptot, generalVars.yfinals[j][l])
        
        b1 = 100
        guiVars.progress_var.set(b1) # type: ignore
        sim.update_idletasks()

    
    
    # If detector efficiency data was loaded the appropriate weights are applied to the y values
    if guiVars.effic_var.get() != 'No': # type: ignore
        # Get the efficiency values for the x values simulated
        detector_effi, detector_effi_sat, detector_effi_shkoff, detector_effi_shkup = detector_efficiency(energy_values, efficiency_values, xfinal, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset)
        # Modify the y values by the effiency weights
        generalVars.ytot = np.multiply(generalVars.ytot, np.array(detector_effi))
        generalVars.ydiagtot = np.multiply(generalVars.ydiagtot, np.array(detector_effi))
        generalVars.ysattot = np.multiply(generalVars.ysattot, np.array(detector_effi_sat))
        generalVars.yshkofftot = np.multiply(generalVars.yshkofftot, np.array(detector_effi_shkoff))
        generalVars.yshkuptot = np.multiply(generalVars.yshkuptot, np.array(detector_effi_shkup))
        generalVars.yfinal = np.multiply(generalVars.yfinal, np.array(detector_effi))
        generalVars.yfinals = np.multiply(generalVars.yfinals, np.array(detector_effi))
    
    return generalVars.ytot, generalVars.ydiagtot, generalVars.ysattot, generalVars.yshkofftot, \
            generalVars.yshkuptot, generalVars.yfinal, generalVars.yfinals


def add_baseline(transition_type: str):
    if 'Diagram' in transition_type or 'Auger' in transition_type:
        for j, yfinal in enumerate(generalVars.yfinal):
            if yfinal != []:
                generalVars.yfinal[j] = np.add(generalVars.yfinal[j], generalVars.currentBaseline) # type: ignore
        
        generalVars.ydiagtot = np.add(generalVars.ydiagtot, generalVars.currentBaseline)
    
    if 'Satellites' in transition_type:
        for j, yfinals in enumerate(generalVars.yfinals):
            for l, yfinal in enumerate(yfinals):
                if yfinal != []:
                    generalVars.yfinals[j][l] = np.add(generalVars.yfinals[j][l], generalVars.currentBaseline) # type: ignore

        generalVars.ysattot = np.add(generalVars.ysattot, generalVars.currentBaseline)
        generalVars.yshkofftot = np.add(generalVars.yshkofftot, generalVars.currentBaseline)
        generalVars.yshkuptot = np.add(generalVars.yshkuptot, generalVars.currentBaseline)
    
    generalVars.ytot = np.add(generalVars.ytot, generalVars.currentBaseline)
    
    

# Normalization function
def normalizer(y0: float, expy_max: float, ytot_max: float) -> float:
    """ 
    Function to normalize the simulated intensity values
        
        Args:
            y0: simulated background intensity offset
            expy_max: maximum experimental intensity
            ytot_max: maximum simulated intensity
            
        Returns:
            normalization_var: value of the normalization multiplyer for the requested normalization
    """
    # Get the type of normalization selected on the interface
    normalize = guiVars.normalizevar.get() # type: ignore
    """
    Value of the normalization type selected in the interface (No, to Experimental Maximum, to Unity)
    """
    
    normalization_var = 1
    
    try:
        # Calculate the normalization multiplier for the normalization chosen
        if normalize == 'ExpMax':
            normalization_var = expy_max * (1 - y0) / ytot_max # (1 - y0 / expy_max) * expy_max / ytot_max
        elif normalize == 'One':
            normalization_var = (1 - y0) / ytot_max
        elif normalize == 'No':
            normalization_var = 1

    except ValueError:
        messagebox.showerror("No Spectrum", "No Experimental Spectrum was loaded")
    except ZeroDivisionError:
        normalization_var = 1
    
    return normalization_var

# Add the extra fitting components to the previously calculated intensities
def add_fitting_components(xfinal: npt.NDArray[np.float64], function: str,
    xPar: float, ampPar: float, GwidthPar: float, LwidthPar: float = 0.0) -> \
        npt.NDArray[np.float64]:
    """Function to add a fitting component to the total intensity

    Args:
        xfinal (npt.NDArray[np.float64]): final energy values to be simulated
        function (str): function to use for the component
        xPar (float): component x offset
        ampPar (float): component amplitude
        GwidthPar (float): gaussian width
        LwidthPar (float, optional): lorentzian width. Defaults to 0.0.

    Returns:
        npt.NDArray[np.float64]: new intensity values with the added component
    """
    component = np.zeros(len(xfinal))
    
    if function == 'Gaussian':
        component = np.array(G(xfinal, xPar, ampPar, GwidthPar, 0))
    elif function == 'Lorentzian':
        component = np.array(L(xfinal, xPar, ampPar, 0, LwidthPar))
    elif function == 'Voigt':
        component = np.array(V(xfinal, xPar, ampPar, GwidthPar, LwidthPar))

    generalVars.ytot = np.add(generalVars.ytot, component)
    generalVars.yextrastot = np.add(generalVars.yextrastot, component)

    return component