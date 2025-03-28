"""
Module for file I/O functions.
Exporting to and importing from files is handled by these functions.
I/O in aps 1, 2 and 3 is not yet implemented in this module.
"""

#GUI Imports for warnings and interface to select files
from tkinter import messagebox
from tkinter.filedialog import askopenfilename, askopenfilenames, asksaveasfilename
from tkinter import StringVar

#Data import for variable management
from data import variables as generalVars
from data.variables import labeldict

import interface.variables as guiVars

#CSV reader import for reading and exporting data
import csv

#OS Imports for file paths
import os
from pathlib import Path

#OS import for timestamps
from datetime import datetime

from data.definitions import Line, processLine

from matplotlib.pyplot import Axes

from plotly.graph_objects import Figure

from data.clustering import determine_clusters, cluster


from typing import List

dir_path = Path(str(os.getcwd()) + '/')

# ----------------------------------------------------- #
#                                                       #
#                   EXPORT FUNCTIONS                    #
#                                                       #
# ----------------------------------------------------- #

# Function to generate the file names when saving data
def file_namer(simulation_or_fit: str, fit_time: datetime, extension: str):
    """
    Function to generate file names
        
        Args:
            simulation_or_fit: prefix for the type of file we want a name for
            fit_time: timestamp to identify the simulation/calculation that this file should correspond
            extension: file extention to be saved as
            
        Returns:
            file_name: final file name to be saved
    """
    # Convert the timestamp to formatted string
    dt_string = fit_time.strftime("%d%m%Y_%H%M%S")
    """
    Formated timestamp string
    """
    # Build the filename
    file_name = simulation_or_fit + '_from_' + dt_string + extension
    """
    Final file name
    """
    
    return file_name

# Function to save the simulation data into an excel file
def write_to_xls(type_t: str, enoffset: float, sat_enoffset: float, shkoff_enoffset: float, shkup_enoffset: float, beam_ener: float, beam_FWHM: float, y0: float, residues_graph: Axes):
    """
    Function to save the current simulation data into an excel file
        
        Args:
            type_t: type of transitions simulated (diagram, satellite, diagram + satellite, auger)
            enoffset: energy offset chosen in the simulation
            sat_enoffset: satellite energy offset chosen in the simulation
            shkoff_enoffset: shake-off energy offset chosen in the simulation
            shkup_enoffset: shake-up energy offset chosen in the simulation
            beam_ener: beam energy chosen in the simulation
            beam_FWHM: beam energy FWHM chosen in the simulation
            y0: intensity offset chosen in the simulation
            residues_graph: residues graph object from where we will extract the calculated residues
            
        Returns:
            Nothing, the file is saved and a message box is shown to the used
    """
    
    date_and_time = datetime.now()
    
    #Print the timestamp of the simulation
    print(date_and_time)
    
    #Generate filename to save the data
    file_title = file_namer("Simulation", date_and_time, ".csv")
    """
    Name of the file that is going to be saved. Please use the :func:`file_namer` function to generate names
    """
    
    # Initialize the header row of the excel file
    first_line = ['Energy (eV)']
    """
    Variable that holds the header row of the file
    """
    # Add an energy offset column if the offset is not 0
    if enoffset != 0:
        first_line += ['Energy Off (eV)']
    # Add a satellite energy offset column if the offset is not 0
    if sat_enoffset != 0:
        first_line += ['Satellite Energy Off (eV)']
    # Add a shake-off energy offset column if the offset is not 0
    if shkoff_enoffset != 0:
        first_line += ['Shake-off Energy Off (eV)']
    # Add a shake-up energy offset column if the offset is not 0
    if shkup_enoffset != 0:
        first_line += ['Shake-up Energy Off (eV)']

    # ---------------------------------------------------------------------------------------------------------------
    # Add the selected radiative and satellite transition labels into a seperate column
    if type_t != 'Auger':
        charge_states = generalVars.rad_PCS + generalVars.rad_NCS
        
        ploted_cs = []

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
                ploted_cs.append(cs)
        
        if len(ploted_cs) > 0:
            for cs_index, cs in enumerate(ploted_cs):
                for index, transition in enumerate(generalVars.the_dictionary):
                    if generalVars.the_dictionary[transition]["selected_state"]:
                        # Add the diagram transitions
                        if max(generalVars.yfinal[cs_index * len(generalVars.the_dictionary) + index]) != 0:
                            first_line += [cs + ' ' + generalVars.the_dictionary[transition]["readable_name"]]
                        # Add the satellite transitions
                        for l, m in enumerate(generalVars.yfinals[cs_index * len(generalVars.the_dictionary) + index]):
                            if max(m) != 0:
                                if l < len(generalVars.label1):
                                    first_line += [cs + ' ' + generalVars.the_dictionary[transition]["readable_name"] + '-' + labeldict[generalVars.label1[l]]]
                                else:
                                    first_line += [cs + ' ' + generalVars.the_dictionary[transition]["readable_name"] + '-' + labeldict[generalVars.label1[l - len(generalVars.label1)]] + " shake-up"]
        else:
            for index, transition in enumerate(generalVars.the_dictionary):
                if generalVars.the_dictionary[transition]["selected_state"]:
                    # Add the diagram transitions
                    if max(generalVars.yfinal[index]) != 0:
                        first_line += [generalVars.the_dictionary[transition]["readable_name"]]
                    # Add the satellite transitions
                    for l, m in enumerate(generalVars.yfinals[index]):
                        if max(m) != 0:
                            if l < len(generalVars.label1):
                                first_line += [generalVars.the_dictionary[transition]["readable_name"] + '-' + labeldict[generalVars.label1[l]]] # type: ignore
                            else:
                                first_line += [generalVars.the_dictionary[transition]["readable_name"] + '-' + labeldict[generalVars.label1[l - len(generalVars.label1)]] + " shake-up"] # type: ignore
    else:
        charge_states = generalVars.aug_PCS + generalVars.aug_NCS
        
        ploted_cs = []

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
                ploted_cs.append(cs)
        
        if len(ploted_cs) > 0:
            for cs_index, cs in enumerate(ploted_cs):
                for index, transition in enumerate(generalVars.the_aug_dictionary):
                    if generalVars.the_aug_dictionary[transition]["selected_state"]:
                        # Add the diagram transitions
                        if max(generalVars.yfinal[index]) != 0:
                            first_line += [cs + ' ' + generalVars.the_aug_dictionary[transition]["readable_name"]]
                        # Add the satellite transitions
                        for l, m in enumerate(generalVars.yfinals[index]):
                            if max(m) != 0:
                                if l < len(generalVars.label1):
                                    first_line += [cs + ' ' + generalVars.the_aug_dictionary[transition]["readable_name"] + '-' + labeldict[generalVars.label1[l]]]
                                else:
                                    first_line += [cs + ' ' + generalVars.the_aug_dictionary[transition]["readable_name"] + '-' + labeldict[generalVars.label1[l - len(generalVars.label1)]] + " shake-up"]
        else:
            for index, transition in enumerate(generalVars.the_aug_dictionary):
                if generalVars.the_aug_dictionary[transition]["selected_state"]:
                    # Add the diagram transitions
                    if max(generalVars.yfinal[index]) != 0:
                        first_line += [generalVars.the_aug_dictionary[transition]["readable_name"]]
                    # Add the satellite transitions
                    for l, m in enumerate(generalVars.yfinals[index]):
                        if max(m) != 0:
                            if l < len(generalVars.label1):
                                first_line += [generalVars.the_aug_dictionary[transition]["readable_name"] + '-' + labeldict[generalVars.label1[l]]] # type: ignore
                            else:
                                first_line += [generalVars.the_aug_dictionary[transition]["readable_name"] + '-' + labeldict[generalVars.label1[l - len(generalVars.label1)]] + " shake-up"] # type: ignore
    
    # ---------------------------------------------------------------------------------------------------------------
    # Add the column for the extra fitting functions total y
    if len(generalVars.extra_fitting_functions) > 0:
        for function in generalVars.extra_fitting_functions:
            first_line += [function]
        
        if y0 != 0:
            for function in generalVars.extra_fitting_functions:
                first_line += [function + ' Off']
    
    # ---------------------------------------------------------------------------------------------------------------
    # Add the column for the total y
    first_line += ['Total']
    
    # Add an intensity offset column if the offset is not 0
    if y0 != 0:
        first_line += ['Total Off']
    
    # Add 2 columns for the experimental spectrum if it is loaded
    if generalVars.exp_x != [] and generalVars.exp_y != [] and generalVars.exp_sigma != []:
        first_line += ['Exp Energy (eV)', 'Intensity', 'Error']

    # Add 4 columns for the residue data if it was calculated. An extra spacing column is added before the chi^2 value
    if residues_graph != None:
        first_line += ['Residues (arb. units)', 'std+', 'std-', '', 'red chi 2']

    # Add a spacing column and 2 columns for the charge state mixture weights if they were used in the simulation
    if len(guiVars.PCS_radMixValues) > 0 or len(guiVars.NCS_radMixValues) > 0 or len(guiVars.PCS_augMixValues) > 0 or len(guiVars.NCS_augMixValues) > 0:
        first_line += ['', 'Charge States', 'Percentage']

    # Now that we have the header line configured we can initialize a matrix to save in excel
    # If we have loaded an experimental spectrum we use the largest dimention between the x values grid and the experimental spectrum
    # Matrix = len(first_line) x max(len(xfinal), len(exp_x))
    if generalVars.exp_x != []:
        matrix = [[None for x in range(len(first_line))] for y in range(max(len(generalVars.xfinal), len(generalVars.exp_x)))]
        """
        Variable that holds the data to be saved in matrix form
        """
    else:
        matrix = [[None for x in range(len(first_line))] for y in range(len(generalVars.xfinal))]
    
    # ---------------------------------------------------------------------------------------------------------------
    # Variable to control which column we need to write to
    transition_columns = 1
    """
    Variable to control which column we need to write to
    """

    # Write the x and x + offset values in the matrix if the offset is not 0, otherwise write only the x
    for i, x in enumerate(generalVars.xfinal):
        matrix[i][0] = x # type: ignore
        if enoffset != 0:
            matrix[i][1] = x + enoffset # type: ignore
        if sat_enoffset != 0:
            matrix[i][2 - (enoffset == 0)] = x + enoffset + sat_enoffset # type: ignore
        if shkoff_enoffset != 0:
            matrix[i][3 - (enoffset == 0) - (sat_enoffset == 0)] = x + enoffset + shkoff_enoffset # type: ignore
        if shkup_enoffset != 0:
            matrix[i][4 - (enoffset == 0) - (sat_enoffset == 0) - (shkoff_enoffset == 0)] = x + enoffset + shkup_enoffset # type: ignore

    transition_columns += (enoffset != 0) + (sat_enoffset != 0) + (shkoff_enoffset != 0) + (shkup_enoffset != 0)
    
    # ---------------------------------------------------------------------------------------------------------------
    # Write the transition data in the respective columns
    for i, y in enumerate(generalVars.yfinal):
        # If we have data for this transition
        if max(y) != 0:
            # Write the values in the column
            for row in range(len(y)):
                matrix[row][transition_columns] = y[row] # type: ignore
            
            transition_columns += 1
        
        # Same for the satellite transitions but we require and extra loop
        if any([max(ys) for ys in generalVars.yfinals[i]]):
            for j, ys in enumerate(generalVars.yfinals[i]):
                if max(ys) != 0:
                    for row in range(len(y)):
                        matrix[row][transition_columns] = ys[row] # type: ignore
                    
                    transition_columns += 1
    
    # ------------------------------------------------------------------------------
    # Write the extra fitting components total y and y + offset values in the matrix 
    # if the offset is not 0, otherwise write only the total y
    if len(generalVars.yextras) > 0:
        if y0 != 0:
            for i, y in enumerate(generalVars.yextras):
                if len(y) > 0:
                # if max(y) != 0:
                    for row in range(len(y)):
                        matrix[row][transition_columns] = y[row] # type: ignore
                        matrix[row][transition_columns + 1] = y[row] + y0 # type: ignore
                
                    transition_columns += 1
        else:
            for i, y in enumerate(generalVars.yextras):
                if len(y) > 0:
                # if max(y) != 0:
                    for row in range(len(y)):
                        matrix[row][transition_columns] = y[row] # type: ignore

                    transition_columns += 1
    
    # ---------------------------------------------------------------------------------------------------------------
    # Write the total y and y + offset values in the matrix if the offset is not 0, otherwise write only the total y
    if y0 != 0:
        for j in range(len(generalVars.ytot)):
            matrix[j][transition_columns] = generalVars.ytot[j] # type: ignore
            matrix[j][transition_columns + 1] = generalVars.ytot[j] + y0 # type: ignore
    
        transition_columns += 1
    else:
        for j in range(len(generalVars.ytot)):
            matrix[j][transition_columns] = generalVars.ytot[j] # type: ignore

    transition_columns += 1
    
    # ---------------------------------------------------------------------------------------------------------------
    # Write the experimental spectrum values
    if generalVars.exp_x == [] and generalVars.exp_y == []:
        print("No experimental spectrum loaded. Skipping...")
    else:
        for i in range(len(generalVars.exp_x)):
            matrix[i][transition_columns] = generalVars.exp_x[i] # type: ignore
            matrix[i][transition_columns + 1] = generalVars.exp_y[i] # type: ignore
            matrix[i][transition_columns + 2] = generalVars.exp_sigma[i] # type: ignore

        transition_columns += 3
    
    # ---------------------------------------------------------------------------------------------------------------
    # Retrieve the residue data from the graph object
    if residues_graph == None:
        print("No residues calculated. Skipping...")
    else:
        # Retrieve the data from the graph
        lines = residues_graph.get_lines()
        """
        Lines from the residue graph
        """
        sigp, sigm, res = lines[0].get_ydata(), lines[1].get_ydata(), lines[2].get_ydata()
        """
        sigp: positive sigma (std. deviation) values for the residues calculate
        sigm: negative sigma (std. deviation) values for the residues calculate
        res: residue values calculated
        """
        # Write the data in the respective columns
        for i in range(len(generalVars.exp_x)):
            matrix[i][transition_columns] = res[i] # type: ignore
            matrix[i][transition_columns + 1] = sigp[i] # type: ignore
            matrix[i][transition_columns + 2] = sigm[i] # type: ignore

        matrix[0][transition_columns + 4] = generalVars.chi_sqrd # type: ignore
        
        if beam_ener != 0:
            matrix[1][transition_columns + 4] = 'Beam Energy (eV)' # type: ignore
            matrix[2][transition_columns + 4] = beam_ener # type: ignore
            matrix[3][transition_columns + 4] = 'Beam Energy FWHM (eV)' # type: ignore
            matrix[4][transition_columns + 4] = beam_FWHM # type: ignore

        transition_columns += 5
    
    # ---------------------------------------------------------------------------------------------------------------
    # Write the mix values in the matrix
    if type_t != 'Auger':
        if len(guiVars.PCS_radMixValues) > 0 or len(guiVars.NCS_radMixValues) > 0:
            idx_p = 0
            idx_n = 0
            # Loop all loaded charge states
            for i, cs in enumerate(generalVars.radiative_files):
                # Write the charge state label
                matrix[i][transition_columns + 1] = cs.split('-intensity_')[1].split('.out')[0] + '_' # type: ignore

                # As the mixture values are split by positive and negative charge states we need to diferenciate them
                if '+' in cs:
                    matrix[i][transition_columns + 2] = generalVars.PCS_radMixValues[idx_p].get() # type: ignore
                    idx_p += 1
                else:
                    matrix[i][transition_columns + 2] = generalVars.NCS_radMixValues[idx_n].get() # type: ignore
                    idx_n += 1
    else:
        if len(guiVars.PCS_augMixValues) > 0 or len(guiVars.NCS_augMixValues) > 0:
            idx_p = 0
            idx_n = 0

            # Add an extra label to know this mixture is for an auger simulation
            matrix[1][transition_columns + 1] = "Auger Mix Values" # type: ignore

            # Loop all loaded charge states
            for i, cs in enumerate(generalVars.auger_files):
                matrix[i + 1][transition_columns + 1] = cs.split('-augrate_')[1].split('.out')[0] + '_' # type: ignore

                # As the mixture values are split by positive and negative charge states we need to diferenciate them
                if '+' in cs:
                    matrix[i + 1][transition_columns + 2] = generalVars.PCS_augMixValues[idx_p].get() # type: ignore
                    idx_p += 1
                else:
                    matrix[i + 1][transition_columns + 2] = generalVars.NCS_augMixValues[idx_n].get() # type: ignore
                    idx_n += 1
    
    # ---------------------------------------------------------------------------------------------------------------
    # Add the header row
    matrix = [first_line] + matrix
    
    # ---------------------------------------------------------------------------------------------------------------
    # Print the matrix values in the console to debug
    # for row in matrix:
    #     print(' '.join(map(str, row)))
    
    # ---------------------------------------------------------------------------------------------------------------
    # Write the matrix in the file. First open as write to create the file, then we append the remaining lines
    for i, item in enumerate(matrix):
        if i == 0:
            with open(file_title, 'w', newline='') as csvfile:
                w1 = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                w1.writerow(matrix[i])
        else:
            with open(file_title, 'a', newline='') as csvfile2:
                w1 = csv.writer(csvfile2, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                w1.writerow(matrix[i])
    
    # Prompt that the data was saved
    messagebox.showinfo("File Saved", "Data file has been saved")

# Function to save the fit report to file
def exportFit(time_of_click: datetime, report: str):
    """
    Function export the fit parameters calculated
        
        Args:
            time_of_click: timestamp of the fit
            report: the report to be saved
            
        Returns:
            Nothing, the data is saved to file and printed on the console
    """
    with open(file_namer("Fit", time_of_click, ".txt"), 'w') as file:
        file.write(report)
        file.write("\nTotal theoretical intensity multiplier for the amplitude parameters: " + str(max(generalVars.ytot)))
        print(report)
        print("\nTotal theoretical intensity multiplier for the amplitude parameters: " + str(max(generalVars.ytot)))

def saveMatrixHtml(fig: Figure, title: str):
    if not os.path.isdir(dir_path / str(generalVars.Z) / "Analysis"):
        os.mkdir(dir_path / str(generalVars.Z) / "Analysis")
    
    fig.write_html(dir_path / str(generalVars.Z) / "Analysis" / title)
    
    #with open(dir_path / str(generalVars.Z) / "Analysis" / title, "r") as html:
    #    code = ''.join(html.readlines())
    
    return "file:///" + str(dir_path).replace("\\", "/") + "/" + str(generalVars.Z) + "/Analysis/" + title

# ----------------------------------------------------- #
#                                                       #
#       LOAD EXPERIMENTAL AND EFFICIENCY DATA           #
#                                                       #
# ----------------------------------------------------- #

# Function to request the file with the experimental spectrum and save the file path
def load(loadvar = None, set: bool = True, title: str = "Choose an Experimental Spectrum File"):
    """
    Function to request the file with the experimental spectrum
        
        Args:
            loadvar: variable where we save the chosen file path
            
        Returns:
            Nothing, the file path is save in the variable
    """
    # Lauch a file picker interface
    if set:
        fnames = askopenfilename(title=title, filetypes=(("Spectra files", "*.csv *.txt"), ("All files", "*.*")))
    else:
        fnames = askopenfilenames(title=title, filetypes=(("Spectra files", "*.csv *.txt"), ("All files", "*.*")))
        
        if type(fnames) == tuple:
            finalNames = []
            for name in fnames:
                try:
                    spectra = loadExp(name)
                    if len(spectra[0]) >= 2:
                        finalNames.append(name)
                except:
                    messagebox.showwarning("Formating error", "Experimental spectrum '" + name + "' could not be loaded due to incorrect formatting.")
    
    if fnames != '':
        # Save the path to the loadvar variable
        if set:
            loadvar.set(fnames) # type: ignore
        else:
            return finalNames
    else:
        return ''


def add_spectra(title: str = "Choose an Experimental Spectrum File"):
    # Lauch a file picker interface
    fnames = askopenfilenames(title=title, filetypes=(("Spectra files", "*.csv *.txt"), ("All files", "*.*")))
    
    for name in fnames:
        if name not in generalVars.currentSpectraList:
            try:
                spectra = loadExp(name)
                if len(spectra[0]) >= 2:
                    generalVars.currentSpectraList.append(name)
            except:
                messagebox.showwarning("Formating error", "Experimental spectrum '" + name + "' could not be loaded due to incorrect formatting.")

    guiVars.drop_spectra['values'] = [spectra.split("/")[-1] for spectra in generalVars.currentSpectraList] # type: ignore


# Function to request the file with the detector efficiency and save the file path
def load_effic_file(effic_var: StringVar):
    """
    Function to request the file with the detector efficiency
        
        Args:
            effic_var: variable where we save the chosen file path
            
        Returns:
            Nothing, the file path is save in the variable
    """
    # Lauch a file picker interface
    effic_fname = askopenfilename(filetypes=(("Efficiency files", "*.csv"), ("All files", "*.*")))
    # Save the path to the effic_var variable
    effic_var.set(effic_fname)

# Function to read the experimental spectrum as csv and return it as a list
def loadExp(file: str):
    """
    Function to read the experimental spectrum as csv
        
        Args:
            file: file path of the experimental spectrum
            
        Returns:
            List with the data still in string format
    """
    return list(csv.reader(open(file, 'r', encoding='utf-8-sig')))

# Function to read the detector efficiency as csv and return it as a list
def loadEfficiency(file: str):
    """
    Function to read the detector efficiency as csv
        
        Args:
            file: file path of the efficiency data
            
        Returns:
            List with the data still in string format
    """
    return list(csv.reader(open(file, 'r')))


# ----------------------------------------------------- #
#                                                       #
#                  READ RATES FILES                     #
#                                                       #
# ----------------------------------------------------- #

# Read the rates file and return a list with the data
def readRates(rates_file: Path):
    """
    Function to read the rates file
        
        Args:
            rates_file: file path of the rates file
            
        Returns:
            linerates: list with the data in Line objects
    """
    try:
        with open(rates_file, 'r') as rates:
            # Write the lines into a list
            return [processLine(line=x) for x in rates.readlines()[3:]]

    except FileNotFoundError:
        messagebox.showwarning("Error", "Rates File is not Avaliable: " + str(rates_file))
        return []

# Read the ionization energies file and return a list with the data
def readIonizationEnergies(ioniz_file: Path):
    """
    Function to read the ionization energies file
        
        Args:
            ioniz_file: file path of the ionization energies file
            
        Returns:
            ionizations: list with the ionization energies still in string format
    """
    try:
        with open(ioniz_file, 'r') as ioniz:
            # Write the lines into a list
            return [processLine(line=x) for x in ioniz.readlines()[3:]]
            
    except FileNotFoundError:
        messagebox.showwarning("Error", "Ionization Energies File is not Avaliable: " + str(ioniz_file))
        return []

# Read the widths file and return a list with the data
def readWidths(widthsfile: Path):
    """
    Function to read the diagram widths file
        
        Args:
            widthsfile: file path of the widths file
            
        Returns:
            widths: list with the diagram widths still in string format
    """
    try:
        with open(widthsfile, 'r') as widths:
            # Write the lines into a list
            return [processLine(line=x) for x in widths.readlines()[3:]]
            
    except FileNotFoundError:
        messagebox.showwarning("Error", "Widths File is not Avaliable: " + str(widthsfile))
        return []


# Read the mean radius file and return a list with the data
def readMeanR(meanR_file: Path):
    """
    Function to read the mean radius file
        
        Args:
            meanR_file: file path of the satellite widths file
            
        Returns:
            meanRs: list with the mean radius still in string format
    """
    try:
        with open(meanR_file, 'r') as means:
            # Write the lines into a list
            meanRs = [x.strip('\n').split() for x in means.readlines()]
            # Remove empty strings from possible uneven formating
            meanRs = list(filter(None, meanRs))
            # Delete the header rows
            del meanRs[0:2]
            
            generalVars.meanR_exists = True
            
            return meanRs
    except FileNotFoundError:
        generalVars.meanR_exists = False
        messagebox.showwarning("Error", "Mean Radius File is not Avaliable: " + str(meanR_file))
        return [['']]


# Read the shake up/off file and return a list with the data
def readShake(shake_file: Path):
    """
    Function to read the shake-up/off file
        
        Args:
            shake_file: file path of the shake file
            
        Returns:
            shake_prob: list with the shake probabilities still in string format
    """
    try:
        with open(shake_file, 'r') as shake:
            # Write the lines into a list
            shake_prob = [x.strip('\n').split() for x in shake.readlines()]
            # Remove empty strings from possible uneven formating
            shake_prob = list(filter(None, shake_prob))
            # Delete the header rows
            del shake_prob[0:2]
            
            label1 = list(set([shake[1] for shake in shake_prob]))
            
            return shake_prob, label1
    except FileNotFoundError:
        messagebox.showwarning("Error", "Shake Probabilities File is not Avaliable: " + str(shake_file))
        
        return [['']], ['']

# ----------------------------------------------------- #
#                                                       #
#    READ RATES AND IONPOP FILES FOR CHARGE STATES      #
#                                                       #
# ----------------------------------------------------- #

# Search the Charge_States folder for all "identifyer" rate files and return a list with their names
def searchChargeStates(dir_path: Path, z: int, identifyer: str):
    """
    Function to search the Charge_States folder for all "identifyer" rate files
        
        Args:
            dir_path: full path of the simulation
            z: z value of the element to simulate
            identifyer: identifyer of the rate files we want to search (intensity, satinty, augrate)
            
        Returns:
            files: file names found in the Charge_States folder with the identifyer
    """
    files: List[str] = []
    # Loop all files in the folder
    for f in os.listdir(dir_path / str(z) / 'Charge_States'):
        # If the name format matches a radiative rates files then append it to the list
        if os.path.isfile(os.path.join(dir_path / str(z) / 'Charge_States', f)) and identifyer in f:
            files.append(f)
    
    return files

# Read the rates files in the files list and return a list with the data split by positive and negative charge states.
# Also return a list with the order in which the data was stored in the lists
def readChargeStates(files: List[str], dir_path: Path, z: int):
    """
    Function to read the rates files in the files list
        
        Args:
            files: list of the file names to read
            dir_path: full path of the simulation
            z: z value of the element to simulate
        
        Returns:
            linerates_PCS: lists of the rates read for each positive charge state
            linerates_NCS: lists of the rates read for each negative charge state
            PCS: list with the order that the rates for the positive charge states were read
            NCS: list with the order that the rates for the negative charge states were read
    """
    linerates_PCS: List[List[Line]] = []
    linerates_NCS: List[List[Line]] = []

    PCS: List[str] = []
    NCS: List[str] = []

    # Loop for each charge state file
    for file in files:
        # Path to the selected file
        tmp_file = dir_path / str(z) / 'Charge_States' / file
        try:
            with open(tmp_file, 'r') as rates:
                if '+' in file:
                    # Write the lines into a list and append it to the total rates for all charge states
                    linerates_PCS.append([processLine(line=x) for x in rates.readlines()[3:]])
                    
                    # Append the charge state value to identify the rates we just appended
                    PCS.append('+' + file.split('+')[1].split('.')[0])
                else:
                    # Write the lines into a list and append it to the total rates for all charge states
                    linerates_NCS.append([processLine(line=x) for x in rates.readlines()[3:]])
                    
                    # Append the charge state value to identify the rates we just appended
                    NCS.append('-' + file.split('-')[1].split('.')[0])
        except FileNotFoundError:
            messagebox.showwarning("Error", "Charge State File is not Avaliable: " + file)
    
    return linerates_PCS, linerates_NCS, PCS, NCS

# Read the ion population file and return a list with the raw data
def readIonPop(ionpop_file: Path):
    """
    Function to read the ion population file
        
        Args:
            ionpop_file: full path of the ion population file
            
        Returns:
            True: if the ion population file could be open
            ionpopdata: list with the ion population data
    """
    try:
        with open(ionpop_file, 'r') as ionpop:
            # Write the lines into a list
            ionpopdata = [x.strip('\n').split() for x in ionpop.readlines()]
            # Remove empty strings from possible uneven formating
            ionpopdata = list(filter(None, ionpopdata))
        
        return True, ionpopdata
    except FileNotFoundError:
        messagebox.showwarning("Error", "Ion Population File is not Avaliable")
        
        return False, [['']]


# ----------------------------------------------------- #
#                                                       #
#           READ RATES FILES FOR EXCITATIONS            #
#                                                       #
# ----------------------------------------------------- #

# Search the Excitations folder for all "identifyer" rate files and return a list with their names
def searchExcitations(dir_path: Path, z: int, identifyer: str):
    """
    Function to search the Excitations folder for all "identifyer" rate files
        
        Args:
            dir_path: full path of the simulation
            z: z value of the element to simulate
            identifyer: identifyer of the rate files we want to search (intensity, satinty, augrate)
            
        Returns:
            files: file names found in the Excitations folder with the identifyer
    """
    files: List[str] = []
    # Loop all files in the folder
    for f in os.listdir(dir_path / str(z) / 'Excitations'):
        # If the name format matches a rates files then append it to the list
        if os.path.isfile(os.path.join(dir_path / str(z) / 'Excitations', f)) and identifyer in f:
            files.append(f)
    
    return files


# Read the rates files in the files list and return a list with the data split by positive and negative charge states.
# Also return a list with the order in which the data was stored in the lists
def readExcitations(files: List[str], dir_path: Path, z: int):
    """
    Function to read the rates files in the files list
        
        Args:
            files: list of the file names to read
            dir_path: full path of the simulation
            z: z value of the element to simulate
        
        Returns:
            linerates: lists of the rates read
            EXC: list with the order that the rates for the excitations were read
    """
    linerates: List[List[Line]] = []
    
    EXC: List[str] = []
    
    # Loop for each charge state file
    for file in files:
        # Path to the selected file
        tmp_file = dir_path / str(z) / 'Excitations' / file
        try:
            with open(tmp_file, 'r') as rates:
                # Write the lines into a list and append it to the total rates for all charge states
                linerates.append([processLine(line=x) for x in rates.readlines()[3:]])
                
                # Append the charge state value to identify the rates we just appended
                EXC.append(file.split('_', 1)[-1].split('.')[0])
        except FileNotFoundError:
            messagebox.showwarning("Error", "Excitation File is not Avaliable: " + file)
    
    return linerates, EXC



# ----------------------------------------------------- #
#                                                       #
#        READ DATABASE AND CONFIGURATION FILES          #
#                                                       #
# ----------------------------------------------------- #

def findElements(dir_path: Path):
    Zs: List[int] = []
    
    for dir in os.walk(dir_path):
        for d in dir[1]:
            try:
                Zs.append(int(d))
            except ValueError:
                pass
        
        break
    
    return Zs

# Read the ELAM database file and return the list with the data for the selected element
def readELAMelement(ELAM_file: Path, z: int):
    """
    Function to read the ELAM database file
        
        Args:
            ELAM_file: file path of the ELAM database file
            z: z value of the element to find in the database
            
        Returns:
            ELAMelement: list with the ELAM data for the z
    """
    
    try:
        with open(ELAM_file, 'r') as ELAM:
            ELAMelement = []
            found = False
            
            symbol = [elem[3].strip() for elem in generalVars.per_table if elem[0] == z][0] # type: ignore
            
            for x in ELAM.readlines():
                if 'EndElement' in x and found:
                    break
                if 'Element ' + symbol in x or found:
                    found = True
                    ELAMelement.append(x.strip('\n'))
            
            generalVars.ELAM_exists = True
            
            return ELAMelement
    except FileNotFoundError:
        generalVars.ELAM_exists = False
        
        messagebox.showwarning("Error", "ELAM database File is not Avaliable: " + str(ELAM_file))
    

def readNISTXrayLines(NIST_file: Path, do_cluster: bool = False):
    """
    Function to read the Full NIST Xray lines database file
        
        Args:
            NIST_file: file path of the ELAM database file
                    
        Returns:
            lines: list with the NIST data for the XRay lines
    """
    try:
        with open(NIST_file, 'r') as NIST:
            lines: List[List[str]] = []
            
            NIST.readline()
            NIST.readline()
            NIST.readline()
            NIST.readline()
            NIST.readline()
            NIST.readline()
            
            for x in NIST.readlines():
                lines.append(list(filter(None, x.strip('\n').split("\t"))))
            
            for line in lines:
                try:
                    tmp = int(line[1])
                except ValueError:
                    line.insert(1, '0')
            
            generalVars.NIST_exists = True
            
            if do_cluster:
                elements = list(set([line[0] for line in lines]))
                
                for i, element in enumerate(elements):
                    print(generalVars.clearLine + "Clustering element " + str(i + 1) + " of " + str(len(elements)), end="")
                    filtered = []
                    for line in lines:
                        if line[0] == element:
                            filtered.append(line)
                    
                    k = determine_clusters(list(set([float(line[3]) for line in filtered])), min(len(list(set([float(line[3]) for line in filtered]))) - 1, 10))
                    generalVars.NIST_ROIS[element] = cluster(list(set([float(line[3]) for line in filtered])), k)
                
            return lines
    except FileNotFoundError:
        generalVars.NIST_exists = False
        
        messagebox.showwarning("Error", "NIST database File is not Avaliable: " + str(NIST_file))


def readNISTClusterLines(NIST_file: Path):
    try:
        with open(NIST_file, 'r') as NIST:
            lines: List[List[str]] = []
            
            for x in NIST.readlines():
                lines.append(list(filter(None, x.strip('\n').split("\t"))))
            
            for line in lines:
                rois = line[1:]
                generalVars.NIST_ROIS[line[0]] = [(float(roi.split(",")[0]), float(roi.split(",")[1])) for roi in rois]
            
            generalVars.NIST_clusters_exists = True
            
            return lines
    except FileNotFoundError:
        generalVars.NIST_clusters_exists = False
        
        messagebox.showwarning("Error", "NIST database File is not Avaliable: " + str(NIST_file))


def loadQuantConfigs(config_dir: Path):
    configs: List[str] = []
    
    if os.path.isdir(config_dir):
        for dir in os.walk(config_dir):
            for file in dir[2]:
                if ".mqc" in file:
                    configs.append(str(config_dir) + "\\" + file)
        
        return configs
    else:
        return []


def save_quantConfig():
    fname = asksaveasfilename(title="Save as", filetypes=(("Quantification Files", "*.mqc"), ("All files", "*.*")))
    
    with open(fname, "w") as conf:
        conf.write("Alpha Parameters\n")
        for el in generalVars.currentQuantConfig:
            conf.write(f'{el}\t{generalVars.currentQuantConfig[el]}\n')
        
        conf.write("Spectra Standard Targets\n")
        for spectra in generalVars.currentQuantConfigSpectra:
            conf.write(spectra + "\n")
            for el in generalVars.currentQuantConfigSpectra[spectra]:
                target = generalVars.currentQuantConfigSpectra[spectra][el]
                conf.write(f'{el}\t{target[0]}\t{target[1]}\t{target[2]}\t{generalVars.weightUnits[target[3]]}\n')

def read_quantConfig(fname: str):
    alphas = False
    targets = False
    spectra = ""
    
    with open(fname, "r") as conf:
        for line in conf:
            if "Alpha Parameters" in line:
                alphas = True
                targets = False
                continue
            elif "Spectra Standard Targets" in line:
                alphas = False
                targets = True
                continue
            
            vals = line.split("\t")
            
            if alphas:
                generalVars.currentQuantConfig[vals[0]] = float(vals[1])
            elif targets:
                if len(vals) == 5:
                    generalVars.currentQuantConfigSpectra[spectra][vals[0]] = (float(vals[1]), float(vals[2]), float(vals[3]), generalVars.weightUnits.index(vals[4].strip()))
                else:
                    spectra = line.strip()
                    generalVars.currentQuantConfigSpectra[spectra] = {}

def load_quantConfig():
    fname = askopenfilename(title="Load Quantification Configuration", filetypes=(("Quantification Files", "*.mqc"), ("All files", "*.*")))
    
    read_quantConfig(fname)