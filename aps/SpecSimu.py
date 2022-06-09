#GUI message box for CS missmatch warning
from tkinter import messagebox

#OS Imports for files paths
import os

#Data Imports for variable management
import data.variables as generalVars

#File IO Imports
from utils.fileIO import readRadRates, readSatRates, readAugRates, readShakeWeights
from utils.fileIO import searchRadChargeStates, readRadChargeStates, searchAugChargeStates, readAugChargeStates, searchSatChargeStates, readSatChargeStates, readIonPop

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
    
    # Em versões anteriores recebiamos apenas o z do elemento, mas para poder ter acesso ao nome, recebe-se um vetor com nome e numero
    z = element[0]
    element_name = element[1]
    
    # Initialize the element name for the functions module
    utils.functions.element_name = element_name
    
    # Caminho do ficheiro na pasta com o nome igual ao numero atomico que tem as intensidades
    radrates_file = dir_path / str(z) / (str(z) + '-intensity.out')
    generalVars.lineradrates = readRadRates(radrates_file)

    # Caminho do ficheiro na pasta com o nome igual ao numero atomico que tem as satelites
    satellites_file = dir_path / str(z) / (str(z) + '-satinty.out')
    generalVars.linesatellites = readSatRates(satellites_file)

    # Caminho do ficheiro na pasta com o nome igual ao numero atomico que tem as satelites
    augrates_file = dir_path / str(z) / (str(z) + '-augrate.out')
    generalVars.lineauger = readAugRates(augrates_file)

    # Caminho do ficheiro na pasta com o nome igual ao numero atomico que tem as satelites
    shakeweights_file = dir_path / str(z) / (str(z) + '-shakeweights.out')
    generalVars.shakeweights, generalVars.label1 = readShakeWeights(shakeweights_file)

    # Flag para ativar ou desativar a opção no menu
    CS_exists = False
    Ionpop_exists = False
    # Verificar se existe a pasta com os varios CS para o atomo escolhido
    if os.path.isdir(dir_path / str(z) / 'Charge_States'):
        CS_exists = True
        
        #Search for the existing radiative files inside the charge states folder
        generalVars.radiative_files = searchRadChargeStates(dir_path, z)
        #load the raw data from the found files and the order in which they were loaded
        generalVars.lineradrates_PCS, generalVars.lineradrates_NCS, generalVars.rad_PCS, generalVars.rad_NCS = readRadChargeStates(generalVars.radiative_files, dir_path, z)

        #Search for the existing auger files inside the charge states folder
        generalVars.auger_files = searchAugChargeStates(dir_path, z)
        #load the raw data from the found files and the order in which they were loaded
        generalVars.lineaugrates_PCS, generalVars.lineaugrates_NCS, generalVars.aug_PCS, generalVars.aug_NCS = readAugChargeStates(generalVars.auger_files, dir_path, z)

        #Search for the existing satellite files inside the charge states folder
        generalVars.sat_files = searchSatChargeStates(dir_path, z)
        #load the raw data from the found files and the order in which they were loaded
        generalVars.linesatellites_PCS, generalVars.linesatellites_NCS, generalVars.sat_PCS, generalVars.sat_NCS = readSatChargeStates(generalVars.sat_files, dir_path, z)


        # Check for a missmatch in the read radiative and satellite files.
        #There should be 1 satellite for each radiative file if you want to simulate a full rad + sat spectrum
        #Otherwise, if you know what you are doing just ignore the warning
        if len(generalVars.linesatellites_NCS) != len(generalVars.lineradrates_NCS) or len(generalVars.linesatellites_PCS) != len(generalVars.lineradrates_PCS):
            messagebox.showwarning("Warning", "Missmatch of radiative and satellite files for Charge State mixture: " + str(len(generalVars.lineradrates_NCS) + len(generalVars.lineradrates_PCS)) + " radiative and " + str(len(generalVars.linesatellites_NCS) + len(generalVars.linesatellites_PCS)) + " satellite files found.")

        # Caminho do ficheiro na pasta com o nome igual ao numero atomico que tem as satelites
        ionpop_file = dir_path / str(z) / (str(z) + '-ionpop.out')
        # Check if the ion population data exists and load it
        generalVars.Ionpop_exists, generalVars.ionpopdata = readIonPop(ionpop_file)

    
    # ----------------------------------------------------------------------------------------------#
    #                                                                                               #
    #                                  INITIALIZE GUI ELEMENTS                                      #
    #                                                                                               #
    #-----------------------------------------------------------------------------------------------#
    
    #Setup the variables to use in the GUI entries
    guiVars.setupVars(parent)
    
    #Initialize the main simulation window, with the main plot inside
    sim, panel_1, f, a, figure_frame, canvas = configureSimuPlot()

    #Initialize the remaining panels containing the buttons and configuration entries for the simulation
    panel_2, toolbar_frame, toolbar, full_frame, buttons_frame, buttons_frame2, buttons_frame3, buttons_frame4 = configureButtonArea(sim, canvas)
    
    #Finish the button area setup and bind the variables to the GUI elements
    setupButtonArea(buttons_frame, buttons_frame2, buttons_frame3, buttons_frame4)
    
    #Bind the default matplotlib shortcuts
    canvas.mpl_connect('key_press_event', on_key_event)


    # Bind para correr a calculate quando se clica no enter
    sim.bind('<Return>', enter_function)
    
    #Setup the dropdown menus on the toolbar on the top of the window
    setupMenus(CS_exists)
    
    # ---------------------------------------------------------------------------------------------------------------
    #Initialize the main loop of the tk window (Enables the user interaction with the GUI)
    sim.mainloop()