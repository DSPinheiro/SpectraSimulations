"""
Module for interface variables and functions.
Here we define the variables bound to the interface elements, window management functions, keybinds,
functions to initialize interface elements, functions to update the elements and functions to plot external data
"""

#GUI Imports
from tkinter import *
from tkinter import messagebox
from tkinter import ttk

#Matplotlib imports for plotting and tkinter compatibility
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import webbrowser


#Data import for variable management
import data.variables as generalVars

import interface.variables as guiVars

#Import file loaders for the interface
from utils.misc.fileIO import saveMatrixHtml

#Import the main functions to bind them to the interface
from utils.misc.analysers import prepareBoostMatrices, prepareRateMatrices, computeCascadeGraph, analyseConvergence

import simulation.shake as shakes
from simulation.fitting import setMaxTotalShake

#Import numpy
import numpy as np

#Math import for interpolation
from scipy.interpolate import interp1d

from typing import List, Dict


# --------------------------------------------------------- #
#                                                           #
#             FUNCTIONS TO LAUNCH EXTRA WINDOWS             #
#                                                           #
# --------------------------------------------------------- #


# Initialize and configure the charge state mixture interface where we configure the mixture
def configureCSMix():
    """
    Function to initialize and configure the charge state mixture interface where we configure the mixture
    """
    
    print(guiVars.choice_var.get()) # type: ignore
    if guiVars.choice_var.get() == '': # type: ignore
        return
    
    mixer = Toplevel(guiVars._parent)
    mixer.title("Charge State Mixer")
    mixer.grab_set()  # Make this window the only interactable one until its closed

    mixer.geometry("700x300")

    # Input check for the percentage number in the entry
    import re
    def check_num(newval):
        """
        Function to input check for the percentage number in the entry
            
            Args:
                newval: the value trying to be introduced
            
            Returns:
                regex match to check if the new value is a numric percentage format
        """
        return re.match('^(?:[0-9]*[.]?[0-9]*)$', newval) is not None
    # Bind the function
    check_num_wrapper = (mixer.register(check_num), '%P')
    """
    Function wrapper to bind this validate command
    """

    # -------------------------------------------------------------------------------------------------------------------------------------------
    # RADIATIVE

    # Lists to hold the interface objects for the radiative section
    slidersRad = []
    CS_labelsRad = []
    # Fetch the order of the positive and negative charge states to show in the interface
    PCS_order = [int(cs.split('intensity_')[1].split('.out')[0].split('+')[-1]) for cs in generalVars.radiative_files if '+' in cs]
    NCS_order = [int(cs.split('intensity_')[1].split('.out')[0].split('-')[-1]) for cs in generalVars.radiative_files if '+' not in cs]

    # List to hold the entries where we can type a mix percentage for each charge state
    CS_mixEntriesRad = []

    # Title label for the radiative section
    labelRad = ttk.Label(mixer, text="Charge States With Radiative Transitions For Selected Atom:")
    labelRad.grid(column=0, row=0, columnspan=len(generalVars.radiative_files), pady=40)

    # If this is the first time we show tins interface we will need to initialize the elements
    if len(guiVars.PCS_radMixValues) == 0:
        # For each found charge state with radiative rates we initialize a set of slider, entry, label and variable to hold the value
        for cs in generalVars.radiative_files:
            if '+' in cs:
                guiVars.PCS_radMixValues.append(StringVar())
                CS_mixEntriesRad.append(ttk.Entry(mixer, textvariable=guiVars.PCS_radMixValues[-1], validate='key', validatecommand=check_num_wrapper))
                slidersRad.append(ttk.Scale(mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=generalVars.PCS_radMixValues[-1])) # type: ignore
                CS_labelsRad.append(ttk.Label(mixer, text=cs.split('intensity_')[1].split('.out')[0]))
                slidersRad[-1].set(0.0)
    else:
        # If we already initialized the variables we only need to reinitialize the interface elements
        i = 0
        for cs in generalVars.radiative_files:
            if '+' in cs:
                CS_mixEntriesRad.append(ttk.Entry(mixer, textvariable=guiVars.PCS_radMixValues[i], validate='key', validatecommand=check_num_wrapper))
                slidersRad.append(ttk.Scale(mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=generalVars.PCS_radMixValues[i])) # type: ignore
                CS_labelsRad.append(ttk.Label(mixer, text=cs.split('intensity_')[1].split('.out')[0]))

                i += 1

    # Same as the positive charge states. This split helps organize the interface when several different charge states are present
    if len(guiVars.NCS_radMixValues) == 0:
        for cs in generalVars.radiative_files:
            if '+' not in cs:
                guiVars.NCS_radMixValues.append(StringVar())
                CS_mixEntriesRad.append(ttk.Entry(mixer, textvariable=guiVars.NCS_radMixValues[-1], validate='key', validatecommand=check_num_wrapper))
                slidersRad.append(ttk.Scale(mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=generalVars.NCS_radMixValues[-1])) # type: ignore
                CS_labelsRad.append(ttk.Label(mixer, text=cs.split('intensity_')[1].split('.out')[0]))
                slidersRad[-1].set(0.0)
    else:
        i = 0
        for cs in generalVars.radiative_files:
            if '+' not in cs:
                CS_mixEntriesRad.append(ttk.Entry(mixer, textvariable=guiVars.NCS_radMixValues[i], validate='key', validatecommand=check_num_wrapper))
                slidersRad.append(ttk.Scale(mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=generalVars.NCS_radMixValues[i])) # type: ignore
                CS_labelsRad.append(ttk.Label(mixer, text=cs.split('intensity_')[1].split('.out')[0]))

                i += 1

    # Copy the orders to a new array to organize the interface order
    initial_PCS_Order = PCS_order.copy()
    initial_NCS_Order = NCS_order.copy()
    colIndex = 0
    
    # Place the interface elements in the order of most negative charge state first
    while len(NCS_order) > 0:
        # Find the most negative charge state
        idx = initial_NCS_Order.index(min(NCS_order))

        # Initialize the interface elements
        CS_labelsRad[idx].grid(column=colIndex, row=1, sticky=(N), pady=5)
        slidersRad[idx].grid(column=colIndex, row=2, sticky=(N, S), pady=5)
        CS_mixEntriesRad[idx].grid(column=colIndex, row=3, sticky=(W, E), padx=5)

        # Configure the grid column resizing
        mixer.columnconfigure(colIndex, weight=1)

        # Update the column index and remove the charge state we just initialized
        colIndex += 1
        del NCS_order[NCS_order.index(min(NCS_order))]

    # Place the positive charge states afterwards, in a similar order as the negative ones
    while len(PCS_order) > 0:
        idx = initial_PCS_Order.index(min(PCS_order))

        CS_labelsRad[idx].grid(column=colIndex, row=1, sticky=(N), pady=5)
        slidersRad[idx].grid(column=colIndex, row=2, sticky=(N, S), pady=5)
        CS_mixEntriesRad[idx].grid(column=colIndex, row=3, sticky=(W, E), padx=5)

        mixer.columnconfigure(colIndex, weight=1)

        colIndex += 1
        del PCS_order[PCS_order.index(min(PCS_order))]

    # Configure the resizing of the row
    mixer.rowconfigure(2, weight=1)

    # ------------------------------------------------------------------------------------------------------------------------------------
    # AUGER
    
    # Same as the radiative section
    if len(generalVars.auger_files) > 0:
        mixer.geometry("800x600")

        slidersAug = []
        CS_labelsAug = []
        PCS_order = [int(cs.split('augrate_')[1].split('.out')[0].split('+')[-1]) for cs in generalVars.auger_files if '+' in cs]
        NCS_order = [int(cs.split('augrate_')[1].split('.out')[0].split('-')[-1]) for cs in generalVars.auger_files if '+' not in cs]

        CS_mixEntriesAug = []

        labelAug = ttk.Label(
            mixer, text="Charge States With Auger Transitions For Selected Atom:")
        labelAug.grid(column=0, row=4, columnspan=len(generalVars.radiative_files), pady=40)

        if len(guiVars.PCS_augMixValues) == 0:
            for cs in generalVars.auger_files:
                if '+' in cs:
                    guiVars.PCS_augMixValues.append(StringVar())
                    CS_mixEntriesAug.append(ttk.Entry(mixer, textvariable=guiVars.PCS_augMixValues[-1], validate='key', validatecommand=check_num_wrapper))
                    slidersAug.append(ttk.Scale(mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=generalVars.PCS_augMixValues[-1])) # type: ignore
                    CS_labelsAug.append(ttk.Label(mixer, text=cs.split('augrate_')[1].split('.out')[0]))
                    slidersAug[-1].set(0.0)
        else:
            i = 0
            for cs in generalVars.auger_files:
                if '+' in cs:
                    CS_mixEntriesAug.append(ttk.Entry(mixer, textvariable=guiVars.PCS_augMixValues[i], validate='key', validatecommand=check_num_wrapper))
                    slidersAug.append(ttk.Scale(mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=generalVars.PCS_augMixValues[i])) # type: ignore
                    CS_labelsAug.append(ttk.Label(mixer, text=cs.split('augrate_')[1].split('.out')[0]))

                    i += 1

        if len(guiVars.NCS_augMixValues) == 0:
            for cs in generalVars.auger_files:
                if '+' not in cs:
                    guiVars.NCS_augMixValues.append(StringVar())
                    CS_mixEntriesAug.append(ttk.Entry(mixer, textvariable=guiVars.NCS_augMixValues[-1], validate='key', validatecommand=check_num_wrapper))
                    slidersAug.append(ttk.Scale(mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=generalVars.NCS_augMixValues[-1])) # type: ignore
                    CS_labelsAug.append(ttk.Label(mixer, text=cs.split('augrate_')[1].split('.out')[0]))
                    slidersAug[-1].set(0.0)
        else:
            i = 0
            for cs in generalVars.auger_files:
                if '+' not in cs:
                    CS_mixEntriesAug.append(ttk.Entry(mixer, textvariable=guiVars.NCS_augMixValues[i], validate='key', validatecommand=check_num_wrapper))
                    slidersAug.append(ttk.Scale(mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=generalVars.NCS_augMixValues[i])) # type: ignore
                    CS_labelsAug.append(ttk.Label(mixer, text=cs.split('augrate_')[1].split('.out')[0]))

                    i += 1

        initial_PCS_Order = PCS_order.copy()
        initial_NCS_Order = NCS_order.copy()
        colIndex = 0
        while len(NCS_order) > 0:
            idx = initial_NCS_Order.index(min(NCS_order))

            CS_labelsAug[idx].grid(column=colIndex, row=5, sticky=(N), pady=5)
            slidersAug[idx].grid(column=colIndex, row=6, sticky=(N, S), pady=5)
            CS_mixEntriesAug[idx].grid(column=colIndex, row=7, sticky=(W, E), padx=5)

            mixer.columnconfigure(colIndex, weight=1)

            colIndex += 1
            del NCS_order[NCS_order.index(min(NCS_order))]

        while len(PCS_order) > 0:
            idx = initial_PCS_Order.index(min(PCS_order))

            CS_labelsAug[idx].grid(column=colIndex, row=5, sticky=(N), pady=5)
            slidersAug[idx].grid(column=colIndex, row=6, sticky=(N, S), pady=5)
            CS_mixEntriesAug[idx].grid(column=colIndex, row=7, sticky=(W, E), padx=5)

            mixer.columnconfigure(colIndex, weight=1)

            colIndex += 1
            del PCS_order[PCS_order.index(min(PCS_order))]

        mixer.rowconfigure(6, weight=1)

    # ------------------------------------------------------------------------------------------------------------------------------------
    # Ion Population slider

    Ion_Populations = {}

    combined_x: List[float] = []
    combined_y: List[float] = []

    # Organize the data from the ion population file into a dictionary for interpolation and plotting
    for i, cs in enumerate(generalVars.ionpopdata[0]):
        Ion_Populations[cs + '_x'] = []
        Ion_Populations[cs + '_y'] = []

        col = i * 2

        for vals in generalVars.ionpopdata[1:]:
            # A predifined spacing of at least 3 dashes is used in the file to keep the structure
            if '---' not in vals[col]:
                combined_x.append(float(vals[col]))
                combined_y.append(float(vals[col + 1]))
                if float(vals[col]) not in Ion_Populations[cs + '_x']:
                    Ion_Populations[cs + '_x'].append(float(vals[col]))
                    Ion_Populations[cs +'_y'].append(float(vals[col + 1]))

    # Normalize the ion populations
    y_max = max(combined_y)
    for cs in generalVars.ionpopdata[0]:
        Ion_Populations[cs + '_y'] = [pop * 100 / y_max for pop in Ion_Populations[cs + '_y']]

    # Interpolate the ion populations
    Ion_Population_Functions = {}
    # linear interpolation because of "corners" in the distribution functions
    for cs in generalVars.ionpopdata[0]:
        order = np.argsort(Ion_Populations[cs + '_x'])
        Ion_Population_Functions[cs] = interp1d(np.array(Ion_Populations[cs + '_x'])[order], np.array(Ion_Populations[cs + '_y'])[order], kind='linear')

    # Remove duplicate values of x on the combined ion population data
    combined_x = list(set(combined_x))

    # Max and min of the x values (by default they are temperature, i.e. plasma temperature)
    temperature_max = max(combined_x)
    temperature_min = min(combined_x)

    # Configure the grid if there are auger charge states
    if len(generalVars.auger_files) > 0:
        fig_row = 7
    else:
        fig_row = 4

    f = Figure(figsize=(10, 5), dpi=100)
    
    a = f.add_subplot(111)
    a.set_xlabel('Temperature (K)')
    a.set_ylabel('Population')
    
    # ---------------------------------------------------------------------------------------------------------------
    # Interface elements for the graph figure and buttons
    figure_frame = Frame(mixer, relief=GROOVE)  # frame for the graph

    # Position the frame for the figure in the grid
    figure_frame.grid(column=0, row=fig_row, columnspan=max(len(generalVars.radiative_files), len(generalVars.auger_files)), pady=20)

    canvas = FigureCanvasTkAgg(f, master=figure_frame)
    canvas.get_tk_widget().pack(fill=BOTH, expand=1)

    mixer.rowconfigure(fig_row, weight=1)

    # Variable and vertical line for the x value to use for the ion population mixture values
    temperature = StringVar()
    temperature.set(str(temperature_min))
    prev_line = a.axvline(x=float(temperature.get()), color='b')

    # Function to update the vertical line in the plot and the mixture values
    def update_temp_line(event, arg1, arg2):
        """
        Function to update the vertical line in the plot and the mixture values
            
            Args:
                event: which event triggered this function call. the function is only bound to write calls
                arg1, arg2: arguments required for the write callback
            
            Returns:
                Nothing, the values are updated in the global variables and the line is redrawn in the interface
        """
        # Update line position
        prev_line.set_xdata(float(temperature.get()))

        # Update the plot
        f.canvas.draw()
        f.canvas.flush_events()

        # Loop the existing interpolated functions and update the mix values acording to the chosen x
        for cs in Ion_Population_Functions:
            if len(guiVars.PCS_radMixValues) > 0:
                i = 0
                for cs_file in generalVars.radiative_files:
                    if cs in cs_file:
                        # If the x value is outside interpolation range we just set it to 0
                        try:
                            guiVars.PCS_radMixValues[i].set(str(Ion_Population_Functions[cs](float(temperature.get()))))
                        except:
                            guiVars.PCS_radMixValues[i].set("0.0")

                        break

                    if '+' in cs:
                        i += 1

            if len(guiVars.NCS_radMixValues) > 0:
                i = 0
                for cs_file in generalVars.radiative_files:
                    if cs in cs_file:
                        # If the x value is outside interpolation range we just set it to 0
                        try:
                            guiVars.NCS_radMixValues[i].set(str(Ion_Population_Functions[cs](float(temperature.get()))))
                        except:
                            guiVars.NCS_radMixValues[i].set("0.0")

                        break

                    if '+' not in cs:
                        i += 1

        # If there is auger rate files make the same updates to the auger mix values
        if len(generalVars.auger_files) > 0:
            for cs in Ion_Population_Functions:
                if len(guiVars.PCS_augMixValues) > 0:
                    i = 0
                    for cs_file in generalVars.auger_files:
                        if cs in cs_file:
                            try:
                                guiVars.PCS_augMixValues[i].set(str(Ion_Population_Functions[cs](float(temperature.get()))))
                            except:
                                guiVars.PCS_augMixValues[i].set("0.0")

                            break

                        if '+' in cs:
                            i += 1

                if len(guiVars.NCS_augMixValues) > 0:
                    i = 0
                    for cs_file in generalVars.auger_files:
                        if cs in cs_file:
                            try:
                                guiVars.NCS_augMixValues[i].set(str(Ion_Population_Functions[cs](float(temperature.get()))))
                            except:
                                guiVars.NCS_augMixValues[i].set("0.0")

                            break

                        if '+' not in cs:
                            i += 1

    # Whenever we update the x value we also update the line and mix values
    temperature.trace_add("write", update_temp_line)
    # Add the slider and entry and position them in the grid
    temp_slider = ttk.Scale(mixer, orient=HORIZONTAL, length=200, from_=temperature_min, to=temperature_max, variable=temperature) # type: ignore
    temp_entry = ttk.Entry(mixer, textvariable=temperature, validate='key', validatecommand=check_num_wrapper)
    temp_slider.grid(column=0, row=fig_row + 1, columnspan=max(len(generalVars.radiative_files), len(generalVars.auger_files)) - 1, sticky=(W, E), padx=10, pady=20) # type: ignore
    temp_entry.grid(column=max(len(generalVars.radiative_files), len(generalVars.auger_files)) - 1, row=fig_row + 1, sticky=(W, E), padx=5) # type: ignore

    # Configure the resizing
    mixer.rowconfigure(fig_row + 1, weight=1)

    # Plot the ion population functions
    for cs in generalVars.ionpopdata[0]:
        x_min = min(Ion_Populations[cs + '_x'])
        x_max = max(Ion_Populations[cs + '_x'])

        temp_new = np.arange(x_min, x_max, (x_max - x_min) / 100)
        pop_new = Ion_Population_Functions[cs](temp_new)

        a.plot(temp_new, pop_new, label=cs)
    
    
    a.legend()


def startBoostWindow(split: bool = True):
    radInitials, radFinals, radData, radDataExtra, \
    augInitials, augFinals, augData, augDataExtra, \
    satInitials, satFinals, satData, satDataExtra = prepareBoostMatrices()
    
    zmax = np.max([np.max(radData), np.max(augData), np.max(satData)])

    
    fig_rad = go.Heatmap(z=radData,
                        x=radFinals,
                        y=radInitials,
                        hovertemplate="Initial State: %{y}" + 
                                "<br>Final State: %{x}" + 
                                "<br>Boost Mult: %{z}" + 
                                "<br>Total Rate: %{text}",
                        text=radDataExtra,
                        zmin=0,
                        zmax=zmax)
    
    fig_aug = go.Heatmap(z=augData,
                        x=augFinals,
                        y=augInitials,
                        hovertemplate="Initial State: %{y}" + 
                                "<br>Final State: %{x}" + 
                                "<br>Boost Mult: %{z}" + 
                                "<br>Total Rate: %{text}",
                        text=augDataExtra,
                        zmin=0,
                        zmax=zmax)
    
    fig_sat = go.Heatmap(z=satData,
                        x=satFinals,
                        y=satInitials,
                        hovertemplate="Initial State: %{y}" + 
                                "<br>Final State: %{x}" + 
                                "<br>Boost Mult: %{z}" + 
                                "<br>Total Rate: %{text}",
                        text=satDataExtra,
                        zmin=0,
                        zmax=zmax)
    
    radMatrixURL = ""
    radMatrixLogURL = ""
    augMatrixURL = ""
    augMatrixLogURL = ""
    satMatrixURL = ""
    satMatrixLogURL = ""
    matricesURL = ""
    matricesLogURL = ""

    
    if split:
        fig = make_subplots(rows=1, cols=1, subplot_titles=["Radiative Boost Matrix"])
        
        fig.append_trace(fig_rad, row=1, col=1)

        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)

        radMatrixURL = saveMatrixHtml(fig, "boostRadMatrix.html")
        
        fig = make_subplots(rows=1, cols=1, subplot_titles=["Auger Boost Matrix"])
        
        
        fig.append_trace(fig_aug, row=1, col=1)

        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)

        augMatrixURL = saveMatrixHtml(fig, "boostAugMatrix.html")
        
        fig = make_subplots(rows=1, cols=1, subplot_titles=["Satellite Boost Matrix"])
        
        fig.append_trace(fig_sat, row=1, col=1)

        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)

        satMatrixURL = saveMatrixHtml(fig, "boostSatMatrix.html")
    else:
        fig = make_subplots(rows=2, cols=2,
                            subplot_titles=[
                                "Radiative Boost Matrix", 
                                "Auger Boost Matrix", 
                                "Satellite Boost Matrix"
                                ],
                            specs=[[{}, {"rowspan": 2}],
                                [{}, None]],
                            column_widths=[len(radFinals) / (len(augFinals) + len(radFinals)),
                                        len(augFinals) / (len(augFinals) + len(radFinals))]
                            )
        
        fig.append_trace(fig_rad, row=1, col=1)
        fig.append_trace(fig_aug, row=1, col=2)
        fig.append_trace(fig_sat, row=2, col=1)
        
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        
        matricesURL = saveMatrixHtml(fig, "boostMatrices.html")
    
    
    radDataLog = np.log10(radData)
    augDataLog = np.log10(augData)
    satDataLog = np.log10(satData)
    
    zmin = min([np.min(radDataLog[radDataLog != -np.inf]), np.min(augDataLog[augDataLog  != -np.inf]), np.min(satDataLog[satDataLog != -np.inf])])

    
    fig_rad = go.Heatmap(z=radDataLog,
                        x=radFinals,
                        y=radInitials,
                        hovertemplate="Initial State: %{y}" + 
                                "<br>Final State: %{x}" + 
                                "<br>Boost Mult: %{z}" + 
                                "<br>Total Rate: %{text}",
                        text=radDataExtra,
                        zmin=zmin,
                        zmax=np.log10(zmax))
    
    fig_aug = go.Heatmap(z=augDataLog,
                        x=augFinals,
                        y=augInitials,
                        hovertemplate="Initial State: %{y}" + 
                                "<br>Final State: %{x}" + 
                                "<br>Boost Mult: %{z}" + 
                                "<br>Total Rate: %{text}",
                        text=augDataExtra,
                        zmin=zmin,
                        zmax=np.log10(zmax))
    
    fig_sat = go.Heatmap(z=satDataLog,
                        x=satFinals,
                        y=satInitials,
                        hovertemplate="Initial State: %{y}" + 
                                "<br>Final State: %{x}" + 
                                "<br>Boost Mult: %{z}" + 
                                "<br>Total Rate: %{text}",
                        text=satDataExtra,
                        zmin=zmin,
                        zmax=np.log10(zmax))
    
    
    if split:
        fig = make_subplots(rows=1, cols=1, subplot_titles=["Radiative Boost Matrix"])
        
        fig.append_trace(fig_rad, row=1, col=1)

        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)

        radMatrixURL = saveMatrixHtml(fig, "boostRadMatrix.html")
        
        fig = make_subplots(rows=1, cols=1, subplot_titles=["Auger Boost Matrix"])
        
        
        fig.append_trace(fig_aug, row=1, col=1)

        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)

        augMatrixURL = saveMatrixHtml(fig, "boostAugMatrix.html")
        
        fig = make_subplots(rows=1, cols=1, subplot_titles=["Satellite Boost Matrix"])
        
        fig.append_trace(fig_sat, row=1, col=1)

        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)

        satMatrixURL = saveMatrixHtml(fig, "boostSatMatrix.html")
    else:
        fig = make_subplots(rows=2, cols=2,
                        subplot_titles=[
                            "Radiative Boost Matrix", 
                            "Auger Boost Matrix", 
                            "Satellite Boost Matrix"
                            ],
                        specs=[[{}, {"rowspan": 2}],
                               [{}, None]],
                        column_widths=[len(radFinals) / (len(augFinals) + len(radFinals)),
                                       len(augFinals) / (len(augFinals) + len(radFinals))]
                        )
        
        fig.append_trace(fig_rad, row=1, col=1)
        fig.append_trace(fig_aug, row=1, col=2)
        fig.append_trace(fig_sat, row=2, col=1)
        
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        
        matricesLogURL = saveMatrixHtml(fig, "boostMatricesLog.html")
    
    if split:
        webbrowser.open_new(radMatrixURL)
        webbrowser.open_new(radMatrixLogURL)
        webbrowser.open_new(augMatrixURL)
        webbrowser.open_new(augMatrixLogURL)
        webbrowser.open_new(satMatrixURL)
        webbrowser.open_new(satMatrixLogURL)
    else:
        webbrowser.open_new(matricesURL)
        webbrowser.open_new(matricesLogURL)


# Initialize and configure the companion window with the rate matrixes to be analyzed for this simulation
def startMatrixWindow(split: bool = True):
    radInitials, radFinals, radData,\
    augInitials, augFinals, augData,\
    satInitials, satFinals, satData = prepareRateMatrices()
    
    if split:
        zmax = np.max(radData)
    else:
        zmax = np.max([np.max(radData), np.max(augData), np.max(satData)])
    
    fig_rad = go.Heatmap(z=radData,
                    #labels=dict(x="Final State", y="Initial State", color="Rate(s-1)"),
                    x=radFinals,
                    y=radInitials,
                    hovertemplate="Initial State: %{y}" + 
                              "<br>Final State: %{x}" + 
                              "<br>Rate: %{z}",
                    zmin=0,
                    zmax=zmax
                    )
    
    if split:
        zmax = np.max(augData)
    
    fig_aug = go.Heatmap(z=augData,
                    #labels=dict(x="Final State", y="Initial State", color="Rate(s-1)"),
                    x=augFinals,
                    y=augInitials,
                    hovertemplate="Initial State: %{y}" + 
                              "<br>Final State: %{x}" + 
                              "<br>Rate: %{z}",
                    zmin=0,
                    zmax=zmax
                    )
    
    if split:
        zmax = np.max(satData)
    
    fig_sat = go.Heatmap(z=satData,
                    #labels=dict(x="Final State", y="Initial State", color="Rate(s-1)"),
                    x=satFinals,
                    y=satInitials,
                    hovertemplate="Initial State: %{y}" + 
                              "<br>Final State: %{x}" + 
                              "<br>Rate: %{z}",
                    zmin=0,
                    zmax=zmax
                    )
    
    radMatrixURL = ""
    radMatrixLogURL = ""
    augMatrixURL = ""
    augMatrixLogURL = ""
    satMatrixURL = ""
    satMatrixLogURL = ""
    matricesURL = ""
    matricesLogURL = ""

    
    if split:
        fig = make_subplots(rows=1, cols=1, subplot_titles=["Radiative Rates Matrix"])
        
        fig.append_trace(fig_rad, row=1, col=1)

        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)

        radMatrixURL = saveMatrixHtml(fig, "rateRadMatrix.html")
        
        fig = make_subplots(rows=1, cols=1, subplot_titles=["Auger Rates Matrix"])
        
        
        fig.append_trace(fig_aug, row=1, col=1)

        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)

        augMatrixURL = saveMatrixHtml(fig, "rateAugMatrix.html")
        
        fig = make_subplots(rows=1, cols=1, subplot_titles=["Satellite Rates Matrix"])
        
        fig.append_trace(fig_sat, row=1, col=1)

        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)

        satMatrixURL = saveMatrixHtml(fig, "rateSatMatrix.html")
    else:
        fig = make_subplots(rows=2, cols=2,
                            subplot_titles=[
                                "Radiative Rates Matrix", 
                                "Auger Rates Matrix", 
                                "Satellite Rates Matrix"
                                ],
                            specs=[[{}, {"rowspan": 2}],
                                [{}, None]],
                            column_widths=[len(radFinals) / (len(augFinals) + len(radFinals)),
                                        len(augFinals) / (len(augFinals) + len(radFinals))]
                            )
        
        fig.append_trace(fig_rad, row=1, col=1)
        fig.append_trace(fig_aug, row=1, col=2)
        fig.append_trace(fig_sat, row=2, col=1)
        
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        
        #fig.update_layout(yaxis = dict(scaleanchor = 'x'),
        #                  yaxis2 = dict(scaleanchor = 'x2'),
        #                  yaxis3 = dict(scaleanchor = 'x3'))
        
        
        matricesURL = saveMatrixHtml(fig, "rateMatrices.html")
    
    radDataLog = np.log10(radData)
    augDataLog = np.log10(augData)
    satDataLog = np.log10(satData)
    
    if split:
        zmin = np.min(radDataLog[radDataLog != -np.inf])
    else:
        zmin = min([np.min(radDataLog[radDataLog != -np.inf]), np.min(augDataLog[augDataLog  != -np.inf]), np.min(satDataLog[satDataLog != -np.inf])])
    
    fig_rad = go.Heatmap(z=radDataLog,
                    #labels=dict(x="Final State", y="Initial State", color="Rate(s-1)"),
                    x=radFinals,
                    y=radInitials,
                    hovertemplate="Initial State: %{y}" + 
                              "<br>Final State: %{x}" + 
                              "<br>Rate: %{text}",
                    text=radData,
                    zmin=zmin,
                    zmax=np.log10(zmax)
                    )
    
    if split:
        zmin = np.min(augDataLog[augDataLog != -np.inf])
    
    fig_aug = go.Heatmap(z=augDataLog,
                    #labels=dict(x="Final State", y="Initial State", color="Rate(s-1)"),
                    x=augFinals,
                    y=augInitials,
                    hovertemplate="Initial State: %{y}" + 
                              "<br>Final State: %{x}" + 
                              "<br>Rate: %{text}",
                    text=augData,
                    zmin=zmin,
                    zmax=np.log10(zmax)
                    )
    
    if split:
        zmin = np.min(satDataLog[satDataLog != -np.inf])
    
    fig_sat = go.Heatmap(z=satDataLog,
                    #labels=dict(x="Final State", y="Initial State", color="Rate(s-1)"),
                    x=satFinals,
                    y=satInitials,
                    hovertemplate="Initial State: %{y}" + 
                              "<br>Final State: %{x}" + 
                              "<br>Rate: %{text}",
                    text=satData,
                    zmin=zmin,
                    zmax=np.log10(zmax)
                    )
    
    
    if split:
        fig = make_subplots(rows=1, cols=1, subplot_titles=["Radiative Rates Matrix"])
        
        fig.append_trace(fig_rad, row=1, col=1)

        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)

        radMatrixLogURL = saveMatrixHtml(fig, "rateRadMatrixLog.html")
        
        fig = make_subplots(rows=1, cols=1, subplot_titles=["Auger Rates Matrix"])
        
        
        fig.append_trace(fig_aug, row=1, col=1)

        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)

        augMatrixLogURL = saveMatrixHtml(fig, "rateAugMatrixLog.html")
        
        fig = make_subplots(rows=1, cols=1, subplot_titles=["Satellite Rates Matrix"])
        
        fig.append_trace(fig_sat, row=1, col=1)

        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)

        satMatrixLogURL = saveMatrixHtml(fig, "rateSatMatrixLog.html")
    else:
        fig = make_subplots(rows=2, cols=2,
                        subplot_titles=[
                            "Radiative Rates Matrix", 
                            "Auger Rates Matrix", 
                            "Satellite Rates Matrix"
                            ],
                        specs=[[{}, {"rowspan": 2}],
                               [{}, None]],
                        column_widths=[len(radFinals) / (len(augFinals) + len(radFinals)),
                                       len(augFinals) / (len(augFinals) + len(radFinals))]
                        )

        fig.append_trace(fig_rad, row=1, col=1)
        fig.append_trace(fig_aug, row=1, col=2)
        fig.append_trace(fig_sat, row=2, col=1)
        
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        
        #fig.update_layout(yaxis = dict(scaleanchor = 'x'),
        #                  yaxis2 = dict(scaleanchor = 'x2'),
        #                  yaxis3 = dict(scaleanchor = 'x3'))
        
        
        matricesLogURL = saveMatrixHtml(fig, "rateMatricesLog.html")
    
    
    if split:
        webbrowser.open_new(radMatrixURL)
        webbrowser.open_new_tab(radMatrixLogURL)
        webbrowser.open_new(augMatrixURL)
        webbrowser.open_new_tab(augMatrixLogURL)
        webbrowser.open_new(satMatrixURL)
        webbrowser.open_new_tab(satMatrixLogURL)
    else:
        webbrowser.open_new(matricesURL)
        webbrowser.open_new_tab(matricesLogURL)
    


# Initialize and configure the companion window with the cascade graph to be analyzed for this simulation
def startCascadeSatellite():
    nodes, edges = computeCascadeGraph("satellite")
    
    edge_x_sat = []
    edge_y_sat = []
    edge_text_sat = []
    
    edge_x_aug = []
    edge_y_aug = []
    edge_text_aug = []
    
    edge_x_dia = []
    edge_y_dia = []
    edge_text_dia = []
    
    edge_x_selected = []
    edge_y_selected = []
    edge_text_selected = []
    
    edge_x_selected_cascade_sat = []
    edge_y_selected_cascade_sat = []
    edge_text_selected_cascade_sat = []
    
    edge_x_selected_cascade_aug = []
    edge_y_selected_cascade_aug = []
    edge_text_selected_cascade_aug = []
    
    edge_x_selected_cascade_dia = []
    edge_y_selected_cascade_dia = []
    edge_text_selected_cascade_dia = []
    
    line_hover_x_sat = []
    line_hover_y_sat = []
    
    line_hover_x_aug = []
    line_hover_y_aug = []
    
    line_hover_x_dia = []
    line_hover_y_dia = []
    
    line_hover_x_selected = []
    line_hover_y_selected = []
    
    line_hover_x_selected_cascade_sat = []
    line_hover_y_selected_cascade_sat = []
    
    line_hover_x_selected_cascade_aug = []
    line_hover_y_selected_cascade_aug = []
    
    line_hover_x_selected_cascade_dia = []
    line_hover_y_selected_cascade_dia = []
    
    
    selected_initials: List[str] = []
    
    selected_transitions: List[Dict[str, str]] = []
    for transition in generalVars.the_dictionary:
        if generalVars.the_dictionary[transition]['selected_state']:
            for key in generalVars.label1:
                selected_initials.append(generalVars.the_dictionary[transition]['low_level'] + key) # type: ignore
                selected_initials.append(key + generalVars.the_dictionary[transition]['low_level']) # type: ignore
            
            if len(guiVars.jj_list) == 0:
                for key in generalVars.label1:
                    selected_transitions.append({'low': generalVars.the_dictionary[transition]['low_level'] + key, 'high': generalVars.the_dictionary[transition]['high_level'] + key}) # type: ignore
                    selected_transitions.append({'low': generalVars.the_dictionary[transition]['low_level'] + key, 'high': key + generalVars.the_dictionary[transition]['high_level']}) # type: ignore
                    selected_transitions.append({'low': key + generalVars.the_dictionary[transition]['low_level'], 'high': generalVars.the_dictionary[transition]['high_level'] + key}) # type: ignore
                    selected_transitions.append({'low': key + generalVars.the_dictionary[transition]['low_level'], 'high': key + generalVars.the_dictionary[transition]['high_level']}) # type: ignore
            else:
                for jj in guiVars.jj_list:
                    for key in generalVars.label1:
                        selected_transitions.append({'low': generalVars.the_dictionary[transition]['low_level'] + key, 'high': generalVars.the_dictionary[transition]['high_level'] + key, 'jj': str(jj)}) # type: ignore
                        selected_transitions.append({'low': generalVars.the_dictionary[transition]['low_level'] + key, 'high': key + generalVars.the_dictionary[transition]['high_level'], 'jj': str(jj)}) # type: ignore
                        selected_transitions.append({'low': key + generalVars.the_dictionary[transition]['low_level'], 'high': generalVars.the_dictionary[transition]['high_level'] + key, 'jj': str(jj)}) # type: ignore
                        selected_transitions.append({'low': key + generalVars.the_dictionary[transition]['low_level'], 'high': key + generalVars.the_dictionary[transition]['high_level'], 'jj': str(jj)}) # type: ignore
    
    cascade_initials: List[str] = []
    edge_type: List[str] = ['na'] * len(edges)
    
    # Determine the type of each computed edge depending on the selected transitions in the interface
    while True:
        last_cascade_initials = cascade_initials.copy()
        
        for i, edge in enumerate(edges):
            if len(guiVars.jj_list) == 0:
                transition = {'low': nodes[edge['initial']]['label'].split()[0], # type: ignore
                            'high': nodes[edge['final']]['label'].split()[0]} # type: ignore
            else:
                transition = {'low': nodes[edge['initial']]['label'].split()[0], # type: ignore
                            'high': nodes[edge['final']]['label'].split()[0], # type: ignore
                            'jj': nodes[edge['initial']]['label'].split()[1]} # type: ignore
            
            if transition in selected_transitions:
                edge_type[i] = 's'
            else:
                if transition['high'] not in selected_initials and transition['high'] not in cascade_initials:
                    if len(transition['low']) == 2 and len(transition['high']) == 2:
                        edge_type[i] = 'ud'
                    elif 'aug' in nodes[edge['initial']]: # type: ignore
                        edge_type[i] = 'ua'
                    else:
                        edge_type[i] = 'us'
                else:
                    if len(transition['low']) == 2 and len(transition['high']) == 2:
                        edge_type[i] = 'cd'
                    elif 'aug' in nodes[edge['initial']]: # type: ignore
                        edge_type[i] = 'ca'
                    else:
                        edge_type[i] = 'cs'
                    
                    if transition['low'] not in cascade_initials:
                        cascade_initials.append(transition['low'])
        
        if cascade_initials == last_cascade_initials:
            break
    
    # Add the edges to the corresponding list to show in the graph
    for i, et in enumerate(edge_type):
        edge = edges[i]
        
        edge_append_x = edge_x_sat
        edge_append_y = edge_y_sat
        edge_append_text = edge_text_sat
        line_hover_append_x = line_hover_x_sat
        line_hover_append_y = line_hover_y_sat
        
        if et == 's':
            edge_append_x = edge_x_selected
            edge_append_y = edge_y_selected
            edge_append_text = edge_text_selected
            line_hover_append_x = line_hover_x_selected
            line_hover_append_y = line_hover_y_selected
        elif et == 'ud':
            edge_append_x = edge_x_dia
            edge_append_y = edge_y_dia
            edge_append_text = edge_text_dia
            line_hover_append_x = line_hover_x_dia
            line_hover_append_y = line_hover_y_dia
        elif et == 'ua':
            edge_append_x = edge_x_aug
            edge_append_y = edge_y_aug
            edge_append_text = edge_text_aug
            line_hover_append_x = line_hover_x_aug
            line_hover_append_y = line_hover_y_aug
        elif et == 'us':
            pass
        elif et == 'cd':
            edge_append_x = edge_x_selected_cascade_dia
            edge_append_y = edge_y_selected_cascade_dia
            edge_append_text = edge_text_selected_cascade_dia
            line_hover_append_x = line_hover_x_selected_cascade_dia
            line_hover_append_y = line_hover_y_selected_cascade_dia
        elif et == 'ca':
            edge_append_x = edge_x_selected_cascade_aug
            edge_append_y = edge_y_selected_cascade_aug
            edge_append_text = edge_text_selected_cascade_aug
            line_hover_append_x = line_hover_x_selected_cascade_aug
            line_hover_append_y = line_hover_y_selected_cascade_aug
        elif et == 'cs':
            edge_append_x = edge_x_selected_cascade_sat
            edge_append_y = edge_y_selected_cascade_sat
            edge_append_text = edge_text_selected_cascade_sat
            line_hover_append_x = line_hover_x_selected_cascade_sat
            line_hover_append_y = line_hover_y_selected_cascade_sat
        else:
            raise RuntimeError("Error in satellite cascade graph calculation: Expected edge type of s, ua, us, ca or cs, got: " + et)
        
        edge_append_x.append(nodes[edge['initial']]['x']) # type: ignore
        edge_append_x.append(nodes[edge['final']]['x']) # type: ignore
        edge_append_x.append(None)
    
        edge_append_y.append(nodes[edge['initial']]['y']) # type: ignore
        edge_append_y.append(nodes[edge['final']]['y']) # type: ignore
        edge_append_y.append(None)
        
        line_hover_append_x.append((nodes[edge['final']]['x'] + nodes[edge['initial']]['x']) / 2) # type: ignore
        line_hover_append_y.append((nodes[edge['final']]['y'] + nodes[edge['initial']]['y']) / 2) # type: ignore
        
        edge_append_text.append("Energy: " + str(edge['energy']) + " eV" + \
                                "<br>Rate: " + str(edge['rate']) + " s-1" + \
                                "<br>Width: " + str(edge['width']) + " eV")
    
    
    edge_trace_sat = go.Scatter(
        name='Unselected Satellite Transitions',
        legendrank=4,
        showlegend=len(edge_x_sat) > 0,
        x=edge_x_sat, y=edge_y_sat,
        mode='lines+markers',
        line=dict(width=0.5, color='gray'),
        marker=dict(size=10, symbol='arrow-bar-up', angleref='previous', color='gray'),
        hoverinfo='none')
    
    edge_trace_aug = go.Scatter(
        name='Unselected Auger Transitions',
        legendrank=4,
        showlegend=len(edge_x_aug) > 0,
        x=edge_x_aug, y=edge_y_aug,
        mode='lines+markers',
        line=dict(width=0.5, color='lightgray'),
        marker=dict(size=10, symbol='arrow-bar-up', angleref='previous', color='lightgray'),
        hoverinfo='none')
    
    edge_trace_dia = go.Scatter(
        name='Unselected Diagram Transitions',
        legendrank=4,
        showlegend=len(edge_x_dia) > 0,
        x=edge_x_dia, y=edge_y_dia,
        mode='lines+markers',
        line=dict(width=0.5, color='yellow'),
        marker=dict(size=10, symbol='arrow-bar-up', angleref='previous', color='yellow'),
        hoverinfo='none')
    
    edge_trace_selected = go.Scatter(
        name='Selected Transitions',
        legendrank=2,
        showlegend=len(edge_x_selected) > 0,
        x=edge_x_selected, y=edge_y_selected,
        mode='lines+markers',
        line=dict(width=0.5, color='red'),
        marker=dict(size=10, symbol='arrow-bar-up', angleref='previous', color='red'),
        hoverinfo='none')
    
    edge_trace_selected_cascade_aug = go.Scatter(
        name='Selected Cascade Auger Transitions',
        legendrank=3,
        showlegend=len(edge_x_selected_cascade_aug) > 0,
        x=edge_x_selected_cascade_aug, y=edge_y_selected_cascade_aug,
        mode='lines+markers',
        line=dict(width=0.5, color='blue'),
        marker=dict(size=10, symbol='arrow-bar-up', angleref='previous', color='blue'),
        hoverinfo='none')
    
    edge_trace_selected_cascade_sat = go.Scatter(
        name='Selected Cascade Satellite Transitions',
        legendrank=3,
        showlegend=len(edge_x_selected_cascade_sat) > 0,
        x=edge_x_selected_cascade_sat, y=edge_y_selected_cascade_sat,
        mode='lines+markers',
        line=dict(width=0.5, color='green'),
        marker=dict(size=10, symbol='arrow-bar-up', angleref='previous', color='green'),
        hoverinfo='none')
    
    edge_trace_selected_cascade_dia = go.Scatter(
        name='Selected Cascade Diagram Transitions',
        legendrank=3,
        showlegend=len(edge_x_selected_cascade_dia) > 0,
        x=edge_x_selected_cascade_dia, y=edge_y_selected_cascade_dia,
        mode='lines+markers',
        line=dict(width=0.5, color='purple'),
        marker=dict(size=10, symbol='arrow-bar-up', angleref='previous', color='purple'),
        hoverinfo='none')
    
    line_hover_trace_sat = go.Scatter(
        showlegend=False,
        x=line_hover_x_sat, y=line_hover_y_sat,
        mode='markers',
        marker=dict(opacity=[0 for _ in range(len(line_hover_x_sat))]),
        hoverinfo='text',
        hoverlabel=dict(bgcolor='gray'),
        text=edge_text_sat)
    
    line_hover_trace_aug = go.Scatter(
        showlegend=False,
        x=line_hover_x_aug, y=line_hover_y_aug,
        mode='markers',
        marker=dict(opacity=[0 for _ in range(len(line_hover_x_aug))]),
        hoverinfo='text',
        hoverlabel=dict(bgcolor='lightgray'),
        text=edge_text_aug)
    
    line_hover_trace_dia = go.Scatter(
        showlegend=False,
        x=line_hover_x_dia, y=line_hover_y_dia,
        mode='markers',
        marker=dict(opacity=[0 for _ in range(len(line_hover_x_dia))]),
        hoverinfo='text',
        hoverlabel=dict(bgcolor='yellow'),
        text=edge_text_dia)
    
    line_hover_trace_selected = go.Scatter(
        showlegend=False,
        x=line_hover_x_selected, y=line_hover_y_selected,
        mode='markers',
        marker=dict(opacity=[0 for _ in range(len(line_hover_x_selected))]),
        hoverinfo='text',
        hoverlabel=dict(bgcolor='red'),
        text=edge_text_selected)
    
    line_hover_trace_selected_cascade_aug = go.Scatter(
        showlegend=False,
        x=line_hover_x_selected_cascade_aug, y=line_hover_y_selected_cascade_aug,
        mode='markers',
        marker=dict(opacity=[0 for _ in range(len(line_hover_x_selected_cascade_aug))]),
        hoverinfo='text',
        hoverlabel=dict(bgcolor='blue'),
        text=edge_text_selected_cascade_aug)
    
    line_hover_trace_selected_cascade_sat = go.Scatter(
        showlegend=False,
        x=line_hover_x_selected_cascade_sat, y=line_hover_y_selected_cascade_sat,
        mode='markers',
        marker=dict(opacity=[0 for _ in range(len(line_hover_x_selected_cascade_sat))]),
        hoverinfo='text',
        hoverlabel=dict(bgcolor='green'),
        text=edge_text_selected_cascade_sat)
    
    line_hover_trace_selected_cascade_dia = go.Scatter(
        showlegend=False,
        x=line_hover_x_selected_cascade_dia, y=line_hover_y_selected_cascade_dia,
        mode='markers',
        marker=dict(opacity=[0 for _ in range(len(line_hover_x_selected_cascade_dia))]),
        hoverinfo='text',
        hoverlabel=dict(bgcolor='purple'),
        text=edge_text_selected_cascade_dia)
    
    
    node_x_sat = []
    node_y_sat = []
    node_text_sat = []
    
    node_x_aug = []
    node_y_aug = []
    node_text_aug = []
    
    node_x_dia = []
    node_y_dia = []
    node_text_dia = []
    
    for node in nodes:
        if 'aug' not in node:
            node_x_append = node_x_sat
            node_y_append = node_y_sat
            node_text_append = node_text_sat
        elif 'dia' not in node:
            node_x_append = node_x_dia
            node_y_append = node_y_dia
            node_text_append = node_text_dia
        else:
            node_x_append = node_x_aug
            node_y_append = node_y_aug
            node_text_append = node_text_aug
        
        node_x_append.append(node['x'])
        node_y_append.append(node['y'])
        
        if 'cross' in node:
            node_text_append.append(str(node['label']) + \
                            "<br>State Energy: " + str(node['Energy']) + " eV" + \
                            "<br>Excitation Mechanism: " + str(node['type']) + \
                            "<br>Cross Section: " + str(node['cross']) + \
                            "<br>Beam: " + str(node['beam']) + " eV")
        else:
            node_text_append.append(node['label'] + \
                            "<br>State Energy: " + str(node['Energy']) + " eV") # type: ignore
    
    node_trace_sat = go.Scatter(
        name='Satellite Atomic States',
        legendrank=1,
        x=node_x_sat, y=node_y_sat,
        mode='markers',
        hoverinfo='text',
        text=node_text_sat,
        marker=dict(
            showscale=False,
            colorscale='YlGnBu',
            reversescale=True,
            color='gray',
            size=10,
            line_width=2
        ))
    
    node_trace_aug = go.Scatter(
        name='Auger Atomic States',
        legendrank=1,
        x=node_x_aug, y=node_y_aug,
        mode='markers',
        hoverinfo='text',
        text=node_text_aug,
        marker=dict(
            showscale=False,
            colorscale='YlGnBu',
            reversescale=True,
            color='lightgray',
            size=10,
            line_width=2
        ))
    
    node_trace_dia = go.Scatter(
        name='Diagram Atomic States',
        legendrank=1,
        x=node_x_dia, y=node_y_dia,
        mode='markers',
        hoverinfo='text',
        text=node_text_dia,
        marker=dict(
            showscale=False,
            colorscale='YlGnBu',
            reversescale=True,
            color='yellow',
            size=10,
            line_width=2
        ))
    
    data_full = [edge_trace_sat, line_hover_trace_sat,
                 edge_trace_aug, line_hover_trace_aug,
                 edge_trace_dia, line_hover_trace_dia]
    
    data_selected = [edge_trace_selected, line_hover_trace_selected]
    data_selected_cascade_aug = [edge_trace_selected_cascade_aug, line_hover_trace_selected_cascade_aug]
    data_selected_cascade_sat = [edge_trace_selected_cascade_sat, line_hover_trace_selected_cascade_sat]
    data_selected_cascade_dia = [edge_trace_selected_cascade_dia, line_hover_trace_selected_cascade_dia]
    
    data_list = data_full + data_selected + \
                data_selected_cascade_aug + \
                data_selected_cascade_sat + \
                data_selected_cascade_dia + \
                [node_trace_sat, node_trace_aug, node_trace_dia]
    
    fig = go.Figure(data=data_list,
                    layout=go.Layout(
                        title='<br>Satellite Levels Cascade',
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20,l=5,r=5,t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                    ))
    
    fig.update_yaxes(
        title_text = "Energy / eV (not to scale)",
        title_standoff = 25)
    
    fig.update_xaxes(
        title_text = "2J value",
        title_standoff = 25)
    
    fig.update_layout(showlegend=True)
    
    cascadeURL = saveMatrixHtml(fig, "satelliteCascade.html")

    
    webbrowser.open_new(cascadeURL)



# Initialize and configure the companion window with the cascade graph to be analyzed for this simulation
def startCascadeDiagram():
    nodes, edges = computeCascadeGraph("diagram")
    
    edge_x = []
    edge_y = []
    edge_text = []
    
    edge_x_selected = []
    edge_y_selected = []
    edge_text_selected = []
    
    edge_x_selected_cascade = []
    edge_y_selected_cascade = []
    edge_text_selected_cascade = []
    
    line_hover_x = []
    line_hover_y = []
    
    line_hover_x_selected = []
    line_hover_y_selected = []
    
    line_hover_x_selected_cascade = []
    line_hover_y_selected_cascade = []
    
    selected_initials: List[str] = []
    
    selected_transitions: List[Dict[str, str]] = []
    for transition in generalVars.the_dictionary:
        if generalVars.the_dictionary[transition]['selected_state']:
            selected_initials.append(generalVars.the_dictionary[transition]['low_level']) # type: ignore
            
            if len(guiVars.jj_list) == 0:
                selected_transitions.append({'low': generalVars.the_dictionary[transition]['low_level'], 'high': generalVars.the_dictionary[transition]['high_level']}) # type: ignore
            else:
                for jj in guiVars.jj_list:
                    selected_transitions.append({'low': generalVars.the_dictionary[transition]['low_level'], 'high': generalVars.the_dictionary[transition]['high_level'], 'jj': str(jj)}) # type: ignore
    
    cascade_initials: List[str] = []
    edge_type: List[str] = ['na'] * len(edges)
    
    # Determine the type of each computed edge depending on the selected transitions in the interface
    while True:
        last_cascade_initials = cascade_initials.copy()
        
        for i, edge in enumerate(edges):
            if len(guiVars.jj_list) == 0:
                transition = {'low': nodes[edge['initial']]['label'].split()[0], # type: ignore
                            'high': nodes[edge['final']]['label'].split()[0]} # type: ignore
            else:
                transition = {'low': nodes[edge['initial']]['label'].split()[0], # type: ignore
                            'high': nodes[edge['final']]['label'].split()[0], # type: ignore
                            'jj': nodes[edge['initial']]['label'].split()[1]} # type: ignore
            
            if transition in selected_transitions:
                edge_type[i] = 's'
            else:
                if transition['high'] not in selected_initials and transition['high'] not in cascade_initials:
                    edge_type[i] = 'u'
                else:
                    edge_type[i] = 'c'
                    if transition['low'] not in cascade_initials:
                        cascade_initials.append(transition['low'])
        
        if cascade_initials == last_cascade_initials:
            break
    
    # Add the edges to the corresponding list to show in the graph
    for i, et in enumerate(edge_type):
        edge = edges[i]
        
        edge_append_x = edge_x
        edge_append_y = edge_y
        edge_append_text = edge_text
        line_hover_append_x = line_hover_x
        line_hover_append_y = line_hover_y
        
        if et == 's':
            edge_append_x = edge_x_selected
            edge_append_y = edge_y_selected
            edge_append_text = edge_text_selected
            line_hover_append_x = line_hover_x_selected
            line_hover_append_y = line_hover_y_selected
        elif et == 'u':
            edge_append_x = edge_x
            edge_append_y = edge_y
            edge_append_text = edge_text
            line_hover_append_x = line_hover_x
            line_hover_append_y = line_hover_y
        elif et == 'c':
            edge_append_x = edge_x_selected_cascade
            edge_append_y = edge_y_selected_cascade
            edge_append_text = edge_text_selected_cascade
            line_hover_append_x = line_hover_x_selected_cascade
            line_hover_append_y = line_hover_y_selected_cascade
        else:
            raise RuntimeError("Error in diagram cascade graph calculation: Expected edge type of s, u or c, got: " + et)
        
        edge_append_x.append(nodes[edge['initial']]['x']) # type: ignore
        edge_append_x.append(nodes[edge['final']]['x']) # type: ignore
        edge_append_x.append(None)
    
        edge_append_y.append(nodes[edge['initial']]['y']) # type: ignore
        edge_append_y.append(nodes[edge['final']]['y']) # type: ignore
        edge_append_y.append(None)
        
        
        line_hover_append_x.append((nodes[edge['final']]['x'] + nodes[edge['initial']]['x']) / 2) # type: ignore
        line_hover_append_y.append((nodes[edge['final']]['y'] + nodes[edge['initial']]['y']) / 2) # type: ignore
        
        edge_append_text.append("Energy: " + str(edge['energy']) + " eV" + \
                                "<br>Rate: " + str(edge['rate']) + " s-1" + \
                                "<br>Width: " + str(edge['width']) + " eV")
    
    
    edge_trace = go.Scatter(
        name='Unselected Transitions',
        legendrank=4,
        showlegend=len(edge_x) > 0,
        x=edge_x, y=edge_y,
        mode='lines+markers',
        line=dict(width=0.5, color='#888'),
        marker=dict(size=10, symbol='arrow-bar-up', angleref='previous', color='#888'),
        hoverinfo='none')
    
    edge_trace_selected = go.Scatter(
        name='Selected Transitions',
        legendrank=2,
        showlegend=len(edge_x_selected) > 0,
        x=edge_x_selected, y=edge_y_selected,
        mode='lines+markers',
        line=dict(width=0.5, color='red'),
        marker=dict(size=10, symbol='arrow-bar-up', angleref='previous', color='red'),
        hoverinfo='none')
    
    edge_trace_selected_cascade = go.Scatter(
        name='Selected Cascade Transitions',
        legendrank=3,
        showlegend=len(edge_x_selected_cascade) > 0,
        x=edge_x_selected_cascade, y=edge_y_selected_cascade,
        mode='lines+markers',
        line=dict(width=0.5, color='green'),
        marker=dict(size=10, symbol='arrow-bar-up', angleref='previous', color='green'),
        hoverinfo='none')
    
    line_hover_trace = go.Scatter(
        showlegend=False,
        x=line_hover_x, y=line_hover_y,
        mode='markers',
        marker=dict(opacity=[0 for _ in range(len(line_hover_x))]),
        hoverinfo='text',
        hoverlabel=dict(bgcolor='#888'),
        text=edge_text)
    
    line_hover_trace_selected = go.Scatter(
        showlegend=False,
        x=line_hover_x_selected, y=line_hover_y_selected,
        mode='markers',
        marker=dict(opacity=[0 for _ in range(len(line_hover_x_selected))]),
        hoverinfo='text',
        hoverlabel=dict(bgcolor='red'),
        text=edge_text_selected)
    
    line_hover_trace_selected_cascade = go.Scatter(
        showlegend=False,
        x=line_hover_x_selected_cascade, y=line_hover_y_selected_cascade,
        mode='markers',
        marker=dict(opacity=[0 for _ in range(len(line_hover_x_selected_cascade))]),
        hoverinfo='text',
        hoverlabel=dict(bgcolor='green'),
        text=edge_text_selected_cascade)
    
    
    node_x = []
    node_y = []
    node_text = []
    
    for node in nodes:
        node_x.append(node['x'])
        node_y.append(node['y'])
        
        if 'cross' in node:
            node_text.append(str(node['label']) + \
                            "<br>State Energy: " + str(node['Energy']) + " eV" + \
                            "<br>Excitation Mechanism: " + str(node['type']) + \
                            "<br>Cross Section: " + str(node['cross']) + \
                            "<br>Beam: " + str(node['beam']) + " eV")
        else:
            node_text.append(node['label'] + \
                            "<br>State Energy: " + str(node['Energy']) + " eV") # type: ignore
    
    node_trace = go.Scatter(
        name='Atomic States',
        legendrank=1,
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        text=node_text,
        marker=dict(
            showscale=False,
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=10,
            line_width=2
        ))
    
    data_full = [edge_trace, line_hover_trace]
    data_selected = [edge_trace_selected, line_hover_trace_selected]
    data_selected_cascade = [edge_trace_selected_cascade, line_hover_trace_selected_cascade]
    
    data_list = data_full + data_selected + data_selected_cascade + [node_trace]
    
    fig = go.Figure(data=data_list,
                    layout=go.Layout(
                        title='<br>Diagram Levels Cascade',
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20,l=5,r=5,t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                    ))
    
    fig.update_yaxes(
        title_text = "Energy / eV (not to scale)",
        title_standoff = 25)
    
    fig.update_xaxes(
        title_text = "2J value",
        title_standoff = 25)
    
    fig.update_layout(showlegend=True)
    
    cascadeURL = saveMatrixHtml(fig, "diagramCascade.html")

    
    webbrowser.open_new(cascadeURL)


# Initialize and configure the companion window with the cascade graph to be analyzed for this simulation
def startCascadeAuger():
    nodes, edges = computeCascadeGraph("auger")
    
    edge_x = []
    edge_y = []
    edge_text = []
    
    edge_x_dia = []
    edge_y_dia = []
    edge_text_dia = []
    
    edge_x_selected = []
    edge_y_selected = []
    edge_text_selected = []
    
    edge_x_selected_cascade = []
    edge_y_selected_cascade = []
    edge_text_selected_cascade = []
    
    edge_x_selected_cascade_dia = []
    edge_y_selected_cascade_dia = []
    edge_text_selected_cascade_dia = []
    
    line_hover_x = []
    line_hover_y = []
    
    line_hover_x_dia = []
    line_hover_y_dia = []
    
    line_hover_x_selected = []
    line_hover_y_selected = []
    
    line_hover_x_selected_cascade = []
    line_hover_y_selected_cascade = []
    
    line_hover_x_selected_cascade_dia = []
    line_hover_y_selected_cascade_dia = []
    
    selected_initials: List[str] = []
    
    selected_transitions: List[Dict[str, str]] = []
    for transition in generalVars.the_aug_dictionary:
        if generalVars.the_aug_dictionary[transition]['selected_state']:
            selected_initials.append(generalVars.the_aug_dictionary[transition]['low_level']) # type: ignore
            
            if len(guiVars.jj_list) == 0:
                selected_transitions.append({'low': generalVars.the_aug_dictionary[transition]['low_level'],
                                             'high': generalVars.the_aug_dictionary[transition]['high_level'],
                                             'auger': generalVars.the_aug_dictionary[transition]['auger_level']}) # type: ignore
            else:
                for jj in guiVars.jj_list:
                    selected_transitions.append({'low': generalVars.the_aug_dictionary[transition]['low_level'],
                                                 'high': generalVars.the_aug_dictionary[transition]['high_level'],
                                                 'auger': generalVars.the_aug_dictionary[transition]['auger_level'],
                                                 'jj': str(jj)}) # type: ignore
    
    cascade_initials: List[str] = []
    edge_type: List[str] = ['na'] * len(edges)
    
    # Determine the type of each computed edge depending on the selected transitions in the interface
    while True:
        last_cascade_initials = cascade_initials.copy()
        
        for i, edge in enumerate(edges):
            if len(nodes[edge['final']]['label'].split()[0]) == 4: # type: ignore
                if len(guiVars.jj_list) == 0:
                    transition = {'low': nodes[edge['initial']]['label'].split()[0], # type: ignore
                                'high': nodes[edge['final']]['label'].split()[0][:2], # type: ignore
                                'auger': nodes[edge['final']]['label'].split()[0][2:]} # type: ignore
                else:
                    transition = {'low': nodes[edge['initial']]['label'].split()[0], # type: ignore
                                'high': nodes[edge['final']]['label'].split()[0][:2], # type: ignore
                                'auger': nodes[edge['final']]['label'].split()[0][2:], # type: ignore
                                'jj': nodes[edge['initial']]['label'].split()[1]} # type: ignore
            else:
                if len(guiVars.jj_list) == 0:
                    transition = {'low': nodes[edge['initial']]['label'].split()[0], # type: ignore
                                'high': nodes[edge['final']]['label'].split()[0]} # type: ignore
                else:
                    transition = {'low': nodes[edge['initial']]['label'].split()[0], # type: ignore
                                'high': nodes[edge['final']]['label'].split()[0], # type: ignore
                                'jj': nodes[edge['initial']]['label'].split()[1]} # type: ignore
            
            if transition in selected_transitions:
                edge_type[i] = 's'
            else:
                if 'auger' not in transition:
                    if transition['high'] not in selected_initials and transition['high'] not in cascade_initials:
                        edge_type[i] = 'ud'
                    else:
                        edge_type[i] = 'cd'
                        
                        if transition['low'] not in cascade_initials:
                            cascade_initials.append(transition['low'])
                else:
                    if transition['high'] + transition['auger'] not in selected_initials and transition['high'] + transition['auger'] not in cascade_initials:
                        edge_type[i] = 'ua'
                    else:
                        edge_type[i] = 'ca'
                        
                        if transition['low'] not in cascade_initials:
                            cascade_initials.append(transition['low'])
                    
                
        if cascade_initials == last_cascade_initials:
            break
    
    # Add the edges to the corresponding list to show in the graph
    for i, et in enumerate(edge_type):
        edge = edges[i]
        
        edge_append_x = edge_x
        edge_append_y = edge_y
        edge_append_text = edge_text
        line_hover_append_x = line_hover_x
        line_hover_append_y = line_hover_y
        
        if et == 's':
            edge_append_x = edge_x_selected
            edge_append_y = edge_y_selected
            edge_append_text = edge_text_selected
            line_hover_append_x = line_hover_x_selected
            line_hover_append_y = line_hover_y_selected
        elif et == 'ud':
            edge_append_x = edge_x_dia
            edge_append_y = edge_y_dia
            edge_append_text = edge_text_dia
            line_hover_append_x = line_hover_x_dia
            line_hover_append_y = line_hover_y_dia
        elif et == 'ua':
            pass
        elif et == 'cd':
            edge_append_x = edge_x_selected_cascade_dia
            edge_append_y = edge_y_selected_cascade_dia
            edge_append_text = edge_text_selected_cascade_dia
            line_hover_append_x = line_hover_x_selected_cascade_dia
            line_hover_append_y = line_hover_y_selected_cascade_dia
        elif et == 'ca':
            edge_append_x = edge_x_selected_cascade
            edge_append_y = edge_y_selected_cascade
            edge_append_text = edge_text_selected_cascade
            line_hover_append_x = line_hover_x_selected_cascade
            line_hover_append_y = line_hover_y_selected_cascade
        else:
            raise RuntimeError("Error in auger cascade graph calculation: Expected edge type of s, u or c, got: " + et)
        
        edge_append_x.append(nodes[edge['initial']]['x']) # type: ignore
        edge_append_x.append(nodes[edge['final']]['x']) # type: ignore
        edge_append_x.append(None)
    
        edge_append_y.append(nodes[edge['initial']]['y']) # type: ignore
        edge_append_y.append(nodes[edge['final']]['y']) # type: ignore
        edge_append_y.append(None)
        
        
        line_hover_append_x.append((nodes[edge['final']]['x'] + nodes[edge['initial']]['x']) / 2) # type: ignore
        line_hover_append_y.append((nodes[edge['final']]['y'] + nodes[edge['initial']]['y']) / 2) # type: ignore
        
        edge_append_text.append("Energy: " + str(edge['energy']) + " eV" + \
                                "<br>Rate: " + str(edge['rate']) + " s-1" + \
                                "<br>Width: " + str(edge['width']) + " eV")
    
    
    edge_trace = go.Scatter(
        name='Unselected Auger Transitions',
        legendrank=4,
        showlegend=len(edge_x) > 0,
        x=edge_x, y=edge_y,
        mode='lines+markers',
        line=dict(width=0.5, color='gray'),
        marker=dict(size=10, symbol='arrow-bar-up', angleref='previous', color='gray'),
        hoverinfo='none')
    
    edge_trace_dia = go.Scatter(
        name='Unselected Diagram Transitions',
        legendrank=4,
        showlegend=len(edge_x_dia) > 0,
        x=edge_x_dia, y=edge_y_dia,
        mode='lines+markers',
        line=dict(width=0.5, color='lightgray'),
        marker=dict(size=10, symbol='arrow-bar-up', angleref='previous', color='lightgray'),
        hoverinfo='none')
    
    edge_trace_selected = go.Scatter(
        name='Selected Auger Transitions',
        legendrank=2,
        showlegend=len(edge_x_selected) > 0,
        x=edge_x_selected, y=edge_y_selected,
        mode='lines+markers',
        line=dict(width=0.5, color='red'),
        marker=dict(size=10, symbol='arrow-bar-up', angleref='previous', color='red'),
        hoverinfo='none')
    
    edge_trace_selected_cascade = go.Scatter(
        name='Selected Auger Cascade Transitions',
        legendrank=3,
        showlegend=len(edge_x_selected_cascade) > 0,
        x=edge_x_selected_cascade, y=edge_y_selected_cascade,
        mode='lines+markers',
        line=dict(width=0.5, color='green'),
        marker=dict(size=10, symbol='arrow-bar-up', angleref='previous', color='green'),
        hoverinfo='none')
    
    edge_trace_selected_cascade_dia = go.Scatter(
        name='Selected Diagram Cascade Transitions',
        legendrank=3,
        showlegend=len(edge_x_selected_cascade_dia) > 0,
        x=edge_x_selected_cascade_dia, y=edge_y_selected_cascade_dia,
        mode='lines+markers',
        line=dict(width=0.5, color='yellow'),
        marker=dict(size=10, symbol='arrow-bar-up', angleref='previous', color='yellow'),
        hoverinfo='none')
    
    line_hover_trace = go.Scatter(
        showlegend=False,
        x=line_hover_x, y=line_hover_y,
        mode='markers',
        marker=dict(opacity=[0 for _ in range(len(line_hover_x))]),
        hoverinfo='text',
        hoverlabel=dict(bgcolor='gray'),
        text=edge_text)
    
    line_hover_trace_dia = go.Scatter(
        showlegend=False,
        x=line_hover_x_dia, y=line_hover_y_dia,
        mode='markers',
        marker=dict(opacity=[0 for _ in range(len(line_hover_x_dia))]),
        hoverinfo='text',
        hoverlabel=dict(bgcolor='lightgray'),
        text=edge_text)
    
    line_hover_trace_selected = go.Scatter(
        showlegend=False,
        x=line_hover_x_selected, y=line_hover_y_selected,
        mode='markers',
        marker=dict(opacity=[0 for _ in range(len(line_hover_x_selected))]),
        hoverinfo='text',
        hoverlabel=dict(bgcolor='red'),
        text=edge_text_selected)
    
    line_hover_trace_selected_cascade = go.Scatter(
        showlegend=False,
        x=line_hover_x_selected_cascade, y=line_hover_y_selected_cascade,
        mode='markers',
        marker=dict(opacity=[0 for _ in range(len(line_hover_x_selected_cascade))]),
        hoverinfo='text',
        hoverlabel=dict(bgcolor='green'),
        text=edge_text_selected_cascade)
    
    line_hover_trace_selected_cascade_dia = go.Scatter(
        showlegend=False,
        x=line_hover_x_selected_cascade_dia, y=line_hover_y_selected_cascade_dia,
        mode='markers',
        marker=dict(opacity=[0 for _ in range(len(line_hover_x_selected_cascade_dia))]),
        hoverinfo='text',
        hoverlabel=dict(bgcolor='yellow'),
        text=edge_text_selected_cascade_dia)
    
    
    node_x = []
    node_y = []
    node_text = []
    
    node_x_dia = []
    node_y_dia = []
    node_text_dia = []
    
    for node in nodes:
        if 'dia' in node:
            node_x_append = node_x_dia
            node_y_append = node_y_dia
            node_text_append = node_text_dia
        else:
            node_x_append = node_x
            node_y_append = node_y
            node_text_append = node_text
        
        node_x_append.append(node['x'])
        node_y_append.append(node['y'])
        
        if 'cross' in node:
            node_text_append.append(str(node['label']) + \
                            "<br>State Energy: " + str(node['Energy']) + " eV" + \
                            "<br>Excitation Mechanism: " + str(node['type']) + \
                            "<br>Cross Section: " + str(node['cross']) + \
                            "<br>Beam: " + str(node['beam']) + " eV")
        else:
            node_text_append.append(node['label'] + \
                            "<br>State Energy: " + str(node['Energy']) + " eV") # type: ignore
    
    node_trace = go.Scatter(
        name='Auger Atomic States',
        legendrank=1,
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        text=node_text,
        marker=dict(
            showscale=False,
            colorscale='YlGnBu',
            reversescale=True,
            color='gray',
            size=10,
            line_width=2
        ))
    
    node_trace_dia = go.Scatter(
        name='Diagram Atomic States',
        legendrank=1,
        x=node_x_dia, y=node_y_dia,
        mode='markers',
        hoverinfo='text',
        text=node_text_dia,
        marker=dict(
            showscale=False,
            colorscale='YlGnBu',
            reversescale=True,
            color='lightgray',
            size=10,
            line_width=2
        ))
    
    data_full = [edge_trace, line_hover_trace, edge_trace_dia, line_hover_trace_dia]
    data_selected = [edge_trace_selected, line_hover_trace_selected]
    data_selected_cascade = [edge_trace_selected_cascade, line_hover_trace_selected_cascade]
    data_selected_cascade_dia = [edge_trace_selected_cascade_dia, line_hover_trace_selected_cascade_dia]
    
    data_list = data_full + data_selected + data_selected_cascade + data_selected_cascade_dia + \
                [node_trace, node_trace_dia]
    
    fig = go.Figure(data=data_list,
                    layout=go.Layout(
                        title='<br>Auger Levels Cascade',
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20,l=5,r=5,t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                    ))
    
    fig.update_yaxes(
        title_text = "Energy / eV (not to scale)",
        title_standoff = 25)
    
    fig.update_xaxes(
        title_text = "2J value",
        title_standoff = 25)
    
    fig.update_layout(showlegend=True)
    
    cascadeURL = saveMatrixHtml(fig, "augerCascade.html")

    
    webbrowser.open_new(cascadeURL)



# Initialize and configure the companion window with the simulations containing only transitions with non converged states and without them
def startConvergenceWindow(split: bool = True):
    radInitials, radFinals, radData,\
    satInitials, satFinals, satData = analyseConvergence()
    
    radUCV = np.zeros((len(radInitials), len(radFinals)))
    radLevelInfo = [["" for _ in radFinals] for _ in radInitials]
    
    for i, initial in enumerate(radInitials):
        for j, final in enumerate(radFinals):
            key = initial + "->" + final
            
            if key in radData:
                radUCV[i, j] = radData[key]["ucv"]
                radLevelInfo[i][j] = \
                "Rate: " + str(radData[key]["rate"]) + \
                "<br><br>Initial:" + \
                "<br>Overlap: " + radData[key]["initial"]["overlap"][0] + " " + str(radData[key]["initial"]["overlap"][1]) + \
                "<br>Percent: " + str(radData[key]["initial"]["percent"]) + \
                "<br>Accuracy: " + str(radData[key]["initial"]["accuracy"]) + \
                "<br>Energy Diff: " + str(radData[key]["initial"]["diff"]) + \
                "<br>UCV: " + str(radData[key]["initial"]["ucv"]) + \
                "<br><br>Final:" + \
                "<br>Overlap: " + radData[key]["final"]["overlap"][0] + " " + str(radData[key]["final"]["overlap"][1]) + \
                "<br>Percent: " + str(radData[key]["final"]["percent"]) + \
                "<br>Accuracy: " + str(radData[key]["final"]["accuracy"]) + \
                "<br>Energy Diff: " + str(radData[key]["final"]["diff"]) + \
                "<br>UCV: " + str(radData[key]["final"]["ucv"])
    
    
    satUCV = np.zeros((len(satInitials), len(satFinals)))
    satLevelInfo = [["" for _ in satFinals] for _ in satInitials]
    
    for i, initial in enumerate(satInitials):
        for j, final in enumerate(satFinals):
            key = initial + "->" + final
            
            if key in satData:
                satUCV[i, j] = satData[key]["ucv"]
                satLevelInfo[i][j] = \
                "Rate: " + str(satData[key]["rate"]) + \
                "<br><br>Initial:" + \
                "<br>Overlap: " + satData[key]["initial"]["overlap"][0] + " " + str(satData[key]["initial"]["overlap"][1]) + \
                "<br>Percent: " + str(satData[key]["initial"]["percent"]) + \
                "<br>Accuracy: " + str(satData[key]["initial"]["accuracy"]) + \
                "<br>Energy Diff: " + str(satData[key]["initial"]["diff"]) + \
                "<br>UCV: " + str(satData[key]["initial"]["ucv"]) + \
                "<br><br>Final:" + \
                "<br>Overlap: " + satData[key]["final"]["overlap"][0] + " " + str(satData[key]["final"]["overlap"][1]) + \
                "<br>Percent: " + str(satData[key]["final"]["percent"]) + \
                "<br>Accuracy: " + str(satData[key]["final"]["accuracy"]) + \
                "<br>Energy Diff: " + str(satData[key]["final"]["diff"]) + \
                "<br>UCV: " + str(satData[key]["final"]["ucv"])

    if split:
        zmax = np.max(radUCV)
    else:
        zmax = np.max([np.max(radUCV), np.max(satUCV)])
    
    fig_rad = go.Heatmap(z=radUCV,
                    #labels=dict(x="Final State", y="Initial State", color="Rate(s-1)"),
                    x=radFinals,
                    y=radInitials,
                    hovertemplate="Initial State: %{y}" + 
                              "<br>Final State: %{x}" + 
                              "<br>UCV: %{z}" + 
                              "<br>%{customdata}",
                    customdata = radLevelInfo,
                    zmin=0,
                    zmax=zmax
                    )
    
    if split:
        zmax = np.max(satUCV)
    
    fig_sat = go.Heatmap(z=satUCV,
                    #labels=dict(x="Final State", y="Initial State", color="Rate(s-1)"),
                    x=satFinals,
                    y=satInitials,
                    hovertemplate="Initial State: %{y}" + 
                              "<br>Final State: %{x}" + 
                              "<br>UCV: %{z}" + 
                              "<br>%{customdata}",
                    customdata = satLevelInfo,
                    zmin=0,
                    zmax=zmax
                    )
    
    radMatrixURL = ""
    radMatrixLogURL = ""
    satMatrixURL = ""
    satMatrixLogURL = ""
    matricesURL = ""
    matricesLogURL = ""

    
    if split:
        fig = make_subplots(rows=1, cols=1, subplot_titles=["Radiative UCV Matrix"])
        
        fig.append_trace(fig_rad, row=1, col=1)

        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)

        radMatrixURL = saveMatrixHtml(fig, "ucvRadMatrix.html")
        
        
        fig = make_subplots(rows=1, cols=1, subplot_titles=["Satellite UCV Matrix"])
        
        fig.append_trace(fig_sat, row=1, col=1)

        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)

        satMatrixURL = saveMatrixHtml(fig, "ucvSatMatrix.html")
    else:
        fig = make_subplots(rows=1, cols=2,
                            subplot_titles=[
                                "Radiative UCV Matrix", 
                                "Satellite UCV Matrix"
                                ],
                            )
        
        fig.append_trace(fig_rad, row=1, col=1)
        fig.append_trace(fig_sat, row=2, col=1)
        
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        
        #fig.update_layout(yaxis = dict(scaleanchor = 'x'),
        #                  yaxis2 = dict(scaleanchor = 'x2'),
        #                  yaxis3 = dict(scaleanchor = 'x3'))
        
        
        matricesURL = saveMatrixHtml(fig, "ucvMatrices.html")
    
    radDataLog = np.log10(radUCV)
    satDataLog = np.log10(satUCV)
    
    if split:
        zmin = np.min(radDataLog[radDataLog != -np.inf])
    else:
        zmin = min([np.min(radDataLog[radDataLog != -np.inf]), np.min(satDataLog[satDataLog != -np.inf])])
    
    fig_rad = go.Heatmap(z=radDataLog,
                    #labels=dict(x="Final State", y="Initial State", color="Rate(s-1)"),
                    x=radFinals,
                    y=radInitials,
                    hovertemplate="Initial State: %{y}" + 
                              "<br>Final State: %{x}" + 
                              "<br>UCV: %{text}" + 
                              "<br>%{customdata}",
                    customdata = radLevelInfo,
                    text=radUCV,
                    zmin=zmin,
                    zmax=np.log10(zmax)
                    )
    
    if split:
        zmin = np.min(satDataLog[satDataLog != -np.inf])
    
    fig_sat = go.Heatmap(z=satDataLog,
                    #labels=dict(x="Final State", y="Initial State", color="Rate(s-1)"),
                    x=satFinals,
                    y=satInitials,
                    hovertemplate="Initial State: %{y}" + 
                              "<br>Final State: %{x}" + 
                              "<br>UCV: %{text}" + 
                              "<br>%{customdata}",
                    customdata = satLevelInfo,
                    text=satUCV,
                    zmin=zmin,
                    zmax=np.log10(zmax)
                    )
    
    
    if split:
        fig = make_subplots(rows=1, cols=1, subplot_titles=["Radiative UCV Matrix"])
        
        fig.append_trace(fig_rad, row=1, col=1)

        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)

        radMatrixLogURL = saveMatrixHtml(fig, "ucvRadMatrixLog.html")
        
        
        fig = make_subplots(rows=1, cols=1, subplot_titles=["Satellite UCV Matrix"])
        
        fig.append_trace(fig_sat, row=1, col=1)

        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)

        satMatrixLogURL = saveMatrixHtml(fig, "ucvSatMatrixLog.html")
    else:
        fig = make_subplots(rows=1, cols=2,
                        subplot_titles=[
                            "Radiative UCV Matrix", 
                            "Satellite UCV Matrix"
                            ],
                        )

        fig.append_trace(fig_rad, row=1, col=1)
        fig.append_trace(fig_sat, row=2, col=1)
        
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        
        #fig.update_layout(yaxis = dict(scaleanchor = 'x'),
        #                  yaxis2 = dict(scaleanchor = 'x2'),
        #                  yaxis3 = dict(scaleanchor = 'x3'))
        
        
        matricesLogURL = saveMatrixHtml(fig, "ucvMatricesLog.html")
    
    
    if split:
        webbrowser.open_new(radMatrixURL)
        webbrowser.open_new_tab(radMatrixLogURL)
        webbrowser.open_new(satMatrixURL)
        webbrowser.open_new_tab(satMatrixLogURL)
    else:
        webbrowser.open_new(matricesURL)
        webbrowser.open_new_tab(matricesLogURL)


def configure_shake_params():
    shakePars = Toplevel(guiVars._parent)
    shakePars.title("Configure Shake Probability Fitting Parameters")
    shakePars.grab_set()  # Make this window the only interactable one until its closed

    shakePars.geometry("700x400")
    
    # Input check for the percentage number in the entry
    import re
    def check_num(newval):
        """
        Function to input check for the percentage number in the entry
            
            Args:
                newval: the value trying to be introduced
            
            Returns:
                regex match to check if the new value is a numeric percentage format
        """
        return re.match('^(?:[0-9]*[.]?[0-9]*)$', newval) is not None
    # Bind the function
    check_num_wrapper = (shakePars.register(check_num), '%P')
    """
    Function wrapper to bind this validate command
    """

    shakes.setupShake()

    totalShakeLabel = Label(shakePars, text="Maximum Total Shake (approximate): ")
    totalShakeEntry = Entry(shakePars, validate='key', validatecommand=check_num_wrapper)
    
    shakeOffLabels: List[Label] = []
    shakeOffFlags = []
    shakeOffChecks: List[Checkbutton] = []
    
    for key in shakes.existing_shakeoffs:
        shakeOffLabels.append(Label(shakePars, text="Fit " + key + " Shake Off: "))
        shakeOffFlags.append(BooleanVar(shakePars))
        shakeOffChecks.append(Checkbutton(shakePars, variable=shakeOffFlags[-1]))
    
    shakeUpLabels: List[Label] = []
    shakeUpFlags = []
    shakeUpChecks: List[Checkbutton] = []
    for key in shakes.existing_shakeups:
        shakeUpLabels.append(Label(shakePars, text="Fit " + key + " Shake Up: "))
        shakeUpFlags.append(BooleanVar(shakePars))
        shakeUpChecks.append(Checkbutton(shakePars, variable=shakeUpFlags[-1]))
    
    def applyFunction():
        setMaxTotalShake(float(totalShakeEntry.get()))
        
        generalVars.shakes_to_fit = []
        for label, shake in zip(shakeOffLabels, shakeOffFlags):
            if shake.get():
                generalVars.shakes_to_fit.append(label.cget("text"))
        for label, shake in zip(shakeUpLabels, shakeUpFlags):
            if shake.get():
                generalVars.shakes_to_fit.append(label.cget("text"))
    
    applyButton = Button(shakePars, text="Apply", command=lambda: applyFunction())
    
    
    totalShakeLabel.grid(column=0, row=0, sticky="WE")
    totalShakeEntry.grid(column=1, row=0, sticky="WE")
    
    for i, (label, check) in enumerate(zip(shakeOffLabels, shakeOffChecks)):
        label.grid(column=0, row=i + 1, sticky="WE")
        check.grid(column=1, row=i + 1, sticky="WE")
    
    for i, (label, check) in enumerate(zip(shakeUpLabels, shakeUpChecks)):
        label.grid(column=2, row=i + 1, sticky="WE")
        check.grid(column=3, row=i + 1, sticky="WE")

    
    applyButton.grid(column=3, row=max(len(shakeOffLabels), len(shakeUpLabels)) + 1, sticky="WE")

# Initialize and configure the extra fitting options interface
def fitOptionsWindow():
    """
    Function to initialize and configure the extra fitting options where we can add possible missing contributions
    """
    extraFit = Toplevel(guiVars._parent)
    extraFit.title("Additional Fitting Options")
    extraFit.grab_set()  # Make this window the only interactable one until its closed

    extraFit.geometry("700x400")
    
    functionsLabel = Label(extraFit, text="Available functions:")
    
    functionsDropdown = ttk.Combobox(extraFit)
    functionsDropdown['values'] = ('Gaussian', 'Lorentzian', 'Voigt')
    functionsDropdown['state'] = 'readonly'
    
    noteLabel = Label(extraFit, text='Component Name: ')
    noteEntry = Entry(extraFit)
    
    parLabel = Label(extraFit, text='Parameter')
    parValLabel = Label(extraFit, text='Value')
    parMinLabel = Label(extraFit, text='Minimum')
    parMaxLabel = Label(extraFit, text='Maximum')
    
    # Input check for the percentage number in the entry
    import re
    def check_num(newval):
        """
        Function to input check for the percentage number in the entry
            
            Args:
                newval: the value trying to be introduced
            
            Returns:
                regex match to check if the new value is a numeric percentage format
        """
        return re.match('^(?:[0-9]*[.]?[0-9]*)$', newval) is not None
    # Bind the function
    check_num_wrapper = (extraFit.register(check_num), '%P')
    """
    Function wrapper to bind this validate command
    """

    
    xParLabel = Label(extraFit, text='X offset: ')
    xParValEntry = Entry(extraFit, validate='key', validatecommand=check_num_wrapper)
    xParMinEntry = Entry(extraFit, validate='key', validatecommand=check_num_wrapper)
    xParMaxEntry = Entry(extraFit, validate='key', validatecommand=check_num_wrapper)
    
    ampParLabel = Label(extraFit, text='Amplitude: ')
    ampParValEntry = Entry(extraFit, validate='key', validatecommand=check_num_wrapper)
    ampParMinEntry = Entry(extraFit, validate='key', validatecommand=check_num_wrapper)
    ampParMaxEntry = Entry(extraFit, validate='key', validatecommand=check_num_wrapper)
    ampParLabelNote = Label(extraFit, text='(multiplier to the simulated intensity)')
    
    GwidthParLabel = Label(extraFit, text='Gaussian FWHM: ')
    GwidthParValEntry = Entry(extraFit, validate='key', validatecommand=check_num_wrapper)
    GwidthParMinEntry = Entry(extraFit, validate='key', validatecommand=check_num_wrapper)
    GwidthParMaxEntry = Entry(extraFit, validate='key', validatecommand=check_num_wrapper)
    
    # Toggle the gaussian width entries to tie them to the experimental resolution parameter
    def disableGwidthEntries():
        res = guiVars.exp_resolution.get() # type: ignore
        maxWidth = res * 4
        minWidth = 0.01
        
        GwidthParValEntry.delete(0, END)
        GwidthParValEntry.insert(0, str(res))
        GwidthParMaxEntry.delete(0, END)
        GwidthParMaxEntry.insert(0, str(maxWidth))
        GwidthParMinEntry.delete(0, END)
        GwidthParMinEntry.insert(0, str(minWidth))
        
        GwidthParLabel['state'] = 'normal' if GwidthParLabel['state'] == 'disabled' else 'disabled'
        GwidthParValEntry['state'] = 'normal' if GwidthParValEntry['state'] == 'disabled' else 'disabled'
        GwidthParMinEntry['state'] = 'normal' if GwidthParMinEntry['state'] == 'disabled' else 'disabled'
        GwidthParMaxEntry['state'] = 'normal' if GwidthParMaxEntry['state'] == 'disabled' else 'disabled'
    
    GwidthParResLabel = Label(extraFit, text='Link to Resolution')
    GwidthParResVar = BooleanVar(extraFit)
    GwidthParResCheck = Checkbutton(extraFit, variable=GwidthParResVar, command=lambda: disableGwidthEntries())
    
    LwidthParLabel = Label(extraFit, text='Lorentzian FWHM: ')
    LwidthParValEntry = Entry(extraFit, validate='key', validatecommand=check_num_wrapper)
    LwidthParMinEntry = Entry(extraFit, validate='key', validatecommand=check_num_wrapper)
    LwidthParMaxEntry = Entry(extraFit, validate='key', validatecommand=check_num_wrapper)
    
    # Toggle the lorentzian width entries to tie them to the experimental resolution parameter
    def disableLwidthEntries():
        res = guiVars.exp_resolution.get() # type: ignore
        maxWidth = res * 4
        minWidth = 0.01
        
        LwidthParValEntry.delete(0, END)
        LwidthParValEntry.insert(0, str(res))
        LwidthParMaxEntry.delete(0, END)
        LwidthParMaxEntry.insert(0, str(maxWidth))
        LwidthParMinEntry.delete(0, END)
        LwidthParMinEntry.insert(0, str(minWidth))
        
        LwidthParLabel['state'] = 'normal' if LwidthParLabel['state'] == 'disabled' else 'disabled'
        LwidthParValEntry['state'] = 'normal' if LwidthParValEntry['state'] == 'disabled' else 'disabled'
        LwidthParMinEntry['state'] = 'normal' if LwidthParMinEntry['state'] == 'disabled' else 'disabled'
        LwidthParMaxEntry['state'] = 'normal' if LwidthParMaxEntry['state'] == 'disabled' else 'disabled'
    
    LwidthParResLabel = Label(extraFit, text='Link to Resolution')
    LwidthParResVar = BooleanVar(extraFit)
    LwidthParResCheck = Checkbutton(extraFit, variable=LwidthParResVar, command=lambda: disableLwidthEntries())
    
    
    # Update the entry boxes for each function in the interface
    def updateFunctionEntries(event):
        """Function to update the interface entries and labels depending on the selected function

        Args:
            event: tkinter event
        """
        function = functionsDropdown.get()
        
        if function == 'Gaussian':
            GwidthParLabel.grid(column=0, row=5, padx=5, sticky="WE")
            GwidthParValEntry.grid(column=1, row=5, padx=5, sticky="WE")
            GwidthParMinEntry.grid(column=2, row=5, padx=5, sticky="WE")
            GwidthParMaxEntry.grid(column=3, row=5, padx=5, sticky="WE")
            GwidthParResLabel.grid(column=4, row=5, padx=5, sticky="WE")
            GwidthParResCheck.grid(column=5, row=5, padx=5, sticky="WE")
            LwidthParLabel.grid_forget()
            LwidthParValEntry.grid_forget()
            LwidthParMinEntry.grid_forget()
            LwidthParMaxEntry.grid_forget()
            LwidthParResLabel.grid_forget()
            LwidthParResCheck.grid_forget()
        elif function == 'Lorentzian':
            LwidthParLabel.grid(column=0, row=6, padx=5, sticky="WE")
            LwidthParValEntry.grid(column=1, row=6, padx=5, sticky="WE")
            LwidthParMinEntry.grid(column=2, row=6, padx=5, sticky="WE")
            LwidthParMaxEntry.grid(column=3, row=6, padx=5, sticky="WE")
            LwidthParResLabel.grid(column=4, row=6, padx=5, sticky="WE")
            LwidthParResCheck.grid(column=5, row=6, padx=5, sticky="WE")
            GwidthParLabel.grid_forget()
            GwidthParValEntry.grid_forget()
            GwidthParMinEntry.grid_forget()
            GwidthParMaxEntry.grid_forget()
            GwidthParResLabel.grid_forget()
            GwidthParResCheck.grid_forget()
        elif function == 'Voigt':
            GwidthParLabel.grid(column=0, row=5, padx=5, sticky="WE")
            GwidthParValEntry.grid(column=1, row=5, padx=5, sticky="WE")
            GwidthParMinEntry.grid(column=2, row=5, padx=5, sticky="WE")
            GwidthParMaxEntry.grid(column=3, row=5, padx=5, sticky="WE")
            GwidthParResLabel.grid(column=4, row=5, padx=5, sticky="WE")
            GwidthParResCheck.grid(column=5, row=5, padx=5, sticky="WE")
            LwidthParLabel.grid(column=0, row=6, padx=5, sticky="WE")
            LwidthParValEntry.grid(column=1, row=6, padx=5, sticky="WE")
            LwidthParMinEntry.grid(column=2, row=6, padx=5, sticky="WE")
            LwidthParMaxEntry.grid(column=3, row=6, padx=5, sticky="WE")
            LwidthParResCheck.deselect()
            
            LwidthParLabel['state'] = 'normal'
            LwidthParValEntry['state'] = 'normal'
            LwidthParMinEntry['state'] = 'normal'
            LwidthParMaxEntry['state'] = 'normal'

            LwidthParResLabel.grid_forget()
            LwidthParResCheck.grid_forget()
    
    functionsDropdown.bind("<<ComboboxSelected>>", updateFunctionEntries)
    functionsDropdown.set('Gaussian')
    
    boxTitle = Label(extraFit, text="Currently active additional fitting components:")
    extraFunctionsBox = Listbox(extraFit)
    
    # Load the selected functions parameters into the entries
    def loadParameters(event):
        """Function to load the selected function's parameters into the entries.
            This is used to easily be able to edit a selected function

        Args:
            event: tkinter event
        """
        try:
            selected = extraFunctionsBox.get(extraFunctionsBox.curselection()[0])
        except IndexError:
            print("Error finding selected function.")
            return
        
        note, function = selected.split(": ")[0].split(", ")
        note = note.strip()
        function = function.strip()
        
        noteEntry.delete(0, END)
        noteEntry.insert(0, note)
        functionsDropdown.set(function)
        updateFunctionEntries(None)
        
        parameters = selected.split(": ")[1]
        xPar = parameters.split("xPar(")[1].split(")")[0]
        xParVal = xPar.split(" < ")[1]
        xParMin = xPar.split(" < ")[0]
        xParMax = xPar.split(" < ")[2]
        
        ampPar = parameters.split("ampPar(")[1].split(")")[0]
        ampParVal = ampPar.split(" < ")[1]
        ampParMin = ampPar.split(" < ")[0]
        ampParMax = ampPar.split(" < ")[2]
        
        xParValEntry.delete(0, END)
        xParValEntry.insert(0, xParVal)
        xParMinEntry.delete(0, END)
        xParMinEntry.insert(0, xParMin)
        xParMaxEntry.delete(0, END)
        xParMaxEntry.insert(0, xParMax)
        
        ampParValEntry.delete(0, END)
        ampParValEntry.insert(0, ampParVal)
        ampParMinEntry.delete(0, END)
        ampParMinEntry.insert(0, ampParMin)
        ampParMaxEntry.delete(0, END)
        ampParMaxEntry.insert(0, ampParMax)
        
        if function == 'Gaussian':
            GwidthPar = parameters.split("GwidthPar(")[1].split(")")[0]
            GwidthParVal = GwidthPar.split(" < ")[1]
            GwidthParMin = GwidthPar.split(" < ")[0]
            GwidthParMax = GwidthPar.split(" < ")[2]
            
            GwidthParValEntry.delete(0, END)
            GwidthParValEntry.insert(0, GwidthParVal)
            GwidthParMinEntry.delete(0, END)
            GwidthParMinEntry.insert(0, GwidthParMin)
            GwidthParMaxEntry.delete(0, END)
            GwidthParMaxEntry.insert(0, GwidthParMax)
            if parameters.split("GwidthPar(")[1].split(")")[1][0] == '*':
                GwidthParResCheck.select()
                disableGwidthEntries()
            else:
                GwidthParResCheck.deselect()
                GwidthParLabel['state'] = 'normal'
                GwidthParValEntry['state'] = 'normal'
                GwidthParMinEntry['state'] = 'normal'
                GwidthParMaxEntry['state'] = 'normal'
        elif function == 'Lorentzian':
            LwidthPar = parameters.split("LwidthPar(")[1].split(")")[0]
            LwidthParVal = LwidthPar.split(" < ")[1]
            LwidthParMin = LwidthPar.split(" < ")[0]
            LwidthParMax = LwidthPar.split(" < ")[2]
            
            LwidthParValEntry.delete(0, END)
            LwidthParValEntry.insert(0, LwidthParVal)
            LwidthParMinEntry.delete(0, END)
            LwidthParMinEntry.insert(0, LwidthParMin)
            LwidthParMaxEntry.delete(0, END)
            LwidthParMaxEntry.insert(0, LwidthParMax)
            if parameters.split("LwidthPar(")[1].split(")")[1][0] == '*':
                LwidthParResCheck.select()
                disableLwidthEntries()
            else:
                LwidthParResCheck.deselect()
                LwidthParLabel['state'] = 'normal'
                LwidthParValEntry['state'] = 'normal'
                LwidthParMinEntry['state'] = 'normal'
                LwidthParMaxEntry['state'] = 'normal'
        elif function == 'Voigt':
            GwidthPar = parameters.split("GwidthPar(")[1].split(")")[0]
            GwidthParVal = GwidthPar.split(" < ")[1]
            GwidthParMin = GwidthPar.split(" < ")[0]
            GwidthParMax = GwidthPar.split(" < ")[2]
            LwidthPar = parameters.split("LwidthPar(")[1].split(")")[0]
            LwidthParVal = LwidthPar.split(" < ")[1]
            LwidthParMin = LwidthPar.split(" < ")[0]
            LwidthParMax = LwidthPar.split(" < ")[2]
            
            GwidthParValEntry.delete(0, END)
            GwidthParValEntry.insert(0, GwidthParVal)
            GwidthParMinEntry.delete(0, END)
            GwidthParMinEntry.insert(0, GwidthParMin)
            GwidthParMaxEntry.delete(0, END)
            GwidthParMaxEntry.insert(0, GwidthParMax)
            if parameters.split("GwidthPar(")[1].split(")")[1][0] == '*':
                GwidthParResCheck.select()
                disableGwidthEntries()
            else:
                GwidthParResCheck.deselect()
                GwidthParLabel['state'] = 'normal'
                GwidthParValEntry['state'] = 'normal'
                GwidthParMinEntry['state'] = 'normal'
                GwidthParMaxEntry['state'] = 'normal'
            
            LwidthParValEntry.delete(0, END)
            LwidthParValEntry.insert(0, LwidthParVal)
            LwidthParMinEntry.delete(0, END)
            LwidthParMinEntry.insert(0, LwidthParMin)
            LwidthParMaxEntry.delete(0, END)
            LwidthParMaxEntry.insert(0, LwidthParMax)
    
    extraFunctionsBox.bind("<<ListboxSelect>>", loadParameters)
    
    # Add the configured function to the listbox
    def addFunction():
        """Function to add a configured component to the listbox of components to fit.
            Executed when the "Add" button is clicked
        """
        function = functionsDropdown.get()
        
        xParText = f'xPar({xParMinEntry.get()} < {xParValEntry.get()} < {xParMaxEntry.get()})'
        ampParText = f'ampPar({ampParMinEntry.get()} < {ampParValEntry.get()} < {ampParMaxEntry.get()})'
        
        if function == 'Gaussian':
            if float(xParMinEntry.get()) <= float(xParValEntry.get()) <= float(xParMaxEntry.get()) and \
            float(ampParMinEntry.get()) <= float(ampParValEntry.get()) <= float(ampParMaxEntry.get()) and \
            float(GwidthParMinEntry.get()) <= float(GwidthParValEntry.get()) <= float(GwidthParMaxEntry.get()):
                GwidthParText = f'GwidthPar({GwidthParMinEntry.get()} < {GwidthParValEntry.get()} < {GwidthParMaxEntry.get()}){"*" if GwidthParResVar.get() else " "}'
                extraFunctionsBox.insert(END, f'{noteEntry.get(): <10}, {function: <20}:{xParText: >30}{ampParText: >30}{GwidthParText: >30}')
            else:
                errorPars = "xPar" if float(xParMinEntry.get()) <= float(xParValEntry.get()) <= float(xParMaxEntry.get()) else ""
                errorPars += " ampPar" if float(ampParMinEntry.get()) <= float(ampParValEntry.get()) <= float(ampParMaxEntry.get()) else ""
                errorPars += " GwidthPar" if float(GwidthParMinEntry.get()) <= float(GwidthParValEntry.get()) <= float(GwidthParMaxEntry.get()) else ""
                messagebox.showerror("Invalid Parameters", message="The function could not be added due to the chosen values for the following parameters: " + errorPars.strip())
        elif function == 'Lorentzian':
            if float(xParMinEntry.get()) <= float(xParValEntry.get()) <= float(xParMaxEntry.get()) and \
            float(ampParMinEntry.get()) <= float(ampParValEntry.get()) <= float(ampParMaxEntry.get()) and \
            float(LwidthParMinEntry.get()) <= float(LwidthParValEntry.get()) <= float(LwidthParMaxEntry.get()):
                LwidthParText = f'LwidthPar({LwidthParMinEntry.get()} < {LwidthParValEntry.get()} < {LwidthParMaxEntry.get()}){"*" if LwidthParResVar.get() else " "}'
                extraFunctionsBox.insert(END, f'{noteEntry.get(): <10}, {function: <20}:{xParText: >30}{ampParText: >30}{LwidthParText: >30}')
            else:
                errorPars = "xPar" if float(xParMinEntry.get()) <= float(xParValEntry.get()) <= float(xParMaxEntry.get()) else ""
                errorPars += " ampPar" if float(ampParMinEntry.get()) <= float(ampParValEntry.get()) <= float(ampParMaxEntry.get()) else ""
                errorPars += " LwidthPar" if float(LwidthParMinEntry.get()) <= float(LwidthParValEntry.get()) <= float(LwidthParMaxEntry.get()) else ""
                messagebox.showerror("Invalid Parameters", message="The function could not be added due to the chosen values for the following parameters: " + errorPars.strip())
        elif function == 'Voigt':
            if float(xParMinEntry.get()) <= float(xParValEntry.get()) <= float(xParMaxEntry.get()) and \
            float(ampParMinEntry.get()) <= float(ampParValEntry.get()) <= float(ampParMaxEntry.get()) and \
            float(GwidthParMinEntry.get()) <= float(GwidthParValEntry.get()) <= float(GwidthParMaxEntry.get()) and \
            float(LwidthParMinEntry.get()) <= float(LwidthParValEntry.get()) <= float(LwidthParMaxEntry.get()):
                GwidthParText = f'GwidthPar({GwidthParMinEntry.get()} < {GwidthParValEntry.get()} < {GwidthParMaxEntry.get()}){"*" if GwidthParResVar.get() else " "}'
                LwidthParText = f'LwidthPar({LwidthParMinEntry.get()} < {LwidthParValEntry.get()} < {LwidthParMaxEntry.get()})'
                extraFunctionsBox.insert(END, f'{noteEntry.get(): <10}, {function: <20}:{xParText: >30}{ampParText: >30}{GwidthParText: >30}{LwidthParText: >30}')
            else:
                errorPars = "xPar" if float(xParMinEntry.get()) <= float(xParValEntry.get()) <= float(xParMaxEntry.get()) else ""
                errorPars += " ampPar" if float(ampParMinEntry.get()) <= float(ampParValEntry.get()) <= float(ampParMaxEntry.get()) else ""
                errorPars += " GwidthPar" if float(GwidthParMinEntry.get()) <= float(GwidthParValEntry.get()) <= float(GwidthParMaxEntry.get()) else ""
                errorPars += " LwidthPar" if float(LwidthParMinEntry.get()) <= float(LwidthParValEntry.get()) <= float(LwidthParMaxEntry.get()) else ""
                messagebox.showerror("Invalid Parameters", message="The function could not be added due to the chosen values for the following parameters: " + errorPars.strip())
    # Remove the selected function from the listbox
    def removeFunction():
        """Function to remove the selected components from the listbox of components to fit.
            Executed when the "Remove" button is clicked
        """
        selection = list(extraFunctionsBox.curselection())
        selection.sort()
        for i, index in enumerate(selection):
            extraFunctionsBox.delete(index - i)
    # Update the selected function in the listbox with the entry values
    def updateFunction():
        """Function to update the selected component in the listbox of components to fit.
            Executed when the "Update" button is clicked
        """
        selected = extraFunctionsBox.curselection()[0]
        
        function = functionsDropdown.get()
        
        xParText = f'xPar({xParMinEntry.get()} < {xParValEntry.get()} < {xParMaxEntry.get()})'
        ampParText = f'ampPar({ampParMinEntry.get()} < {ampParValEntry.get()} < {ampParMaxEntry.get()})'
        
        if function == 'Gaussian':
            if float(xParMinEntry.get()) <= float(xParValEntry.get()) <= float(xParMaxEntry.get()) and \
            float(ampParMinEntry.get()) <= float(ampParValEntry.get()) <= float(ampParMaxEntry.get()) and \
            float(GwidthParMinEntry.get()) <= float(GwidthParValEntry.get()) <= float(GwidthParMaxEntry.get()):
                extraFunctionsBox.delete(selected)
                GwidthParText = f'GwidthPar({GwidthParMinEntry.get()} < {GwidthParValEntry.get()} < {GwidthParMaxEntry.get()}){"*" if GwidthParResVar.get() else " "}'
                extraFunctionsBox.insert(selected, f'{noteEntry.get(): <10}, {function: <20}: {xParText: >30} {ampParText: >30} {GwidthParText: >30}')
            else:
                errorPars = "xPar" if float(xParMinEntry.get()) <= float(xParValEntry.get()) <= float(xParMaxEntry.get()) else ""
                errorPars += " ampPar" if float(ampParMinEntry.get()) <= float(ampParValEntry.get()) <= float(ampParMaxEntry.get()) else ""
                errorPars += " GwidthPar" if float(GwidthParMinEntry.get()) <= float(GwidthParValEntry.get()) <= float(GwidthParMaxEntry.get()) else ""
                messagebox.showerror("Invalid Parameters", message="The function could not be added due to the chosen values for the following parameters: " + errorPars.strip())
        elif function == 'Lorentzian':
            if float(xParMinEntry.get()) <= float(xParValEntry.get()) <= float(xParMaxEntry.get()) and \
            float(ampParMinEntry.get()) <= float(ampParValEntry.get()) <= float(ampParMaxEntry.get()) and \
            float(LwidthParMinEntry.get()) <= float(LwidthParValEntry.get()) <= float(LwidthParMaxEntry.get()):
                extraFunctionsBox.delete(selected)
                LwidthParText = f'LwidthPar({LwidthParMinEntry.get()} < {LwidthParValEntry.get()} < {LwidthParMaxEntry.get()}){"*" if LwidthParResVar.get() else " "}'
                extraFunctionsBox.insert(selected, f'{noteEntry.get(): <10}, {function: <20}: {xParText: >30} {ampParText: >30} {LwidthParText: >30}')
            else:
                errorPars = "xPar" if float(xParMinEntry.get()) <= float(xParValEntry.get()) <= float(xParMaxEntry.get()) else ""
                errorPars += " ampPar" if float(ampParMinEntry.get()) <= float(ampParValEntry.get()) <= float(ampParMaxEntry.get()) else ""
                errorPars += " LwidthPar" if float(LwidthParMinEntry.get()) <= float(LwidthParValEntry.get()) <= float(LwidthParMaxEntry.get()) else ""
                messagebox.showerror("Invalid Parameters", message="The function could not be added due to the chosen values for the following parameters: " + errorPars.strip())
        elif function == 'Voigt':
            if float(xParMinEntry.get()) <= float(xParValEntry.get()) <= float(xParMaxEntry.get()) and \
            float(ampParMinEntry.get()) <= float(ampParValEntry.get()) <= float(ampParMaxEntry.get()) and \
            float(GwidthParMinEntry.get()) <= float(GwidthParValEntry.get()) <= float(GwidthParMaxEntry.get()) and \
            float(LwidthParMinEntry.get()) <= float(LwidthParValEntry.get()) <= float(LwidthParMaxEntry.get()):
                extraFunctionsBox.delete(selected)
                GwidthParText = f'GwidthPar({GwidthParMinEntry.get()} < {GwidthParValEntry.get()} < {GwidthParMaxEntry.get()}){"*" if GwidthParResVar.get() else " "}'
                LwidthParText = f'LwidthPar({LwidthParMinEntry.get()} < {LwidthParValEntry.get()} < {LwidthParMaxEntry.get()})'
                extraFunctionsBox.insert(selected, f'{noteEntry.get(): <10}, {function: <20}: {xParText: >30} {ampParText: >30} {GwidthParText: >30} {LwidthParText: >30}')
            else:
                errorPars = "xPar" if float(xParMinEntry.get()) <= float(xParValEntry.get()) <= float(xParMaxEntry.get()) else ""
                errorPars += " ampPar" if float(ampParMinEntry.get()) <= float(ampParValEntry.get()) <= float(ampParMaxEntry.get()) else ""
                errorPars += " GwidthPar" if float(GwidthParMinEntry.get()) <= float(GwidthParValEntry.get()) <= float(GwidthParMaxEntry.get()) else ""
                errorPars += " LwidthPar" if float(LwidthParMinEntry.get()) <= float(LwidthParValEntry.get()) <= float(LwidthParMaxEntry.get()) else ""
                messagebox.showerror("Invalid Parameters", message="The function could not be added due to the chosen values for the following parameters: " + errorPars.strip())
    # Save the listbox contents to a dictionary to be used in the fitting algorithm
    def applyFunction():
        """Function to save the components in the listbox of components to fit into a dictionary.
            Executed when the "Apply" button is clicked
        """
        items = extraFunctionsBox.get(0, END)
        
        # Clean previous functions
        generalVars.extra_fitting_functions = {}
        
        existing_cnt = {}
        
        for item in items:
            note, function = item.split(":")[0].split(", ")
            note = note.strip()
            function = function.strip()
            pars = item.split(":")[1]
            
            xPar = pars.split("xPar(")[1].split(")")[0]
            xParVal = xPar.split(" < ")[1]
            xParMin = xPar.split(" < ")[0]
            xParMax = xPar.split(" < ")[2]
            
            ampPar = pars.split("ampPar(")[1].split(")")[0]
            ampParVal = ampPar.split(" < ")[1]
            ampParMin = ampPar.split(" < ")[0]
            ampParMax = ampPar.split(" < ")[2]
            
            GwidthParVal = ''
            GwidthParMin = ''
            GwidthParMax = ''
            GwidthParRes = ''
            
            LwidthParVal = ''
            LwidthParMin = ''
            LwidthParMax = ''
            LwidthParRes = ''
            
            if function == 'Gaussian':
                GwidthPar = pars.split("GwidthPar(")[1].split(")")[0]
                GwidthParVal = GwidthPar.split(" < ")[1]
                GwidthParMin = GwidthPar.split(" < ")[0]
                GwidthParMax = GwidthPar.split(" < ")[2]
                GwidthParRes = 1.0 if pars.split("GwidthPar(")[1].split(")")[1][0] == '*' else 0.0
            elif function == 'Lorentzian':
                LwidthPar = pars.split("LwidthPar(")[1].split(")")[0]
                LwidthParVal = LwidthPar.split(" < ")[1]
                LwidthParMin = LwidthPar.split(" < ")[0]
                LwidthParMax = LwidthPar.split(" < ")[2]
                LwidthParRes = 1.0 if pars.split("LwidthPar(")[1].split(")")[1][0] == '*' else 0.0
            elif function == 'Voigt':
                GwidthPar = pars.split("GwidthPar(")[1].split(")")[0]
                GwidthParVal = GwidthPar.split(" < ")[1]
                GwidthParMin = GwidthPar.split(" < ")[0]
                GwidthParMax = GwidthPar.split(" < ")[2]
                GwidthParRes = 1.0 if pars.split("GwidthPar(")[1].split(")")[1][0] == '*' else 0.0
                LwidthPar = pars.split("LwidthPar(")[1].split(")")[0]
                LwidthParVal = LwidthPar.split(" < ")[1]
                LwidthParMin = LwidthPar.split(" < ")[0]
                LwidthParMax = LwidthPar.split(" < ")[2]
            
            if note + "_" + function not in generalVars.extra_fitting_functions:
                existing_cnt[note + "_" + function] = 1
                if function == 'Gaussian':
                    generalVars.extra_fitting_functions[note + "_" + function] = {
                        'xParVal': float(xParVal),
                        'xParMin': float(xParMin),
                        'xParMax': float(xParMax),
                        
                        'ampParVal': float(ampParVal),
                        'ampParMin': float(ampParMin),
                        'ampParMax': float(ampParMax),
                        
                        'GwidthParVal': float(GwidthParVal),
                        'GwidthParMin': float(GwidthParMin),
                        'GwidthParMax': float(GwidthParMax),
                        
                        'widthRes': float(GwidthParRes)
                    }
                elif function == 'Lorentzian':
                    generalVars.extra_fitting_functions[note + "_" + function] = {
                        'xParVal': float(xParVal),
                        'xParMin': float(xParMin),
                        'xParMax': float(xParMax),
                        
                        'ampParVal': float(ampParVal),
                        'ampParMin': float(ampParMin),
                        'ampParMax': float(ampParMax),
                        
                        'LwidthParVal': float(LwidthParVal),
                        'LwidthParMin': float(LwidthParMin),
                        'LwidthParMax': float(LwidthParMax),
                        
                        'widthRes': float(LwidthParRes)
                    }
                elif function == 'Voigt':
                    generalVars.extra_fitting_functions[note + "_" + function] = {
                        'xParVal': float(xParVal),
                        'xParMin': float(xParMin),
                        'xParMax': float(xParMax),
                        
                        'ampParVal': float(ampParVal),
                        'ampParMin': float(ampParMin),
                        'ampParMax': float(ampParMax),
                        
                        'GwidthParVal': float(GwidthParVal),
                        'GwidthParMin': float(GwidthParMin),
                        'GwidthParMax': float(GwidthParMax),
                        
                        'widthRes': float(GwidthParRes),
                        
                        'LwidthParVal': float(LwidthParVal),
                        'LwidthParMin': float(LwidthParMin),
                        'LwidthParMax': float(LwidthParMax)
                    }
            else:
                if function == 'Gaussian':
                    generalVars.extra_fitting_functions[note + "_" + function + "_" + str(existing_cnt[note + "_" + function])] = {
                        'xParVal': float(xParVal),
                        'xParMin': float(xParMin),
                        'xParMax': float(xParMax),
                        
                        'ampParVal': float(ampParVal),
                        'ampParMin': float(ampParMin),
                        'ampParMax': float(ampParMax),
                        
                        'GwidthParVal': float(GwidthParVal),
                        'GwidthParMin': float(GwidthParMin),
                        'GwidthParMax': float(GwidthParMax),
                        
                        'widthRes': float(GwidthParResVar.get())
                    }
                elif function == 'Lorentzian':
                    generalVars.extra_fitting_functions[note + "_" + function + "_" + str(existing_cnt[note + "_" + function])] = {
                        'xParVal': float(xParVal),
                        'xParMin': float(xParMin),
                        'xParMax': float(xParMax),
                        
                        'ampParVal': float(ampParVal),
                        'ampParMin': float(ampParMin),
                        'ampParMax': float(ampParMax),
                        
                        'LwidthParVal': float(LwidthParVal),
                        'LwidthParMin': float(LwidthParMin),
                        'LwidthParMax': float(LwidthParMax),
                        
                        'widthRes': float(LwidthParResVar.get())
                    }
                elif function == 'Voigt':
                    generalVars.extra_fitting_functions[note + "_" + function + "_" + str(existing_cnt[note + "_" + function])] = {
                        'xParVal': float(xParVal),
                        'xParMin': float(xParMin),
                        'xParMax': float(xParMax),
                        
                        'ampParVal': float(ampParVal),
                        'ampParMin': float(ampParMin),
                        'ampParMax': float(ampParMax),
                        
                        'GwidthParVal': float(GwidthParVal),
                        'GwidthParMin': float(GwidthParMin),
                        'GwidthParMax': float(GwidthParMax),
                        
                        'widthRes': float(GwidthParResVar.get()),
                        
                        'LwidthParVal': float(LwidthParVal),
                        'LwidthParMin': float(LwidthParMin),
                        'LwidthParMax': float(LwidthParMax)
                    }
                
                existing_cnt[note + "_" + function] += 1
        
        # We have to control the interface button through the cascade menu as tkinter does not return an object for it
        guiVars.total_menu.entryconfigure(5, state=NORMAL if len(generalVars.extra_fitting_functions) > 0 else DISABLED) # type: ignore
    
    addButton = Button(extraFit, text="Add", command=lambda: addFunction())
    removeButton = Button(extraFit, text="Remove", command=lambda: removeFunction())
    updateButton = Button(extraFit, text="Update", command=lambda: updateFunction())
    applyButton = Button(extraFit, text="Apply", command=lambda: applyFunction())

    
    functionsLabel.grid(column=0, row=0, sticky="WE")
    functionsDropdown.grid(column=1, row=0, sticky="WE")
    
    noteLabel.grid(column=0, row=1, sticky="WE")
    noteEntry.grid(column=1, row=1, sticky="WE")
    
    parLabel.grid(column=0, row=2, padx=5, sticky="WE")
    parValLabel.grid(column=1, row=2, padx=5, sticky="WE")
    parMinLabel.grid(column=2, row=2, padx=5, sticky="WE")
    parMaxLabel.grid(column=3, row=2, padx=5, sticky="WE")
    
    xParLabel.grid(column=0, row=3, padx=5, sticky="WE")
    xParValEntry.grid(column=1, row=3, padx=5, sticky="WE")
    xParMinEntry.grid(column=2, row=3, padx=5, sticky="WE")
    xParMaxEntry.grid(column=3, row=3, padx=5, sticky="WE")
    
    ampParLabel.grid(column=0, row=4, padx=5, sticky="WE")
    ampParValEntry.grid(column=1, row=4, padx=5, sticky="WE")
    ampParMinEntry.grid(column=2, row=4, padx=5, sticky="WE")
    ampParMaxEntry.grid(column=3, row=4, padx=5, sticky="WE")
    ampParLabelNote.grid(column=4, row=4, padx=5, sticky="WE")
    
    GwidthParLabel.grid(column=0, row=5, padx=5, sticky="WE")
    GwidthParValEntry.grid(column=1, row=5, padx=5, sticky="WE")
    GwidthParMinEntry.grid(column=2, row=5, padx=5, sticky="WE")
    GwidthParMaxEntry.grid(column=3, row=5, padx=5, sticky="WE")
    GwidthParResLabel.grid(column=4, row=5, padx=(5, 0), sticky="WE")
    GwidthParResCheck.grid(column=5, row=5, padx=5, sticky="WE")

    LwidthParLabel.grid(column=0, row=6, padx=5, sticky="WE")
    LwidthParValEntry.grid(column=1, row=6, padx=5, sticky="WE")
    LwidthParMinEntry.grid(column=2, row=6, padx=5, sticky="WE")
    LwidthParMaxEntry.grid(column=3, row=6, padx=5, sticky="WE")
    LwidthParResLabel.grid(column=4, row=6, padx=(5, 0), sticky="WE")
    LwidthParResCheck.grid(column=5, row=6, padx=5, sticky="WE")
    
    boxTitle.grid(column=0, row=7, columnspan=6, pady=(10, 0))
    extraFunctionsBox.grid(column=0, row=8, columnspan=6, sticky="NEWS")
    
    addButton.grid(column=1, row=9, sticky="WE")
    removeButton.grid(column=2, row=9, sticky="WE")
    updateButton.grid(column=3, row=9, sticky="WE")
    applyButton.grid(column=4, row=9, sticky="WE")
    
    extraFit.columnconfigure((1, 2, 3, 4), weight=1)
    extraFit.rowconfigure((8), weight=1)
    
    updateFunctionEntries(None)
    
    if len(generalVars.extra_fitting_functions) > 0:
        for key in generalVars.extra_fitting_functions:
            note = key.split("_")[0]
            function = key.split("_")[1]
            
            pars = generalVars.extra_fitting_functions[key]
            
            xParText = f'xPar({pars["xParMin"]} < {pars["xParVal"]} < {pars["xParMax"]})'
            ampParText = f'ampPar({pars["ampParMin"]} < {pars["ampParVal"]} < {pars["ampParMax"]})'
            
            if function == 'Gaussian':
                GwidthParText = f'GwidthPar({pars["GwidthParMin"]} < {pars["GwidthParVal"]} < {pars["GwidthParMax"]}){"*" if pars["widthRes"] == 1.0 else " "}'
                extraFunctionsBox.insert(END, f'{note: <10}, {function: <20}: {xParText: >30}{ampParText: >30}{GwidthParText: >30}')
            elif function == 'Lorentzian':
                LwidthParText = f'LwidthPar({pars["LwidthParMin"]} < {pars["LwidthParVal"]} < {pars["LwidthParMax"]}){"*" if pars["widthRes"] == 1.0 else " "}'
                extraFunctionsBox.insert(END, f'{note: <10}, {function: <20}: {xParText: >30}{ampParText: >30}{LwidthParText: >30}')
            elif function == 'Voigt':
                GwidthParText = f'GwidthPar({pars["GwidthParMin"]} < {pars["GwidthParVal"]} < {pars["GwidthParMax"]}){"*" if pars["widthRes"] == 1.0 else " "}'
                LwidthParText = f'LwidthPar({pars["LwidthParMin"]} < {pars["LwidthParVal"]} < {pars["LwidthParMax"]})'
                extraFunctionsBox.insert(END, f'{note: <10}, {function: <20}: {xParText: >30}{ampParText: >30}{GwidthParText: >30}{LwidthParText: >30}')