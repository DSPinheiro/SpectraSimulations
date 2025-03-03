
from __future__ import annotations


from pathlib import Path

import data.variables as generalVars

import interface.variables as guiVars

from simulation.simulation import simulate

from interface.updaters import selected, selected_2j, selected_spectra, selected_quant_conf, \
                reset_limits, select_all_transitions, update_offsets, update_transition_dropdown, \
                update_quant_table, selected_elements, selected_base

from interface.base import _quit, restarter, VerticalScrolledFrame

from interface.extras import startMatrixWindow, startBoostWindow, \
                            startCascadeDiagram, startCascadeSatellite, startCascadeAuger, \
                            startConvergenceWindow, configureCSMix, fitOptionsWindow, \
                            configure_shake_params


from interface.experimental import extractExpVals, getBoundedExp


from utils.misc.fileIO import load, add_spectra, load_effic_file, write_to_xls, loadExp, \
                            save_quantConfig, load_quantConfig


#GUI Imports
from tkinter import *
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.figure import Figure

from functools import partial


from typing import List

# --------------------------------------------------------- #
#                                                           #
#      FUNCTIONS TO INITIALIZE AND CONFIGURE ELEMENTS       #
#                                                           #
# --------------------------------------------------------- #

# Initialize and configure the simulation plot
def configureSimuPlot(root: Tk, quantify: bool = False):
    """
    Function to initialize and configure the simulation window and plot
        
        Args:
            
        
        Returns:
            sim: tkinter simulation window object
            panel_1: tkinter panel object to hold the simulation frame
            f: matplotlib figure object for the simulation plot
            a: maplotlib plot object where we will plot the simulation data
            figure_frame: tkinter frame object to hold the tkinter simulation figure object
            canvas: tkinter object we can place in the frame which is created from the matplotlib figure
    """
    
    # ---------------------------------------------------------------------------------------------------------------
    # Define the title
    root.title("Spectrum Simulation")
    
    root.resizable(True, True)
    
    if quantify:
        root.geometry("1050x700")
    else:
        root.geometry("1400x700")
    
    # Pack a panel into the window where we will place our canvas to plot the simulations. This way the window will properly resize
    panel_1 = PanedWindow(root, orient=VERTICAL)
    panel_1.pack(fill=BOTH, expand=1)
    
    # ---------------------------------------------------------------------------------------------------------------
    # Matplotlib figure where we will place the graph objects
    f = Figure(figsize=(10, 5), dpi=100)
    # Add a plotting space to the figure
    a = f.add_subplot(111)
    # Set labels for the axis
    a.set_xlabel('Energy (eV)')
    a.set_ylabel('Intensity (arb. units)')
    
    
    # ---------------------------------------------------------------------------------------------------------------
    # Frame where we will place the figure with the graph
    figure_frame = Frame(panel_1, relief=GROOVE) # grooved border style
    # Add the frame to the panel
    panel_1.add(figure_frame)
    # Create the tk widget canvas to place the figure in the frame
    canvas = FigureCanvasTkAgg(f, master=figure_frame)
    # pack the canvas in the frame
    canvas.get_tk_widget().pack(fill=BOTH, expand=1)

    # Store the interface objects for use in other functions across the file
    guiVars._a = a
    guiVars._f = f
    guiVars._canvas = canvas
    
    return panel_1, f, a, figure_frame, canvas

# Initialize and configure the areas where we will place the buttons, entries and labels for the simulation parameters
def configureButtonArea(root: Tk, canvas: FigureCanvasTkAgg):
    """
    Function to initialize and configure the areas where we will place the buttons, entries and labels for the simulation parameters
        
        Args:
            sim: tkinter simulation window object
            canvas: tkinter object we can place in the frame which is created from the matplotlib figure
        
        Returns:
            panel_2: tkinter panel placed below the simulation plot
            toolbar_frame: tkinter frame for the matplotlib graph buttons
            toolbar: tkinter object for the matplotlib default toolbar
            full_frame: tkinter frame for the remaining buttons
            buttons_frame: tkinter frame for the transition dropdown
            buttons_frame2: tkinter frame for the bounds entries and reset button
            buttons_frame3: tkinter frame for the simulation parameters entries (offsets, resolution, calculate button)
            buttons_frame4: tkinter frame for the progress bar
    """
    # Panel for the area below the plot
    panel_2 = PanedWindow(root, orient=VERTICAL)
    panel_2.pack(fill=X, expand=0)

    # Matplotlib toolbar
    toolbar_frame = Frame(panel_2, bd=1, relief=GROOVE)
    panel_2.add(toolbar_frame)
    toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)

    # Frame for the buttons
    full_frame = Frame(panel_2, relief=GROOVE)
    panel_2.add(full_frame)
    buttons_frame = Frame(full_frame, bd=1, relief=GROOVE)
    buttons_frame.pack(fill=BOTH, expand=1)
    # Max, min & Points Frame
    buttons_frame2 = Frame(full_frame, bd=1, relief=GROOVE)
    buttons_frame2.pack(fill=BOTH, expand=1)
    # Frame  yoffset, Energy offset and Calculate
    buttons_frame3 = Frame(full_frame, bd=1, relief=GROOVE, name='buttons_frame3')
    buttons_frame3.pack(fill=BOTH, expand=1)
    # Frame progress bar
    buttons_frame4 = Frame(full_frame)
    buttons_frame4.pack(fill=BOTH, expand=1)

    guiVars._toolbar = toolbar
    
    return panel_2, toolbar_frame, toolbar, full_frame, buttons_frame, buttons_frame2, buttons_frame3, buttons_frame4

# Setup the variables to hold the values of the interface entries
def setupVars(p: Tk):
    """
    Function to setup the variables to hold the values of the interface entries
        
        Args:
            p: tkinter parent object
        
        Returns:
            Nothing, all the variables initalized in the function are global module variables that can be used in other modules directly
    """
    # setup the parent object to bind stuff to
    guiVars._parent = p
    
    # ---------------------------------------------------------------------------------------------------------------
    # Variable to know if we need to show the total y in the plot
    guiVars.totalvar = StringVar(master = guiVars._parent)
    # Initialize it as false
    guiVars.totalvar.set('No')
    # Variable to know if we need to show the total diagram y in the plot
    guiVars.totaldiagvar = StringVar(master = guiVars._parent)
    # Initialize it as false
    guiVars.totaldiagvar.set('No')
    # Variable to know if we need to show the total satellite y in the plot
    guiVars.totalsatvar = StringVar(master = guiVars._parent)
    # Initialize it as false
    guiVars.totalsatvar.set('No')
    # Variable to know if we need to show the total shake-off y in the plot
    guiVars.totalshkoffvar = StringVar(master = guiVars._parent)
    # Initialize it as false
    guiVars.totalshkoffvar.set('No')
    # Variable to know if we need to show the total shake-up y in the plot
    guiVars.totalshkupvar = StringVar(master = guiVars._parent)
    # Initialize it as false
    guiVars.totalshkupvar.set('No')
    # Variable to know if we need to show the total extra fit y in the plot
    guiVars.totalextrafitvar = StringVar(master = guiVars._parent)
    # Initialize it as false
    guiVars.totalextrafitvar.set('No')
    # Variable to know if we need to make the y axis logarithmic or linear
    guiVars.yscale_log = StringVar(master = guiVars._parent)
    # Initialize it as false
    guiVars.yscale_log.set('No')
    # Variable to know if we need to make the x axis logarithmic or linear
    guiVars.xscale_log = StringVar(master = guiVars._parent)
    # Initialize it as false
    guiVars.xscale_log.set('No')
    # Variable to know if we need to perform an autofit of the simulation to experimental data
    guiVars.autofitvar = StringVar(master = guiVars._parent)
    # Initialize it as false
    guiVars.autofitvar.set('No')
   
    # Variable to know what normalization we need to perform (no normalization, normalize to unity, normalize to experimental maximum)
    guiVars.normalizevar = StringVar(master = guiVars._parent)
    # Initialize to no normalization
    guiVars.normalizevar.set('No')
    # Variable to know if we need to load an experimental spectrum and if so where it is located
    guiVars.loadvar = StringVar(master = guiVars._parent)
    # Initialize to no file
    guiVars.loadvar.set('No')
    # Variable to know if we need to load detector efficiency data and if so where it is located
    guiVars.effic_var = StringVar(master = guiVars._parent)
    # Initialize to no file
    guiVars.effic_var.set('No')

    # Variable to hold the experimental resolution value introduced in the interface
    guiVars.exp_resolution = DoubleVar(master = guiVars._parent, value=1.0)
    # Variable to hold the experimental background offset value introduced in the interface
    guiVars.yoffset = DoubleVar(master = guiVars._parent, value=0.0)
    # Variable to hold the experimental energy offset value introduced in the interface
    guiVars.energy_offset = DoubleVar(master = guiVars._parent, value=0.0)
    # Variable to hold the experimental satellite energy offset value introduced in the interface
    guiVars.sat_energy_offset = DoubleVar(master = guiVars._parent, value=0.0)
    # Variable to hold the experimental shake-off energy offset value introduced in the interface
    guiVars.shkoff_energy_offset = DoubleVar(master = guiVars._parent, value=0.0)
    # Variable to hold the experimental shake-up energy offset value introduced in the interface
    guiVars.shkup_energy_offset = DoubleVar(master = guiVars._parent, value=0.0)
    # Variable to hold the excitation/beam energy value introduced in the interface
    guiVars.excitation_energy = DoubleVar(master = guiVars._parent, value=0.0)
    # Variable to hold the excitation/beam energy FWHM value introduced in the interface
    guiVars.excitation_energyFWHM = DoubleVar(master = guiVars._parent, value=0.0)
    # Variable to hold the number of points to simulate introduced in the interface
    guiVars.number_points = IntVar(master = guiVars._parent, value=500)
    
    # Variable to hold the maximum x value to be simulated introduced in the interface
    guiVars.x_max = StringVar(master = guiVars._parent)
    # Initialize to be calculated automatically
    guiVars.x_max.set('Auto')
    # Variable to hold the minimum x value to be simulated introduced in the interface
    guiVars.x_min = StringVar(master = guiVars._parent)
    # Initialize to be calculated automatically
    guiVars.x_min.set('Auto')
    
    # Variable to hold the percentage of current progress to be displayed in the bottom of the interface
    guiVars.progress_var = DoubleVar(master = guiVars._parent)
    
    # Variable to hold the text with the selected transitions that will be shown in the interface label
    guiVars.label_text = StringVar(master = guiVars._parent)
    
    # Variable to hold the text with the selected 2j values that will be shown in the interface label
    guiVars.jj_text = StringVar(master = guiVars._parent)
    
    # Initialize the transition type to diagram
    guiVars.satelite_var = StringVar(value='Diagram')
    # Initialize the simulation type to simulation
    guiVars.choice_var = StringVar(value='Simulation')
    # Initialize the profile type to lorentzian
    guiVars.type_var = StringVar(value='Lorentzian')
    # Initialize the exitation mechanism to empty as this is not yet implemented
    guiVars.exc_mech_var = StringVar(value='')
    
    # Initialize the baseline type to SNIP
    guiVars.baseline_type = StringVar(value='SNIP')
    
    # Initialize the SNIP max window to 10
    guiVars.max_window = IntVar(value=10)
    # Initialize the SNIP smooth window to 1
    guiVars.smooth_window = IntVar(value=1)
    # Initialize the SNIP iteration order to false
    guiVars.decreasing = BooleanVar(value=False)
    
    # Initialize the cascade flag as false
    guiVars.include_cascades = BooleanVar(value=False)
    # Initialize the separate offsets flag as false
    guiVars.separate_offsets = BooleanVar(value=False)
    # Initialize the separate offsets flag as false
    guiVars.fit_shake_prob = BooleanVar(value=False)
    # Initialize the 2J colors flag as false
    guiVars.JJ_colors = BooleanVar(value=False)
 
# Setup the buttons in the button area
def setupButtonArea(dir_path: Path, buttons_frame: Frame, buttons_frame2: Frame, buttons_frame3: Frame, buttons_frame4: Frame, excitation: bool = False, quantify: bool = False):
    """
    Function to setup the buttons in the button area
        
        Args:
            buttons_frame: tkinter frame for the transition dropdown
            buttons_frame2: tkinter frame for the bounds entries and reset button
            buttons_frame3: tkinter frame for the simulation parameters entries (offsets, resolution, calculate button)
            buttons_frame4: tkinter frame for the progress bar
        
        Returns:
            Nothing, we just configure the interface elements in the various button frames below the simulation plot
    """
    
    # Before selecting any transition we show this
    guiVars.label_text.set('Select a Transition: ') # type: ignore
    ttk.Label(buttons_frame, textvariable=guiVars.label_text).grid(row=0, column=1) # type: ignore
    
    if not quantify:
        # Before selecting any 2j value we show this
        guiVars.jj_text.set('Select a 2J value: ') # type: ignore
        ttk.Label(buttons_frame, textvariable=guiVars.jj_text).grid(row=0, column=3) # type: ignore
    
    
    # Transitions dropdown
    guiVars.drop_menu = ttk.Combobox(buttons_frame, value=[transition for transition in generalVars.the_dictionary], height=5, width=10) # type: ignore
    guiVars.drop_menu.set('Transitions:')
    guiVars.drop_menu.bind("<<ComboboxSelected>>", selected)
    guiVars.drop_menu.grid(row=0, column=0)
    
    if not quantify:
        # 2J dropdown
        guiVars.drop_menu_2j = ttk.Combobox(buttons_frame, value=["N/A"], height=5, width=10, state='disabled') # type: ignore
        guiVars.drop_menu_2j.set('2J values:')
        guiVars.drop_menu_2j.bind("<<ComboboxSelected>>", selected_2j)
        guiVars.drop_menu_2j.grid(row=0, column=2)
    
    
    # N Points
    ttk.Label(buttons_frame2, text="Points").pack(side=LEFT)
    ttk.Entry(buttons_frame2, width=7, textvariable=guiVars.number_points).pack(side=LEFT) # type: ignore
    if not quantify:
        # X max
        ttk.Label(buttons_frame2, text="x Max").pack(side=LEFT)
        ttk.Entry(buttons_frame2, width=7, textvariable=guiVars.x_max).pack(side=LEFT) # type: ignore
        # X min
        ttk.Label(buttons_frame2, text="x Min").pack(side=LEFT)
        ttk.Entry(buttons_frame2, width=7, textvariable=guiVars.x_min).pack(side=LEFT) # type: ignore
        # Reset limits button
        ttk.Button(master=buttons_frame2, text="Reset", command=lambda: reset_limits()).pack(side=LEFT, padx=(10, 0))
    # Select all transitions
    ttk.Button(master=buttons_frame2, text="Select All Transitions", command=lambda: select_all_transitions()).pack(side=LEFT, padx=(30, 0))
    if not quantify:
        # Include cascades in simulated intensity
        ttk.Checkbutton(buttons_frame2, text='Cascades', variable=guiVars.include_cascades, onvalue=1, offvalue=0, width=10).pack(side=LEFT, padx=(20, 5)) # type: ignore
    # Swap between all satellite offset and separate shake-off and shake-up offsets
    ttk.Checkbutton(buttons_frame2, text='Separate offsets', variable=guiVars.separate_offsets, command=lambda: update_offsets(buttons_frame3), state='', onvalue=1, offvalue=0, width=15).pack(side=LEFT, padx=(5, 5)) # type: ignore
    # Additional fit parameters for the shake probabilities
    ttk.Checkbutton(buttons_frame2, text='Fit Shake Probabilities', variable=guiVars.fit_shake_prob, command=lambda: configure_shake_params(), state='', onvalue=1, offvalue=0, width=20).pack(side=LEFT, padx=(5, 30)) # type: ignore
    if not quantify:
        # Plot each 2J with a seperate color (only for stick plots)
        ttk.Checkbutton(buttons_frame2, text='2J Colors (stick)', variable=guiVars.JJ_colors, state='', onvalue=1, offvalue=0, width=15).pack(side=LEFT, padx=(20, 30)) # type: ignore
    
    # Calculate button
    ttk.Style().configure('red/black.TButton', foreground='red', background='black')
    ttk.Button(master=buttons_frame3, text=("Calculate" if not quantify else "Fit"), command=lambda: simulate(dir_path, guiVars._parent, guiVars._f, guiVars._a, excitation, quantify), style='red/black.TButton').pack(side=RIGHT, padx=(30, 0)) # type: ignore
    # yoffset
    ttk.Entry(buttons_frame3, width=7, textvariable=guiVars.yoffset).pack(side=RIGHT) # type: ignore
    ttk.Label(buttons_frame3, text="y Offset").pack(side=RIGHT)
    # Shake-up En. Offset
    ttk.Entry(buttons_frame3, width=7, textvariable=guiVars.shkup_energy_offset, name='shkup_offsetEntry', state='disabled').pack(side=RIGHT, padx=(0, 30)) # type: ignore
    ttk.Label(buttons_frame3, text="Shake-up offset (eV)", name='shkup_offsetLabel', state='disabled').pack(side=RIGHT)
    # Shake-off En. Offset
    ttk.Entry(buttons_frame3, width=7, textvariable=guiVars.shkoff_energy_offset, name='shkoff_offsetEntry', state='disabled').pack(side=RIGHT, padx=(0, 5)) # type: ignore
    ttk.Label(buttons_frame3, text="Shake-off offset (eV)", name='shkoff_offsetLabel', state='disabled').pack(side=RIGHT)
    # Satellite En. Offset
    ttk.Entry(buttons_frame3, width=7, textvariable=guiVars.sat_energy_offset, name='sat_offsetEntry').pack(side=RIGHT, padx=(0, 5)) # type: ignore
    ttk.Label(buttons_frame3, text="Satellite offset (eV)", name='sat_offsetLabel').pack(side=RIGHT)
    # En. Offset
    ttk.Entry(buttons_frame3, width=7, textvariable=guiVars.energy_offset).pack(side=RIGHT, padx=(0, 5)) # type: ignore
    ttk.Label(buttons_frame3, text="En. offset (eV)").pack(side=RIGHT)
    if not quantify:
        # Beam Energy
        ttk.Entry(buttons_frame3, width=7, textvariable=guiVars.excitation_energy).pack(side=RIGHT, padx=(0, 30)) # type: ignore
        ttk.Label(buttons_frame3, text="Beam Energy (eV)").pack(side=RIGHT)
        # Beam Energy FWHM
        ttk.Entry(buttons_frame3, width=7, textvariable=guiVars.excitation_energyFWHM).pack(side=RIGHT, padx=(0, 5)) # type: ignore
        ttk.Label(buttons_frame3, text="Beam FWHM (eV)").pack(side=RIGHT)
    # Energy Resolution
    ttk.Label(buttons_frame3, text="Experimental Resolution (eV)").pack(side=LEFT)
    ttk.Entry(buttons_frame3, width=7, textvariable=guiVars.exp_resolution).pack(side=LEFT) # type: ignore
    
    # Progress Bar
    ttk.Progressbar(buttons_frame4, variable=guiVars.progress_var, maximum=100).pack(fill=X, expand=1) # type: ignore

# Setup the dropdown menus on the top toolbar
def setupMenus(root: Tk, CS_exists: bool, Exc_exists: bool, quantify: bool = False):
    """
    Function to setup the dropdown menus on the top toolbar
        
        Args:
            CS_exists: boolean if the charge states folder exists for the current element
        
        Returns:
            Nothing, we just setup the top toolbar and bind the necessary variables and functions to the interface elements
    """
    
    # Initialize the menus
    my_menu = Menu(root)
    root.config(menu=my_menu) # type: ignore
    options_menu = Menu(my_menu, tearoff=0)
    total_menu = Menu(my_menu, tearoff=0)
    if not quantify:
        stick_plot_menu = Menu(my_menu, tearoff=0)
    transition_type_menu = Menu(my_menu, tearoff=0)
    if not quantify:
        line_type_menu = Menu(my_menu, tearoff=0)
    fitting_menu = Menu(my_menu, tearoff=0)
    fitting_method = Menu(fitting_menu,tearoff=0)
    if not quantify:
        norm_menu = Menu(my_menu, tearoff=0)
    exc_mech_menu = Menu(my_menu, tearoff=0)
    if not quantify:
        tool_menu = Menu(my_menu, tearoff=0)
        cascade_analysis = Menu(my_menu, tearoff=0)
    else:
        baseline_menu = Menu(my_menu, tearoff=0)
        window_menu = Menu(my_menu, tearoff=0)
    
    # ---------------------------------------------------------------------------------------------------------------
    # Add the Options dropdown menu and the buttons bound to the corresponding variables and functions
    my_menu.add_cascade(label="Options", menu=options_menu)
    options_menu.add_cascade(label="Show Total Y", menu=total_menu)
    total_menu.add_checkbutton(label='Total Y', variable=guiVars.totalvar, onvalue='Total', offvalue='No') # type: ignore
    total_menu.add_checkbutton(label='Total Diagram Y', variable=guiVars.totaldiagvar, onvalue='Total', offvalue='No') # type: ignore
    total_menu.add_checkbutton(label='Total Satellite Y', variable=guiVars.totalsatvar, onvalue='Total', offvalue='No') # type: ignore
    total_menu.add_checkbutton(label='Total Shake-off Y', variable=guiVars.totalshkoffvar, onvalue='Total', offvalue='No') # type: ignore
    total_menu.add_checkbutton(label='Total Shake-up Y', variable=guiVars.totalshkupvar, onvalue='Total', offvalue='No') # type: ignore
    total_menu.add_checkbutton(label='Total Extra Fit Y', variable=guiVars.totalextrafitvar, onvalue='Total', offvalue='No', state='disabled') # type: ignore
    guiVars.total_menu = total_menu
    options_menu.add_separator()
    options_menu.add_checkbutton(label='Log Scale Y Axis', variable=guiVars.yscale_log, onvalue='Ylog', offvalue='No') # type: ignore
    options_menu.add_checkbutton(label='Log Scale X Axis', variable=guiVars.xscale_log, onvalue='Xlog', offvalue='No') # type: ignore
    options_menu.add_separator()
    options_menu.add_command(label="Load Experimental Spectrum", command=lambda: load(guiVars.loadvar)) # type: ignore
    options_menu.add_checkbutton(label="Import Detector Efficiency", command=lambda: load_effic_file(guiVars.effic_var)) # type: ignore
    options_menu.add_separator()
    options_menu.add_command(label="Export Spectrum", command=lambda: write_to_xls(guiVars.satelite_var.get(), guiVars.energy_offset.get(), guiVars.sat_energy_offset.get(), guiVars.shkoff_energy_offset.get(), guiVars.shkup_energy_offset.get(), guiVars.excitation_energy.get(), guiVars.excitation_energyFWHM.get(), guiVars.yoffset.get(), guiVars._residues_graph)) # type: ignore
    options_menu.add_separator()
    options_menu.add_command(label="Choose New Element", command=restarter)
    options_menu.add_command(label="Quit", command=_quit)
    
    if not quantify:
        # ---------------------------------------------------------------------------------------------------------------
        # Add the Spectrum type dropdown menu and the buttons bound to the corresponding variables and functions
        my_menu.add_cascade(label="Spectrum Type", menu=stick_plot_menu)
        stick_plot_menu.add_checkbutton(label='Stick', variable=guiVars.choice_var, onvalue='Stick', offvalue='') # type: ignore
        stick_plot_menu.add_checkbutton(label='Simulation', variable=guiVars.choice_var, onvalue='Simulation', offvalue='') # type: ignore
        stick_plot_menu.add_checkbutton(label='CS Mixture: Stick', variable=guiVars.choice_var, onvalue='M_Stick', offvalue='', command=lambda: configureCSMix(), state='disabled') # type: ignore
        stick_plot_menu.add_checkbutton(label='CS Mixture: Simulation', variable=guiVars.choice_var, onvalue='M_Simulation', offvalue='', command=lambda: configureCSMix(), state='disabled') # type: ignore
        # Active and deactivate the charge state mixture options if they exist
        if CS_exists:
            stick_plot_menu.entryconfigure(2, state=NORMAL)
            # Good TK documentation: https://tkdocs.com/tutorial/menus.html
            stick_plot_menu.entryconfigure(3, state=NORMAL)
        
    # ---------------------------------------------------------------------------------------------------------------
    # Add the Transition type dropdown menu and the buttons bound to the corresponding variables and functions
    my_menu.add_cascade(label="Transitions Type", menu=transition_type_menu)
    transition_type_menu.add_checkbutton(label='Diagram', variable=guiVars.satelite_var, onvalue='Diagram', offvalue='', command=lambda: update_transition_dropdown(cascade_analysis)) # type: ignore
    transition_type_menu.add_checkbutton(label='Satellites', variable=guiVars.satelite_var, onvalue='Satellites', offvalue='', command=lambda: update_transition_dropdown(cascade_analysis)) # type: ignore
    transition_type_menu.add_checkbutton(label='Diagram + Satellites', variable=guiVars.satelite_var, onvalue='Diagram + Satellites', offvalue='', command=lambda: update_transition_dropdown(cascade_analysis)) # type: ignore
    if not quantify:
        transition_type_menu.add_checkbutton(label='Excitation', variable=guiVars.satelite_var, onvalue='Excitation', offvalue='', command=lambda: update_transition_dropdown(cascade_analysis), state='disabled') # type: ignore
        transition_type_menu.add_checkbutton(label='Excitation + Satellites', variable=guiVars.satelite_var, onvalue='Excitation + ESat', offvalue='', command=lambda: update_transition_dropdown(cascade_analysis), state='disabled') # type: ignore
        transition_type_menu.add_checkbutton(label='Excitation + Diagram', variable=guiVars.satelite_var, onvalue='Excitation + Diagram', offvalue='', command=lambda: update_transition_dropdown(cascade_analysis), state='disabled') # type: ignore
        transition_type_menu.add_checkbutton(label='Excitation + Diagram + Satellites', variable=guiVars.satelite_var, onvalue='Excitation + ESat + Diagram + Satellites', offvalue='', command=lambda: update_transition_dropdown(cascade_analysis), state='disabled') # type: ignore
        transition_type_menu.add_checkbutton(label='Auger', variable=guiVars.satelite_var, onvalue='Auger', offvalue='', command=lambda: update_transition_dropdown(cascade_analysis)) # type: ignore
    
        if Exc_exists:
            transition_type_menu.entryconfigure(3, state=NORMAL)
            transition_type_menu.entryconfigure(4, state=NORMAL)
            transition_type_menu.entryconfigure(5, state=NORMAL)
            transition_type_menu.entryconfigure(6, state=NORMAL)
    
    if not quantify:
        # ---------------------------------------------------------------------------------------------------------------
        # Add the Line type dropdown menu and the buttons bound to the corresponding variables and functions
        my_menu.add_cascade(label="Line Type", menu=line_type_menu)
        line_type_menu.add_checkbutton(label='Voigt', variable=guiVars.type_var, onvalue='Voigt', offvalue='') # type: ignore
        line_type_menu.add_checkbutton(label='Lorentzian', variable=guiVars.type_var, onvalue='Lorentzian', offvalue='') # type: ignore
        line_type_menu.add_checkbutton(label='Gaussian', variable=guiVars.type_var, onvalue='Gaussian', offvalue='') # type: ignore
    
    # ---------------------------------------------------------------------------------------------------------------
    # Add the Fitting dropdown menu and the buttons bound to the corresponding variables and functions
    my_menu.add_cascade(label="Fitting", menu=fitting_menu)
    fitting_menu.add_cascade(label = "Fit Method", menu = fitting_method)
    fitting_method.add_checkbutton(label='LMFit', variable=guiVars.autofitvar, onvalue='LMFit', offvalue='No') # type: ignore
    fitting_method.add_checkbutton(label='iminuit', variable=guiVars.autofitvar, onvalue='iminuit', offvalue='No') # type: ignore
    fitting_menu.add_command(label='Aditional Fitting Options', command=lambda: fitOptionsWindow())
    
    if not quantify:
        # ---------------------------------------------------------------------------------------------------------------
        # Add the Normalization options dropdown menu and the buttons bound to the corresponding variables and functions
        my_menu.add_cascade(label="Normalization Options", menu=norm_menu)
        norm_menu.add_checkbutton(label='to Experimental Maximum', variable=guiVars.normalizevar, onvalue='ExpMax', offvalue='No') # type: ignore
        norm_menu.add_checkbutton(label='to Unity', variable=guiVars.normalizevar, onvalue='One', offvalue='No') # type: ignore
    else:
        guiVars.normalizevar.set('ExpMax') # type: ignore
    
    # ---------------------------------------------------------------------------------------------------------------
    # Add the Excitation mechanism dropdown menu and the buttons bound to the corresponding variables and functions (disables as it is not implemented)
    my_menu.add_cascade(label="Excitation Mechanism", menu=exc_mech_menu)
    exc_mech_menu.add_checkbutton(label='Nuclear Electron Capture', variable=guiVars.exc_mech_var, onvalue='NEC', offvalue='', state="disabled") # type: ignore
    exc_mech_menu.add_checkbutton(label='Photoionization (ELAM database)', variable=guiVars.exc_mech_var, onvalue='PIon', offvalue='', state="disabled") # type: ignore
    exc_mech_menu.add_checkbutton(label='Electron Impact Ionization (MRBEB Model)', variable=guiVars.exc_mech_var, onvalue='EII', offvalue='', state="disabled") # type: ignore
    
    if generalVars.meanR_exists:
        exc_mech_menu.entryconfigure(2, state=NORMAL)
    if generalVars.ELAM_exists:
        exc_mech_menu.entryconfigure(1, state=NORMAL)
    
    if not quantify:
        # ---------------------------------------------------------------------------------------------------------------
        # Add the tools dropdown menu and the buttons bound to the corresponding functions
        my_menu.add_cascade(label="Tools", menu=tool_menu)
        tool_menu.add_command(label="Rate Matrix Analysis", command=lambda: startMatrixWindow(True))
        tool_menu.add_command(label="Boost Matrix Analysis", command=lambda: startBoostWindow(True))
        
        tool_menu.add_cascade(label="Cascade Analysis", menu=cascade_analysis)
        cascade_analysis.add_command(label="Diagram Cascade", command=lambda: startCascadeDiagram())
        cascade_analysis.add_command(label="Satellite Cascade", command=lambda: startCascadeSatellite())
        cascade_analysis.add_command(label="Auger Cascade", command=lambda: startCascadeAuger(), state=DISABLED)
        
        tool_menu.add_command(label="Convergence Analysis", command=lambda: startConvergenceWindow())
    else:
        my_menu.add_cascade(label="Baseline", menu=baseline_menu)
        baseline_menu.add_checkbutton(label="SNIP", variable=guiVars.baseline_type, onvalue='SNIP', offvalue='', command=lambda: configure_SNIP(root)) # type: ignore
        
        my_menu.add_cascade(label="Windows", menu=window_menu)
        window_menu.add_command(label="Periodic Table", command=lambda: PTable(root, guiVars.graph_area)) # type: ignore
        window_menu.add_command(label="Parameters Window", command=lambda: QuantPars(root))


# ---------------------------------------------------------------------------------------------------------------
# Configurate the window that apears after the periodic table where we choose the atomic parameters we want
def PTable(root: Tk, first: bool = False):
    """
    Function that creates and configures the interface where we select the elements we want to simulate and quantify.
        
        Args:
            root: root element for the tk app
        
        Returns:
            Nothing this is just a wrapper for the window creation
    """
    if guiVars.launched_ptable:
        return
    
    ptable = Toplevel(root)
    
    # Set title
    ptable.title("Periodic Table of the Elements")
    
    ptable.resizable(False, False)
    
    x = root.winfo_x()
    y = root.winfo_y()

    w = root.winfo_width()
    
    if first:
        ptable.geometry("%dx%d+%d+%d" % (620, 300, x + 3.19 * w, y))
    else:
        ptable.geometry("%dx%d+%d+%d" % (620, 300, x + w, y))
    
    # ---------------------------------------------------------------------------------------------------------------
    # Setup the window frame and grid system
    subelem = ttk.Frame(ptable, padding="3 3 12 12")
    """
    Window frame object
    """
    subelem.grid(column=0, row=0, sticky=(N, W, E, S)) # type: ignore
    subelem.columnconfigure(0, weight=1)
    subelem.rowconfigure(0, weight=1)
    
    
    # Set the labels and spacing around the periodic table that will be created using the grid system
    topLabel = Label(subelem, text="", font=20) # type: ignore
    topLabel.grid(row=2, column=3, columnspan=10)

    Label1 = Label(subelem, text="Click the element for which you would like to obtain the atomic parameters.", font=22) # type: ignore
    Label1.grid(row=0, column=0, columnspan=18)

    Label2 = Label(subelem, text="", font=20) # type: ignore
    Label2.grid(row=8, column=0, columnspan=18)

    Label3 = Label(subelem, text="* Lanthanoids", font=20) # type: ignore
    Label3.grid(row=9, column=1, columnspan=2)

    Label4 = Label(subelem, text="** Actinoids", font=20) # type: ignore
    Label4.grid(row=10, column=1, columnspan=2)

    # Create all buttons for the periodic table with a loop
    buttons: List[Button] = []
    
    exp = loadExp(generalVars.currentSpectraList[0])
    
    max_E = max([float(line[0]) for line in exp])
    min_E = min([float(line[0]) for line in exp])
    
    possibleElements: List[str] = []
    for line in generalVars.NIST_Data:
        if line[0] not in possibleElements:
            if float(line[3]) >= min_E and float(line[3]) <= max_E:
                possibleElements.append(line[0])
    
    for i, element in enumerate(generalVars.per_table):
        active = str(element[3]).strip() in possibleElements and element[0] in generalVars.existingElements
        button = \
            Button(subelem, text=element[3], width=3, height=1, bg="ghostwhite",
                   state=("normal" if active else "disabled"),
                   disabledforeground="darkgray"
                )
        
        update_elements = partial(selected_elements, ((i + 1), str(generalVars.per_table[i][3]), str(generalVars.per_table[i][5])), button)
        
        button.configure(command=update_elements)
        buttons.append(button)

        buttons[i].grid(row=element[6], column=element[7]) # type: ignore
    
    # Configure padding around the buttons
    for child in subelem.winfo_children():
        child.grid_configure(padx=0, pady=0)
    
    guiVars.launched_ptable = True
    
    def on_close():
        guiVars.launched_ptable = False
        ptable.destroy()
    
    ptable.protocol("WM_DELETE_WINDOW", on_close)


def QuantPars(root: Tk, first: bool = False):
    """
    Function that creates and configures the interface where we can see and modify the quantification parameters for the spectra.
        
        Args:
            root: root element for the tk app
        
        Returns:
            Nothing this is just a wrapper for the window creation
    """
    if guiVars.launched_quantPars:
        return
    
    quantPars = Toplevel(root)
    
    # Set title
    quantPars.title("Quantification and Matrix Parameters")
    
    quantPars.resizable(False, False)
    
    x = root.winfo_x()
    y = root.winfo_y()
    
    w = root.winfo_width()

    if first:
        quantPars.geometry("%dx%d+%d+%d" % (460, 370, x + 3.19 * w, y + 330))
    else:
        quantPars.geometry("%dx%d+%d+%d" % (460, 370, x + w, y + 330))
    
    # ---------------------------------------------------------------------------------------------------------------
    # Setup the window frame and grid system
    
    # Header section
    header = ttk.Frame(quantPars, padding="0 0 5 5")
    header.grid(column=0, row=0, sticky=NSEW)
    
    ttk.Label(header, text="Spectrum: ").grid(row=0, column=0)
    
    # Experimental Spectra dropdown
    guiVars.drop_spectra = ttk.Combobox(header, value=[spectra.split("/")[-1] for spectra in generalVars.currentSpectraList], height=5, width=35) # type: ignore
    
    guiVars.loadvar.set(generalVars.currentSpectraList[0]) # type: ignore
    
    exp_spectrum = loadExp(generalVars.currentSpectraList[0])
    xe, ye, sigma_exp = extractExpVals(exp_spectrum)
    generalVars.exp_x, generalVars.exp_y, generalVars.exp_sigma = getBoundedExp(xe, ye, sigma_exp, 0.0, 500, "Auto", "Auto")
    
    
    guiVars.drop_spectra.bind("<<ComboboxSelected>>", selected_spectra)
    guiVars.drop_spectra.current(0)
    guiVars.drop_spectra.grid(row=0, column=1, columnspan=3)
    
    ttk.Button(header, text="...", command=add_spectra).grid(row=0, column=4)
    ttk.Label(header, text="", width=10).grid(row=0, column=5)
    
    
    ttk.Label(header, text="Baseline: ").grid(row=1, column=0)
    
    # Experimental Xray tube Spectra dropdown
    generalVars.currentTubeSpectraList.insert(0, "SNIP Baseline")
    guiVars.drop_tube_spectra = ttk.Combobox(header, value=[spectra.split("/")[-1] for spectra in generalVars.currentTubeSpectraList], height=5, width=35) # type: ignore
    
    guiVars.drop_tube_spectra.bind("<<ComboboxSelected>>", selected_base)
    guiVars.drop_tube_spectra.current(0)
    guiVars.drop_tube_spectra.grid(row=1, column=1, columnspan=3)
    
    ttk.Button(header, text="...", command=add_spectra).grid(row=1, column=4)
    ttk.Label(header, text="", width=10).grid(row=1, column=5)
    
    
    # Parameters table
    tableHeader = ttk.Frame(quantPars, padding="0 0 0 0")
    tableHeader.grid(column=0, row=2, sticky=NSEW)
    
    tableHeader_1 = ttk.Entry(tableHeader, width=5)
    tableHeader_2 = ttk.Entry(tableHeader, width=10)
    tableHeader_3 = ttk.Entry(tableHeader, width=10)
    tableHeader_4 = ttk.Entry(tableHeader, width=10)
    tableHeader_5 = ttk.Entry(tableHeader, width=10)
    tableHeader_6 = ttk.Entry(tableHeader, width=10)
    tableHeader_7 = ttk.Entry(tableHeader, width=10)
    
    tableHeader_1.grid(row=0, column=0)
    tableHeader_2.grid(row=0, column=1)
    tableHeader_3.grid(row=0, column=2)
    tableHeader_4.grid(row=0, column=3)
    tableHeader_5.grid(row=0, column=4)
    tableHeader_6.grid(row=0, column=5)
    tableHeader_7.grid(row=0, column=6)
    
    tableHeader_1.insert(0, "")
    tableHeader_2.insert(0, "alpha")
    tableHeader_3.insert(0, "curr w%")
    tableHeader_4.insert(0, "target w%")
    tableHeader_5.insert(0, "target -w%")
    tableHeader_6.insert(0, "target +w%")
    tableHeader_7.insert(0, "unit")
    
    tableHeader_1.configure(state="disabled")
    tableHeader_2.configure(state="disabled")
    tableHeader_3.configure(state="disabled")
    tableHeader_4.configure(state="disabled")
    tableHeader_5.configure(state="disabled")
    tableHeader_6.configure(state="disabled")
    tableHeader_7.configure(state="disabled")
    
    
    guiVars.table = VerticalScrolledFrame(quantPars)
    guiVars.table.grid(column=0, row=3, sticky=NSEW)
    
    update_quant_table()
    
    # Bottom buttons
    buttonsFrame = ttk.Frame(quantPars, padding="0 0 20 20")
    buttonsFrame.grid(column=0, row=4, sticky=NSEW)
    
    # Experimental Spectra dropdown
    guiVars.drop_quantConfs = ttk.Combobox(buttonsFrame, value=[conf.split("\\")[-1] for conf in generalVars.existingQuantConfs], height=5, width=30) # type: ignore
    guiVars.drop_quantConfs.bind("<<ComboboxSelected>>", selected_quant_conf)
    guiVars.drop_quantConfs.set("<New Quantification File>")
    # guiVars.drop_quantConfs.current(0)
    guiVars.drop_quantConfs.grid(row=0, column=0)
    
    ttk.Button(buttonsFrame, text="Save", command=save_quantConfig).grid(row=0, column=1)
    ttk.Button(buttonsFrame, text="Load", command=load_quantConfig).grid(row=0, column=2)
    
    guiVars.launched_quantPars = True
    
    def on_close():
        guiVars.launched_quantPars = False
        quantPars.destroy()
    
    quantPars.protocol("WM_DELETE_WINDOW", on_close)



def configure_SNIP(root: Tk):
    snipConf = Toplevel(root)
    
    # Set title
    snipConf.title("Configure SNIP parameters")
    
    snipConf.geometry("400x300")
    
    inner = ttk.Frame(snipConf)
    inner.grid(row=0, column=0, sticky=NSEW)
    
    ttk.Label(inner, text="Max Window: ").grid(row=0, column=0)
    ttk.Entry(inner, textvariable=guiVars.max_window).grid(row=0, column=1) # type: ignore
    
    ttk.Label(inner, text="Smoothing Window: ").grid(row=1, column=0)
    ttk.Entry(inner, textvariable=guiVars.smooth_window).grid(row=1, column=1) # type: ignore
    
    ttk.Label(inner, text="Decreasing: ").grid(row=2, column=0)
    ttk.Checkbutton(inner, variable=guiVars.decreasing).grid(row=2, column=1) # type: ignore