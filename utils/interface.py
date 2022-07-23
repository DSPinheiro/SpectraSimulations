"""
Module for interface variables and functions.
Here we define the variables bound to the interface elements, window management functions, keybinds,
functions to initialize interface elements, functions to update the elements and functions to plot external data
"""

#GUI Imports
from tkinter import *
from tkinter import ttk

#Matplotlib imports for plotting and tkinter compatibility
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib import gridspec
from matplotlib.backend_bases import key_press_handler

#Data import for variable management
from data.variables import labeldict, the_dictionary, the_aug_dictionary
import data.variables as generalVars

#Import file loaders for the interface
from utils.fileIO import load, load_effic_file, loadExp

#Import the main functions to bind them to the interface
#from utils.functions import y_calculator, func2min, stem_ploter, plot_stick
from utils.functions import * # Avoids circular imports from the tester

#Import numpy
import numpy as np

#Math import for interpolation
from scipy.interpolate import interp1d


# --------------------------------------------------------- #
#                                                           #
#         DEFINE THE VARIABLES TO INITIALIZE LATER          #
#                                                           #
# --------------------------------------------------------- #

# -----------------------------------------------------------------------------------------------------------------------------
# Private variables to hold current parent, window and plotting spaces.
# The parent is required to know where the GUI variables need to be bound to
# Might cause some confusion but when we split the code it was easier to do this instead of passing these between the functions
_parent = None
"""
Private variable for the current tkinter parent object
"""
_a = None
"""
Private variable for the matplotlib plot area object
"""
_sim = None
"""
Private variable for the tkinter simulation window object
"""
_f = None
"""
Private variable for the matplotlib simulation figure object
"""


# --------------------------------------------------------------------
# VARIABLES TO HOLD THE VALUES OF THE INTERFACE ENTRIES

# Variable to know if the total intensity needs to be shown
totalvar = None
"""
Variable to know if the total intensity needs to be shown
"""
# Variable to know if the y axis needs to be set as logarithmic
yscale_log = None
"""
Variable to know if the y axis needs to be set as logarithmic
"""
# Variable to know if the x axis needs to be set as logarithmic
xscale_log = None
"""
Variable to know if the x axis needs to be set as logarithmic
"""
# Variable to know if we need to perform an autofit to the simulation
autofitvar = None
"""
Variable to know if we need to perform an autofit to the simulation
"""
# Variable to know which normalization was chosen, if any
normalizevar = None
"""
Variable to know which normalization was chosen, if any
"""
# Variable to know where the experimental spectrum to load is located, if any
loadvar = None
"""
Variable to know where the experimental spectrum to load is located, if any
"""
# Variable to know where the detector efficiency to load is located, if any
effic_var = None
"""
Variable to know where the detector efficiency to load is located, if any
"""
# Variable to hold the value of the experimental resolution introduced by the user in the interface
exp_resolution = None
"""
Variable to hold the value of the experimental resolution introduced by the user in the interface
"""
# Variable to hold the value of the intensity offset introduced by the user in the interface
yoffset = None
"""
Variable to hold the value of the intensity offset introduced by the user in the interface
"""
# Variable to hold the value of the energy introduced by the user in the interface
energy_offset = None
"""
Variable to hold the value of the energy introduced by the user in the interface
"""
# Variable to hold the number of points introduced by the user in the interface, to calculate the energy grid where we simulate the spectrum
number_points = None
"""
Variable to hold the number of points introduced by the user in the interface, to calculate the energy grid where we simulate the spectrum
"""
# Variable to hold the value of the maximum energy to simulate introduced by the user in the interface
x_max = None
"""
Variable to hold the value of the maximum energy to simulate introduced by the user in the interface
"""
# Variable to hold the value of the minimum energy to simulate introduced by the user in the interface
x_min = None
"""
Variable to hold the value of the minimum energy to simulate introduced by the user in the interface
"""
# Variable to hold the value of the progress to show in the progress bar at the bottom of the interface
progress_var = None
"""
Variable to hold the value of the progress to show in the progress bar at the bottom of the interface
"""
# Variable to hold the names of the transitions selected for the simulation
transition_list = []
"""
Variable to hold the names of the transitions selected for the simulation
"""
# Variable to hold the text to show in the interface corresponding to the transition_list
label_text = None
"""
Variable to hold the text to show in the interface corresponding to the transition_list
"""


# Variable to know which types of transitions to simulate (radiative, auger, satellites)
satelite_var = None
"""
Variable to know which types of transitions to simulate (radiative, auger, satellites)
"""
# Variable to know which type of simulation to perform (stick, simulation, with or without multiple charge states)
choice_var = None
"""
Variable to know which type of simulation to perform (stick, simulation, with or without multiple charge states)
"""
# Variable to know which type of profile we want to simulate fro each line
type_var = None
"""
Variable to know which type of profile we want to simulate fro each line
"""
# Variable to know which type of exiting mechanism we want to consider in the simulation (currently not implemented)
exc_mech_var = None
"""
Variable to know which type of exiting mechanism we want to consider in the simulation (currently not implemented)
"""

# ---------------------------------------------------------------------
# VARIABLES TO HOLD THE TKINTER ENTRIES AND LABELS

# Dropdown from where to choose the transitions to simulate
drop_menu = None
"""
Dropdown from where to choose the transitions to simulate
"""
# Label where to write the label_text
trans_lable = None
"""
Label where to write the label_text
"""

# Entry where to type the number of points to simulate
points = None
"""
Entry where to type the number of points to simulate
"""
# Entry where to type the maximum energy to simulate
max_x = None
"""
Entry where to type the maximum energy to simulate
"""
# Entry where to type the minimum energy to simulate
min_x = None
"""
Entry where to type the minimum energy to simulate
"""
# Entry where to type the experimental resolution to simulate
res_entry = None
"""
Entry where to type the experimental resolution to simulate
"""
# Progress bar on the bottom of the interface to show the simulation progress
progressbar = None
"""
Progress bar on the bottom of the interface to show the simulation progress
"""



# --------------------------------------------------------- #
#                                                           #
#               WINDOW MANAGEMENT FUNCTIONS                 #
#                                                           #
# --------------------------------------------------------- #

# Function to destroy the window and free memory properly
def destroy(window):
    """
    Function to destroy the window and free memory properly
    
        Args:
            window: the window to be disposed of
        
        Returns:
            Nothing, the window is disposed of and the program continues
    """
    window.destroy()

# Function to deselect all selected transitions when exiting the simulation window
def _quit():
    """
    Private function to deselect all selected transitions when exiting the simulation window
        
        Args:
            
        
        Returns:
            Nothing, the transition dictionaries are reset and the simulation window is disposed of
    """
    original = satelite_var.get()

    satelite_var.set('Diagram')

    for transition in the_dictionary:
        if the_dictionary[transition]["selected_state"]:
            dict_updater(transition)

    satelite_var.set('Auger')

    for transition in the_aug_dictionary:
        if the_aug_dictionary[transition]["selected_state"]:
            dict_updater(transition)

    satelite_var.set(original)

    _sim.quit()  # stops mainloop
    _sim.destroy()  # this is necessary on Windows to prevent fatal Python Error: PyEval_RestoreThread: NULL tstate

# Function to deselect all selected transitions and restart the whole app
def restarter():
    """
    Private function to deselect all selected transitions and restart the whole application
        
        Args:
            
        
        Returns:
            Nothing, the transition dictionaries are reset and the tkinter windows are disposed of
    """
    original = satelite_var.get()

    satelite_var.set('Diagram')

    for transition in the_dictionary:
        if the_dictionary[transition]["selected_state"]:
            dict_updater(transition)

    satelite_var.set('Auger')

    for transition in the_aug_dictionary:
        if the_aug_dictionary[transition]["selected_state"]:
            dict_updater(transition)

    satelite_var.set(original)

    _sim.quit()  # stops mainloop
    _sim.destroy()
    _parent.destroy()
    main()  # this is necessary on Windows to prevent fatal Python Error: PyEval_RestoreThread: NULL tstate


# --------------------------------------------------------- #
#                                                           #
#                     KEYBIND FUNCTIONS                     #
#                                                           #
# --------------------------------------------------------- #

# Function to bind the default matplotlib hotkeys
def on_key_event(event):
    """
    Function to bind the default matplotlib hotkeys
        
        Args:
            event: which key event was triggered
        
        Returns:
            Nothing, the key event is passed to the default matplotlib key handler and the correct action is performed
    """
    print('you pressed %s' % event.key)
    key_press_handler(event, canvas, toolbar)

# Function to bind the simulation function to the enter key
def enter_function(event):
    """
    Function to bind the simulation function to the enter key
        
        Args:
            event: which key event was triggered
        
        Returns:
            Nothing, the simulation function is executed
    """
    utils.functions.plot_stick(_sim, _f, _a)



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
    text_T = drop_menu.get()
    # Update the dictionary for the transition
    dict_updater(text_T)
    
    if satelite_var.get() != 'Auger':
        # If the transition added to the selection
        if the_dictionary[text_T]["selected_state"]:
            transition_list.append(text_T)
        # If it was removed
        elif not the_dictionary[text_T]["selected_state"]:
            transition_list.remove(text_T)
    else:
        # Same for Auger
        if the_aug_dictionary[text_T]["selected_state"]:
            transition_list.append(text_T)
        elif not the_aug_dictionary[text_T]["selected_state"]:
            transition_list.remove(text_T)
    
    # Variable with the text to be shown in the interface with the selected transitions
    to_print = ', '.join(transition_list)
    
    # Set the interface label to the text
    label_text.set('Selected Transitions: ' + to_print)

# Function to properly reset the x limits in the interface (bound to the reset button)
def reset_limits():
    """
    Function to properly reset the x limits in the interface (bound to the reset button).
    """
    global number_points, x_max, x_min
    
    number_points.set(500)
    x_max.set('Auto')
    x_min.set('Auto')

# Update the selection state of a transition in the correct dictionary
def dict_updater(transition):
    """
    Function to update the selection state of a transition in the correct dictionary
        
        Args:
            transition: which transition to update
        
        Returns:
            Nothing, the transition is updated in the dictionaries
    """
    if satelite_var.get() != 'Auger':
        # Toggle the current state of the transition
        the_dictionary[transition]["selected_state"] = not the_dictionary[transition]["selected_state"]
    else:
        # Toggle the current state of the transition
        the_aug_dictionary[transition]["selected_state"] = not the_aug_dictionary[transition]["selected_state"]

# Function to update the transitions that can be selected from the dropdown, depending on if we want to simulate radiative or auger
def update_transition_dropdown():
    """
    Function to update the transitions that can be selected from the dropdown, depending on if we want to simulate radiative or auger
    """
    global transition_list
    
    if satelite_var.get() != 'Auger':
        # Update the values on the dropdown
        drop_menu['values'] = [transition for transition in the_dictionary]
        if not any([the_dictionary[transition]["selected_state"] for transition in the_dictionary]):
            # Reset the interface text
            label_text.set('Select a Transition: ')
            drop_menu.set('Transitions:')
            # Deselect transitions
            for transition in the_aug_dictionary:
                the_aug_dictionary[transition]["selected_state"] = False
    else:
        # Update the values on the dropdown
        drop_menu['values'] = [transition for transition in the_aug_dictionary]
        if not any([the_aug_dictionary[transition]["selected_state"] for transition in the_aug_dictionary]):
            # Reset the interface text
            label_text.set('Select a Transition: ')
            drop_menu.set('Transitions:')
            # Deselect transitions
            for transition in the_dictionary:
                the_dictionary[transition]["selected_state"] = False



# --------------------------------------------------------- #
#                                                           #
#      FUNCTIONS TO INITIALIZE AND CONFIGURE ELEMENTS       #
#                                                           #
# --------------------------------------------------------- #

# Initialize and configure the simulation plot
def configureSimuPlot():
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
    global _sim, _a, _f, _parent
    
    # ---------------------------------------------------------------------------------------------------------------
    # Start a new window for the simulation plot. We use TopLevel as we want this window to be the main interface
    sim = Toplevel(master=_parent)
    # Define the title
    sim.title("Spectrum Simulation")
    # Pack a panel into the window where we will place our canvas to plot the simulations. This way the window will properly resize
    panel_1 = PanedWindow(sim, orient=VERTICAL)
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
    _a = a
    _f = f
    _sim = sim
    
    return sim, panel_1, f, a, figure_frame, canvas

# Initialize and configure the areas where we will place the buttons, entries and labels for the simulation parameters
def configureButtonArea(sim, canvas):
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
    panel_2 = PanedWindow(sim, orient=VERTICAL)
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
    buttons_frame3 = Frame(full_frame, bd=1, relief=GROOVE)
    buttons_frame3.pack(fill=BOTH, expand=1)
    # Frame progress bar
    buttons_frame4 = Frame(full_frame)
    buttons_frame4.pack(fill=BOTH, expand=1)

    return panel_2, toolbar_frame, toolbar, full_frame, buttons_frame, buttons_frame2, buttons_frame3, buttons_frame4

# Setup the variables to hold the values of the interface entries
def setupVars(p):
    """
    Function to setup the variables to hold the values of the interface entries
        
        Args:
            p: tkinter parent object
        
        Returns:
            Nothing, all the variables initalized in the function are global module variables that can be used in other modules directly
    """
    # Use global to be able to initialize and change the values of the global interface variables
    global _parent, totalvar, yscale_log, xscale_log, autofitvar, normalizevar, loadvar, effic_var
    global exp_resolution, yoffset, energy_offset, number_points, x_max, x_min, progress_var, label_text
    global satelite_var, choice_var, type_var, exc_mech_var
    
    # setup the parent object to bind stuff to
    _parent = p
    
    # ---------------------------------------------------------------------------------------------------------------
    # Variable to know if we need to show the total y in the plot
    totalvar = StringVar(master = _parent)
    # Initialize it as false
    totalvar.set('No')
    # Variable to know if we need to make the y axis logarithmic or linear
    yscale_log = StringVar(master = _parent)
    # Initialize it as false
    yscale_log.set('No')
    # Variable to know if we need to make the x axis logarithmic or linear
    xscale_log = StringVar(master = _parent)
    # Initialize it as false
    xscale_log.set('No')
    # Variable to know if we need to perform an autofit of the simulation to experimental data
    autofitvar = StringVar(master = _parent)
    # Initialize it as false
    autofitvar.set('No')
    # Variable to know what normalization we need to perform (no normalization, normalize to unity, normalize to experimental maximum)
    normalizevar = StringVar(master = _parent)
    # Initialize to no normalization
    normalizevar.set('No')
    # Variable to know if we need to load an experimental spectrum and if so where it is located
    loadvar = StringVar(master = _parent)
    # Initialize to no file
    loadvar.set('No')
    # Variable to know if we need to load detector efficiency data and if so where it is located
    effic_var = StringVar(master = _parent)
    # Initialize to no file
    effic_var.set('No')

    # Variable to hold the experimental resolution value introduced in the interface
    exp_resolution = DoubleVar(master = _parent, value=1.0)
    # Variable to hold the experimental background offset value introduced in the interface
    yoffset = DoubleVar(master = _parent, value=0.0)
    # Variable to hold the experimental energy offset value introduced in the interface
    energy_offset = DoubleVar(master = _parent, value=0.0)
    # Variable to hold the number of points to simulate introduced in the interface
    number_points = IntVar(master = _parent, value=500)
    
    # Variable to hold the maximum x value to be simulated introduced in the interface
    x_max = StringVar(master = _parent)
    # Initialize to be calculated automatically
    x_max.set('Auto')
    # Variable to hold the minimum x value to be simulated introduced in the interface
    x_min = StringVar(master = _parent)
    # Initialize to be calculated automatically
    x_min.set('Auto')
    
    # Variable to hold the percentage of current progress to be displayed in the bottom of the interface
    progress_var = DoubleVar(master = _parent)
    
    # Variable to hold the text with the selected transitions that will be shown in the interface label
    label_text = StringVar(master = _parent)
    
    # Initialize the transition type to diagram
    satelite_var = StringVar(value='Diagram')
    # Initialize the simulation type to simulation
    choice_var = StringVar(value='Simulation')
    # Initialize the profile type to lorentzian
    type_var = StringVar(value='Lorentzian')
    # Initialize the exitation mechanism to empty as this is not yet implemented
    exc_mech_var = StringVar(value='')
 
# Setup the buttons in the button area
def setupButtonArea(buttons_frame, buttons_frame2, buttons_frame3, buttons_frame4):
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
    global trans_lable, drop_menu, points, max_x, min_x, res_entry, progressbar, transition_list
    
    # Antes de se selecionar alguma transição aparece isto
    label_text.set('Select a Transition: ')
    trans_lable = Label(buttons_frame, textvariable=label_text).grid(row=0, column=1)
    
    
    # DropList das transições, Labels e botão calculate a apresentar na janela
    drop_menu = ttk.Combobox(buttons_frame, value=[transition for transition in the_dictionary], height=5, width=10)
    drop_menu.set('Transitions:')
    drop_menu.bind("<<ComboboxSelected>>", selected)
    drop_menu.grid(row=0, column=0)
    
    # Min Max e Nº Pontos
    ttk.Label(buttons_frame2, text="Points").pack(side=LEFT)
    points = ttk.Entry(buttons_frame2, width=7, textvariable=number_points).pack(side=LEFT)
    ttk.Label(buttons_frame2, text="x Max").pack(side=LEFT)
    max_x = ttk.Entry(buttons_frame2, width=7, textvariable=x_max).pack(side=LEFT)
    ttk.Label(buttons_frame2, text="x Min").pack(side=LEFT)
    min_x = ttk.Entry(buttons_frame2, width=7, textvariable=x_min).pack(side=LEFT)
    ttk.Button(master=buttons_frame2, text="Reset", command=lambda: reset_limits()).pack(side=LEFT, padx=(30, 0))

    # Res, Offsets e Calculate
    # , font = ('Sans','10','bold'))  #definicoes botao "calculate"
    ttk.Style().configure('red/black.TButton', foreground='red', background='black')
    ttk.Button(master=buttons_frame3, text="Calculate", command=lambda: utils.functions.plot_stick(_sim, _f, _a), style='red/black.TButton').pack(side=RIGHT, padx=(30, 0))
    # yoffset
    res_entry = ttk.Entry(buttons_frame3, width=7, textvariable=yoffset).pack(side=RIGHT)
    ttk.Label(buttons_frame3, text="y Offset").pack(side=RIGHT)
    # En. Offset
    res_entry = ttk.Entry(buttons_frame3, width=7, textvariable=energy_offset).pack(side=RIGHT, padx=(0, 30))
    ttk.Label(buttons_frame3, text="En. offset (eV)").pack(side=RIGHT)
    # Energy Resolution
    ttk.Label(buttons_frame3, text="Experimental Resolution (eV)").pack(side=LEFT)
    res_entry = ttk.Entry(buttons_frame3, width=7, textvariable=exp_resolution).pack(side=LEFT)

    # Barra progresso
    progressbar = ttk.Progressbar(buttons_frame4, variable=progress_var, maximum=100)
    progressbar.pack(fill=X, expand=1)

# Setup the dropdown menus on the top toolbar
def setupMenus(CS_exists):
    """
    Function to setup the dropdown menus on the top toolbar
        
        Args:
            CS_exists: boolean if the charge states folder exists for the current element
        
        Returns:
            Nothing, we just setup the top toolbar and bind the necessary variables and functions to the interface elements
    """
    global totalvar, yscale_log, xscale_log, autofitvar, energy_offset, yoffset, normalizevar, satelite_var, choice_var, type_var, exc_mech_var, _sim
    global loadvar, effic_var
    
    # Initialize the menus
    my_menu = Menu(_sim)
    _sim.config(menu=my_menu)
    options_menu = Menu(my_menu, tearoff=0)
    stick_plot_menu = Menu(my_menu, tearoff=0)
    transition_type_menu = Menu(my_menu, tearoff=0)
    fit_type_menu = Menu(my_menu, tearoff=0)
    norm_menu = Menu(my_menu, tearoff=0)
    exc_mech_menu = Menu(my_menu, tearoff=0)
    
    # ---------------------------------------------------------------------------------------------------------------
    # Add the Options dropdown menu and the buttons bound to the corresponding variables and functions
    my_menu.add_cascade(label="Options", menu=options_menu)
    options_menu.add_checkbutton(label='Show Total Y', variable=totalvar, onvalue='Total', offvalue='No')
    options_menu.add_separator()
    options_menu.add_checkbutton(label='Log Scale Y Axis', variable=yscale_log, onvalue='Ylog', offvalue='No')
    options_menu.add_checkbutton(label='Log Scale X Axis', variable=xscale_log, onvalue='Xlog', offvalue='No')
    options_menu.add_separator()
    options_menu.add_command(label="Load Experimental Spectrum", command=lambda: load(loadvar))
    options_menu.add_checkbutton(label='Perform Autofit', variable=autofitvar, onvalue='Yes', offvalue='No')
    options_menu.add_separator()
    options_menu.add_checkbutton(label="Import Detector Efficiency", command=lambda: load_effic_file(effic_var))
    options_menu.add_separator()
    options_menu.add_command(label="Export Spectrum", command=lambda: write_to_xls(satelite_var.get(), xfinal, energy_offset.get(), yoffset.get(), exp_x, exp_y, residues_graph, radiative_files, auger_files, generalVars.label1, time_of_click))
    options_menu.add_separator()
    options_menu.add_command(label="Choose New Element", command=restarter)
    options_menu.add_command(label="Quit", command=_quit)
    
    # ---------------------------------------------------------------------------------------------------------------
    # Add the Spectrum type dropdown menu and the buttons bound to the corresponding variables and functions
    my_menu.add_cascade(label="Spectrum Type", menu=stick_plot_menu)
    stick_plot_menu.add_checkbutton(label='Stick', variable=choice_var, onvalue='Stick', offvalue='')
    stick_plot_menu.add_checkbutton(label='Simulation', variable=choice_var, onvalue='Simulation', offvalue='')
    stick_plot_menu.add_checkbutton(label='CS Mixture: Stick', variable=choice_var, onvalue='M_Stick', offvalue='', command=lambda: configureCSMix(), state='disabled')
    stick_plot_menu.add_checkbutton(label='CS Mixture: Simulation', variable=choice_var, onvalue='M_Simulation', offvalue='', command=lambda: configureCSMix(), state='disabled')
    # Active and deactivate the charge state mixture options if they exist
    if CS_exists:
        stick_plot_menu.entryconfigure(2, state=NORMAL)
        # Good TK documentation: https://tkdocs.com/tutorial/menus.html
        stick_plot_menu.entryconfigure(3, state=NORMAL)
    
    # ---------------------------------------------------------------------------------------------------------------
    # Add the Transition type dropdown menu and the buttons bound to the corresponding variables and functions
    my_menu.add_cascade(label="Transition Type", menu=transition_type_menu)
    transition_type_menu.add_checkbutton(label='Diagram', variable=satelite_var, onvalue='Diagram', offvalue='', command=update_transition_dropdown)
    transition_type_menu.add_checkbutton(label='Satellites', variable=satelite_var, onvalue='Satellites', offvalue='', command=update_transition_dropdown)
    transition_type_menu.add_checkbutton(label='Diagram + Satellites', variable=satelite_var, onvalue='Diagram + Satellites', offvalue='', command=update_transition_dropdown)
    transition_type_menu.add_checkbutton(label='Auger', variable=satelite_var, onvalue='Auger', offvalue='', command=update_transition_dropdown)
    
    # ---------------------------------------------------------------------------------------------------------------
    # Add the Fit type dropdown menu and the buttons bound to the corresponding variables and functions
    my_menu.add_cascade(label="Fit Type", menu=fit_type_menu)
    fit_type_menu.add_checkbutton(label='Voigt', variable=type_var, onvalue='Voigt', offvalue='')
    fit_type_menu.add_checkbutton(label='Lorentzian', variable=type_var, onvalue='Lorentzian', offvalue='')
    fit_type_menu.add_checkbutton(label='Gaussian', variable=type_var, onvalue='Gaussian', offvalue='')
    
    # ---------------------------------------------------------------------------------------------------------------
    # Add the Normalization options dropdown menu and the buttons bound to the corresponding variables and functions
    my_menu.add_cascade(label="Normalization Options", menu=norm_menu)
    norm_menu.add_checkbutton(label='to Experimental Maximum', variable=normalizevar, onvalue='ExpMax', offvalue='No')
    norm_menu.add_checkbutton(label='to Unity', variable=normalizevar, onvalue='One', offvalue='No')
    
    # ---------------------------------------------------------------------------------------------------------------
    # Add the Excitation mechanism dropdown menu and the buttons bound to the corresponding variables and functions (disables as it is not implemented)
    my_menu.add_cascade(label="Excitation Mechanism", menu=exc_mech_menu, state="disabled")
    exc_mech_menu.add_checkbutton(label='Nuclear Electron Capture', variable=exc_mech_var, onvalue='NEC', offvalue='')
    exc_mech_menu.add_checkbutton(label='Photoionization', variable=exc_mech_var, onvalue='PIon', offvalue='')
    exc_mech_menu.add_checkbutton(label='Electron Impact Ionization', variable=exc_mech_var, onvalue='EII', offvalue='')

# Initialize and configure the charge state mixture interface where we configure the mixture
def configureCSMix():
    """
    Function to initialize and configure the charge state mixture interface where we configure the mixture
    """
    mixer = Toplevel(_sim)
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
    if len(generalVars.PCS_radMixValues) == 0:
        # For each found charge state with radiative rates we initialize a set of slider, entry, label and variable to hold the value
        for cs in generalVars.radiative_files:
            if '+' in cs:
                generalVars.PCS_radMixValues.append(StringVar())
                CS_mixEntriesRad.append(ttk.Entry(mixer, textvariable=generalVars.PCS_radMixValues[-1], validate='key', validatecommand=check_num_wrapper))
                slidersRad.append(ttk.Scale(mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=generalVars.PCS_radMixValues[-1]))
                CS_labelsRad.append(ttk.Label(mixer, text=cs.split('intensity_')[1].split('.out')[0]))
                slidersRad[-1].set(0.0)
    else:
        # If we already initialized the variables we only need to reinitialize the interface elements
        i = 0
        for cs in generalVars.radiative_files:
            if '+' in cs:
                CS_mixEntriesRad.append(ttk.Entry(mixer, textvariable=generalVars.PCS_radMixValues[i], validate='key', validatecommand=check_num_wrapper))
                slidersRad.append(ttk.Scale(mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=generalVars.PCS_radMixValues[i]))
                CS_labelsRad.append(ttk.Label(mixer, text=cs.split('intensity_')[1].split('.out')[0]))

                i += 1

    # Same as the positive charge states. This split helps organize the interface when several different charge states are present
    if len(generalVars.NCS_radMixValues) == 0:
        for cs in generalVars.radiative_files:
            if '+' not in cs:
                generalVars.NCS_radMixValues.append(StringVar())
                CS_mixEntriesRad.append(ttk.Entry(mixer, textvariable=generalVars.NCS_radMixValues[-1], validate='key', validatecommand=check_num_wrapper))
                slidersRad.append(ttk.Scale(mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=generalVars.NCS_radMixValues[-1]))
                CS_labelsRad.append(ttk.Label(mixer, text=cs.split('intensity_')[1].split('.out')[0]))
                slidersRad[-1].set(0.0)
    else:
        i = 0
        for cs in generalVars.radiative_files:
            if '+' not in cs:
                CS_mixEntriesRad.append(ttk.Entry(mixer, textvariable=generalVars.NCS_radMixValues[i], validate='key', validatecommand=check_num_wrapper))
                slidersRad.append(ttk.Scale(mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=generalVars.NCS_radMixValues[i]))
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

        if len(generalVars.PCS_augMixValues) == 0:
            for cs in generalVars.auger_files:
                if '+' in cs:
                    generalVars.PCS_augMixValues.append(StringVar())
                    CS_mixEntriesAug.append(ttk.Entry(mixer, textvariable=generalVars.PCS_augMixValues[-1], validate='key', validatecommand=check_num_wrapper))
                    slidersAug.append(ttk.Scale(mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=generalVars.PCS_augMixValues[-1]))
                    CS_labelsAug.append(ttk.Label(mixer, text=cs.split('augrate_')[1].split('.out')[0]))
                    slidersAug[-1].set(0.0)
        else:
            i = 0
            for cs in generalVars.auger_files:
                if '+' in cs:
                    CS_mixEntriesAug.append(ttk.Entry(mixer, textvariable=generalVars.PCS_augMixValues[i], validate='key', validatecommand=check_num_wrapper))
                    slidersAug.append(ttk.Scale(mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=generalVars.PCS_augMixValues[i]))
                    CS_labelsAug.append(ttk.Label(mixer, text=cs.split('augrate_')[1].split('.out')[0]))

                    i += 1

        if len(generalVars.NCS_augMixValues) == 0:
            for cs in generalVars.auger_files:
                if '+' not in cs:
                    generalVars.NCS_augMixValues.append(StringVar())
                    CS_mixEntriesAug.append(ttk.Entry(mixer, textvariable=generalVars.NCS_augMixValues[-1], validate='key', validatecommand=check_num_wrapper))
                    slidersAug.append(ttk.Scale(mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=generalVars.NCS_augMixValues[-1]))
                    CS_labelsAug.append(ttk.Label(mixer, text=cs.split('augrate_')[1].split('.out')[0]))
                    slidersAug[-1].set(0.0)
        else:
            i = 0
            for cs in generalVars.auger_files:
                if '+' not in cs:
                    CS_mixEntriesAug.append(ttk.Entry(mixer, textvariable=generalVars.NCS_augMixValues[i], validate='key', validatecommand=check_num_wrapper))
                    slidersAug.append(ttk.Scale(mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=generalVars.NCS_augMixValues[i]))
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

    combined_x = []
    combined_y = []

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

    # Figura onde o gráfico vai ser desenhado
    # canvas para o gráfico do espectro
    f = Figure(figsize=(10, 5), dpi=100)
    # plt.style.use('ggplot') Estilo para os plots
    a = f.add_subplot(111)  # zona onde estara o gráfico
    a.set_xlabel('Temperature (K)')
    a.set_ylabel('Population')
    
    # ---------------------------------------------------------------------------------------------------------------
    # Frames onde se vão pôr a figura e os labels e botões e etc
    figure_frame = Frame(mixer, relief=GROOVE)  # frame para o gráfico

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
            if len(generalVars.PCS_radMixValues) > 0:
                i = 0
                for cs_file in generalVars.radiative_files:
                    if cs in cs_file:
                        # If the x value is outside interpolation range we just set it to 0
                        try:
                            generalVars.PCS_radMixValues[i].set(str(Ion_Population_Functions[cs](float(temperature.get()))))
                        except:
                            generalVars.PCS_radMixValues[i].set("0.0")

                        break

                    if '+' in cs:
                        i += 1

            if len(generalVars.NCS_radMixValues) > 0:
                i = 0
                for cs_file in generalVars.radiative_files:
                    if cs in cs_file:
                        # If the x value is outside interpolation range we just set it to 0
                        try:
                            generalVars.NCS_radMixValues[i].set(str(Ion_Population_Functions[cs](float(temperature.get()))))
                        except:
                            generalVars.NCS_radMixValues[i].set("0.0")

                        break

                    if '+' not in cs:
                        i += 1

        # If there is auger rate files make the same updates to the auger mix values
        if len(generalVars.auger_files) > 0:
            for cs in Ion_Population_Functions:
                if len(generalVars.PCS_augMixValues) > 0:
                    i = 0
                    for cs_file in generalVars.auger_files:
                        if cs in cs_file:
                            try:
                                generalVars.PCS_augMixValues[i].set(str(Ion_Population_Functions[cs](float(temperature.get()))))
                            except:
                                generalVars.PCS_augMixValues[i].set("0.0")

                            break

                        if '+' in cs:
                            i += 1

                if len(generalVars.NCS_augMixValues) > 0:
                    i = 0
                    for cs_file in generalVars.auger_files:
                        if cs in cs_file:
                            try:
                                generalVars.NCS_augMixValues[i].set(str(Ion_Population_Functions[cs](float(temperature.get()))))
                            except:
                                generalVars.NCS_augMixValues[i].set("0.0")

                            break

                        if '+' not in cs:
                            i += 1

    # Whenever we update the x value we also update the line and mix values
    temperature.trace_add("write", update_temp_line)
    # Add the slider and entry and position them in the grid
    temp_slider = ttk.Scale(mixer, orient=HORIZONTAL, length=200, from_=temperature_min, to=temperature_max, variable=temperature)
    temp_entry = ttk.Entry(mixer, textvariable=temperature, validate='key', validatecommand=check_num_wrapper)
    temp_slider.grid(column=0, row=fig_row + 1, columnspan=max(len(generalVars.radiative_files), len(generalVars.auger_files)) - 1, sticky=(W, E), padx=10, pady=20)
    temp_entry.grid(column=max(len(generalVars.radiative_files), len(generalVars.auger_files)) - 1, row=fig_row + 1, sticky=(W, E), padx=5)

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



# --------------------------------------------------------- #
#                                                           #
#           FUNCTIONS TO PLOT EXPERIMENTAL DATA             #
#                                                           #
# --------------------------------------------------------- #

# Function to setup the experimental plot when we load one and the residue plot
def setupExpPlot(f, load, element_name):
    """
    Function to setup the experimental plot when we load one and the residue plot
        
        Args:
            f: matplotlib figure object
            load: file path to the experimental spectrum selected
            element_name: name of the element we are simulating
        
        Returns:
            graph_area: new matplotlib plot configured to make space for the residue graph
            residues_graph: matplotlib plot for the residue data
            exp_spectrum: experimental spectrum data loaded from file
    """
    # Clear the plot
    f.clf()
    # Split the figure plot into two with the first having 3 times the height
    gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])
    # Add the first subplot to the figure
    graph_area = f.add_subplot(gs[0])
    
    # Set the logarithmic axes if needed
    if yscale_log.get() == 'Ylog':
        graph_area.set_yscale('log')
    if xscale_log.get() == 'Xlog':
        graph_area.set_xscale('log')
    # Add the name of the plot
    graph_area.legend(title=element_name)
    # Add the second subplot for the residues
    residues_graph = f.add_subplot(gs[1])
    # Set the axes labels
    residues_graph.set_xlabel('Energy (eV)')
    residues_graph.set_ylabel('Residues (arb. units)')
    
    # Read and load the experimental spectrum file
    exp_spectrum = loadExp(load)
    
    return graph_area, residues_graph, exp_spectrum

# Function to plot the experimental data and std deviation on the residue plot
def plotExp(graph_area, residues_graph, exp_x, exp_y, exp_sigma, normalize):
    """
    Function to plot the experimental data and std deviation on the residue plot
    
        Args:
            graph_area: new matplotlib plot configured to make space for the residue graph
            residues_graph: matplotlib plot for the residue data
            exp_x: energy values from the experimental spectrum
            exp_y: intensity values from the experimental spectrum
            exp_sigma: error values from the experimental spectrum
            normalize: normalization type selected in the interface
        
        Returns:
            Nothing, the function plots the normalized experimetnal spectrum in the simulation plot and the experimental errors in the residue plot
    """
    if normalize == 'One':
        # Plot dos dados experimentais normalizados à unidade
        graph_area.scatter(exp_x, exp_y / max(exp_y), marker='.', label='Exp.')
        # Plot do desvio padrão no gráfico dos resíduos (linha positiva)
        residues_graph.plot(exp_x, np.array(exp_sigma) / max(exp_y), 'k--')
        # Plot do desvio padrão no gráfico dos resíduos (linha negativa)
        residues_graph.plot(exp_x, -np.array(exp_sigma) / max(exp_y), 'k--')
    else:
        # Plot dos dados experimentais
        graph_area.scatter(exp_x, exp_y, marker='.', label='Exp.')
        # Plot do desvio padrão no gráfico dos resíduos (linha positiva)
        residues_graph.plot(exp_x, np.array(exp_sigma), 'k--')
        # Plot do desvio padrão no gráfico dos resíduos (linha negativa)
        residues_graph.plot(exp_x, -np.array(exp_sigma), 'k--')

    graph_area.legend()