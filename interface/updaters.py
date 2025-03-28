"""
Module with dedicated updater functions for specific interface elements.
"""

#GUI Imports
from tkinter import * # type: ignore
from tkinter import ttk

from tkinter import messagebox


import data.variables as generalVars

import interface.variables as guiVars


from simulation.shake import jj_search

from simulation.lineUpdater import updateRadTransitionVals, updateAugTransitionVals
from simulation.diagram import simu_diagram
from simulation.satellite import simu_sattelite
from simulation.auger import simu_auger

from simulation.profiles import background_SNIP

from interface.experimental import loadExp, extractExpVals, update_expElements
from interface.plotters import plot_elements_roi, select_color, plotBaseline

from utils.misc.fileIO import read_quantConfig

from scipy.interpolate import interp1d

import numpy as np


from functools import partial

from typing import List, Tuple

# --------------------------------------------------------- #
#                                                           #
#          FUNCTIONS TO UPDATE INTERFACE ELEMENTS           #
#                                                           #
# --------------------------------------------------------- #

# Update the transition that was just selected from the dropdown into the list of transitions to simulate
# This function runs whenever we one transition is selected from the dropdown
def selected(event):
    """
    Function to update the transition that was just selected from the dropdown into the list of transitions to simulate.
    This function runs whenever we one transition is selected from the dropdown
        
        Args:
            event: which dropdown element was selected
        
        Returns:
            Nothing, the selected transition toggled in the dictionary and is added to the label in the interface
    """
    # Read which transition was selected
    text_T = guiVars.drop_menu.get() # type: ignore
    # Update the dictionary for the transition
    dict_updater(text_T)
    
    if guiVars.satelite_var.get() != 'Auger': # type: ignore
        # If the transition added to the selection
        if generalVars.the_dictionary[text_T]["selected_state"]:
            guiVars.transition_list.append(text_T)
        # If it was removed
        elif not generalVars.the_dictionary[text_T]["selected_state"]:
            guiVars.transition_list.remove(text_T)
    else:
        # Same for Auger
        if generalVars.the_aug_dictionary[text_T]["selected_state"]:
            guiVars.transition_list.append(text_T)
        elif not generalVars.the_aug_dictionary[text_T]["selected_state"]:
            guiVars.transition_list.remove(text_T)
    
    # Variable with the text to be shown in the interface with the selected transitions
    to_print = ', '.join(guiVars.transition_list)
    
    # Set the interface label to the text
    guiVars.label_text.set('Selected Transitions: ' + to_print) # type: ignore
    
    # Update the 2J values in the dropdown
    if guiVars.drop_menu_2j != None:
        if len(guiVars.transition_list) > 0:
            guiVars.drop_menu_2j['state'] = 'normal' # type: ignore
            jj_vals = jj_search(guiVars.transition_list)
            update_2j_dropdown(jj_vals)
        else:
            guiVars.drop_menu_2j['state'] = 'disabled' # type: ignore

def selected_elements(element: Tuple[int, str, str], button: Button):
    if element in guiVars.elementList:
        del guiVars.elementList[guiVars.elementList.index(element)]
        button.configure(background = "ghostwhite")
        button.configure(fg="black")
    else:
        guiVars.elementList.append(element)
        button.configure(background = str(element[2]))
        elementColor = select_color()
        button.configure(fg=elementColor)
        
        guiVars.elementColors[element[1]] = elementColor
    
    update_quant_table()
    
    plot_elements_roi(guiVars.graph_area, guiVars.elementColors) # type: ignore


def selected_spectra(event):
    idx: int = guiVars.drop_spectra.current() # type: ignore
    guiVars.loadvar.set(generalVars.currentSpectraList[idx]) # type: ignore
    
    update_quant_table()
    
    update_expElements(guiVars.graph_area, guiVars._residues_graph, generalVars.currentSpectraList[idx], # type: ignore
                            0.0, 0.0, 0.0, 0.0, 500, "Auto", "Auto", "Experimental", True)

def selected_base(event):
    idx: int = guiVars.drop_tube_spectra.current() # type: ignore
    if idx == 0:
        base, bkg = background_SNIP(list(generalVars.exp_x), list(generalVars.exp_y),
            guiVars.decreasing.get(), guiVars.max_window.get(), guiVars.smooth_window.get(), # type: ignore
            guiVars.number_points.get()) # type: ignore
        base_type = "SNIP"
    else:
        tube_spectrum = loadExp(generalVars.currentTubeSpectraList[idx])
        xe, ye, _ = extractExpVals(tube_spectrum)
        
        base_interp = interp1d(xe, ye, 'cubic')
        
        base = []
        for x in np.linspace(min(generalVars.exp_x), max(generalVars.exp_x), guiVars.number_points.get()): # type: ignore
            try:
                val = base_interp(x)
                if val >= 0.0:
                    base.append(val)
                else:
                    base.append(0.0)
            except ValueError:
                base.append(0.0)
        
        base_type = "Xray Tube Spectrum"
    
    plotBaseline(guiVars.graph_area, # type: ignore
                 np.linspace(min(generalVars.exp_x), max(generalVars.exp_x), guiVars.number_points.get()), # type: ignore
                 list(base), base_type)


def selected_quant_conf(event):
    idx: int = guiVars.drop_quantConfs.current() # type: ignore
    read_quantConfig(generalVars.currentSpectraList[idx])

# Function to automatically select all transitions in the dictionary. (bound to a button in the interface)
# Usefull for searching all possible theoretical lines in an experimental spectrum
def select_all_transitions():
    """
    Function to automatically select all transitions in the dictionary
    (bound to the Select All Transitions button in the interface).
    """
    min_x = 0
    max_x = 0
    
    load = guiVars.loadvar.get() # type: ignore
    if load != "No":
        exp_spectrum = loadExp(load)
        # Extract the x, y, and sigma values from the loaded experimental spectrum
        xe, ye, sigma_exp = extractExpVals(exp_spectrum)
        
        min_x = min(xe)
        max_x = max(xe)
    else:
        if guiVars.x_min.get() != "Auto": # type: ignore
            min_x = float(guiVars.x_min.get()) # type: ignore
        else:
            messagebox.showerror("Error", "Minimum value for the x axis is not set")
            return
        if guiVars.x_max.get() != "Auto": # type: ignore
            max_x = float(guiVars.x_max.get()) # type: ignore
        else:
            messagebox.showerror("Error", "Maximum value for the x axis is not set")
            return
    
    sat: str = guiVars.satelite_var.get() # type: ignore
    beam: float = guiVars.excitation_energy.get() # type: ignore
    FWHM: float = guiVars.excitation_energyFWHM.get() # type: ignore
    
    if guiVars.satelite_var.get() != 'Auger': # type: ignore
        for transition in generalVars.the_dictionary:
            _, low_level, high_level, diag_sim_val, sat_sim_val = updateRadTransitionVals(transition, 0, beam, FWHM)
            
            x, y, w = [], [], []
            xs, ws = [], []
            if 'Diagram' in sat:
                # Store the values in a list containing all the transitions to simulate
                x, y, w = simu_diagram(diag_sim_val, beam, FWHM)
            if 'Satellites' in sat:
                # Store the values in a list containing all the transitions to simulate
                xs, _, ws = simu_sattelite(sat_sim_val, low_level, high_level, beam, FWHM, calc_int=False)
            
            xs = [x1 for x in xs for x1 in x]
            ws = [w1 for w in ws for w1 in w]
            # ys = [y1 for y in ys for y1 in y]
            
            if any([len(i) > 0 for i in [x, y, w, xs, ws]]):
                if any([x1 - w1 / 2 <= max_x and x1 + w1 / 2 > min_x for x1, w1 in zip(x, w)]) or \
                    any([x1 - w1 / 2 <= max_x and x1 + w1 / 2 > min_x for x1, w1 in zip(xs, ws)]):
                    dict_updater(transition)
                    
                    # If the transition added to the selection
                    if generalVars.the_dictionary[transition]["selected_state"]:
                        guiVars.transition_list.append(transition)
                    # If it was removed
                    elif not generalVars.the_dictionary[transition]["selected_state"]:
                        guiVars.transition_list.remove(transition)
    else:
        # Same for Auger
        for transition in generalVars.the_aug_dictionary:
            _, aug_stick_val = updateAugTransitionVals(transition, 0)
            
            # Store the values in a list containing all the transitions to simulate
            x, y, w = simu_auger(aug_stick_val, beam, FWHM)
            
            if any([len(i) > 0 for i in [x, y, w]]):
                if any([x1 - w1 / 2 <= max_x and x1 + w1 / 2 > min_x for x1, w1 in zip(x, w)]):
                    dict_updater(transition)
                    
                    if generalVars.the_aug_dictionary[transition]["selected_state"]:
                        guiVars.transition_list.append(transition)
                    elif not generalVars.the_aug_dictionary[transition]["selected_state"]:
                        guiVars.transition_list.remove(transition)
    
    # Variable with the text to be shown in the interface with the selected transitions
    to_print = ', '.join(guiVars.transition_list)
    
    # Set the interface label to the text
    guiVars.label_text.set('Selected Transitions: ' + to_print) # type: ignore
    
    # Update the 2J values in the dropdown
    if len(guiVars.transition_list) > 0:
        guiVars.drop_menu_2j['state'] = 'normal' # type: ignore
        jj_vals = jj_search(guiVars.transition_list)
        update_2j_dropdown(jj_vals)
    else:
        guiVars.drop_menu_2j['state'] = 'disabled' # type: ignore

# Function to properly reset the x limits in the interface (bound to the reset button)
def reset_limits():
    """
    Function to properly reset the x limits in the interface (bound to the reset button).
    """
    guiVars.number_points.set(500) # type: ignore
    guiVars.x_max.set('Auto') # type: ignore
    guiVars.x_min.set('Auto') # type: ignore

# Function to update the offset entries in the interface (bound to the separate toggle button)
def update_offsets(buttons_frame: Frame):
    """
    Function to update the offset entries in the interface (bound to the separate toggle button).
    """
    if guiVars.separate_offsets.get(): # type: ignore
        buttons_frame.nametowidget('sat_offsetEntry').config(state='disabled') # type: ignore
        buttons_frame.nametowidget('sat_offsetLabel').config(state='disabled') # type: ignore
        buttons_frame.nametowidget('shkoff_offsetEntry').config(state='normal') # type: ignore
        buttons_frame.nametowidget('shkoff_offsetLabel').config(state='normal') # type: ignore
        buttons_frame.nametowidget('shkup_offsetEntry').config(state='normal') # type: ignore
        buttons_frame.nametowidget('shkup_offsetLabel').config(state='normal') # type: ignore
    else:
        buttons_frame.nametowidget('sat_offsetEntry').config(state='normal') # type: ignore
        buttons_frame.nametowidget('sat_offsetLabel').config(state='normal') # type: ignore
        buttons_frame.nametowidget('shkoff_offsetEntry').config(state='disabled') # type: ignore
        buttons_frame.nametowidget('shkoff_offsetLabel').config(state='disabled') # type: ignore
        buttons_frame.nametowidget('shkup_offsetEntry').config(state='disabled') # type: ignore
        buttons_frame.nametowidget('shkup_offsetLabel').config(state='disabled') # type: ignore

# Update the selection state of a transition in the correct dictionary
def dict_updater(transition: str):
    """
    Function to update the selection state of a transition in the correct dictionary
        
        Args:
            transition: which transition to update
        
        Returns:
            Nothing, the transition is updated in the dictionaries
    """
    if guiVars.satelite_var.get() != 'Auger': # type: ignore
        # Toggle the current state of the transition
        generalVars.the_dictionary[transition]["selected_state"] = not generalVars.the_dictionary[transition]["selected_state"]
    else:
        # Toggle the current state of the transition
        generalVars.the_aug_dictionary[transition]["selected_state"] = not generalVars.the_aug_dictionary[transition]["selected_state"]

# Function to update the transitions that can be selected from the dropdown, depending on if we want to simulate radiative or auger
def update_transition_dropdown(cascade_analysis: Menu):
    """
    Function to update the transitions that can be selected from the dropdown, depending on if we want to simulate radiative or auger
    """
    if guiVars.satelite_var.get() != 'Auger': # type: ignore
        # Update the values on the dropdown
        guiVars.drop_menu['values'] = [transition for transition in generalVars.the_dictionary] # type: ignore
        if not any([generalVars.the_dictionary[transition]["selected_state"] for transition in generalVars.the_dictionary]):
            # Reset the interface text
            guiVars.label_text.set('Select a Transition: ') # type: ignore
            guiVars.drop_menu.set('Transitions:') # type: ignore
            # Deselect transitions
            for transition in generalVars.the_aug_dictionary:
                generalVars.the_aug_dictionary[transition]["selected_state"] = False
        
        cascade_analysis.entryconfigure(2, state=DISABLED)
    else:
        # Update the values on the dropdown
        guiVars.drop_menu['values'] = [transition for transition in generalVars.the_aug_dictionary] # type: ignore
        if not any([generalVars.the_aug_dictionary[transition]["selected_state"] for transition in generalVars.the_aug_dictionary]):
            # Reset the interface text
            guiVars.label_text.set('Select a Transition: ') # type: ignore
            guiVars.drop_menu.set('Transitions:') # type: ignore
            # Deselect transitions
            for transition in generalVars.the_dictionary:
                generalVars.the_dictionary[transition]["selected_state"] = False
        
        cascade_analysis.entryconfigure(2, state=NORMAL)

# Function to update the 2j values that can be selected from the dropdown, depending on the selected transitions
def update_2j_dropdown(jj_vals: List[int]):
    """
    Function to update the 2j values that can be selected from the dropdown, depending on the selected transitions
    """
    guiVars.drop_menu_2j['values'] = [str(jj) for jj in jj_vals] # type: ignore
    guiVars.jj_text.set('Select a 2J value: ') # type: ignore
    guiVars.drop_menu_2j.set("2J Values:") # type: ignore


# Update the 2j value that was just selected from the dropdown into the list of 2j values to simulate
# This function runs whenever we one 2j value is selected from the dropdown
def selected_2j(event):
    """
    Update the 2j value that was just selected from the dropdown into the list of 2j values to simulate
    This function runs whenever we one 2j value is selected from the dropdown
    
        Args:
            event: which dropdown element was selected
        
        Returns:
            Nothing, the selected 2j value is added to the label in the interface
    """
    # Read which 2j value was selected
    text_T = guiVars.drop_menu_2j.get() # type: ignore
    
    # If the 2j value was added to the selection
    if text_T not in guiVars.jj_list:
        guiVars.jj_list.append(text_T)
        generalVars.jj_vals.append(int(text_T))
    # If it was removed
    elif text_T in guiVars.jj_list:
        guiVars.jj_list.remove(text_T)
        generalVars.jj_vals.remove(int(text_T))
    
    # Variable with the text to be shown in the interface with the selected 2j values
    to_print = ', '.join(guiVars.jj_list)
    
    # Set the interface label to the text
    guiVars.jj_text.set('Selected 2J values: ' + to_print) # type: ignore


def update_unit(event, el: str, idx: int):
    generalVars.currentQuantConfigSpectra[guiVars.drop_spectra.get()][el] = ( # type: ignore
        generalVars.currentQuantConfigSpectra[guiVars.drop_spectra.get()][el][0], # type: ignore
        generalVars.currentQuantConfigSpectra[guiVars.drop_spectra.get()][el][1], # type: ignore
        generalVars.currentQuantConfigSpectra[guiVars.drop_spectra.get()][el][2], # type: ignore
        generalVars.weightUnits.index(guiVars.drop_units_list[idx].get())
    )
    
    return True

def validate_target(el: str, idx: int):
    generalVars.currentQuantConfigSpectra[guiVars.drop_spectra.get()][el] = ( # type: ignore
        float(guiVars.targetEntries[idx].get()), # type: ignore
        float(guiVars.targetNegEntries[idx].get()), # type: ignore
        float(guiVars.targetPosEntries[idx].get()), # type: ignore
        generalVars.currentQuantConfigSpectra[guiVars.drop_spectra.get()][el][3], # type: ignore
    )
    print(generalVars.currentQuantConfigSpectra)
    
    return True

def validate_alpha(el: str, idx: int):
    generalVars.currentQuantConfig[el] = float(guiVars.alphaEntries[idx].get())
    print(generalVars.currentQuantConfig)
    return True

def update_target(var, index, mode, el: str, idx: int):
    generalVars.currentQuantConfigSpectra[guiVars.drop_spectra.get()][el] = ( # type: ignore
        float(guiVars.targetEntries[idx].get()), # type: ignore
        float(guiVars.targetNegEntries[idx].get()), # type: ignore
        float(guiVars.targetPosEntries[idx].get()), # type: ignore
        generalVars.currentQuantConfigSpectra[guiVars.drop_spectra.get()][el][3], # type: ignore
    )


def update_alpha(var, index, mode, el: str, idx: int):
    generalVars.currentQuantConfig[el] = float(guiVars.alphaEntries[idx].get())
    guiVars.quantityLabels[idx].set((max(generalVars.weightFractions[idx]) / (generalVars.total_weight if generalVars.total_weight != 0.0 else 1.0)) * guiVars.alphaEntries[idx].get())



def update_quant_config():
    if guiVars.drop_spectra.get() not in generalVars.currentQuantConfig: # type: ignore
        generalVars.currentQuantConfig[guiVars.drop_spectra.get()] = {} # type: ignore
    
    for i, el in enumerate(guiVars.elementList):
        generalVars.currentQuantConfig[el[1]] = float(guiVars.alphaEntries[i].get())
        generalVars.currentQuantConfigSpectra[guiVars.drop_spectra.get()][el[1]] = ( # type: ignore
                float(guiVars.targetEntries[i].get()), 
                float(guiVars.targetNegEntries[i].get()), 
                float(guiVars.targetPosEntries[i].get()), 
                generalVars.weightUnits.index(guiVars.drop_units_list[i].get()))


def update_quant_table():
    for widget in guiVars.table.interior.winfo_children(): # type: ignore
        widget.destroy()
    
    guiVars.alphaEntries.clear()
    guiVars.quantityLabels.clear()
    guiVars.targetEntries.clear()
    guiVars.targetNegEntries.clear()
    guiVars.targetPosEntries.clear()
    
    guiVars.drop_units_list.clear()
    
    # Table with the active elements, alpha coeficient, current quantity and target quantity if any
    for i, element in enumerate(guiVars.elementList):
        if guiVars.drop_spectra.get() not in generalVars.currentQuantConfigSpectra: # type: ignore
            generalVars.currentQuantConfigSpectra[guiVars.drop_spectra.get()] = {} # type: ignore
        if element[1] not in generalVars.currentQuantConfigSpectra[guiVars.drop_spectra.get()]: # type: ignore
            generalVars.currentQuantConfigSpectra[guiVars.drop_spectra.get()][element[1]] = (0.0, 0.0, 0.0, 0) # type: ignore
        
        if element[1] not in generalVars.currentQuantConfig:
            generalVars.currentQuantConfig[element[1]] = 1.0
        
        
        guiVars.alphaEntries.append(DoubleVar(master=guiVars.table.interior, # type: ignore
            value=generalVars.currentQuantConfig[element[1]]))
        guiVars.quantityLabels.append(DoubleVar(master=guiVars.table.interior, # type: ignore
            value=0.0))
        guiVars.targetEntries.append(DoubleVar(master=guiVars.table.interior, # type: ignore
            value=generalVars.currentQuantConfigSpectra[guiVars.drop_spectra.get()][element[1]][0])) # type: ignore
        guiVars.targetNegEntries.append(DoubleVar(master=guiVars.table.interior, # type: ignore
            value=generalVars.currentQuantConfigSpectra[guiVars.drop_spectra.get()][element[1]][1])) # type: ignore
        guiVars.targetPosEntries.append(DoubleVar(master=guiVars.table.interior, # type: ignore
            value=generalVars.currentQuantConfigSpectra[guiVars.drop_spectra.get()][element[1]][2])) # type: ignore
        
        alphaVal = partial(validate_alpha, el=element[1], idx=i)
        targetVal = partial(validate_target, el=element[1], idx=i)
        
        tmp = ttk.Entry(guiVars.table.interior, width=5) # type: ignore
        ttk.Spinbox(guiVars.table.interior, from_=0, to=100000, increment=0.05, textvariable=guiVars.alphaEntries[i], validate="key", validatecommand=alphaVal, width=7).grid(row=i, column=1, ipadx=2) # type: ignore
        ttk.Entry(guiVars.table.interior, textvariable=guiVars.quantityLabels[i], state='disabled', width=9).grid(row=i, column=2, ipadx=3) # type: ignore
        ttk.Spinbox(guiVars.table.interior, from_=0, to=100000, increment=0.05, textvariable=guiVars.targetEntries[i], validate="key", validatecommand=targetVal, width=7).grid(row=i, column=3, ipadx=3) # type: ignore
        ttk.Spinbox(guiVars.table.interior, from_=0, to=100000, increment=0.05, textvariable=guiVars.targetNegEntries[i], validate="key", validatecommand=targetVal, width=7).grid(row=i, column=4, ipadx=3) # type: ignore
        ttk.Spinbox(guiVars.table.interior, from_=0, to=100000, increment=0.05, textvariable=guiVars.targetPosEntries[i], validate="key", validatecommand=targetVal, width=7).grid(row=i, column=5, ipadx=2) # type: ignore
        
        
        guiVars.drop_units_list.append(ttk.Combobox(guiVars.table.interior, value=generalVars.weightUnits, width=7)) # type: ignore
        
        tmp.insert(0, element[1])
        tmp.configure(state='disabled')
        tmp.grid(row=i, column=0)
        
        alphaUp = partial(update_alpha, el=element[1], idx=i)
        guiVars.alphaEntries[i].trace_add('write', alphaUp)
        
        targetUp = partial(update_target, el=element[1], idx=i)
        guiVars.targetEntries[i].trace_add('write', targetUp)
        guiVars.targetNegEntries[i].trace_add('write', targetUp)
        guiVars.targetPosEntries[i].trace_add('write', targetUp)
        
        if element[1] in generalVars.currentQuantConfigSpectra[guiVars.drop_spectra.get()]: # type: ignore
            guiVars.drop_units_list[i].current(generalVars.currentQuantConfigSpectra[guiVars.drop_spectra.get()][element[1]][3]) # type: ignore
        else:
            generalVars.currentQuantConfigSpectra[guiVars.drop_spectra.get()][element[1]] = ( # type: ignore
                generalVars.currentQuantConfigSpectra[guiVars.drop_spectra.get()][element[1]][0], # type: ignore
                generalVars.currentQuantConfigSpectra[guiVars.drop_spectra.get()][element[1]][1], # type: ignore
                generalVars.currentQuantConfigSpectra[guiVars.drop_spectra.get()][element[1]][2], # type: ignore
                0
            )
            guiVars.drop_units_list[i].current(0)
        
        callback = partial(update_unit, el=element[1], idx=i)
        guiVars.drop_units_list[i].bind("<<ComboboxSelected>>", callback)
        
        if element[1] in generalVars.currentQuantConfigSpectra[guiVars.drop_spectra.get()]: # type: ignore
            guiVars.drop_units_list[i].current(generalVars.currentQuantConfigSpectra[guiVars.drop_spectra.get()][element[1]][3]) # type: ignore
        else:
            generalVars.currentQuantConfigSpectra[guiVars.drop_spectra.get()][element[1]] = ( # type: ignore
                generalVars.currentQuantConfigSpectra[guiVars.drop_spectra.get()][element[1]][0], # type: ignore
                generalVars.currentQuantConfigSpectra[guiVars.drop_spectra.get()][element[1]][1], # type: ignore
                generalVars.currentQuantConfigSpectra[guiVars.drop_spectra.get()][element[1]][2], # type: ignore
                0
            )
            guiVars.drop_units_list[i].current(0)

        guiVars.drop_units_list[i].grid(row=i, column=6)
        