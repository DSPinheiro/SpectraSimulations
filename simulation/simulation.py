"""
Module with functions that group the data to be simulated and send it to the plotters in the correct format.
"""
from __future__ import annotations


import data.variables as generalVars
import interface.variables as guiVars


from pathlib import Path

import numpy as np

from scipy.interpolate import interp1d


from data.wrappers import UpdateElementsMCDFData

# Transition lines to simulate updater functions
from simulation.lineUpdater import updateRadTransitionVals, updateAugTransitionVals, \
                                    updateRadCSTrantitionsVals, updateAugCSTransitionsVals

# Transition simulation functions
from simulation.diagram import stick_diagram
from simulation.satellite import stick_satellite
from simulation.auger import stick_auger

# preprocessing functions to determine x, y, w lists
from simulation.preprocessors import process_simulation, process_quantify_simu, process_Msimulation, \
                                        process_ionization_shake_data


# Bad selection reporting functions
from utils.experimental.detector import initialize_detectorEfficiency

from simulation.ycalc import y_calculator, normalizer, add_fitting_components
from simulation.bounds import calculate_xfinal, mergeXFinals
from simulation.fitting import calculateResidues, execute_autofit,execute_autofit_minuit


from interface.plotters import simu_plot, Esimu_plot, Msimu_plot, Qsimu_plot, format_legend
from interface.experimental import initialize_expElements, unpackExpSpectrum, update_expElements


from datetime import datetime

#GUI Imports for warnings
from tkinter import messagebox

from matplotlib.pyplot import Axes
from matplotlib.figure import Figure

from tkinter import Toplevel

from typing import Dict, Any


# ---------------------------------------------------------------------- #
#                                                                        #
#  FUNCTIONS TO PREPARE THE SIMULATION DATA AND SEND IT TO THE PLOTERS   #
#                                                                        #
# ---------------------------------------------------------------------- #


def make_stick(sim: Toplevel | None, graph_area: Axes | None):
    """
    Function to calculate the values that will be sent to the stick plotter function.
        
        Args:
            sim: tkinter simulation window to update the progress bar
            graph_area: matplotlib graph to plot the simulated transitions
        
        Returns:
            Nothing, the sticks that need to be plotted are calculated and the data is sent to the plotting functions.
    """
    # Variable for the total number of plotted transitions
    num_of_transitions = 0
    # Variable for the number of transitions that were selected but no rates were found
    bad_selection = 0
    
    sat = guiVars.satelite_var.get() # type: ignore
    beam = guiVars.excitation_energy.get() # type: ignore
    FWHM = guiVars.excitation_energyFWHM.get() # type: ignore
    
    # Reset the 2J colors dictionary if needed
    if guiVars.JJ_colors.get(): # type: ignore
        generalVars.colors_2J = {}
    
    # Radiative and Auger code has to be split due to the different dictionaries used for the transitions
    if sat != 'Auger':
        # Loop possible radiative transitions
        for transition in generalVars.the_dictionary:
            # If the transition was selected
            if generalVars.the_dictionary[transition]["selected_state"]:
                # Filter the radiative and satellite rates corresponding to this transition
                num_of_transitions, low_level, high_level, diag_stick_val, sat_stick_val = updateRadTransitionVals(transition, num_of_transitions, beam, FWHM)
                
                # -------------------------------------------------------------------------------------------
                if 'Diagram' in sat:
                    bad_selection, graph_area = stick_diagram(graph_area, diag_stick_val, transition, bad_selection)
                if 'Satellites' in sat:
                    bad_selection, graph_area = stick_satellite(sim, graph_area, sat_stick_val, transition, low_level, high_level, bad_selection)
            
    else:
        # Loop possible auger transitions
        for transition in generalVars.the_aug_dictionary:
            # If the transition is selected
            if generalVars.the_aug_dictionary[transition]["selected_state"]:
                # Filter the auger rates for this transition
                num_of_transitions, aug_stick_val = updateAugTransitionVals(transition, num_of_transitions)
                
                bad_selection, graph_area = stick_auger(graph_area, aug_stick_val, transition, bad_selection)
    
    # Set the labels for the axis
    if graph_area:
        graph_area.set_xlabel('Energy (eV)')
        graph_area.set_ylabel('Intensity (arb. units)')

    if num_of_transitions == 0:
        messagebox.showerror("No Transition", "No transition was chosen")
    elif bad_selection != 0:
        messagebox.showerror("Wrong Transition", "You chose " + str(bad_selection) + " invalid transition(s)")
    
    return graph_area


def make_simulation(sim: Toplevel | None, f: Figure | None, graph_area: Axes | None,
                    time_of_click: datetime, plotSimu: bool = True, quantify: bool = False,
                    headless_config: Dict[str, Any] = {}):
    """
    Function to calculate the values that will be sent to the plot function.
        
        Args:
            sim: tkinter simulation window to update the progress bar
            f: matplotlib figure object where to plot the data
            graph_area: matplotlib graph to plot the simulated transitions
            time_of_click: timestamp to use when saving files for this simulation plot
        
        Returns:
            Nothing, the simulation is performed, the transitions are plotted and the interface is updated
    """
    if sim:
        sat = guiVars.satelite_var.get() # type: ignore
    else:
        if len(headless_config) == 0:
            print("Error running headless mode: No configuration passed to headless_config parameter.")
            print("Stopping....")
            exit(-1)
        else:
            if 'satelite_var' in headless_config:
                sat = headless_config['satelite_var']
            else:
                print("Error: No transition type chosen.")
                print("Please define the value for the satelite_var in the headless_config dictionary.")
                print("Stopping....")
                exit(-1)
    
    print("Transitions to Simulate:")
    if 'Auger' not in sat:
        for transition in generalVars.the_dictionary:
            if generalVars.the_dictionary[transition]['selected_state']:
                print(generalVars.the_dictionary[transition]['readable_name'])
    else:
        for transition in generalVars.the_dictionary:
            if generalVars.the_aug_dictionary[transition]['selected_state']:
                print(generalVars.the_aug_dictionary[transition]['readable_name'])
    
    if quantify:
        x, y, w, xs, ys, ws, bad_selection = process_quantify_simu()
        
        if generalVars.verbose >= 3:
            for el_idx, el in enumerate(guiVars.elementList):
                print(f'{el}: {x[(el_idx * len(generalVars.the_dictionary)):((el_idx + 1) * len(generalVars.the_dictionary))]}')
    else:
        x, y, w, xs, ys, ws, bad_selection, xe, ye, we, xse, yse, wse, \
        bad_selection_e = process_simulation(prompt=plotSimu, headless_config=headless_config)
    
    # -------------------------------------------------------------------------------------------
    # Get the values from interface entries
    if sim:
        num_of_points = guiVars.number_points.get() # type: ignore
        x_mx = guiVars.x_max.get() # type: ignore
        x_mn = guiVars.x_min.get() # type: ignore
        enoffset = guiVars.energy_offset.get() # type: ignore
        sat_enoffset = guiVars.sat_energy_offset.get() # type: ignore
        sep_offsets = guiVars.separate_offsets.get() # type: ignore
        shkoff_enoffset = guiVars.shkoff_energy_offset.get() # type: ignore
        shkup_enoffset = guiVars.shkup_energy_offset.get() # type: ignore
        res = guiVars.exp_resolution.get() # type: ignore
        
        load = guiVars.loadvar.get() # type: ignore
        effic_file_name = guiVars.effic_var.get() # type: ignore
        peak = guiVars.type_var.get() # type: ignore
        y0 = guiVars.yoffset.get() # type: ignore
        
        norm = None
        autofit = guiVars.autofitvar.get() # type: ignore
        
        beam = None
    else:
        if 'number_points' in headless_config:
            num_of_points = headless_config['number_points']
        else:
            print("Error: No number of simulation points chosen.")
            print("Please define the value for the number_points in the headless_config dictionary.")
            print("Stopping....")
            exit(-1)
        if 'x_max' in headless_config:
            x_mx = headless_config['x_max']
        else:
            print("Error: No maximum simulation x value chosen.")
            print("Please define the value for the x_max in the headless_config dictionary.")
            print("Stopping....")
            exit(-1)
        if 'x_min' in headless_config:
            x_mn = headless_config['x_min']
        else:
            print("Error: No minimum simulation x value chosen.")
            print("Please define the value for the x_min in the headless_config dictionary.")
            print("Stopping....")
            exit(-1)
        if 'energy_offset' in headless_config:
            enoffset = headless_config['energy_offset']
        else:
            print("Error: No simulation energy offset chosen.")
            print("Please define the value for the energy_offset in the headless_config dictionary.")
            print("Stopping....")
            exit(-1)
        if 'sat_energy_offset' in headless_config:
            sat_enoffset = headless_config['sat_energy_offset']
        else:
            print("Error: No energy offset for all satelites chosen.")
            print("Please define the value for the sat_energy_offset in the headless_config dictionary.")
            print("Stopping....")
            exit(-1)
        if 'seperate_offsets' in headless_config:
            sep_offsets = headless_config['seperate_offsets']
        else:
            print("Error: No flag for separating the energy satelite offsets chosen.")
            print("Please define the value for the seperate_offsets in the headless_config dictionary.")
            print("Stopping....")
            exit(-1)
        if 'shkoff_energy_offset' in headless_config:
            shkoff_enoffset = headless_config['shkoff_energy_offset']
        else:
            print("Error: No energy offset for shake-off chosen.")
            print("Please define the value for the shkoff_energy_offset in the headless_config dictionary.")
            print("Stopping....")
            exit(-1)
        if 'shkup_energy_offset' in headless_config:
            shkup_enoffset = headless_config['shkup_energy_offset']
        else:
            print("Error: No energy offset for shake-up chosen.")
            print("Please define the value for the shkup_energy_offset in the headless_config dictionary.")
            print("Stopping....")
            exit(-1)
        if 'exp_resolution' in headless_config:
            res = headless_config['exp_resolution']
        else:
            print("Error: No simulated experimental broadening chosen.")
            print("Please define the value for the exp_resolution in the headless_config dictionary.")
            print("Stopping....")
            exit(-1)

        
        if 'loadvar' in headless_config:
            load = headless_config['loadvar']
        else:
            print("Error: No path to experimental spectrum chosen.")
            print("Please define the value for the loadvar in the headless_config dictionary (use 'No' for no spectrum).")
            print("Stopping....")
            exit(-1)
        if 'effic_var' in headless_config:
            effic_file_name = headless_config['effic_var']
        else:
            print("Error: No path to detector efficiency function chosen.")
            print("Please define the value for the effic_var in the headless_config dictionary (use 'No' for no function).")
            print("Stopping....")
            exit(-1)
        if 'type_var' in headless_config:
            peak = headless_config['type_var']
        else:
            print("Error: No transition line profile chosen.")
            print("Please define the value for the type_var in the headless_config dictionary (available: 'Voigt', 'Lorentzian', 'Gaussian').")
            print("Stopping....")
            exit(-1)
        if 'yoffset' in headless_config:
            y0 = headless_config['yoffset']
        else:
            print("Error: No intensity offset chosen.")
            print("Please define the value for the yoffset in the headless_config dictionary.")
            print("Stopping....")
            exit(-1)
        
        
        if 'normalizevar' in headless_config:
            norm = headless_config['normalizevar']
        else:
            print("Error: No normalization type was chosen.")
            print("Please define the value for the normalizevar in the headless_config dictionary (available: 'ExpMax', 'One', 'No').")
            print("Stopping....")
            exit(-1)
        if 'autofitvar' in headless_config:
            autofit = headless_config['autofitvar']
        else:
            print("Error: No flag for autofitting was chosen.")
            print("Please define the value for the autofitvar in the headless_config dictionary (available: 'LMFit', 'iminuit').")
            print("Stopping....")
            exit(-1)
        if 'excitation_energy' in headless_config:
            beam = headless_config['excitation_energy']
        else:
            print("Error: No excitation energy chosen.")
            print("Please define the value for the excitation_energy in the headless_config dictionary.")
            print("Stopping....")
            exit(-1)

    
    # ---------------------------------------------------------------------------------------------------------------
    # Load and plot the experimental spectrum
    generalVars.exp_x = []
    generalVars.exp_y = []
    generalVars.exp_sigma = []
    
    # Initialize needed elements if we have loaded an experimental spectrum
    
    if load != 'No' and not quantify:
        graph_area, exp_spectrum, _ = initialize_expElements(f, load, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, num_of_points, x_mx, x_mn, guiVars.normalizevar.get()) # type: ignore
    elif quantify:
        update_expElements(guiVars.graph_area, guiVars._residues_graph, load, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, num_of_points, x_mx, x_mn, guiVars.normalizevar.get(), quantify) # type: ignore

    # ---------------------------------------------------------------------------------------------------------------
    # Calculate the xfinal set of x values to use in the simulation

    if 'Diagram' in sat or 'Satellites' in sat or 'Auger' in sat:
        generalVars.xfinal, bounds = calculate_xfinal(sat, x, w, xs, ws, x_mx, x_mn, res, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, num_of_points, bad_selection, quantify)
    if 'Excitation' in sat or 'ESat' in sat:
        xfinal, bounds = calculate_xfinal(sat, xe, we, xse, wse, x_mx, x_mn, res, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, num_of_points, bad_selection, quantify)
        
        if 'Diagram' in sat or 'Satellites' in sat or 'Auger' in sat:
            generalVars.xfinal = mergeXFinals(generalVars.xfinal, xfinal)
            # print(generalVars.xfinal)
        else:
            generalVars.xfinal = xfinal
    
    if generalVars.verbose >= 3:
        print(bounds)
    
    # ---------------------------------------------------------------------------------------------------------------
    # Read the efficiency file if it was loaded
    energy_values = []
    efficiency_values = []
    
    if effic_file_name != 'No':
        energy_values, efficiency_values = initialize_detectorEfficiency(effic_file_name)
    
    # Initialize element weight fractions
    if quantify:
        generalVars.weightFractions = [[0.5 if generalVars.the_dictionary[tr]["selected_state"] else 0.0 for tr in generalVars.the_dictionary] for _ in guiVars.elementList]
        # generalVars.weightFractions = [[0.5] * len(generalVars.the_dictionary)] * len(guiVars.elementList)
    else:
        if len(generalVars.rad_EXC) > 0:
            generalVars.weightFractions = [[1.0 for _ in generalVars.the_dictionary] for _ in generalVars.rad_EXC]
        else:
            generalVars.weightFractions = [[1.0 for _ in generalVars.the_dictionary]]
    
    # ---------------------------------------------------------------------------------------------------------------
    # Calculate the final y values
    if 'Excitation' in sat or 'ESat' in sat:
        generalVars.ytot_exc, generalVars.ydiagtot_exc, generalVars.ysattot_exc, generalVars.yshkofftot_exc, \
        generalVars.yshkuptot_exc, generalVars.yfinal_exc, generalVars.yfinals_exc = \
            y_calculator(sim, sat, peak, generalVars.xfinal, xe, ye, we, xse, yse, wse, res, \
                energy_values, efficiency_values, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset,
                separate_offsets=sep_offsets, effic_var=effic_file_name)
    
    generalVars.ytot, generalVars.ydiagtot, generalVars.ysattot, generalVars.yshkofftot, \
        generalVars.yshkuptot, generalVars.yfinal, generalVars.yfinals = \
            y_calculator(sim, sat, peak, generalVars.xfinal, x, y, w, xs, ys, ws, res, \
                energy_values, efficiency_values, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset,
                separate_offsets=sep_offsets, effic_var=effic_file_name)
    
    # Add the extra fitting components
    if len(generalVars.extra_fitting_functions) > 0:
        # TODO: Add extra fitting function to the excitation lines (not really needed right now)
        generalVars.yextras.resize((len(generalVars.extra_fitting_functions), len(generalVars.xfinal)))
        print(generalVars.extra_fitting_functions)
        for i, key in enumerate(generalVars.extra_fitting_functions):
            function = key.split("_")[1]
            pars = generalVars.extra_fitting_functions[key]
            
            if function == 'Gaussian':
                generalVars.yextras[i] = add_fitting_components(generalVars.xfinal, function, pars['xParVal'], pars['ampParVal'] * max(generalVars.ytot), pars['GwidthParVal'])
            elif function == 'Lorentzian':
                generalVars.yextras[i] = add_fitting_components(generalVars.xfinal, function, pars['xParVal'], pars['ampParVal'] * max(generalVars.ytot), 0.0, pars['LwidthParVal'])
            elif function == 'Voigt':
                generalVars.yextras[i] = add_fitting_components(generalVars.xfinal, function, pars['xParVal'], pars['ampParVal'] * max(generalVars.ytot), pars['GwidthParVal'], pars['LwidthParVal'])
    
    # ---------------------------------------------------------------------------------------------------------------
    # Calculate the normalization multiplyer
    if load != 'No':
        unpackExpSpectrum(load, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, num_of_points, x_mx, x_mn, quantify)
        if quantify:
            exp_base = interp1d(generalVars.xfinal, generalVars.currentBaseline, 'cubic')
            eff_y = np.array(generalVars.exp_y) - exp_base(generalVars.exp_x)
        else:
            eff_y = np.array(generalVars.exp_y)
        
        if 'Excitation' in sat or 'ESat' in sat:
            normalization_var = normalizer(y0, max(eff_y), max(max(generalVars.ytot), max(generalVars.ytot_exc)),
                                           normalizevar=norm)
        else:
            normalization_var = normalizer(y0, max(eff_y), max(generalVars.ytot),
                                           normalizevar=norm)
    else:
        if sim:
            # If we try to normalize without an experimental spectrum
            if guiVars.normalizevar.get() == 'ExpMax': # type: ignore
                messagebox.showwarning("No experimental spectrum is loaded", "Choose different normalization option")
                # Reset the normalizer to the default
                guiVars.normalizevar.set('No') # type: ignore
            
        if 'Excitation' in sat or 'ESat' in sat:
            normalization_var = normalizer(y0, 1, max(max(generalVars.ytot), max(generalVars.ytot_exc)),
                                           normalizevar=norm)
        else:
            normalization_var = normalizer(y0, 1, max(generalVars.ytot), normalizevar=norm)
    
    # ---------------------------------------------------------------------------------------------------------------
    # Autofit:
    number_of_fit_variables = 0
    if autofit == 'LMFit':
        # We can only fit if we have an experimental spectrum
        if load != 'No':
            number_of_fit_variables, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, \
            y0, res, ytot_max, normalization_var, extra_pars = \
                execute_autofit(sim, sat, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, \
                    y0, res, num_of_points, peak, x, y, w, xs, ys, ws, energy_values, \
                    efficiency_values, time_of_click, quantify, \
                    xe, ye, we, xse, yse, wse)
        else:
            if sim:
                messagebox.showerror("Error", "Autofit is only avaliable if an experimental spectrum is loaded")
    elif autofit == 'iminuit':
        # We can only fit if we have an experimental spectrum
        if load != 'No':
            number_of_fit_variables, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, \
            y0, res, ytot_max, normalization_var, extra_pars = \
                execute_autofit_minuit(sim, sat, enoffset, sat_enoffset, shkoff_enoffset, \
                    shkup_enoffset, y0, res, num_of_points, peak, x, y, w, xs, ys, ws, \
                    energy_values, efficiency_values, time_of_click, quantify, \
                    xe, ye, we, xse, yse, wse)
        else:
            if sim:
                messagebox.showerror("Error", "Autofit is only avaliable if an experimental spectrum is loaded")
    
    # ------------------------------------------------------------------------------------------------------------------------
    # Plot the selected lines
    if quantify:
        graph_area = Qsimu_plot(guiVars.elementList, sat, guiVars.graph_area, normalization_var, y0, plotSimu, quantify) # type: ignore
    else:
        graph_area = simu_plot(sat, graph_area, normalization_var, y0, plotSimu, excitation_energy=beam)
        if 'Excitation' in sat or 'ESat' in sat:
            graph_area = Esimu_plot(generalVars.rad_EXC, sat, graph_area, normalization_var, y0, plotSimu,
                                    excitation_energy=beam)
    # ------------------------------------------------------------------------------------------------------------------------
    # Calculate the residues
    if load != 'No':
        calculateResidues(generalVars.exp_x, generalVars.exp_y, generalVars.exp_sigma, generalVars.xfinal, normalization_var, guiVars.normalizevar.get(), y0, number_of_fit_variables, guiVars._residues_graph) # type: ignore
    
    if plotSimu and graph_area:
        # ------------------------------------------------------------------------------------------------------------------------
        # Set the axis labels
        graph_area.set_ylabel('Intensity (arb. units)')
        graph_area.legend(title=generalVars.element_name, title_fontsize='large')
        if load == 'No':
            graph_area.set_xlabel('Energy (eV)')
        
        # ------------------------------------------------------------------------------------------------------------------------
        # Automatic legend formating
        format_legend(graph_area)
    
    return graph_area



def make_Mstick(sim: Toplevel | None, graph_area: Axes | None):
    """
    Function to calculate the values that will be sent to the stick plotter function when simulating a mixture of charge states.
        
        Args:
            sim: tkinter simulation window to update the progress bar
            graph_area: matplotlib graph to plot the simulated transitions
        
        Returns:
            Nothing, the sticks that need to be plotted are calculated and the data is sent to the plotting functions.
    """
    # Variable for the total number of plotted transitions
    num_of_transitions = 0
    # Variable for the number of transitions that were selected but no rates were found
    bad_selection = 0
    
    sat: str = guiVars.satelite_var.get() # type: ignore
    beam: float = guiVars.excitation_energy.get() # type: ignore
    FWHM: float = guiVars.excitation_energyFWHM.get() # type: ignore
    
    # Reset the 2J colors dictionary if needed
    if guiVars.JJ_colors.get(): # type: ignore
        generalVars.colors_2J = {}
    
    # Radiative and Auger code has to be split due to the different dictionaries used for the transitions
    if sat != 'Auger':
        # Initialize the charge states we have to loop through
        charge_states = generalVars.rad_PCS + generalVars.rad_NCS

        # Loop the charge states
        for cs_index, cs in enumerate(charge_states):
            # Initialize the mixture value chosen for this charge state
            mix_val = '0.0'
            # Flag to check if this is a negative or positive charge state
            ncs = False

            # Check if this charge state is positive or negative and get the mix value
            if cs_index < len(generalVars.rad_PCS):
                mix_val = guiVars.PCS_radMixValues[cs_index].get()
            else:
                mix_val = guiVars.NCS_radMixValues[cs_index - len(generalVars.rad_PCS)].get()
                ncs = True
            
            # Check if the mix value is not 0, otherwise no need to plot the transitions for this charge state
            if mix_val != '0.0':
                # Loop the possible radiative transitions
                for transition in generalVars.the_dictionary:
                    # If the transition is selected
                    if generalVars.the_dictionary[transition]["selected_state"]:
                        # Filter the radiative and satellite rates for this transition and charge state
                        num_of_transitions, low_level, high_level, diag_stick_val, sat_stick_val = updateRadCSTrantitionsVals(transition, num_of_transitions, ncs, cs)
                        
                        if 'Diagram' in sat:
                            bad_selection, graph_area = stick_diagram(graph_area, diag_stick_val, transition, bad_selection, cs)
                        if 'Satellites' in sat:
                            bad_selection, graph_area = stick_satellite(sim, graph_area, sat_stick_val, transition, low_level, high_level, bad_selection, cs)
                    
    else:
        # Initialize the charge states we have to loop through
        charge_states = generalVars.aug_PCS + generalVars.aug_NCS

        # Loop the charge states
        for cs_index, cs in enumerate(charge_states):
            # Initialize the mixture value chosen for this charge state
            mix_val = '0.0'
            # Flag to check if this is a negative or positive charge state
            ncs = False

            # Check if this charge state is positive or negative and get the mix value
            if cs_index < len(generalVars.aug_PCS):
                mix_val = guiVars.PCS_augMixValues[cs_index].get()
            else:
                mix_val = guiVars.NCS_augMixValues[cs_index - len(generalVars.aug_PCS)].get()
                ncs = True
            
            # Check if the mix value is not 0, otherwise no need to plot the transitions for this charge state
            if mix_val != '0.0':
                # Loop the possible auger transitions
                for transition in generalVars.the_aug_dictionary:
                    # If the transition is selected
                    if generalVars.the_aug_dictionary[transition]["selected_state"]:
                        # Filter the auger rates for this transition and charge state
                        num_of_transitions, aug_stick_val = updateAugCSTransitionsVals(transition, num_of_transitions, ncs, cs)
                        
                        bad_selection, graph_area = stick_auger(graph_area, aug_stick_val, transition, bad_selection, cs)

    # Set the labels for the axis
    if graph_area:
        graph_area.set_xlabel('Energy (eV)')
        graph_area.set_ylabel('Intensity (arb. units)')

    if num_of_transitions == 0:
        messagebox.showerror("No Transition", "No transition was chosen")
    elif bad_selection != 0:
        messagebox.showerror("Wrong Transition", "You chose " + str(bad_selection) + " invalid transition(s)")
    
    return graph_area


def make_Msimulation(sim: Toplevel | None, f: Figure | None, graph_area: Axes | None, time_of_click: datetime):
    """
    Function to calculate the values that will be sent to the plot function.
        
        Args:
            sim: tkinter simulation window to update the progress bar
            f: matplotlib figure object where to plot the data
            graph_area: matplotlib graph to plot the simulated transitions
            time_of_click: timestamp to use when saving files for this simulation plot
            
        Returns:
            Nothing, the simulation is performed, the transitions are plotted and the interface is updated
    """
    sat = guiVars.satelite_var.get() # type: ignore

    x, y, w, xs, ys, ws, bad_selection, ploted_cs = process_Msimulation()
    
    # -------------------------------------------------------------------------------------------
    # Calculate the xfinal set of x values to use in the simulation
    enoffset = guiVars.energy_offset.get() # type: ignore
    sat_enoffset = guiVars.sat_energy_offset.get() # type: ignore
    shkoff_enoffset = guiVars.shkoff_energy_offset.get() # type: ignore
    shkup_enoffset = guiVars.shkup_energy_offset.get() # type: ignore
    res = guiVars.exp_resolution.get() # type: ignore
    num_of_points = guiVars.number_points.get() # type: ignore
    x_mx = guiVars.x_max.get() # type: ignore
    x_mn = guiVars.x_min.get() # type: ignore
    
    calculate_xfinal(sat, x, w, xs, ws, x_mx, x_mn, res, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, num_of_points, bad_selection, False)

    # ---------------------------------------------------------------------------------------------------------------
    # Load and plot the experimental spectrum
    generalVars.exp_x = []
    generalVars.exp_y = []
    generalVars.exp_sigma = []
    min_exp_lim = 0
    max_exp_lim = 0
    
    # If we have loaded an experimental spectrum
    load = guiVars.loadvar.get() # type: ignore
    
    if load != 'No':
        graph_area, exp_spectrum, _ = initialize_expElements(f, load, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, num_of_points, x_mx, x_mn, guiVars.normalizevar.get()) # type: ignore

    # ---------------------------------------------------------------------------------------------------------------
    # Read the efficiency file if it was loaded
    efficiency_values = []
    energy_values = []
    
    effic_file_name = guiVars.effic_var.get() # type: ignore
    
    if effic_file_name != 'No':
        energy_values, efficiency_values = initialize_detectorEfficiency(effic_file_name)
    
    # ---------------------------------------------------------------------------------------------------------------
    # Calculate the final y values
    peak = guiVars.type_var.get() # type: ignore
    
    generalVars.ytot, generalVars.ydiagtot, generalVars.ysattot, generalVars.yshkofftot, \
        generalVars.yshkuptot, generalVars.yfinal, generalVars.yfinals = y_calculator(sim, sat, peak, generalVars.xfinal, x, y, w, xs, ys, ws, res, energy_values, efficiency_values, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset)
    
    # Add the extra fitting components
    if len(generalVars.extra_fitting_functions) > 0:
        generalVars.yextras.resize((len(generalVars.extra_fitting_functions), len(generalVars.xfinal)))
        for i, key in enumerate(generalVars.extra_fitting_functions):
            function = key.split("_")[1]
            pars = generalVars.extra_fitting_functions[key]
            
            if function == 'Gaussian':
                generalVars.yextras[i] = add_fitting_components(generalVars.xfinal, function, pars['xParVal'], pars['ampParVal'] * max(generalVars.ytot), pars['GwidthParVal'])
            elif function == 'Lorentzian':
                generalVars.yextras[i] = add_fitting_components(generalVars.xfinal, function, pars['xParVal'], pars['ampParVal'] * max(generalVars.ytot), 0.0, pars['LwidthParVal'])
            elif function == 'Voigt':
                generalVars.yextras[i] = add_fitting_components(generalVars.xfinal, function, pars['xParVal'], pars['ampParVal'] * max(generalVars.ytot), pars['GwidthParVal'], pars['LwidthParVal'])
    
    # ---------------------------------------------------------------------------------------------------------------
    # Calculate the normalization multiplyer
    y0 = guiVars.yoffset.get() # type: ignore
    
    if load != 'No':
        normalization_var = normalizer(y0, max(generalVars.exp_y), max(generalVars.ytot))
    else:
        # If we try to normalize without an experimental spectrum
        if guiVars.normalizevar.get() == 'ExpMax': # type: ignore
            messagebox.showwarning("No experimental spectrum is loaded", "Choose different normalization option")
            # Reset the normalizer to the default
            guiVars.normalizevar.set('No') # type: ignore
        normalization_var = normalizer(y0, 1, max(generalVars.ytot))
    
    # ---------------------------------------------------------------------------------------------------------------
    # Autofit:
    number_of_fit_variables = 0
    if guiVars.autofitvar.get() == 'LMFit': # type: ignore
        # We can only fit if we have an experimental spectrum
        if load != 'No':
            number_of_fit_variables, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, y0, res, ytot_max, normalization_var, extra_pars = execute_autofit(sim, sat, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, y0, res, num_of_points, peak, x, y, w, xs, ys, ws, energy_values, efficiency_values, time_of_click)
        else:
            messagebox.showerror("Error", "Autofit is only avaliable if an experimental spectrum is loaded")
    elif guiVars.autofitvar.get() == 'iminuit': # type: ignore
        # We can only fit if we have an experimental spectrum
        if load != 'No':
            number_of_fit_variables, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, y0, res, ytot_max, normalization_var, extra_pars = execute_autofit_minuit(sim, sat, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, y0, res, num_of_points, peak, x, y, w, xs, ys, ws, energy_values, efficiency_values, time_of_click)
        else:
            messagebox.showerror("Error", "Autofit is only avaliable if an experimental spectrum is loaded")
    
    # ------------------------------------------------------------------------------------------------------------------------
    # Plot the selected lines
    if graph_area:
        graph_area = Msimu_plot(ploted_cs, sat, graph_area, normalization_var, y0) # type: ignore

    # ------------------------------------------------------------------------------------------------------------------------
    # Calculate the residues
    if load != 'No':
        calculateResidues(generalVars.exp_x, generalVars.exp_y, generalVars.exp_sigma, generalVars.xfinal, normalization_var, guiVars.normalizevar.get(), y0, number_of_fit_variables, guiVars._residues_graph) # type: ignore
    
    if graph_area:
        # ------------------------------------------------------------------------------------------------------------------------
        # Set the axis labels
        graph_area.set_ylabel('Intensity (arb. units)')
        graph_area.legend(title=generalVars.element_name, title_fontsize='large')
        if load == 'No':
            graph_area.set_xlabel('Energy (eV)')
        
        # ------------------------------------------------------------------------------------------------------------------------
        # Automatic legend formating
        format_legend(graph_area)
    
    return graph_area



# Profile plotter. Plots each transition, applying the selected profile
def simulate(dir_path: Path, sim: Toplevel | None, f: Figure | None, graph_area: Axes | None,
             excitation: bool = False, quantify: bool = False, headless_config: Dict[str, Any] = {}):
    """
    Profile plotter function. Plots each transition, applying the selected profile
        
        Args:
            sim: tkinter simulation window to update the progress bar
            f: matplotlib figure object where to plot the data
            graph_area: matplotlib graph to plot the simulated transitions
            
        Returns:
            Nothing, the simulation is performed, the transitions are plotted and the interface is updated
    """
    if not sim or not f or not graph_area:
        print("Simulation started with tk gui handles as None. Running headless mode.")
        if len(headless_config) == 0:
            print("Error starting headless mode: No configuration passed to headless_config parameter.")
            print("Stopping....")
            exit(-1)
    
    if quantify:
        UpdateElementsMCDFData(dir_path, guiVars.elementList)
        guiVars.choice_var.set('Simulation') # type: ignore
    
    
    # Get the timestamp to use when saving files for this simulation plot
    time_of_click = datetime.now()
    """
    Timestamp to use when saving files for this simulation plot
    """
    
    generalVars.exp_x = None
    """
    List of experimental spectrum energies
    """
    generalVars.exp_y = None
    """
    List of experimental spectrum intensities
    """
    
    if graph_area:
        # Reset the plot with the configurations selected
        graph_area.clear()
        if guiVars.yscale_log.get() == 'Ylog': # type: ignore
            graph_area.set_yscale('log')
        if guiVars.xscale_log.get() == 'Xlog': # type: ignore
            graph_area.set_xscale('log')
        
        graph_area.legend(title=generalVars.element_name)
    
    number_of_fit_variables = 0
    
    if sim:
        spectype = guiVars.choice_var.get() # type: ignore
    elif 'choice_var' in headless_config:
        spectype = headless_config['choice_var']
    else:
        print("Error: No simulation type chosen in the headless_config dictionary.")
        print("Please define the key 'choice_var' in this parameter.")
        print("Stopping....")
        exit(-1)
    
    # Setup shake and cross section data
    process_ionization_shake_data(excitation, quantify)
    
    # --------------------------------------------------------------------------------------------------------------------------
    if spectype == 'Stick':
        graph_area = make_stick(sim, graph_area)
    # --------------------------------------------------------------------------------------------------------------------------
    elif spectype == 'M_Stick':
        graph_area = make_Mstick(sim, graph_area)
    # --------------------------------------------------------------------------------------------------------------------------
    elif spectype == 'Simulation':
        if sim:
            make_grid = False
        else:
            if 'make_grid' in headless_config:
                make_grid = headless_config['make_grid']
            else:
                print("Error: No flag for making a simulation grid was chosen.")
                print("Please define the key make_grid in the headless_config parameter.")
                print("Stopping....")
                exit(-1)
        
        if not make_grid:
            graph_area = make_simulation(sim, f, graph_area, time_of_click, quantify=quantify,
                                         headless_config=headless_config)
        else:
            # CODE FOR AUTOMATIC BEAM ENERGY INCREMENTATION
            import numpy as np
            
            if sim:
                threads = 4
                offset = 0
            else:
                if 'threads' in headless_config:
                    threads = headless_config['threads']
                else:
                    print("Error: Simulation grid was chosen but no thread count was chosen.")
                    print("Please define the key threads in the headless_config parameter.")
                    print("Stopping....")
                    exit(-1)
                if 'offset' in headless_config:
                    offset = headless_config['offset']
                else:
                    print("Error: Simulation grid was chosen but no instance offset was chosen.")
                    print("Please define the key offset in the headless_config parameter.")
                    print("Stopping....")
                    exit(-1)
            
            for i, energ in enumerate(np.linspace(8975, 10500, int(10318 / 2.0), endpoint=True)):
                if (i + offset) % threads == 0:
                    if sim:
                        guiVars.excitation_energy.set(energ) # type: ignore
                    else:
                        headless_config['excitation_energy'] = energ
                    
                    graph_area = make_simulation(sim, f, graph_area, time_of_click, False,
                                                 headless_config=headless_config)
    
    # --------------------------------------------------------------------------------------------------------------------------------------
    elif spectype == 'M_Simulation':
        graph_area = make_Msimulation(sim, f, graph_area, time_of_click)
    
    if f:
        f.canvas.draw()

