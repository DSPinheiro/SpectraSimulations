"""
Module with several functions for data handling and computation.
In this module we define the profile functions, normalizing function, autofitting function and the main function that calculates and plots spectra.
Other utility functions for updating the transition rates to be used and determine the bounds of the simulation are also defined.
"""

#GUI Imports for warnings
from tkinter import messagebox

#Import numpy
import numpy as np

#Math imports for interpolation and fitting
from scipy.interpolate import interp1d
from lmfit import Minimizer, Parameters, report_fit, fit_report

#OS import for timestamps
from datetime import datetime

#Data import for variable management
from data.variables import labeldict, the_dictionary, the_aug_dictionary
import data.variables as generalVars

#Import file namer function
from utils.fileIO import file_namer, loadEfficiency

#GUI utils for interface variables
import utils.interface as guiVars


element_name = None
"""
Element name to use when sending the data to plot
"""

# --------------------------------------------------------- #
#                                                           #
#            MATH FUNCTIONS FOR LINE PROFILES               #
#                                                           #
# --------------------------------------------------------- #

# Gaussian profile
def G(T, energy, intens, res, width):
    """ 
    Function to calculate the Gaussian line shape at x with HWHM alpha
        
        Args:
            T: list of x values for which we want the y values of the profile
            energy: x value of the profile center
            intens: hight of the profile
            res: experimental resolution to be added to the profile width
            width: natural width of the transition for the profile
        
        Returns:
            y: list of y values for each of the x values in T
    """
    y = [intens * np.sqrt(np.log(2) / np.pi) / (res + width) * np.exp(-((l - energy) / (res + width)) ** 2 * np.log(2)) for l in T]
    
    return y

# Lorentzian profile
def L(T, energy, intens, res, width):
    """ 
    Function to calculate the Lorentzian line shape at x with HWHM alpha
        
        Args:
            T: list of x values for which we want the y values of the profile
            energy: x value of the profile center
            intens: hight of the profile
            res: experimental resolution to be added to the profile width
            width: natural width of the transition for the profile
        
        Returns:
            y: list of y values for each of the x values in T
    """
    y = [intens * (0.5 * (width + res) / np.pi) / ((l - energy) ** 2 + (0.5 * (width + res)) ** 2) for l in T]
    
    return y

# Voigt profile
def V(T, energy, intens, res, width):
    """ 
    Function to calculate the Voigt line shape at x with HWHM alpha
        
        Args:
            T: list of x values for which we want the y values of the profile
            energy: x value of the profile center
            intens: hight of the profile
            res: experimental resolution to be added to the profile width
            width: natural width of the transition for the profile
        
        Returns:
            y: list of y values for each of the x values in T
    """
    sigma = res / np.sqrt(2 * np.log(2))
    y = [np.real(intens * wofz(complex(l - energy, width / 2) / sigma / np.sqrt(2))) / sigma / np.sqrt(2 * np.pi) for l in T]
    
    return y



# --------------------------------------------------------- #
#                                                           #
# DETECTOR EFFICIENCY INTERPOLATOR AND NORMALIZER FUNCTION  #
#                                                           #
# --------------------------------------------------------- #

# Interpolate detector efficiency on the simulation xfinal
def detector_efficiency(energy_values, efficiency_values, xfinal, enoffset):
    """ 
    Function to interpolate the detector efficiency to the simulated x values
        
        Args:
            energy_values: list of the energy values provided in the detector efficiency data
            efficiency_values: list of the efficiency values provided in the detector efficiency data
            xfinal: list of the simulated x values
            enoffset: value of the simulated x offset
            
        Returns:
            interpolated_effic: list of efficiency values interpolated for the simulated x values
    """
    # Initialize interpolated y values
    interpolated_effic = [0 for i in range(len(xfinal))]
    # Interpolate data
    effic_interpolation = interp1d(energy_values, np.array(efficiency_values)/100)
    """
    Interpolation function initialized from the efficiency data, normalized to 1
    """
    # Loop the energy values with the simulated offset and store the efficiency
    for i, energy in enumerate(xfinal+enoffset):
        interpolated_effic[i] = effic_interpolation(energy)
    return interpolated_effic

# Normalization function
def normalizer(y0, expy_max, ytot_max):
    """ 
    Function to normalize the simulated intensity values
        
        Args:
            y0: simulated background intensity offset
            expy_max: maximum experimental intensity
            ytot_max: maximum simulated intensity
            
        Returns:
            normalization_var: value of the normalization multiplyer for the requested normalization
    """
    # Get the type of normalization selected on the interface
    normalize = guiVars.normalizevar.get()
    """
    Value of the normalization type selected in the interface (No, to Experimental Maximum, to Unity)
    """
    
    try:
        # Calculate the normalization multiplier for the normalization chosen
        if normalize == 'ExpMax':
            normalization_var = (1 - y0 / expy_max) * expy_max / ytot_max
        elif normalize == 'One':
            normalization_var = (1 - y0) / ytot_max
        elif normalize == 'No':
            normalization_var = 1

    except ValueError:
        messagebox.showerror("No Spectrum", "No Experimental Spectrum was loaded")
    except ZeroDivisionError:
        normalization_var = 1
    return normalization_var



# --------------------------------------------------------- #
#                                                           #
#            Y CALCULATOR AND FITTING FUNCTIONS             #
#                                                           #
# --------------------------------------------------------- #

# Calculate the simulated y values applying the selected line profile, detector efficiency, resolution and energy offset
def y_calculator(sim, transition_type, fit_type, xfinal, x, y, w, xs, ys, ws, res, energy_values, efficiency_values, enoffset):
    """ 
    Function to calculate the simulated intensities for all the transitions requested, taking into account the simulated offsets.
    This function is used only to apply the selected profile to the already filtered x, y and width values for the transitions.
        
        Args:
            sim: tkinter simulation window required to update the progress bar
            transition_type: type of transition to be simulated (diagram data comes in the x, y, w and satellite data in the xs, ys, ws)
            fit_type: profile type selected in the interface
            xfinal: simulate x values
            x: energy values for each diagram transition to simulate
            y: intensity values for each diagram transition to simulate
            w: natural width values for each diagram transition to simulate
            xs: energy values for each satellite transition in each radiative transition to simulate
            ys: intensity values for each satellite transition in each radiative transition to simulate
            ws: natural width values for each satellite transition in each radiative transition to simulate
            res: experimental resolution to simulate
            energy_values: energy values read from the detector efficiency data
            efficiency_values: efficiency values read from the detector efficiency data
            enoffset: energy offset to simulate
        
        Returns:
            yfinal: list of simulated y values for each diagrma transition we want to simulate for each of the x values in T
            ytot: list of the simulated total y values for all transitions we want to simulate for each of the x values in T
            yfinals: list of simulated y values for each satellite transition in each digram transition we want to simulate for each of the x values in T
    """
    # Initialize a list to store the final y values for each selected transition to be calulated
    yfinal = [[0 for i in range(len(xfinal))] for j in range(len(x))]
    """
    List of simulated y values for each diagrma transition we want to simulate for each of the x values in T
    """
    # Initialize a list to store the final y values summed across all selected transitions
    ytot = [0 for i in range(len(xfinal))]
    """
    List of the simulated total y values for all transitions we want to simulate for each of the x values in T
    """
    # Initialize a list to store the final y values for each satellite transition for each of the selected transitions
    yfinals = [[[0 for n in range(len(xfinal))] for i in generalVars.label1] for j in range(len(xs))]
    """
    List of simulated y values for each satellite transition in each digram transition we want to simulate for each of the x values in T
    """
    
    if transition_type == 'Diagram' or transition_type == 'Auger':
        b1 = 0
        # Loop all the diagram or auger transitions to calculate (y parameter)
        for j, k in enumerate(y):
            # For each transition (high-low levels) loop all the different rates
            for i in range(len(k)):
                # Depending on the profile selected add the y values of the calculated profile to the y values of this transition
                # This profile is calculated across the entire simulated range of x values
                if fit_type == 'Voigt':
                    yfinal[j] = np.add(yfinal[j], V(xfinal, x[j][i], y[j][i], res, w[j][i]))
                elif fit_type == 'Lorentzian':
                    yfinal[j] = np.add(yfinal[j], L(xfinal, x[j][i], y[j][i], res, w[j][i]))
                elif fit_type == 'Gaussian':
                    yfinal[j] = np.add(yfinal[j], G(xfinal, x[j][i], y[j][i], res, w[j][i]))
                # Add a proportionate amount of progress to the current progress value
                b1 += 100 / (len(y) * len(k))
                # Set the progress on the interface
                guiVars.progress_var.set(b1)
                # Update the interface to show the progress
                sim.update_idletasks()
            
            # If the transition rates list is not empty then add the y values for this transition into the total y values for all transitions
            if k != []:
                ytot = np.add(ytot, yfinal[j])
        
        # Set and update the progress and progress bar to 100%
        b1 = 100
        guiVars.progress_var.set(b1)
        sim.update_idletasks()
    elif transition_type == 'Satellites':
        b1 = 0
        # Similar to the diagram transitions but we need an extra for loop to get the rates of each satellite in each diagram transition
        for j, k in enumerate(ys):
            for l, m in enumerate(k):
                for i, n in enumerate(m):
                    if fit_type == 'Voigt':
                        yfinals[j][l] = np.add(yfinals[j][l], V(xfinal, xs[j][l][i], ys[j][l][i], res, ws[j][l][i]))
                    elif fit_type == 'Lorentzian':
                        yfinals[j][l] = np.add(yfinals[j][l], L(xfinal, xs[j][l][i], ys[j][l][i], res, ws[j][l][i]))
                    elif fit_type == 'Gaussian':
                        yfinals[j][l] = np.add(yfinals[j][l], G(xfinal, xs[j][l][i], ys[j][l][i], res, ws[j][l][i]))
                    b1 += 100 / (len(ys) * len(generalVars.label1) * len(m))
                    guiVars.progress_var.set(b1)
                    sim.update_idletasks()
                
                if m != []:
                    ytot = np.add(ytot, yfinals[j][l])
        
        b1 = 100
        guiVars.progress_var.set(b1)
        sim.update_idletasks()
    elif transition_type == 'Diagram + Satellites':
        b1 = 0
        # Diagram block
        for j, k in enumerate(y):
            for i, n in enumerate(k):
                if fit_type == 'Voigt':
                    yfinal[j] = np.abs(np.add(yfinal[j], V(xfinal, x[j][i], y[j][i], res, w[j][i])))
                elif fit_type == 'Lorentzian':
                    yfinal[j] = np.abs(np.add(yfinal[j], L(xfinal, x[j][i], y[j][i], res, w[j][i])))
                elif fit_type == 'Gaussian':
                    yfinal[j] = np.abs(np.add(yfinal[j], G(xfinal, x[j][i], y[j][i], res, w[j][i])))
                b1 += 200 / (len(y) * len(k))
                guiVars.progress_var.set(b1)
                sim.update_idletasks()
            
            if k != []:
                ytot = np.add(ytot, yfinal[j])

        # We define the 50% mark in between the two blocks
        b1 = 50
        guiVars.progress_var.set(b1)
        sim.update_idletasks()
        
        # Satellite block
        for j, k in enumerate(ys):
            for l, m in enumerate(ys[j]):
                for i, n in enumerate(m):
                    if fit_type == 'Voigt':
                        yfinals[j][l] = np.abs(np.add(yfinals[j][l], V(xfinal, xs[j][l][i], ys[j][l][i], res, ws[j][l][i])))
                    elif fit_type == 'Lorentzian':
                        yfinals[j][l] = np.abs(np.add(yfinals[j][l], L(xfinal, xs[j][l][i], ys[j][l][i], res, ws[j][l][i])))
                    elif fit_type == 'Gaussian':
                        yfinals[j][l] = np.abs(np.add(yfinals[j][l], G(xfinal, xs[j][l][i], ys[j][l][i], res, ws[j][l][i])))
                    b1 += 100 / (len(ys) * len(generalVars.label1) * len(m))
                    guiVars.progress_var.set(b1)
                    sim.update_idletasks()
                
                if m != []:
                    ytot = np.add(ytot, yfinals[j][l])
        
        b1 = 100
        guiVars.progress_var.set(b1)
        sim.update_idletasks()
    
    # If detector efficiency data was loaded the appropriate weights are applied to the y values
    if guiVars.effic_var.get() != 'No':
        # Get the efficiency values for the x values simulated
        detector_effi = detector_efficiency(energy_values, efficiency_values, xfinal, enoffset)
        # Modify the y values by the effiency weights
        return ytot*np.array(detector_effi), yfinal*np.array(detector_effi), yfinals*np.array(detector_effi)
    else:
        return ytot, yfinal, yfinals

# Initialize the parameters for fitting
def initializeFitParameters(exp_x, exp_y, enoffset, y0, res):
    """
    Function to initialize the parameters for fitting
        
        Args:
            exp_x: list of energy values read from the experimental spectrum
            exp_y: list of intensity values read from the experimental spectrum
            enoffset: simulated energy offset
            y0: simulated intensity offset
            res: simulated experimental resolution
        
        Returns:
            params: parameter object with the parameters to be optimized
    """
    # Initialize the parameters to be optimized
    params = Parameters()
    
    # --------------------------------------------------------------------------------------------------------
    # Energy offset parameter
    # We set the range of variation for this parameter during optimization to +- 10% of the simulated x range
    xoff_lim = (max(exp_x) - min(exp_x)) * 0.1
    """
    Variation limits for the energy offset parameter
    """
    # Add the parameter to the set of parameters
    params.add('xoff', value=enoffset, min=enoffset - xoff_lim, max=enoffset + xoff_lim)

    # --------------------------------------------------------------------------------------------------------
    # y background offset parameter
    # We set the range of variation for this parameter during optimization to +- 10% of the experimental y range
    yoff_lim = (max(exp_y) - min(exp_y)) * 0.1
    """
    Variation limits for the intensity offset parameter
    """
    # Add the parameter to the set of parameters
    params.add('yoff', value=y0, min=y0 - yoff_lim, max=y0 + yoff_lim)

    # --------------------------------------------------------------------------------------------------------
    # Experimental resolution
    # We set the range of variation for this parameter during optimization +- 3 times the initial value
    res_lim = res * 3
    """
    Variation limits for the experimental resolution parameter
    """
    # Add the parameter to the set of parameters
    params.add('res', value=res, min=0.01, max=res + res_lim)
    
    # --------------------------------------------------------------------------------------------------------
    # New maximum y value parameter
    # Add the parameter to the set of parameters
    params.add('ytot_max', value=max(generalVars.ytot))
    
    return params

# Extract the values of the fitted parameters
def fetchFittedParams(result):
    """
    Function to extract the values of the fitted parameters. These values are also set in the interface
        
        Args:
            result: result object from the fitting
            
        Returns:
            enoffset: fitted value of the simulated energy offset
            y0: fitted value of the simulated intensity offset
            res: fitted value of the simulated experimental resolution
            ytot_max: fitted value of the simulated maximum intensity
    """
    # Get the fitted value of the x offset
    enoffset = result.params['xoff'].value
    # Set the fitted value in the interface
    guiVars.energy_offset.set(enoffset)
    
    # Get the fitted value of the y offset
    y0 = result.params['yoff'].value
    # Set the fitted value in the interface
    guiVars.yoffset.set(y0)
    
    # Get the fitted value of the experimental resolution
    res = result.params['res'].value
    # Set the fitted value in the interface
    guiVars.exp_resolution.set(res)
    
    # Get the fitted value of the fitted total y maximum
    ytot_max = result.params['ytot_max'].value
    
    return enoffset, y0, res, ytot_max

# Create the function to be minimized for the fitting
def func2min(params, sim, exp_x, exp_y, num_of_points, sat, peak, x, y, w, xs, ys, ws, energy_values, efficiency_values, enoffset):
    """
    Function to be minimized in the fitting
        
        Args:
            params: parameters to be minimized in the function
            sim: tkinter window object to update the progress bar
            exp_x: energy values of the experimental spectrum
            exp_y: intensity values of the experimental spectrum
            num_of_points: number of simulated points
            sat: type of transitions to be simulated (diagram data comes in the x, y, w and satellite data in the xs, ys, ws)
            peak: profile type selected in the interface
            x: energy values for each diagram transition to simulate
            y: intensity values for each diagram transition to simulate
            w: natural width values for each diagram transition to simulate
            xs: energy values for each satellite transition in each radiative transition to simulate
            ys: intensity values for each satellite transition in each radiative transition to simulate
            ws: natural width values for each satellite transition in each radiative transition to simulate
            energy_values: energy values read from the detector efficiency data
            efficiency_values: efficiency values read from the detector efficiency data
            enoffset: energy offset to simulate
            
        Returns:
            list with the differences between the simulated y values and the experimental intensities
    """
    global xfinal
    
    # Normalizer for the function to match the plotted values
    normalize = guiVars.normalizevar.get()
    # Initialize the interpolated y values
    y_interp = [0 for i in range(len(exp_x))]
    """
    List for the interpolated values of the simulated y at each energy value of the experimental spectrum
    """
    
    # Get the parameters from the list of initialized parameters
    xoff = params['xoff']
    y0 = params['yoff']
    res = params['res']
    ytot_max = params['ytot_max']
    
    # Initialize the xfinal from which to interpolate
    xfinal = np.array(np.linspace(min(exp_x) - xoff, max(exp_x) - xoff, num=num_of_points))
    
    # Calculate the simulated values
    generalVars.ytot, generalVars.yfinal, generalVars.yfinals = y_calculator(sim, sat, peak, xfinal, x, y, w, xs, ys, ws, res, energy_values, efficiency_values, enoffset)
    # Calculate the normalization multiplier
    normalization_var = normalizer(y0, max(exp_y), ytot_max)
    
    # Interpolate the data
    f_interpolate = interp1d(xfinal + xoff, np.array(generalVars.ytot * normalization_var) + y0, kind='cubic')
    """
    Interpolated function of the simulated points
    """
    
    for g, h in enumerate(exp_x):
        # Get the values of the interpolation for the experimental x values
        y_interp[g] = f_interpolate(h)
    
    # Return the normalized function
    if normalize == 'One':
        return np.array(y_interp) - np.array(exp_y) / max(exp_y)
    else:
        return np.array(y_interp) - np.array(exp_y)



# --------------------------------------------------------- #
#                                                           #
#      FUNCTIONS TO UPDATE THE TRANSITIONS TO SIMULATE      #
#                                                           #
# --------------------------------------------------------- #

# Update the radiative and satellite rates for the selected transition
def updateRadTransitionVals(transition, num):
    """
    Function to update the radiative and satellite rates for the selected transition
        
        Args:
            transition: which transition to fetch the rates of
            num: total number of transitions processed
        
        Returns:
            num_of_transitions: total number of transitions processed
            low_level: low level of the selected transition
            high_level: high level of the selected transition
            diag_stick_val: rates data for the selected transition
            sat_stick_val: rates data for the possible satellite transitions for the selected transition
    """
    # Update the number of transitions loaded (this could be done by reference as well)
    num_of_transitions = num + 1
    # Get the low and high levels for the selected transition
    low_level = the_dictionary[transition]["low_level"]
    high_level = the_dictionary[transition]["high_level"]
    
    # Filter the radiative and satellite rates data for the selected transition
    diag_stick_val = [line for line in generalVars.lineradrates if line[1] in low_level and line[5] == high_level and float(line[8]) != 0]
    sat_stick_val = [line for line in generalVars.linesatellites if low_level in line[1] and high_level in line[5] and float(line[8]) != 0]
    
    return num_of_transitions, low_level, high_level, diag_stick_val, sat_stick_val

# Update the satellite rates for the selected transition
def updateSatTransitionVals(low_level, high_level, key, sat_stick_val):
    """
    Function to update the satellite rates for the selected transition and shake level
        
        Args:
            low_level: low level of the selected transition
            high_level: high level of the selected transition
            key: shake level of the satellite transition
            sat_stick_val: list with all the possible satellite transitions for the current diagram transition
        
        Returns:
            sat_stick_val_ind: list with the satellite rates for the selected diagram transition and shake level
    """
    # Filter the satellite rates data for the combinations of selected levels
    sat_stick_val_ind1 = [line for line in sat_stick_val if low_level + key in line[1] and key + high_level in line[5]]
    sat_stick_val_ind2 = [line for line in sat_stick_val if low_level + key in line[1] and high_level + key in line[5] and key != high_level]
    sat_stick_val_ind3 = [line for line in sat_stick_val if key + low_level in line[1] and key + high_level in line[5]]
    sat_stick_val_ind4 = [line for line in sat_stick_val if key + low_level in line[1] and high_level + key in line[5] and key != high_level]
    sat_stick_val_ind = sat_stick_val_ind1 + sat_stick_val_ind2 + sat_stick_val_ind3 + sat_stick_val_ind4
    
    return sat_stick_val_ind

# Update the auger rates for the selected transition
def updateAugTransitionVals(transition, num):
    """
    Function to update the auger rates for the selected transition
        
        Args:
            transition: which transition to fetch the rates of
            num: total number of transitions processed
        
        Returns:
            num_of_transitions: total number of transitions processed
            aug_stick_val: rates data for the selected transition
    """
    # Update the number of transitions loaded (this could be done by reference as well)
    num_of_transitions = num + 1
    # Get the low, high and auger levels for the selected transition
    low_level = the_aug_dictionary[transition]["low_level"]
    high_level = the_aug_dictionary[transition]["high_level"]
    auger_level = the_aug_dictionary[transition]["auger_level"]

    # Filter the auger rates data for the selected transition
    aug_stick_val = [line for line in generalVars.lineauger if low_level in line[1] and high_level in line[5][:2] and auger_level in line[5][2:4] and float(line[8]) != 0]
    
    return num_of_transitions, aug_stick_val

# Update the radiative and satellite rates for the selected transition and charge state
def updateRadCSTrantitionsVals(transition, num, ncs, cs):
    """
    Function to update the radiative and satellite rates for the selected transition and charge state
        
        Args:
            transition: which transition to fetch the rates of
            num: total number of transitions processed
            ncs: boolean selecting if this is a negative charge state or not
            cs: value of the charge state
        
        Returns:
            num_of_transitions: total number of transitions processed
            low_level: low level of the selected transition and charge state
            high_level: high level of the selected transition and charge state
            diag_stick_val: rates data for the selected transition and charge state
            sat_stick_val: rates data for the possible satellite transitions for the selected transition and charge state
    """
    # Update the number of transitions loaded (this could be done by reference as well)
    num_of_transitions = num + 1
    # Get the low and high levels for the selected transition
    low_level = the_dictionary[transition]["low_level"]
    high_level = the_dictionary[transition]["high_level"]
    
    # Filter the radiative and satellite rates data for the selected transition and charge state
    if not ncs:
        diag_stick_val = [line + [generalVars.PCS_radMixValues[i].get()] for i, linerad in enumerate(generalVars.lineradrates_PCS) for line in linerad if line[1] in low_level and line[5] == high_level and float(line[8]) != 0 and generalVars.rad_PCS[i] == cs]  # Cada vez que o for corre, lê o ficheiro de uma transição
    else:
        diag_stick_val = [line + [generalVars.NCS_radMixValues[i].get()] for i, linerad in enumerate(generalVars.lineradrates_NCS) for line in linerad if line[1] in low_level and line[5] == high_level and float(line[8]) != 0 and generalVars.rad_NCS[i] == cs]

    if not ncs:
        sat_stick_val = [line + [generalVars.PCS_radMixValues[i].get()] for i, linesat in enumerate(generalVars.linesatellites_PCS) for line in linesat if low_level in line[1] and high_level in line[5] and float(line[8]) != 0 and generalVars.sat_PCS[i] == cs]
    else:
        sat_stick_val = [line + [generalVars.NCS_radMixValues[i].get()] for i, linesat in enumerate(generalVars.linesatellites_NCS) for line in linesat if low_level in line[1] and high_level in line[5] and float(line[8]) != 0 and generalVars.sat_NCS[i] == cs]
    
    return num_of_transitions, low_level, high_level, diag_stick_val, sat_stick_val

# Update the auger rates for the selected transition and charge state
def updateAugCSTransitionsVals(transition, num, ncs, cs):
    """
    Function to update the auger rates for the selected transition and charge state
        
        Args:
            transition: which transition to fetch the rates of
            num: total number of transitions processed
            ncs: boolean selecting if this is a negative charge state or not
            cs: value of the charge state
        
        Returns:
            num_of_transitions: total number of transitions processed
            aug_stick_val: rates data for the selected transition and charge state
    """
    # Update the number of transitions loaded (this could be done by reference as well)
    num_of_transitions = num + 1
    # Get the low, high and auger levels for the selected transition
    low_level = the_aug_dictionary[transition]["low_level"]
    high_level = the_aug_dictionary[transition]["high_level"]
    auger_level = the_aug_dictionary[transition]["auger_level"]

    # Filter the auger rates data for the selected transition and charge state
    if not ncs:
        aug_stick_val = [line + [generalVars.PCS_augMixValues[i].get()] for i, lineaug in enumerate(generalVars.lineaugrates_PCS) for line in lineaug if low_level in line[1] and high_level in line[5][:2] and auger_level in line[5][2:4] and float(line[8]) != 0 and generalVars.aug_PCS[i] == cs]
    else:
        aug_stick_val = [line + [generalVars.NCS_augMixValues[i].get()] for i, lineaug in enumerate(generalVars.lineaugrates_NCS) for line in lineaug if low_level in line[1] and high_level in line[5][:2] and auger_level in line[5][2:4] and float(line[8]) != 0 and generalVars.aug_PCS[i] == cs]
    
    return num_of_transitions, aug_stick_val



# --------------------------------------------------------- #
#                                                           #
#       FUNCTIONS TO UPDATE X BOUNDS AND REBIND DATA        #
#                                                           #
# --------------------------------------------------------- #

# Calculate the x bounds from the simulated transition energy and width data (excluing satellite transitions)
def getBounds(x, w):
    """
    Function to calculate the x bounds from the simulated transition energy and width data (excluing satellite transitions)
        
        Args:
            x: energy values for the simulated diagram transitions
            w: width values for the simulated diagram transitions
        
        Returns:
            deltaE: difference between the max and min energy of each transition
            max_value: maximum value to be simulated, taking into consideration all transition energies and widths
            min_value: minimum value to be simulated, taking into consideration all transition energies and widths
    """
    deltaE = []
    # Loop the values of x and calulate the range of each transition
    for j, k in enumerate(x):
        if k != []:
            deltaE.append(max(x[j]) - min(x[j]))

    # Calculate the automatic min and max values of x to be plotted
    max_value = max([max(x[i]) for i in range(len(x)) if x[i] != []]) + 4 * max([max(w[i]) for i in range(len(w)) if w[i] != []])
    min_value = min([min(x[i]) for i in range(len(x)) if x[i] != []]) - 4 * max([max(w[i]) for i in range(len(w)) if w[i] != []])
    
    return deltaE, max_value, min_value

# Calculate the x bound from the simulated satellite transition energy and width data
def getSatBounds(xs, ws):
    """
    Function to calculate the x bound from the simulated satellite transition energy and width data
        
        Args:
            xs: energy values for the simulated satellite transitions
            ws: width values for the simulated satellite transitions
        
        Returns:
            deltaE: difference between the max and min energy of each transition
            max_value: maximum value to be simulated, taking into consideration all transition energies and widths
            min_value: minimum value to be simulated, taking into consideration all transition energies and widths
    """
    deltaE = []
    # Loop the values of x and calulate the range of each satellite transition in each diagram transition
    for j, k in enumerate(xs):
        for l, m in enumerate(xs[j]):
            if m != []:
                deltaE.append(max(m) - min(m))
    
    # Calculate the automatic min and max values of x to be plotted
    max_value = max([max(xs[i][j]) for i in range(len(xs)) for j in range(len(xs[i])) if xs[i][j] != []]) + max([max(ws[i][j]) for i in range(len(ws)) for j in range(len(ws[i])) if ws[i][j] != []])  # valor max de todos os elementos de xs (satt) que tem 7 linhas(ka1, ka2, etc) e o tamanho da lista label1 dentro de cada linha
    min_value = min([min(xs[i][j]) for i in range(len(xs)) for j in range(len(xs[i])) if xs[i][j] != []]) - max([max(ws[i][j]) for i in range(len(ws)) for j in range(len(ws[i])) if ws[i][j] != []])
    
    return deltaE, max_value, min_value

# Update the bounds for the user selected bounds (Auto or value)
def updateMaxMinVals(x_mx, x_mn, deltaE, max_value, min_value, res, enoffset):
    """
    Function to update the bounds for the user selected bounds (Auto or value)
        
        Args:
            x_mx: user value for the maximum x value. if set to Auto we calculate it
            x_mn: user value for the minimum x value. if set to Auto we calculate it
            deltaE: delta values for each of the plotted transitions
            max_value: maximum value to be simulated, taking into consideration all transition energies and widths
            min_value: minimum value to be simulated, taking into consideration all transition energies and widths
            res: simulated experimental resolution
            enoffset: simulated energy offset
        
        Returns:
            array_input_max: maximum x value to be plotted
            array_input_min: minimum x value to be plotted
    """
    if x_mn == 'Auto':
        # If we are automaticaly calculating the bounds we add extra space arround the data to show possible tails of transitions
        if res <= 0.2 * (min(deltaE)):
            array_input_min = min_value - 2 * min(deltaE)
        else:
            array_input_min = min_value - 2 * res * min(deltaE)
    else:
        # We use the value in the interface while also accounting for the x offset
        array_input_min = float(x_mn) - enoffset
    
    if x_mx == 'Auto':
        # If we are automaticaly calculating the bounds we add extra space arround the data to show possible tails of transitions
        if res <= 0.2 * (min(deltaE)):
            array_input_max = max_value + 2 * min(deltaE)
        else:
            array_input_max = max_value + 2 * res * (min(deltaE))
    else:
        # We use the value in the interface while also accounting for the x offset
        array_input_max = float(x_mx) - enoffset
    
    return array_input_max, array_input_min
    
# Extract x, y and sigma values from the read experimental file
def extractExpVals(exp_spectrum):
    """
    Function to extract x, y and sigma values from the read experimental file
        
        Args:
            exp_spectrum: list with the experimental spectrum to be handled
        
        Returns:
            xe: energy values of the experimental spectrum
            ye: intensity values of the experimental spectrum
            sigma_exp: error values of the experimental spectrum (sqrt(intensity) by default if no data is provided)
    """
    for i, it in enumerate(exp_spectrum):
        # Convert the loaded values to float. Update this to a map function?
        for j, itm in enumerate(exp_spectrum[i]):
            if exp_spectrum[i][j] != '':
                exp_spectrum[i][j] = float(itm)
    
    # Split the values into x and y
    xe = np.array([float(row[0]) for row in exp_spectrum])
    ye = np.array([float(row[1]) for row in exp_spectrum])
    
    # If the spectrum has 3 columns of data then use the third column as the uncertainty
    if len(exp_spectrum[0]) >= 3:
        sigma_exp = np.array([float(row[2]) for row in exp_spectrum])
    else:
        # Otherwise use the sqrt of the count number
        sigma_exp = np.sqrt(ye)
    
    return xe, ye, sigma_exp

# Bind the experimental values into the chosen bounds
def getBoundedExp(xe, ye, sigma_exp, enoffset, num_of_points, x_mx, x_mn):
    """
    Function to bind the experimental values into the chosen bounds.
    If Auto bounds are chosen the simulation will be performed for all the experimental spectrum span
    Otherwise we remove the experimental data that is outside the bounds we want
        
        Args:
            xe: energy values from the experimental spectrum
            ye: intensity values from the experimental spectrum
            sigma_exp: error values from the experimental spectrum
            enoffset: simulated energy offset
            num_of_points: number of simulated points
            x_mx: user value for the maximum x value. if set to Auto we calculate it
            x_mn: user value for the minimum x value. if set to Auto we calculate it
        
        Returns:
            exp_x: list of xe values inside the bounds
            exp_y: list of ye values inside the bounds
            exp_sigma: list of sigma_exp values inside the bounds
    """
    exp_x = []
    exp_y = []
    exp_sigma = []
    
    # When we have an experimental spectrum loaded we use the bounds of this spectrum
    if x_mx == 'Auto':
        max_exp_lim = max(xe)
    else:
        max_exp_lim = float(x_mx)

    if x_mn == 'Auto':
        min_exp_lim = min(xe)
    else:
        min_exp_lim = float(x_mn)

    # Check if the energy value is within the bounds
    for i in range(len(xe)):
        if min_exp_lim <= xe[i] <= max_exp_lim:
            exp_x.append(xe[i])
            exp_y.append(ye[i])
            exp_sigma.append(sigma_exp[i])
    
    return exp_x, exp_y, exp_sigma



# --------------------------------------------------------- #
#                                                           #
#  FUNCTIONS TO PREPARE THE DATA AND SEND IT TO THE PLOTS   #
#                                                           #
# --------------------------------------------------------- #

# Stick plotter. Plots a stick for the transition
def stem_ploter(transition_values, transition, spec_type, ind, key):
    """
    Stick plotter function. Plots a stick for the transition
        
        Args:
            transition_values: list of the transition rates data
            transition: the selected transition to plot
            spec_type: simulation type selected in the interface (diagram, satellite, auger, diagram_cs, satellite_cs, auger_cs)
            ind: shake level index to use when plotting a satellite transition
            key: shake level label to use when plotting a satellite transition
        
        Returns:
            Nothing, the transition is plotted and the interface is updated
    """
    # Set of colors to choose from when plotting
    col2 = [['b'], ['g'], ['r'], ['c'], ['m'], ['y'], ['k']]
    """
    Set of colors to choose from when plotting
    """
    # Extract the energy values
    x = [float(row[8]) for row in transition_values]
    """
    Energy values for the selected transition
    """

    # Add extra values before and after to make the y start and terminate on 0
    max_value = max(x)
    min_value = min(x)
    x.insert(0, 2 * min_value - max_value)
    x.append(2 * max_value - min_value)
    
    # Calculate the y's weighted with the shake weights depending on the spectrum type and plot the sticks
    # In the case of charge state simulation the y's are also weighted by the selected mixture percentages
    if spec_type == 'Diagram' or spec_type == 'Auger':
        y = [float(row[11]) * (1 - 0.01 * sum(generalVars.shakeweights)) for row in transition_values]
        """
        Intensity values for the selected diagram or auger transition
        """
        y.insert(0, 0)
        y.append(0)
        a.stem(x, y, markerfmt=' ', linefmt=str(col2[np.random.randint(0, 7)][0]), label=str(transition), use_line_collection=True)
        a.legend(loc='best', numpoints=1)
    elif spec_type == 'Satellites':
        sy_points = [float(float(row[11]) * 0.01 * generalVars.shakeweights[ind]) for row in transition_values]
        """
        Intensity values for the selected satellite transition
        """
        sy_points.insert(0, 0)
        sy_points.append(0)
        a.stem(x, sy_points, markerfmt=' ', linefmt=str(col2[np.random.randint(0, 7)][0]), label=transition + ' - ' + labeldict[key], use_line_collection=True)  # Plot a stemplot
        a.legend(loc='best', numpoints=1)
    elif spec_type == 'Diagram_CS' or spec_type == 'Auger_CS':
        y = [float(row[11]) * (1 - 0.01 * sum(generalVars.shakeweights)) * float(row[-1]) for row in transition_values]
        """
        Intensity values for the selected diagram or auger transition weight by the charge state mix value
        """
        y.insert(0, 0)
        y.append(0)
        a.stem(x, y, markerfmt=' ', linefmt=str(col2[np.random.randint(0, 7)][0]), label=str(transition), use_line_collection=True)
        a.legend(loc='best', numpoints=1)
    elif spec_type == 'Satellites_CS':
        sy_points = [float(float(row[11]) * 0.01 * generalVars.shakeweights[ind] * float(row[-1])) for row in transition_values]
        """
        Intensity values for the selected satellite transition weight by the charge state mix value
        """
        sy_points.insert(0, 0)
        sy_points.append(0)
        a.stem(x, sy_points, markerfmt=' ', linefmt=str(col2[np.random.randint(0, 7)][0]), label=transition + ' - ' + labeldict[key], use_line_collection=True)  # Plot a stemplot
        a.legend(loc='best', numpoints=1)
    
    # --------------------------------------------------------------------------------------------------------------------------
    # Automatic legend formating
    a.legend(title=element_name, title_fontsize='large')
    a.legend(title=element_name)
    # Number of total labels to place in the legend
    number_of_labels = len(a.legend().get_texts())
    # Initialize the numeber of legend columns
    legend_columns = 1
    # Initialize the number of legends in each columns
    labels_per_columns = number_of_labels / legend_columns
    
    # While we have more than 10 labels per column
    while labels_per_columns > 10:
        # Add one more column
        legend_columns += 1
        # Recalculate the number of labels per column
        labels_per_columns = number_of_labels / legend_columns
    
    # Place the legend with the final number of columns
    a.legend(ncol=legend_columns)

# Profile plotter. Plots each transition, applying the selected profile
def plot_stick(sim, f, graph_area):
    """
    Profile plotter function. Plots each transition, applying the selected profile
        
        Args:
            sim: tkinter simulation window to update the progress bar
            f: matplotlib figure object where to plot the data
            graph_area: matplotlib graph to plot the simulated transitions
            
        Returns:
            Nothing, the simulation is performed, the transitions are plotted and the interface is updated
    """
    # Get the timestamp to use when saving files for this simulation plot
    time_of_click = datetime.now()
    """
    Timestamp to use when saving files for this simulation plot
    """
    global xfinal, exp_x, exp_y, residues_graph
    
    # Reinitialize the residues graph and experimental points
    residues_graph = None
    """
    Matplotlib graph object for the residues
    """
    exp_x = None
    """
    List of experimental spectrum energies
    """
    exp_y = None
    """
    List of experimental spectrum intensities
    """
    
    # Reset the plot with the configurations selected
    graph_area.clear()
    if guiVars.yscale_log.get() == 'Ylog':
        graph_area.set_yscale('log')
    if guiVars.xscale_log.get() == 'Xlog':
        graph_area.set_xscale('log')
    
    graph_area.legend(title=element_name)
    
    # Get the values from the interface
    autofit = guiVars.autofitvar.get()
    total = guiVars.totalvar.get()
    normalize = guiVars.normalizevar.get()
    y0 = guiVars.yoffset.get()
    enoffset = guiVars.energy_offset.get()
    res = guiVars.exp_resolution.get()
    spectype = guiVars.choice_var.get()
    peak = guiVars.type_var.get()
    load = guiVars.loadvar.get()
    effic_file_name = guiVars.effic_var.get()
    sat = guiVars.satelite_var.get()
    num_of_points = guiVars.number_points.get()
    x_mx = guiVars.x_max.get()
    x_mn = guiVars.x_min.get()
    
    number_of_fit_variables = 0
    
    # Set of colors to choose from when plotting
    col2 = [['b'], ['g'], ['r'], ['c'], ['m'], ['y'], ['k']]
    """
    Set of colors to choose from when plotting
    """
    
    # Initialize the x, y and w arrays for both the non satellites and satellites (xs, ys, ws) transitions
    x = [[] for i in range(len(the_dictionary))]
    """
    Energy values for each of the possible radiative transitions
    """
    y = [[] for i in range(len(the_dictionary))]
    """
    Intensity values for each of the possible radiative transitions
    """
    w = [[] for i in range(len(the_dictionary))]
    """
    Natural width values for each of the possible radiative transitions
    """
    xs = [[[] for i in generalVars.label1] for j in x]
    """
    Energy values for each of the possible radiative satellite transitions
    """
    ys = [[[] for i in generalVars.label1] for j in y]
    """
    Intensity values for each of the possible radiative satellite transitions
    """
    ws = [[[] for i in generalVars.label1] for j in w]
    """
    Natural width values for each of the possible radiative satellite transitions
    """
    
    # Initialize the normalization multiplier
    normalization_var = 1
    """
    Normalization multiplyer
    """
    
    # --------------------------------------------------------------------------------------------------------------------------
    if spectype == 'Stick':
        # Variable for the total number of plotted transitions
        num_of_transitions = 0
        # Variable for the number of transitions that were selected but no rates were found
        bad_selection = 0
        
        # Radiative and Auger code has to be split due to the different dictionaries used for the transitions
        if sat != 'Auger':
            # Loop possible radiative transitions
            for transition in the_dictionary:
                # If the transition was selected
                if the_dictionary[transition]["selected_state"]:
                    # Filter the radiative and satellite rates corresponding to this transition
                    num_of_transitions, low_level, high_level, diag_stick_val, sat_stick_val = updateRadTransitionVals(transition, num_of_transitions)
                    
                    # -------------------------------------------------------------------------------------------
                    if sat == 'Diagram':
                        # Check if there is no data for the selected transition
                        if not diag_stick_val:
                            # Make a 0 vector to still have data to plot
                            diag_stick_val = [['0' for i in range(16)]]
                            # Show a warning that this transition has no data and add it to the bad selection count
                            messagebox.showwarning("Wrong Transition", transition + " is not Available")
                            bad_selection += 1
                        
                        # Plot the transition
                        stem_ploter(diag_stick_val, transition, 'Diagram', 0, 0)
                    elif sat == 'Satellites':
                        # Check if there is no data for the selected transition
                        if not sat_stick_val:
                            # Make a 0 vector to still have data to plot
                            sat_stick_val = [['0' for i in range(16)]]
                            # Show a warning that this transition has no data and add it to the bad selection count
                            messagebox.showwarning("Wrong Transition", transition + " is not Available")
                            bad_selection += 1
                        
                        # Initialize a variable to control the progress bar
                        b1 = 0
                        
                        # Loop all shake levels read in the shake weights file
                        for ind, key in enumerate(generalVars.label1):
                            # Filter the specific combination of radiative transition and shake level (key) to simulate
                            sat_stick_val_ind = updateSatTransitionVals(low_level, high_level, key, sat_stick_val)
                            
                            # Check for at least one satellite transition
                            if len(sat_stick_val_ind) > 1:
                                stem_ploter(sat_stick_val_ind, transition, 'Satellites', ind, key)
                            
                            # Update the progress bar
                            b1 += 100 / len(generalVars.label1)
                            guiVars.progress_var.set(b1)
                            sim.update_idletasks()
                    elif sat == 'Diagram + Satellites':
                        # Diagram block
                        if not diag_stick_val:
                            diag_stick_val = [['0' for i in range(16)]]
                            messagebox.showwarning("Wrong Transition", "Diagram info. for " + transition + " is not Available")
                            bad_selection += 1
                        
                        stem_ploter(diag_stick_val, transition, 'Diagram', 0, 0)
                        
                        # Satellite block
                        if not sat_stick_val:
                            sat_stick_val = [['0' for i in range(16)]]
                            messagebox.showwarning("Wrong Transition", "Satellites info.  for " + transition + " is not Available")
                            bad_selection += 1
                        
                        # Initialize a variable to control the progress bar
                        b1 = 0
                        for ind, key in enumerate(generalVars.label1):
                            # Filter the specific combination of radiative transition and shake level (key) to simulate
                            sat_stick_val_ind = updateSatStickTransitionVals(low_level, high_level, key, sat_stick_val)
                            
                            # Check for at least one satellite transition
                            if len(sat_stick_val_ind) > 1:
                                stem_ploter(sat_stick_val_ind, transition, 'Satellites', ind, key)
                            
                            # Update the progress bar
                            b1 += 100 / len(generalVars.label1)
                            guiVars.progress_var.set(b1)
                            sim.update_idletasks()

                # Set the labels for the axis
                graph_area.set_xlabel('Energy (eV)')
                graph_area.set_ylabel('Intensity (arb. units)')
        else:
            # Loop possible auger transitions
            for transition in the_aug_dictionary:
                # If the transition is selected
                if the_aug_dictionary[transition]["selected_state"]:
                    # Filter the auger rates for this transition
                    num_of_transitions, aug_stick_val = updateAugTransitionVals(transition, num_of_transitions)
                    
                    # Check if there is no data for the selected transition
                    if not aug_stick_val:
                        # Make a 0 vector to still have data to plot
                        aug_stick_val = [['0' for i in range(16)]]
                        # Show a warning that this transition has no data and add it to the bad selection count
                        messagebox.showwarning("Wrong Transition", "Auger info. for " + transition + " is not Available")
                        bad_selection += 1
                    
                    # Plot the transition
                    stem_ploter(aug_stick_val, transition, 'Auger', 0, 0)

                # Set the labels for the axis
                graph_area.set_xlabel('Energy (eV)')
                graph_area.set_ylabel('Intensity (arb. units)')

        if num_of_transitions == 0:
            messagebox.showerror("No Transition", "No transition was chosen")
        elif bad_selection != 0:
            messagebox.showerror("Wrong Transition", "You chose " + str(bad_selection) + " invalid transition(s)")
    # --------------------------------------------------------------------------------------------------------------------------
    elif spectype == 'M_Stick':
        # Variable for the total number of plotted transitions
        num_of_transitions = 0
        # Variable for the number of transitions that were selected but no rates were found
        bad_selection = 0
        
        # Radiative and Auger code has to be split due to the different dictionaries used for the transitions
        if sat != 'Auger':
            # Initialize the charge states we have to loop through
            charge_states = generalVars.rad_PCS + generalVars.rad_NCS

            # Loop the charge states
            for cs_index, cs in enumerate(charge_states):
                # Initialize the mixture value chosen for this charge state
                mix_val = '0.0'
                # Flag to check if this is a negative or positive charge state
                ncs = False

                # Check if this charge state is positive or negative and get the mix value
                if cs_index < len(generalVars.rad_PCS):
                    mix_val = generalVars.PCS_radMixValues[cs_index].get()
                else:
                    mix_val = generalVars.NCS_radMixValues[cs_index - len(generalVars.rad_PCS)].get()
                    ncs = True
                
                # Check if the mix value is not 0, otherwise no need to plot the transitions for this charge state
                if mix_val != '0.0':
                    # Loop the possible radiative transitions
                    for transition in the_dictionary:
                        # If the transition is selected
                        if the_dictionary[transition]["selected_state"]:
                            # Filter the radiative and satellite rates for this transition and charge state
                            num_of_transitions, low_level, high_level, diag_stick_val, sat_stick_val = updateRadCSTrantitionsVals(transition, num_of_transitions, ncs, cs)
                            
                            if sat == 'Diagram':
                                # Check if there is no data for the selected transition
                                if not diag_stick_val:
                                    # Make a 0 vector to still have data to plot
                                    diag_stick_val = [['0' for i in range(16)]]
                                    # Show a warning that this transition has no data and add it to the bad selection count
                                    messagebox.showwarning("Wrong Transition", transition + " is not Available for charge state: " + cs)
                                    bad_selection += 1
                                
                                stem_ploter(diag_stick_val, cs + ' ' + transition, 'Diagram_CS', 0, 0)
                            elif sat == 'Satellites':
                                # Check if there is no data for the selected transition
                                if not sat_stick_val:
                                    # Make a 0 vector to still have data to plot
                                    sat_stick_val = [['0' for i in range(16)]]
                                    # Show a warning that this transition has no data and add it to the bad selection count
                                    messagebox.showwarning("Wrong Transition", transition + " is not Available for charge state: " + cs)
                                    bad_selection += 1
                                
                                # Initialize a variable to control the progress bar
                                b1 = 0
                                
                                # Loop the shake levels read from the shake weights file
                                for ind, key in enumerate(generalVars.label1):
                                    # Filter the specific combination of radiative transition and shake level (key) to simulate
                                    sat_stick_val_ind = updateSatStickTransitionVals(low_level, high_level, key, sat_stick_val)
                                    
                                    # Check for at least one satellite transition
                                    if len(sat_stick_val_ind) > 1:
                                        stem_ploter(sat_stick_val_ind, cs + ' ' + transition, 'Satellites_CS', ind, key)
                                    
                                    # Update the progress bar
                                    b1 += 100 / len(generalVars.label1)
                                    guiVars.progress_var.set(b1)
                                    sim.update_idletasks()
                            elif sat == 'Diagram + Satellites':
                                # Diagram block
                                if not diag_stick_val:
                                    diag_stick_val = [['0' for i in range(16)]]
                                    messagebox.showwarning("Wrong Transition", "Diagram info. for " + transition + " is not Available")
                                    bad_selection += 1
                                
                                stem_ploter(diag_stick_val, cs + ' ' + transition, 'Diagram_CS', 0, 0)
                                
                                # Satellite block
                                if not sat_stick_val:
                                    sat_stick_val = [['0' for i in range(16)]]
                                    messagebox.showwarning("Wrong Transition", "Satellites info.  for " + transition + " is not Available")
                                    bad_selection += 1
                                
                                # Initialize a variable to control the progress bar
                                b1 = 0
                                
                                for ind, key in enumerate(generalVars.label1):
                                    # Filter the specific combination of radiative transition and shake level (key) to simulate
                                    sat_stick_val_ind = updateSatStickTransitionVals(low_level, high_level, key, sat_stick_val)
                                    
                                    # Check for at least one satellite transition
                                    if len(sat_stick_val_ind) > 1:
                                        stem_ploter(sat_stick_val_ind, cs + ' ' + transition, 'Satellites_CS', ind, key)
                                    
                                    # Update the progress bar
                                    b1 += 100 / len(generalVars.label1)
                                    guiVars.progress_var.set(b1)
                                    sim.update_idletasks()

                        # Set the labels for the axis
                        graph_area.set_xlabel('Energy (eV)')
                        graph_area.set_ylabel('Intensity (arb. units)')
        else:
            # Initialize the charge states we have to loop through
            charge_states = generalVars.aug_PCS + generalVars.aug_NCS

            # Loop the charge states
            for cs_index, cs in enumerate(charge_states):
                # Initialize the mixture value chosen for this charge state
                mix_val = '0.0'
                # Flag to check if this is a negative or positive charge state
                ncs = False

                # Check if this charge state is positive or negative and get the mix value
                if cs_index < len(generalVars.aug_PCS):
                    mix_val = generalVars.PCS_augMixValues[cs_index].get()
                else:
                    mix_val = generalVars.NCS_augMixValues[cs_index - len(generalVars.aug_PCS)].get()
                    ncs = True
                
                # Check if the mix value is not 0, otherwise no need to plot the transitions for this charge state
                if mix_val != '0.0':
                    # Loop the possible auger transitions
                    for transition in the_aug_dictionary:
                        # If the transition is selected
                        if the_aug_dictionary[transition]["selected_state"]:
                            # Filter the auger rates for this transition and charge state
                            num_of_transitions, aug_stick_val = updateAugCSTransitionsVals(transition, num_of_transitions, ncs, cs)
                            
                            # Check if there is no data for the selected transition
                            if not aug_stick_val:
                                # Make a 0 vector to still have data to plot
                                aug_stick_val = [['0' for i in range(16)]]
                                # Show a warning that this transition has no data and add it to the bad selection count
                                messagebox.showwarning("Wrong Transition", "Auger info. for " + transition + " is not Available for charge state: " + cs)
                                bad_selection += 1
                            
                            stem_ploter(aug_stick_val, cs + ' ' + transition, 'Auger_CS', 0, 0)

                        # Set the labels for the axis
                        graph_area.set_xlabel('Energy (eV)')
                        graph_area.set_ylabel('Intensity (arb. units)')

        if num_of_transitions == 0:
            messagebox.showerror("No Transition", "No transition was chosen")
        elif bad_selection != 0:
            messagebox.showerror("Wrong Transition", "You chose " + str(bad_selection) + " invalid transition(s)")
    # --------------------------------------------------------------------------------------------------------------------------
    elif spectype == 'Simulation':
        # Variable for the number of transitions that were selected but no rates were found
        bad_selection = 0

        if sat != 'Auger':
            # -------------------------------------------------------------------------------------------
            # Read the selected transitions
            # In this case we first store all the values for the transitions and then we calculate the y values to be plotted according to a profile
            for index, transition in enumerate(the_dictionary):
                if the_dictionary[transition]["selected_state"]:
                    # Same filter as the sticks but we dont keep track of the number of selected transitions
                    _, low_level, high_level, diag_sim_val, sat_sim_val = updateRadTransitionVals(transition, 0)
                    
                    if sat == 'Diagram':
                        # Extract the energies, intensities and widths of the transition (different j and eigv)
                        x1 = [float(row[8]) for row in diag_sim_val]
                        y1 = [float(row[11]) * (1 - sum(generalVars.shakeweights)) for row in diag_sim_val]
                        w1 = [float(row[15]) for row in diag_sim_val]
                        # Store the values in a list containing all the transitions to simulate
                        x[index] = x1
                        y[index] = y1
                        w[index] = w1
                    elif sat == 'Satellites':
                        # Loop the shake labels read from the shake weights file
                        for ind, key in enumerate(generalVars.label1):
                            # Filter the specific combination of radiative transition and shake level (key) to simulate
                            sat_sim_val_ind = updateSatTransitionVals(low_level, high_level, key, sat_sim_val)
                            
                            # Check if there is at least one satellite transition
                            if len(sat_sim_val_ind) > 1:
                                # Extract the energies, intensities and widths of the transition (different j and eigv)
                                x1s = [float(row[8]) for row in sat_sim_val_ind]
                                y1s = [float(float(row[11]) * generalVars.shakeweights[ind]) for row in sat_sim_val_ind]
                                w1s = [float(row[15]) for row in sat_sim_val_ind]
                                # Store the values in a list containing all the transitions to simulate
                                xs[index][ind] = x1s
                                ys[index][ind] = y1s
                                ws[index][ind] = w1s
                    elif sat == 'Diagram + Satellites':
                        # Extract the energies, intensities and widths of the transition (different j and eigv)
                        x1 = [float(row[8]) for row in diag_sim_val]
                        y1 = [float(row[11]) * (1 - sum(generalVars.shakeweights)) for row in diag_sim_val]
                        w1 = [float(row[15]) for row in diag_sim_val]
                        # Store the values in a list containing all the transitions to simulate
                        x[index] = x1
                        y[index] = y1
                        w[index] = w1
                        
                        # -----------------------------------------------------------------------------------------------
                        # Loop the shake labels read from the shake weights file
                        for ind, key in enumerate(generalVars.label1):
                            # Filter the specific combination of radiative transition and shake level (key) to simulate
                            sat_sim_val_ind = updateSatStickTransitionVals(low_level, high_level, key, sat_sim_val)
                            
                            # Check if there is at least one satellite transition
                            if len(sat_sim_val_ind) > 1:
                                # Extract the energies, intensities and widths of the transition (different j and eigv)
                                x1s = [float(row[8]) for row in sat_sim_val_ind]
                                y1s = [float(float(row[11]) * generalVars.shakeweights[ind]) for row in sat_sim_val_ind]
                                w1s = [float(row[15]) for row in sat_sim_val_ind]
                                # Store the values in a list containing all the transitions to simulate
                                xs[index][ind] = x1s
                                ys[index][ind] = y1s
                                ws[index][ind] = w1s
            # -------------------------------------------------------------------------------------------
            # Check if there are any transitions with missing rates
            for index, transition in enumerate(the_dictionary):
                if the_dictionary[transition]["selected_state"]:
                    if not x[index] and not any(xs[index]):
                        messagebox.showwarning("Wrong Transition", transition + " is not Available")
                        x[index] = []
                        bad_selection += 1
        else:
            # Reinitialize the x, y and w arrays for both the non satellites and satellites (xs, ys, ws) transitions
            x = [[] for i in range(len(the_aug_dictionary))]
            y = [[] for i in range(len(the_aug_dictionary))]
            w = [[] for i in range(len(the_aug_dictionary))]
            xs = [[[] for i in generalVars.label1] for j in x]
            ys = [[[] for i in generalVars.label1] for j in y]
            ws = [[[] for i in generalVars.label1] for j in w]

            # Loop possible auger transitions
            for index, transition in enumerate(the_aug_dictionary):
                if the_aug_dictionary[transition]["selected_state"]:
                    # Same as the stick but we dont care about the number of transitions
                    _, aug_stick_val = updateAugTransitionVals(transition, 0)
                    
                    # Extract the energies, intensities and widths of the transition (different j and eigv)
                    x1 = [float(row[8]) for row in aug_sim_val]
                    y1 = [float(row[9]) * (1 - sum(generalVars.shakeweights)) for row in aug_sim_val]
                    w1 = [float(row[10]) for row in aug_sim_val]
                    # Store the values in a list containing all the transitions to simulate
                    x[index] = x1
                    y[index] = y1
                    w[index] = w1

            # -------------------------------------------------------------------------------------------
            # Check if there are any transitions with missing rates
            for index, transition in enumerate(the_aug_dictionary):
                if the_aug_dictionary[transition]["selected_state"]:
                    if not x[index]:
                        messagebox.showwarning("Wrong Auger Transition", transition + " is not Available")
                        x[index] = []
                        bad_selection += 1

        # -------------------------------------------------------------------------------------------
        # In this block we calculate the xfinal set of x values to use in the simulation
        # We take into account if an experimental spectrum is loaded, the energy of the transitions and resolution
        try:
            if sat == 'Diagram':
                # Get the bounds of the energies and widths to plot
                deltaE, max_value, min_value = getBounds(x, w)

            elif sat == 'Satellites' or sat == 'Diagram + Satellites':
                # Get the bounds of the energies and widths to plot
                deltaE, max_value, min_value = getSatBounds(xs, ws)
            
            elif sat == 'Auger':
                # Get the bounds of the energies and widths to plot
                deltaE, max_value, min_value = getBounds(x, w)
            
            # Update the bounds considering the resolution and energy offset chosen
            array_input_max, array_input_min = updateMaxMinVals(x_mx, x_mn, deltaE, max_value, min_value, res, enoffset)
            
            # Calculate the grid of x values to use in the simulation
            xfinal = np.linspace(array_input_min, array_input_max, num=num_of_points)
        except ValueError:
            xfinal = np.zeros(num_of_points)
            if not bad_selection:
                messagebox.showerror("No Transition", "No transition was chosen")
            else:
                messagebox.showerror("Wrong Transition", "You chose " + str(bad_selection) + " invalid transition(s)")

        # ---------------------------------------------------------------------------------------------------------------
        # Load and plot the experimental spectrum
        exp_x = []
        exp_y = []
        exp_sigma = []
        min_exp_lim = 0
        max_exp_lim = 0
        
        # If we have loaded an experimental spectrum
        if load != 'No':
            # Initialize the residue plot and load the experimental spectrum
            graph_area, residues_graph, exp_spectrum = guiVars.setupExpPlot(f, load, element_name)
            
            # Extract the x, y, and sigma values from the loaded experimental spectrum
            xe, ye, sigma_exp = extractExpVals(exp_spectrum)
            
            # Bind the experimental spectrum to the calculated bounds
            exp_x, exp_y, exp_sigma = getBoundedExp(xe, ye, sigma_exp, enoffset, num_of_points, x_mx, x_mn)

            # Calculate the final energy values
            xfinal = np.array(np.linspace(min(exp_x) - enoffset, max(exp_x) - enoffset, num=num_of_points))

            # plot the experimental spectrum and residues graph
            guiVars.plotExp(graph_area, residues_graph, exp_x, exp_y, exp_sigma, normalize)

        # ---------------------------------------------------------------------------------------------------------------
        # Read the efficiency file if it was loaded
        efficiency_values = []
        energy_values = []
        if effic_file_name != 'No':
            try:
                # Read and load the file
                efficiency = loadEfficiency(effic_file_name)
                # Convert to floats
                for pair in efficiency:
                    energy_values.append(float(pair[0]))
                    efficiency_values.append(float(pair[1]))
            except FileNotFoundError:
                messagebox.showwarning("Error", "Efficiency File is not Avaliable")
        
        # ---------------------------------------------------------------------------------------------------------------
        # Calculate the final y values
        generalVars.ytot, generalVars.yfinal, generalVars.yfinals = y_calculator(sim, sat, peak, xfinal, x, y, w, xs, ys, ws, res, energy_values, efficiency_values, enoffset)

        # ---------------------------------------------------------------------------------------------------------------
        # Calculate the normalization multiplyer
        if load != 'No':
            normalization_var = normalizer(y0, max(exp_y), max(generalVars.ytot))
        else:
            # If we try to normalize without an experimental spectrum
            if guiVars.normalizevar.get() == 'ExpMax':
                messagebox.showwarning("No experimental spectrum is loaded", "Choose different normalization option")
                # Reset the normalizer to the default
                guiVars.normalizevar.set('No')
            normalization_var = normalizer(y0, 1, max(generalVars.ytot))
        
        # ---------------------------------------------------------------------------------------------------------------
        # Autofit:
        if autofit == 'Yes':
            # We can only fit if we have an experimental spectrum
            if load != 'No':
                # Initialize the fit parameters
                params = initializeFitParameters(exp_x, exp_y, enoffset, y0, res)
                
                # Minimize the function for the initialized parameters
                number_of_fit_variables = len(params.valuesdict())
                minner = Minimizer(func2min, params, fcn_args=(sim, exp_x, exp_y, num_of_points, sat, peak, x, y, w, xs, ys, ws, energy_values, efficiency_values, enoffset))
                result = minner.minimize()
                
                # Get the fitted values
                enoffset, y0, res, ytot_max = fetchFittedParams(result)

                # Calculate the energy values for the fitted parameters
                xfinal = np.array(np.linspace(min(exp_x) - enoffset, max(exp_x) - enoffset, num=num_of_points))
                # Calculate the normalizer multiplier for the fitted parameters
                normalization_var = normalizer(y0, max(exp_y), ytot_max)
                
                # Calculate the intensities for the fitted parameters
                generalVars.ytot, generalVars.yfinal, generalVars.yfinals = y_calculator(sim, sat, peak, xfinal, x, y, w, xs, ys, ws, res, energy_values, efficiency_values, enoffset)
                
                # Ask to save the fit
                if messagebox.askyesno("Fit Saving", "Do you want to save this fit?"):
                    # Get the report on the fit
                    report = fit_report(result)
                    # Export the fit to file
                    exportFit(time_of_click, report)
                
            else:
                messagebox.showerror("Error", "Autofit is only avaliable if an experimental spectrum is loaded")
        
        # ------------------------------------------------------------------------------------------------------------------------
        # Plot the selected lines
        if sat == 'Diagram':
            for index, key in enumerate(the_dictionary):
                if the_dictionary[key]["selected_state"]:
                    # Plot the selected transition
                    graph_area.plot(xfinal + enoffset, (np.array(generalVars.yfinal[index]) * normalization_var) + y0, label=key, color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                    graph_area.legend()
        elif sat == 'Satellites':
            for index, key in enumerate(the_dictionary):
                if the_dictionary[key]["selected_state"]:
                    for l, m in enumerate(generalVars.yfinals[index]):
                        # Dont plot the satellites that have a max y value of 0
                        if max(m) != 0:
                            # Plot the selected transition
                            graph_area.plot(xfinal + enoffset, (np.array(generalVars.yfinals[index][l]) * normalization_var) + y0, label=key + ' - ' + labeldict[generalVars.label1[l]], color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                            graph_area.legend()
        elif sat == 'Diagram + Satellites':
            # Diagram block
            for index, key in enumerate(the_dictionary):
                if the_dictionary[key]["selected_state"]:
                    # Plot the selected transition
                    graph_area.plot(xfinal + enoffset, (np.array(generalVars.yfinal[index]) * normalization_var) + y0, label=key, color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                    graph_area.legend()

            # Satellite block
            for index, key in enumerate(the_dictionary):
                if the_dictionary[key]["selected_state"]:
                    for l, m in enumerate(generalVars.yfinals[index]):
                        if max(m) != 0:
                            # Plot the selected transition
                            graph_area.plot(xfinal + enoffset, (np.array(generalVars.yfinals[index][l]) * normalization_var) + y0, label=key + ' - ' + labeldict[generalVars.label1[l]], color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                            graph_area.legend()
        elif sat == 'Auger':
            for index, key in enumerate(the_aug_dictionary):
                if the_aug_dictionary[key]["selected_state"]:
                    # Plot the selected transition
                    graph_area.plot(xfinal + enoffset, (np.array(generalVars.yfinal[index]) * normalization_var) + y0, label=key, color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                    graph_area.legend()
        if total == 'Total':
            # Plot the selected transition
            graph_area.plot(xfinal + enoffset, (generalVars.ytot * normalization_var) + y0, label='Total', ls='--', lw=2, color='k')
            graph_area.legend()
        
        # ------------------------------------------------------------------------------------------------------------------------
        # Calculate the residues
        if load != 'No':
            # Initialize a list for the interpolated experimental y values
            y_interp = [0 for i in range(len(exp_x))]
            # Interpolate the total plotted intensities
            f_interpolate = interp1d(xfinal + enoffset, (np.array(generalVars.ytot) * normalization_var) + y0, kind='cubic')
            
            # Initialize a list for the residue values
            y_res = [0 for x in range(len(exp_x))]
            # Temporary variable for the chi sum to calculate the chi^2
            chi_sum = 0
            
            # Loop the experimental x values
            for g, h in enumerate(exp_x):
                # Get the interpolated y values
                y_interp[g] = f_interpolate(h)
                # Calculate the chi sum from the interpolated values
                if normalize == 'ExpMax' or normalize == 'No':
                    y_res[g] = (exp_y[g] - y_interp[g])
                    chi_sum += (y_res[g] ** 2) / ((exp_sigma[g]**2))
                elif normalize == 'One':
                    y_res[g] = ((exp_y[g] / max(exp_y)) - y_interp[g])
                    chi_sum += (y_res[g] ** 2) / ((exp_sigma[g] / max(exp_y))**2)
            
            # Calculate the reduced chi^2 value
            generalVars.chi_sqrd = chi_sum / (len(exp_x) - number_of_fit_variables)
            # Plot the residues
            residues_graph.plot(exp_x, y_res)
            # Print the value in the console
            print("Valor Manual Chi", generalVars.chi_sqrd)
            # Put the chi^2 value in the plot legend
            residues_graph.legend(title="Red. \u03C7\u00B2 = " + "{:.5f}".format(generalVars.chi_sqrd))
        
        # ------------------------------------------------------------------------------------------------------------------------
        # Set the axis labels
        graph_area.set_ylabel('Intensity (arb. units)')
        graph_area.legend(title=element_name, title_fontsize='large')
        if load == 'No':
            graph_area.set_xlabel('Energy (eV)')
        
        # ------------------------------------------------------------------------------------------------------------------------
        # Automatic legend formating
        # Number of total labels to place in the legend
        number_of_labels = len(graph_area.legend().get_texts())
        # Initialize the numeber of legend columns
        legend_columns = 1
        # Initialize the number of legends in each columns
        labels_per_columns = number_of_labels / legend_columns
        # While we have more than 10 labels per column
        while labels_per_columns > 10:
            # Add one more column
            legend_columns += 1
            # Recalculate the number of labels per column
            labels_per_columns = number_of_labels / legend_columns
        
        # Place the legend with the final number of columns
        graph_area.legend(ncol=legend_columns)
    # --------------------------------------------------------------------------------------------------------------------------------------
    elif spectype == 'M_Simulation':
        # Variable for the number of transitions that were selected but no rates were found
        bad_selection = 0
        
        # Dictionary to hold the lines that arent found for each charge state
        bad_lines = {}

        # Radiative and Auger code has to be split due to the different dictionaries used for the transitions
        if sat != 'Auger':
            # Initialize the charge states we have to loop through
            charge_states = generalVars.rad_PCS + generalVars.rad_NCS

            # Before plotting we filter the charge state that need to be plotted (mix_val != 0)
            # And store the charge state values in this list
            ploted_cs = []

            # Loop the charge states
            for cs_index, cs in enumerate(charge_states):
                # Initialize the mixture value chosen for this charge state
                mix_val = '0.0'
                # Flag to check if this is a negative or positive charge state
                ncs = False

                # Check if this charge state is positive or negative and get the mix value
                if cs_index < len(generalVars.rad_PCS):
                    mix_val = generalVars.PCS_radMixValues[cs_index].get()
                else:
                    mix_val = generalVars.NCS_radMixValues[cs_index - len(generalVars.rad_PCS)].get()
                    ncs = True

                # Check if the mix value is not 0, otherwise no need to plot the transitions for this charge state
                if mix_val != '0.0':
                    ploted_cs.append(cs)

            # Reinitialize the x, y and w arrays for both the non satellites and satellites (xs, ys, ws) transitions
            # Taking into account the number of charge states to plot
            x = [[] for i in range(len(the_dictionary) * len(ploted_cs))]
            y = [[] for i in range(len(the_dictionary) * len(ploted_cs))]
            w = [[] for i in range(len(the_dictionary) * len(ploted_cs))]
            xs = [[[] for i in generalVars.label1] for j in x]
            ys = [[[] for i in generalVars.label1] for j in y]
            ws = [[[] for i in generalVars.label1] for j in w]

            # Loop the charge states to plot
            for cs_index, cs in enumerate(ploted_cs):
                # -------------------------------------------------------------------------------------------
                # Read the selected transitions
                # In this case we first store all the values for the transitions and then we calculate the y values to be plotted according to a profile
                for index, transition in enumerate(the_dictionary):
                    if the_dictionary[transition]["selected_state"]:
                        # Same as sticks but we dont care about the number of transitions
                        _, low_level, high_level, diag_sim_val, sat_sim_val = updateRadCSTrantitionsVals(transition, 0, ncs, cs)
                        
                        if sat == 'Diagram':
                            # Extract the energies, intensities and widths of the transition (different j and eigv)
                            # Here we also weight int the mix value
                            x1 = [float(row[8]) for row in diag_sim_val]
                            y1 = [float(row[11]) * (1 - sum(generalVars.shakeweights)) * float(row[-1]) for row in diag_sim_val]
                            w1 = [float(row[15]) for row in diag_sim_val]
                            # Store the values in a list containing all the transitions and charge states to simulate
                            x[cs_index * len(the_dictionary) + index] = x1
                            y[cs_index * len(the_dictionary) + index] = y1
                            w[cs_index * len(the_dictionary) + index] = w1
                        elif sat == 'Satellites':
                            # Loop the shake labels read from the shake weights file
                            for ind, key in enumerate(generalVars.label1):
                                # Filter the specific combination of radiative transition and shake level (key) to simulate
                                sat_sim_val_ind = updateSatTransitionVals(low_level, high_level, key, sat_stick_val)
                                
                                # Check if there is at least one satellite transition
                                if len(sat_sim_val_ind) > 1:
                                    # Extract the energies, intensities and widths of the transition (different j and eigv)
                                    x1s = [float(row[8]) for row in sat_sim_val_ind]
                                    y1s = [float(float(row[11]) * generalVars.shakeweights[ind] * float(row[-1])) for row in sat_sim_val_ind]
                                    w1s = [float(row[15]) for row in sat_sim_val_ind]
                                    # Store the values in a list containing all the charge states and transitions to simulate
                                    xs[cs_index * len(the_dictionary) + index][ind] = x1s
                                    ys[cs_index * len(the_dictionary) + index][ind] = y1s
                                    ws[cs_index * len(the_dictionary) + index][ind] = w1s
                        elif sat == 'Diagram + Satellites':
                            # Extract the energies, intensities and widths of the transition (different j and eigv)
                            x1 = [float(row[8])for row in diag_sim_val]
                            y1 = [float(row[11]) * (1 - sum(generalVars.shakeweights)) * float(row[-1]) for row in diag_sim_val]
                            w1 = [float(row[15]) for row in diag_sim_val]
                            # Store the values in a list containing all the charge states and transitions to simulate
                            x[cs_index * len(the_dictionary) + index] = x1
                            y[cs_index * len(the_dictionary) + index] = y1
                            w[cs_index * len(the_dictionary) + index] = w1
                            
                            # ---------------------------------------------------------------------------------------------------------------------
                            # Loop the shake labels read from the shake weights file
                            for ind, key in enumerate(generalVars.label1):
                                # Filter the specific combination of radiative transition and shake level (key) to simulate
                                sat_sim_val_ind = updateSatStickTransitionVals(low_level, high_level, key, sat_stick_val)
                                
                                # Check if there is at least one satellite transition
                                if len(sat_sim_val_ind) > 1:
                                    # Extract the energies, intensities and widths of the transition (different j and eigv)
                                    x1s = [float(row[8]) for row in sat_sim_val_ind]
                                    y1s = [float(float(row[11]) * generalVars.shakeweights[ind] * float(row[-1])) for row in sat_sim_val_ind]
                                    w1s = [float(row[15]) for row in sat_sim_val_ind]
                                    # Store the values in a list containing all the charge states and transitions to simulate
                                    xs[cs_index * len(the_dictionary) + index][ind] = x1s
                                    ys[cs_index * len(the_dictionary) + index][ind] = y1s
                                    ws[cs_index * len(the_dictionary) + index][ind] = w1s
                # -------------------------------------------------------------------------------------------
                # Check if there are any transitions with missing rates
                for index, transition in enumerate(the_dictionary):
                    if the_dictionary[transition]["selected_state"]:
                        if not x[cs_index * len(the_dictionary) + index] and not any(xs[cs_index * len(the_dictionary) + index]):
                            if cs not in bad_lines:
                                bad_lines[cs] = [transition]
                            else:
                                bad_lines[cs].append(transition)

                            x[cs_index * len(the_dictionary) + index] = []
                            bad_selection += 1

            # As there are multiples charge state we need a more detailed feedback for which lines failed
            # First we build the text that is going to be shown
            text = "Transitions not available for:\n"
            for cs in bad_lines:
                text += cs + ": " + str(bad_lines[cs]) + "\n"

            messagebox.showwarning("Wrong Transition", text)

            # Even if one of the transitions is not plotted for on charge state we might still have
            # At least one charge state where that transition is plotted
            # For this we show if there are any transitions that were plotted 0 times
            # Check if all charge states have at least one transition that was not plotted
            if len(bad_lines) == len(ploted_cs):
                # Initialize the intersection
                intersection = list(bad_lines.values())[-1]
                # Calculate the intersection of all the charge states
                for cs in bad_lines:
                    l1 = set(bad_lines[cs])
                    intersection = list(l1.intersection(intersection))

                # Show the common transitions that were not plotted
                messagebox.showwarning("Common Transitions", intersection)
            else:
                messagebox.showwarning("Common Transitions", "Every transition is plotted for at least 1 charge state.")
        else:
            # Initialize the charge states we have to loop through
            charge_states = generalVars.aug_PCS + generalVars.aug_NCS

            # Before plotting we filter the charge state that need to be plotted (mix_val != 0)
            # And store the charge state values in this list
            ploted_cs = []

            # Loop the charge states
            for cs_index, cs in enumerate(charge_states):
                # Initialize the mixture value chosen for this charge state
                mix_val = '0.0'
                # Flag to check if this is a negative or positive charge state
                ncs = False

                # Check if this charge state is positive or negative and get the mix value
                if cs_index < len(generalVars.aug_PCS):
                    mix_val = generalVars.PCS_augMixValues[cs_index].get()
                else:
                    mix_val = generalVars.NCS_augMixValues[cs_index - len(generalVars.aug_PCS)].get()
                    ncs = True
                
                # Check if the mix value is not 0, otherwise no need to plot the transitions for this charge state
                if mix_val != '0.0':
                    ploted_cs.append(cs)

            # Reinitialize the x, y and w arrays for both the non satellites and satellites (xs, ys, ws) transitions
            # Taking into account the number of charge states to plot
            x = [[] for i in range(len(the_aug_dictionary) * len(ploted_cs))]
            y = [[] for i in range(len(the_aug_dictionary) * len(ploted_cs))]
            w = [[] for i in range(len(the_aug_dictionary) * len(ploted_cs))]
            xs = [[[] for i in generalVars.label1] for j in x]
            ys = [[[] for i in generalVars.label1] for j in y]
            ws = [[[] for i in generalVars.label1] for j in w]

            # Loop the charge states to plot
            for cs_index, cs in enumerate(ploted_cs):
                # Loop the possible auger transitions
                for index, transition in enumerate(the_aug_dictionary):
                    if the_aug_dictionary[transition]["selected_state"]:
                        # Same as stick but we dont care about the number of transitions
                        _, aug_stick_val = updateAugCSTransitionsVals(transition, 0, ncs, cs)
                        
                        # Extract the energies, intensities and widths of the transition (different j and eigv)
                        x1 = [float(row[8]) for row in aug_sim_val]
                        y1 = [float(row[9]) * (1 - sum(generalVars.shakeweights)) * float(row[-1]) for row in aug_sim_val]
                        w1 = [float(row[10]) for row in aug_sim_val]
                        # Store the values in a list containing all the transitions to simulate
                        x[cs_index * len(the_aug_dictionary) + index] = x1
                        y[cs_index * len(the_aug_dictionary) + index] = y1
                        w[cs_index * len(the_aug_dictionary) + index] = w1

                # -------------------------------------------------------------------------------------------
                # Check if there are any transitions with missing rates
                for index, transition in enumerate(the_aug_dictionary):
                    if the_aug_dictionary[transition]["selected_state"]:
                        if not x[cs_index * len(the_aug_dictionary) + index]:
                            if cs not in bad_lines:
                                bad_lines[cs] = [transition]
                            else:
                                bad_lines[cs].append(transition)

                            x[cs_index * len(the_aug_dictionary) + index] = []
                            bad_selection += 1

            # Same report as for the radiative transitions
            text = "Transitions not available for:\n"
            for cs in bad_lines:
                text += cs + ": " + str(bad_lines[cs]) + "\n"

            messagebox.showwarning("Wrong Auger Transition", text)

            if len(bad_lines) == len(ploted_cs):
                intersection = list(bad_lines.values())[-1]
                for cs in bad_lines:
                    l1 = set(bad_lines[cs])
                    intersection = list(l1.intersection(intersection))

                messagebox.showwarning("Common Auger Transitions", intersection)
            else:
                messagebox.showwarning("Common Auger Transitions", "Every transition is plotted for at least 1 charge state.")

        # -------------------------------------------------------------------------------------------
        # In this block we calculate the xfinal set of x values to use in the simulation
        # We take into account if an experimental spectrum is loaded, the energy of the transitions and resolution
        try:
            if sat == 'Diagram':
                # Get the bounds of the energies and widths to plot
                deltaE, max_value, min_value = getBounds(x, w)

            elif sat == 'Satellites' or sat == 'Diagram + Satellites':
                # Get the bounds of the energies and widths to plot
                deltaE, max_value, min_value = getSatBounds(xs, ws)
                
            elif sat == 'Auger':
                # Get the bounds of the energies and widths to plot
                deltaE, max_value, min_value = getBounds(x, w)
            
            # Update the bounds considering the resolution and energy offset chosen
            array_input_max, array_input_min = updateMaxMinVals(x_mx, x_mn, deltaE, max_value, min_value, res, enoffset)
            
            # Calcular o array com os valores de xfinal igualmente espacados
            xfinal = np.linspace(array_input_min, array_input_max, num=num_of_points)
        except ValueError:
            xfinal = np.zeros(num_of_points)
            if not bad_selection:
                messagebox.showerror("No Transition", "No transition was chosen")
            else:
                messagebox.showerror("Wrong Transition", "You chose " + str(bad_selection) + " invalid transition(s)")

        # ---------------------------------------------------------------------------------------------------------------
        # Load and plot the experimental spectrum
        exp_x = []
        exp_y = []
        exp_sigma = []
        min_exp_lim = 0
        max_exp_lim = 0
        
        # If we have loaded an experimental spectrum
        if load != 'No':
            # Initialize the residue plot and load the experimental spectrum
            graph_area, residues_graph, exp_spectrum = guiVars.setupExpPlot(f, load, element_name)
            
            # Extract the x, y, and sigma values from the loaded experimental spectrum
            xe, ye, sigma_exp = extractExpVals(exp_spectrum)
            
            # Bind the experimental spectrum to the calculated bounds
            exp_x, exp_y, exp_sigma = getBoundedExp(xe, ye, sigma_exp, enoffset, num_of_points, x_mx, x_mn)

            # Calculate the final energy values
            xfinal = np.array(np.linspace(min(exp_x) - enoffset, max(exp_x) - enoffset, num=num_of_points))

            # plot the experimental spectrum and residues graph
            guiVars.plotExp(graph_area, residues_graph, exp_x, exp_y, exp_sigma, normalize)

        # ---------------------------------------------------------------------------------------------------------------
        # Read the efficiency file if it was loaded
        efficiency_values = []
        energy_values = []
        if effic_file_name != 'No':
            try:
                # Read and load the file
                efficiency = loadEfficiency(effic_file_name)
                # Convert to floats
                for pair in efficiency:
                    energy_values.append(float(pair[0]))
                    efficiency_values.append(float(pair[1]))
            except FileNotFoundError:
                messagebox.showwarning("Error", "Efficiency File is not Avaliable")
        
        # ---------------------------------------------------------------------------------------------------------------
        # Calculate the final y values
        generalVars.ytot, generalVars.yfinal, generalVars.yfinals = y_calculator(sim, sat, peak, xfinal, x, y, w, xs, ys, ws, res, energy_values, efficiency_values, enoffset)

        # ---------------------------------------------------------------------------------------------------------------
        # Calculate the normalization multiplyer
        if load != 'No':
            normalization_var = normalizer(y0, max(exp_y), max(generalVars.ytot))
        else:
            # If we try to normalize without an experimental spectrum
            if guiVars.normalizevar.get() == 'ExpMax':
                messagebox.showwarning("No experimental spectrum is loaded", "Choose different normalization option")
                # Reset the normalizer to the default
                guiVars.normalizevar.set('No')
            normalization_var = normalizer(y0, 1, max(generalVars.ytot))
        
        # ---------------------------------------------------------------------------------------------------------------
        # Autofit:
        if autofit == 'Yes':
            # We can only fit if we have an experimental spectrum
            if load != 'No':
                # Initialize the fit parameters
                params = initializeFitParameters(exp_x, exp_y, enoffset, y0, res)
                
                # Minimize the function for the initialized parameters
                number_of_fit_variables = len(params.valuesdict())
                minner = Minimizer(func2min, params, fcn_args=(sim, exp_x, exp_y, num_of_points, sat, peak, x, y, w, xs, ys, ws, energy_values, efficiency_values, enoffset))
                result = minner.minimize()
                
                # Get the fitted values
                enoffset, y0, res, ytot_max = fetchFittedParams(result)

                # Calculate the energy values for the fitted parameters
                xfinal = np.array(np.linspace(min(exp_x) - enoffset, max(exp_x) - enoffset, num=num_of_points))
                # Calculate the normalizer multiplier for the fitted parameters
                normalization_var = normalizer(y0, max(exp_y), ytot_max)
                
                # Calculate the intensities for the fitted parameters
                generalVars.ytot, generalVars.yfinal, generalVars.yfinals = y_calculator(sim, sat, peak, xfinal, x, y, w, xs, ys, ws, res, energy_values, efficiency_values, enoffset)
                
                # Ask to save the fit
                if messagebox.askyesno("Fit Saving", "Do you want to save this fit?"):
                    # Get the report on the fit
                    report = fit_report(result)
                    # Export the fit to file
                    exportFit(time_of_click, report)
                
            else:
                messagebox.showerror("Error", "Autofit is only avaliable if an experimental spectrum is loaded")
        
        # ------------------------------------------------------------------------------------------------------------------------
        # Plot the selected lines
        if sat == 'Diagram':
            for cs_index, cs in enumerate(ploted_cs):
                for index, key in enumerate(the_dictionary):
                    if the_dictionary[key]["selected_state"]:
                        # Plot the selected transition
                        graph_area.plot(xfinal + enoffset, (np.array(generalVars.yfinal[cs_index * len(the_dictionary) + index]) * normalization_var) + y0, label=cs + ' ' + key, color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                        graph_area.legend()
        elif sat == 'Satellites':
            for cs_index, cs in enumerate(ploted_cs):
                for index, key in enumerate(the_dictionary):
                    if the_dictionary[key]["selected_state"]:
                        for l, m in enumerate(generalVars.yfinals[cs_index * len(the_dictionary) + index]):
                            # Dont plot the satellites that have a max y value of 0
                            if max(m) != 0:
                                # Plot the selected transition
                                graph_area.plot(xfinal + enoffset, (np.array(generalVars.yfinals[cs_index * len(the_dictionary) + index][l]) * normalization_var) + y0, label=key + ' - ' + labeldict[generalVars.label1[l]], color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                                graph_area.legend()
        elif sat == 'Diagram + Satellites':
            for cs_index, cs in enumerate(ploted_cs):
                # Diagram block
                for index, key in enumerate(the_dictionary):
                    if the_dictionary[key]["selected_state"]:
                        # Plot the selected transition
                        graph_area.plot(xfinal + enoffset, (np.array(generalVars.yfinal[cs_index * len(the_dictionary) + index]) * normalization_var) + y0, label=cs + ' ' + key, color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                        graph_area.legend()

                # Satellite block
                for index, key in enumerate(the_dictionary):
                    if the_dictionary[key]["selected_state"]:
                        for l, m in enumerate(generalVars.yfinals[cs_index * len(the_dictionary) + index]):
                            if max(m) != 0:
                                # Plot the selected transition
                                graph_area.plot(xfinal + enoffset, (np.array(generalVars.yfinals[cs_index * len(the_dictionary) + index][l]) * normalization_var) + y0, label=cs + ' ' + key + ' - ' + labeldict[generalVars.label1[l]], color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                                graph_area.legend()
        elif sat == 'Auger':
            for cs_index, cs in enumerate(ploted_cs):
                for index, key in enumerate(the_aug_dictionary):
                    if the_aug_dictionary[key]["selected_state"]:
                        # Plot the selected transition
                        graph_area.plot(xfinal + enoffset, (np.array(generalVars.yfinal[cs_index * len(the_aug_dictionary) + index]) * normalization_var) + y0, label=cs + ' ' + key, color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                        graph_area.legend()
        if total == 'Total':
            # Plot the selected transition
            graph_area.plot(xfinal + enoffset, (generalVars.ytot * normalization_var) + y0, label='Total', ls='--', lw=2, color='k')  # Plot the simulation of all lines
            graph_area.legend()
        
        # ------------------------------------------------------------------------------------------------------------------------
        # Calculate the residues
        if load != 'No':
            # Initialize a list for the interpolated experimental y values
            y_interp = [0 for i in range(len(exp_x))]
            # Interpolate the total plotted intensities
            f_interpolate = interp1d(xfinal + enoffset, (np.array(generalVars.ytot) * normalization_var) + y0, kind='cubic')
            
            # Initialize a list for the residue values
            y_res = [0 for x in range(len(exp_x))]
            # Temporary variable for the chi sum to calculate the chi^2
            chi_sum = 0
            
            # Loop the experimental x values
            for g, h in enumerate(exp_x):
                # Get the interpolated y values
                y_interp[g] = f_interpolate(h)
                # Calculate the chi sum from the interpolated values
                if normalize == 'ExpMax' or normalize == 'No':
                    y_res[g] = (exp_y[g] - y_interp[g])
                    chi_sum += (y_res[g] ** 2) / ((exp_sigma[g]**2))
                elif normalize == 'One':
                    y_res[g] = ((exp_y[g] / max(exp_y)) - y_interp[g])
                    chi_sum += (y_res[g] ** 2) / ((exp_sigma[g] / max(exp_y))**2)
            
            # Calculate the reduced chi^2 value
            generalVars.chi_sqrd = chi_sum / (len(exp_x) - number_of_fit_variables)
            # Plot the residues
            residues_graph.plot(exp_x, y_res)
            # Print the value in the console
            print("Valor Manual Chi", generalVars.chi_sqrd)
            # Put the chi^2 value in the plot legend
            residues_graph.legend(title="Red. \u03C7\u00B2 = " + "{:.5f}".format(generalVars.chi_sqrd))
        
        # ------------------------------------------------------------------------------------------------------------------------
        # Set the axis labels
        graph_area.set_ylabel('Intensity (arb. units)')
        graph_area.legend(title=element_name, title_fontsize='large')
        if load == 'No':
            graph_area.set_xlabel('Energy (eV)')
        
        # ------------------------------------------------------------------------------------------------------------------------
        # Automatic legend formating
        # Number of total labels to place in the legend
        number_of_labels = len(graph_area.legend().get_texts())
        # Initialize the numeber of legend columns
        legend_columns = 1
        # Initialize the number of legends in each columns
        labels_per_columns = number_of_labels / legend_columns
        # While we have more than 10 labels per column
        while labels_per_columns > 10:
            # Add one more column
            legend_columns += 1
            # Recalculate the number of labels per column
            labels_per_columns = number_of_labels / legend_columns
        
        # Place the legend with the final number of columns
        graph_area.legend(ncol=legend_columns)

    f.canvas.draw()
