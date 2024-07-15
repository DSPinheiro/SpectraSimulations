"""
Module with the functions used in fitting the simulations
"""

from __future__ import annotations


import data.variables as generalVars
import interface.variables as guiVars

# from interface.plotters import Qsimu_plot

from simulation.preprocessors import process_simulation, process_Msimulation

import simulation.shake as shakes

from simulation.ycalc import y_calculator, normalizer, add_fitting_components, add_baseline

from simulation.bounds import calculate_xfinal

from utils.misc.fileIO import exportFit

from datetime import datetime

from scipy.interpolate import interp1d

from lmfit import Minimizer, Parameters, fit_report
from lmfit.minimizer import MinimizerResult
from lmfit.parameter import Parameters

import numpy as np

from typing import List, Tuple
import numpy.typing as npt


from iminuit import Minuit
from iminuit.cost import template_nll_asy

from functools import partial



#GUI Imports for warnings
from tkinter import messagebox, Toplevel

from matplotlib.pyplot import Axes

# Variable to track the total function evaluations during the fitting
totalEvals = 0
"""
Variable to track the total function evaluations during the fitting
"""

# Maximum total shake that sould be considered during the fitting process
maxTotalShake = 0.6
"""
Value of the maximum total shake that sould be considered during the fitting process. This is approximate
"""

def setMaxTotalShake(shake: float):
    global maxTotalShake
    maxTotalShake = shake

# --------------------------------------------------------- #
#                                                           #
#                     FITTING FUNCTIONS                     #
#                                                           #
# --------------------------------------------------------- #

# Initialize the parameters for fitting
def initializeFitParameters(sat: str, exp_x: List[float] | npt.NDArray[np.float64],
                            exp_y: List[float] | npt.NDArray[np.float64],
                            enoffset: float, sat_enoffset: float, shkoff_enoffset: float,
                            shkup_enoffset: float, y0: float, res: float, quantify: bool):
    """
    Function to initialize the parameters for fitting.
    Extra parameters for user defined components are also fetched from the extra_fitting_functions dictionary.
        
        Args:
            exp_x: list of energy values read from the experimental spectrum
            exp_y: list of intensity values read from the experimental spectrum
            enoffset: simulated energy offset
            sat_enoffset: satellite simulated energy offset
            shkoff_enoffset: shake-off simulated energy offset
            shkup_enoffset: shake-up simulated energy offset
            y0: simulated intensity offset
            res: simulated experimental resolution
        
        Returns:
            params: parameter object with the parameters to be optimized
    """
    # Initialize the parameters to be optimized
    params = Parameters()
    
    # --------------------------------------------------------------------------------------------------------
    # Energy offset parameter
    # We set the range of variation for this parameter during optimization to +- 10% of the simulated x range
    xoff_lim = max(min((max(exp_x) - min(exp_x)) * 0.1, 15.0), 0.1)
    """
    Variation limits for the energy offset parameter
    """
    # Add the parameter to the set of parameters
    params.add('xoff', value=enoffset, min=enoffset - xoff_lim, max=enoffset + xoff_lim)

    if 'Satellites' in sat:
        if guiVars.separate_offsets.get(): # type: ignore  ## tem de ser diferente de None ou False
            # --------------------------------------------------------------------------------------------------------
            # Shake-off energy offset parameter
            # We set the range of variation for this parameter during optimization to +- 10% of the simulated x range
            shkoff_xoff_lim = min((max(exp_x) - min(exp_x)) * 0.1, 15.0)
            """
            Variation limits for the shake-off energy offset parameter
            """
            # Add the parameter to the set of parameters
            params.add('shkoff_xoff', value=shkoff_enoffset, min=shkoff_enoffset - shkoff_xoff_lim, max=shkoff_enoffset + shkoff_xoff_lim)

            # --------------------------------------------------------------------------------------------------------
            # Shake-up energy offset parameter
            # We set the range of variation for this parameter during optimization to +- 10% of the simulated x range
            shkup_xoff_lim = min((max(exp_x) - min(exp_x)) * 0.1, 15.0)
            """
            Variation limits for the shake-off energy offset parameter
            """
            # Add the parameter to the set of parameters
            params.add('shkup_xoff', value=shkup_enoffset, min=shkup_enoffset - shkup_xoff_lim, max=shkup_enoffset + shkup_xoff_lim)
        else:
            # --------------------------------------------------------------------------------------------------------
            # Satellite energy offset parameter
            # We set the range of variation for this parameter during optimization to +- 10% of the simulated x range
            sat_xoff_lim = min((max(exp_x) - min(exp_x)) * 0.1, 15.0)
            """
            Variation limits for the satellite energy offset parameter
            """
            # Add the parameter to the set of parameters
            params.add('sat_xoff', value=sat_enoffset, min=sat_enoffset - sat_xoff_lim, max=sat_enoffset + sat_xoff_lim)

        if guiVars.fit_shake_prob.get(): # type: ignore
            # max_tot = max(generalVars.ytot)
            # max_sat = max([max([max(l) for l in m]) for m in generalVars.yfinals])
            # shake_max_mult = (max_tot / max_sat) / 2.0
            
            avg_shake = shakes.calculateAvgTotalShake()
            shake_max_mult = (maxTotalShake / avg_shake) * 2 ## relação entre o da interface e o teórico
            print(avg_shake)
            print("Max shake multiplyer: " + str(shake_max_mult))
            
            if len(generalVars.shakes_to_fit) == 0:
                for key in generalVars.label1:
                    if key in generalVars.existing_shakeoffs:
                        params.add('shake_amp_' + key, value=1, min=0.1, max=shake_max_mult)
                
                if generalVars.Shakeup_exists:
                    for key in generalVars.label1:
                        if any([key in shakeKey for shakeKey in generalVars.existing_shakeups]):
                            params.add('shakeup_amp_' + key, value=1, min=0.1, max=shake_max_mult)
            else:
                for label in generalVars.shakes_to_fit:
                    if "Shake Off" in label:
                        params.add('shake_amp_' + label.split()[1], value=1, min=0.1, max=shake_max_mult)
                    elif "Shake Up" in label:
                        params.add('shakeup_amp_' + label.split()[1], value=1, min=0.1, max=shake_max_mult)
                        
    
    # --------------------------------------------------------------------------------------------------------
    # y background offset parameter
    # We set the range of variation for this parameter during optimization to +- 10% of the experimental y range
    yoff_lim = max((max(exp_y) - min(exp_y)) * 0.05, 0.1)
    """
    Variation limits for the intensity offset parameter
    """
    # Add the parameter to the set of parameters
    if not quantify:
        params.add('yoff', value=y0, min=y0 - yoff_lim, max=y0 + yoff_lim)

    # --------------------------------------------------------------------------------------------------------
    # Experimental resolution
    # We set the range of variation for this parameter during optimization +- 3 times the initial value
    res_lim = res * 3
    """
    Variation limits for the experimental resolution parameter
    """
    # Add the parameter to the set of parameters
    params.add('res', value=res, min=0.01, max=res + res_lim)
    
    # --------------------------------------------------------------------------------------------------------
    # New maximum y value parameter
    # Add the parameter to the set of parameters
    # if not quantify:
    params.add('ytot_max', value=max(generalVars.ytot), min=0.0, max=1E6)
    
    if len(generalVars.extra_fitting_functions) > 0:
        for key in generalVars.extra_fitting_functions:
            function = key.split("_")[1]
            pars = generalVars.extra_fitting_functions[key]
            # Add the parameters to the set of parameters
            params.add(key + '_xPar', value=pars['xParVal'], min=pars['xParMin'], max=pars['xParMax'])
            params.add(key + '_ampPar', value=pars['ampParVal'], min=pars['ampParMin'], max=pars['ampParMax'])
            
            if function == 'Gaussian':
                if pars['widthRes'] == 0.0:
                    params.add(key + '_GwidthPar', value=pars['GwidthParVal'], min=pars['GwidthParMin'], max=pars['GwidthParMax'])
            elif function == 'Lorentzian':
                if pars['widthRes'] == 0.0:
                    params.add(key + '_LwidthPar', value=pars['LwidthParVal'], min=pars['LwidthParMin'], max=pars['LwidthParMax'])
            elif function == 'Voigt':
                if pars['widthRes'] == 0.0:
                    params.add(key + '_GwidthPar', value=pars['GwidthParVal'], min=pars['GwidthParMin'], max=pars['GwidthParMax'])
                params.add(key + '_LwidthPar', value=pars['LwidthParVal'], min=pars['LwidthParMin'], max=pars['LwidthParMax'])
    
    if quantify:
        for el_idx, weights in enumerate(generalVars.weightFractions):
            # for tr_idx, weight in enumerate(weights):
                # params.add('weight_' + str(el_idx) + '_' + str(tr_idx), value=weight, min=1E-4, max=1.0, vary=weight == 0.5)
            params.add('weight_' + str(el_idx), value=max(weights), min=1E-6, max=1.0)
    
    return params

def initializeFitParameters_minuit(exp_x: List[float] | npt.NDArray[np.float64],
                            exp_y: List[float] | npt.NDArray[np.float64],
                            enoffset: float, sat_enoffset: float, shkoff_enoffset: float,
                            shkup_enoffset: float, y0: float, res: float, quantify: bool):
    
    
    # Initialize the parameters to be optimized
    params = () 
    
    # Define the name of the parameters
    name = ()
    
    # Define limits of the parameters
    limits = []
    
    # --------------------------------------------------------------------------------------------------------
    # Energy offset parameter
    # We set the range of variation for this parameter during optimization to +- 10% of the simulated x range
    xoff_lim = (max(exp_x) - min(exp_x)) * 0.1
    """
    Variation limits for the energy offset parameter
    """
    # Add the parameter to the set of parameters
    params += (enoffset,)
    name += ('xoff',)
    limits.append((enoffset - xoff_lim,enoffset + xoff_lim))
    
    if guiVars.separate_offsets.get(): # type: ignore  ## tem de ser diferente de None ou False
        # --------------------------------------------------------------------------------------------------------
        # Shake-off energy offset parameter
        # We set the range of variation for this parameter during optimization to +- 10% of the simulated x range
        shkoff_xoff_lim = (max(exp_x) - min(exp_x)) * 0.1
        """
        Variation limits for the shake-off energy offset parameter
        """
        # Add the parameter to the set of parameters
        params += (shkoff_enoffset,)
        name += ('shkoff_xoff',)
        limits.append((shkoff_enoffset - shkoff_xoff_lim,shkoff_enoffset + shkoff_xoff_lim))
    

        # --------------------------------------------------------------------------------------------------------
        # Shake-up energy offset parameter
        # We set the range of variation for this parameter during optimization to +- 10% of the simulated x range
        shkup_xoff_lim = (max(exp_x) - min(exp_x)) * 0.1
        """
        Variation limits for the shake-off energy offset parameter
        """
        # Add the parameter to the set of parameters
        params += (shkup_enoffset,)
        name += ('shkup_xoff',)
        limits.append((shkup_enoffset - shkup_xoff_lim,shkup_enoffset + shkup_xoff_lim))
        
    else:
        # --------------------------------------------------------------------------------------------------------
        # Satellite energy offset parameter
        # We set the range of variation for this parameter during optimization to +- 10% of the simulated x range
        sat_xoff_lim = (max(exp_x) - min(exp_x)) * 0.1
        """
        Variation limits for the satellite energy offset parameter
        """
        # Add the parameter to the set of parameters
        params += (sat_enoffset,)
        name += ('sat_xoff',)
        limits.append((sat_enoffset - sat_xoff_lim,sat_enoffset + sat_xoff_lim))
        
    if guiVars.fit_shake_prob.get(): # type: ignore
        # max_tot = max(generalVars.ytot)
        # max_sat = max([max([max(l) for l in m]) for m in generalVars.yfinals])
        # shake_max_mult = (max_tot / max_sat) / 2.0
        
        avg_shake = shakes.calculateAvgTotalShake()
        shake_max_mult = (maxTotalShake / avg_shake) * 2 ## relação entre o da interface e o teórico
        print(avg_shake)
        print("Max shake multiplyer: " + str(shake_max_mult))
        
        if len(generalVars.shakes_to_fit) == 0:
            for key in generalVars.label1:
                if key in generalVars.existing_shakeoffs:
                    params += (1,)
                    name += ('shake_amp_' + key,)
                    limits.append((None,shake_max_mult))
                    
            
            if generalVars.Shakeup_exists:
                for key in generalVars.label1:
                    if any([key in shakeKey for shakeKey in generalVars.existing_shakeups]):
                        params += (1,)
                        name += ('shakeup_amp_' + key,)
                        limits.append((0.1,shake_max_mult))
                        
        else:
            for label in generalVars.shakes_to_fit:
                if "Shake Off" in label:
                    params += (1,)
                    name += ('shake_amp_' + label.split()[1],)
                    limits.append((0.1,shake_max_mult))
                    
                elif "Shake Up" in label:
                    params += (1,)
                    name += ('shakeup_amp_' + label.split()[1],)
                    limits.append((0.1,shake_max_mult))
                    
    # --------------------------------------------------------------------------------------------------------
    # y background offset parameter
    # We set the range of variation for this parameter during optimization to +- 10% of the experimental y range
    yoff_lim = (max(exp_y) - min(exp_y)) * 0.05
    """
    Variation limits for the intensity offset parameter
    """
    # Add the parameter to the set of parameters
    params += (y0,)
    name += ('yoff',)
    limits.append((y0 - yoff_lim,y0 + yoff_lim))

    # --------------------------------------------------------------------------------------------------------
    # Experimental resolution
    # We set the range of variation for this parameter during optimization +- 3 times the initial value
    res_lim = res * 3
    """
    Variation limits for the experimental resolution parameter
    """
    # Add the parameter to the set of parameters
    params += (res,)
    name += ('res',)
    limits.append((0.01,res + res_lim))
    
    # --------------------------------------------------------------------------------------------------------
    # New maximum y value parameter
    # Add the parameter to the set of parameters
    params += (max(generalVars.ytot),)
    name += ('ytot_max',)
    limits.append((0.0,None))
    
    
    if len(generalVars.extra_fitting_functions) > 0:
        for key in generalVars.extra_fitting_functions:
            function = key.split("_")[1]
            pars = generalVars.extra_fitting_functions[key]
            # Add the parameters to the set of parameters
            params += (pars['xParVal'],)
            name += (key + '_xPar',)
            limits.append((pars['xParMin'],pars['xParMax']))
            params += (pars['ampParVal'],)
            name += (key + '_ampPar',)
            limits.append((pars['ampParMin'],pars['ampParMax']))
            
            if function == 'Gaussian':
                if pars['widthRes'] == 0.0:
                    params += (pars['GwidthParVal'],)
                    name += (key + '_GwidthPar',)
                    limits.append((pars['GwidthParMin'],pars['GwidthParMax']))
                    
            elif function == 'Lorentzian':
                if pars['widthRes'] == 0.0:
                    params += (pars['LwidthParVal'],)
                    name +=(key + '_LwidthPar',)
                    limits.append((pars['LwidthParMin'],pars['LwidthParMax']))
                    
            elif function == 'Voigt':
                if pars['widthRes'] == 0.0:
                    params += (pars['GwidthParVal'],)
                    name += (key + '_GwidthPar',)
                    limits.append((pars['GwidthParMin'],pars['GwidthParMax']))
                params += (pars['LwidthParVal'],)
                name += (key + '_LwidthPar',)
                limits.append((pars['LwidthParMin'],pars['LwidthParMax']))   
               
    
    if quantify:
        for el_idx, weights in enumerate(generalVars.weightFractions):
            for tr_idx, weight in enumerate(weights):
                params += (weight,)
                name += ('weight_' + str(el_idx) + '_' + str(tr_idx),)
                limits.append((1E-4, 1.0))
    
    
    return params,name,limits


# Extract the values of the fitted parameters
def fetchFittedParams(result: MinimizerResult, sat: str, quantify: bool = False) -> Tuple[float, float, float, float, float, float, float, dict, dict]:
    """
    Function to extract the values of the fitted parameters. These values are also set in the interface
        
        Args:
            result: result object from the fitting
            
        Returns:
            enoffset: fitted value of the simulated energy offset
            y0: fitted value of the simulated intensity offset
            res: fitted value of the simulated experimental resolution
            ytot_max: fitted value of the simulated maximum intensity
    """
    # Get the fitted value of the x offset
    enoffset: float = result.params['xoff'].value # type: ignore
    # Set the fitted value in the interface
    guiVars.energy_offset.set(enoffset) # type: ignore
    
    if 'Satellites' in sat:
        if guiVars.separate_offsets.get(): # type: ignore
            # Get the fitted value of the shake-off x offset
            shkoff_enoffset: float = result.params['shkoff_xoff'].value # type: ignore
            # Set the fitted value in the interface
            guiVars.shkoff_energy_offset.set(shkoff_enoffset) # type: ignore
            
            # Get the fitted value of the shake-off x offset
            shkup_enoffset: float = result.params['shkup_xoff'].value # type: ignore
            # Set the fitted value in the interface
            guiVars.shkup_energy_offset.set(shkup_enoffset) # type: ignore
            
            sat_enoffset: float = 0.0
        else: 
            # Get the fitted value of the satellite x offset
            sat_enoffset: float = result.params['sat_xoff'].value # type: ignore
            # Set the fitted value in the interface
            guiVars.sat_energy_offset.set(sat_enoffset) # type: ignore
            
            shkoff_enoffset: float = 0.0
            shkup_enoffset: float = 0.0
    else:
        sat_enoffset: float = 0.0
        shkoff_enoffset: float = 0.0
        shkup_enoffset: float = 0.0
    
    shake_amps = {}
    if guiVars.fit_shake_prob.get(): # type: ignore
        for key in result.params: # type: ignore
            if 'shake_amp_' in key:
                shake_amps[key] = result.params[key].value # type: ignore
            if 'shakeup_amp_' in key:
                shake_amps[key] = result.params[key].value # type: ignore
    
    # Get the fitted value of the y offset
    if not quantify:
        y0: float = result.params['yoff'].value # type: ignore
    else:
        y0: float = 0.0
    # Set the fitted value in the interface
    guiVars.yoffset.set(y0) # type: ignore
    
    # Get the fitted value of the experimental resolution
    res: float = result.params['res'].value # type: ignore
    # Set the fitted value in the interface
    guiVars.exp_resolution.set(res) # type: ignore
    
    # Get the fitted value of the fitted total y maximum
    ytot_max: float = result.params['ytot_max'].value # type: ignore
    
    extra_pars = {}
    if len(generalVars.extra_fitting_functions) > 0:
        for key in generalVars.extra_fitting_functions:
            function = key.split("_")[1]
            xPar = result.params[key + '_xPar'].value # type: ignore
            ampPar = result.params[key + '_ampPar'].value # type: ignore
            
            if function == 'Gaussian':
                if key + '_GwidthPar' in result.params: # type: ignore
                    GwidthPar = result.params[key + '_GwidthPar'].value # type: ignore
                else:
                    GwidthPar = res
                
                extra_pars[key] = {
                    'xPar': xPar,
                    'ampPar': ampPar,
                    'GwidthPar': GwidthPar
                }
            elif function == 'Lorentzian':
                if key + '_LwidthPar' in result.params: # type: ignore
                    LwidthPar = result.params[key + '_LwidthPar'].value # type: ignore
                else:
                    LwidthPar = res
                
                extra_pars[key] = {
                    'xPar': xPar,
                    'ampPar': ampPar,
                    'LwidthPar': LwidthPar
                }
            elif function == 'Voigt':
                if key + '_GwidthPar' in result.params: # type: ignore
                    GwidthPar = result.params[key + '_GwidthPar'].value # type: ignore
                else:
                    GwidthPar = res
                
                LwidthPar = result.params[key + '_LwidthPar'].value # type: ignore
                
                extra_pars[key] = {
                    'xPar': xPar,
                    'ampPar': ampPar,
                    'GwidthPar': GwidthPar,
                    'LwidthPar': LwidthPar
                }
    
    if quantify:
        for el_idx, weights in enumerate(generalVars.weightFractions):
            for tr_idx, _ in enumerate(weights):
                # generalVars.weightFractions[el_idx][tr_idx] = result.params['weight_' + str(el_idx) + '_' + str(tr_idx)].value # type: ignore
                generalVars.weightFractions[el_idx][tr_idx] = result.params['weight_' + str(el_idx)].value # type: ignore
    
    
    return enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, y0, res, ytot_max, shake_amps, extra_pars


# Extract the values of the fitted parameters
def fetchFittedParams_minuit(result: Minuit, quantify: bool = False) -> Tuple[float, float, float, float, float, float, float, dict, dict]:
    """
    Function to extract the values of the fitted parameters. These values are also set in the interface
        
        Args:
            result: result object from the fitting
            
        Returns:
            enoffset: fitted value of the simulated energy offset
            y0: fitted value of the simulated intensity offset
            res: fitted value of the simulated experimental resolution
            ytot_max: fitted value of the simulated maximum intensity
    """
    # Get the fitted value of the x offset
    enoffset: float = result.values['xoff'] # type: ignore
    # Set the fitted value in the interface
    guiVars.energy_offset.set(enoffset) # type: ignore
    
    if guiVars.separate_offsets.get(): # type: ignore
        # Get the fitted value of the shake-off x offset
        shkoff_enoffset: float = result.values['shkoff_xoff'] # type: ignore
        # Set the fitted value in the interface
        guiVars.shkoff_energy_offset.set(shkoff_enoffset) # type: ignore
        
        # Get the fitted value of the shake-off x offset
        shkup_enoffset: float = result.values['shkup_xoff']# type: ignore
        # Set the fitted value in the interface
        guiVars.shkup_energy_offset.set(shkup_enoffset) # type: ignore
        
        sat_enoffset: float = 0.0
    else: 
        # Get the fitted value of the satellite x offset
        sat_enoffset: float = result.values['sat_xoff']# type: ignore
        # Set the fitted value in the interface
        guiVars.sat_energy_offset.set(sat_enoffset) # type: ignore
        
        shkoff_enoffset: float = 0.0
        shkup_enoffset: float = 0.0
    
    shake_amps = {}
    if guiVars.fit_shake_prob.get(): # type: ignore  ## boolenao que indica se pretende ajustar as probabilidade de shake
        for key in result.parameters: # type: ignore
            if 'shake_amp_' in key:
                shake_amps[key] = result.values[key]# type: ignore
            if 'shakeup_amp_' in key:
                shake_amps[key] = result.values[key] # type: ignore
    
    # Get the fitted value of the y offset
    y0: float = result.values['yoff'] # type: ignore
    # Set the fitted value in the interface
    guiVars.yoffset.set(y0) # type: ignore
    
    # Get the fitted value of the experimental resolution
    res: float = result.values['res'] # type: ignore
    # Set the fitted value in the interface
    guiVars.exp_resolution.set(res) # type: ignore
    
    # Get the fitted value of the fitted total y maximum
    ytot_max: float = result.values['ytot_max'] # type: ignore
    
    extra_pars = {}
    if len(generalVars.extra_fitting_functions) > 0:
        for key in generalVars.extra_fitting_functions:
            function = key.split("_")[1]
            xPar = result.values[key + '_xPar'] # type: ignore
            ampPar = result.values[key + '_ampPar'] # type: ignore
            
            if function == 'Gaussian':
                if key + '_GwidthPar' in result.parameters: # type: ignore   
                    GwidthPar = result.values[key + '_GwidthPar'] # type: ignore
                else:
                    GwidthPar = res
                
                extra_pars[key] = {
                    'xPar': xPar,
                    'ampPar': ampPar,
                    'GwidthPar': GwidthPar
                }
            elif function == 'Lorentzian':
                if key + '_LwidthPar' in result.parameters: # type: ignore  
                    LwidthPar = result.values[key + '_LwidthPar'] # type: ignore
                else:
                    LwidthPar = res
                
                extra_pars[key] = {
                    'xPar': xPar,
                    'ampPar': ampPar,
                    'LwidthPar': LwidthPar
                }
            elif function == 'Voigt':
                if key + '_GwidthPar' in result.parameters: # type: ignore  
                    GwidthPar = result.values[key + '_GwidthPar'] # type: ignore
                else:
                    GwidthPar = res
                
                LwidthPar = result.values[key + '_LwidthPar'] # type: ignore 
                
                extra_pars[key] = {
                    'xPar': xPar,
                    'ampPar': ampPar,
                    'GwidthPar': GwidthPar,
                    'LwidthPar': LwidthPar
                }
    
    if quantify:
        for el_idx, weights in enumerate(generalVars.weightFractions):
            for tr_idx, _ in enumerate(weights):
                generalVars.weightFractions[el_idx][tr_idx] = result.values['weight_' + str(el_idx) + '_' + str(tr_idx)]
    
    
    return enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, y0, res, ytot_max, shake_amps, extra_pars


# Create the function to be minimized for the fitting
def func2min(params: Parameters, sim: Toplevel,
             exp_x: List[float], exp_y: List[float], num_of_points: int,
             sat: str, peak: str,
             x: List[List[float]], y: List[List[float]], w: List[List[float]],
             xs: List[List[List[float]]], ys: List[List[List[float]]], ws: List[List[List[float]]],
             energy_values: List[float], efficiency_values: List[float], baseline: bool = False):
    """
    Function to be minimized in the fitting
        
        Args:
            params: parameters to be minimized in the function
            sim: tkinter window object to update the progress bar
            exp_x: energy values of the experimental spectrum
            exp_y: intensity values of the experimental spectrum
            num_of_points: number of simulated points
            sat: type of transitions to be simulated (diagram data comes in the x, y, w and satellite data in the xs, ys, ws)
            peak: profile type selected in the interface
            x: energy values for each diagram transition to simulate
            y: intensity values for each diagram transition to simulate
            w: natural width values for each diagram transition to simulate
            xs: energy values for each satellite transition in each radiative transition to simulate
            ys: intensity values for each satellite transition in each radiative transition to simulate
            ws: natural width values for each satellite transition in each radiative transition to simulate
            energy_values: energy values read from the detector efficiency data
            efficiency_values: efficiency values read from the detector efficiency data
            
        Returns:
            list with the differences between the simulated y values and the experimental intensities
    """
    global totalEvals
    # Track the total function evaluations during the fitting
    totalEvals += 1
    
    # Normalizer for the function to match the plotted values
    normalize = guiVars.normalizevar.get() # type: ignore
    
    # Get the parameters from the list of initialized parameters
    xoff = params['xoff'].value
    if 'Satellites' in sat:
        if guiVars.separate_offsets.get(): # type: ignore
            shkoff_xoff = params['shkoff_xoff'].value
            shkup_xoff = params['shkup_xoff'].value
            sat_xoff = 0.0
        else:
            sat_xoff = params['sat_xoff'].value
            shkoff_xoff = 0.0
            shkup_xoff = 0.0
    else:
        sat_xoff = 0.0
        shkoff_xoff = 0.0
        shkup_xoff = 0.0

    if not baseline:
        y0 = params['yoff'].value
        # ytot_max = params['ytot_max'].value
    else:
        y0 = 0.0
        # ytot_max = 1.0
    
    ytot_max = params['ytot_max'].value
    
    res = params['res'].value
    
    
    if baseline:
        for el_idx, weights in enumerate(generalVars.weightFractions):
            for tr_idx, _ in enumerate(weights):
                # generalVars.weightFractions[el_idx][tr_idx] = params['weight_' + str(el_idx) + '_' + str(tr_idx)].value
                generalVars.weightFractions[el_idx][tr_idx] = params['weight_' + str(el_idx)].value
    
    # Console feedback for long fits
    if generalVars.verbose == 0:
        print('\r\x1b[K' + "Function evaluations: " + str(totalEvals), end='')
    elif generalVars.verbose == 1:
        print("Function evaluations: " + str(totalEvals))
    elif generalVars.verbose >= 2:
        print("Function evaluations: " + str(totalEvals))
        params.pretty_print()
    elif generalVars.verbose >= 3:
        print(f'({xoff}, {sat_xoff}, {res}, {y0}, {ytot_max})')
        print(f'({generalVars.weightFractions}) = ', end='')
    
    # Initialize the xfinal from which to interpolate
    x_mx = guiVars.x_max.get() # type: ignore
    x_mn = guiVars.x_min.get() # type: ignore
    
    generalVars.xfinal, bounds = calculate_xfinal(sat, x, w, xs, ws, x_mx, x_mn, res, xoff, sat_xoff, shkoff_xoff, shkup_xoff, num_of_points, 0, baseline) #np.array(np.linspace(min(exp_x), max(exp_x), num=num_of_points))
    
    if guiVars.fit_shake_prob.get(): # type: ignore
        shake_amps = {}
        for key in params:
            if 'shake_amp_' in key:
                shake_amps[key] = params[key].value
            if 'shakeup_amp_' in key:
                shake_amps[key] = params[key].value

        print(shake_amps)
        
        # shake_pars = {}
        # for key in shakes.existing_shakeups:
        #     shake_pars[key] = shake_amps["shakeup_amp_" + key.split("_")[0]] * shakes.get_shakeup(key.split("_")[0], "10", int(key.split("_")[1]))

        # for key in shakes.existing_shakeoffs:
        #     shake_pars[key] = shake_amps["shake_amp_" + key] * shakes.get_shakeoff(key)
        
        # for key1 in shakes.shake_relations:
        #     shake1 = shake_pars[key1]
        #     for key2 in shakes.shake_relations[key1]:
        #         shake2 = shake_pars[key2]
        #         if shakes.shake_relations[key1][key2] == ">" and shake1 <= shake2:
        #             print("Invalid parameter values for shake probabilities " + key1 + " and " + key2)
        #             res = []
        #             for g, h in enumerate(exp_x):
        #                 if h > min(generalVars.xfinal) and h < max(generalVars.xfinal):
        #                     res.append(np.sqrt(float_info.max / 2.0))
        #             res = (np.array(res) / (len(res) * 1E+75)).tolist()
                    
        #             print(sum(np.square(res)))
                    
        #             return res
        #         elif shakes.shake_relations[key1][key2] == "<=" and shake1 > shake2:
        #             print("Invalid parameter values for shake probabilities " + key1 + " and " + key2)
        #             res = []
        #             for g, h in enumerate(exp_x):
        #                 if h > min(generalVars.xfinal) and h < max(generalVars.xfinal):
        #                     res.append(np.sqrt(float_info.max / 2.0))
        #             res = (np.array(res) / (len(res) * 1E+75)).tolist()
                    
        #             print(sum(np.square(res)))
                    
        #             return res
        
        if guiVars.choice_var.get()[:2] == "M_": # type: ignore
            x, y, w, xs, ys, ws, _ = process_Msimulation(shake_amps, False) ##  para vários estados de carga
        else:
            x, y, w, xs, ys, ws, _ = process_simulation(shake_amps, False) ## consideramos apenas o átomo
    
    
    # Calculate the simulated values
    generalVars.ytot, generalVars.ydiagtot, generalVars.ysattot, generalVars.yshkofftot, \
        generalVars.yshkuptot, generalVars.yfinal, generalVars.yfinals = y_calculator(sim, sat, peak, generalVars.xfinal, x, y, w, xs, ys, ws, res, energy_values, efficiency_values, xoff, sat_xoff, shkoff_xoff, shkup_xoff)
    
    if len(generalVars.extra_fitting_functions) > 0:
        for key in generalVars.extra_fitting_functions:
            function = key.split("_")[1]
            
            xPar = params[key + "_xPar"].value
            ampPar = params[key + "_ampPar"] * max(generalVars.ytot)
            
            if function == 'Gaussian':
                if generalVars.extra_fitting_functions[key]['widthRes'] == 0.0:
                    GwidthPar = params[key + "_GwidthPar"].value
                else:
                    GwidthPar = res
                add_fitting_components(generalVars.xfinal, function, xPar, ampPar, GwidthPar)
            elif function == 'Lorentzian':
                if generalVars.extra_fitting_functions[key]['widthRes'] == 0.0:
                    LwidthPar = params[key + "_LwidthPar"].value
                else:
                    LwidthPar = res
                add_fitting_components(generalVars.xfinal, function, xPar, ampPar, 0.0, LwidthPar)
            elif function == 'Voigt':
                if generalVars.extra_fitting_functions[key]['widthRes'] == 0.0:
                    GwidthPar = params[key + "_GwidthPar"].value
                else:
                    GwidthPar = res
                LwidthPar = params[key + "_LwidthPar"].value
                add_fitting_components(generalVars.xfinal, function, xPar, ampPar, GwidthPar, LwidthPar)
            
    
    # Calculate the normalization multiplier
    # normalization_var = normalizer(y0, max(exp_y), max(generalVars.ytot)) # ytot_max)# if not baseline else max(generalVars.ytot))
    normalization_var = normalizer(y0, max(exp_y), ytot_max)# if not baseline else max(generalVars.ytot))
    
    # Interpolate the data
    norm_simu = (np.array(generalVars.ytot) * normalization_var) + y0
    exp_interpolate = interp1d(exp_x, exp_y, kind='cubic')
    
    if generalVars.verbose >= 3:
        print(exp_x)
        print(exp_y)
        print(f'exp: {max(exp_y)}, exp_interp: {max(exp_interpolate([x_ for x_ in generalVars.xfinal if x_ >= min(exp_x) and x_ <= max(exp_x)]))}, simu: {max(generalVars.ytot)}, mult: {normalization_var} = {max(norm_simu)}')
    
    """
    Interpolated function of the simulated points
    """
    
    # Initialize the interpolated y values
    y_interp: List[float] = []
    """
    List for the interpolated values of the simulated y at each energy value of the experimental spectrum
    """
    exp_y_f: List[float] = []
    
    if baseline:
        for g, h in enumerate(generalVars.xfinal):
            if h > min(exp_x) and h < max(exp_x):
                if any([h >= bound[0] and h <= bound[1] for bound in bounds]):
                    y_interp.append(norm_simu[g])
                    # exp_y_f.append(exp_interpolate(h))
                    # "if" to prevent interpolation overshoots
                    exp_y_f.append(exp_interpolate(h) if exp_interpolate(h) <= max(exp_y) else max(exp_y))
    else:
        for g, h in enumerate(generalVars.xfinal):
            if h > min(exp_x) and h < max(exp_x):
                # Get the values of the interpolation for the experimental x values
                y_interp.append(norm_simu[g])
                # exp_y_f.append(exp_interpolate(h))
                # "if" to prevent interpolation overshoots
                exp_y_f.append(exp_interpolate(h) if exp_interpolate(h) <= max(exp_y) else max(exp_y))
    
    
    if generalVars.verbose >= 3:
        print(np.array(y_interp))
        print(np.array(exp_y_f))
        
        # Qsimu_plot(guiVars.elementList, sat, guiVars.graph_area, normalization_var, y0, True, baseline) # type: ignore
        
        # guiVars._f.canvas.draw() # type: ignore
        
        # sim.update_idletasks()
        
    
    if generalVars.verbose >= 2:
        if normalize == 'One':
            print(sum(np.square(np.array(y_interp) - np.array(exp_y_f) / max(exp_y_f))))
        else:
            print(sum(np.square(np.array(y_interp) - np.array(exp_y_f))))
    
        print(f'Simu max: {max(y_interp)}; Exp max: {max(exp_y_f)}')
    
    # Return the normalized function
    if normalize == 'One':
        return (np.array(y_interp) - np.array(exp_y_f)) / max(exp_y_f)
    else:
        return np.array(y_interp) - np.array(exp_y_f)


# Create the function to be minimized for the fitting
def func2min_minuit(params: tuple, name: tuple, sim: Toplevel,
             exp_x: List[float], exp_y: List[float], num_of_points: int,
             sat: str, peak: str,
             x: List[List[float]], y: List[List[float]], w: List[List[float]],
             xs: List[List[List[float]]], ys: List[List[List[float]]], ws: List[List[List[float]]],
             energy_values: List[float], efficiency_values: List[float], baseline: bool = False):
    """
    Function to be minimized in the fitting
        
        Args:
            params: valeu of the parameters to be minimized in the function
            name : name of the parameters to be minimized in the function
            
            sim: tkinter window object to update the progress bar
            exp_x: energy values of the experimental spectrum
            exp_y: intensity values of the experimental spectrum
            num_of_points: number of simulated points
            sat: type of transitions to be simulated (diagram data comes in the x, y, w and satellite data in the xs, ys, ws)
            peak: profile type selected in the interface
            x: energy values for each diagram transition to simulate
            y: intensity values for each diagram transition to simulate
            w: natural width values for each diagram transition to simulate
            xs: energy values for each satellite transition in each radiative transition to simulate
            ys: intensity values for each satellite transition in each radiative transition to simulate
            ws: natural width values for each satellite transition in each radiative transition to simulate
            energy_values: energy values read from the detector efficiency data
            efficiency_values: efficiency values read from the detector efficiency data
            
        Returns:
            list with the differences between the simulated y values and the experimental intensities
    """  
    
    global totalEvals
    # Track the total function evaluations during the fitting
    totalEvals += 1
    # Console feedback for long fits
    print('\r\x1b[K' + "Function evaluations: " + str(totalEvals), end='')
    # print("Function evaluations: " + str(totalEvals), end='')
    
    # Normalizer for the function to match the plotted values
    normalize = guiVars.normalizevar.get() # type: ignore
    
    # Get the parameters from the list of initialized parameters
    ind_xoff = name.index('xoff')
    xoff = params[ind_xoff]
    
    if guiVars.separate_offsets.get(): # type: ignore
        ind_shkoff_xoff  = name.index('shkoff_xoff')
        shkoff_xoff = params[ind_shkoff_xoff]
        ind_shkup_xoff = name.index('shkup_xoff')
        shkup_xoff = params[ind_shkup_xoff]
        sat_xoff = 0.0
    else:
        ind_sat_xoff = name.index('sat_xoff')
        sat_xoff = params[ind_sat_xoff]
        shkoff_xoff = 0.0
        shkup_xoff = 0.0
    ind_yo = name.index('yoff')
    y0 = params[ind_yo]
    ind_res = name.index('res')
    res = params[ind_res]
    ind_ytot_max = name.index('ytot_max')
    ytot_max = params[ind_ytot_max]
    
    # print(" (", end='')
    # print(xoff, end='')
    # print(" , ", end='')
    # print(sat_xoff, end='')
    # print(" , ", end='')
    # print(res, end='')
    # print(" , ", end='')
    # print(y0, end='')
    # print(" , ", end='')
    # print(ytot_max, end='')
    # print(")")
    # print(") = ", end='')
    
    # Initialize the xfinal from which to interpolate
    x_mx = guiVars.x_max.get() # type: ignore
    x_mn = guiVars.x_min.get() # type: ignore
    
    generalVars.xfinal, bounds = calculate_xfinal(sat, x, w, xs, ws, x_mx, x_mn, res, xoff, sat_xoff, shkoff_xoff, shkup_xoff, num_of_points, 0, baseline) #np.array(np.linspace(min(exp_x), max(exp_x), num=num_of_points))
    
    if baseline:
        exp_base = interp1d(generalVars.xfinal, generalVars.currentBaseline, 'cubic')
        eff_y = np.array(exp_y) - exp_base(generalVars.exp_x)
    else:
        eff_y = np.array(exp_y)
    
    
    if guiVars.fit_shake_prob.get(): # type: ignore
        shake_amps = {}
        for key in params:
            if 'shake_amp_' in key:
                ind_key = name.index(key)
                shake_amps[key] = params[ind_key]
            if 'shakeup_amp_' in key:
                ind_key1 = name.index(key)
                shake_amps[key] = params[ind_key1]

        print(shake_amps)
        
        if guiVars.choice_var.get()[:2] == "M_": # type: ignore
            x, y, w, xs, ys, ws, _ = process_Msimulation(shake_amps, False) ##  para vários estados de carga
        else:
            x, y, w, xs, ys, ws, _ = process_simulation(shake_amps, False) ## consideramos apenas o átomo
    
    
    if baseline:
        for el_idx, weights in enumerate(generalVars.weightFractions):
            for tr_idx, _ in enumerate(weights):
                weight_idx = name.index('weight_' + str(el_idx) + '_' + str(tr_idx))
                generalVars.weightFractions[el_idx][tr_idx] = params[weight_idx]
    
    
    # Calculate the simulated values
    generalVars.ytot, generalVars.ydiagtot, generalVars.ysattot, generalVars.yshkofftot, \
        generalVars.yshkuptot, generalVars.yfinal, generalVars.yfinals = y_calculator(sim, sat, peak, generalVars.xfinal, x, y, w, xs, ys, ws, res, energy_values, efficiency_values, xoff, sat_xoff, shkoff_xoff, shkup_xoff)
    
    if len(generalVars.extra_fitting_functions) > 0:
        for key in generalVars.extra_fitting_functions:
            function = key.split("_")[1]
            ind_xPar = name.index(key + "_xPar")
            xPar = params[ind_xPar]
            ind_ampPar = name.index(key + "_ampPar")
            ampPar = params[ind_ampPar ] * max(generalVars.ytot)
            
            if function == 'Gaussian':
                if generalVars.extra_fitting_functions[key]['widthRes'] == 0.0:
                    ind_GwidthPar = name.index(key + "_GwidthPar")
                    GwidthPar = params[ind_GwidthPar]
                else:
                    GwidthPar = res
                add_fitting_components(generalVars.xfinal, function, xPar, ampPar, GwidthPar)
            elif function == 'Lorentzian':
                if generalVars.extra_fitting_functions[key]['widthRes'] == 0.0:
                    ind_LwidthPar = name.index(key + "_LwidthPar")
                    LwidthPar = params[ind_LwidthPar]
                else:
                    LwidthPar = res
                add_fitting_components(generalVars.xfinal, function, xPar, ampPar, 0.0, LwidthPar)
            elif function == 'Voigt':
                if generalVars.extra_fitting_functions[key]['widthRes'] == 0.0:
                    ind_GwidthPar = name.index(key + "_GwidthPar")
                    GwidthPar = params[ind_GwidthPar]
                else:
                    GwidthPar = res
                ind_LwidthPar = name.index(key + "_LwidthPar")
                LwidthPar = params[ind_LwidthPar]
                add_fitting_components(generalVars.xfinal, function, xPar, ampPar, GwidthPar, LwidthPar)
            
    
    # Calculate the normalization multiplier
    normalization_var = normalizer(y0, max(eff_y), ytot_max)
    
    # Interpolate the data
    f_interpolate = interp1d(generalVars.xfinal, np.array(np.array(generalVars.ytot) * normalization_var) + y0, kind='cubic')
    
    """
    Interpolated function of the simulated points
    """
        
    # Initialize the interpolated y values
    y_interp: List[float] = []     ## pode conter valores yfinal, regra geral nunca nenhum vai coincidir
    """
    List for the interpolated values of the simulated y at each energy value of the experimental spectrum
    """
    exp_y_f: List[float] = [] ## filtro para os valores experimentais
    
    for g, h in enumerate(exp_x):  
        if h > min(generalVars.xfinal) and h < max(generalVars.xfinal):  
            # Get the values of the interpolation for the experimental x values
            y_interp.append(f_interpolate(h)) 
            exp_y_f.append(eff_y[g])  ## para cada valor de energia experimmental vai buscar o seu valor de intensidade correspondente
    
    var = np.sqrt(exp_y_f)
    neg_log1 = template_nll_asy(mu=exp_y_f, n=y_interp, mu_var=var) 
    return (neg_log1)
    

# Calculate the residues, reduced chi^2 and update the respective graph
def calculateResidues(exp_x: List[float], exp_y: List[float], exp_sigma: List[float],
                      xfinal: List[float] | npt.NDArray[np.float64], normalization_var: float,
                      normalize: str, y0: float, number_of_fit_variables: int, residues_graph: Axes):
    """
    Function to calculate the residues, reduced chi^2 and update the respective graph
        
        Args:
            exp_x: energy values from the experimental spectrum
            exp_y: intensity values from the experimental spectrum
            exp_sigma: error values from the experimental spectrum
            xfinal: list of the simulated x values
            normalization_var: normalization multiplyer
            normalize: normalization type chosen
            y0: simulated intensity offset
            number_of_fit_variables: total number of fitted variables
            residues_graph: matplotlib plot object where to plot the residue data
        
        Returns:
            Nothing, the residues are plotted and the chi^2 value is updated in the variables module
    """
    # Initialize a list for the interpolated experimental y values
    y_interp = [0.0 for i in range(len(exp_x))]
    # Interpolate the total plotted intensities
    f_interpolate = interp1d(np.array(xfinal), (np.array(generalVars.ytot) * normalization_var) + y0, kind='cubic')
    
    # Initialize a list for the residue values
    y_res = [0.0 for x in range(len(exp_x))]
    # Temporary variable for the chi sum to calculate the chi^2
    chi_sum = 0
    
    # Loop the experimental x values
    for g, h in enumerate(exp_x):
        if h >= min(xfinal) and h <= max(xfinal):
            # Get the interpolated y values
            y_interp[g] = f_interpolate(h)
            # Calculate the chi sum from the interpolated values
            if normalize == 'ExpMax' or normalize == 'No':
                y_res[g] = (exp_y[g] - y_interp[g])
                chi_sum += (y_res[g] ** 2) / ((exp_sigma[g]**2))
            elif normalize == 'One':
                y_res[g] = ((exp_y[g] / max(exp_y)) - y_interp[g])
                chi_sum += (y_res[g] ** 2) / ((exp_sigma[g] / max(exp_y))**2)
    
    # Calculate the reduced chi^2 value
    generalVars.chi_sqrd = chi_sum / (len(exp_x) - number_of_fit_variables)
    # Plot the residues
    residues_graph.plot(exp_x, y_res)
    # Print the value in the console
    print("Valor Manual Chi", generalVars.chi_sqrd)
    # Put the chi^2 value in the plot legend
    residues_graph.legend(title="Red. $\chi^2$ = " + "{:.5f}".format(generalVars.chi_sqrd))


# Function to obtain report - iminuit
def report_minuit(result,num_data,num_var):
    report = "[[Minuit Fit Statistics]]\n"
    report += "fitting method = template_nll_asy\n"
    report += f"Valid Minimum = {result.valid}\n"
    report += f"Funcion value at minimum = {result.fval}\n"
    report += f"covariance matrix accurate = {result.accurate}\n"
    report += f"data points = {len(num_data)}\n"
    report += f"variabels = {(num_var)}\n"
    report += "[[Variables]]\n"
    for name in(result.parameters):
        report += f"{name} = {result.values[name]}, Hesse Err = {result.errors[name]},{abs(result.errors[name]) / abs(result.values[name])}% , limits = {result.limits[name]}\n"
    report += "[[Correlations]]\n"
    for name in(result.parameters):
        for name1 in(result.parameters):
            report += f"C({name},{name1}) = {result.covariance[name][name1]}\n"
    
    return report

def execute_autofit(sim: Toplevel, sat: str, enoffset: float, sat_enoffset: float,
                    shkoff_enoffset: float, shkup_enoffset: float, y0: float, res: float,
                    num_of_points: int, peak: str, x: List[List[float]], y: List[List[float]],
                    w: List[List[float]], xs: List[List[List[float]]], ys: List[List[List[float]]],
                    ws: List[List[List[float]]], energy_values: List[float],
                    efficiency_values: List[float], time_of_click: datetime, quantify: bool = False):
    """
    Execute the autofit for the current simulation to the loaded experimental values.
    Fitting is currently performed with the LMfit package.
    
        Args:
            sat: simulation type selected in the interface (diagram, satellite, auger)
            enoffset: energy offset user value from the interface
            sat_enoffset: satellite energy offset user value from the interface
            shkoff_enoffset: shake-off energy offset user value from the interface
            shkup_enoffset: shake-up energy offset user value from the interface
            y0: intensity offset user value from the interface
            res: energy resolution user value from the interface
            num_of_points: user value for the number of points to simulate from the interface
            peak: profile type selected in the interface
            x: energy values for each of the possible transitions
            y: intensity values for each of the possible transitions
            w: width values for each of the possible transitions
            xs: energy values for each of the possible radiative sattelite transitions for each radiative transition
            ys: intensity values for each of the possible radiative sattelite transitions for each radiative transition
            ws: width values for each of the possible radiative sattelite transitions for each radiative transition
            energy_values: list of energy values in the efficiency file
            efficiency_values: list of efficiency values in the efficiency file
            time_of_click: timestamp to use when saving files for this simulation plot
        
        Returns:
            number_of_fit_variables: number of fitted variables
            enoffset: fitted energy offset
            y0: fitted intensity offset
            res: fitted energy resolution
            ytot_max: fitted intensity maximum value
            normalization_var: fitted normalization multiplier to normalize intensity when plotting
    """
    # Console feedback for long fits
    print("Starting AutoFit...")
    
    # Calculate the energy values for the fitted parameters
    x_mx = guiVars.x_max.get() # type: ignore
    x_mn = guiVars.x_min.get() # type: ignore
    
    generalVars.xfinal, bounds = calculate_xfinal(sat, x, w, xs, ws, x_mx, x_mn, res, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, num_of_points, 0, quantify) #np.array(np.linspace(min(exp_x), max(exp_x), num=num_of_points))
    
    # Initialize the fit parameters
    if quantify:
        exp_base = interp1d(generalVars.xfinal, generalVars.currentBaseline, 'cubic')
        # guiVars.graph_area.plot(generalVars.exp_x, exp_base(generalVars.exp_x)) # type: ignore
        # guiVars._f.canvas.draw() # type: ignore
        
        eff_y = np.array(generalVars.exp_y) - exp_base(generalVars.exp_x)
        eff_y = [y if y >= 0.0 else 0.0 for y in eff_y]
    else:
        eff_y = np.array(generalVars.exp_y)
    
    params= initializeFitParameters(sat, generalVars.exp_x, eff_y, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, y0, res, quantify)
    
    # Minimize the function for the initialized parameters
    number_of_fit_variables = len(params.valuesdict())
    minner = Minimizer(func2min, params, fcn_args=(sim, generalVars.exp_x, eff_y, num_of_points, sat, peak, x, y, w, xs, ys, ws, energy_values, efficiency_values, quantify))
    
    result = minner.minimize()
    
    # Get the fitted values
    enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, y0, res, ytot_max, shake_amps, extra_pars = fetchFittedParams(result, sat, quantify)

    # Update the fitted weights on the correct interface entry
    if quantify:
        generalVars.total_weight = sum([max(fractions) for fractions in generalVars.weightFractions])
        
        for el_idx, element in enumerate(guiVars.elementList):
            guiVars.quantityLabels[el_idx].set((max(generalVars.weightFractions[el_idx]) / generalVars.total_weight) * guiVars.alphaEntries[el_idx].get())
    
    # Reprocess the effective line intensities for the fitted satelite probabilities
    if len(shake_amps) > 0:
        if guiVars.choice_var.get()[:2] == "M_": # type: ignore
            x, y, w, xs, ys, ws, _ = process_Msimulation(shake_amps, False)
        else:
            x, y, w, xs, ys, ws, _ = process_simulation(shake_amps, False)

    
    # Calculate the normalizer multiplier for the fitted parameters
    normalization_var = normalizer(y0, max(eff_y), max(generalVars.ytot)) # ytot_max)
    
    # Calculate the intensities for the fitted parameters
    generalVars.ytot, generalVars.ydiagtot, generalVars.ysattot, generalVars.yshkofftot, \
        generalVars.yshkuptot, generalVars.yfinal, generalVars.yfinals = y_calculator(sim, sat, peak, generalVars.xfinal, x, y, w, xs, ys, ws, res, energy_values, efficiency_values, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset)
    
    if len(extra_pars) > 0:
        generalVars.yextras.resize((len(generalVars.extra_fitting_functions), len(generalVars.xfinal)))
        generalVars.yextrastot.resize(len(generalVars.xfinal))
        for i, key in enumerate(extra_pars):
            function = key.split("_")[1]
            
            xPar = extra_pars[key]["xPar"]
            ampPar = extra_pars[key]["ampPar"] * max(generalVars.ytot)
            
            if function == 'Gaussian':
                GwidthPar = extra_pars[key]["GwidthPar"]
                generalVars.yextras[i] = add_fitting_components(generalVars.xfinal, function, xPar, ampPar, GwidthPar)
            elif function == 'Lorentzian':
                LwidthPar = extra_pars[key]["LwidthPar"]
                generalVars.yextras[i] = add_fitting_components(generalVars.xfinal, function, xPar, ampPar, 0.0, LwidthPar)
            elif function == 'Voigt':
                GwidthPar = extra_pars[key]["GwidthPar"]
                LwidthPar = extra_pars[key]["LwidthPar"]
                generalVars.yextras[i] = add_fitting_components(generalVars.xfinal, function, xPar, ampPar, GwidthPar, LwidthPar)
    
    if quantify:
        add_baseline(sat)
    
    if generalVars.verbose >= 3:
        print(generalVars.weightFractions)
    
    # Ask to save the fit
    if messagebox.askyesno("Fit Saving", "Do you want to save this fit?"):
        # Get the report on the fit
        report: str = fit_report(result)
        # Export the fit to file
        exportFit(time_of_click, report)
    
    return number_of_fit_variables, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, y0, res, ytot_max, normalization_var, extra_pars


def execute_autofit_minuit(sim: Toplevel, sat: str, enoffset: float, sat_enoffset: float,
                    shkoff_enoffset: float, shkup_enoffset: float, y0: float, res: float,
                    num_of_points: int, peak: str, x: List[List[float]], y: List[List[float]],
                    w: List[List[float]], xs: List[List[List[float]]], ys: List[List[List[float]]],
                    ws: List[List[List[float]]], energy_values: List[float],
                    efficiency_values: List[float], time_of_click: datetime, quantify: bool = False):
    """
    Execute the autofit for the current simulation to the loaded experimental values.
    Fitting is currently performed with the LMfit package.
    
        Args:
            sat: simulation type selected in the interface (diagram, satellite, auger)
            enoffset: energy offset user value from the interface
            sat_enoffset: satellite energy offset user value from the interface
            shkoff_enoffset: shake-off energy offset user value from the interface
            shkup_enoffset: shake-up energy offset user value from the interface
            y0: intensity offset user value from the interface
            res: energy resolution user value from the interface
            num_of_points: user value for the number of points to simulate from the interface
            peak: profile type selected in the interface
            x: energy values for each of the possible transitions
            y: intensity values for each of the possible transitions
            w: width values for each of the possible transitions
            xs: energy values for each of the possible radiative sattelite transitions for each radiative transition
            ys: intensity values for each of the possible radiative sattelite transitions for each radiative transition
            ws: width values for each of the possible radiative sattelite transitions for each radiative transition
            energy_values: list of energy values in the efficiency file
            efficiency_values: list of efficiency values in the efficiency file
            time_of_click: timestamp to use when saving files for this simulation plot
        
        Returns:
            number_of_fit_variables: number of fitted variables
            enoffset: fitted energy offset
            y0: fitted intensity offset
            res: fitted energy resolution
            ytot_max: fitted intensity maximum value
            normalization_var: fitted normalization multiplier to normalize intensity when plotting
    """
    # Console feedback for long fits
    print("Starting AutoFit...")
    
    # Initialize the fit parameters
    if quantify:
        exp_base = interp1d(generalVars.exp_x, generalVars.currentBaseline, 'cubic')
        eff_y = np.array(generalVars.exp_y) - exp_base(generalVars.exp_x)
        params,name,limits= initializeFitParameters_minuit(generalVars.exp_x, eff_y, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, y0, res, quantify)
    else:
        params,name,limits= initializeFitParameters_minuit(generalVars.exp_x, generalVars.exp_y, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, y0, res, quantify)
    
    # Minimize the function for the initialized parameters
    number_of_fit_variables = len(params)
    
    fun_min_minuit = partial(func2min_minuit,name = name, sim = sim , exp_x = list(generalVars.exp_x), exp_y = list(generalVars.exp_y), num_of_points=num_of_points, sat = sat, peak = peak, x = x, y = y, w = w, xs = xs, ys = ys, ws = ws, energy_values = energy_values, efficiency_values = efficiency_values, baseline = quantify)
    
    m = Minuit(fun_min_minuit, params, name = name) # type: ignore
    
    Minuit.errordef = Minuit.LIKELIHOOD ## para garantir que os erros são calculados de forma correta
    m.limits = limits
    result = m.migrad()
    
    
    # Get the fitted values
    enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, y0, res, ytot_max, shake_amps, extra_pars = fetchFittedParams_minuit(result)

    # Reprocess the effective line intensities for the fitted satelite probabilities
    if len(shake_amps) > 0:
        if guiVars.choice_var.get()[:2] == "M_": # type: ignore
            x, y, w, xs, ys, ws, _ = process_Msimulation(shake_amps, False)
        else:
            x, y, w, xs, ys, ws, _ = process_simulation(shake_amps, False)

    
    # Calculate the energy values for the fitted parameters
    x_mx = guiVars.x_max.get() # type: ignore
    x_mn = guiVars.x_min.get() # type: ignore
    
    generalVars.xfinal, bounds = calculate_xfinal(sat, x, w, xs, ws, x_mx, x_mn, res, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, num_of_points, 0, quantify) #np.array(np.linspace(min(exp_x), max(exp_x), num=num_of_points))
    
    # Calculate the normalizer multiplier for the fitted parameters
    if quantify:
        normalization_var = normalizer(y0, max(np.array(generalVars.exp_y) - generalVars.currentBaseline), ytot_max)
    else:
        normalization_var = normalizer(y0, max(generalVars.exp_y), ytot_max)
    
    # Calculate the intensities for the fitted parameters
    generalVars.ytot, generalVars.ydiagtot, generalVars.ysattot, generalVars.yshkofftot, \
        generalVars.yshkuptot, generalVars.yfinal, generalVars.yfinals = y_calculator(sim, sat, peak, generalVars.xfinal, x, y, w, xs, ys, ws, res, energy_values, efficiency_values, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset)
    
    if len(extra_pars) > 0:
        generalVars.yextras.resize((len(generalVars.extra_fitting_functions), len(generalVars.xfinal)))
        generalVars.yextrastot.resize(len(generalVars.xfinal))
        for i, key in enumerate(extra_pars):
            function = key.split("_")[1]
            
            xPar = extra_pars[key]["xPar"]
            ampPar = extra_pars[key]["ampPar"] * max(generalVars.ytot)
            
            if function == 'Gaussian':
                GwidthPar = extra_pars[key]["GwidthPar"]
                generalVars.yextras[i] = add_fitting_components(generalVars.xfinal, function, xPar, ampPar, GwidthPar)
            elif function == 'Lorentzian':
                LwidthPar = extra_pars[key]["LwidthPar"]
                generalVars.yextras[i] = add_fitting_components(generalVars.xfinal, function, xPar, ampPar, 0.0, LwidthPar)
            elif function == 'Voigt':
                GwidthPar = extra_pars[key]["GwidthPar"]
                LwidthPar = extra_pars[key]["LwidthPar"]
                generalVars.yextras[i] = add_fitting_components(generalVars.xfinal, function, xPar, ampPar, GwidthPar, LwidthPar)
    
    add_baseline(sat)
    
    # Ask to save the fit
    if messagebox.askyesno("Fit Saving", "Do you want to save this fit?"):
        # Get the report on the fit
        report: str = report_minuit(result,generalVars.exp_x,number_of_fit_variables)
        # Export the fit to file
        exportFit(time_of_click, report)
        
    print(result)
    return number_of_fit_variables, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, y0, res, ytot_max, normalization_var, extra_pars
