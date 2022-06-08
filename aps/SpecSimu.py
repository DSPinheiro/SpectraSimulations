#GUI Imports
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename

#Matplotlib Imports for graph drawing and tkinter compatibility
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib import gridspec

#Math Imports for interpolation and fitting
from scipy.interpolate import interp1d
from lmfit import Minimizer, Parameters, report_fit, fit_report

#Data Handling Imports
import numpy as np
import csv

#OS Imports for files and dates
import os

#Data Imports for variable management
from data.variables import labeldict, the_dictionary, the_aug_dictionary
import data.variables as generalVars

#File IO Imports
from utils.fileIO import file_namer, write_to_xls, load, load_effic_file
from utils.fileIO import readRadRates, readSatRates, readAugRates, readShakeWeights
from utils.fileIO import searchRadChargeStates, readRadChargeStates, searchAugChargeStates, readAugChargeStates, searchSatChargeStates, readSatChargeStates, readIonPop

#Math Function Imports for calculating line profiles
import utils.functions

#GUI utils: destroy window
from utils.interface import destroy, restarter, _quit, on_key_event, enter_function, selected, reset_limits, dict_updater, update_transition_dropdown
from utils.interface import configureSimuPlot, configureButtonArea, setupButtonArea, setupMenus
import utils.interface as guiVars


def simulateSpectra(dir_path, element, parent):
    # Em versões anteriores recebiamos apenas o z do elemento, mas para poder ter acesso ao nome, recebe-se um vetor com nome e numero
    z = element[0]
    element_name = element[1]
    
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

    # Flag para ativar ou desativar a opção no menu (algures nas linhas ~1500)
    CS_exists = False
    Ionpop_exists = False
    # Verificar se existe a pasta com os varios CS para o atomo escolhido
    if os.path.isdir(dir_path / str(z) / 'Charge_States'):
        CS_exists = True
        
        generalVars.radiative_files = searchRadChargeStates(dir_path, z)
        generalVars.lineradrates_PCS, generalVars.lineradrates_NCS, generalVars.rad_PCS, generalVars.rad_NCS = readRadChargeStates(generalVars.radiative_files, dir_path, z)

        generalVars.auger_files = searchAugChargeStates(dir_path, z)
        generalVars.lineaugrates_PCS, generalVars.lineaugrates_NCS, generalVars.aug_PCS, generalVars.aug_NCS = readAugChargeStates(generalVars.auger_files, dir_path, z)

        generalVars.sat_files = searchSatChargeStates(dir_path, z)
        generalVars.linesatellites_PCS, generalVars.linesatellites_NCS, generalVars.sat_PCS, generalVars.sat_NCS = readSatChargeStates(generalVars.sat_files, dir_path, z)


        if len(generalVars.linesatellites_NCS) != len(generalVars.lineradrates_NCS) or len(generalVars.linesatellites_PCS) != len(generalVars.lineradrates_PCS):
            messagebox.showwarning("Error", "Missmatch of radiative and satellite files for Charge State mixture: " + str(len(generalVars.lineradrates_NCS) + len(generalVars.lineradrates_PCS)) + " radiative and " + str(len(generalVars.linesatellites_NCS) + len(generalVars.linesatellites_PCS)) + " satellite files found.")

        # Caminho do ficheiro na pasta com o nome igual ao numero atomico que tem as satelites
        ionpop_file = dir_path / str(z) / (str(z) + '-ionpop.out')
        generalVars.Ionpop_exists, generalVars.ionpopdata = readIonPop(ionpop_file)

    sim, panel_1, f, a, figure_frame, canvas = configureSimuPlot(parent)

    panel_2, toolbar_frame, toolbar, full_frame, buttons_frame, buttons_frame2, buttons_frame3, buttons_frame4 = configureButtonArea(sim, canvas)

    guiVars.setupVars(parent)
    
    setupButtonArea(buttons_frame, buttons_frame2, buttons_frame3, buttons_frame4)
    
    
    # NAO SEI BEM O QUE ISTO FAZ
    canvas.mpl_connect('key_press_event', on_key_event)


    # Botão para correr a calculate quando se clica no enter
    sim.bind('<Return>', enter_function)
    
    setupMenus(sim, CS_exists)
    
    # ---------------------------------------------------------------------------------------------------------------
    sim.mainloop()