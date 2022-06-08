import numpy as np
from scipy.interpolate import interp1d
from tkinter import messagebox

from lmfit import Minimizer, Parameters, report_fit, fit_report

from datetime import datetime

from data.variables import labeldict, the_dictionary, the_aug_dictionary
import data.variables as generalVars

from utils.fileIO import file_namer

import utils.interface as guiVars


element_name = None

# ---------------------------------------------------------------------------------------------------------------
# Funções que fazem o cálculo das riscas a ser plotadas FALTA: Mal explicado e sem comentários nas funções em si
def G(T, energy, intens, res, width):
    """ Return Gaussian line shape at x with HWHM alpha """
    y = [0 for j in range(
        len(T))]  # Criar um vector com o tamanho de T cheio de zeros
    for i, l in enumerate(T):
        y[i] = intens * np.sqrt(np.log(2) / np.pi) / (res + width) * np.exp(-((T[i] - energy) / (res + width)) ** 2 * np.log(2))
    return (y)


def L(T, energy, intens, res, width):
    """ Return Lorentzian line shape at x with HWHM gamma """
    y = [0 for j in range(
        len(T))]  # Criar um vector com o tamanho de T cheio de zeros
    for i, l in enumerate(T):
        y[i] = intens * (0.5 * (width + res) / np.pi) / ((T[i] - energy) ** 2 + (0.5 * (width + res)) ** 2)
        # y[i]=(intens*2*(width+res)) / (np.pi*(4*(T[i]-energy)**2 + (width+res)**2))
    return (y)


def V(T, energy, intens, res, width):
    """ Return the Voigt line shape at x with Lorentzian component HWHM gamma and Gaussian component HWHM alpha."""
    y = [0 for j in range(
        len(T))]  # Criar um vector com o tamanho de T cheio de zeros
    for i, l in enumerate(T):
        sigma = res / np.sqrt(2 * np.log(2))
        y[i] = np.real(intens * wofz(complex(T[i] - energy, width/2) / sigma / np.sqrt(2))) / sigma / np.sqrt(2 * np.pi)
    return (y)


def detector_efficiency(energy_values, efficiency_values, xfinal, enoffset):
        interpolated_effic = [0 for i in range(len(xfinal))]
        effic_interpolation = interp1d(energy_values, np.array(efficiency_values)/100)
        for i, energy in enumerate(xfinal+enoffset):
            interpolated_effic[i] = effic_interpolation(energy)
            print(interpolated_effic[i], energy)
        return interpolated_effic

def normalizer(y0, expy_max, ytot_max):
    normalize = guiVars.normalizevar.get()
    try:
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




def updateRadTransitionVals(transition, num):
    num_of_transitions = num + 1
    # Estas variáveis servem só para não ter de escrever o acesso ao valor do dicionário todas as vezes
    low_level = the_dictionary[transition]["low_level"]
    high_level = the_dictionary[transition]["high_level"]
    
    diag_stick_val = [line for line in generalVars.lineradrates if line[1] in low_level and line[5] == high_level and float(line[8]) != 0]  # Cada vez que o for corre, lê o ficheiro de uma transição
    sat_stick_val = [line for line in generalVars.linesatellites if low_level in line[1] and high_level in line[5] and float(line[8]) != 0]
    
    return num_of_transitions, low_level, high_level, diag_stick_val, sat_stick_val
    

def updateSatTransitionVals(low_level, high_level, key, sat_stick_val):
    sat_stick_val_ind1 = [line for line in sat_stick_val if low_level + key in line[1] and key + high_level in line[5]]
    sat_stick_val_ind2 = [line for line in sat_stick_val if low_level + key in line[1] and high_level + key in line[5] and key != high_level]
    sat_stick_val_ind3 = [line for line in sat_stick_val if key + low_level in line[1] and key + high_level in line[5]]
    sat_stick_val_ind4 = [line for line in sat_stick_val if key + low_level in line[1] and high_level + key in line[5] and key != high_level]
    sat_stick_val_ind = sat_stick_val_ind1 + sat_stick_val_ind2 + sat_stick_val_ind3 + sat_stick_val_ind4
    
    return sat_stick_val


def updateRadCSTrantitionsVals(transition, num, ncs, cs):
    num_of_transitions = num + 1
    # Estas variáveis servem só para não ter de escrever o acesso ao valor do dicionário todas as vezes
    low_level = the_dictionary[transition]["low_level"]
    high_level = the_dictionary[transition]["high_level"]

    if not ncs:
        diag_stick_val = [line + [generalVars.PCS_radMixValues[i].get()] for i, linerad in enumerate(generalVars.lineradrates_PCS) for line in linerad if line[1] in low_level and line[5] == high_level and float(line[8]) != 0 and generalVars.rad_PCS[i] == cs]  # Cada vez que o for corre, lê o ficheiro de uma transição
    else:
        diag_stick_val = [line + [generalVars.NCS_radMixValues[i].get()] for i, linerad in enumerate(generalVars.lineradrates_NCS) for line in linerad if line[1] in low_level and line[5] == high_level and float(line[8]) != 0 and generalVars.rad_NCS[i] == cs]

    if not ncs:
        sat_stick_val = [line + [generalVars.PCS_radMixValues[i].get()] for i, linesat in enumerate(generalVars.linesatellites_PCS) for line in linesat if low_level in line[1] and high_level in line[5] and float(line[8]) != 0 and generalVars.sat_PCS[i] == cs]
    else:
        sat_stick_val = [line + [generalVars.NCS_radMixValues[i].get()] for i, linesat in enumerate(generalVars.linesatellites_NCS) for line in linesat if low_level in line[1] and high_level in line[5] and float(line[8]) != 0 and generalVars.sat_NCS[i] == cs]
    
    return num_of_transitions, low_level, high_level, diag_stick_val, sat_stick_val


def updateAugCSTransitionsVals(transition, num, ncs, cs):
    num_of_transitions = num + 1
    low_level = the_aug_dictionary[transition]["low_level"]
    high_level = the_aug_dictionary[transition]["high_level"]
    auger_level = the_aug_dictionary[transition]["auger_level"]

    if not ncs:
        aug_stick_val = [line + [generalVars.PCS_augMixValues[i].get()] for i, lineaug in enumerate(generalVars.lineaugrates_PCS) for line in lineaug if low_level in line[1] and high_level in line[5][:2] and auger_level in line[5][2:4] and float(line[8]) != 0 and generalVars.aug_PCS[i] == cs]
    else:
        aug_stick_val = [line + [generalVars.NCS_augMixValues[i].get()] for i, lineaug in enumerate(generalVars.lineaugrates_NCS) for line in lineaug if low_level in line[1] and high_level in line[5][:2] and auger_level in line[5][2:4] and float(line[8]) != 0 and generalVars.aug_PCS[i] == cs]
    
    return num_of_transitions, aug_stick_val


def updateAugTransitionVals(transition, num):
    num_of_transitions = num + 1
    low_level = the_aug_dictionary[transition]["low_level"]
    high_level = the_aug_dictionary[transition]["high_level"]
    auger_level = the_aug_dictionary[transition]["auger_level"]

    aug_stick_val = [line for line in generalVars.lineauger if low_level in line[1] and high_level in line[5][:2] and auger_level in line[5][2:4] and float(line[8]) != 0]
    
    return num_of_transitions, aug_stick_val


def getBounds(x, w):
    deltaE = []
    # Percorremos as listas guardadas em x. k é a lista e i o indice onde ela está guardada em x.
    for j, k in enumerate(x):
        if k != []:  # Se a lista não estiver vazia, guardamos em deltaE a diferença entre o seu valor máximo e mí­nimo
            deltaE.append(max(x[j]) - min(x[j]))

    max_value = max([max(x[i]) for i in range(len(x)) if x[i] != []]) + 4 * max([max(w[i]) for i in range(len(w)) if w[i] != []])
    min_value = min([min(x[i]) for i in range(len(x)) if x[i] != []]) - 4 * max([max(w[i]) for i in range(len(w)) if w[i] != []])
    
    return deltaE, max_value, min_value


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


def updateMaxMinVals(x_mx, x_mn, deltaE, max_value, min_value, res, enoffset):
    # Definimos o x Mí­nimo que queremos plotar. Pode ser definido automáticamente ou pelo valor x_mn
    if x_mn == 'Auto':  # x_mn é inicializado a Auto, da primeira vez que o programa corre isto é verdade
        if res <= 0.2 * (min(deltaE)):
            array_input_min = min_value - 2 * min(deltaE)
        else:
            array_input_min = min_value - 2 * res * min(deltaE)
    else:
        array_input_min = float(x_mn) - enoffset
    # Definimos o x Máximo que queremos plotar. Pode ser definido automáticamente ou pelo valor x_mx
    if x_mx == 'Auto':  # x_mx é inicializado a Auto, da primeira vez que o programa corre isto é verdade
        if res <= 0.2 * (min(deltaE)):
            array_input_max = max_value + 2 * min(deltaE)
        else:
            array_input_max = max_value + 2 * res * (min(deltaE))
    else:
        array_input_max = float(x_mx) - enoffset
    
    return array_input_max, array_input_min
    

def extractExpVals(exp_spectrum):
    for i, it in enumerate(exp_spectrum):
        # Transformar os valores do espectro experimental para float
        for j, itm in enumerate(exp_spectrum[i]):
            if exp_spectrum[i][j] != '':
                exp_spectrum[i][j] = float(itm)
    xe = np.array([float(row[0]) for row in exp_spectrum])
    ye = np.array([float(row[1]) for row in exp_spectrum])
    # Se o espectro experimental tiver 3 colunas a terceira sera a incerteza
    if len(exp_spectrum[0]) >= 3:
        sigma_exp = np.array([float(row[2]) for row in exp_spectrum])
    else:  # Caso contrario utiliza-se raiz do numero de contagens como a incerteza de cada ponto
        sigma_exp = np.sqrt(ye)
    
    return xe, ye, sigma_exp


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

    for i in range(len(xe)):
        if min_exp_lim <= xe[i] <= max_exp_lim:
            exp_x.append(xe[i])
            exp_y.append(ye[i])
            exp_sigma.append(sigma_exp[i])
    
    return exp_x, exp_y, exp_sigma


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

def func2min(params, sim, exp_x, exp_y, num_of_points, sat, peak, x, y, w, xs, ys, ws, energy_values, efficiency_values, enoffset):
    global xfinal
    
    normalize = guiVars.normalizevar.get()
    y_interp = [0 for i in range(len(exp_x))]
    xoff = params['xoff']
    y0 = params['yoff']
    res = params['res']
    ytot_max = params['ytot_max']
    xfinal = np.array(np.linspace(min(exp_x) - xoff, max(exp_x) - xoff, num=num_of_points))
    generalVars.ytot, generalVars.yfinal, generalVars.yfinals = y_calculator(sim, sat, peak, xfinal, x, y, w, xs, ys, ws, res, energy_values, efficiency_values, enoffset)
    normalization_var = normalizer(y0, max(exp_y), ytot_max)
    # print(xoff, res, y0, normalization_var)
    # print(xoff, res, y0, ytot_max)
    f_interpolate = interp1d(xfinal + xoff, np.array(generalVars.ytot * normalization_var) + y0, kind='cubic')  # Falta adicionar o y0
    for g, h in enumerate(exp_x):
        # Obtemos o valor de y interpolado pela função definida a cima
        y_interp[g] = f_interpolate(h)
    # graph_a.plot(exp_x, y_interp, 'y', marker = ',')
    if normalize == 'One':
        return np.array(y_interp) - np.array(exp_y) / max(exp_y)
    else:
        return np.array(y_interp) - np.array(exp_y)

def stem_ploter(transition_values, transition, spec_type, ind, key):
    col2 = [['b'], ['g'], ['r'], ['c'], ['m'], ['y'], ['k']]
    x = [float(row[8]) for row in transition_values]
    max_value = max(x)
    min_value = min(x)
    x.insert(0, 2 * min_value - max_value)
    x.append(2 * max_value - min_value)
    if spec_type == 'Diagram':
        y = [float(row[11]) * (1 - 0.01 * sum(generalVars.shakeweights)) for row in transition_values]  # *float(row[11])*float(row[9])
        y.insert(0, 0)
        y.append(0)
        a.stem(x, y, markerfmt=' ', linefmt=str(col2[np.random.randint(0, 7)][0]), label=str(transition), use_line_collection=True)
        a.legend(loc='best', numpoints=1)
    elif spec_type == 'Satellites':
        sy_points = [float(float(row[11]) * 0.01 * generalVars.shakeweights[ind]) for row in transition_values]  # *float(row[11])*float(row[9])
        sy_points.insert(0, 0)
        sy_points.append(0)
        a.stem(x, sy_points, markerfmt=' ', linefmt=str(col2[np.random.randint(0, 7)][0]), label=transition + ' - ' + labeldict[key], use_line_collection=True)  # Plot a stemplot
        a.legend(loc='best', numpoints=1)
    elif spec_type == 'Auger':
        y = [float(row[11]) * (1 - 0.01 * sum(generalVars.shakeweights)) for row in transition_values]  # *float(row[11])*float(row[9])
        y.insert(0, 0)
        y.append(0)
        a.stem(x, y, markerfmt=' ', linefmt=str(col2[np.random.randint(0, 7)][0]), label=str(transition), use_line_collection=True)
        a.legend(loc='best', numpoints=1)
    elif spec_type == 'Diagram_CS':
        y = [float(row[11]) * (1 - 0.01 * sum(generalVars.shakeweights)) * float(row[-1]) for row in transition_values]  # *float(row[11])*float(row[9])
        y.insert(0, 0)
        y.append(0)
        a.stem(x, y, markerfmt=' ', linefmt=str(col2[np.random.randint(0, 7)][0]), label=str(transition), use_line_collection=True)
        a.legend(loc='best', numpoints=1)
    elif spec_type == 'Satellites_CS':
        sy_points = [float(float(row[11]) * 0.01 * generalVars.shakeweights[ind] * float(row[-1])) for row in transition_values]  # *float(row[11])*float(row[9])
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
    a.legend(title=element_name, title_fontsize='large')
    # --------------------------------------------------------------------------------------------------------------------------
    # Tratamento da Legenda
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

def plot_stick(sim, f, graph_area):
    # Obtenho o a data e hora exacta para dar nome aos ficheiros a gravar
    time_of_click = datetime.now()
    
    
    global xfinal, exp_x, exp_y, residues_graph
    residues_graph = None
    exp_x = None
    exp_y = None
    graph_area.clear()
    if guiVars.yscale_log.get() == 'Ylog':
        graph_area.set_yscale('log')
    if guiVars.xscale_log.get() == 'Xlog':
        graph_area.set_xscale('log')
    graph_area.legend(title=element_name)
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
    col2 = [['b'], ['g'], ['r'], ['c'], ['m'], ['y'], ['k']]
    x = [[] for i in range(len(the_dictionary))]
    y = [[] for i in range(len(the_dictionary))]
    w = [[] for i in range(len(the_dictionary))]
    xs = [[[] for i in generalVars.label1] for j in x]
    ys = [[[] for i in generalVars.label1] for j in y]
    ws = [[[] for i in generalVars.label1] for j in w]
    normalization_var = 1
    # --------------------------------------------------------------------------------------------------------------------------
    if spectype == 'Stick':
        # Duas variáveis que servem para ver se há alguma transição mal escolhida. A primeira serve para saber o numero total de transiões escolhidas e a segunda para anotar quantas tranisções erradas se escolheram
        num_of_transitions = 0
        bad_selection = 0
        if sat != 'Auger':
            for transition in the_dictionary:
                # Se a transição estiver selecionada:
                if the_dictionary[transition]["selected_state"]:
                    num_of_transitions, low_level, high_level, diag_stick_val, sat_stick_val = updateRadStickTransitionVals(transition, num_of_transitions)
                    
                    # -------------------------------------------------------------------------------------------
                    if sat == 'Diagram':
                        if not diag_stick_val:  # Se não ouver dados no vetor da diagrama
                            # Crio um vector de zeros para o programa continuar a correr (Em string porque estava a dar um erro qq quando punha em int)(range 16 porque é o tamanho da
                            diag_stick_val = [['0' for i in range(16)]]
                            # linha do ficheiro que supostamente preencheria este vertor)
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
                        b1 = 0
                        for ind, key in enumerate(generalVars.label1):
                            sat_stick_val_ind = updateSatStickTransitionVals(low_level, high_level, key, sat_stick_val)
                            
                            if len(sat_stick_val_ind) > 1:
                                stem_ploter(sat_stick_val_ind, transition, 'Satellites', ind, key)
                            b1 += 100 / len(generalVars.label1)
                            guiVars.progress_var.set(b1)
                            sim.update_idletasks()
                    elif sat == 'Diagram + Satellites':
                        if not diag_stick_val:  # Se não ouver dados no vetor da diagrama
                            # Crio um vector de zeros para o programa continuar a correr (Em string porque estava a dar um erro qq quando punha em int)(range 16 porque é o tamanho da
                            diag_stick_val = [['0' for i in range(16)]]
                            # linha do ficheiro que supostamente preencheria este vertor)
                            # Mostro no ecrã a transição errada que escolheram
                            messagebox.showwarning("Wrong Transition", "Diagram info. for " + transition + " is not Available")
                            bad_selection += 1  # incremento o numero de transições "mal" escolhidas
                        stem_ploter(diag_stick_val, transition, 'Diagram', 0, 0)
                        if not sat_stick_val:  # Se não ouver nada no vetor das satelites
                            sat_stick_val = [['0' for i in range(16)]]
                            # Mostro no ecrã a transição errada que escolheram
                            messagebox.showwarning("Wrong Transition", "Satellites info.  for " + transition + " is not Available")
                            bad_selection += 1  # incremento o numero de transições "mal" escolhidas
                        b1 = 0
                        for ind, key in enumerate(generalVars.label1):
                            sat_stick_val_ind = updateSatStickTransitionVals(low_level, high_level, key, sat_stick_val)
                            
                            if len(sat_stick_val_ind) > 1:
                                stem_ploter(sat_stick_val_ind, transition, 'Satellites', ind, key)
                            b1 += 100 / len(generalVars.label1)
                            guiVars.progress_var.set(b1)
                            sim.update_idletasks()

                graph_area.set_xlabel('Energy (eV)')
                graph_area.set_ylabel('Intensity (arb. units)')
        else:
            for transition in the_aug_dictionary:
                # Se a transição estiver selecionada:
                if the_aug_dictionary[transition]["selected_state"]:
                    num_of_transitions, aug_stick_val = updateAugTransitionVals(transition, num_of_transitions)
                    
                    if not aug_stick_val:  # Se não ouver dados no vetor da diagrama
                        # Crio um vector de zeros para o programa continuar a correr (Em string porque estava a dar um erro qq quando punha em int)(range 16 porque é o tamanho da
                        aug_stick_val = [['0' for i in range(16)]]
                        # linha do ficheiro que supostamente preencheria este vertor)
                        # Mostro no ecrã a transição errada que escolheram
                        messagebox.showwarning("Wrong Transition", "Auger info. for " + transition + " is not Available")
                        bad_selection += 1  # incremento o numero de transições "mal" escolhidas
                    stem_ploter(aug_stick_val, transition, 'Auger', 0, 0)

                graph_area.set_xlabel('Energy (eV)')
                graph_area.set_ylabel('Intensity (arb. units)')

        if num_of_transitions == 0:
            messagebox.showerror("No Transition", "No transition was chosen")
        elif bad_selection != 0:
            messagebox.showerror("Wrong Transition", "You chose " + str(bad_selection) + " invalid transition(s)")
    # --------------------------------------------------------------------------------------------------------------------------
    elif spectype == 'M_Stick':
        # Duas variáveis que servem para ver se há alguma transição mal escolhida. A primeira serve para saber o numero total de transiões escolhidas e a segunda para anotar quantas tranisções erradas se escolheram
        num_of_transitions = 0
        bad_selection = 0
        if sat != 'Auger':
            charge_states = generalVars.rad_PCS + generalVars.rad_NCS

            for cs_index, cs in enumerate(charge_states):
                mix_val = '0.0'
                ncs = False

                if cs_index < len(generalVars.rad_PCS):
                    mix_val = generalVars.PCS_radMixValues[cs_index].get()
                else:
                    mix_val = generalVars.NCS_radMixValues[cs_index - len(generalVars.rad_PCS)].get()
                    ncs = True
                if mix_val != '0.0':
                    for transition in the_dictionary:
                        # Se a transição estiver selecionada:
                        if the_dictionary[transition]["selected_state"]:
                            num_of_transitions, low_level, high_level, diag_stick_val, sat_stick_val = updateRadCSTrantitionsVals(transition, num_of_transitions, ncs, cs)
                            
                            if sat == 'Diagram':
                                if not diag_stick_val:  # Se não ouver dados no vetor da diagrama
                                    # Crio um vector de zeros para o programa continuar a correr (Em string porque estava a dar um erro qq quando punha em int)(range 16 porque é o tamanho da
                                    diag_stick_val = [['0' for i in range(16)]]
                                    # linha do ficheiro que supostamente preencheria este vertor)
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
                                b1 = 0
                                for ind, key in enumerate(generalVars.label1):
                                    sat_stick_val_ind = updateSatStickTransitionVals(low_level, high_level, key, sat_stick_val)
                                    
                                    if len(sat_stick_val_ind) > 1:
                                        stem_ploter(sat_stick_val_ind, cs + ' ' + transition, 'Satellites_CS', ind, key)
                                    b1 += 100 / len(generalVars.label1)
                                    guiVars.progress_var.set(b1)
                                    sim.update_idletasks()
                            elif sat == 'Diagram + Satellites':
                                if not diag_stick_val:  # Se não ouver dados no vetor da diagrama
                                    # Crio um vector de zeros para o programa continuar a correr (Em string porque estava a dar um erro qq quando punha em int)(range 16 porque é o tamanho da
                                    diag_stick_val = [['0' for i in range(16)]]
                                    # linha do ficheiro que supostamente preencheria este vertor)
                                    # Mostro no ecrã a transição errada que escolheram
                                    messagebox.showwarning("Wrong Transition", "Diagram info. for " + transition + " is not Available")
                                    bad_selection += 1  # incremento o numero de transições "mal" escolhidas
                                stem_ploter(diag_stick_val, cs + ' ' + transition, 'Diagram_CS', 0, 0)
                                if not sat_stick_val:  # Se não ouver nada no vetor das satelites
                                    sat_stick_val = [['0' for i in range(16)]]
                                    # Mostro no ecrã a transição errada que escolheram
                                    messagebox.showwarning("Wrong Transition", "Satellites info.  for " + transition + " is not Available")
                                    bad_selection += 1  # incremento o numero de transições "mal" escolhidas
                                b1 = 0
                                for ind, key in enumerate(generalVars.label1):
                                    sat_stick_val_ind = updateSatStickTransitionVals(low_level, high_level, key, sat_stick_val)
                                    
                                    if len(sat_stick_val_ind) > 1:
                                        stem_ploter(sat_stick_val_ind, cs + ' ' + transition, 'Satellites_CS', ind, key)
                                    b1 += 100 / len(generalVars.label1)
                                    guiVars.progress_var.set(b1)
                                    sim.update_idletasks()

                        graph_area.set_xlabel('Energy (eV)')
                        graph_area.set_ylabel('Intensity (arb. units)')
        else:
            charge_states = generalVars.aug_PCS + generalVars.aug_NCS

            for cs_index, cs in enumerate(charge_states):
                mix_val = '0.0'
                ncs = False

                if cs_index < len(generalVars.aug_PCS):
                    mix_val = generalVars.PCS_augMixValues[cs_index].get()
                else:
                    mix_val = generalVars.NCS_augMixValues[cs_index - len(generalVars.aug_PCS)].get()
                    ncs = True
                if mix_val != '0.0':
                    for transition in the_aug_dictionary:
                        # Se a transição estiver selecionada:
                        if the_aug_dictionary[transition]["selected_state"]:
                            num_of_transitions, aug_stick_val = updateAugCSTransitionsVals(transition, num_of_transitions, ncs, cs)
                            
                            if not aug_stick_val:  # Se não ouver dados no vetor da diagrama
                                # Crio um vector de zeros para o programa continuar a correr (Em string porque estava a dar um erro qq quando punha em int)(range 16 porque é o tamanho da
                                aug_stick_val = [['0' for i in range(16)]]
                                # linha do ficheiro que supostamente preencheria este vertor)
                                # Mostro no ecrã a transição errada que escolheram
                                messagebox.showwarning("Wrong Transition", "Auger info. for " + transition + " is not Available for charge state: " + cs)
                                bad_selection += 1  # incremento o numero de transições "mal" escolhidas
                            stem_ploter(aug_stick_val, cs + ' ' + transition, 'Auger_CS', 0, 0)

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
                    _, low_level, high_level, diag_sim_val, sat_sim_val = updateRadTransitionVals(transition, 0)
                    
                    if sat == 'Diagram':
                        x1 = [float(row[8]) for row in diag_sim_val]
                        y1 = [float(row[11]) * (1 - sum(generalVars.shakeweights)) for row in diag_sim_val]
                        w1 = [float(row[15]) for row in diag_sim_val]
                        x[index] = x1
                        y[index] = y1
                        w[index] = w1
                    elif sat == 'Satellites':
                        for ind, key in enumerate(generalVars.label1):
                            sat_sim_val_ind = updateSatStickTransitionVals(low_level, high_level, key, sat_sim_val)
                            
                            if len(sat_sim_val_ind) > 1:
                                x1s = [float(row[8]) for row in sat_sim_val_ind]
                                y1s = [float(float(row[11]) * generalVars.shakeweights[ind]) for row in sat_sim_val_ind]
                                w1s = [float(row[15]) for row in sat_sim_val_ind]
                                xs[index][ind] = x1s
                                ys[index][ind] = y1s
                                ws[index][ind] = w1s
                    elif sat == 'Diagram + Satellites':
                        x1 = [float(row[8]) for row in diag_sim_val]
                        y1 = [float(row[11]) * (1 - sum(generalVars.shakeweights)) for row in diag_sim_val]
                        w1 = [float(row[15]) for row in diag_sim_val]
                        x[index] = x1
                        y[index] = y1
                        w[index] = w1
                        # ---------------------------------------------------------------------------------------------------------------------
                        ka1s = [line for line in generalVars.linesatellites if 'K1' in line[1] and 'L3' in line[5] and float(line[8]) != 0]
                        for ind, key in enumerate(generalVars.label1):
                            sat_sim_val_ind = updateSatStickTransitionVals(low_level, high_level, key, sat_sim_val)
                            
                            if len(sat_sim_val_ind) > 1:
                                x1s = [float(row[8]) for row in sat_sim_val_ind]
                                y1s = [float(float(row[11]) * generalVars.shakeweights[ind]) for row in sat_sim_val_ind]
                                w1s = [float(row[15]) for row in sat_sim_val_ind]
                                xs[index][ind] = x1s
                                ys[index][ind] = y1s
                                ws[index][ind] = w1s
            # -------------------------------------------------------------------------------------------
            # Verificar se se selecionaram transições indí­sponí­veis
            for index, transition in enumerate(the_dictionary):
                if the_dictionary[transition]["selected_state"]:
                    if not x[index] and not any(xs[index]):
                        messagebox.showwarning("Wrong Transition", transition + " is not Available")
                        x[index] = []
                        bad_selection += 1
        else:
            x = [[] for i in range(len(the_aug_dictionary))]
            y = [[] for i in range(len(the_aug_dictionary))]
            w = [[] for i in range(len(the_aug_dictionary))]
            xs = [[[] for i in generalVars.label1] for j in x]
            ys = [[[] for i in generalVars.label1] for j in y]
            ws = [[[] for i in generalVars.label1] for j in w]

            for index, transition in enumerate(the_aug_dictionary):
                if the_aug_dictionary[transition]["selected_state"]:
                    _, aug_stick_val = updateAugTransitionVals(transition, 0)
                    
                    x1 = [float(row[8]) for row in aug_sim_val]
                    y1 = [float(row[9]) * (1 - sum(generalVars.shakeweights)) for row in aug_sim_val]
                    w1 = [float(row[10]) for row in aug_sim_val]
                    x[index] = x1
                    y[index] = y1
                    w[index] = w1

            # -------------------------------------------------------------------------------------------
            # Verificar se se selecionaram transições indí­sponí­veis
            for index, transition in enumerate(the_aug_dictionary):
                if the_aug_dictionary[transition]["selected_state"]:
                    if not x[index]:
                        messagebox.showwarning("Wrong Auger Transition", transition + " is not Available")
                        x[index] = []
                        bad_selection += 1

        # -------------------------------------------------------------------------------------------
        # Obtenção do valor de xfinal a usar nos cáclulos dos yy (caso não seja selecionado um espectro experimental, porque se fo xfinal é mudado)
        # (Calcular a dispersão em energia das varias riscas para criar o array de valores de x a plotar em funcao desta dispersão e da resolução experimental)
        try:
            if sat == 'Diagram':
                deltaE, max_value, min_value = getBounds(x, w)

            elif sat == 'Satellites' or sat == 'Diagram + Satellites':
                deltaE, max_value, min_value = getSatBounds(xs, ws)
            
            elif sat == 'Auger':
                deltaE, max_value, min_value = getBounds(x, w)
            
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
            graph_area, residues_graph, exp_spectrum = guiVars.setupExpPlot(f, load, element_name)
            
            xe, ye, sigma_exp = extractExpVals(exp_spectrum)
            
            exp_x, exp_y, exp_sigma = getBoundedExp(xe, ye, sigma_exp, enoffset, num_of_points, x_mx, x_mn)

            xfinal = np.array(np.linspace(min(exp_x) - enoffset, max(exp_x) - enoffset, num=num_of_points))

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
        # Variáveis necessárias para os cálcuos dos y e para os plots:
        generalVars.ytot, generalVars.yfinal, generalVars.yfinals = y_calculator(sim, sat, peak, xfinal, x, y, w, xs, ys, ws, res, energy_values, efficiency_values, enoffset)

        # ---------------------------------------------------------------------------------------------------------------
        # Cálculo da variável de notificação:
        # O cálculo é feito na função normalizer, e é lá que é lida a escolha de normalização do utilizador. Aqui só passamos dados para a funçao
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
        # start_time = time.time()
        if autofit == 'Yes':
            # Fazemos fit apenas se houver um gráfico experimental carregado
            if load != 'No':
                params = initializeFitParameters(exp_x, exp_y, enoffset, y0, res)
                
                number_of_fit_variables = len(params.valuesdict())
                minner = Minimizer(func2min, params, fcn_args=(sim, exp_x, exp_y, num_of_points, sat, peak, x, y, w, xs, ys, ws, energy_values, efficiency_values, enoffset))
                result = minner.minimize()
                
                enoffset, y0, res, ytot_max = fetchFittedParams(result)

                xfinal = np.array(np.linspace(min(exp_x) - enoffset, max(exp_x) - enoffset, num=num_of_points))
                normalization_var = normalizer(y0, max(exp_y), ytot_max)
                
                generalVars.ytot, generalVars.yfinal, generalVars.yfinals = y_calculator(sim, sat, peak, xfinal, x, y, w, xs, ys, ws, res, energy_values, efficiency_values, enoffset)
                
                if messagebox.askyesno("Fit Saving", "Do you want to save this fit?"):
                    with open(file_namer("Fit", time_of_click, ".txt"), 'w') as file:
                        file.write(fit_report(result))
                    print(fit_report(result))
                
            else:
                messagebox.showerror("Error", "Autofit is only avaliable if an experimental spectrum is loaded")
        # ------------------------------------------------------------------------------------------------------------------------
        # Plot das linhas
        # print('Time of fit execution: --- %s seconds ---' % (time.time() - start_time))
        if sat == 'Diagram':
            for index, key in enumerate(the_dictionary):
                if the_dictionary[key]["selected_state"]:
                    graph_area.plot(xfinal + enoffset, (np.array(generalVars.yfinal[index]) * normalization_var) + y0, label=key, color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                    graph_area.legend()
        elif sat == 'Satellites':
            for index, key in enumerate(the_dictionary):
                if the_dictionary[key]["selected_state"]:
                    for l, m in enumerate(generalVars.yfinals[index]):
                        if max(m) != 0:  # Excluir as linhas que nao foram seleccionados nos botoes
                            graph_area.plot(xfinal + enoffset, (np.array(generalVars.yfinals[index][l]) * normalization_var) + y0, label=key + ' - ' + labeldict[generalVars.label1[l]], color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                            graph_area.legend()
        elif sat == 'Diagram + Satellites':
            for index, key in enumerate(the_dictionary):
                if the_dictionary[key]["selected_state"]:
                    graph_area.plot(xfinal + enoffset, (np.array(generalVars.yfinal[index]) * normalization_var) + y0, label=key, color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                    graph_area.legend()

            for index, key in enumerate(the_dictionary):
                if the_dictionary[key]["selected_state"]:
                    for l, m in enumerate(generalVars.yfinals[index]):
                        if max(m) != 0:  # Excluir as linhas que nao foram seleccionados nos botoes
                            graph_area.plot(xfinal + enoffset, (np.array(generalVars.yfinals[index][l]) * normalization_var) + y0, label=key + ' - ' + labeldict[generalVars.label1[l]], color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                            graph_area.legend()
        elif sat == 'Auger':
            for index, key in enumerate(the_aug_dictionary):
                if the_aug_dictionary[key]["selected_state"]:
                    graph_area.plot(xfinal + enoffset, (np.array(generalVars.yfinal[index]) * normalization_var) + y0, label=key, color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                    graph_area.legend()
        if total == 'Total':
            graph_area.plot(xfinal + enoffset, (generalVars.ytot * normalization_var) + y0, label='Total', ls='--', lw=2, color='k')  # Plot the simulation of all lines
            graph_area.legend()
        # ------------------------------------------------------------------------------------------------------------------------
        # Cálculo dos Residuos
        if load != 'No':
            # if load != 'No':
            # Definimos uma função que recebe um numero, e tendo como dados o que passamos à interp1d faz a sua interpolação
            # print(*ytot, sep=',')
            # Criar lista vazia para o gráfico de resí­duos
            y_interp = [0 for i in range(len(exp_x))]
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
                    # y_res[g] = y_interp[g] - exp_y[g]                  ORIGINAL CODE
                    chi_sum += (y_res[g] ** 2) / ((exp_sigma[g]**2))
                elif normalize == 'One':
                    y_res[g] = ((exp_y[g] / max(exp_y)) - y_interp[g])
                    # y_res[g] = y_interp[g] - (exp_y[g] / max(exp_y))           ORGINAL CODE
                    chi_sum += (y_res[g] ** 2) / ((exp_sigma[g] / max(exp_y))**2)
                #     y_res[g] = (exp_y[g] / max(exp_y)) - y_interp[g]
                # Somatório para o cálculo de chi quad
            
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

        bad_lines = {}

        if sat != 'Auger':
            # -------------------------------------------------------------------------------------------
            # Leitura dos valores das transições selecionadas
            # Contrariamente ao spectype == 'Stick' onde os plots são feitos quando se trata de cada risca, aqui,
            # o  que se faz é obter os valores necessários para os plots. Não se faz nenhum plot em si dentro deste ciclo.
            charge_states = generalVars.rad_PCS + generalVars.rad_NCS

            ploted_cs = []

            for cs_index, cs in enumerate(charge_states):
                mix_val = '0.0'
                ncs = False

                if cs_index < len(generalVars.rad_PCS):
                    mix_val = generalVars.PCS_radMixValues[cs_index].get()
                else:
                    mix_val = generalVars.NCS_radMixValues[cs_index - len(generalVars.rad_PCS)].get()
                    ncs = True

                if mix_val != '0.0':
                    ploted_cs.append(cs)

            x = [[] for i in range(len(the_dictionary) * len(ploted_cs))]
            y = [[] for i in range(len(the_dictionary) * len(ploted_cs))]
            w = [[] for i in range(len(the_dictionary) * len(ploted_cs))]
            xs = [[[] for i in generalVars.label1] for j in x]
            ys = [[[] for i in generalVars.label1] for j in y]
            ws = [[[] for i in generalVars.label1] for j in w]

            for cs_index, cs in enumerate(ploted_cs):
                for index, transition in enumerate(the_dictionary):
                    if the_dictionary[transition]["selected_state"]:
                        _, low_level, high_level, diag_sim_val, sat_sim_val = updateRadCSTrantitionsVals(transition, 0, ncs, cs)
                        
                        if sat == 'Diagram':
                            x1 = [float(row[8]) for row in diag_sim_val]
                            y1 = [float(row[11]) * (1 - sum(generalVars.shakeweights)) * float(row[-1]) for row in diag_sim_val]
                            w1 = [float(row[15]) for row in diag_sim_val]
                            x[cs_index * len(the_dictionary) + index] = x1
                            y[cs_index * len(the_dictionary) + index] = y1
                            w[cs_index * len(the_dictionary) + index] = w1
                        elif sat == 'Satellites':
                            for ind, key in enumerate(generalVars.label1):
                                sat_sim_val_ind = updateSatStickTransitionVals(low_level, high_level, key, sat_stick_val)
                                
                                if len(sat_sim_val_ind) > 1:
                                    x1s = [float(row[8]) for row in sat_sim_val_ind]
                                    y1s = [float(float(row[11]) * generalVars.shakeweights[ind] * float(row[-1])) for row in sat_sim_val_ind]
                                    w1s = [float(row[15]) for row in sat_sim_val_ind]
                                    xs[cs_index * len(the_dictionary) + index][ind] = x1s
                                    ys[cs_index * len(the_dictionary) + index][ind] = y1s
                                    ws[cs_index * len(the_dictionary) + index][ind] = w1s
                        elif sat == 'Diagram + Satellites':
                            x1 = [float(row[8])for row in diag_sim_val]
                            y1 = [float(row[11]) * (1 - sum(generalVars.shakeweights)) * float(row[-1]) for row in diag_sim_val]
                            w1 = [float(row[15]) for row in diag_sim_val]
                            x[cs_index * len(the_dictionary) + index] = x1
                            y[cs_index * len(the_dictionary) + index] = y1
                            w[cs_index * len(the_dictionary) + index] = w1
                            # ---------------------------------------------------------------------------------------------------------------------
                            for ind, key in enumerate(generalVars.label1):
                                sat_sim_val_ind = updateSatStickTransitionVals(low_level, high_level, key, sat_stick_val)
                                
                                if len(sat_sim_val_ind) > 1:
                                    x1s = [float(row[8]) for row in sat_sim_val_ind]
                                    y1s = [float(float(row[11]) * generalVars.shakeweights[ind] * float(row[-1])) for row in sat_sim_val_ind]
                                    w1s = [float(row[15]) for row in sat_sim_val_ind]
                                    xs[cs_index * len(the_dictionary) + index][ind] = x1s
                                    ys[cs_index * len(the_dictionary) + index][ind] = y1s
                                    ws[cs_index * len(the_dictionary) + index][ind] = w1s
                # -------------------------------------------------------------------------------------------
                # Verificar se se selecionaram transições indí­sponí­veis
                for index, transition in enumerate(the_dictionary):
                    if the_dictionary[transition]["selected_state"]:
                        if not x[cs_index * len(the_dictionary) + index] and not any(xs[cs_index * len(the_dictionary) + index]):
                            if cs not in bad_lines:
                                bad_lines[cs] = [transition]
                            else:
                                bad_lines[cs].append(transition)

                            x[cs_index * len(the_dictionary) + index] = []
                            bad_selection += 1

            text = "Transitions not available for:\n"
            for cs in bad_lines:
                text += cs + ": " + str(bad_lines[cs]) + "\n"

            messagebox.showwarning("Wrong Transition", text)

            if len(bad_lines) == len(ploted_cs):
                intersection = list(bad_lines.values())[-1]
                for cs in bad_lines:
                    l1 = set(bad_lines[cs])
                    intersection = list(l1.intersection(intersection))

                messagebox.showwarning("Common Transitions", intersection)
            else:
                messagebox.showwarning("Common Transitions", "Every transition is plotted for at least 1 charge state.")
        else:
            charge_states = generalVars.aug_PCS + generalVars.aug_NCS

            ploted_cs = []

            for cs_index, cs in enumerate(charge_states):
                mix_val = '0.0'
                ncs = False

                if cs_index < len(generalVars.aug_PCS):
                    mix_val = generalVars.PCS_augMixValues[cs_index].get()
                else:
                    mix_val = generalVars.NCS_augMixValues[cs_index - len(generalVars.aug_PCS)].get()
                    ncs = True
                if mix_val != '0.0':
                    ploted_cs.append(cs)

            x = [[] for i in range(len(the_aug_dictionary) * len(ploted_cs))]
            y = [[] for i in range(len(the_aug_dictionary) * len(ploted_cs))]
            w = [[] for i in range(len(the_aug_dictionary) * len(ploted_cs))]
            xs = [[[] for i in generalVars.label1] for j in x]
            ys = [[[] for i in generalVars.label1] for j in y]
            ws = [[[] for i in generalVars.label1] for j in w]

            for cs_index, cs in enumerate(ploted_cs):
                for index, transition in enumerate(the_aug_dictionary):
                    if the_aug_dictionary[transition]["selected_state"]:
                        _, aug_stick_val = updateAugCSTransitionsVals(transition, 0, ncs, cs)
                        
                        x1 = [float(row[8]) for row in aug_sim_val]
                        y1 = [float(row[9]) * (1 - sum(generalVars.shakeweights)) * float(row[-1]) for row in aug_sim_val]
                        w1 = [float(row[10]) for row in aug_sim_val]
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
        # Obtenção do valor de xfinal a usar nos cáclulos dos yy (caso não seja selecionado um espectro experimental, porque se fo xfinal é mudado)
        # (Calcular a dispersão em energia das varias riscas para criar o array de valores de x a plotar em funcao desta dispersão e da resolução experimental)
        try:
            if sat == 'Diagram':
                deltaE, max_value, min_value = getBounds(x, w)

            elif sat == 'Satellites' or sat == 'Diagram + Satellites':
                deltaE, max_value, min_value = getSatBounds(xs, ws)
                
            elif sat == 'Auger':
                deltaE, max_value, min_value = getBounds(x, w)
            
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
            graph_area, residues_graph, exp_spectrum = guiVars.setupExpPlot(f, load, element_name)
            
            xe, ye, sigma_exp = extractExpVals(exp_spectrum)
            
            exp_x, exp_y, exp_sigma = getBoundedExp(xe, ye, sigma_exp, enoffset, num_of_points, x_mx, x_mn)

            xfinal = np.array(np.linspace(min(exp_x) - enoffset, max(exp_x) - enoffset, num=num_of_points))

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
        # Variáveis necessárias para os cálcuos dos y e para os plots:
        generalVars.ytot, generalVars.yfinal, generalVars.yfinals = y_calculator(sim, sat, peak, xfinal, x, y, w, xs, ys, ws, res, energy_values, efficiency_values, enoffset)

        # ---------------------------------------------------------------------------------------------------------------
        # Cálculo da variável de notificação:
        # O cálculo é feito na função normalizer, e é lá que é lida a escolha de normalização do utilizador. Aqui só passamos dados para a funçao
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
        # start_time = time.time()
        if autofit == 'Yes':
            # Fazemos fit apenas se houver um gráfico experimental carregado
            if load != 'No':

                params = initializeFitParameters(exp_x, exp_y, enoffset, y0, res)
                
                number_of_fit_variables = len(params.valuesdict())
                minner = Minimizer(func2min, params, fcn_args=(sim, exp_x, exp_y, num_of_points, sat, peak, x, y, w, xs, ys, ws, energy_values, efficiency_values, enoffset))
                result = minner.minimize()
                
                enoffset, y0, res, ytot_max = fetchFittedParams(result)

                xfinal = np.array(np.linspace(min(exp_x) - enoffset, max(exp_x) - enoffset, num=num_of_points))
                normalization_var = normalizer(y0, max(exp_y), ytot_max)
                
                generalVars.ytot, generalVars.yfinal, generalVars.yfinals = y_calculator(sim, sat, peak, xfinal, x, y, w, xs, ys, ws, res, energy_values, efficiency_values, enoffset)
                
                if messagebox.askyesno("Fit Saving", "Do you want to save this fit?"):
                    with open(file_namer("Fit", time_of_click, ".txt"), 'w') as file:
                        file.write(fit_report(result))
                    print(fit_report(result))
                
            else:
                messagebox.showerror("Error", "Autofit is only avaliable if an experimental spectrum is loaded")
        # ------------------------------------------------------------------------------------------------------------------------
        # Plot das linhas
        # print('Time of fit execution: --- %s seconds ---' % (time.time() - start_time))
        if sat == 'Diagram':
            for cs_index, cs in enumerate(ploted_cs):
                for index, key in enumerate(the_dictionary):
                    if the_dictionary[key]["selected_state"]:
                        graph_area.plot(xfinal + enoffset, (np.array(generalVars.yfinal[cs_index * len(the_dictionary) + index]) * normalization_var) + y0, label=cs + ' ' + key, color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                        graph_area.legend()
        elif sat == 'Satellites':
            for cs_index, cs in enumerate(ploted_cs):
                for index, key in enumerate(the_dictionary):
                    if the_dictionary[key]["selected_state"]:
                        for l, m in enumerate(generalVars.yfinals[cs_index * len(the_dictionary) + index]):
                            # Excluir as linhas que nao foram seleccionados nos botoes
                            if max(m) != 0:
                                graph_area.plot(xfinal + enoffset, (np.array(generalVars.yfinals[cs_index * len(the_dictionary) + index][l]) * normalization_var) + y0, label=key + ' - ' + labeldict[generalVars.label1[l]], color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                                graph_area.legend()
        elif sat == 'Diagram + Satellites':
            for cs_index, cs in enumerate(ploted_cs):
                for index, key in enumerate(the_dictionary):
                    if the_dictionary[key]["selected_state"]:
                        graph_area.plot(xfinal + enoffset, (np.array(generalVars.yfinal[cs_index * len(the_dictionary) + index]) * normalization_var) + y0, label=cs + ' ' + key, color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                        graph_area.legend()

                for index, key in enumerate(the_dictionary):
                    if the_dictionary[key]["selected_state"]:
                        for l, m in enumerate(generalVars.yfinals[cs_index * len(the_dictionary) + index]):
                            # Excluir as linhas que nao foram seleccionados nos botoes
                            if max(m) != 0:
                                graph_area.plot(xfinal + enoffset, (np.array(generalVars.yfinals[cs_index * len(the_dictionary) + index][l]) * normalization_var) + y0, label=cs + ' ' + key + ' - ' + labeldict[generalVars.label1[l]], color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                                graph_area.legend()
        elif sat == 'Auger':
            for cs_index, cs in enumerate(ploted_cs):
                for index, key in enumerate(the_aug_dictionary):
                    if the_aug_dictionary[key]["selected_state"]:
                        graph_area.plot(xfinal + enoffset, (np.array(generalVars.yfinal[cs_index * len(the_aug_dictionary) + index]) * normalization_var) + y0, label=cs + ' ' + key, color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                        graph_area.legend()
        if total == 'Total':
            graph_area.plot(xfinal + enoffset, (generalVars.ytot * normalization_var) + y0, label='Total', ls='--', lw=2, color='k')  # Plot the simulation of all lines
            graph_area.legend()
        # ------------------------------------------------------------------------------------------------------------------------
        # Cálculo dos Residuos
        if load != 'No':
            # if load != 'No':
            # Definimos uma função que recebe um numero, e tendo como dados o que passamos à interp1d faz a sua interpolação
            # print(*ytot, sep=',')
            # Criar lista vazia para o gráfico de resí­duos
            y_interp = [0 for i in range(len(exp_x))]
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
                    # y_res[g] = y_interp[g] - exp_y[g]                  ORIGINAL CODE
                    chi_sum += (y_res[g] ** 2) / ((exp_sigma[g]**2))
                elif normalize == 'One':
                    y_res[g] = ((exp_y[g] / max(exp_y)) - y_interp[g])
                    # y_res[g] = y_interp[g] - (exp_y[g] / max(exp_y))           ORGINAL CODE
                    chi_sum += (y_res[g] ** 2) / ((exp_sigma[g] / max(exp_y))**2)
                #     y_res[g] = (exp_y[g] / max(exp_y)) - y_interp[g]
                # Somatório para o cálculo de chi quad

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
