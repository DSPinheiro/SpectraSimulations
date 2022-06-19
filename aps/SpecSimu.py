#GUI message box for CS missmatch warning
from tkinter import messagebox

#OS Imports for files paths
import os

#Data Imports for variable management
import data.variables as generalVars

#File IO Imports
from utils.fileIO import readRates, readShakeWeights
from utils.fileIO import searchChargeStates, readChargeStates, readIonPop

#Function Imports
import utils.functions

#GUI utils for interface setup
from utils.interface import on_key_event, enter_function
from utils.interface import configureSimuPlot, configureButtonArea, setupButtonArea, setupMenus
import utils.interface as guiVars


def simulateSpectra(dir_path, element, parent):
    # ----------------------------------------------------------------------------------------------#
    #                                                                                               #
    #                   INITIALIZE AND READ DATA FROM THE PREDEFINED FILES                          #
    #                                                                                               #
    #-----------------------------------------------------------------------------------------------#
    
    # Retrieve the z and name of the element to simulate
    z = element[0]
    element_name = element[1]
    
    # Initialize the element name for the functions module
    utils.functions.element_name = element_name
    
    # Path to the radiative rates file for this element
    radrates_file = dir_path / str(z) / (str(z) + '-intensity.out')
    # Read the rates file
    generalVars.lineradrates = readRates(radrates_file)

    # Path to the satellite rates file for this element
    satellites_file = dir_path / str(z) / (str(z) + '-satinty.out')
    # Read the rates file
    generalVars.linesatellites = readRates(satellites_file)

    # Path to the auger rates file for this element
    augrates_file = dir_path / str(z) / (str(z) + '-augrate.out')
    # Read the rates file
    generalVars.lineauger = readRates(augrates_file)

    # Path to the shake weigths file for this element
    shakeweights_file = dir_path / str(z) / (str(z) + '-shakeweights.out')
    # Read the shake weights file
    generalVars.shakeweights, generalVars.label1 = readShakeWeights(shakeweights_file)

    # Variable to active or deactivate the charge state simulation in the interface menu
    CS_exists = False
    
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
            messagebox.showwarning("Warning", "Missmatch of radiative and satellite files for Charge State mixture: " + str(len(generalVars.lineradrates_NCS) + len(generalVars.lineradrates_PCS)) + " radiative and " + str(len(generalVars.linesatellites_NCS) + len(generalVars.linesatellites_PCS)) + " satellite files found.")

        # Path to the ion population file file for this element
        ionpop_file = dir_path / str(z) / (str(z) + '-ionpop.out')
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

    # Initialize the remaining panels containing the buttons and configuration entries for the simulation
    panel_2, toolbar_frame, toolbar, full_frame, buttons_frame, buttons_frame2, buttons_frame3, buttons_frame4 = configureButtonArea(sim, canvas)
    
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