"""
Module with wrapper functions to initialize sets of interface elements.
"""

#GUI Imports
from tkinter import Tk
from tkinter import * # type: ignore

import data.variables as generalVars

import interface.variables as guiVars

from pathlib import Path

#GUI utils for interface setup
from interface.binds import on_key_event, enter_function
from interface.initializers import configureSimuPlot, configureButtonArea, \
                                    setupButtonArea, setupMenus, setupVars, \
                                    PTable, QuantPars

from interface.experimental import initialize_expElements



def SimulationWindow(dir_path: Path, root: Tk, CS_exists: bool = False, quantify: bool = False):
    # Setup the variables to use in the GUI entries
    setupVars(root)
    
    # Initialize the main simulation window, with the main plot inside
    panel_1, f, a, figure_frame, canvas = configureSimuPlot(root, quantify)
    """
    panel_1: panel object that holds the matplotlib graph in the interface.
    f: matplotlib figure object where the graph will be displayed.
    a: matplotlib plot object where we can plot the data.
    figure_frame: frame that is placed inside the panel_1 object where the figure will be placed.
    canvas: tkinter object created from the matplotlib figure which is required to place the figure in the interface.
    """
    # Initialize the remaining panels containing the buttons and configuration entries for the simulation
    panel_2, toolbar_frame, toolbar, full_frame, buttons_frame, buttons_frame2, buttons_frame3, buttons_frame4 = configureButtonArea(root, canvas)
    """
    panel_2: panel object that holds the controls placed below the graph
    toolbar_frame: frame that holds the toolbar buttons for the matplotlib plot
    toolbar: default toolbar buttons for the matplotlib plot
    full_frame: full frame for the button area to configure the simulations
    buttons_frame: frame for the transition dropdown
    buttons_frame2: frame for the simulation bounds and number of points
    buttons_frame3: frame for the yoffset, energy offset and calculate
    buttons_frame4: frame for the progress bar
    """
    # Finish the button area setup and bind the variables to the GUI elements
    setupButtonArea(dir_path, buttons_frame, buttons_frame2, buttons_frame3, buttons_frame4, quantify)
    
    # Bind the default matplotlib shortcuts
    canvas.mpl_connect('key_press_event', on_key_event)

    # Bind to run calculate when pressing enter
    root.bind('<Return>', func=str(enter_function))
    
    # Setup the dropdown menus on the toolbar on the top of the window
    setupMenus(root, CS_exists, quantify)
    
    if quantify:
        guiVars.graph_area, guiVars._residues_graph, _ = initialize_expElements(f, generalVars.currentSpectraList[0],
                               0.0, 0.0, 0.0, 0.0, 500, "Auto", "Auto", "Experimental", True)
        QuantPars(root, True)
        PTable(root, True)