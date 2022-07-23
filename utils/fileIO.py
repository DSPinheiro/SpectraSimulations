"""
Module for file I/O functions.
Exporting to and importing from files is handled by these functions.
I/O in aps 1, 2 and 3 is not yet implemented in this module.
"""

#GUI Imports for warnings and interface to select files
from tkinter import messagebox
from tkinter.filedialog import askopenfilename

#Data import for variable management
from data.variables import labeldict, the_dictionary, the_aug_dictionary
import data.variables

#CSV reader import for reading and exporting data
import csv

#OS Imports for file paths
import os


# ----------------------------------------------------- #
#                                                       #
#                   EXPORT FUNCTIONS                    #
#                                                       #
# ----------------------------------------------------- #

# Function to generate the file names when saving data
def file_namer(simulation_or_fit, fit_time, extension):
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
def write_to_xls(type_t, xfinal, enoffset, y0, exp_x, exp_y, residues_graph, radiative_files, auger_files, label1, date_and_time):
    """
    Function to save the current simulation data into an excel file
        
        Args:
            type_t: type of transitions simulated (diagram, satellite, diagram + satellite, auger)
            xfinal: simulated x values
            enoffset: energy offset chosen in the simulation
            y0: intensity offset chosen in the simulation
            exp_x: loaded experimental spectrum x values
            exp_y: loaded experimental spectrum y values
            residues_graph: residues graph object from where we will extract the calculated residues
            radiative_files: radiative rates file names found for each charge state
            auger_files: auger rates file names found for each charge state
            label1: shake weights labels read from the shake weigths file
            date_and_time: timestamp of the simulation for the name of the file saved
            
        Returns:
            Nothing, the file is saved and a message box is shown to the used
    """
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

    # ---------------------------------------------------------------------------------------------------------------
    # Add the selected radiative and satellite transition labels into a seperate column
    if type_t != 'Auger':
        for index, transition in enumerate(the_dictionary):
            if the_dictionary[transition]["selected_state"]:
                # Add the diagram transitions
                if max(data.variables.yfinal[index]) != 0:
                    first_line += [the_dictionary[transition]["readable_name"]]
                # Add the satellite transitions
                for l, m in enumerate(data.variables.yfinals[index]):
                    if max(m) != 0:
                        first_line += [the_dictionary[transition]["readable_name"] + '-' + labeldict[label1[l]]]
    else:
        for index, transition in enumerate(the_aug_dictionary):
            if the_aug_dictionary[transition]["selected_state"]:
                # Add the diagram transitions
                if max(data.variables.yfinal[index]) != 0:
                    first_line += [the_aug_dictionary[transition]["readable_name"]]
                # Add the satellite transitions
                for l, m in enumerate(data.variables.yfinals[index]):
                    if max(m) != 0:
                        first_line += [the_aug_dictionary[transition]["readable_name"] + '-' + labeldict[label1[l]]]
    
    # ---------------------------------------------------------------------------------------------------------------
    # Add the column for the total y
    first_line += ['Total']
    
    # Add an intensity offset column if the offset is not 0
    if y0 != 0:
        first_line += ['Total Off']
    
    # Add 2 columns for the experimental spectrum if it is loaded
    if exp_x != None and exp_y != None:
        first_line += ['Exp Energy (eV)', 'Intensity']

    # Add 4 columns for the residue data if it was calculated. An extra spacing column is added before the chi^2 value
    if residues_graph != None:
        first_line += ['Residues (arb. units)', 'std+', 'std-', '', 'red chi 2']

    # Add a spacing column and 2 columns for the charge state mixture weights if they were used in the simulation
    if len(data.variables.PCS_radMixValues) > 0 or len(data.variables.NCS_radMixValues) > 0 or len(data.variables.PCS_augMixValues) > 0 or len(data.variables.NCS_augMixValues) > 0:
        first_line += ['', 'Charge States', 'Percentage']

    # Now that we have the header line configured we can initialize a matrix to save in excel
    # If we have loaded an experimental spectrum we use the largest dimention between the x values grid and the experimental spectrum
    # Matrix = len(first_line) x max(len(xfinal), len(exp_x))
    if exp_x != None:
        matrix = [[None for x in range(len(first_line))] for y in range(max(len(xfinal), len(exp_x)))]
        """
        Variable that holds the data to be saved in matrix form
        """
    else:
        matrix = [[None for x in range(len(first_line))] for y in range(len(xfinal))]
    
    # ---------------------------------------------------------------------------------------------------------------
    # Variable to control which column we need to write to
    transition_columns = 1
    """
    Variable to control which column we need to write to
    """

    # Write the x and x + offset values in the matrix if the offset is not 0, otherwise write only the x
    if enoffset != 0:
        for i, x in enumerate(xfinal):
            matrix[i][0] = x
            matrix[i][1] = x + enoffset

        transition_columns += 1
    else:
        for i, x in enumerate(xfinal):
            matrix[i][0] = x
    
    # ---------------------------------------------------------------------------------------------------------------
    # Write the transition data in the respective columns
    for i, y in enumerate(data.variables.yfinal):
        # If we have data for this transition
        if max(y) != 0:
            # Write the values in the column
            for row in range(len(y)):
                matrix[row][transition_columns] = y[row]
            
            transition_columns += 1
        
        # Same for the satellite transitions but we require and extra loop
        if any(data.variables.yfinals[i]) != 0:
            for j, ys in enumerate(data.variables.yfinals[i]):
                if max(ys) != 0:
                    for row in range(len(y)):
                        matrix[row][transition_columns] = ys[row]
                    
                    transition_columns += 1
    
    # ---------------------------------------------------------------------------------------------------------------
    # Write the total y and y + offset values in the matrix if the offset is not 0, otherwise write only the total y
    if y0 != 0:
        for j in range(len(data.variables.ytot)):
            matrix[j][transition_columns] = data.variables.ytot[j]
            matrix[j][transition_columns + 1] = data.variables.ytot[j] + y0
    
        transition_columns += 1
    else:
        for j in range(len(data.variables.ytot)):
            matrix[j][transition_columns] = data.variables.ytot[j]

    transition_columns += 1
    
    # ---------------------------------------------------------------------------------------------------------------
    # Write the experimental spectrum values
    if exp_x == None and exp_y == None:
        print("No experimental spectrum loaded. Skipping...")
    else:
        for i in range(len(exp_x)):
            matrix[i][transition_columns] = exp_x[i]
            matrix[i][transition_columns + 1] = exp_y[i]

        transition_columns += 2
    
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
        for i in range(len(exp_x)):
            matrix[i][transition_columns] = res[i]
            matrix[i][transition_columns + 1] = sigp[i]
            matrix[i][transition_columns + 2] = sigm[i]

        matrix[0][transition_columns + 4] = data.variables.chi_sqrd

        transition_columns += 5
    
    # ---------------------------------------------------------------------------------------------------------------
    # Write the mix values in the matrix
    if type_t != 'Auger':
        if len(data.variables.PCS_radMixValues) > 0 or len(data.variables.NCS_radMixValues) > 0:
            idx_p = 0
            idx_n = 0
            # Loop all loaded charge states
            for i, cs in enumerate(radiative_files):
                # Write the charge state label
                matrix[i][transition_columns + 1] = cs.split('-intensity_')[1].split('.out')[0] + '_'

                # As the mixture values are split by positive and negative charge states we need to diferenciate them
                if '+' in cs:
                    matrix[i][transition_columns + 2] = data.variables.PCS_radMixValues[idx_p].get()
                    idx_p += 1
                else:
                    matrix[i][transition_columns + 2] = data.variables.NCS_radMixValues[idx_n].get()
                    idx_n += 1
    else:
        if len(data.variables.PCS_augMixValues) > 0 or len(data.variables.NCS_augMixValues) > 0:
            idx_p = 0
            idx_n = 0

            # Add an extra label to know this mixture is for an auger simulation
            matrix[1][transition_columns + 1] = "Auger Mix Values"

            # Loop all loaded charge states
            for i, cs in enumerate(auger_files):
                matrix[i + 1][transition_columns + 1] = cs.split('-augrate_')[1].split('.out')[0] + '_'

                # As the mixture values are split by positive and negative charge states we need to diferenciate them
                if '+' in cs:
                    matrix[i + 1][transition_columns + 2] = data.variables.PCS_augMixValues[idx_p].get()
                    idx_p += 1
                else:
                    matrix[i + 1][transition_columns + 2] = data.variables.NCS_augMixValues[idx_n].get()
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
def exportFit(time_of_click, report):
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
        print(report)

# ----------------------------------------------------- #
#                                                       #
#       LOAD EXPERIMENTAL AND EFFICIENCY DATA           #
#                                                       #
# ----------------------------------------------------- #

# Function to request the file with the experimental spectrum and save the file path
def load(loadvar):
    """
    Function to request the file with the experimental spectrum
        
        Args:
            loadvar: variable where we save the chosen file path
            
        Returns:
            Nothing, the file path is save in the variable
    """
    # Lauch a file picker interface
    fname = askopenfilename(filetypes=(("Spectra files", "*.csv *.txt"), ("All files", "*.*")))
    # Save the path to the loadvar variable
    loadvar.set(fname)

# Function to request the file with the detector efficiency and save the file path
def load_effic_file(effic_var):
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
def loadExp(file):
    """
    Function to read the experimental spectrum as csv
        
        Args:
            file: file path of the experimental spectrum
            
        Returns:
            List with the data still in string format
    """
    return list(csv.reader(open(file, 'r', encoding='utf-8-sig')))

# Function to read the detector efficiency as csv and return it as a list
def loadEfficiency(file):
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
def readRates(rates_file):
    """
    Function to read the rates file
        
        Args:
            rates_file: file path of the rates file
            
        Returns:
            linerates: list with the data still in string format
    """
    
    try:
        pass # TODO T-4.1
        
    except FileNotFoundError:
        messagebox.showwarning("Error", "Rate File is not Available: " + rates_file)

# Read the shake weights file and return a list with the data and a list with the labels
def readShakeWeights(shakeweights_file):
    """
    Function to read the shake weights file
        
        Args:
            shakeweights_file: file path of the shake weights file
            
        Returns:
            shakeweights: list with the shake weights in float
            label1: list with the shake labels
    """
    try:
        with open(shakeweights_file, 'r') as shakeweights_f:
            # Write the lines into a list
            shakeweights_m = [x.strip('\n').split(',') for x in shakeweights_f.readlines()]
            shakeweights = []
            label1 = []
            
            # Loop the read values and store them in two lists
            for i in range(len(shakeweights_m)):
                shakeweights.append(float(shakeweights_m[i][1]))
                label1.append(shakeweights_m[i][0])
            
            return shakeweights, label1
    except FileNotFoundError:
        messagebox.showwarning("Error", "Shake Weigths File is not Avaliable")



# ----------------------------------------------------- #
#                                                       #
#    READ RATES AND IONPOP FILES FOR CHARGE STATES      #
#                                                       #
# ----------------------------------------------------- #

# Search the Charge_States folder for all "identifyer" rate files and return a list with their names
def searchChargeStates(dir_path, z, identifyer):
    """
    Function to search the Charge_States folder for all "identifyer" rate files
        
        Args:
            dir_path: full path of the simulation
            z: z value of the element to simulate
            identifyer: identifyer of the rate files we want to search (intensity, satinty, augrate)
            
        Returns:
            files: file names found in the Charge_States folder with the identifyer
    """
    files = []
    # Loop all files in the folder
    for f in os.listdir(dir_path / str(z) / 'Charge_States'):
        # If the name format matches a radiative rates files then append it to the list
        if os.path.isfile(os.path.join(dir_path / str(z) / 'Charge_States', f)) and identifyer in f:
            files.append(f)
    
    return files

# Read the rates files in the files list and return a list with the data split by positive and negative charge states.
# Also return a list with the order in which the data was stored in the lists
def readChargeStates(files, dir_path, z):
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
    linerates_PCS = []
    linerates_NCS = []

    PCS = []
    NCS = []

    # Loop for each charge state file
    for file in files:
        # Path to the selected file
        tmp_file = dir_path / str(z) / 'Charge_States' / file
        try:
            with open(tmp_file, 'r') as rates:
                if '+' in file:
                    # Write the lines into a list and append it to the total rates for all charge states
                    linerates_PCS.append([x.strip('\n').split() for x in rates.readlines()])
                    # Remove empty strings from possible uneven formating in the appended list
                    linerates_PCS[-1] = list(filter(None, linerates_PCS[-1]))
                    # Delete the header rows from the last list
                    del linerates_PCS[-1][0:2]
                    
                    # Append the charge state value to identify the rates we just appended
                    PCS.append('+' + file.split('+')[1].split('.')[0])
                else:
                    # Write the lines into a list and append it to the total rates for all charge states
                    linerates_NCS.append([x.strip('\n').split() for x in rates.readlines()])
                    # Remove empty strings from possible uneven formating in the appended list
                    linerates_NCS[-1] = list(filter(None, linerates_NCS[-1]))
                    # Delete the header rows from the last list
                    del linerates_NCS[-1][0:2]
                    
                    # Append the charge state value to identify the rates we just appended
                    NCS.append('-' + file.split('-')[1].split('.')[0])
        except FileNotFoundError:
            messagebox.showwarning("Error", "Charge State File is not Avaliable: " + file)
    
    return linerates_PCS, linerates_NCS, PCS, NCS

# Read the ion population file and return a list with the raw data
def readIonPop(ionpop_file):
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