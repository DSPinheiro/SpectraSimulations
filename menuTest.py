'''
Created on 02/01/2017

@author: MGuerra
'''
from tkinter import *
import tkinter as tk
from tkinter import ttk
import sys, os
import csv
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from numpy import *
from pylab import *
import math
import heapq
from pathlib import Path

matplotlib.use('TkAgg')
from scipy.special import wofz
from scipy.interpolate import interp1d
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from matplotlib import gridspec

dir_path = Path(str(os.getcwd()) + '/')


def write_to_xls(ap, xfinal, yfinal, yfinals, xtot, ytot):  # Escrever para um ficheiro xls
    path = 'data.csv'  # Nome do ficheiro onde serao guardados os dados

    if ap == 1:
        print('yields')
        # print(T,CSBEB(B,U,N,T))
    #        dic[2]=CSBEB(B,U,N,T)
    #        dic2[2]='BEB'
    if ap == 2:
        print('level widths')
        # print(T,CSBEBav(B,U,N,T))
    #        dic[3]=CSBEBav(B,U,N,T)
    #        dic2[3]='BEBav'
    if ap == 3:
        print('Cross sections')
        # print(T,CSMBEB(B,U,N,T))
    #        dic[4]=CSMBEB(B,U,N,T)
    #        dic2[4]='MBEB'
    if ap == 4:
        print('Spectra simulations')
        # print(T,CSRBEB(B,U,N,T))
    #        dic[5]=CSRBEB(B,U,N,T)
    #        dic2[5]='RBEB'

    with open(path, 'w', newline='') as csvfile:
        w1 = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

    with open(path, 'a', newline='') as csvfile2:
        w2 = csv.writer(csvfile2, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)


# ---------------------------------------------------------------------------------------------------------------
labeldict = {'K1': '1s', 'L1': '2s', 'L2': '2p*', 'L3': '2p', 'M1': '3s', 'M2': '3p*', 'M3': '3p', 'M4': '3d*',
             'M5': '3d', 'N1': '4s', 'N2': '4p*', 'N3': '4p', 'N4': '4d*', 'N5': '4d', 'N6': '4f*', 'N7': '4f',
             'O1': '5s', 'O2': '5p*', 'O3': '5p', 'O4': '5d*', 'O5': '5d', 'O6': '5f*', 'O7': '5f', 'O8': '5g*',
             'O9': '5g', 'P1': '6s'}

the_dictionary = {
    "Kα₁": {"low_level": "K1", "high_level": "L3", "selected_state": False},
    "Kα₂": {"low_level": "K1", "high_level": "L2", "selected_state": False},
    "Kβ₁": {"low_level": "K1", "high_level": "M3", "selected_state": False},
    "Kᴵβ₂": {"low_level": "K1", "high_level": "N3", "selected_state": False},
    "Kᴵᴵβ₂": {"low_level": "K1", "high_level": "N2", "selected_state": False},
    "Kβ₃": {"low_level": "K1", "high_level": "M2", "selected_state": False},
    "Kᴵβ₄": {"low_level": "K1", "high_level": "N5", "selected_state": False},
    "Kᴵᴵβ₄": {"low_level": "K1", "high_level": "N4", "selected_state": False},
    "Kᴵβ₅": {"low_level": "K1", "high_level": "M5", "selected_state": False},
    "Kᴵᴵβ₅": {"low_level": "K1", "high_level": "M4", "selected_state": False},
    "Lα₁": {"low_level": "L3", "high_level": "M5", "selected_state": False},
    "Lα₂": {"low_level": "L3", "high_level": "M4", "selected_state": False},
    "Lβ₁": {"low_level": "L2", "high_level": "M4", "selected_state": False},
    "Lβ₃": {"low_level": "L1", "high_level": "M3", "selected_state": False},
    "Lβ₄": {"low_level": "L1", "high_level": "M2", "selected_state": False},
    "Lβ₆": {"low_level": "L3", "high_level": "N1", "selected_state": False},
    "Lβ₉": {"low_level": "L1", "high_level": "M5", "selected_state": False},
    "Lβ₁₀": {"low_level": "L1", "high_level": "M4", "selected_state": False},
    "Lβ₁₇": {"low_level": "L2", "high_level": "M3", "selected_state": False},
    "Lγ₁": {"low_level": "L2", "high_level": "N4", "selected_state": False},
    "Lγ₂": {"low_level": "L1", "high_level": "N2", "selected_state": False},
    "Lγ₃": {"low_level": "L1", "high_level": "N3", "selected_state": False},
    "Lγ₄": {"low_level": "L1", "high_level": "O3", "selected_state": False},
    "Lγ₄'": {"low_level": "L1", "high_level": "O2", "selected_state": False},
    "Lγ₅": {"low_level": "L2", "high_level": "N1", "selected_state": False},
    "Lγ₆": {"low_level": "L2", "high_level": "O4", "selected_state": False},
    "Lγ₈": {"low_level": "L2", "high_level": "O1", "selected_state": False},
    "Lη": {"low_level": "L2", "high_level": "M1", "selected_state": False},
    "Ll": {"low_level": "L3", "high_level": "M1", "selected_state": False},
    "Ls": {"low_level": "L3", "high_level": "M3", "selected_state": False},
    "Lt": {"low_level": "L3", "high_level": "M2", "selected_state": False},
    "Mα₁": {"low_level": "M5", "high_level": "N7", "selected_state": False},
    "Mα₂": {"low_level": "M5", "high_level": "N6", "selected_state": False},
    "Mβ": {"low_level": "M4", "high_level": "N6", "selected_state": False},
    "Mγ": {"low_level": "M3", "high_level": "N5", "selected_state": False},
}


def dict_updater(transition):
    # O "Estado actual" que as riscas têm quando esta função corre é o oposto daquele que está definido no dicionário, porque a função só corre se clicarmos para mudar
    current_state = not the_dictionary[transition]["selected_state"]
    # Alteramos o estado das riscas para o estado actual
    the_dictionary[transition]["selected_state"] = current_state


def G(T, energy, intens, res, width):
    """ Return Gaussian line shape at x with HWHM alpha """
    y = [0 for j in range(len(T))]  # Criar um vector com o tamanho de T cheio de zeros
    for i, l in enumerate(T):
        y[i] = intens * np.sqrt(np.log(2) / np.pi) / (res + width) \
               * np.exp(-((T[i] - energy) / (res + width)) ** 2 * np.log(2))
    return (y)


def L(T, energy, intens, res, width):
    """ Return Lorentzian line shape at x with HWHM gamma """
    y = [0 for j in range(len(T))]  # Criar um vector com o tamanho de T cheio de zeros
    for i, l in enumerate(T):
        y[i] = intens * (0.5 * (width + res) / np.pi) / ((T[i] - energy) ** 2 + (0.5 * (width + res)) ** 2)
        # y[i]=(intens*2*(width+res)) / (np.pi*(4*(T[i]-energy)**2 + (width+res)**2))
    return (y)


def V(T, energy, intens, res, width):
    """ Return the Voigt line shape at x with Lorentzian component HWHM gamma and Gaussian component HWHM alpha."""
    y = [0 for j in range(len(T))]  # Criar um vector com o tamanho de T cheio de zeros
    for i, l in enumerate(T):
        sigma = res / np.sqrt(2 * np.log(2))
        y[i] = np.real(intens * wofz((T[i] - energy + 1j * width) / sigma / np.sqrt(2))) / sigma \
               / np.sqrt(2 * np.pi)
    return (y)


def destroy(window):
    window.destroy()


def calculate(Z, ap, parent):  # Z e o numero atomico e ap e o parametro atomico a calcular (yields, widths,cross sections,etc)
    if ap == 1:  # Yields
        yields_file = dir_path / str(Z) / (str(Z) + '-yields.out')  # Caminho do ficheiro na pasta com o nome igual ao numero atomico que tem as yields
        try:
            with open(yields_file, 'r') as yields:  # Abrir o ficheiro
                lineyields = [x.strip('\n').split() for x in yields.readlines()]  # Escrever todas as linhas no
                # ficheiro como uma lista
                lineyields = list(filter(None, lineyields))  # Remover as linhas compostas apenas por celulas vazias
            # criar uma janela onde serao apresentados os resultados dos yields, widths, cross sections ou spectra simulations
            atdata = Toplevel()
            atdata.title("Fluorescence and nonRadiative Yields")  # titulo da janela
            # Criar uma grelha dentro da janela onde serao inseridos os dados
            atdatayields = ttk.Frame(atdata, padding="3 3 12 12")
            atdatayields.grid(column=0, row=0, sticky=(N, W, E, S))
            atdatayields.columnconfigure(0, weight=1)
            atdatayields.rowconfigure(0, weight=1)
            # Labels dos dados na janela
            ttk.Label(atdatayields, text="Fluorescence Yields").grid(column=0, row=0, sticky=W, columnspan=2)  # Label abaixo do qual serao escritos os resultados dos fluorescence yields
            ttk.Label(atdatayields, text="Auger Yields").grid(column=5, row=0, sticky=W, columnspan=2)  # Label abaixo do qual serao escritos os resultados dos auger yields
            ttk.Label(atdatayields, text="Coster-Kronig Yields").grid(column=8, row=0, sticky=W, columnspan=2)  # Label abaixo do qual serao escritos os resultados dos coster kronig yields
            ttk.Button(master=atdatayields, text='Export', command=lambda: write_to_xls(ap)).grid(column=12, row=0, sticky=W, columnspan=2)  # botao que exporta os resultados para um xls
            ttk.Button(master=atdatayields, text='Back', command=lambda: destroy(atdata)).grid(column=12, row=1,sticky=W, columnspan=2)  # botao que destroi esta janela
            ttk.Button(master=atdatayields, text='Exit', command=lambda: destroy(atdata)).grid(column=12, row=2, sticky=W, columnspan=2)  # botao que destroi esta janela

            NR = False  # Variavel que diz se ja se esta a ler a parte nao radiativa do ficheiro yields
            n1 = 1  # contadores para escrever os yields em linhas sequencialmente distribuidas
            n2 = 1
            n3 = 1
            for i, j in enumerate(lineyields):  # Ciclo sobre todas as linhas do ficheiro yields para ler todos os yields FY, AY, CKY
                if j[1] == 'FLyield' and j[0] != '':
                    print('FY_' + j[0], '=', j[2])
                    ttk.Label(atdatayields, text='FY_' + j[0] + '=' + j[2]).grid(column=0, row=n1, sticky=W, columnspan=2)
                    n1 = n1 + 1
                if j[1] == 'NRyield' and j[0] != '':
                    print('AY_' + j[0], '=', j[2])
                    ttk.Label(atdatayields, text='AY_' + j[0] + '=' + j[2]).grid(column=5, row=n2, sticky=W, columnspan=2)
                    n2 = n2 + 1
            for i, j in enumerate(lineyields):
                if j[1] == 'Non' and j[2] == 'Radiative' and j[3] == 'Yields':
                    NR = True
                if j[0] == 'L1' and j[2] == 'L2' and NR == True:
                    print('fL12_', '=', j[3])
                    ttk.Label(atdatayields, text='fL12_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                    n3 = n3 + 1
                if j[0] == 'L1' and j[2] == 'L3' and NR == True:
                    print('fL13_', '=', j[3])
                    ttk.Label(atdatayields, text='fL13_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                    n3 = n3 + 1
                if j[0] == 'L2' and j[2] == 'L3' and NR == True:
                    print('fL23_', '=', j[3])
                    ttk.Label(atdatayields, text='fL23_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                    n3 = n3 + 1
                if j[0] == 'M1' and j[2] == 'M2' and NR == True:
                    print('fM12_', '=', j[3])
                    ttk.Label(atdatayields, text='fM12_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                    n3 = n3 + 1
                if j[0] == 'M1' and j[2] == 'M3' and NR == True:
                    print('fM13_', '=', j[3])
                    ttk.Label(atdatayields, text='fM13_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                    n3 = n3 + 1
                if j[0] == 'M1' and j[2] == 'M4' and NR == True:
                    print('fM14_', '=', j[3])
                    ttk.Label(atdatayields, text='fM14_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                    n3 = n3 + 1
                if j[0] == 'M1' and j[2] == 'M5' and NR == True:
                    print('fM15_', '=', j[3])
                    ttk.Label(atdatayields, text='fM15_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                    n3 = n3 + 1
                if j[0] == 'M2' and j[2] == 'M3' and NR == True:
                    print('fM23_', '=', j[3])
                    ttk.Label(atdatayields, text='fM23_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                    n3 = n3 + 1
                if j[0] == 'M2' and j[2] == 'M4' and NR == True:
                    print('fM24_', '=', j[3])
                    ttk.Label(atdatayields, text='fM24_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                    n3 = n3 + 1
                if j[0] == 'M2' and j[2] == 'M5' and NR == True:
                    print('fM25_', '=', j[3])
                    ttk.Label(atdatayields, text='fM25_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                    n3 = n3 + 1
                if j[0] == 'M3' and j[2] == 'M4' and NR == True:
                    print('fM34_', '=', j[3])
                    ttk.Label(atdatayields, text='fM34_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                    n3 = n3 + 1
                if j[0] == 'M3' and j[2] == 'M5' and NR == True:
                    print('fM35_', '=', j[3])
                    ttk.Label(atdatayields, text='fM35_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                    n3 = n3 + 1
                if j[0] == 'M4' and j[2] == 'M5' and NR == True:
                    print('fM45_', '=', j[3])
                    ttk.Label(atdatayields, text='fM45_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                    n3 = n3 + 1
        except FileNotFoundError:
            messagebox.showerror("Error", "Required File is Missing")

    # ---------------------------------------------------------------------------------------------------------------

    elif ap == 2:  # Line widths
        radrates_file = dir_path / str(Z) / (str(Z) + '-radrate.out')  # Caminho do ficheiro na pasta com o nome igual ao numero atomico que tem as yields
        try:
            with open(radrates_file, 'r') as radrates:  # Abrir o ficheiro
                lineradrates = [x.strip('\n').split() for x in radrates.readlines()]  # Escrever todas as linhas no ficheiro como uma lista
                lineradrates = list(filter(None, lineradrates))  # Remover as linhas compostas apenas por celulas vazias

            # criar uma janela onde serao apresentados os resultados dos yields, widths, cross sections ou spectra
            # simulations
            atdata = Toplevel()
            atdata.title("Level and Line Widths")  # titulo da janela
            # Criar uma grelha dentro da janela onde serao inseridos os dados
            atdatayields = ttk.Frame(atdata, padding="3 3 12 12")
            atdatayields.grid(column=0, row=0, sticky=(N, W, E, S))
            atdatayields.columnconfigure(0, weight=1)
            atdatayields.rowconfigure(0, weight=1)
            # Labels dos dados na janela
            ttk.Label(atdatayields, text="Level Widths").grid(column=0, row=0, sticky=W, columnspan=2)  # Label abaixo do qual serao escritos os resultados dos level widths
            ttk.Label(atdatayields, text="Line Widths").grid(column=5, row=0, sticky=W, columnspan=2)  # Label abaixo do qual serao escritos os resultados das line widths
            ttk.Button(master=atdatayields, text='Export', command=lambda: write_to_xls(ap)).grid(column=12, row=0, sticky=W, columnspan=2)  # botao que exporta os resultados para um xls
            ttk.Button(master=atdatayields, text='Back', command=lambda: destroy(atdata)).grid(column=12, row=1, sticky=W,columnspan=2)  # botao que destroi esta janela
            ttk.Button(master=atdatayields, text='Exit', command=lambda: destroy(atdata)).grid(column=12, row=2,sticky=W, columnspan=2)  # botao que destroi esta janela
        except FileNotFoundError:
            messagebox.showerror("Error", "Required File is Missing")

    # ---------------------------------------------------------------------------------------------------------------

    elif ap == 4:  # Simular espectro
        radrates_file = dir_path / str(Z) / (str(Z) + '-intensity.out')  # Caminho do ficheiro na pasta com o nome igual ao numero atomico que tem as intensidades
        try:
            with open(radrates_file, 'r') as radrates:  # Abrir o ficheiro
                lineradrates = [x.strip('\n').split() for x in radrates.readlines()]  # Escrever todas as linhas no ficheiro como uma lista
                lineradrates = list(filter(None, lineradrates))  # Remover as linhas compostas apenas por celulas vazias
                del lineradrates[0:2]
        except FileNotFoundError:
            messagebox.showwarning("Error", "Diagram File is not Avaliable")

        satellites_file = dir_path / str(Z) / (str(Z) + '-satinty.out')  # Caminho do ficheiro na pasta com o nome igual ao numero atomico que tem as satelites
        try:
            with open(satellites_file, 'r') as satellites:  # Abrir o ficheiro
                linesatellites = [x.strip('\n').split() for x in satellites.readlines()]  # Escrever todas as linhas no ficheiro como uma lista
                linesatellites = list(filter(None, linesatellites))  # Remover as linhas compostas apenas por celulas vazias
                del linesatellites[0:2]  # Tira as linhas que têm o nome das variáveis e etc
        except FileNotFoundError:
            messagebox.showwarning("Error", "Satellites File is not Avaliable")

        shakeweights_file = dir_path / str(Z) / (str(Z) + '-shakeweights.out')  # Caminho do ficheiro na pasta com o nome igual ao numero atomico que tem as satelites
        try:
            with open(shakeweights_file, 'r') as shakeweights_f:  # Abrir o ficheiro
                shakeweights_m = [x.strip('\n').split(',') for x in shakeweights_f.readlines()]  # Escrever todas as linhas no ficheiro como uma lista
                shakeweights = []
                label1 = []
                for i, j in enumerate(shakeweights_m):
                    # Neste for corremos as linhas todas guardadas em shakeweights_m e metemos os valores numéricos no shakeweights
                    shakeweights.append(float(shakeweights_m[i][1]))
                for k, l in enumerate(shakeweights_m):
                    # Neste for corremos as linhas todas guardadas em shakeweights_m e metemos os rotulos no label 1
                    label1.append(shakeweights_m[k][0])

        except FileNotFoundError:
            messagebox.showwarning("Error", "Shake Weigth File is not Avaliable")
        sim = Toplevel(master=parent)  # Abrir janela toplevel - nao podem existir duas janelas tk abertas simultaneamente senao as variaveis dos botoes nao funcionam
        sim.title("Spectrum Simulation")
        totalvar = StringVar()
        totalvar.set('No')  # initialize Total
        normalizevar = StringVar()
        normalizevar.set('No')  # initialize Normalize
        loadvar = StringVar()
        loadvar.set('No')  # initialize

        f = Figure(figsize=(10, 5), dpi=100)  # canvas para o grafico do espectro
        # plt.style.use('ggplot')
        a = f.add_subplot(111)  # zona onde estara o grafico
        a.set_xlabel('Energy (eV)')
        a.set_ylabel('Intensity (arb. units)')

        def stem_ploter(transition_values, transition, spec_type, ind, key):
            col2 = [['b'], ['g'], ['r'], ['c'], ['m'], ['y'], ['k']]
            x = [float(row[8]) for row in transition_values]
            max_value = max(x)
            min_value = min(x)
            x.insert(0, 2 * min_value - max_value)
            x.append(2 * max_value - min_value)
            if spec_type == 'Diagram':
                y = [float(row[11]) * (1 - 0.01 * sum(shakeweights)) for row in transition_values]  # *float(row[11])*float(row[9])
                y.insert(0, 0)
                y.append(0)
                a.stem(x, y, markerfmt=' ', linefmt=str(col2[np.random.randint(0, 7)][0]), label=str(transition), use_line_collection=True)
                a.legend(loc='best', numpoints=1)
            elif spec_type == 'Satellites':
                sy_points = [float(float(row[11]) * 0.01 * shakeweights[ind]) for row in transition_values]  # *float(row[11])*float(row[9])
                sy_points.insert(0, 0)
                sy_points.append(0)
                a.stem(x, sy_points, markerfmt=' ', linefmt=str(col2[np.random.randint(0, 7)][0]), label=transition + ' - ' + labeldict[key], use_line_collection=True)  # Plot a stemplot
                a.legend(loc='best', numpoints=1)

        def plot_stick(total, normalize, y0, enoffset, res, spectype, peak, load, sat, num_of_points, x_mx, x_mn, graph_area):
            graph_area.clear()
            col2 = [['b'], ['g'], ['r'], ['c'], ['m'], ['y'], ['k']]
            x = [[] for i in range(len(the_dictionary))]
            y = [[] for i in range(len(the_dictionary))]
            w = [[] for i in range(len(the_dictionary))]
            xs = [[[] for i in labeldict] for j in x]
            ys = [[[] for i in labeldict] for j in y]
            ws = [[[] for i in labeldict] for j in w]
            if spectype == 'Stick':
                for transition in the_dictionary:
                    # Se a transição estiver selecionada:
                    if the_dictionary[transition]["selected_state"]:
                        # Estas variáveis servem só para não ter de escrever o acesso ao valor do dicionário todas as vezes
                        low_level = the_dictionary[transition]["low_level"]
                        high_level = the_dictionary[transition]["high_level"]
                        diag_stick_val = [line for line in lineradrates if line[1] in low_level and line[5] == high_level and float(line[9]) != 0]  # Cada vez que o for corre, lê o ficheiro de uma transição
                        # for u in range(len(diag_stick_val)):
                        #     if diag_stick_val[u][1] in low_level:
                        #         print(diag_stick_val[u][1], low_level)
                        sat_stick_val = [line for line in linesatellites if low_level in line[1] and high_level in line[5] and float(line[9]) != 0]
                        if sat == 'Diagram':
                            stem_ploter(diag_stick_val, transition, 'Diagram', 0, 0)
                        elif sat == 'Satellites':
                            b1 = 0
                            for ind, key in enumerate(label1):
                                sat_stick_val_ind1 = [line for line in sat_stick_val if low_level + key in line[1] and key + high_level in line[5]]
                                sat_stick_val_ind2 = [line for line in sat_stick_val if low_level + key in line[1] and high_level + key in line[5] and key != high_level]
                                sat_stick_val_ind3 = [line for line in sat_stick_val if key + low_level in line[1] and key + high_level in line[5]]
                                sat_stick_val_ind4 = [line for line in sat_stick_val if key + low_level in line[1] and high_level + key in line[5] and key != high_level]
                                sat_stick_val_ind = sat_stick_val_ind1 + sat_stick_val_ind2 + sat_stick_val_ind3 + sat_stick_val_ind4
                                if len(sat_stick_val_ind) > 1:
                                    stem_ploter(sat_stick_val_ind, transition, 'Satellites', ind, key)
                                b1 += 100 / len(label1)
                                progress_var.set(b1)
                                sim.update_idletasks()
                        elif sat == 'Diagram + Satellites':
                            stem_ploter(diag_stick_val, transition, 'Diagram', 0, 0)
                            b1 = 0
                            for ind, key in enumerate(label1):
                                sat_stick_val_ind1 = [line for line in sat_stick_val if low_level + key in line[1] and key + high_level in line[5]]
                                sat_stick_val_ind2 = [line for line in sat_stick_val if low_level + key in line[1] and high_level + key in line[5] and key != high_level]
                                sat_stick_val_ind3 = [line for line in sat_stick_val if key + low_level in line[1] and key + high_level in line[5]]
                                sat_stick_val_ind4 = [line for line in sat_stick_val if key + low_level in line[1] and high_level + key in line[5] and key != high_level]
                                sat_stick_val_ind = sat_stick_val_ind1 + sat_stick_val_ind2 + sat_stick_val_ind3 + sat_stick_val_ind4
                                if len(sat_stick_val_ind) > 1:
                                    stem_ploter(sat_stick_val_ind, transition, 'Satellites', ind, key)
                                b1 += 100 / len(label1)
                                progress_var.set(b1)
                                sim.update_idletasks()
                    graph_area.set_xlabel('Energy (eV)')
                    graph_area.set_ylabel('Intensity (arb. units)')
            # --------------------------------------------------------------------------------------------------------------------------
            elif spectype == 'Simulation':
                # Contrariamente ao spectype == 'Stick' onde os plots são feitos quando se trata de cada risca, aqui,
                # o  que se faz é obter os valores necessários para os plots. Não se faz nenhum plot em si dentro deste ciclo.
                for index, transition in enumerate(the_dictionary):
                    if the_dictionary[transition]["selected_state"]:
                        low_level = the_dictionary[transition]["low_level"]  # orbital da lacuna no início da transição
                        high_level = the_dictionary[transition]["high_level"]  # orbital da lacuna no fim da transição
                        diag_sim_val = [line for line in lineradrates if line[1] in low_level and line[5] == high_level and float(line[9]) != 0]  # Guarda para uma lista as linhas do ficheiro que se referem à trasição transition
                        sat_sim_val = [line for line in linesatellites if low_level in line[1] and high_level in line[5] and float(line[9]) != 0]  # Guarda para uma lista as linhas do ficheiro que se referem às satélites de transition
                        if sat == 'Diagram':
                            x1 = [float(row[8]) for row in diag_sim_val]
                            y1 = [float(row[11]) * (1 - sum(shakeweights)) for row in diag_sim_val]
                            w1 = [float(row[15]) for row in diag_sim_val]
                            x[index] = x1
                            y[index] = y1
                            w[index] = w1
                        elif sat == 'Satellites':
                            for ind, key in enumerate(label1):
                                sat_sim_val_ind1 = [line for line in sat_sim_val if low_level + key in line[1] and key + high_level in line[5]]
                                sat_sim_val_ind2 = [line for line in sat_sim_val if low_level + key in line[1] and high_level + key in line[5] and key != 'L3']
                                sat_sim_val_ind3 = [line for line in sat_sim_val if key + low_level in line[1] and key + high_level in line[5]]
                                sat_sim_val_ind4 = [line for line in sat_sim_val if key + low_level in line[1] and high_level + key in line[5] and key != 'L3']
                                sat_sim_val_ind = sat_sim_val_ind1 + sat_sim_val_ind2 + sat_sim_val_ind3 + sat_sim_val_ind4
                                if len(sat_sim_val_ind) > 1:
                                    x1s = [float(row[8]) for row in sat_sim_val_ind]
                                    y1s = [float(float(row[11]) * shakeweights[ind]) for row in sat_sim_val_ind]
                                    w1s = [float(row[15]) for row in sat_sim_val_ind]
                                    xs[index][ind] = x1s
                                    ys[index][ind] = y1s
                                    ws[index][ind] = w1s
                        elif sat == 'Diagram + Satellites':
                            x1 = [float(row[8]) for row in diag_sim_val]
                            y1 = [float(row[11]) * (1 - sum(shakeweights)) for row in diag_sim_val]
                            w1 = [float(row[15]) for row in diag_sim_val]
                            x[index] = x1
                            y[index] = y1
                            w[index] = w1
                            # ---------------------------------------------------------------------------------------------------------------------
                            ka1s = [line for line in linesatellites if 'K1' in line[1] and 'L3' in line[5] and float(line[9]) != 0]
                            for ind, key in enumerate(label1):
                                sat_sim_val_ind1 = [line for line in sat_sim_val if low_level + key in line[1] and key + high_level in line[5]]
                                sat_sim_val_ind2 = [line for line in sat_sim_val if low_level + key in line[1] and high_level + key in line[5] and key != 'L3']
                                sat_sim_val_ind3 = [line for line in sat_sim_val if key + low_level in line[1] and key + high_level in line[5]]
                                sat_sim_val_ind4 = [line for line in sat_sim_val if key + low_level in line[1] and high_level + key in line[5] and key != 'L3']
                                sat_sim_val_ind = sat_sim_val_ind1 + sat_sim_val_ind2 + sat_sim_val_ind3 + sat_sim_val_ind4
                                if len(sat_sim_val_ind) > 1:
                                    x1s = [float(row[8]) for row in sat_sim_val_ind]
                                    y1s = [float(float(row[11]) * shakeweights[ind]) for row in sat_sim_val_ind]
                                    w1s = [float(row[15]) for row in sat_sim_val_ind]
                                    xs[index][ind] = x1s
                                    ys[index][ind] = y1s
                                    ws[index][ind] = w1s

                # -------------------------------------------------------------------------------------------
                # Verificar se se selecionaram transições indísponíveis
                bad_selection = 0
                for index, transition in enumerate(the_dictionary):
                    if the_dictionary[transition]["selected_state"]:
                        if not x[index]:
                            messagebox.showwarning("Wrong Transition", transition + " is not Available")
                            x[index]= []
                            bad_selection += 1

                # -------------------------------------------------------------------------------------------
                # Calcular a dispersão em energia das varias riscas para criar o array de valores de x a plotar em funcao desta dispersão e da resolução experimental
                try:
                    if sat == 'Diagram':
                        deltaE = []
                        for j, k in enumerate(x):  # Percorremos as listas guardadas em x. k é a lista e i o indice onde ela está guardada em x.
                            if k != []:  # Se a lista não estiver vazia, guardamos em deltaE a diferença entre o seu valor máximo e mínimo
                                deltaE.append(max(x[j]) - min(x[j]))
                        max_value = max([max(x[i]) for i in range(len(x)) if x[i] != []])
                        min_value = min([min(x[i]) for i in range(len(x)) if x[i] != []])

                    elif sat == 'Satellites' or 'Diagram + Satellites':
                        deltaE = []
                        for j, k in enumerate(xs):  # Ciclo sobre os elementos de x (ka1, ka2, kb1, etc... 7 no total)
                            for l, m in enumerate(xs[j]):
                                if m != []:
                                    deltaE.append(max(m) - min(m))
                        max_value = max([max(xs[i][j]) for i in range(len(xs)) for j in range(len(xs[i])) if xs[i][j] != []])  # valor max de todos os elementos de xs (satt) que tem 7 linhas(ka1, ka2, etc) e o tamanho da lista label1 dentro de cada linha
                        min_value = min([min(xs[i][j]) for i in range(len(xs)) for j in range(len(xs[i])) if xs[i][j] != []])
                    # Definimos o x Mínimo que queremos plotar. Pode ser definido automáticamente ou pelo valor x_mn
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
                    # Calcular o array com os valores de xfinal igualmente espacados
                    xfinal = np.array(linspace(array_input_min, array_input_max, num=num_of_points))
                except ValueError:
                    xfinal= np.zeros(num_of_points)
                    if not bad_selection:
                        messagebox.showerror("No Transition", "No transition was chosen")
                    else:
                        messagebox.showerror("Wrong Transition", "You chose "+ str(bad_selection) + " invalid transition(s)")


                # ---------------------------------------------------------------------------------------------------------------
                exp_x = []
                exp_y = []
                if load != 'No':  # procedimento para fazer o plot experimental
                    f.clf()
                    gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])
                    new_graph_area = f.add_subplot(gs[0])
                    graph_area = new_graph_area
                    residues_graph = f.add_subplot(gs[1])
                    residues_graph.set_xlabel('Energy (eV)')
                    residues_graph.set_ylabel('Residues (arb. units)')
                    # graph_area.set_xticklabels([]) Isto tira os valores do gráfico grande
                    normalize = 'Normalize'  # O plot experimental para poder ser comparado sera sempre normalizado
                    normalizevar.set('Normalize')
                    exp_spectrum = list(csv.reader(open(load, 'r')))  # Carregar a matriz do espectro experimental do ficheiro escolhido no menu
                    for i, it in enumerate(exp_spectrum):
                        for j, itm in enumerate(exp_spectrum[i]):  # Transformar os valores do espectro experimental para float
                            if exp_spectrum[i][j] != '':
                                exp_spectrum[i][j] = float(itm)
                    xe = ([float(row[0]) for row in exp_spectrum])
                    ye = np.array([float(row[1]) for row in exp_spectrum])
                    maxe = max(xe)
                    mine = min(xe)

                    if mine < array_input_min:
                        if x_mn == 'Auto':  # x_mn é inicializado a Auto, da primeira vez que o programa corre isto é verdade
                            array_input_min = mine - enoffset
                            min_x_lim = min([mine, min(xfinal)])
                        else:
                            min_x_lim = float(x_mn)
                            array_input_min = min_x_lim - enoffset

                    if maxe > array_input_max:
                        if x_mx == 'Auto':  # x_mx é inicializado a Auto, da primeira vez que o programa corre isto é verdade
                            array_input_max = maxe - enoffset
                            max_x_lim = max([maxe, max(xfinal)])
                        else:
                            max_x_lim = float(x_mx)
                            array_input_max = max_x_lim - enoffset


                    for i in range(len(xe)):
                        if min_x_lim <= xe[i] <= max_x_lim:
                            exp_x.append(xe[i])
                            exp_y.append(ye[i])

                    xfinal = np.array(linspace(array_input_min, array_input_max, num=num_of_points))
                    graph_area.scatter(exp_x, exp_y / max(exp_y), marker='.', label='Exp.')  # Plot the simulation of all lines
                    graph_area.legend()

                # ---------------------------------------------------------------------------------------------------------------

                yfinal = [[0 for i in range(len(xfinal))] for j in range(len(the_dictionary))]  # Criar uma lista de listas cheia de zeros que ira ser o yfinal para diagrama
                ytot = [0 for i in range(len(xfinal))]
                yfinals = [[[0 for n in range(len(xfinal))] for i in label1] for j in range(len(the_dictionary))]  # Criar uma lista de listas cheia de zeros que ira ser o yfinal para satellites
                y_interp = [0 for i in range(len(exp_x))]  # Criar lista vazia para o gráfico de resíduos
                norm = 0
                # Ciclo sobre todas os conjuntos de riscas
                if sat == 'Diagram':
                    b1 = 0
                    for j, k in enumerate(y):
                        # Ciclo sobre todas as riscas para somar um pico (voigt, lorentz ou gauss) para cada individual
                        for i, n in enumerate(k):
                            if peak == 'Voigt':
                                yfinal[j] = np.add(yfinal[j], V(xfinal, x[j][i], y[j][i], res, w[j][i]))
                            elif peak == 'Lorentzian':
                                yfinal[j] = np.add(yfinal[j], L(xfinal, x[j][i], y[j][i], res, w[j][i]))
                            elif peak == 'Gaussian':
                                yfinal[j] = np.add(yfinal[j], G(xfinal, x[j][i], y[j][i], res, w[j][i]))
                            b1 += 100 / (len(y) * len(k))
                            progress_var.set(b1)
                            sim.update_idletasks()
                        if k != []:  # Excluir as linhas que nao foram seleccionados nos botoes
                            ytot = np.add(ytot, yfinal[j])
                            if max(ytot) > norm:
                                norm = max(ytot)
                    b1 = 100
                    progress_var.set(b1)
                    sim.update_idletasks()
                elif sat == 'Satellites':
                    b1 = 0
                    for j, k in enumerate(ys):
                        for l, m in enumerate(ys[j]):
                            # Ciclo sobre todas as riscas para somar um pico (voigt, lorentz ou gauss) para cada individual
                            for i, n in enumerate(m):
                                if peak == 'Voigt':
                                    yfinals[j][l] = np.add(yfinals[j][l], V(xfinal, xs[j][l][i], ys[j][l][i], res, ws[j][l][i]))
                                elif peak == 'Lorentzian':
                                    yfinals[j][l] = np.add(yfinals[j][l], L(xfinal, xs[j][l][i], ys[j][l][i], res, ws[j][l][i]))
                                elif peak == 'Gaussian':
                                    yfinals[j][l] = np.add(yfinals[j][l], G(xfinal, xs[j][l][i], ys[j][l][i], res, ws[j][l][i]))
                                b1 += 100 / (len(ys) * len(label1) * len(m))
                                progress_var.set(b1)
                                sim.update_idletasks()
                            if m != []:  # Excluir as linhas que nao foram seleccionados nos botoes
                                ytot = np.add(ytot, yfinals[j][l])
                                if max(ytot) > norm:
                                    norm = max(ytot)
                    b1 = 100
                    progress_var.set(b1)
                    sim.update_idletasks()
                elif sat == 'Diagram + Satellites':
                    b1 = 0
                    for j, k in enumerate(y):
                        # Ciclo sobre todas as riscas para somar um pico (voigt, lorentz ou gauss) para cada individual
                        for i, n in enumerate(k):
                            if peak == 'Voigt':
                                yfinal[j] = np.add(yfinal[j], V(xfinal, x[j][i], y[j][i], res, w[j][i]))
                            elif peak == 'Lorentzian':
                                yfinal[j] = np.add(yfinal[j], L(xfinal, x[j][i], y[j][i], res, w[j][i]))
                            elif peak == 'Gaussian':
                                yfinal[j] = np.add(yfinal[j], G(xfinal, x[j][i], y[j][i], res, w[j][i]))
                            b1 += 200 / (len(y) * len(k))
                            progress_var.set(b1)
                            sim.update_idletasks()
                        if k != []:  # Excluir as linhas que nao foram seleccionados nos botoes
                            ytot = np.add(ytot, yfinal[j])
                            if max(ytot) > norm:
                                norm = max(ytot)

                    b1 = 50
                    progress_var.set(b1)
                    sim.update_idletasks()
                    for j, k in enumerate(ys):
                        for l, m in enumerate(ys[j]):
                            # Ciclo sobre todas as riscas para somar um pico (voigt, lorentz ou gauss) para cada individual
                            for i, n in enumerate(m):
                                if peak == 'Voigt':
                                    yfinals[j][l] = np.add(yfinals[j][l],
                                                           V(xfinal, xs[j][l][i], ys[j][l][i], res, ws[j][l][i]))
                                elif peak == 'Lorentzian':
                                    yfinals[j][l] = np.add(yfinals[j][l],
                                                           L(xfinal, xs[j][l][i], ys[j][l][i], res, ws[j][l][i]))
                                elif peak == 'Gaussian':
                                    yfinals[j][l] = np.add(yfinals[j][l],
                                                           G(xfinal, xs[j][l][i], ys[j][l][i], res, ws[j][l][i]))
                                b1 += 100 / (len(ys) * len(label1) * len(m))
                                progress_var.set(b1)
                                sim.update_idletasks()
                            if m != []:  # Excluir as linhas que nao foram seleccionados nos botoes
                                ytot = np.add(ytot, yfinals[j][l])
                                if max(ytot) > norm:
                                    norm = max(ytot)
                    b1 = 100
                    progress_var.set(b1)
                    sim.update_idletasks()

                # ------------------------------------------------------------------------------------------------------------------------
                if sat == 'Diagram':
                    for index, key in enumerate(the_dictionary):
                        if the_dictionary[key]["selected_state"]:
                            if normalize == 'Normalize':
                                graph_area.plot(xfinal + enoffset, (np.array(yfinal[index]) * (1 - y0) / norm) + y0, label=key, color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                                graph_area.legend()
                            elif normalize == 'No':
                                graph_area.plot(xfinal+ enoffset, (np.array(yfinal[index]) + y0), label=key)  # Plot the simulation of all lines #, color=str(col2[np.random.randint(0, 7)][0])
                                graph_area.legend()

                elif sat == 'Satellites':
                    for index, key in enumerate(the_dictionary):
                        if the_dictionary[key]["selected_state"]:
                            for l, m in enumerate(yfinals[index]):
                                if max(m) != 0:  # Excluir as linhas que nao foram seleccionados nos botoes
                                    if normalize == 'Normalize':
                                        graph_area.plot(xfinal+ enoffset, (np.array(yfinals[index][l]) * (1 - y0) / norm) + y0, label=key + ' - ' + labeldict[label1[l]], color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                                        graph_area.legend()
                                    elif normalize == 'No':
                                        graph_area.plot(xfinal+ enoffset, (np.array(yfinals[index][l]) + y0), label=key + ' - ' + labeldict[label1[l]], color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                                        graph_area.legend()

                elif sat == 'Diagram + Satellites':
                    for index, key in enumerate(the_dictionary):
                        if the_dictionary[key]["selected_state"]:
                            if normalize == 'Normalize':
                                graph_area.plot(xfinal+ enoffset, (np.array(yfinal[index]) * (1 - y0) / norm) + y0, label=key, color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                                graph_area.legend()
                            elif normalize == 'No':
                                graph_area.plot(xfinal+ enoffset, (np.array(yfinal[index]) + y0), label=key, color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                                graph_area.legend()

                    for index, key in enumerate(the_dictionary):
                        if the_dictionary[key]["selected_state"]:
                            for l, m in enumerate(yfinals[index]):
                                if max(m) != 0:  # Excluir as linhas que nao foram seleccionados nos botoes
                                    if normalize == 'Normalize':
                                        graph_area.plot(xfinal+ enoffset, (np.array(yfinals[index][l]) * (1 - y0) / norm) + y0, label=key + ' - ' + labeldict[label1[l]], color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                                        graph_area.legend()
                                    elif normalize == 'No':
                                        graph_area.plot(xfinal+ enoffset, (np.array(yfinals[index][l]) + y0), label=key + ' - ' + labeldict[label1[l]], color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                                        graph_area.legend()

                ################ CÁLCULO RESÍDUOS ###########################
                if load != 'No':
                    f_interpolate = interp1d(xfinal+ enoffset, (ytot * (1 - y0))/norm + y0, kind='cubic')
                    y_res = [0 for x in range(len(exp_x))]
                    chi_sum = 0

                    for g, h in enumerate(exp_x):
                        y_interp[g] = f_interpolate(h)
                        y_res[g] = (exp_y[g] / max(exp_y)) - y_interp[g]
                        chi_sum += (y_res[g] * y_res[g])
                    chi_sqrd = chi_sum / len(exp_x)
                    residues_graph.plot(exp_x, y_res / max(y_res))
                    residues_graph.legend(title="χ²= "+ "{:.5f}".format(chi_sqrd))


                #############################################################

                if total == 'Total':
                    if normalize == 'Normalize':
                        graph_area.plot(xfinal + enoffset, (ytot * (1 - y0) / norm) + y0, label='Total', ls='--', lw=2, color='k')  # Plot the simulation of all lines
                        graph_area.legend()
                    elif normalize == 'No':
                        graph_area.plot(xfinal + enoffset, ytot + y0, label='Total', ls='--', lw=2, color='k')  # Plot the simulation of all lines
                        graph_area.legend()

                if normalize == 'Normalize':
                    graph_area.set_ylim([0, 1.1])  # Manter os mesmo aspecto em y quer o grafico esteja normalizado que nao
                elif normalize == 'No':
                    graph_area.set_ylim([0, norm * 1.1])

                graph_area.set_ylabel('Intensity (arb. units)')
                if load == 'No':
                    graph_area.set_xlabel('Energy (eV)')

                matrix = [[0 for x in range(int(1 + len(yfinal) + len(yfinal) * len(label1) + 1))] for y in range(len(xfinal))]  # o range desta matriz corresponde a coluna da energia (1) mais o numero de colunas das transicoes (Ka1, Ka2,
                # etc...) mais a quantidade de transicoes possiveis vezes o numero de satelites consideradas (pelo ficheiro shakeweights) mais 1 coluna que tera o total

                if spectype == 'Simulation':
                    for i, j in enumerate(xfinal):
                        matrix[i][0] = xfinal[i]
                        for n, m in enumerate(yfinals):
                            matrix[i][int(1 + (n))] = yfinal[n][i]
                            for k, l in enumerate(label1):
                                matrix[i][int(len(yfinal) + (n) * len(label1) + (k + 1))] = yfinals[n][k][i]

                matrix2 = ['Energy(eV)', 'Ka1', 'Ka2', 'Kb1', 'La1', 'La2', 'Lb1', 'Kb3']  # matriz que vai ter as labels a serem gravadas para o ficheiro data.csv
                for h in range(len(yfinal)):  # irao ser tantas riscas quantas as contempladas no programa vezes o numero de satelites que estiverem no ficheiro shakeweghts.out
                    for g in range(len(label1)):
                        matrix2 = matrix2 + [str(matrix2[h + 1]) + '-' + str(label1[g])]
                matrix2 = matrix2 + ['Total']  # Inserir a label da ultima coluna (total)

                matrix = [matrix2] + matrix
                for i, item in enumerate(matrix):
                    if i == 0:
                        with open('data.csv', 'w', newline='') as csvfile:
                            w1 = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                            w1.writerow(matrix[i])
                    else:
                        with open('data.csv', 'a', newline='') as csvfile2:
                            w1 = csv.writer(csvfile2, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                            w1.writerow(matrix[i])

            # --------------------------------------------------------------------------------------------------------------------------
            f.canvas.draw()

        figure_frame = Frame(sim, bd = 1, relief = GROOVE)  # frame para o grafico
        figure_frame.grid(row=0, column=0, columnspan=2, sticky="nesw")  # frame para o grafico
        canvas = FigureCanvasTkAgg(f, master=figure_frame)
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        toolbar_frame = Frame(sim)
        toolbar_frame.grid(row=4, column=0, columnspan=2, sticky="w")
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)

        buttons_frame = Frame(sim, bd = 1, relief = GROOVE)  # Frame transições
        buttons_frame.grid(row=1, column=0,columnspan=2, sticky="nesw")
        buttons_frame2 = Frame(sim, bd = 1, relief = GROOVE)  # Max, min & Points Frame
        buttons_frame2.grid(row=2, column=0, sticky="nesw")
        buttons_frame3 = Frame(sim, bd = 1, relief = GROOVE)  # Frame  y0, Energy offset e Calculate
        buttons_frame3.grid(row=2, column=1, sticky="nesw")
        buttons_frame4 = Frame(sim)  # Frame Barra Progresso
        buttons_frame4.grid(row=3, column=0, columnspan=2, sticky="nesw")

        def on_key_event(event):  # NAO SEI BEM O QUE ISTO FAZ
            print('you pressed %s' % event.key)
            key_press_handler(event, canvas, toolbar)

        canvas.mpl_connect('key_press_event', on_key_event)  # NAO SEI BEM O QUE ISTO FAZ

        def _quit():
            for transition in the_dictionary:
                if the_dictionary[transition]["selected_state"]:
                    dict_updater(transition)
            sim.quit()  # stops mainloop
            sim.destroy()  # this is necessary on Windows to prevent
            # Fatal Python Error: PyEval_RestoreThread: NULL tstate

        def restarter():
            for transition in the_dictionary:
                if the_dictionary[transition]["selected_state"]:
                    dict_updater(transition)
            sim.quit()  # stops mainloop
            sim.destroy()
            parent.destroy()
            main()  # this is necessary on Windows to prevent
            # Fatal Python Error: PyEval_RestoreThread: NULL tstate

        def load():  # funcao que muda o nome da variavel correspondente ao ficheiro experimental
            fname = askopenfilename(filetypes=(("Spectra files", "*.csv *.txt"), ("All files", "*.*")))
            loadvar.set(fname)  # Muda o nome da variavel loadvar para a string correspondente ao path do ficheiro seleccionado

        exp_resolution = DoubleVar(value=1.0)  # Float correspondente a resolucao experimental
        y0 = DoubleVar(value=0.0)  # Float correspondente ao fundo experimental
        energy_offset = DoubleVar(value=0.0)  # Float correspondente a resolucao experimental
        number_points = IntVar(value=500)  # Numero de pontos a plotar na simulação
        x_max = StringVar()  # Controlo do x Máximo a entrar no gráfico
        x_max.set('Auto')
        x_min = StringVar()  # Controlo do x Mínimo a entrar no gráfico
        x_min.set('Auto')
        progress_var = DoubleVar()  # Float que da a percentagem de progresso

        # -------------------------------------------------------------------------------------------------------------
        # Selecção das Transições na Combobox + Apresentação das transições no label

        transition_list = []
        label_text = StringVar()
        label_text.set('Selected Transitions: ')
        trans_lable = tk.Label(buttons_frame, textvariable=label_text).grid(row=0, column=1)

        def selected(event):
            text_T = drop_menu.get() # Lê Texto da box com as transições
            dict_updater(text_T) # Faz update do dicionário com a transição lida
            to_print = '' # Texto a imprimir no label com as transições selecionadas
            if the_dictionary[text_T]["selected_state"]: # Se a transição estiver selecionada:
                transition_list.append(text_T) # É adicionada à lista de transições que vai para o label
            elif not the_dictionary[text_T]["selected_state"]: # Se for descelecionada
                transition_list.remove(text_T) # É removida da lista que vai para o label
            for a, b in enumerate(transition_list): # Este for serve para colocar as virgulas entre as transições que vão para o label
                if len(transition_list) == a + 1:
                    to_print += str(b) + ' '
                else:
                    to_print += str(b) + ', '
            label_text.set('Selected Transitions: ' + to_print) # Definimos o novo label

        drop_menu = ttk.Combobox(buttons_frame, value=[transition for transition in the_dictionary], height=5, width=10)
        drop_menu.set('Transitions:')
        drop_menu.bind("<<ComboboxSelected>>", selected)
        drop_menu.grid(row=0, column=0, padx = 20)

        # Min Max e Nº Pontos
        ttk.Label(buttons_frame2, text="Points").pack(side=tk.LEFT)
        points = ttk.Entry(buttons_frame2, width=7, textvariable=number_points).pack(side=tk.LEFT)
        ttk.Label(buttons_frame2, text="x Máx").pack(side=tk.LEFT)
        max_x = ttk.Entry(buttons_frame2, width=7, textvariable=x_max).pack(side=tk.LEFT)
        ttk.Label(buttons_frame2, text="x Min").pack(side=tk.LEFT)
        min_x = ttk.Entry(buttons_frame2, width=7, textvariable=x_min).pack(side=tk.LEFT)

        # Res, Offsets e Calculate
        ttk.Style().configure('red/black.TButton', foreground='red', background='black')  # , font = ('Sans','10','bold'))  #definicoes botao "calculate"
        ttk.Button(master=buttons_frame3, text="Calculate",
                   command=lambda: plot_stick(totalvar.get(), normalizevar.get(), y0.get(), energy_offset.get(), exp_resolution.get(), choice_var.get(), type_var.get(), loadvar.get(), satelite_var.get(), number_points.get(), x_max.get(), x_min.get(),
                                              a), style='red/black.TButton').pack(side=tk.RIGHT, padx = (30, 0))
        # y0
        res_entry = ttk.Entry(buttons_frame3, width=7, textvariable=y0).pack(side=tk.RIGHT)
        ttk.Label(buttons_frame3, text="y0").pack(side=tk.RIGHT)
        # En. Offset
        res_entry = ttk.Entry(buttons_frame3, width=7, textvariable=energy_offset).pack(side=tk.RIGHT, padx = (0, 30))
        ttk.Label(buttons_frame3, text="En. offset (eV)").pack(side=tk.RIGHT)
        # Energy Resolution
        ttk.Label(buttons_frame3, text="Experimental Resolution (eV)").pack(side=tk.LEFT)
        res_entry = ttk.Entry(buttons_frame3, width=7, textvariable=exp_resolution).pack(side=tk.LEFT)

        # Barra progresso
        progressbar = ttk.Progressbar(buttons_frame4, variable=progress_var, maximum=100)
        progressbar.pack(fill=X, expand=1)

        def enter_function(event):
            plot_stick(totalvar.get(), normalizevar.get(), y0.get(), energy_offset.get(), exp_resolution.get(), choice_var.get(), type_var.get(), loadvar.get(), satelite_var.get(), number_points.get(), x_max.get(), x_min.get(), a)

        sim.bind('<Return>', enter_function )

        # MENUS  ---------------------------------------------------------------------------------------------------------------

        my_menu = Menu(sim)
        sim.config(menu=my_menu)
        options_menu = Menu(my_menu, tearoff=0)
        stick_plot_menu = Menu(my_menu, tearoff=0)
        transition_type_menu = Menu(my_menu, tearoff=0)
        fit_type_menu = Menu(my_menu, tearoff=0)
        more_options_menu = Menu(my_menu, tearoff=0)
        # ---------------------------------------------------------------------------------------------------------------
        my_menu.add_cascade(label="Options", menu=options_menu)
        options_menu.add_command(label="Choose New Element", command=restarter)
        options_menu.add_command(label="Export Spectrum", command=lambda: write_to_xls(ap))
        options_menu.add_command(label="Load Experimental Spectrum", command=load)
        options_menu.add_command(label="Quit", command=_quit)
        # ---------------------------------------------------------------------------------------------------------------
        my_menu.add_cascade(label="Spectrum Type", menu=stick_plot_menu)
        choice_var = StringVar(value='Simulation')
        stick_plot_menu.add_checkbutton(label='Stick', variable=choice_var, onvalue='Stick', offvalue='')
        stick_plot_menu.add_checkbutton(label='Simulation', variable=choice_var, onvalue='Simulation', offvalue='')
        # ---------------------------------------------------------------------------------------------------------------
        my_menu.add_cascade(label="Transition Type", menu=transition_type_menu)
        satelite_var = StringVar(value='Diagram')
        transition_type_menu.add_checkbutton(label='Diagram', variable=satelite_var, onvalue='Diagram', offvalue='')
        transition_type_menu.add_checkbutton(label='Satellites', variable=satelite_var, onvalue='Satellites', offvalue='')
        transition_type_menu.add_checkbutton(label='Diagram + Satellites', variable=satelite_var, onvalue='Diagram + Satellites', offvalue='')
        # ---------------------------------------------------------------------------------------------------------------
        my_menu.add_cascade(label="Fit Type", menu=fit_type_menu)
        type_var = StringVar(value='Voigt')
        fit_type_menu.add_checkbutton(label='Voigt', variable=type_var, onvalue='Voigt', offvalue='')
        fit_type_menu.add_checkbutton(label='Lorentzian', variable=type_var, onvalue='Lorentzian', offvalue='')
        fit_type_menu.add_checkbutton(label='Gaussian', variable=type_var, onvalue='Gaussian', offvalue='')
        # ---------------------------------------------------------------------------------------------------------------
        my_menu.add_cascade(label="Fit Options", menu=more_options_menu)
        more_options_menu.add_checkbutton(label='Show Total Y', variable=totalvar, onvalue='Total', offvalue='No')
        more_options_menu.add_checkbutton(label='Normalize', variable=normalizevar, onvalue='Normalize', offvalue='No')

        # ---------------------------------------------------------------------------------------------------------------

        sim.mainloop()


# -----------------------------------------------------------------------------
def shell(Z):  # Definicoes relacionadas com a segunda janela (depois da tabela periodica)

    def p():  # Esta def so faz imprimir na consola o valor da variavel CheckVar (yields=1, widths=2, etc...)
        print(CheckVar.get())

    shells = Tk()  # Abrir uma janela com botoes que seleccionam o que calcular (yields, widths, cross sections e simulacao)
    shells.title("Atomic Parameters")  # nome da janela

    CheckVar = IntVar()  # variavel que vai dar o valor do botao seleccionado (yields=1, widths=2, cross sections=3, simulacao=4)
    CheckVar.set(1)  # initialize (o botao 1, yields, comeca seleccionado por defeito)

    # Propriedades da janela
    subshell = ttk.Frame(shells, padding="3 3 12 12")
    subshell.grid(column=0, row=0, sticky=(N, W, E, S))
    subshell.columnconfigure(0, weight=1)
    subshell.rowconfigure(0, weight=1)
    # botoes e nomes dos botoes
    ttk.Button(subshell, text="Get", command=lambda: calculate(Z, CheckVar.get(), shells)).grid(column=6, row=5, sticky=E, columnspan=2)  # este botao faz correr a funcao calculate
    ttk.Button(subshell, text="Exit", command=lambda: destroy(shells)).grid(column=6, row=6, sticky=E, columnspan=2)  # este botao fecha a janela
    ttk.Radiobutton(subshell, text='Yields', command=p, variable=CheckVar, value=1).grid(column=0, row=5, sticky=W)
    ttk.Radiobutton(subshell, text='Level Widths', command=p, variable=CheckVar, value=2).grid(column=1, row=5, sticky=W)
    ttk.Radiobutton(subshell, text='Cross Sections', command=p, variable=CheckVar, value=3).grid(column=0, row=6, sticky=W)
    ttk.Radiobutton(subshell, text='Spectra Simulations', command=p, variable=CheckVar, value=4).grid(column=1, row=6, sticky=W)
    ttk.Label(subshell, text="Which parameters do you want to retrieve?").grid(column=0, row=4, sticky=W, columnspan=2)

    subshell.mainloop()


# Main class para a janela principal com a tabela periodica
class App(Tk):
    def __init__(self):
        Tk.__init__(self)

        def quit_window(Z):
            self.destroy()
            shell(Z)

        self.title("Periodic Table of the Elements")

        self.topLabel = Label(self, text="", font=20)
        self.topLabel.grid(row=2, column=3, columnspan=10)

        self.Label1 = Label(self, text="Click the element for which you would like to obtain the atomic parameters.",
                            font=22)
        self.Label1.grid(row=0, column=0, columnspan=18)

        self.Label2 = Label(self, text="", font=20)
        self.Label2.grid(row=8, column=0, columnspan=18)

        self.Label3 = Label(self, text="* Lanthanoids", font=20)
        self.Label3.grid(row=9, column=1, columnspan=2)

        self.Label4 = Label(self, text="** Actinoids", font=20)
        self.Label4.grid(row=10, column=1, columnspan=2)

        per_table = [[1, 1.0079, ' Hydrogen ', ' H ', 0.09, 'grey', 1, 1, ' 1s1 ', 13.5984],
                     [2, 4.0026, ' Helium ', ' He ', 0.18, 'cyan', 1, 18, ' 1s2 ', 24.5874],
                     [3, 6.941, ' Lithium ', ' Li ', 0.53, 'orange', 2, 1, ' [He] 2s1 ', 5.3917],
                     [4, 9.0122, ' Beryllium ', ' Be ', 1.85, 'yellow', 2, 2, ' [He] 2s2 ', 9.3227],
                     [5, 10.811, ' Boron ', ' B ', 2.34, 'green', 2, 13, ' [He] 2s2 2p1 ', 8.298],
                     [6, 12.0107, ' Carbon ', ' C ', 2.26, 'green', 2, 14, ' [He] 2s2 2p2 ', 11.2603],
                     [7, 14.0067, ' Nitrogen ', ' N ', 1.25, 'green', 2, 15, ' [He] 2s2 2p3 ', 14.5341],
                     [8, 15.9994, ' Oxygen ', ' O ', 1.43, 'green', 2, 16, ' [He] 2s2 2p4 ', 13.6181],
                     [9, 18.9984, ' Fluorine ', ' F ', 1.7, 'green', 2, 17, ' [He] 2s2 2p5 ', 17.4228],
                     [10, 20.1797, ' Neon ', ' Ne ', 0.9, 'cyan', 2, 18, ' [He] 2s2 2p6 ', 21.5645],
                     [11, 22.9897, ' Sodium ', ' Na ', 0.97, 'orange', 3, 1, ' [Ne] 3s1 ', 5.1391],
                     [12, 24.305, ' Magnesium ', ' Mg ', 1.74, 'yellow', 3, 2, ' [Ne] 3s2 ', 7.6462],
                     [13, 26.9815, ' Aluminum ', ' Al ', 2.7, 'blue', 3, 13, ' [Ne] 3s2 3p1 ', 5.9858],
                     [14, 28.0855, ' Silicon ', ' Si ', 2.33, 'green', 3, 14, ' [Ne] 3s2 3p2 ', 8.1517],
                     [15, 30.9738, ' Phosphorus ', ' P ', 1.82, 'green', 3, 15, ' [Ne] 3s2 3p3 ', 10.4867],
                     [16, 32.065, ' Sulfur ', ' S ', 2.07, 'green', 3, 16, ' [Ne] 3s2 3p4 ', 10.36],
                     [17, 35.453, ' Chlorine ', ' Cl ', 3.21, 'green', 3, 17, ' [Ne] 3s2 3p5 ', 12.9676],
                     [18, 39.948, ' Argon ', ' Ar ', 1.78, 'cyan', 3, 18, ' [Ne] 3s2 3p6 ', 15.7596],
                     [19, 39.0983, ' Potassium ', ' K ', 0.86, 'orange', 4, 1, ' [Ar] 4s1 ', 4.3407],
                     [20, 40.078, ' Calcium ', ' Ca ', 1.55, 'yellow', 4, 2, ' [Ar] 4s2 ', 6.1132],
                     [21, 44.9559, ' Scandium ', ' Sc ', 2.99, 'pink', 4, 3, ' [Ar] 3d1 4s2 ', 6.5615],
                     [22, 47.867, ' Titanium ', ' Ti ', 4.54, 'pink', 4, 4, ' [Ar] 3d2 4s2 ', 6.8281],
                     [23, 50.9415, ' Vanadium ', ' V ', 6.11, 'pink', 4, 5, ' [Ar] 3d3 4s2 ', 6.7462],
                     [24, 51.9961, ' Chromium ', ' Cr ', 7.19, 'pink', 4, 6, ' [Ar] 3d5 4s1 ', 6.7665],
                     [25, 54.938, ' Manganese ', ' Mn ', 7.43, 'pink', 4, 7, ' [Ar] 3d5 4s2 ', 7.434],
                     [26, 55.845, ' Iron ', ' Fe ', 7.87, 'pink', 4, 8, ' [Ar] 3d6 4s2 ', 7.9024],
                     [27, 58.9332, ' Cobalt ', ' Co ', 8.9, 'pink', 4, 9, ' [Ar] 3d7 4s2 ', 7.881],
                     [28, 58.6934, ' Nickel ', ' Ni ', 8.9, 'pink', 4, 10, ' [Ar] 3d8 4s2 ', 7.6398],
                     [29, 63.546, ' Copper ', ' Cu ', 8.96, 'pink', 4, 11, ' [Ar] 3d10 4s1 ', 7.7264],
                     [30, 65.39, ' Zinc ', ' Zn ', 7.13, 'pink', 4, 12, ' [Ar] 3d10 4s2 ', 9.3942],
                     [31, 69.723, ' Gallium ', ' Ga ', 5.91, 'blue', 4, 13, ' [Ar] 3d10 4s2 4p1 ', 5.9993],
                     [32, 72.64, ' Germanium ', ' Ge ', 5.32, 'blue', 4, 14, ' [Ar] 3d10 4s2 4p2 ', 7.8994],
                     [33, 74.9216, ' Arsenic ', ' As ', 5.72, 'green', 4, 15, ' [Ar] 3d10 4s2 4p3 ', 9.7886],
                     [34, 78.96, ' Selenium ', ' Se ', 4.79, 'green', 4, 16, ' [Ar] 3d10 4s2 4p4 ', 9.7524],
                     [35, 79.904, ' Bromine ', ' Br ', 3.12, 'green', 4, 17, ' [Ar] 3d10 4s2 4p5 ', 11.8138],
                     [36, 83.8, ' Krypton ', ' Kr ', 3.75, 'cyan', 4, 18, ' [Ar] 3d10 4s2 4p6 ', 13.9996],
                     [37, 85.4678, ' Rubidium ', ' Rb ', 1.63, 'orange', 5, 1, ' [Kr] 5s1 ', 4.1771],
                     [38, 87.62, ' Strontium ', ' Sr ', 2.54, 'yellow', 5, 2, ' [Kr] 5s2 ', 5.6949],
                     [39, 88.9059, ' Yttrium ', ' Y ', 4.47, 'pink', 5, 3, ' [Kr] 4d1 5s2 ', 6.2173],
                     [40, 91.224, ' Zirconium ', ' Zr ', 6.51, 'pink', 5, 4, ' [Kr] 4d2 5s2 ', 6.6339],
                     [41, 92.9064, ' Niobium ', ' Nb ', 8.57, 'pink', 5, 5, ' [Kr] 4d4 5s1 ', 6.7589],
                     [42, 95.94, ' Molybdenum ', ' Mo ', 10.22, 'pink', 5, 6, ' [Kr] 4d5 5s1 ', 7.0924],
                     [43, 98, ' Technetium ', ' Tc ', 11.5, 'pink', 5, 7, ' [Kr] 4d5 5s2 ', 7.28],
                     [44, 101.07, ' Ruthenium ', ' Ru ', 12.37, 'pink', 5, 8, ' [Kr] 4d7 5s1 ', 7.3605],
                     [45, 102.9055, ' Rhodium ', ' Rh ', 12.41, 'pink', 5, 9, ' [Kr] 4d8 5s1 ', 7.4589],
                     [46, 106.42, ' Palladium ', ' Pd ', 12.02, 'pink', 5, 10, ' [Kr] 4d10 ', 8.3369],
                     [47, 107.8682, ' Silver ', ' Ag ', 10.5, 'pink', 5, 11, ' [Kr] 4d10 5s1 ', 7.5762],
                     [48, 112.411, ' Cadmium ', ' Cd ', 8.65, 'pink', 5, 12, ' [Kr] 4d10 5s2 ', 8.9938],
                     [49, 114.818, ' Indium ', ' In ', 7.31, 'blue', 5, 13, ' [Kr] 4d10 5s2 5p1 ', 5.7864],
                     [50, 118.71, ' Tin ', ' Sn ', 7.31, 'blue', 5, 14, ' [Kr] 4d10 5s2 5p2 ', 7.3439],
                     [51, 121.76, ' Antimony ', ' Sb ', 6.68, 'blue', 5, 15, ' [Kr] 4d10 5s2 5p3 ', 8.6084],
                     [52, 127.6, ' Tellurium ', ' Te ', 6.24, 'green', 5, 16, ' [Kr] 4d10 5s2 5p4 ', 9.0096],
                     [53, 126.9045, ' Iodine ', ' I ', 4.93, 'green', 5, 17, ' [Kr] 4d10 5s2 5p5 ', 10.4513],
                     [54, 131.293, ' Xenon ', ' Xe ', 5.9, 'cyan', 5, 18, ' [Kr] 4d10 5s2 5p6 ', 12.1298],
                     [55, 132.9055, ' Cesium ', ' Cs ', 1.87, 'orange', 6, 1, ' [Xe] 6s1 ', 3.8939],
                     [56, 137.327, ' Barium ', ' Ba ', 3.59, 'yellow', 6, 2, ' [Xe] 6s2 ', 5.2117],
                     [57, 138.9055, ' Lanthanum ', ' La ', 6.15, 'purple', 9, 3, ' [Xe] 5d1 6s2 ', 5.5769],
                     [58, 140.116, ' Cerium ', ' Ce ', 6.77, 'purple', 9, 4, ' [Xe] 4f1 5d1 6s2 ', 5.5387],
                     [59, 140.9077, ' Praseodymium ', ' Pr ', 6.77, 'purple', 9, 5, ' [Xe] 4f3 6s2 ', 5.473],
                     [60, 144.24, ' Neodymium ', ' Nd ', 7.01, 'purple', 9, 6, ' [Xe] 4f4 6s2 ', 5.525],
                     [61, 145, ' Promethium ', ' Pm ', 7.3, 'purple', 9, 7, ' [Xe] 4f5 6s2 ', 5.582],
                     [62, 150.36, ' Samarium ', ' Sm ', 7.52, 'purple', 9, 8, ' [Xe] 4f6 6s2 ', 5.6437],
                     [63, 151.964, ' Europium ', ' Eu ', 5.24, 'purple', 9, 9, ' [Xe] 4f7 6s2 ', 5.6704],
                     [64, 157.25, ' Gadolinium ', ' Gd ', 7.9, 'purple', 9, 10, ' [Xe] 4f7 5d1 6s2 ', 6.1501],
                     [65, 158.9253, ' Terbium ', ' Tb ', 8.23, 'purple', 9, 11, ' [Xe] 4f9 6s2 ', 5.8638],
                     [66, 162.5, ' Dysprosium ', ' Dy ', 8.55, 'purple', 9, 12, ' [Xe] 4f10 6s2 ', 5.9389],
                     [67, 164.9303, ' Holmium ', ' Ho ', 8.8, 'purple', 9, 13, ' [Xe] 4f11 6s2 ', 6.0215],
                     [68, 167.259, ' Erbium ', ' Er ', 9.07, 'purple', 9, 14, ' [Xe] 4f12 6s2 ', 6.1077],
                     [69, 168.9342, ' Thulium ', ' Tm ', 9.32, 'purple', 9, 15, ' [Xe] 4f13 6s2 ', 6.1843],
                     [70, 173.04, ' Ytterbium ', ' Yb ', 6.9, 'purple', 9, 16, ' [Xe] 4f14 6s2 ', 6.2542],
                     [71, 174.967, ' Lutetium ', ' Lu ', 9.84, 'purple', 9, 17, ' [Xe] 4f14 5d1 6s2 ', 5.4259],
                     [72, 178.49, ' Hafnium ', ' Hf ', 13.31, 'pink', 6, 4, ' [Xe] 4f14 5d2 6s2 ', 6.8251],
                     [73, 180.9479, ' Tantalum ', ' Ta ', 16.65, 'pink', 6, 5, ' [Xe] 4f14 5d3 6s2 ', 7.5496],
                     [74, 183.84, ' Tungsten ', ' W ', 19.35, 'pink', 6, 6, ' [Xe] 4f14 5d4 6s2 ', 7.864],
                     [75, 186.207, ' Rhenium ', ' Re ', 21.04, 'pink', 6, 7, ' [Xe] 4f14 5d5 6s2 ', 7.8335],
                     [76, 190.23, ' Osmium ', ' Os ', 22.6, 'pink', 6, 8, ' [Xe] 4f14 5d6 6s2 ', 8.4382],
                     [77, 192.217, ' Iridium ', ' Ir ', 22.4, 'pink', 6, 9, ' [Xe] 4f14 5d7 6s2 ', 8.967],
                     [78, 195.078, ' Platinum ', ' Pt ', 21.45, 'pink', 6, 10, ' [Xe] 4f14 5d9 6s1 ', 8.9587],
                     [79, 196.9665, ' Gold ', ' Au ', 19.32, 'pink', 6, 11, ' [Xe] 4f14 5d10 6s1 ', 9.2255],
                     [80, 200.59, ' Mercury ', ' Hg ', 13.55, 'pink', 6, 12, ' [Xe] 4f14 5d10 6s2 ', 10.4375],
                     [81, 204.3833, ' Thallium ', ' Tl ', 11.85, 'blue', 6, 13, ' [Xe] 4f14 5d10 6s2 6p1 ', 6.1082],
                     [82, 207.2, ' Lead ', ' Pb ', 11.35, 'blue', 6, 14, ' [Xe] 4f14 5d10 6s2 6p2 ', 7.4167],
                     [83, 208.9804, ' Bismuth ', ' Bi ', 9.75, 'blue', 6, 15, ' [Xe] 4f14 5d10 6s2 6p3 ', 7.2856],
                     [84, 209, ' Polonium ', ' Po ', 9.3, 'blue', 6, 16, ' [Xe] 4f14 5d10 6s2 6p4 ', 8.417],
                     [85, 210, ' Astatine ', ' At ', 6.2, 'green', 6, 17, ' [Xe] 4f14 5d10 6s2 6p5 ', 9.3],
                     [86, 222, ' Radon ', ' Rn ', 9.73, 'cyan', 6, 18, ' [Xe] 4f14 5d10 6s2 6p6 ', 10.7485],
                     [87, 223, ' Francium ', ' Fr ', 1.87, 'orange', 7, 1, ' [Rn] 7s1 ', 4.0727],
                     [88, 226, ' Radium ', ' Ra ', 5.5, 'yellow', 7, 2, ' [Rn] 7s2 ', 5.2784],
                     [89, 227, ' Actinium ', ' Ac ', 10.07, 'purple', 10, 3, ' [Rn] 6d1 7s2 ', 5.17],
                     [90, 232.0381, ' Thorium ', ' Th ', 11.72, 'purple', 10, 4, ' [Rn] 6d2 7s2 ', 6.3067],
                     [91, 231.0359, ' Protactinium ', ' Pa ', 15.4, 'purple', 10, 5, ' [Rn] 5f2 6d1 7s2 ', 5.89],
                     [92, 238.0289, ' Uranium ', ' U ', 18.95, 'purple', 10, 6, ' [Rn] 5f3 6d1 7s2 ', 6.1941],
                     [93, 237, ' Neptunium ', ' Np ', 20.2, 'purple', 10, 7, ' [Rn] 5f4 6d1 7s2 ', 6.2657],
                     [94, 244, ' Plutonium ', ' Pu ', 19.84, 'purple', 10, 8, ' [Rn] 5f6 7s2 ', 6.0262],
                     [95, 243, ' Americium ', ' Am ', 13.67, 'purple', 10, 9, ' [Rn] 5f7 7s2 ', 5.9738],
                     [96, 247, ' Curium ', ' Cm ', 13.5, 'purple', 10, 10, ' ', 5.9915],
                     [97, 247, ' Berkelium ', ' Bk ', 14.78, 'purple', 10, 11, ' ', 6.1979],
                     [98, 251, ' Californium ', ' Cf ', 15.1, 'purple', 10, 12, ' ', 6.2817],
                     [99, 252, ' Einsteinium ', ' Es ', 8.84, 'purple', 10, 13, ' ', 6.42],
                     [100, 257, ' Fermium ', ' Fm ', '?', 'purple', 10, 14, ' ', 6.5],
                     [101, 258, ' Mendelevium ', ' Md ', '?', 'purple', 10, 15, ' ', 6.58],
                     [102, 259, ' Nobelium ', ' No ', '?', 'purple', 10, 16, ' ', 6.65],
                     [103, 262, ' Lawrencium ', ' Lr ', '?', 'purple', 10, 17, ' ', 4.9],
                     [104, 261, ' Rutherfordium ', ' Rf ', '?', 'pink', 7, 4, ' ', '?'],
                     [105, 262, ' Dubnium ', ' Db ', '?', 'pink', 7, 5, ' ', '?'],
                     [106, 266, ' Seaborgium ', ' Sg ', '?', 'pink', 7, 6, ' ', '?'],
                     [107, 264, ' Bohrium ', ' Bh ', '?', 'pink', 7, 7, ' ', '?'],
                     [108, 277, ' Hassium ', ' Hs ', '?', 'pink', 7, 8, ' ', '?'],
                     [109, 268, ' Meitnerium ', ' Mt ', '?', 'pink', 7, 9, ' ', '?'],
                     [110, 277, ' Darmstadtium ', ' Ds ', '?', 'pink', 7, 10, ' ', '?'],
                     [111, 277, ' Roentgenium ', ' Rg ', '?', 'pink', 7, 11, ' ', '?'],
                     [112, 277, ' Copernicium ', ' Cn ', '?', 'pink', 7, 12, ' ', '?'],
                     [113, 277, ' Ununtrium ', ' Uut ', '?', 'grey', 7, 13, ' ', '?'],
                     [114, 277, ' Flerovium ', ' Fl ', '?', 'grey', 7, 14, ' ', '?'],
                     [115, 277, ' Ununpentium ', ' Uup ', '?', 'grey', 7, 15, ' ', '?'],
                     [116, 277, ' Livermorium ', ' Lv ', '?', 'grey', 7, 16, ' ', '?'],
                     [117, 277, ' Ununseptium ', ' Uus ', '?', 'grey', 7, 17, ' ', '?'],
                     [118, 277, ' Ununoctium ', ' Uuo ', '?', 'grey', 7, 18, ' ', '?'], ]

        # create all buttons with a loop
        for i, element in enumerate(per_table):
            #        print(element[1])
            tk.Button(self, text=element[3], width=5, height=2, bg=element[5],
                      command=lambda i=i: quit_window(i + 1)).grid(row=element[6], column=element[7])

        for child in self.winfo_children(): child.grid_configure(padx=3, pady=3)

        self.mainloop()


def main():
    a = App()


if __name__ == "__main__":
    main()
