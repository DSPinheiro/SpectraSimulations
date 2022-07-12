"""
Module that implements the spectra simulations.
First we search and read all the required files to simulate the selected element, as well as all charge states if they exist.
Second we initialize the Tkinter interface. In this initialization all the functions that calculate and plot the simulated spectrum are bound to interface variables and buttons.
"""

# GUI message box for CS missmatch warning
from tkinter import messagebox

# OS Imports for files paths
import os

# Data Imports for variable management
import data.variables as generalVars

# File IO Imports
from utils.fileIO import readRates, readShakeWeights
from utils.fileIO import searchChargeStates, readChargeStates, readIonPop

# Function Imports
import utils.functions

# GUI utils for interface setup
from utils.interface import on_key_event, enter_function
from utils.interface import configureSimuPlot, configureButtonArea, setupButtonArea, setupMenus
import utils.interface as guiVars


def simulateSpectra(dir_path, element, parent):
    """
    Function to run the simulations interface

        Args:
            dir_path: full path to the location where the application is ran
            element: list with the [z value, element name] to simulate
            parent: parent tkinter window object where we will bind the new interface

        Returns:
            Nothing, we just setup the interface and all commands are bound and performed through the interface
    """
    # ----------------------------------------------------------------------------------------------#
    #                                                                                               #
    #                   INITIALIZE AND READ DATA FROM THE PREDEFINED FILES                          #
    #                                                                                               #
    #-----------------------------------------------------------------------------------------------#

    # Retrieve the z and name of the element to simulate
    z = element[0]
    """Variable with the z value of the element to simulate"""

    element_name = element[1]
    """Variable with the element name to simulate"""

    # Initialize the element name for the functions module
    utils.functions.element_name = element_name

    # Path to the radiative rates file for this element
    radrates_file = dir_path / str(z) / (str(z) + '-intensity.out')
    """Variable with the full path to the radiative rates file of this element"""

    # Read the rates file
    generalVars.lineradrates = readRates(radrates_file)

    # Path to the satellite rates file for this element
    satellites_file = dir_path / str(z) / (str(z) + '-satinty.out')
    """Variable with the full path to the satellite rates file of this element"""

    # Read the rates file
    generalVars.linesatellites = readRates(satellites_file)

    # Path to the auger rates file for this element
    augrates_file = dir_path / str(z) / (str(z) + '-augrate.out')
    """Variable with the full path to the auger rates file of this element"""

    # Read the rates file
    generalVars.lineauger = readRates(augrates_file)

    # Path to the shake weigths file for this element
    shakeweights_file = dir_path / str(z) / (str(z) + '-shakeweights.out')
    """Variable with the full path to the shake weights file of this element"""

    # Read the shake weights file
    generalVars.shakeweights, generalVars.label1 = readShakeWeights(shakeweights_file)

    # Variable to active or deactivate the charge state simulation in the interface menu
    CS_exists = False
    """Variable to control if this element has transition rates for different charge states"""

    # Check if the charge states folder exists in the element folder
    if os.path.isdir(dir_path / str(z) / 'Charge_States'):
        CS_exists = True

        # Search for the existing radiative files inside the charge states folder
        generalVars.radiative_files = searchChargeStates(dir_path, z, '-intensity_')
        # Load the raw data from the found files and the order in which they were loaded
        generalVars.lineradrates_PCS, generalVars.lineradrates_NCS, generalVars.rad_PCS, generalVars.rad_NCS = readChargeStates(generalVars.radiative_files, dir_path, z)

        # Search for the existing auger files inside the charge states folder
        generalVars.auger_files = searchChargeStates(dir_path, z, '-augrate_')
        # Load the raw data from the found files and the order in which they were loaded
        generalVars.lineaugrates_PCS, generalVars.lineaugrates_NCS, generalVars.aug_PCS, generalVars.aug_NCS = readChargeStates(generalVars.auger_files, dir_path, z)

        # Search for the existing satellite files inside the charge states folder
        generalVars.sat_files = searchChargeStates(dir_path, z, '-satinty_')
        # Load the raw data from the found files and the order in which they were loaded
        generalVars.linesatellites_PCS, generalVars.linesatellites_NCS, generalVars.sat_PCS, generalVars.sat_NCS = readChargeStates(generalVars.sat_files, dir_path, z)

        # Check for a missmatch in the read radiative and satellite files.
        # There should be 1 satellite for each radiative file if you want to simulate a full rad + sat spectrum
        # Otherwise, if you know what you are doing just ignore the warning
        if len(generalVars.linesatellites_NCS) != len(generalVars.lineradrates_NCS) or len(generalVars.linesatellites_PCS) != len(generalVars.lineradrates_PCS):
            messagebox.showwarning("Warning", "Missmatch of radiative and satellite files for Charge State mixture: " + str(len(generalVars.lineradrates_NCS) + len(
                generalVars.lineradrates_PCS)) + " radiative and " + str(len(generalVars.linesatellites_NCS) + len(generalVars.linesatellites_PCS)) + " satellite files found.")

        # Path to the ion population file file for this element
        ionpop_file = dir_path / str(z) / (str(z) + '-ionpop.out')
        """Variable with the full path to the ion population file of this element"""

        # Check if the ion population data exists and load it
        generalVars.Ionpop_exists, generalVars.ionpopdata = readIonPop(ionpop_file)

    # ----------------------------------------------------------------------------------------------#
    #                                                                                               #
    #                                  INITIALIZE GUI ELEMENTS                                      #
    #                                                                                               #
    #-----------------------------------------------------------------------------------------------#

    # Setup the variables to use in the GUI entries
    guiVars.setupVars(parent)

    # Initialize the main simulation window, with the main plot inside
    sim, panel_1, f, a, figure_frame, canvas = configureSimuPlot()
    """
    sim: variable to hold the tkinter simulation window object.
    panel_1: panel object that holds the matplotlib graph in the interface.
    f: matplotlib figure object where the graph will be displayed.
    a: matplotlib plot object where we can plot the data.
    figure_frame: frame that is placed inside the panel_1 object where the figure will be placed.
    canvas: tkinter object created from the matplotlib figure which is required to place the figure in the interface.
    """
    # Initialize the remaining panels containing the buttons and configuration entries for the simulation
    panel_2, toolbar_frame, toolbar, full_frame, buttons_frame, buttons_frame2, buttons_frame3, buttons_frame4 = configureButtonArea(sim, canvas)
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
    setupButtonArea(buttons_frame, buttons_frame2, buttons_frame3, buttons_frame4)

    # Bind the default matplotlib shortcuts
    canvas.mpl_connect('key_press_event', on_key_event)

    # Bind para correr a calculate quando se clica no enter
    sim.bind('<Return>', enter_function)

    # Setup the dropdown menus on the toolbar on the top of the window
    setupMenus(CS_exists)

    # ---------------------------------------------------------------------------------------------------------------
    # Initialize the main loop of the tk window (Enables the user interaction with the GUI)
    sim.mainloop()
