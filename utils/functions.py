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
from utils.fileIO import file_namer

#GUI utils for interface variables
import utils.interface as guiVars


element_name = None


# --------------------------------------------------------- #
#                                                           #
#            MATH FUNCTIONS FOR LINE PROFILES               #
#                                                           #
# --------------------------------------------------------- #

# Gaussian profile
def G(T, energy, intens, res, width):
    """ Return Gaussian line shape at x with HWHM alpha """
    y = [0 for j in range(len(T))]  # Criar um vector com o tamanho de T cheio de zeros
    for i, l in enumerate(T):
        y[i] = intens * np.sqrt(np.log(2) / np.pi) / (res + width) * np.exp(-((T[i] - energy) / (res + width)) ** 2 * np.log(2))
    return (y)

# Lorentzian profile
def L(T, energy, intens, res, width):
    """ Return Lorentzian line shape at x with HWHM gamma """
    y = [0 for j in range(len(T))]  # Criar um vector com o tamanho de T cheio de zeros
    for i, l in enumerate(T):
        y[i] = intens * (0.5 * (width + res) / np.pi) / ((T[i] - energy) ** 2 + (0.5 * (width + res)) ** 2)
    return (y)

# Voigt profile
def V(T, energy, intens, res, width):
    """ Return the Voigt line shape at x with Lorentzian component HWHM gamma and Gaussian component HWHM alpha."""
    y = [0 for j in range(len(T))]  # Criar um vector com o tamanho de T cheio de zeros
    for i, l in enumerate(T):
        sigma = res / np.sqrt(2 * np.log(2))
        y[i] = np.real(intens * wofz(complex(T[i] - energy, width/2) / sigma / np.sqrt(2))) / sigma / np.sqrt(2 * np.pi)
    return (y)



# --------------------------------------------------------- #
#                                                           #
# DETECTOR EFFICIENCY INTERPOLATOR AND NORMALIZER FUNCTION  #
#                                                           #
# --------------------------------------------------------- #

# Interpolate detector efficiency on the simulation xfinal
def detector_efficiency(energy_values, efficiency_values, xfinal, enoffset):
    # Initialize interpolated y values
    interpolated_effic = [0 for i in range(len(xfinal))]
    # Interpolate data
    effic_interpolation = interp1d(energy_values, np.array(efficiency_values)/100)
    
    # Loop the energy values with the simulated offset and store the efficiency
    for i, energy in enumerate(xfinal+enoffset):
        interpolated_effic[i] = effic_interpolation(energy)
        print(interpolated_effic[i], energy)
    return interpolated_effic

# Normalization function
def normalizer(y0, expy_max, ytot_max):
    # Get the type of normalization selected on the interface
    normalize = guiVars.normalizevar.get()
    
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
    # Criar uma lista de listas cheia de zeros que ira ser o yfinal para diagrama
    generalVars.yfinal = [[0 for i in range(len(xfinal))] for j in range(len(x))]
    generalVars.ytot = [0 for i in range(len(xfinal))]
    # Criar uma lista de listas cheia de zeros que ira ser o yfinal para satellites
    generalVars.yfinals = [[[0 for n in range(len(xfinal))] for i in generalVars.label1] for j in range(len(xs))]
    if transition_type == 'Diagram':
        b1 = 0
        for j, k in enumerate(y):
            # Ciclo sobre todas as riscas para somar um pico (voigt, lorentz ou gauss) para cada individual
            for i, n in enumerate(k):
                if fit_type == 'Voigt':
                    generalVars.yfinal[j] = np.add(generalVars.yfinal[j], V(xfinal, x[j][i], y[j][i], res, w[j][i]))
                elif fit_type == 'Lorentzian':
                    generalVars.yfinal[j] = np.add(generalVars.yfinal[j], L(xfinal, x[j][i], y[j][i], res, w[j][i]))
                elif fit_type == 'Gaussian':
                    generalVars.yfinal[j] = np.add(generalVars.yfinal[j], G(xfinal, x[j][i], y[j][i], res, w[j][i]))
                b1 += 100 / (len(y) * len(k))
                guiVars.progress_var.set(b1)
                sim.update_idletasks()
            if k != []:  # Excluir as linhas que nao foram seleccionados nos botoes
                generalVars.ytot = np.add(generalVars.ytot, generalVars.yfinal[j])

        b1 = 100
        guiVars.progress_var.set(b1)
        sim.update_idletasks()
    elif transition_type == 'Satellites':
        b1 = 0
        for j, k in enumerate(ys):
            for l, m in enumerate(ys[j]):
                # Ciclo sobre todas as riscas para somar um pico (voigt, lorentz ou gauss) para cada individual
                for i, n in enumerate(m):
                    if fit_type == 'Voigt':
                        generalVars.yfinals[j][l] = np.add(generalVars.yfinals[j][l], V(xfinal, xs[j][l][i], ys[j][l][i], res, ws[j][l][i]))
                    elif fit_type == 'Lorentzian':
                        generalVars.yfinals[j][l] = np.add(generalVars.yfinals[j][l], L(xfinal, xs[j][l][i], ys[j][l][i], res, ws[j][l][i]))
                    elif fit_type == 'Gaussian':
                        generalVars.yfinals[j][l] = np.add(generalVars.yfinals[j][l], G(xfinal, xs[j][l][i], ys[j][l][i], res, ws[j][l][i]))
                    b1 += 100 / (len(ys) * len(generalVars.label1) * len(m))
                    guiVars.progress_var.set(b1)
                    sim.update_idletasks()
                if m != []:  # Excluir as linhas que nao foram seleccionados nos botoes
                    generalVars.ytot = np.add(generalVars.ytot, generalVars.yfinals[j][l])
        b1 = 100
        guiVars.progress_var.set(b1)
        sim.update_idletasks()
    elif transition_type == 'Diagram + Satellites':
        b1 = 0
        for j, k in enumerate(y):
            # Ciclo sobre todas as riscas para somar um pico (voigt, lorentz ou gauss) para cada individual
            for i, n in enumerate(k):
                if fit_type == 'Voigt':
                    generalVars.yfinal[j] = np.abs(np.add(generalVars.yfinal[j], V(xfinal, x[j][i], y[j][i], res, w[j][i])))
                elif fit_type == 'Lorentzian':
                    generalVars.yfinal[j] = np.abs(np.add(generalVars.yfinal[j], L(xfinal, x[j][i], y[j][i], res, w[j][i])))
                elif fit_type == 'Gaussian':
                    generalVars.yfinal[j] = np.abs(np.add(generalVars.yfinal[j], G(xfinal, x[j][i], y[j][i], res, w[j][i])))
                b1 += 200 / (len(y) * len(k))
                guiVars.progress_var.set(b1)
                sim.update_idletasks()
            if k != []:  # Excluir as linhas que nao foram seleccionados nos botoes
                generalVars.ytot = np.add(generalVars.ytot, generalVars.yfinal[j])

        b1 = 50
        guiVars.progress_var.set(b1)
        sim.update_idletasks()
        for j, k in enumerate(ys):
            for l, m in enumerate(ys[j]):
                # Ciclo sobre todas as riscas para somar um pico (voigt, lorentz ou gauss) para cada individual
                for i, n in enumerate(m):
                    if fit_type == 'Voigt':
                        generalVars.yfinals[j][l] = np.abs(np.add(generalVars.yfinals[j][l], V(xfinal, xs[j][l][i], ys[j][l][i], res, ws[j][l][i])))
                    elif fit_type == 'Lorentzian':
                        generalVars.yfinals[j][l] = np.abs(np.add(generalVars.yfinals[j][l], L(xfinal, xs[j][l][i], ys[j][l][i], res, ws[j][l][i])))
                    elif fit_type == 'Gaussian':
                        generalVars.yfinals[j][l] = np.abs(np.add(generalVars.yfinals[j][l], G(xfinal, xs[j][l][i], ys[j][l][i], res, ws[j][l][i])))
                    b1 += 100 / (len(ys) * len(generalVars.label1) * len(m))
                    guiVars.progress_var.set(b1)
                    sim.update_idletasks()
                if m != []:  # Excluir as linhas que nao foram seleccionados nos botoes
                    generalVars.ytot = np.add(generalVars.ytot, generalVars.yfinals[j][l])
        b1 = 100
        guiVars.progress_var.set(b1)
        sim.update_idletasks()
    elif transition_type == 'Auger':
        # Criar uma lista de listas cheia de zeros que ira ser o yfinal para diagrama
        generalVars.yfinal = [[0 for i in range(len(xfinal))] for j in range(len(x))]
        generalVars.ytot = [0 for i in range(len(xfinal))]
        # Criar uma lista de listas cheia de zeros que ira ser o yfinal para satellites
        generalVars.yfinals = [[[0 for n in range(len(xfinal))] for i in generalVars.label1] for j in range(len(xs))]

        b1 = 0
        for j, k in enumerate(y):
            # Ciclo sobre todas as riscas para somar um pico (voigt, lorentz ou gauss) para cada individual
            for i, n in enumerate(k):
                if fit_type == 'Voigt':
                    generalVars.yfinal[j] = np.add(generalVars.yfinal[j], V(xfinal, x[j][i], y[j][i], res, w[j][i]))
                elif fit_type == 'Lorentzian':
                    generalVars.yfinal[j] = np.add(generalVars.yfinal[j], L(xfinal, x[j][i], y[j][i], res, w[j][i]))
                elif fit_type == 'Gaussian':
                    generalVars.yfinal[j] = np.add(generalVars.yfinal[j], G(xfinal, x[j][i], y[j][i], res, w[j][i]))
                b1 += 100 / (len(y) * len(k))
                guiVars.progress_var.set(b1)
                sim.update_idletasks()
            if k != []:  # Excluir as linhas que nao foram seleccionados nos botoes
                generalVars.ytot = np.add(generalVars.ytot, generalVars.yfinal[j])

        b1 = 100
        guiVars.progress_var.set(b1)
        sim.update_idletasks()

    if guiVars.effic_var.get() != 'No':
        detector_effi = detector_efficiency(energy_values, efficiency_values, xfinal, enoffset)
        return generalVars.ytot*np.array(detector_effi), generalVars.yfinal*np.array(detector_effi), generalVars.yfinals*np.array(detector_effi)
    else:
        return generalVars.ytot, generalVars.yfinal, generalVars.yfinals

# Initialize the parameters for fitting
def initializeFitParameters(exp_x, exp_y, enoffset, y0, res):
    # Criar os parametros que vão ser otimizados
    params = Parameters()

    # Offset em energia
    # O offset vai variar entre o valor introduzido +/- 10% do tamanho do gráfico
    xoff_lim = (max(exp_x) - min(exp_x)) * 0.1
    params.add('xoff', value=enoffset, min=enoffset - xoff_lim, max=enoffset + xoff_lim)

    # Offset no yy
    yoff_lim = (max(exp_y) - min(exp_y)) * 0.1
    params.add('yoff', value=y0, min=y0 - yoff_lim, max=y0 + yoff_lim)

    # Resolução experimental
    res_lim = res * 3
    params.add('res', value=res, min=0.01, max=res + res_lim)
    
    # Parametro na Normalization var
    params.add('ytot_max', value=max(generalVars.ytot))
    
    return params

# Extract the values of the fitted parameters
def fetchFittedParams(result):
    # Offset em energia a ser definido para o plot final das linhas
    enoffset = result.params['xoff'].value
    guiVars.energy_offset.set(enoffset)
    # Offset no yy a ser definido para o plot final das linhas
    y0 = result.params['yoff'].value
    guiVars.yoffset.set(y0)
    # Resolução experimental a ser definido para o plot final das linhas
    res = result.params['res'].value
    guiVars.exp_resolution.set(res)
    # normalization_var = result.params['normal'].value
    ytot_max = result.params['ytot_max'].value
    
    return enoffset, y0, res, ytot_max

# Create the function to be minimized for the fitting
def func2min(params, sim, exp_x, exp_y, num_of_points, sat, peak, x, y, w, xs, ys, ws, energy_values, efficiency_values, enoffset):
    global xfinal
    
    # Normalizer for the function to match the plotted values
    normalize = guiVars.normalizevar.get()
    # Initialize the interpolated y values
    y_interp = [0 for i in range(len(exp_x))]
    
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
    
    for g, h in enumerate(exp_x):
        # Obtemos o valor de y interpolado pela função definida a cima
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
    # Filter the satellite rates data for the combinations of selected levels
    sat_stick_val_ind1 = [line for line in sat_stick_val if low_level + key in line[1] and key + high_level in line[5]]
    sat_stick_val_ind2 = [line for line in sat_stick_val if low_level + key in line[1] and high_level + key in line[5] and key != high_level]
    sat_stick_val_ind3 = [line for line in sat_stick_val if key + low_level in line[1] and key + high_level in line[5]]
    sat_stick_val_ind4 = [line for line in sat_stick_val if key + low_level in line[1] and high_level + key in line[5] and key != high_level]
    sat_stick_val_ind = sat_stick_val_ind1 + sat_stick_val_ind2 + sat_stick_val_ind3 + sat_stick_val_ind4
    
    return sat_stick_val

# Update the auger rates for the selected transition
def updateAugTransitionVals(transition, num):
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
    deltaE = []
    # Percorremos as listas guardadas em x. k é a lista e i o indice onde ela está guardada em x.
    for j, k in enumerate(x):
        if k != []:  # Se a lista não estiver vazia, guardamos em deltaE a diferença entre o seu valor máximo e mí­nimo
            deltaE.append(max(x[j]) - min(x[j]))

    max_value = max([max(x[i]) for i in range(len(x)) if x[i] != []]) + 4 * max([max(w[i]) for i in range(len(w)) if w[i] != []])
    min_value = min([min(x[i]) for i in range(len(x)) if x[i] != []]) - 4 * max([max(w[i]) for i in range(len(w)) if w[i] != []])
    
    return deltaE, max_value, min_value

# Calculate the x bound from the simulated satellite transition energy and width data
def getSatBounds(xs, ws):
    deltaE = []
    # Ciclo sobre os elementos de x (ka1, ka2, kb1, etc... 7 no total)
    for j, k in enumerate(xs):
        for l, m in enumerate(xs[j]):
            if m != []:
                deltaE.append(max(m) - min(m))
    
    max_value = max([max(xs[i][j]) for i in range(len(xs)) for j in range(len(xs[i])) if xs[i][j] != []]) + max([max(ws[i][j]) for i in range(len(ws)) for j in range(len(ws[i])) if ws[i][j] != []])  # valor max de todos os elementos de xs (satt) que tem 7 linhas(ka1, ka2, etc) e o tamanho da lista label1 dentro de cada linha
    min_value = min([min(xs[i][j]) for i in range(len(xs)) for j in range(len(xs[i])) if xs[i][j] != []]) - max([max(ws[i][j]) for i in range(len(ws)) for j in range(len(ws[i])) if ws[i][j] != []])
    
    return deltaE, max_value, min_value

# Update the bounds for the user selected bounds (Auto or value)
def updateMaxMinVals(x_mx, x_mn, deltaE, max_value, min_value, res, enoffset):
    # Definimos o x Mínimo que queremos plotar. Pode ser definido automáticamente ou pelo valor x_mn
    if x_mn == 'Auto':  # x_mn é inicializado a Auto
        if res <= 0.2 * (min(deltaE)):
            array_input_min = min_value - 2 * min(deltaE)
        else:
            array_input_min = min_value - 2 * res * min(deltaE)
    else:
        array_input_min = float(x_mn) - enoffset
    # Definimos o x Máximo que queremos plotar. Pode ser definido automáticamente ou pelo valor x_mx
    if x_mx == 'Auto':  # x_mx é inicializado a Auto
        if res <= 0.2 * (min(deltaE)):
            array_input_max = max_value + 2 * min(deltaE)
        else:
            array_input_max = max_value + 2 * res * (min(deltaE))
    else:
        array_input_max = float(x_mx) - enoffset
    
    return array_input_max, array_input_min
    
# Extract x, y and sigma values from the read experimental file
def extractExpVals(exp_spectrum):
    for i, it in enumerate(exp_spectrum):
        # Transformar os valores do espectro experimental para float
        for j, itm in enumerate(exp_spectrum[i]):
            if exp_spectrum[i][j] != '':
                exp_spectrum[i][j] = float(itm)
    
    # Split the values into x and y
    xe = np.array([float(row[0]) for row in exp_spectrum])
    ye = np.array([float(row[1]) for row in exp_spectrum])
    # Se o espectro experimental tiver 3 colunas a terceira sera a incerteza
    if len(exp_spectrum[0]) >= 3:
        sigma_exp = np.array([float(row[2]) for row in exp_spectrum])
    else:  # Caso contrario utiliza-se raiz do numero de contagens como a incerteza de cada ponto
        sigma_exp = np.sqrt(ye)
    
    return xe, ye, sigma_exp

# Bind the experimental values into the chosen bounds
def getBoundedExp(xe, ye, sigma_exp, enoffset, num_of_points, x_mx, x_mn):
    exp_x = []
    exp_y = []
    exp_sigma = []
    
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

# Stick plotter. Plots a stick for each transition
def stem_ploter(transition_values, transition, spec_type, ind, key):
    # Set of colors to choose from when plotting
    col2 = [['b'], ['g'], ['r'], ['c'], ['m'], ['y'], ['k']]
    
    # Extract the energy values
    x = [float(row[8]) for row in transition_values]

    # Add extra values before and after to make the y start and terminate on 0
    max_value = max(x)
    min_value = min(x)
    x.insert(0, 2 * min_value - max_value)
    x.append(2 * max_value - min_value)
    
    # Calculate the y's weighted with the shake weights depending on the spectrum type and plot the sticks
    # In the case of charge state simulation the y's are also weighted by the selected mixture percentages
    if spec_type == 'Diagram':
        y = [float(row[11]) * (1 - 0.01 * sum(generalVars.shakeweights)) for row in transition_values]
        y.insert(0, 0)
        y.append(0)
        a.stem(x, y, markerfmt=' ', linefmt=str(col2[np.random.randint(0, 7)][0]), label=str(transition), use_line_collection=True)
        a.legend(loc='best', numpoints=1)
    elif spec_type == 'Satellites':
        sy_points = [float(float(row[11]) * 0.01 * generalVars.shakeweights[ind]) for row in transition_values]
        sy_points.insert(0, 0)
        sy_points.append(0)
        a.stem(x, sy_points, markerfmt=' ', linefmt=str(col2[np.random.randint(0, 7)][0]), label=transition + ' - ' + labeldict[key], use_line_collection=True)  # Plot a stemplot
        a.legend(loc='best', numpoints=1)
    elif spec_type == 'Auger':
        y = [float(row[11]) * (1 - 0.01 * sum(generalVars.shakeweights)) for row in transition_values]
        y.insert(0, 0)
        y.append(0)
        a.stem(x, y, markerfmt=' ', linefmt=str(col2[np.random.randint(0, 7)][0]), label=str(transition), use_line_collection=True)
        a.legend(loc='best', numpoints=1)
    elif spec_type == 'Diagram_CS':
        y = [float(row[11]) * (1 - 0.01 * sum(generalVars.shakeweights)) * float(row[-1]) for row in transition_values]
        y.insert(0, 0)
        y.append(0)
        a.stem(x, y, markerfmt=' ', linefmt=str(col2[np.random.randint(0, 7)][0]), label=str(transition), use_line_collection=True)
        a.legend(loc='best', numpoints=1)
    elif spec_type == 'Satellites_CS':
        sy_points = [float(float(row[11]) * 0.01 * generalVars.shakeweights[ind] * float(row[-1])) for row in transition_values]
        sy_points.insert(0, 0)
        sy_points.append(0)
        a.stem(x, sy_points, markerfmt=' ', linefmt=str(col2[np.random.randint(0, 7)][0]), label=transition + ' - ' + labeldict[key], use_line_collection=True)  # Plot a stemplot
        a.legend(loc='best', numpoints=1)
    elif spec_type == 'Auger_CS':
        y = [float(row[11]) * (1 - 0.01 * sum(generalVars.shakeweights)) * float(row[-1]) for row in transition_values]  # *float(row[11])*float(row[9])
        y.insert(0, 0)
        y.append(0)
        a.stem(x, y, markerfmt=' ', linefmt=str(col2[np.random.randint(0, 7)][0]), label=str(transition), use_line_collection=True)
        a.legend(loc='best', numpoints=1)
    
    # --------------------------------------------------------------------------------------------------------------------------
    # Tratamento da Legenda
    a.legend(title=element_name, title_fontsize='large')
    a.legend(title=element_name)
    # Descubro quantas entradas vai ter a legenda
    number_of_labels = len(a.legend().get_texts())
    # Inicialmente há uma coluna, mas vou fazer contas para ter 10 itens por coluna no máximo
    legend_columns = 1
    labels_per_columns = number_of_labels / legend_columns  # Numero de entradas por coluna
    while labels_per_columns > 10:  # Se a priori for menos de 10 entradas por coluna, não acontece nada
        legend_columns += 1  # Se houver mais que 10 entradas por coluna, meto mais uma coluna
        # Recalculo o numero de entradas por coluna
        labels_per_columns = number_of_labels / legend_columns
    # Defino o numero de colunas na legenda = numero de colunas necessárias para não ter mais de 10 entradas por coluna
    a.legend(ncol=legend_columns)

# Profile plotter. Plots each transition, applying the selected profile
def plot_stick(sim, f, graph_area):
    # Obtenho o a data e hora exacta para dar nome aos ficheiros a gravar
    time_of_click = datetime.now()
    
    global xfinal, exp_x, exp_y, residues_graph
    
    # Reinitialize the residues graph and experimental points
    residues_graph = None
    exp_x = None
    exp_y = None
    
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
    
    # Initialize the x, y and w arrays for both the non satellites and satellites (xs, ys, ws) transitions
    x = [[] for i in range(len(the_dictionary))]
    y = [[] for i in range(len(the_dictionary))]
    w = [[] for i in range(len(the_dictionary))]
    xs = [[[] for i in generalVars.label1] for j in x]
    ys = [[[] for i in generalVars.label1] for j in y]
    ws = [[[] for i in generalVars.label1] for j in w]
    
    # Initialize the normalization multiplier
    normalization_var = 1
    # --------------------------------------------------------------------------------------------------------------------------
    if spectype == 'Stick':
        # Duas variáveis que servem para ver se há alguma transição mal escolhida.
        # A primeira serve para saber o numero total de transiões escolhidas e a segunda para anotar quantas tranisções erradas se escolheram
        num_of_transitions = 0
        bad_selection = 0
        
        # Radiative and Auger code has to be split due to the different dictionaries used for the transitions
        if sat != 'Auger':
            # Loop possible radiative transitions
            for transition in the_dictionary:
                # Se a transição estiver selecionada:
                if the_dictionary[transition]["selected_state"]:
                    # Filter the radiative and satellite rates corresponding to this transition
                    num_of_transitions, low_level, high_level, diag_stick_val, sat_stick_val = updateRadTransitionVals(transition, num_of_transitions)
                    
                    # -------------------------------------------------------------------------------------------
                    if sat == 'Diagram':
                        if not diag_stick_val:  # Se não ouver dados no vetor da diagrama
                            # Crio um vector de zeros para o programa continuar a correr
                            diag_stick_val = [['0' for i in range(16)]]
                            # Mostro no ecrã a transição errada que escolheram
                            messagebox.showwarning("Wrong Transition", transition + " is not Available")
                            bad_selection += 1  # incremento o numero de transições "mal" escolhidas
                        stem_ploter(diag_stick_val, transition, 'Diagram', 0, 0)
                    elif sat == 'Satellites':
                        if not sat_stick_val:  # Se não ouver nada no vetor das satelites
                            sat_stick_val = [['0' for i in range(16)]]
                            # Mostro no ecrã a transição errada que escolheram
                            messagebox.showwarning("Wrong Transition", transition + " is not Available")
                            bad_selection += 1  # incremento o numero de transições "mal" escolhidas
                        
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
                        if not diag_stick_val:  # Se não ouver dados no vetor da diagrama
                            # Crio um vector de zeros para o programa continuar a correr
                            diag_stick_val = [['0' for i in range(16)]]
                            # Mostro no ecrã a transição errada que escolheram
                            messagebox.showwarning("Wrong Transition", "Diagram info. for " + transition + " is not Available")
                            bad_selection += 1  # incremento o numero de transições "mal" escolhidas
                        stem_ploter(diag_stick_val, transition, 'Diagram', 0, 0)
                        
                        if not sat_stick_val:  # Se não ouver nada no vetor das satelites
                            sat_stick_val = [['0' for i in range(16)]]
                            # Mostro no ecrã a transição errada que escolheram
                            messagebox.showwarning("Wrong Transition", "Satellites info.  for " + transition + " is not Available")
                            bad_selection += 1  # incremento o numero de transições "mal" escolhidas
                        
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
                # Se a transição estiver selecionada:
                if the_aug_dictionary[transition]["selected_state"]:
                    # Filter the auger rates for this transition
                    num_of_transitions, aug_stick_val = updateAugTransitionVals(transition, num_of_transitions)
                    
                    if not aug_stick_val:  # Se não ouver dados no vetor da diagrama
                        # Crio um vector de zeros para o programa continuar a correr (Em string porque estava a dar um erro qq quando punha em int)(range 16 porque é o tamanho da
                        aug_stick_val = [['0' for i in range(16)]]
                        # linha do ficheiro que supostamente preencheria este vertor)
                        # Mostro no ecrã a transição errada que escolheram
                        messagebox.showwarning("Wrong Transition", "Auger info. for " + transition + " is not Available")
                        bad_selection += 1  # incremento o numero de transições "mal" escolhidas
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
        # Duas variáveis que servem para ver se há alguma transição mal escolhida.
        # A primeira serve para saber o numero total de transiões escolhidas e a segunda para anotar quantas tranisções erradas se escolheram
        num_of_transitions = 0
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
                        # Se a transição estiver selecionada:
                        if the_dictionary[transition]["selected_state"]:
                            # Filter the radiative and satellite rates for this transition and charge state
                            num_of_transitions, low_level, high_level, diag_stick_val, sat_stick_val = updateRadCSTrantitionsVals(transition, num_of_transitions, ncs, cs)
                            
                            if sat == 'Diagram':
                                if not diag_stick_val:  # Se não ouver dados no vetor da diagrama
                                    # Crio um vector de zeros para o programa continuar a correr
                                    diag_stick_val = [['0' for i in range(16)]]
                                    # Mostro no ecrã a transição errada que escolheram
                                    messagebox.showwarning("Wrong Transition", transition + " is not Available for charge state: " + cs)
                                    bad_selection += 1  # incremento o numero de transições "mal" escolhidas
                                stem_ploter(diag_stick_val, cs + ' ' + transition, 'Diagram_CS', 0, 0)
                            elif sat == 'Satellites':
                                if not sat_stick_val:  # Se não ouver nada no vetor das satelites
                                    sat_stick_val = [['0' for i in range(16)]]
                                    # Mostro no ecrã a transição errada que escolheram
                                    messagebox.showwarning("Wrong Transition", transition + " is not Available for charge state: " + cs)
                                    bad_selection += 1  # incremento o numero de transições "mal" escolhidas
                                
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
                                if not diag_stick_val:  # Se não ouver dados no vetor da diagrama
                                    # Crio um vector de zeros para o programa continuar a correr
                                    diag_stick_val = [['0' for i in range(16)]]
                                    # Mostro no ecrã a transição errada que escolheram
                                    messagebox.showwarning("Wrong Transition", "Diagram info. for " + transition + " is not Available")
                                    bad_selection += 1  # incremento o numero de transições "mal" escolhidas
                                stem_ploter(diag_stick_val, cs + ' ' + transition, 'Diagram_CS', 0, 0)
                                if not sat_stick_val:  # Se não ouver nada no vetor das satelites
                                    sat_stick_val = [['0' for i in range(16)]]
                                    # Mostro no ecrã a transição errada que escolheram
                                    messagebox.showwarning("Wrong Transition", "Satellites info.  for " + transition + " is not Available")
                                    bad_selection += 1  # incremento o numero de transições "mal" escolhidas
                                
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
                        # Se a transição estiver selecionada:
                        if the_aug_dictionary[transition]["selected_state"]:
                            # Filter the auger rates for this transition and charge state
                            num_of_transitions, aug_stick_val = updateAugCSTransitionsVals(transition, num_of_transitions, ncs, cs)
                            
                            if not aug_stick_val:  # Se não ouver dados no vetor da diagrama
                                # Crio um vector de zeros para o programa continuar a correr
                                aug_stick_val = [['0' for i in range(16)]]
                                # Mostro no ecrã a transição errada que escolheram
                                messagebox.showwarning("Wrong Transition", "Auger info. for " + transition + " is not Available for charge state: " + cs)
                                bad_selection += 1  # incremento o numero de transições "mal" escolhidas
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
        # Variável para contar as transições erradas
        bad_selection = 0

        if sat != 'Auger':
            # -------------------------------------------------------------------------------------------
            # Leitura dos valores das transições selecionadas
            # Contrariamente ao spectype == 'Stick' onde os plots são feitos quando se trata de cada risca, aqui,
            # o  que se faz é obter os valores necessários para os plots. Não se faz nenhum plot em si dentro deste ciclo.
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
            # Verificar se se selecionaram transições indísponíveis
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
            # Verificar se se selecionaram transições indísponíveis
            for index, transition in enumerate(the_aug_dictionary):
                if the_aug_dictionary[transition]["selected_state"]:
                    if not x[index]:
                        messagebox.showwarning("Wrong Auger Transition", transition + " is not Available")
                        x[index] = []
                        bad_selection += 1

        # -------------------------------------------------------------------------------------------
        # Obtenção do valor de xfinal a usar nos cáclulos dos yy
        # Caso não seja selecionado um espectro experimental, porque se fo xfinal é mudado
        # Calcular a dispersão em energia das varias riscas para criar o array de valores de x a plotar
        # em funcao desta dispersão e da resolução experimental
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
        # Load e plot o espectro experimental
        exp_x = []
        exp_y = []
        exp_sigma = []
        min_exp_lim = 0
        max_exp_lim = 0
        if load != 'No':  # procedimento para fazer o plot experimental
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
        # Leitura dos valores da eficácia do detector:
        efficiency_values = []
        energy_values = []
        if effic_file_name != "No":
            try:
                efficiency = list(csv.reader(open(effic_file_name, 'r')))
                for pair in efficiency:
                    energy_values.append(float(pair[0]))
                    efficiency_values.append(float(pair[1]))
            except FileNotFoundError:
                messagebox.showwarning("Error", "Efficiency File is not Avaliable")
        
        # ---------------------------------------------------------------------------------------------------------------
        # Calculate the final y values
        generalVars.ytot, generalVars.yfinal, generalVars.yfinals = y_calculator(sim, sat, peak, xfinal, x, y, w, xs, ys, ws, res, energy_values, efficiency_values, enoffset)

        # ---------------------------------------------------------------------------------------------------------------
        # Cálculo da variável de normalização
        if load != 'No':
            normalization_var = normalizer(y0, max(exp_y), max(generalVars.ytot))
        else:
            if guiVars.normalizevar.get() == 'ExpMax':  # Se tentarem normalizar ao maximo experimental sem terem carregado espectro
                messagebox.showwarning("No experimental spectrum is loaded", "Choose different normalization option")  # Apresenta aviso
                # Define a variavel global de normalização para não normalizar
                guiVars.normalizevar.set('No')
            normalization_var = normalizer(y0, 1, max(generalVars.ytot))
        
        # ---------------------------------------------------------------------------------------------------------------
        # Autofit:
        if autofit == 'Yes':
            # Fazemos fit apenas se houver um gráfico experimental carregado
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
                
                if messagebox.askyesno("Fit Saving", "Do you want to save this fit?"):
                    with open(file_namer("Fit", time_of_click, ".txt"), 'w') as file:
                        file.write(fit_report(result))
                    print(fit_report(result))
                
            else:
                messagebox.showerror("Error", "Autofit is only avaliable if an experimental spectrum is loaded")
        
        # ------------------------------------------------------------------------------------------------------------------------
        # Plot das linhas
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
                        if max(m) != 0:  # Excluir as linhas que nao foram seleccionados nos botoes
                            # Plot the selected transition
                            graph_area.plot(xfinal + enoffset, (np.array(generalVars.yfinals[index][l]) * normalization_var) + y0, label=key + ' - ' + labeldict[generalVars.label1[l]], color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                            graph_area.legend()
        elif sat == 'Diagram + Satellites':
            for index, key in enumerate(the_dictionary):
                if the_dictionary[key]["selected_state"]:
                    # Plot the selected transition
                    graph_area.plot(xfinal + enoffset, (np.array(generalVars.yfinal[index]) * normalization_var) + y0, label=key, color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                    graph_area.legend()

            for index, key in enumerate(the_dictionary):
                if the_dictionary[key]["selected_state"]:
                    for l, m in enumerate(generalVars.yfinals[index]):
                        if max(m) != 0:  # Excluir as linhas que nao foram seleccionados nos botoes
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
            graph_area.plot(xfinal + enoffset, (generalVars.ytot * normalization_var) + y0, label='Total', ls='--', lw=2, color='k')  # Plot the simulation of all lines
            graph_area.legend()
        
        # ------------------------------------------------------------------------------------------------------------------------
        # Cálculo dos Residuos
        if load != 'No':
            # Criar lista vazia para o gráfico de resíduos
            y_interp = [0 for i in range(len(exp_x))]
            # Interpolate the total plotted intensities
            f_interpolate = interp1d(xfinal + enoffset, (np.array(generalVars.ytot) * normalization_var) + y0, kind='cubic')
            
            # Vetor para guardar o y dos residuos (não precisamos de guardar o x porque é igual ao exp_x
            y_res = [0 for x in range(len(exp_x))]
            # Variável para a soma do chi quadrado
            chi_sum = 0
            # Percorremos todos os valores de x
            for g, h in enumerate(exp_x):
                # Obtemos o valor de y interpolado pela função definida a cima
                y_interp[g] = f_interpolate(h)
                # Cálculamos o y dos residuos subtraindo o interpolado ao experimental
                if normalize == 'ExpMax' or normalize == 'No':
                    y_res[g] = (exp_y[g] - y_interp[g])
                    chi_sum += (y_res[g] ** 2) / ((exp_sigma[g]**2))
                elif normalize == 'One':
                    y_res[g] = ((exp_y[g] / max(exp_y)) - y_interp[g])
                    chi_sum += (y_res[g] ** 2) / ((exp_sigma[g] / max(exp_y))**2)
            
            
            generalVars.chi_sqrd = chi_sum / (len(exp_x) - number_of_fit_variables)
            residues_graph.plot(exp_x, y_res)
            print("Valor Manual Chi", generalVars.chi_sqrd)
            residues_graph.legend(title="Red. \u03C7\u00B2 = " + "{:.5f}".format(generalVars.chi_sqrd))
        
        # ------------------------------------------------------------------------------------------------------------------------
        # Definição do label do eixo yy e, consoante haja ou não um gráfico de resí­duos, do eixo  xx
        graph_area.set_ylabel('Intensity (arb. units)')
        graph_area.legend(title=element_name, title_fontsize='large')
        if load == 'No':
            graph_area.set_xlabel('Energy (eV)')
        
        # ------------------------------------------------------------------------------------------------------------------------
        # Controlo do numero de entradas na legenda
        # Descubro quantas entradas vai ter a legenda
        number_of_labels = len(graph_area.legend().get_texts())
        # Inicialmente há uma coluna, mas vou fazer contas para ter 10 itens por coluna no máximo
        legend_columns = 1
        labels_per_columns = number_of_labels / legend_columns  # Numero de entradas por coluna
        while labels_per_columns > 10:  # Se a priori for menos de 10 entradas por coluna, não acontece nada
            legend_columns += 1  # Se houver mais que 10 entradas por coluna, meto mais uma coluna
            # Recalculo o numero de entradas por coluna
            labels_per_columns = number_of_labels / legend_columns
        # Defino o numero de colunas na legenda = numero de colunas necessárias para não ter mais de 10 entradas por coluna
        graph_area.legend(ncol=legend_columns)
    # --------------------------------------------------------------------------------------------------------------------------------------
    elif spectype == 'M_Simulation':
        # Variável para contar as transições erradas
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
                # Leitura dos valores das transições selecionadas
                # Contrariamente ao spectype == 'Stick' onde os plots são feitos quando se trata de cada risca, aqui,
                # o  que se faz é obter os valores necessários para os plots. Não se faz nenhum plot em si dentro deste ciclo.
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
                # Verificar se se selecionaram transições indísponíveis
                # Neste caso bad_lines é um dicionario que cada entrada corresponde às linhas de um charge state
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
                # Verificar se se selecionaram transições indí­sponí­veis
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
        # Obtenção do valor de xfinal a usar nos cáclulos dos yy
        # Caso não seja selecionado um espectro experimental, porque se fo xfinal é mudado
        # Calcular a dispersão em energia das varias riscas para criar o array de valores de x a plotar
        # em funcao desta dispersão e da resolução experimental
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
        # Load e plot do espectro experimental
        exp_x = []
        exp_y = []
        exp_sigma = []
        min_exp_lim = 0
        max_exp_lim = 0
        if load != 'No':  # procedimento para fazer o plot experimental
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
        # Leitura dos valores da eficácia do detector:
        efficiency_values = []
        energy_values = []
        if effic_file_name != "No":
            try:
                efficiency = list(csv.reader(open(effic_file_name, 'r')))
                for pair in efficiency:
                    energy_values.append(float(pair[0]))
                    efficiency_values.append(float(pair[1]))
            except FileNotFoundError:
                messagebox.showwarning("Error", "Efficiency File is not Avaliable")
        
        # ---------------------------------------------------------------------------------------------------------------
        # Calculate the final y values
        generalVars.ytot, generalVars.yfinal, generalVars.yfinals = y_calculator(sim, sat, peak, xfinal, x, y, w, xs, ys, ws, res, energy_values, efficiency_values, enoffset)

        # ---------------------------------------------------------------------------------------------------------------
        # Cálculo da variável de normalização
        if load != 'No':
            normalization_var = normalizer(y0, max(exp_y), max(generalVars.ytot))
        else:
            if guiVars.normalizevar.get() == 'ExpMax':  # Se tentarem normalizar ao maximo experimental sem terem carregado espectro
                messagebox.showwarning("No experimental spectrum is loaded", "Choose different normalization option")  # Apresenta aviso
                # Define a variavel global de normalização para não normalizar
                guiVars.normalizevar.set('No')
            normalization_var = normalizer(y0, 1, max(generalVars.ytot))
        
        # ---------------------------------------------------------------------------------------------------------------
        # Autofit:
        if autofit == 'Yes':
            # Fazemos fit apenas se houver um gráfico experimental carregado
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
                
                if messagebox.askyesno("Fit Saving", "Do you want to save this fit?"):
                    with open(file_namer("Fit", time_of_click, ".txt"), 'w') as file:
                        file.write(fit_report(result))
                    print(fit_report(result))
                
            else:
                messagebox.showerror("Error", "Autofit is only avaliable if an experimental spectrum is loaded")
        
        # ------------------------------------------------------------------------------------------------------------------------
        # Plot das linhas
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
                            # Excluir as linhas que nao foram seleccionados nos botoes
                            if max(m) != 0:
                                # Plot the selected transition
                                graph_area.plot(xfinal + enoffset, (np.array(generalVars.yfinals[cs_index * len(the_dictionary) + index][l]) * normalization_var) + y0, label=key + ' - ' + labeldict[generalVars.label1[l]], color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                                graph_area.legend()
        elif sat == 'Diagram + Satellites':
            for cs_index, cs in enumerate(ploted_cs):
                for index, key in enumerate(the_dictionary):
                    if the_dictionary[key]["selected_state"]:
                        # Plot the selected transition
                        graph_area.plot(xfinal + enoffset, (np.array(generalVars.yfinal[cs_index * len(the_dictionary) + index]) * normalization_var) + y0, label=cs + ' ' + key, color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                        graph_area.legend()

                for index, key in enumerate(the_dictionary):
                    if the_dictionary[key]["selected_state"]:
                        for l, m in enumerate(generalVars.yfinals[cs_index * len(the_dictionary) + index]):
                            # Excluir as linhas que nao foram seleccionados nos botoes
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
        # Cálculo dos Residuos
        if load != 'No':
            # Criar lista vazia para o gráfico de resí­duos
            y_interp = [0 for i in range(len(exp_x))]
            # Interpolate the total plotted intensities
            f_interpolate = interp1d(xfinal + enoffset, (np.array(generalVars.ytot) * normalization_var) + y0, kind='cubic')
            
            # Vetor para guardar o y dos residuos (não precisamos de guardar o x porque é igual ao exp_x
            y_res = [0 for x in range(len(exp_x))]
            # Variável para a soma do chi quadrado
            chi_sum = 0
            # Percorremos todos os valores de x
            for g, h in enumerate(exp_x):
                # Obtemos o valor de y interpolado pela função definida a cima
                y_interp[g] = f_interpolate(h)
                # Cálculamos o y dos residuos subtraindo o interpolado ao experimental
                if normalize == 'ExpMax' or normalize == 'No':
                    y_res[g] = (exp_y[g] - y_interp[g])
                    chi_sum += (y_res[g] ** 2) / ((exp_sigma[g]**2))
                elif normalize == 'One':
                    y_res[g] = ((exp_y[g] / max(exp_y)) - y_interp[g])
                    chi_sum += (y_res[g] ** 2) / ((exp_sigma[g] / max(exp_y))**2)
            
            
            generalVars.chi_sqrd = chi_sum / (len(exp_x) - number_of_fit_variables)
            residues_graph.plot(exp_x, y_res)
            print("Valor Manual Chi", generalVars.chi_sqrd)
            residues_graph.legend(title="Red. \u03C7\u00B2 = " + "{:.5f}".format(generalVars.chi_sqrd))
        
        # ------------------------------------------------------------------------------------------------------------------------
        # Definição do label do eixo yy e, consoante haja ou não um gráfico de resí­duos, do eixo  xx
        graph_area.set_ylabel('Intensity (arb. units)')
        graph_area.legend(title=element_name, title_fontsize='large')
        if load == 'No':
            graph_area.set_xlabel('Energy (eV)')
        
        # ------------------------------------------------------------------------------------------------------------------------
        # Controlo do numero de entradas na legenda
        # Descubro quantas entradas vai ter a legenda
        number_of_labels = len(graph_area.legend().get_texts())
        # Inicialmente há uma coluna, mas vou fazer contas para ter 10 itens por coluna no máximo
        legend_columns = 1
        labels_per_columns = number_of_labels / legend_columns  # Numero de entradas por coluna
        while labels_per_columns > 10:  # Se a priori for menos de 10 entradas por coluna, não acontece nada
            legend_columns += 1  # Se houver mais que 10 entradas por coluna, meto mais uma coluna
            # Recalculo o numero de entradas por coluna
            labels_per_columns = number_of_labels / legend_columns
        # Defino o numero de colunas na legenda = numero de colunas necessárias para não ter mais de 10 entradas por coluna
        graph_area.legend(ncol=legend_columns)

    f.canvas.draw()
