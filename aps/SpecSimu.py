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
from datetime import datetime

#Data Imports for variable management
from data.variables import labeldict, the_dictionary, the_aug_dictionary
import data.variables

#File IO Imports
from utils.fileIO import file_namer, write_to_xls

#Math Function Imports for calculating line profiles
from utils.functions import G, L, V

#GUI utils: destroy window
from utils.interface import destroy


def simulateSpectra(dir_path, element, parent):    
    radiative_files = []
    auger_files = []
    
    # Obtenho o a data e hora exacta para dar nome aos ficheiros a gravar
    time_of_click = datetime.now()
    
    # Em versões anteriores recebiamos apenas o z do elemento, mas para poder ter acesso ao nome, recebe-se um vetor com nome e numero
    z = element[0]
    element_name = element[1]
    
    # Caminho do ficheiro na pasta com o nome igual ao numero atomico que tem as intensidades
    radrates_file = dir_path / str(z) / (str(z) + '-intensity.out')
    try:
        with open(radrates_file, 'r') as radrates:  # Abrir o ficheiro
            # Escrever todas as linhas no ficheiro como uma lista
            lineradrates = [x.strip('\n').split()
                            for x in radrates.readlines()]
            # Remover as linhas compostas apenas por celulas vazias
            lineradrates = list(filter(None, lineradrates))
            del lineradrates[0:2]
    except FileNotFoundError:
        messagebox.showwarning("Error", "Diagram File is not Avaliable")

    # Caminho do ficheiro na pasta com o nome igual ao numero atomico que tem as satelites
    satellites_file = dir_path / str(z) / (str(z) + '-satinty.out')
    try:
        with open(satellites_file, 'r') as satellites:  # Abrir o ficheiro
            # Escrever todas as linhas no ficheiro como uma lista
            linesatellites = [x.strip('\n').split()
                              for x in satellites.readlines()]
            # Remover as linhas compostas apenas por celulas vazias
            linesatellites = list(filter(None, linesatellites))
            # Tira as linhas que têm o nome das variáveis e etc
            del linesatellites[0:2]
    except FileNotFoundError:
        messagebox.showwarning("Error", "Satellites File is not Avaliable")

    # Caminho do ficheiro na pasta com o nome igual ao numero atomico que tem as satelites
    augrates_file = dir_path / str(z) / (str(z) + '-augrate.out')
    try:
        with open(augrates_file, 'r') as augrates:  # Abrir o ficheiro
            # Escrever todas as linhas no ficheiro como uma lista
            lineauger = [x.strip('\n').split()
                         for x in augrates.readlines()]
            # Remover as linhas compostas apenas por celulas vazias
            lineauger = list(filter(None, lineauger))
            # Tira as linhas que têm o nome das variáveis e etc
            del lineauger[0:2]
    except FileNotFoundError:
        messagebox.showwarning(
            "Error", "Auger Rates File is not Avaliable")

    # Caminho do ficheiro na pasta com o nome igual ao numero atomico que tem as satelites
    shakeweights_file = dir_path / str(z) / (str(z) + '-shakeweights.out')
    try:
        with open(shakeweights_file, 'r') as shakeweights_f:  # Abrir o ficheiro
            # Escrever todas as linhas no ficheiro como uma lista
            shakeweights_m = [x.strip('\n').split(',')
                              for x in shakeweights_f.readlines()]
            shakeweights = []
            label1 = []
            for i, j in enumerate(shakeweights_m):
                # Neste for corremos as linhas todas guardadas em shakeweights_m e metemos os valores numéricos no shakeweights
                shakeweights.append(float(shakeweights_m[i][1]))
            for k, l in enumerate(shakeweights_m):
                # Neste for corremos as linhas todas guardadas em shakeweights_m e metemos os rotulos no label 1
                label1.append(shakeweights_m[k][0])
    except FileNotFoundError:
        messagebox.showwarning(
            "Error", "Shake Weigth File is not Avaliable")

    # Flag para ativar ou desativar a opção no menu (algures nas linhas ~1500)
    CS_exists = False
    Ionpop_exists = False
    # Verificar se existe a pasta com os varios CS para o atomo escolhido
    if os.path.isdir(dir_path / str(z) / 'Charge_States'):
        CS_exists = True
        radiative_files = [f for f in os.listdir(dir_path / str(z) / 'Charge_States') if os.path.isfile(
            os.path.join(dir_path / str(z) / 'Charge_States', f)) and '-intensity_' in f]

        lineradrates_PCS = []
        lineradrates_NCS = []

        rad_PCS = []
        rad_NCS = []

        for radfile in radiative_files:
            # Caminho do ficheiro na pasta com o nome igual ao numero atomico que tem as intensidades
            rad_tmp_file = dir_path / str(z) / 'Charge_States' / radfile
            try:
                with open(rad_tmp_file, 'r') as radrates:  # Abrir o ficheiro
                    if '+' in radfile:
                        # Escrever todas as linhas no ficheiro como uma lista
                        lineradrates_PCS.append(
                            [x.strip('\n').split() for x in radrates.readlines()])
                        # Remover as linhas compostas apenas por celulas vazias
                        lineradrates_PCS[-1] = list(
                            filter(None, lineradrates_PCS[-1]))
                        del lineradrates_PCS[-1][0:2]
                        rad_PCS.append(
                            '+' + radfile.split('+')[1].split('.')[0])
                    else:
                        # Escrever todas as linhas no ficheiro como uma lista
                        lineradrates_NCS.append(
                            [x.strip('\n').split() for x in radrates.readlines()])
                        # Remover as linhas compostas apenas por celulas vazias
                        lineradrates_NCS[-1] = list(
                            filter(None, lineradrates_NCS[-1]))
                        del lineradrates_NCS[-1][0:2]
                        rad_NCS.append(
                            '-' + radfile.split('-')[1].split('.')[0])
            except FileNotFoundError:
                messagebox.showwarning(
                    "Error", "Charge State File is not Avaliable: " + radfile)

        auger_files = [f for f in os.listdir(dir_path / str(z) / 'Charge_States') if os.path.isfile(
            os.path.join(dir_path / str(z) / 'Charge_States', f)) and '-augrate_' in f]

        lineaugrates_PCS = []
        lineaugrates_NCS = []

        aug_PCS = []
        aug_NCS = []

        for augfile in auger_files:
            # Caminho do ficheiro na pasta com o nome igual ao numero atomico que tem as intensidades
            aug_tmp_file = dir_path / str(z) / 'Charge_States' / augfile
            try:
                with open(aug_tmp_file, 'r') as augrates:  # Abrir o ficheiro
                    if '+' in augfile:
                        # Escrever todas as linhas no ficheiro como uma lista
                        lineaugrates_PCS.append(
                            [x.strip('\n').split() for x in augrates.readlines()])
                        # Remover as linhas compostas apenas por celulas vazias
                        lineaugrates_PCS[-1] = list(
                            filter(None, lineaugrates_PCS[-1]))
                        del lineaugrates_PCS[-1][0:2]
                        aug_PCS.append(
                            '+' + radfile.split('+')[1].split('.')[0])
                    else:
                        # Escrever todas as linhas no ficheiro como uma lista
                        lineaugrates_NCS.append(
                            [x.strip('\n').split() for x in augrates.readlines()])
                        # Remover as linhas compostas apenas por celulas vazias
                        lineaugrates_NCS[-1] = list(
                            filter(None, lineaugrates_NCS[-1]))
                        del lineaugrates_NCS[-1][0:2]
                        aug_NCS.append(
                            '-' + radfile.split('-')[1].split('.')[0])
            except FileNotFoundError:
                messagebox.showwarning(
                    "Error", "Charge State File is not Avaliable: " + augfile)

        sat_files = [f for f in os.listdir(dir_path / str(z) / 'Charge_States') if os.path.isfile(
            os.path.join(dir_path / str(z) / 'Charge_States', f)) and '-satinty_' in f]

        linesatellites_PCS = []
        linesatellites_NCS = []

        sat_PCS = []
        sat_NCS = []

        for satfile in sat_files:
            # Caminho do ficheiro na pasta com o nome igual ao numero atomico que tem as intensidades
            sat_tmp_file = dir_path / str(z) / 'Charge_States' / satfile
            try:
                with open(sat_tmp_file, 'r') as satrates:  # Abrir o ficheiro
                    if '+' in satfile:
                        # Escrever todas as linhas no ficheiro como uma lista
                        linesatellites_PCS.append(
                            [x.strip('\n').split() for x in satrates.readlines()])
                        # Remover as linhas compostas apenas por celulas vazias
                        linesatellites_PCS[-1] = list(
                            filter(None, linesatellites_PCS[-1]))
                        del linesatellites_PCS[-1][0:2]
                        sat_PCS.append(
                            '+' + satfile.split('+')[1].split('.')[0])
                    else:
                        # Escrever todas as linhas no ficheiro como uma lista
                        linesatellites_NCS.append(
                            [x.strip('\n').split() for x in satrates.readlines()])
                        # Remover as linhas compostas apenas por celulas vazias
                        linesatellites_NCS[-1] = list(
                            filter(None, linesatellites_NCS[-1]))
                        del linesatellites_NCS[-1][0:2]
                        sat_NCS.append(
                            '-' + satfile.split('-')[1].split('.')[0])
            except FileNotFoundError:
                messagebox.showwarning(
                    "Error", "Charge State File is not Avaliable: " + satfile)

        if len(linesatellites_NCS) != len(lineradrates_NCS) or len(linesatellites_PCS) != len(lineradrates_PCS):
            messagebox.showwarning("Error", "Missmatch of radiative and satellite files for Charge State mixture: " + str(len(lineradrates_NCS) + len(
                lineradrates_PCS)) + " radiative and " + str(len(linesatellites_NCS) + len(linesatellites_PCS)) + " satellite files found.")

        # Caminho do ficheiro na pasta com o nome igual ao numero atomico que tem as satelites
        ionpop_file = dir_path / str(z) / (str(z) + '-ionpop.out')
        try:
            with open(ionpop_file, 'r') as ionpop:  # Abrir o ficheiro
                # Escrever todas as linhas no ficheiro como uma lista
                ionpopdata = [x.strip('\n').split()
                              for x in ionpop.readlines()]
                # Remover as linhas compostas apenas por celulas vazias
                ionpopdata = list(filter(None, ionpopdata))
            Ionpop_exists = True
        except FileNotFoundError:
            messagebox.showwarning(
                "Error", "Ion Population File is not Avaliable")

    # ---------------------------------------------------------------------------------------------------------------
    # Criamos uma nova janela onde aparecerão os gráficos todos (TopLevel porque não podem haver duas janelas tk abertas ao mesmo tempo)
    # E definimos o seu titulo
    sim = Toplevel(master=parent)
    sim.title("Spectrum Simulation")
    # Criamos um "panel" onde vamos colocar o canvas para fazer o plot do gráfico. Panels são necessários para a janela poder mudar de tamanho
    panel_1 = PanedWindow(sim, orient=VERTICAL)
    panel_1.pack(fill=BOTH, expand=1)
    # ---------------------------------------------------------------------------------------------------------------
    # Figura onde o gráfico vai ser desenhado
    # canvas para o gráfico do espectro
    f = Figure(figsize=(10, 5), dpi=100)
    # plt.style.use('ggplot') Estilo para os plots
    a = f.add_subplot(111)  # zona onde estara o gráfico
    a.set_xlabel('Energy (eV)')
    a.set_ylabel('Intensity (arb. units)')
    # ---------------------------------------------------------------------------------------------------------------
    # Frames onde se vão por a figura e os labels e botões e etc
    figure_frame = Frame(panel_1, relief=GROOVE)  # frame para o gráfico
    panel_1.add(figure_frame)
    canvas = FigureCanvasTkAgg(f, master=figure_frame)
    canvas.get_tk_widget().pack(fill=BOTH, expand=1)

    panel_2 = PanedWindow(sim, orient=VERTICAL)
    panel_2.pack(fill=X, expand=0)

    toolbar_frame = Frame(panel_2, bd=1, relief=GROOVE)
    panel_2.add(toolbar_frame)
    toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)

    full_frame = Frame(panel_2, relief=GROOVE)  # Frame transições
    panel_2.add(full_frame)
    buttons_frame = Frame(
        full_frame, bd=1, relief=GROOVE)  # Frame transições
    buttons_frame.pack(fill=BOTH, expand=1)
    # Max, min & Points Frame
    buttons_frame2 = Frame(full_frame, bd=1, relief=GROOVE)
    buttons_frame2.pack(fill=BOTH, expand=1)
    # Frame  yoffset, Energy offset e Calculate
    buttons_frame3 = Frame(full_frame, bd=1, relief=GROOVE)
    buttons_frame3.pack(fill=BOTH, expand=1)
    buttons_frame4 = Frame(full_frame)  # Frame Barra Progresso
    buttons_frame4.pack(fill=BOTH, expand=1)

    # ---------------------------------------------------------------------------------------------------------------
    # Variáveis
    # Variável que define se apresentamos o ytot(soma de todas as riscas) no gráfico
    totalvar = StringVar()
    # inicializamos Total como não, porque só se apresenta se o utilizador escolher manualmente
    totalvar.set('No')
    # Variável que define se o eixo y é apresentado com escala logaritmica ou não
    yscale_log = StringVar()
    # Inicializamos a No porque só  se apresenta assim se o utilizador escolher manualmente
    yscale_log.set('No')
    # Variável que define se o eixo y é apresentado com escala logaritmica ou não
    xscale_log = StringVar()
    # Inicializamos a No porque só  se apresenta assim se o utilizador escolher manualmente
    xscale_log.set('No')
    autofitvar = StringVar()  # Variável que define se o fit se faz automáticamente ou não
    # Inicializamos a No porque só faz fit automático se o utilizador quiser
    autofitvar.set('No')
    normalizevar = StringVar()  # Variável que define como se normalizam os gráficos (3 opções até agora: não normalizar, normalizar à unidade, ou ao máximo do espectro experimental)
    # inicializamos Normalize a no, porque só se normaliza se o utilizador escolher
    normalizevar.set('No')
    loadvar = StringVar()  # Variável que define se se carrega um expectro experimental. A string, caso se queira carregar o espectro, muda para o path do ficheiro do espectro
    # inicializamos Load a no, porque só se carrega ficheiro se o utilizador escolher
    loadvar.set('No')
    effic_var = StringVar()
    effic_var.set("No")

    # Float correspondente a resolucao experimental
    exp_resolution = DoubleVar(value=1.0)
    # Float correspondente ao fundo experimental
    yoffset = DoubleVar(value=0.0)
    # Float correspondente a resolucao experimental
    energy_offset = DoubleVar(value=0.0)
    # Numero de pontos a plotar na simulação
    number_points = IntVar(value=500)
    x_max = StringVar()  # Controlo do x Máximo a entrar no gráfico
    x_max.set('Auto')
    x_min = StringVar()  # Controlo do x Mí­nimo a entrar no gráfico
    x_min.set('Auto')
    progress_var = DoubleVar()  # Float que da a percentagem de progresso

    global transition_list  # Usada na função Selected
    transition_list = []
    label_text = StringVar()  # Texto com as transições selecionadas a apresentar no ecrã
    # Antes de se selecionar alguma transição aparece isto
    label_text.set('Select a Transition: ')
    trans_lable = Label(
        buttons_frame, textvariable=label_text).grid(row=0, column=1)

    # ---------------------------------------------------------------------------------------------------------------
    # Função para alterar o estado de uma transição que seja selecionada na GUI
    def dict_updater(transition):
        if satelite_var.get() != 'Auger':
            # O "Estado actual" que as riscas têm quando esta função corre é o oposto daquele que está definido no dicionário, porque a função só corre se clicarmos para mudar
            current_state = not the_dictionary[transition]["selected_state"]
            # Alteramos o estado das riscas para o estado actual
            the_dictionary[transition]["selected_state"] = current_state
        else:
            # O "Estado actual" que as riscas têm quando esta função corre é o oposto daquele que está definido no dicionário, porque a função só corre se clicarmos para mudar
            current_state = not the_aug_dictionary[transition]["selected_state"]
            # Alteramos o estado das riscas para o estado actual
            the_aug_dictionary[transition]["selected_state"] = current_state

    # ---------------------------------------------------------------------------------------------------------------
    # Funções
    def detector_efficiency(energy_values, efficiency_values, xfinal, enoffset):
        interpolated_effic = [0 for i in range(len(xfinal))]
        effic_interpolation = interp1d(
            energy_values, np.array(efficiency_values)/100)
        for i, energy in enumerate(xfinal+enoffset):
            interpolated_effic[i] = effic_interpolation(energy)
            print(interpolated_effic[i], energy)
        return interpolated_effic

    def normalizer(y0, expy_max, ytot_max):
        normalize = normalizevar.get()
        try:
            if normalize == 'ExpMax':
                normalization_var = (
                    1 - y0 / expy_max) * expy_max / ytot_max
            elif normalize == 'One':
                normalization_var = (1 - y0) / ytot_max
            elif normalize == 'No':
                normalization_var = 1

        except ValueError:
            messagebox.showerror(
                "No Spectrum", "No Experimental Spectrum was loaded")
        except ZeroDivisionError:
            normalization_var = 1
        return normalization_var

    def y_calculator(transition_type, fit_type, xfinal, x, y, w, xs, ys, ws, res, energy_values, efficiency_values, enoffset):
        # Criar uma lista de listas cheia de zeros que ira ser o yfinal para diagrama
        data.variables.yfinal = [[0 for i in range(len(xfinal))] for j in range(len(x))]
        data.variables.ytot = [0 for i in range(len(xfinal))]
        # Criar uma lista de listas cheia de zeros que ira ser o yfinal para satellites
        data.variables.yfinals = [[[0 for n in range(len(xfinal))]
                    for i in label1] for j in range(len(xs))]
        if transition_type == 'Diagram':
            b1 = 0
            for j, k in enumerate(y):
                # Ciclo sobre todas as riscas para somar um pico (voigt, lorentz ou gauss) para cada individual
                for i, n in enumerate(k):
                    if fit_type == 'Voigt':
                        data.variables.yfinal[j] = np.add(data.variables.yfinal[j], V(
                            xfinal, x[j][i], y[j][i], res, w[j][i]))
                    elif fit_type == 'Lorentzian':
                        data.variables.yfinal[j] = np.add(data.variables.yfinal[j], L(
                            xfinal, x[j][i], y[j][i], res, w[j][i]))
                    elif fit_type == 'Gaussian':
                        data.variables.yfinal[j] = np.add(data.variables.yfinal[j], G(
                            xfinal, x[j][i], y[j][i], res, w[j][i]))
                    b1 += 100 / (len(y) * len(k))
                    progress_var.set(b1)
                    sim.update_idletasks()
                if k != []:  # Excluir as linhas que nao foram seleccionados nos botoes
                    data.variables.ytot = np.add(data.variables.ytot, data.variables.yfinal[j])

            b1 = 100
            progress_var.set(b1)
            sim.update_idletasks()
        elif transition_type == 'Satellites':
            b1 = 0
            for j, k in enumerate(ys):
                for l, m in enumerate(ys[j]):
                    # Ciclo sobre todas as riscas para somar um pico (voigt, lorentz ou gauss) para cada individual
                    for i, n in enumerate(m):
                        if fit_type == 'Voigt':
                            data.variables.yfinals[j][l] = np.add(data.variables.yfinals[j][l], V(
                                xfinal, xs[j][l][i], ys[j][l][i], res, ws[j][l][i]))
                        elif fit_type == 'Lorentzian':
                            data.variables.yfinals[j][l] = np.add(data.variables.yfinals[j][l], L(
                                xfinal, xs[j][l][i], ys[j][l][i], res, ws[j][l][i]))
                        elif fit_type == 'Gaussian':
                            data.variables.yfinals[j][l] = np.add(data.variables.yfinals[j][l], G(
                                xfinal, xs[j][l][i], ys[j][l][i], res, ws[j][l][i]))
                        b1 += 100 / (len(ys) * len(label1) * len(m))
                        progress_var.set(b1)
                        sim.update_idletasks()
                    if m != []:  # Excluir as linhas que nao foram seleccionados nos botoes
                        data.variables.ytot = np.add(data.variables.ytot, data.variables.yfinals[j][l])
            b1 = 100
            progress_var.set(b1)
            sim.update_idletasks()
        elif transition_type == 'Diagram + Satellites':
            b1 = 0
            for j, k in enumerate(y):
                # Ciclo sobre todas as riscas para somar um pico (voigt, lorentz ou gauss) para cada individual
                for i, n in enumerate(k):
                    if fit_type == 'Voigt':
                        data.variables.yfinal[j] = np.abs(
                            np.add(data.variables.yfinal[j], V(xfinal, x[j][i], y[j][i], res, w[j][i])))
                    elif fit_type == 'Lorentzian':
                        data.variables.yfinal[j] = np.abs(
                            np.add(data.variables.yfinal[j], L(xfinal, x[j][i], y[j][i], res, w[j][i])))
                    elif fit_type == 'Gaussian':
                        data.variables.yfinal[j] = np.abs(
                            np.add(data.variables.yfinal[j], G(xfinal, x[j][i], y[j][i], res, w[j][i])))
                    b1 += 200 / (len(y) * len(k))
                    progress_var.set(b1)
                    sim.update_idletasks()
                if k != []:  # Excluir as linhas que nao foram seleccionados nos botoes
                    data.variables.ytot = np.add(data.variables.ytot, data.variables.yfinal[j])

            b1 = 50
            progress_var.set(b1)
            sim.update_idletasks()
            for j, k in enumerate(ys):
                for l, m in enumerate(ys[j]):
                    # Ciclo sobre todas as riscas para somar um pico (voigt, lorentz ou gauss) para cada individual
                    for i, n in enumerate(m):
                        if fit_type == 'Voigt':
                            data.variables.yfinals[j][l] = np.abs(np.add(data.variables.yfinals[j][l], V(
                                xfinal, xs[j][l][i], ys[j][l][i], res, ws[j][l][i])))
                        elif fit_type == 'Lorentzian':
                            data.variables.yfinals[j][l] = np.abs(np.add(data.variables.yfinals[j][l], L(
                                xfinal, xs[j][l][i], ys[j][l][i], res, ws[j][l][i])))
                        elif fit_type == 'Gaussian':
                            data.variables.yfinals[j][l] = np.abs(np.add(data.variables.yfinals[j][l], G(
                                xfinal, xs[j][l][i], ys[j][l][i], res, ws[j][l][i])))
                        b1 += 100 / (len(ys) * len(label1) * len(m))
                        progress_var.set(b1)
                        sim.update_idletasks()
                    if m != []:  # Excluir as linhas que nao foram seleccionados nos botoes
                        data.variables.ytot = np.add(data.variables.ytot, data.variables.yfinals[j][l])
            b1 = 100
            progress_var.set(b1)
            sim.update_idletasks()
        elif transition_type == 'Auger':
            # Criar uma lista de listas cheia de zeros que ira ser o yfinal para diagrama
            data.variables.yfinal = [[0 for i in range(len(xfinal))]
                      for j in range(len(x))]
            data.variables.ytot = [0 for i in range(len(xfinal))]
            # Criar uma lista de listas cheia de zeros que ira ser o yfinal para satellites
            data.variables.yfinals = [[[0 for n in range(len(xfinal))]
                        for i in label1] for j in range(len(xs))]

            b1 = 0
            for j, k in enumerate(y):
                # Ciclo sobre todas as riscas para somar um pico (voigt, lorentz ou gauss) para cada individual
                for i, n in enumerate(k):
                    if fit_type == 'Voigt':
                        data.variables.yfinal[j] = np.add(data.variables.yfinal[j], V(
                            xfinal, x[j][i], y[j][i], res, w[j][i]))
                    elif fit_type == 'Lorentzian':
                        data.variables.yfinal[j] = np.add(data.variables.yfinal[j], L(
                            xfinal, x[j][i], y[j][i], res, w[j][i]))
                    elif fit_type == 'Gaussian':
                        data.variables.yfinal[j] = np.add(data.variables.yfinal[j], G(
                            xfinal, x[j][i], y[j][i], res, w[j][i]))
                    b1 += 100 / (len(y) * len(k))
                    progress_var.set(b1)
                    sim.update_idletasks()
                if k != []:  # Excluir as linhas que nao foram seleccionados nos botoes
                    data.variables.ytot = np.add(data.variables.ytot, data.variables.yfinal[j])

            b1 = 100
            progress_var.set(b1)
            sim.update_idletasks()

        if effic_var.get() != 'No':
            detector_effi = detector_efficiency(
                energy_values, efficiency_values, xfinal, enoffset)
            return data.variables.ytot*np.array(detector_effi), data.variables.yfinal*np.array(detector_effi), data.variables.yfinals*np.array(detector_effi)
        else:
            return data.variables.ytot, data.variables.yfinal, data.variables.yfinals

    def func2min(params, exp_x, exp_y, num_of_points, sat, peak, x, y, w, xs, ys, ws, energy_values, efficiency_values, enoffset):
        global xfinal
        
        normalize = normalizevar.get()
        y_interp = [0 for i in range(len(exp_x))]
        xoff = params['xoff']
        y0 = params['yoff']
        res = params['res']
        ytot_max = params['ytot_max']
        xfinal = np.array(np.linspace(min(exp_x) - xoff,
                          max(exp_x) - xoff, num=num_of_points))
        data.variables.ytot, data.variables.yfinal, data.variables.yfinals = y_calculator(
            sat, peak, xfinal, x, y, w, xs, ys, ws, res, energy_values, efficiency_values, enoffset)
        normalization_var = normalizer(y0, max(exp_y), ytot_max)
        # print(xoff, res, y0, normalization_var)
        # print(xoff, res, y0, ytot_max)
        f_interpolate = interp1d(
            xfinal + xoff, np.array(data.variables.ytot * normalization_var) + y0, kind='cubic')  # Falta adicionar o y0
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
            y = [float(row[11]) * (1 - 0.01 * sum(shakeweights))
                 for row in transition_values]  # *float(row[11])*float(row[9])
            y.insert(0, 0)
            y.append(0)
            a.stem(x, y, markerfmt=' ', linefmt=str(col2[np.random.randint(
                0, 7)][0]), label=str(transition), use_line_collection=True)
            a.legend(loc='best', numpoints=1)
        elif spec_type == 'Satellites':
            sy_points = [float(float(row[11]) * 0.01 * shakeweights[ind])
                         for row in transition_values]  # *float(row[11])*float(row[9])
            sy_points.insert(0, 0)
            sy_points.append(0)
            a.stem(x, sy_points, markerfmt=' ', linefmt=str(col2[np.random.randint(
                0, 7)][0]), label=transition + ' - ' + labeldict[key], use_line_collection=True)  # Plot a stemplot
            a.legend(loc='best', numpoints=1)
        elif spec_type == 'Auger':
            y = [float(row[11]) * (1 - 0.01 * sum(shakeweights))
                 for row in transition_values]  # *float(row[11])*float(row[9])
            y.insert(0, 0)
            y.append(0)
            a.stem(x, y, markerfmt=' ', linefmt=str(col2[np.random.randint(
                0, 7)][0]), label=str(transition), use_line_collection=True)
            a.legend(loc='best', numpoints=1)
        elif spec_type == 'Diagram_CS':
            y = [float(row[11]) * (1 - 0.01 * sum(shakeweights)) * float(row[-1])
                 for row in transition_values]  # *float(row[11])*float(row[9])
            y.insert(0, 0)
            y.append(0)
            a.stem(x, y, markerfmt=' ', linefmt=str(col2[np.random.randint(
                0, 7)][0]), label=str(transition), use_line_collection=True)
            a.legend(loc='best', numpoints=1)
        elif spec_type == 'Satellites_CS':
            sy_points = [float(float(row[11]) * 0.01 * shakeweights[ind] * float(row[-1]))
                         for row in transition_values]  # *float(row[11])*float(row[9])
            sy_points.insert(0, 0)
            sy_points.append(0)
            a.stem(x, sy_points, markerfmt=' ', linefmt=str(col2[np.random.randint(
                0, 7)][0]), label=transition + ' - ' + labeldict[key], use_line_collection=True)  # Plot a stemplot
            a.legend(loc='best', numpoints=1)
        elif spec_type == 'Auger_CS':
            y = [float(row[11]) * (1 - 0.01 * sum(shakeweights)) * float(row[-1])
                 for row in transition_values]  # *float(row[11])*float(row[9])
            y.insert(0, 0)
            y.append(0)
            a.stem(x, y, markerfmt=' ', linefmt=str(col2[np.random.randint(
                0, 7)][0]), label=str(transition), use_line_collection=True)
            a.legend(loc='best', numpoints=1)
        a.legend(title=element_name, title_fontsize='large')
        # --------------------------------------------------------------------------------------------------------------------------
        # Tratamento da Legenda
        a.legend(title=element_name)
        # Descubro quantas entradas vai ter a legenda
        number_of_labels = len(a.legend().get_texts())
        # Inicialmente há uma coluna, mas vou fazer contas para ter 10 itens por coluna no máximo
        legend_columns = 1
        labels_per_columns = number_of_labels / \
            legend_columns  # Numero de entradas por coluna
        while labels_per_columns > 10:  # Se a priori for menos de 10 entradas por coluna, não acontece nada
            legend_columns += 1  # Se houver mais que 10 entradas por coluna, meto mais uma coluna
            # Recalculo o numero de entradas por coluna
            labels_per_columns = number_of_labels / legend_columns
        # Defino o numero de colunas na legenda = numero de colunas necessárias para não ter mais de 10 entradas por coluna
        a.legend(ncol=legend_columns)

    def plot_stick(graph_area):
        global xfinal, exp_x, exp_y, residues_graph
        residues_graph = None
        exp_x = None
        exp_y = None
        graph_area.clear()
        if yscale_log.get() == 'Ylog':
            graph_area.set_yscale('log')
        if xscale_log.get() == 'Xlog':
            graph_area.set_xscale('log')
        graph_area.legend(title=element_name)
        autofit = autofitvar.get()
        total = totalvar.get()
        normalize = normalizevar.get()
        y0 = yoffset.get()
        enoffset = energy_offset.get()
        res = exp_resolution.get()
        spectype = choice_var.get()
        peak = type_var.get()
        load = loadvar.get()
        effic_file_name = effic_var.get()
        sat = satelite_var.get()
        num_of_points = number_points.get()
        x_mx = x_max.get()
        x_mn = x_min.get()
        number_of_fit_variables = 0
        col2 = [['b'], ['g'], ['r'], ['c'], ['m'], ['y'], ['k']]
        x = [[] for i in range(len(the_dictionary))]
        y = [[] for i in range(len(the_dictionary))]
        w = [[] for i in range(len(the_dictionary))]
        xs = [[[] for i in label1] for j in x]
        ys = [[[] for i in label1] for j in y]
        ws = [[[] for i in label1] for j in w]
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
                        num_of_transitions += 1
                        # Estas variáveis servem só para não ter de escrever o acesso ao valor do dicionário todas as vezes
                        low_level = the_dictionary[transition]["low_level"]
                        high_level = the_dictionary[transition]["high_level"]
                        diag_stick_val = [line for line in lineradrates if line[1] in low_level and line[5] == high_level and float(
                            line[8]) != 0]  # Cada vez que o for corre, lê o ficheiro de uma transição
                        # for u in range(len(diag_stick_val)):
                        #     if diag_stick_val[u][1] in low_level:
                        #         print(diag_stick_val[u][1], low_level)
                        sat_stick_val = [line for line in linesatellites if low_level in line[1]
                                         and high_level in line[5] and float(line[8]) != 0]
                        # -------------------------------------------------------------------------------------------
                        if sat == 'Diagram':
                            if not diag_stick_val:  # Se não ouver dados no vetor da diagrama
                                # Crio um vector de zeros para o programa continuar a correr (Em string porque estava a dar um erro qq quando punha em int)(range 16 porque é o tamanho da
                                diag_stick_val = [['0' for i in range(16)]]
                                # linha do ficheiro que supostamente preencheria este vertor)
                                # Mostro no ecrã a transição errada que escolheram
                                messagebox.showwarning(
                                    "Wrong Transition", transition + " is not Available")
                                bad_selection += 1  # incremento o numero de transições "mal" escolhidas
                            stem_ploter(diag_stick_val,
                                        transition, 'Diagram', 0, 0)
                        elif sat == 'Satellites':
                            if not sat_stick_val:  # Se não ouver nada no vetor das satelites
                                sat_stick_val = [['0' for i in range(16)]]
                                # Mostro no ecrã a transição errada que escolheram
                                messagebox.showwarning(
                                    "Wrong Transition", transition + " is not Available")
                                bad_selection += 1  # incremento o numero de transições "mal" escolhidas
                            b1 = 0
                            for ind, key in enumerate(label1):
                                sat_stick_val_ind1 = [
                                    line for line in sat_stick_val if low_level + key in line[1] and key + high_level in line[5]]
                                sat_stick_val_ind2 = [line for line in sat_stick_val if low_level +
                                                      key in line[1] and high_level + key in line[5] and key != high_level]
                                sat_stick_val_ind3 = [
                                    line for line in sat_stick_val if key + low_level in line[1] and key + high_level in line[5]]
                                sat_stick_val_ind4 = [
                                    line for line in sat_stick_val if key + low_level in line[1] and high_level + key in line[5] and key != high_level]
                                sat_stick_val_ind = sat_stick_val_ind1 + sat_stick_val_ind2 + \
                                    sat_stick_val_ind3 + sat_stick_val_ind4
                                if len(sat_stick_val_ind) > 1:
                                    stem_ploter(
                                        sat_stick_val_ind, transition, 'Satellites', ind, key)
                                b1 += 100 / len(label1)
                                progress_var.set(b1)
                                sim.update_idletasks()
                        elif sat == 'Diagram + Satellites':
                            if not diag_stick_val:  # Se não ouver dados no vetor da diagrama
                                # Crio um vector de zeros para o programa continuar a correr (Em string porque estava a dar um erro qq quando punha em int)(range 16 porque é o tamanho da
                                diag_stick_val = [['0' for i in range(16)]]
                                # linha do ficheiro que supostamente preencheria este vertor)
                                # Mostro no ecrã a transição errada que escolheram
                                messagebox.showwarning(
                                    "Wrong Transition", "Diagram info. for " + transition + " is not Available")
                                bad_selection += 1  # incremento o numero de transições "mal" escolhidas
                            stem_ploter(diag_stick_val,
                                        transition, 'Diagram', 0, 0)
                            if not sat_stick_val:  # Se não ouver nada no vetor das satelites
                                sat_stick_val = [['0' for i in range(16)]]
                                # Mostro no ecrã a transição errada que escolheram
                                messagebox.showwarning(
                                    "Wrong Transition", "Satellites info.  for " + transition + " is not Available")
                                bad_selection += 1  # incremento o numero de transições "mal" escolhidas
                            b1 = 0
                            for ind, key in enumerate(label1):
                                sat_stick_val_ind1 = [
                                    line for line in sat_stick_val if low_level + key in line[1] and key + high_level in line[5]]
                                sat_stick_val_ind2 = [line for line in sat_stick_val if low_level +
                                                      key in line[1] and high_level + key in line[5] and key != high_level]
                                sat_stick_val_ind3 = [
                                    line for line in sat_stick_val if key + low_level in line[1] and key + high_level in line[5]]
                                sat_stick_val_ind4 = [
                                    line for line in sat_stick_val if key + low_level in line[1] and high_level + key in line[5] and key != high_level]
                                sat_stick_val_ind = sat_stick_val_ind1 + sat_stick_val_ind2 + \
                                    sat_stick_val_ind3 + sat_stick_val_ind4
                                if len(sat_stick_val_ind) > 1:
                                    stem_ploter(
                                        sat_stick_val_ind, transition, 'Satellites', ind, key)
                                b1 += 100 / len(label1)
                                progress_var.set(b1)
                                sim.update_idletasks()

                    graph_area.set_xlabel('Energy (eV)')
                    graph_area.set_ylabel('Intensity (arb. units)')
            else:
                for transition in the_aug_dictionary:
                    # Se a transição estiver selecionada:
                    if the_aug_dictionary[transition]["selected_state"]:
                        num_of_transitions += 1
                        low_level = the_aug_dictionary[transition]["low_level"]
                        high_level = the_aug_dictionary[transition]["high_level"]
                        auger_level = the_aug_dictionary[transition]["auger_level"]

                        aug_stick_val = [line for line in lineauger if low_level in line[1]
                                         and high_level in line[5][:2] and auger_level in line[5][2:4] and float(line[8]) != 0]

                        if not aug_stick_val:  # Se não ouver dados no vetor da diagrama
                            # Crio um vector de zeros para o programa continuar a correr (Em string porque estava a dar um erro qq quando punha em int)(range 16 porque é o tamanho da
                            aug_stick_val = [['0' for i in range(16)]]
                            # linha do ficheiro que supostamente preencheria este vertor)
                            # Mostro no ecrã a transição errada que escolheram
                            messagebox.showwarning(
                                "Wrong Transition", "Auger info. for " + transition + " is not Available")
                            bad_selection += 1  # incremento o numero de transições "mal" escolhidas
                        stem_ploter(aug_stick_val,
                                    transition, 'Auger', 0, 0)

                    graph_area.set_xlabel('Energy (eV)')
                    graph_area.set_ylabel('Intensity (arb. units)')

            if num_of_transitions == 0:
                messagebox.showerror(
                    "No Transition", "No transition was chosen")
            elif bad_selection != 0:
                messagebox.showerror(
                    "Wrong Transition", "You chose " + str(bad_selection) + " invalid transition(s)")
        # --------------------------------------------------------------------------------------------------------------------------
        elif spectype == 'M_Stick':
            # Duas variáveis que servem para ver se há alguma transição mal escolhida. A primeira serve para saber o numero total de transiões escolhidas e a segunda para anotar quantas tranisções erradas se escolheram
            num_of_transitions = 0
            bad_selection = 0
            if sat != 'Auger':
                charge_states = rad_PCS + rad_NCS

                for cs_index, cs in enumerate(charge_states):
                    mix_val = '0.0'
                    ncs = False

                    if cs_index < len(rad_PCS):
                        mix_val = data.variables.PCS_radMixValues[cs_index].get()
                    else:
                        mix_val = data.variables.NCS_radMixValues[cs_index -
                                                   len(rad_PCS)].get()
                        ncs = True
                    if mix_val != '0.0':
                        for transition in the_dictionary:
                            # Se a transição estiver selecionada:
                            if the_dictionary[transition]["selected_state"]:
                                num_of_transitions += 1
                                # Estas variáveis servem só para não ter de escrever o acesso ao valor do dicionário todas as vezes
                                low_level = the_dictionary[transition]["low_level"]
                                high_level = the_dictionary[transition]["high_level"]

                                if not ncs:
                                    diag_stick_val = [line + [data.variables.PCS_radMixValues[i].get()] for i, linerad in enumerate(lineradrates_PCS) for line in linerad if line[1] in low_level and line[5]
                                                      == high_level and float(line[8]) != 0 and rad_PCS[i] == cs]  # Cada vez que o for corre, lê o ficheiro de uma transição
                                else:
                                    diag_stick_val = [line + [data.variables.NCS_radMixValues[i].get()] for i, linerad in enumerate(
                                        lineradrates_NCS) for line in linerad if line[1] in low_level and line[5] == high_level and float(line[8]) != 0 and rad_NCS[i] == cs]

                                if not ncs:
                                    sat_stick_val = [line + [data.variables.PCS_radMixValues[i].get()] for i, linesat in enumerate(
                                        linesatellites_PCS) for line in linesat if low_level in line[1] and high_level in line[5] and float(line[8]) != 0 and sat_PCS[i] == cs]
                                else:
                                    sat_stick_val = [line + [data.variables.NCS_radMixValues[i].get()] for i, linesat in enumerate(
                                        linesatellites_NCS) for line in linesat if low_level in line[1] and high_level in line[5] and float(line[8]) != 0 and sat_NCS[i] == cs]
                                    # -------------------------------------------------------------------------------------------
                                if sat == 'Diagram':
                                    if not diag_stick_val:  # Se não ouver dados no vetor da diagrama
                                        # Crio um vector de zeros para o programa continuar a correr (Em string porque estava a dar um erro qq quando punha em int)(range 16 porque é o tamanho da
                                        diag_stick_val = [
                                            ['0' for i in range(16)]]
                                        # linha do ficheiro que supostamente preencheria este vertor)
                                        # Mostro no ecrã a transição errada que escolheram
                                        messagebox.showwarning(
                                            "Wrong Transition", transition + " is not Available for charge state: " + cs)
                                        bad_selection += 1  # incremento o numero de transições "mal" escolhidas
                                    stem_ploter(
                                        diag_stick_val, cs + ' ' + transition, 'Diagram_CS', 0, 0)
                                elif sat == 'Satellites':
                                    if not sat_stick_val:  # Se não ouver nada no vetor das satelites
                                        sat_stick_val = [
                                            ['0' for i in range(16)]]
                                        # Mostro no ecrã a transição errada que escolheram
                                        messagebox.showwarning(
                                            "Wrong Transition", transition + " is not Available for charge state: " + cs)
                                        bad_selection += 1  # incremento o numero de transições "mal" escolhidas
                                    b1 = 0
                                    for ind, key in enumerate(label1):
                                        sat_stick_val_ind1 = [
                                            line for line in sat_stick_val if low_level + key in line[1] and key + high_level in line[5]]
                                        sat_stick_val_ind2 = [
                                            line for line in sat_stick_val if low_level + key in line[1] and high_level + key in line[5] and key != high_level]
                                        sat_stick_val_ind3 = [
                                            line for line in sat_stick_val if key + low_level in line[1] and key + high_level in line[5]]
                                        sat_stick_val_ind4 = [
                                            line for line in sat_stick_val if key + low_level in line[1] and high_level + key in line[5] and key != high_level]
                                        sat_stick_val_ind = sat_stick_val_ind1 + sat_stick_val_ind2 + \
                                            sat_stick_val_ind3 + sat_stick_val_ind4
                                        if len(sat_stick_val_ind) > 1:
                                            stem_ploter(
                                                sat_stick_val_ind, cs + ' ' + transition, 'Satellites_CS', ind, key)
                                        b1 += 100 / len(label1)
                                        progress_var.set(b1)
                                        sim.update_idletasks()
                                elif sat == 'Diagram + Satellites':
                                    if not diag_stick_val:  # Se não ouver dados no vetor da diagrama
                                        # Crio um vector de zeros para o programa continuar a correr (Em string porque estava a dar um erro qq quando punha em int)(range 16 porque é o tamanho da
                                        diag_stick_val = [
                                            ['0' for i in range(16)]]
                                        # linha do ficheiro que supostamente preencheria este vertor)
                                        # Mostro no ecrã a transição errada que escolheram
                                        messagebox.showwarning(
                                            "Wrong Transition", "Diagram info. for " + transition + " is not Available")
                                        bad_selection += 1  # incremento o numero de transições "mal" escolhidas
                                    stem_ploter(
                                        diag_stick_val, cs + ' ' + transition, 'Diagram_CS', 0, 0)
                                    if not sat_stick_val:  # Se não ouver nada no vetor das satelites
                                        sat_stick_val = [
                                            ['0' for i in range(16)]]
                                        # Mostro no ecrã a transição errada que escolheram
                                        messagebox.showwarning(
                                            "Wrong Transition", "Satellites info.  for " + transition + " is not Available")
                                        bad_selection += 1  # incremento o numero de transições "mal" escolhidas
                                    b1 = 0
                                    for ind, key in enumerate(label1):
                                        sat_stick_val_ind1 = [
                                            line for line in sat_stick_val if low_level + key in line[1] and key + high_level in line[5]]
                                        sat_stick_val_ind2 = [
                                            line for line in sat_stick_val if low_level + key in line[1] and high_level + key in line[5] and key != high_level]
                                        sat_stick_val_ind3 = [
                                            line for line in sat_stick_val if key + low_level in line[1] and key + high_level in line[5]]
                                        sat_stick_val_ind4 = [
                                            line for line in sat_stick_val if key + low_level in line[1] and high_level + key in line[5] and key != high_level]
                                        sat_stick_val_ind = sat_stick_val_ind1 + sat_stick_val_ind2 + \
                                            sat_stick_val_ind3 + sat_stick_val_ind4
                                        if len(sat_stick_val_ind) > 1:
                                            stem_ploter(
                                                sat_stick_val_ind, cs + ' ' + transition, 'Satellites_CS', ind, key)
                                        b1 += 100 / len(label1)
                                        progress_var.set(b1)
                                        sim.update_idletasks()

                            graph_area.set_xlabel('Energy (eV)')
                            graph_area.set_ylabel('Intensity (arb. units)')
            else:
                charge_states = aug_PCS + aug_NCS

                for cs_index, cs in enumerate(charge_states):
                    mix_val = '0.0'
                    ncs = False

                    if cs_index < len(aug_PCS):
                        mix_val = data.variables.PCS_augMixValues[cs_index].get()
                    else:
                        mix_val = data.variables.NCS_augMixValues[cs_index -
                                                   len(aug_PCS)].get()
                        ncs = True
                    if mix_val != '0.0':
                        for transition in the_aug_dictionary:
                            # Se a transição estiver selecionada:
                            if the_aug_dictionary[transition]["selected_state"]:
                                num_of_transitions += 1
                                low_level = the_aug_dictionary[transition]["low_level"]
                                high_level = the_aug_dictionary[transition]["high_level"]
                                auger_level = the_aug_dictionary[transition]["auger_level"]

                                if not ncs:
                                    aug_stick_val = [line + [data.variables.PCS_augMixValues[i].get()] for i, lineaug in enumerate(lineaugrates_PCS) for line in lineaug if low_level in line[1]
                                                     and high_level in line[5][:2] and auger_level in line[5][2:4] and float(line[8]) != 0 and aug_PCS[i] == cs]
                                else:
                                    aug_stick_val = [line + [data.variables.NCS_augMixValues[i].get()] for i, lineaug in enumerate(lineaugrates_NCS) for line in lineaug if low_level in line[1]
                                                     and high_level in line[5][:2] and auger_level in line[5][2:4] and float(line[8]) != 0 and aug_PCS[i] == cs]

                                if not aug_stick_val:  # Se não ouver dados no vetor da diagrama
                                    # Crio um vector de zeros para o programa continuar a correr (Em string porque estava a dar um erro qq quando punha em int)(range 16 porque é o tamanho da
                                    aug_stick_val = [
                                        ['0' for i in range(16)]]
                                    # linha do ficheiro que supostamente preencheria este vertor)
                                    # Mostro no ecrã a transição errada que escolheram
                                    messagebox.showwarning(
                                        "Wrong Transition", "Auger info. for " + transition + " is not Available for charge state: " + cs)
                                    bad_selection += 1  # incremento o numero de transições "mal" escolhidas
                                stem_ploter(
                                    aug_stick_val, cs + ' ' + transition, 'Auger_CS', 0, 0)

                            graph_area.set_xlabel('Energy (eV)')
                            graph_area.set_ylabel('Intensity (arb. units)')

            if num_of_transitions == 0:
                messagebox.showerror(
                    "No Transition", "No transition was chosen")
            elif bad_selection != 0:
                messagebox.showerror(
                    "Wrong Transition", "You chose " + str(bad_selection) + " invalid transition(s)")
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
                        # orbital da lacuna no iní­cio da transição
                        low_level = the_dictionary[transition]["low_level"]
                        # orbital da lacuna no fim da transição
                        high_level = the_dictionary[transition]["high_level"]
                        diag_sim_val = [line for line in lineradrates if line[1] in low_level and line[5] == high_level and float(
                            line[8]) != 0]  # Guarda para uma lista as linhas do ficheiro que se referem à trasição transition
                        sat_sim_val = [line for line in linesatellites if low_level in line[1] and high_level in line[5] and float(
                            line[8]) != 0]  # Guarda para uma lista as linhas do ficheiro que se referem às satélites de transition

                        if sat == 'Diagram':
                            x1 = [float(row[8]) for row in diag_sim_val]
                            y1 = [float(row[11]) * (1 - sum(shakeweights))
                                  for row in diag_sim_val]
                            w1 = [float(row[15]) for row in diag_sim_val]
                            x[index] = x1
                            y[index] = y1
                            w[index] = w1
                        elif sat == 'Satellites':
                            for ind, key in enumerate(label1):
                                sat_sim_val_ind1 = [
                                    line for line in sat_sim_val if low_level + key in line[1] and key + high_level in line[5]]
                                sat_sim_val_ind2 = [line for line in sat_sim_val if low_level +
                                                    key in line[1] and high_level + key in line[5] and key != high_level]
                                sat_sim_val_ind3 = [
                                    line for line in sat_sim_val if key + low_level in line[1] and key + high_level in line[5]]
                                sat_sim_val_ind4 = [
                                    line for line in sat_sim_val if key + low_level in line[1] and high_level + key in line[5] and key != high_level]
                                sat_sim_val_ind = sat_sim_val_ind1 + sat_sim_val_ind2 + \
                                    sat_sim_val_ind3 + sat_sim_val_ind4
                                if len(sat_sim_val_ind) > 1:
                                    x1s = [float(row[8])
                                           for row in sat_sim_val_ind]
                                    y1s = [
                                        float(float(row[11]) * shakeweights[ind]) for row in sat_sim_val_ind]
                                    w1s = [float(row[15])
                                           for row in sat_sim_val_ind]
                                    xs[index][ind] = x1s
                                    ys[index][ind] = y1s
                                    ws[index][ind] = w1s
                        elif sat == 'Diagram + Satellites':
                            x1 = [float(row[8]) for row in diag_sim_val]
                            y1 = [float(row[11]) * (1 - sum(shakeweights))
                                  for row in diag_sim_val]
                            w1 = [float(row[15]) for row in diag_sim_val]
                            x[index] = x1
                            y[index] = y1
                            w[index] = w1
                            # ---------------------------------------------------------------------------------------------------------------------
                            ka1s = [line for line in linesatellites if 'K1' in line[1]
                                    and 'L3' in line[5] and float(line[8]) != 0]
                            for ind, key in enumerate(label1):
                                sat_sim_val_ind1 = [
                                    line for line in sat_sim_val if low_level + key in line[1] and key + high_level in line[5]]
                                sat_sim_val_ind2 = [line for line in sat_sim_val if low_level +
                                                    key in line[1] and high_level + key in line[5] and key != high_level]
                                sat_sim_val_ind3 = [
                                    line for line in sat_sim_val if key + low_level in line[1] and key + high_level in line[5]]
                                sat_sim_val_ind4 = [
                                    line for line in sat_sim_val if key + low_level in line[1] and high_level + key in line[5] and key != high_level]
                                sat_sim_val_ind = sat_sim_val_ind1 + sat_sim_val_ind2 + \
                                    sat_sim_val_ind3 + sat_sim_val_ind4
                                if len(sat_sim_val_ind) > 1:
                                    x1s = [float(row[8])
                                           for row in sat_sim_val_ind]
                                    y1s = [
                                        float(float(row[11]) * shakeweights[ind]) for row in sat_sim_val_ind]
                                    w1s = [float(row[15])
                                           for row in sat_sim_val_ind]
                                    xs[index][ind] = x1s
                                    ys[index][ind] = y1s
                                    ws[index][ind] = w1s
                # -------------------------------------------------------------------------------------------
                # Verificar se se selecionaram transições indí­sponí­veis
                for index, transition in enumerate(the_dictionary):
                    if the_dictionary[transition]["selected_state"]:
                        if not x[index] and not any(xs[index]):
                            messagebox.showwarning(
                                "Wrong Transition", transition + " is not Available")
                            x[index] = []
                            bad_selection += 1
            else:
                x = [[] for i in range(len(the_aug_dictionary))]
                y = [[] for i in range(len(the_aug_dictionary))]
                w = [[] for i in range(len(the_aug_dictionary))]
                xs = [[[] for i in label1] for j in x]
                ys = [[[] for i in label1] for j in y]
                ws = [[[] for i in label1] for j in w]

                for index, transition in enumerate(the_aug_dictionary):
                    if the_aug_dictionary[transition]["selected_state"]:
                        # orbital da lacuna no iní­cio da transição
                        low_level = the_aug_dictionary[transition]["low_level"]
                        # orbital da lacuna no fim da transição
                        high_level = the_aug_dictionary[transition]["high_level"]
                        auger_level = the_aug_dictionary[transition]["auger_level"]

                        aug_sim_val = [line for line in lineauger if low_level in line[1] and high_level in line[5][:2] and auger_level in line[5][2:4] and float(
                            line[8]) != 0]  # Guarda para uma lista as linhas do ficheiro que se referem à trasição transition

                        x1 = [float(row[8]) for row in aug_sim_val]
                        y1 = [float(row[9]) * (1 - sum(shakeweights))
                              for row in aug_sim_val]
                        w1 = [float(row[10]) for row in aug_sim_val]
                        x[index] = x1
                        y[index] = y1
                        w[index] = w1

                # -------------------------------------------------------------------------------------------
                # Verificar se se selecionaram transições indí­sponí­veis
                for index, transition in enumerate(the_aug_dictionary):
                    if the_aug_dictionary[transition]["selected_state"]:
                        if not x[index]:
                            messagebox.showwarning(
                                "Wrong Auger Transition", transition + " is not Available")
                            x[index] = []
                            bad_selection += 1

            # -------------------------------------------------------------------------------------------
            # Obtenção do valor de xfinal a usar nos cáclulos dos yy (caso não seja selecionado um espectro experimental, porque se fo xfinal é mudado)
            # (Calcular a dispersão em energia das varias riscas para criar o array de valores de x a plotar em funcao desta dispersão e da resolução experimental)
            try:
                if sat == 'Diagram':
                    deltaE = []
                    # Percorremos as listas guardadas em x. k é a lista e i o indice onde ela está guardada em x.
                    for j, k in enumerate(x):
                        if k != []:  # Se a lista não estiver vazia, guardamos em deltaE a diferença entre o seu valor máximo e mí­nimo
                            deltaE.append(max(x[j]) - min(x[j]))

                    max_value = max([max(x[i]) for i in range(len(x)) if x[i] != [
                    ]]) + 4 * max([max(w[i]) for i in range(len(w)) if w[i] != []])
                    min_value = min([min(x[i]) for i in range(len(x)) if x[i] != [
                    ]]) - 4 * max([max(w[i]) for i in range(len(w)) if w[i] != []])

                elif sat == 'Satellites' or sat == 'Diagram + Satellites':
                    deltaE = []
                    # Ciclo sobre os elementos de x (ka1, ka2, kb1, etc... 7 no total)
                    for j, k in enumerate(xs):
                        for l, m in enumerate(xs[j]):
                            if m != []:
                                deltaE.append(max(m) - min(m))
                    max_value = max(
                        [max(xs[i][j]) for i in range(len(xs)) for j in range(len(xs[i])) if xs[i][j] != []]) + max([max(ws[i][j]) for i in range(len(ws)) for j in range(len(ws[i])) if ws[i][j] != []])  # valor max de todos os elementos de xs (satt) que tem 7 linhas(ka1, ka2, etc) e o tamanho da lista label1 dentro de cada linha
                    min_value = min([min(xs[i][j]) for i in range(len(xs)) for j in range(len(xs[i])) if xs[i][j] != [
                    ]]) - max([max(ws[i][j]) for i in range(len(ws)) for j in range(len(ws[i])) if ws[i][j] != []])

                elif sat == 'Auger':
                    deltaE = []
                    # Percorremos as listas guardadas em x. k é a lista e i o indice onde ela está guardada em x.
                    for j, k in enumerate(x):
                        if k != []:  # Se a lista não estiver vazia, guardamos em deltaE a diferença entre o seu valor máximo e mí­nimo
                            deltaE.append(max(x[j]) - min(x[j]))

                    max_value = max([max(x[i]) for i in range(len(x)) if x[i] != [
                    ]]) + 4 * max([max(w[i]) for i in range(len(w)) if w[i] != []])
                    min_value = min([min(x[i]) for i in range(len(x)) if x[i] != [
                    ]]) - 4 * max([max(w[i]) for i in range(len(w)) if w[i] != []])
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
                        array_input_max = max_value + \
                            2 * res * (min(deltaE))
                else:
                    array_input_max = float(x_mx) - enoffset
                # Calcular o array com os valores de xfinal igualmente espacados
                xfinal = np.linspace(
                    array_input_min, array_input_max, num=num_of_points)
            except ValueError:
                xfinal = np.zeros(num_of_points)
                if not bad_selection:
                    messagebox.showerror(
                        "No Transition", "No transition was chosen")
                else:
                    messagebox.showerror(
                        "Wrong Transition", "You chose " + str(bad_selection) + " invalid transition(s)")

            # ---------------------------------------------------------------------------------------------------------------
            # Load e plot do espectro experimental
            exp_x = []
            exp_y = []
            exp_sigma = []
            min_exp_lim = 0
            max_exp_lim = 0
            if load != 'No':  # procedimento para fazer o plot experimental
                f.clf()
                gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])
                new_graph_area = f.add_subplot(gs[0])
                graph_area = new_graph_area
                if yscale_log.get() == 'Ylog':
                    graph_area.set_yscale('log')
                if xscale_log.get() == 'Xlog':
                    graph_area.set_xscale('log')
                graph_area.legend(title=element_name)
                residues_graph = f.add_subplot(gs[1])
                residues_graph.set_xlabel('Energy (eV)')
                residues_graph.set_ylabel('Residues (arb. units)')
                # print(load)
                # Carregar a matriz do espectro experimental do ficheiro escolhido no menu
                exp_spectrum = list(csv.reader(
                    open(load, 'r', encoding='utf-8-sig')))
                for i, it in enumerate(exp_spectrum):
                    # Transformar os valores do espectro experimental para float
                    for j, itm in enumerate(exp_spectrum[i]):
                        if exp_spectrum[i][j] != '':
                            exp_spectrum[i][j] = float(itm)
                xe = np.array([float(row[0]) for row in exp_spectrum])
                ye = np.array([float(row[1]) for row in exp_spectrum])
                # Se o espectro experimental tiver 3 colunas a terceira sera a incerteza
                if len(exp_spectrum[0]) >= 3:
                    sigma_exp = np.array([float(row[2])
                                         for row in exp_spectrum])
                else:  # Caso contrario utiliza-se raiz do numero de contagens como a incerteza de cada ponto
                    sigma_exp = np.sqrt(ye)
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

                xfinal = np.array(np.linspace(
                    min(exp_x) - enoffset, max(exp_x) - enoffset, num=num_of_points))

                if normalize == 'One':
                    # Plot dos dados experimentais normalizados à unidade
                    graph_area.scatter(
                        exp_x, exp_y / max(exp_y), marker='.', label='Exp.')
                    # Plot do desvio padrão no gráfico dos resí­duos (linha positiva)
                    residues_graph.plot(exp_x, np.array(
                        exp_sigma) / max(exp_y), 'k--')
                    # Plot do desvio padrão no gráfico dos resí­duos (linha negativa)
                    residues_graph.plot(
                        exp_x, -np.array(exp_sigma) / max(exp_y), 'k--')
                else:
                    # Plot dos dados experimentais
                    graph_area.scatter(
                        exp_x, exp_y, marker='.', label='Exp.')
                    # Plot do desvio padrão no gráfico dos resí­duos (linha positiva)
                    residues_graph.plot(exp_x, np.array(exp_sigma), 'k--')
                    # Plot do desvio padrão no gráfico dos resí­duos (linha negativa)
                    residues_graph.plot(exp_x, -np.array(exp_sigma), 'k--')

                graph_area.legend()

            # ---------------------------------------------------------------------------------------------------------------
            # Leitura dos valores da eficácia do detector:
            efficiency_values = []
            energy_values = []
            if effic_file_name != "No":
                try:
                    efficiency = list(csv.reader(
                        open(effic_file_name, 'r')))
                    for pair in efficiency:
                        energy_values.append(float(pair[0]))
                        efficiency_values.append(float(pair[1]))
                except FileNotFoundError:
                    messagebox.showwarning(
                        "Error", "Efficiency File is not Avaliable")
            # ---------------------------------------------------------------------------------------------------------------
            # Variáveis necessárias para os cálcuos dos y e para os plots:
            data.variables.ytot, data.variables.yfinal, data.variables.yfinals = y_calculator(
                sat, peak, xfinal, x, y, w, xs, ys, ws, res, energy_values, efficiency_values, enoffset)

            # ---------------------------------------------------------------------------------------------------------------
            # Cálculo da variável de notificação:
            # O cálculo é feito na função normalizer, e é lá que é lida a escolha de normalização do utilizador. Aqui só passamos dados para a funçao
            if load != 'No':
                normalization_var = normalizer(y0, max(exp_y), max(data.variables.ytot))
            else:
                if normalizevar.get() == 'ExpMax':  # Se tentarem normalizar ao maximo experimental sem terem carregado espectro
                    messagebox.showwarning(
                        "No experimental spectrum is loaded", "Choose different normalization option")  # Apresenta aviso
                    # Define a variavel global de normalização para não normalizar
                    normalizevar.set('No')
                normalization_var = normalizer(y0, 1, max(data.variables.ytot))
            # ---------------------------------------------------------------------------------------------------------------
            # Autofit:
            # start_time = time.time()
            if autofit == 'Yes':
                # Fazemos fit apenas se houver um gráfico experimental carregado
                if load != 'No':

                    # Criar os parametros que vão ser otimizados
                    params = Parameters()

                    # Offset em energia
                    # O offset vai variar entre o valor introduzido +/- 10% do tamanho do gráfico
                    xoff_lim = (max(exp_x) - min(exp_x)) * 0.1
                    params.add('xoff', value=enoffset, min=enoffset -
                               xoff_lim, max=enoffset + xoff_lim)

                    # Offset no yy
                    yoff_lim = (max(exp_y) - min(exp_y)) * 0.1
                    params.add('yoff', value=y0, min=y0 -
                               yoff_lim, max=y0 + yoff_lim)

                    # Resolução experimental
                    res_lim = res * 3
                    params.add('res', value=res, min=0.01,
                               max=res + res_lim)

                    # # Variável de normalização
                    # norm_lim = normalization_var * 0.5
                    # params.add('normal', value=normalization_var)

                    # Parametro na Normalization var
                    params.add('ytot_max', value=max(data.variables.ytot))
                    number_of_fit_variables = len(params.valuesdict())
                    minner = Minimizer(func2min, params, fcn_args=(
                        exp_x, exp_y, num_of_points, sat, peak, x, y, w, xs, ys, ws, energy_values, efficiency_values, enoffset))
                    result = minner.minimize()
                    # report_fit(result)

                    # Offset em energia a ser definido para o plot final das linhas
                    enoffset = result.params['xoff'].value
                    energy_offset.set(enoffset)
                    # Offset no yy a ser definido para o plot final das linhas
                    y0 = result.params['yoff'].value
                    yoffset.set(y0)
                    # Resolução experimental a ser definido para o plot final das linhas
                    res = result.params['res'].value
                    exp_resolution.set(res)
                    # normalization_var = result.params['normal'].value
                    ytot_max = result.params['ytot_max'].value

                    xfinal = np.array(np.linspace(
                        min(exp_x) - enoffset, max(exp_x) - enoffset, num=num_of_points))
                    data.variables.ytot, data.variables.yfinal, data.variables.yfinals = y_calculator(
                        sat, peak, xfinal, x, y, w, xs, ys, ws, res, energy_values, efficiency_values, enoffset)
                    normalization_var = normalizer(
                        y0, max(exp_y), ytot_max)
                    if messagebox.askyesno("Fit Saving", "Do you want to save this fit?"):
                        with open(file_namer("Fit", time_of_click, ".txt"), 'w') as file:
                            file.write(fit_report(result))
                        print(fit_report(result))
                    # residues_graph.plot(exp_x, np.array(result.residual))
                    # residues_graph.legend(title="Red.= " + "{:.5f}".format(result.redchi), loc='lower right')

                else:
                    messagebox.showerror(
                        "Error", "Autofit is only avaliable if an experimental spectrum is loaded")
            # ------------------------------------------------------------------------------------------------------------------------
            # Plot das linhas
            # print('Time of fit execution: --- %s seconds ---' % (time.time() - start_time))
            if sat == 'Diagram':
                for index, key in enumerate(the_dictionary):
                    if the_dictionary[key]["selected_state"]:
                        graph_area.plot(xfinal + enoffset, (np.array(data.variables.yfinal[index]) * normalization_var) + y0, label=key, color=str(
                            col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                        graph_area.legend()
            elif sat == 'Satellites':
                for index, key in enumerate(the_dictionary):
                    if the_dictionary[key]["selected_state"]:
                        for l, m in enumerate(data.variables.yfinals[index]):
                            if max(m) != 0:  # Excluir as linhas que nao foram seleccionados nos botoes
                                graph_area.plot(xfinal + enoffset, (np.array(data.variables.yfinals[index][l]) * normalization_var) + y0, label=key + ' - ' + labeldict[label1[l]], color=str(
                                    col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                                graph_area.legend()
            elif sat == 'Diagram + Satellites':
                for index, key in enumerate(the_dictionary):
                    if the_dictionary[key]["selected_state"]:
                        graph_area.plot(xfinal + enoffset, (np.array(data.variables.yfinal[index]) * normalization_var) + y0, label=key, color=str(
                            col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                        graph_area.legend()

                for index, key in enumerate(the_dictionary):
                    if the_dictionary[key]["selected_state"]:
                        for l, m in enumerate(data.variables.yfinals[index]):
                            if max(m) != 0:  # Excluir as linhas que nao foram seleccionados nos botoes
                                graph_area.plot(xfinal + enoffset, (np.array(data.variables.yfinals[index][l]) * normalization_var) + y0, label=key + ' - ' + labeldict[label1[l]], color=str(
                                    col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                                graph_area.legend()
            elif sat == 'Auger':
                for index, key in enumerate(the_aug_dictionary):
                    if the_aug_dictionary[key]["selected_state"]:
                        graph_area.plot(xfinal + enoffset, (np.array(data.variables.yfinal[index]) * normalization_var) + y0, label=key, color=str(
                            col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                        graph_area.legend()
            if total == 'Total':
                graph_area.plot(xfinal + enoffset, (data.variables.ytot * normalization_var) + y0,
                                label='Total', ls='--', lw=2, color='k')  # Plot the simulation of all lines
                graph_area.legend()
            # ------------------------------------------------------------------------------------------------------------------------
            # Cálculo dos Residuos
            if load != 'No':
                # if load != 'No':
                # Definimos uma função que recebe um numero, e tendo como dados o que passamos à interp1d faz a sua interpolação
                # print(*ytot, sep=',')
                # Criar lista vazia para o gráfico de resí­duos
                y_interp = [0 for i in range(len(exp_x))]
                f_interpolate = interp1d(
                    xfinal + enoffset, (np.array(data.variables.ytot) * normalization_var) + y0, kind='cubic')
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
                        chi_sum += (y_res[g] ** 2) / \
                            ((exp_sigma[g] / max(exp_y))**2)
                    #     y_res[g] = (exp_y[g] / max(exp_y)) - y_interp[g]
                    # Somatório para o cálculo de chi quad
                
                data.variables.chi_sqrd = chi_sum / (len(exp_x) - number_of_fit_variables)
                residues_graph.plot(exp_x, y_res)
                print("Valor Manual Chi", data.variables.chi_sqrd)
                residues_graph.legend(
                    title="Red. \u03C7\u00B2 = " + "{:.5f}".format(data.variables.chi_sqrd))
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
            labels_per_columns = number_of_labels / \
                legend_columns  # Numero de entradas por coluna
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
                charge_states = rad_PCS + rad_NCS

                ploted_cs = []

                for cs_index, cs in enumerate(charge_states):
                    mix_val = '0.0'
                    ncs = False

                    if cs_index < len(rad_PCS):
                        mix_val = data.variables.PCS_radMixValues[cs_index].get()
                    else:
                        mix_val = data.variables.NCS_radMixValues[cs_index -
                                                   len(rad_PCS)].get()
                        ncs = True

                    if mix_val != '0.0':
                        ploted_cs.append(cs)

                x = [[]
                     for i in range(len(the_dictionary) * len(ploted_cs))]
                y = [[]
                     for i in range(len(the_dictionary) * len(ploted_cs))]
                w = [[]
                     for i in range(len(the_dictionary) * len(ploted_cs))]
                xs = [[[] for i in label1] for j in x]
                ys = [[[] for i in label1] for j in y]
                ws = [[[] for i in label1] for j in w]

                for cs_index, cs in enumerate(ploted_cs):
                    for index, transition in enumerate(the_dictionary):
                        if the_dictionary[transition]["selected_state"]:
                            # orbital da lacuna no iní­cio da transição
                            low_level = the_dictionary[transition]["low_level"]
                            # orbital da lacuna no fim da transição
                            high_level = the_dictionary[transition]["high_level"]

                            if not ncs:
                                diag_sim_val = [line + [data.variables.PCS_radMixValues[i].get()] for i, linerad in enumerate(lineradrates_PCS) for line in linerad if line[1] in low_level and line[5]
                                                == high_level and float(line[8]) != 0 and rad_PCS[i] == cs]  # Guarda para uma lista as linhas do ficheiro que se referem à trasição transition
                            else:
                                diag_sim_val = [line + [data.variables.NCS_radMixValues[i].get()] for i, linerad in enumerate(lineradrates_NCS)
                                                for line in linerad if line[1] in low_level and line[5] == high_level and float(line[8]) != 0 and rad_NCS[i] == cs]

                            if not ncs:
                                sat_sim_val = [line + [data.variables.PCS_radMixValues[rad_PCS.index(sat_PCS[i])].get()] for i, linesat in enumerate(linesatellites_PCS) for line in linesat if low_level in line[1] and high_level in line[5] and float(
                                    line[8]) != 0 and sat_PCS[i] == cs]  # Guarda para uma lista as linhas do ficheiro que se referem às satélites de transition
                            else:
                                sat_sim_val = [line + [data.variables.NCS_radMixValues[rad_NCS.index(sat_NCS[i])].get()] for i, linesat in enumerate(linesatellites_NCS) for line in linesat if low_level in line[1] and high_level in line[5] and float(
                                    line[8]) != 0 and sat_NCS[i] == cs]  # Guarda para uma lista as linhas do ficheiro que se referem às satélites de transition

                            if sat == 'Diagram':
                                x1 = [float(row[8])
                                      for row in diag_sim_val]
                                y1 = [float(row[11]) * (1 - sum(shakeweights))
                                      * float(row[-1]) for row in diag_sim_val]
                                w1 = [float(row[15])
                                      for row in diag_sim_val]
                                x[cs_index *
                                    len(the_dictionary) + index] = x1
                                y[cs_index *
                                    len(the_dictionary) + index] = y1
                                w[cs_index *
                                    len(the_dictionary) + index] = w1
                            elif sat == 'Satellites':
                                for ind, key in enumerate(label1):
                                    sat_sim_val_ind1 = [
                                        line for line in sat_sim_val if low_level + key in line[1] and key + high_level in line[5]]
                                    sat_sim_val_ind2 = [line for line in sat_sim_val if low_level +
                                                        key in line[1] and high_level + key in line[5] and key != high_level]
                                    sat_sim_val_ind3 = [
                                        line for line in sat_sim_val if key + low_level in line[1] and key + high_level in line[5]]
                                    sat_sim_val_ind4 = [
                                        line for line in sat_sim_val if key + low_level in line[1] and high_level + key in line[5] and key != high_level]
                                    sat_sim_val_ind = sat_sim_val_ind1 + sat_sim_val_ind2 + \
                                        sat_sim_val_ind3 + sat_sim_val_ind4
                                    if len(sat_sim_val_ind) > 1:
                                        x1s = [float(row[8])
                                               for row in sat_sim_val_ind]
                                        y1s = [float(
                                            float(row[11]) * shakeweights[ind] * float(row[-1])) for row in sat_sim_val_ind]
                                        w1s = [float(row[15])
                                               for row in sat_sim_val_ind]
                                        xs[cs_index *
                                            len(the_dictionary) + index][ind] = x1s
                                        ys[cs_index *
                                            len(the_dictionary) + index][ind] = y1s
                                        ws[cs_index *
                                            len(the_dictionary) + index][ind] = w1s
                            elif sat == 'Diagram + Satellites':
                                x1 = [float(row[8])
                                      for row in diag_sim_val]
                                y1 = [float(row[11]) * (1 - sum(shakeweights))
                                      * float(row[-1]) for row in diag_sim_val]
                                w1 = [float(row[15])
                                      for row in diag_sim_val]
                                x[cs_index *
                                    len(the_dictionary) + index] = x1
                                y[cs_index *
                                    len(the_dictionary) + index] = y1
                                w[cs_index *
                                    len(the_dictionary) + index] = w1
                                # ---------------------------------------------------------------------------------------------------------------------
                                for ind, key in enumerate(label1):
                                    sat_sim_val_ind1 = [
                                        line for line in sat_sim_val if low_level + key in line[1] and key + high_level in line[5]]
                                    sat_sim_val_ind2 = [line for line in sat_sim_val if low_level +
                                                        key in line[1] and high_level + key in line[5] and key != high_level]
                                    sat_sim_val_ind3 = [
                                        line for line in sat_sim_val if key + low_level in line[1] and key + high_level in line[5]]
                                    sat_sim_val_ind4 = [
                                        line for line in sat_sim_val if key + low_level in line[1] and high_level + key in line[5] and key != high_level]
                                    sat_sim_val_ind = sat_sim_val_ind1 + sat_sim_val_ind2 + \
                                        sat_sim_val_ind3 + sat_sim_val_ind4

                                    if len(sat_sim_val_ind) > 1:
                                        x1s = [float(row[8])
                                               for row in sat_sim_val_ind]
                                        y1s = [float(
                                            float(row[11]) * shakeweights[ind] * float(row[-1])) for row in sat_sim_val_ind]
                                        w1s = [float(row[15])
                                               for row in sat_sim_val_ind]
                                        xs[cs_index *
                                            len(the_dictionary) + index][ind] = x1s
                                        ys[cs_index *
                                            len(the_dictionary) + index][ind] = y1s
                                        ws[cs_index *
                                            len(the_dictionary) + index][ind] = w1s
                    # -------------------------------------------------------------------------------------------
                    # Verificar se se selecionaram transições indí­sponí­veis
                    for index, transition in enumerate(the_dictionary):
                        if the_dictionary[transition]["selected_state"]:
                            if not x[cs_index * len(the_dictionary) + index] and not any(xs[cs_index * len(the_dictionary) + index]):
                                if cs not in bad_lines:
                                    bad_lines[cs] = [transition]
                                else:
                                    bad_lines[cs].append(transition)

                                x[cs_index *
                                    len(the_dictionary) + index] = []
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

                    messagebox.showwarning(
                        "Common Transitions", intersection)
                else:
                    messagebox.showwarning(
                        "Common Transitions", "Every transition is plotted for at least 1 charge state.")
            else:
                charge_states = aug_PCS + aug_NCS

                ploted_cs = []

                for cs_index, cs in enumerate(charge_states):
                    mix_val = '0.0'
                    ncs = False

                    if cs_index < len(aug_PCS):
                        mix_val = data.variables.PCS_augMixValues[cs_index].get()
                    else:
                        mix_val = data.variables.NCS_augMixValues[cs_index -
                                                   len(aug_PCS)].get()
                        ncs = True
                    if mix_val != '0.0':
                        ploted_cs.append(cs)

                x = [[]
                     for i in range(len(the_aug_dictionary) * len(ploted_cs))]
                y = [[]
                     for i in range(len(the_aug_dictionary) * len(ploted_cs))]
                w = [[]
                     for i in range(len(the_aug_dictionary) * len(ploted_cs))]
                xs = [[[] for i in label1] for j in x]
                ys = [[[] for i in label1] for j in y]
                ws = [[[] for i in label1] for j in w]

                for cs_index, cs in enumerate(ploted_cs):
                    for index, transition in enumerate(the_aug_dictionary):
                        if the_aug_dictionary[transition]["selected_state"]:
                            # orbital da lacuna no iní­cio da transição
                            low_level = the_aug_dictionary[transition]["low_level"]
                            # orbital da lacuna no fim da transição
                            high_level = the_aug_dictionary[transition]["high_level"]
                            auger_level = the_aug_dictionary[transition]["auger_level"]

                            if not ncs:
                                aug_sim_val = [line + [data.variables.PCS_augMixValues[i].get()] for i, lineaug in enumerate(lineaugrates_PCS) for line in lineaug if low_level in line[1] and high_level in line[5]
                                               [:2] and auger_level in line[5][2:4] and float(line[8]) != 0 and aug_PCS[i] == cs]  # Guarda para uma lista as linhas do ficheiro que se referem à trasição transition
                            else:
                                aug_sim_val = [line + [data.variables.NCS_augMixValues[i].get()] for i, lineaug in enumerate(lineaugrates_NCS) for line in lineaug if low_level in line[1] and high_level in line[5]
                                               [:2] and auger_level in line[5][2:4] and float(line[8]) != 0 and aug_NCS[i] == cs]  # Guarda para uma lista as linhas do ficheiro que se referem à trasição transition

                            x1 = [float(row[8]) for row in aug_sim_val]
                            y1 = [float(row[9]) * (1 - sum(shakeweights))
                                  * float(row[-1]) for row in aug_sim_val]
                            w1 = [float(row[10]) for row in aug_sim_val]
                            x[cs_index *
                                len(the_aug_dictionary) + index] = x1
                            y[cs_index *
                                len(the_aug_dictionary) + index] = y1
                            w[cs_index *
                                len(the_aug_dictionary) + index] = w1

                    # -------------------------------------------------------------------------------------------
                    # Verificar se se selecionaram transições indí­sponí­veis
                    for index, transition in enumerate(the_aug_dictionary):
                        if the_aug_dictionary[transition]["selected_state"]:
                            if not x[cs_index * len(the_aug_dictionary) + index]:
                                if cs not in bad_lines:
                                    bad_lines[cs] = [transition]
                                else:
                                    bad_lines[cs].append(transition)

                                x[cs_index *
                                    len(the_aug_dictionary) + index] = []
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

                    messagebox.showwarning(
                        "Common Auger Transitions", intersection)
                else:
                    messagebox.showwarning(
                        "Common Auger Transitions", "Every transition is plotted for at least 1 charge state.")

            # -------------------------------------------------------------------------------------------
            # Obtenção do valor de xfinal a usar nos cáclulos dos yy (caso não seja selecionado um espectro experimental, porque se fo xfinal é mudado)
            # (Calcular a dispersão em energia das varias riscas para criar o array de valores de x a plotar em funcao desta dispersão e da resolução experimental)
            try:
                if sat == 'Diagram':
                    deltaE = []
                    # Percorremos as listas guardadas em x. k é a lista e i o indice onde ela está guardada em x.
                    for j, k in enumerate(x):
                        if k != []:  # Se a lista não estiver vazia, guardamos em deltaE a diferença entre o seu valor máximo e mí­nimo
                            deltaE.append(max(x[j]) - min(x[j]))

                    max_value = max([max(x[i]) for i in range(len(x)) if x[i] != [
                    ]]) + 4 * max([max(w[i]) for i in range(len(w)) if w[i] != []])
                    min_value = min([min(x[i]) for i in range(len(x)) if x[i] != [
                    ]]) - 4 * max([max(w[i]) for i in range(len(w)) if w[i] != []])

                elif sat == 'Satellites' or sat == 'Diagram + Satellites':
                    deltaE = []
                    # Ciclo sobre os elementos de x (ka1, ka2, kb1, etc... 7 no total)
                    for j, k in enumerate(xs):
                        for l, m in enumerate(xs[j]):
                            if m != []:
                                deltaE.append(max(m) - min(m))
                    max_value = max(
                        [max(xs[i][j]) for i in range(len(xs)) for j in range(len(xs[i])) if xs[i][j] != []]) + max([max(ws[i][j]) for i in range(len(ws)) for j in range(len(ws[i])) if ws[i][j] != []])  # valor max de todos os elementos de xs (satt) que tem 7 linhas(ka1, ka2, etc) e o tamanho da lista label1 dentro de cada linha
                    min_value = min([min(xs[i][j]) for i in range(len(xs)) for j in range(len(xs[i])) if xs[i][j] != [
                    ]]) - max([max(ws[i][j]) for i in range(len(ws)) for j in range(len(ws[i])) if ws[i][j] != []])

                elif sat == 'Auger':
                    deltaE = []
                    # Percorremos as listas guardadas em x. k é a lista e i o indice onde ela está guardada em x.
                    for j, k in enumerate(x):
                        if k != []:  # Se a lista não estiver vazia, guardamos em deltaE a diferença entre o seu valor máximo e mí­nimo
                            deltaE.append(max(x[j]) - min(x[j]))

                    max_value = max([max(x[i]) for i in range(len(x)) if x[i] != [
                    ]]) + 4 * max([max(w[i]) for i in range(len(w)) if w[i] != []])
                    min_value = min([min(x[i]) for i in range(len(x)) if x[i] != [
                    ]]) - 4 * max([max(w[i]) for i in range(len(w)) if w[i] != []])
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
                        array_input_max = max_value + \
                            2 * res * (min(deltaE))
                else:
                    array_input_max = float(x_mx) - enoffset
                # Calcular o array com os valores de xfinal igualmente espacados
                xfinal = np.linspace(
                    array_input_min, array_input_max, num=num_of_points)
            except ValueError:
                xfinal = np.zeros(num_of_points)
                if not bad_selection:
                    messagebox.showerror(
                        "No Transition", "No transition was chosen")
                else:
                    messagebox.showerror(
                        "Wrong Transition", "You chose " + str(bad_selection) + " invalid transition(s)")

            # ---------------------------------------------------------------------------------------------------------------
            # Load e plot do espectro experimental
            exp_x = []
            exp_y = []
            exp_sigma = []
            min_exp_lim = 0
            max_exp_lim = 0
            if load != 'No':  # procedimento para fazer o plot experimental
                f.clf()
                gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])
                new_graph_area = f.add_subplot(gs[0])
                graph_area = new_graph_area
                if yscale_log.get() == 'Ylog':
                    graph_area.set_yscale('log')
                if xscale_log.get() == 'Xlog':
                    graph_area.set_xscale('log')
                graph_area.legend(title=element_name)
                residues_graph = f.add_subplot(gs[1])
                residues_graph.set_xlabel('Energy (eV)')
                residues_graph.set_ylabel('Residues (arb. units)')
                # print(load)
                # Carregar a matriz do espectro experimental do ficheiro escolhido no menu
                exp_spectrum = list(csv.reader(
                    open(load, 'r', encoding='utf-8-sig')))
                for i, it in enumerate(exp_spectrum):
                    # Transformar os valores do espectro experimental para float
                    for j, itm in enumerate(exp_spectrum[i]):
                        if exp_spectrum[i][j] != '':
                            exp_spectrum[i][j] = float(itm)
                xe = np.array([float(row[0]) for row in exp_spectrum])
                ye = np.array([float(row[1]) for row in exp_spectrum])
                # Se o espectro experimental tiver 3 colunas a terceira sera a incerteza
                if len(exp_spectrum[0]) >= 3:
                    sigma_exp = np.array([float(row[2])
                                         for row in exp_spectrum])
                else:  # Caso contrario utiliza-se raiz do numero de contagens como a incerteza de cada ponto
                    sigma_exp = np.sqrt(ye)
                    # replace zeros with the min unceartanty to prevent an inf chi sqr
                    sigma_exp[sigma_exp == 0] = np.min(
                        sigma_exp[sigma_exp != 0])
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

                xfinal = np.array(np.linspace(
                    min(exp_x) - enoffset, max(exp_x) - enoffset, num=num_of_points))

                if normalize == 'One':
                    # Plot dos dados experimentais normalizados à unidade
                    graph_area.scatter(
                        exp_x, exp_y / max(exp_y), marker='.', label='Exp.')
                    # Plot do desvio padrão no gráfico dos resí­duos (linha positiva)
                    residues_graph.plot(exp_x, np.array(
                        exp_sigma) / max(exp_y), 'k--')
                    # Plot do desvio padrão no gráfico dos resí­duos (linha negativa)
                    residues_graph.plot(
                        exp_x, -np.array(exp_sigma) / max(exp_y), 'k--')
                else:
                    # Plot dos dados experimentais
                    graph_area.scatter(
                        exp_x, exp_y, marker='.', label='Exp.')
                    # Plot do desvio padrão no gráfico dos resí­duos (linha positiva)
                    residues_graph.plot(exp_x, np.array(exp_sigma), 'k--')
                    # Plot do desvio padrão no gráfico dos resí­duos (linha negativa)
                    residues_graph.plot(exp_x, -np.array(exp_sigma), 'k--')

                graph_area.legend()

            # ---------------------------------------------------------------------------------------------------------------
            # Leitura dos valores da eficácia do detector:
            efficiency_values = []
            energy_values = []
            if effic_file_name != "No":
                try:
                    efficiency = list(csv.reader(
                        open(effic_file_name, 'r')))
                    for pair in efficiency:
                        energy_values.append(float(pair[0]))
                        efficiency_values.append(float(pair[1]))
                except FileNotFoundError:
                    messagebox.showwarning(
                        "Error", "Efficiency File is not Avaliable")
            # ---------------------------------------------------------------------------------------------------------------
            # Variáveis necessárias para os cálcuos dos y e para os plots:
            data.variables.ytot, data.variables.yfinal, data.variables.yfinals = y_calculator(
                sat, peak, xfinal, x, y, w, xs, ys, ws, res, energy_values, efficiency_values, enoffset)

            # ---------------------------------------------------------------------------------------------------------------
            # Cálculo da variável de notificação:
            # O cálculo é feito na função normalizer, e é lá que é lida a escolha de normalização do utilizador. Aqui só passamos dados para a funçao
            if load != 'No':
                normalization_var = normalizer(y0, max(exp_y), max(data.variables.ytot))
            else:
                if normalizevar.get() == 'ExpMax':  # Se tentarem normalizar ao maximo experimental sem terem carregado espectro
                    messagebox.showwarning(
                        "No experimental spectrum is loaded", "Choose different normalization option")  # Apresenta aviso
                    # Define a variavel global de normalização para não normalizar
                    normalizevar.set('No')
                normalization_var = normalizer(y0, 1, max(data.variables.ytot))
            # ---------------------------------------------------------------------------------------------------------------
            # Autofit:
            # start_time = time.time()
            if autofit == 'Yes':
                # Fazemos fit apenas se houver um gráfico experimental carregado
                if load != 'No':

                    # Criar os parametros que vão ser otimizados
                    params = Parameters()

                    # Offset em energia
                    # O offset vai variar entre o valor introduzido +/- 10% do tamanho do gráfico
                    xoff_lim = (max(exp_x) - min(exp_x)) * 0.1
                    params.add('xoff', value=enoffset, min=enoffset -
                               xoff_lim, max=enoffset + xoff_lim)

                    # Offset no yy
                    yoff_lim = (max(exp_y) - min(exp_y)) * 0.1
                    params.add('yoff', value=y0, min=y0 -
                               yoff_lim, max=y0 + yoff_lim)

                    # Resolução experimental
                    res_lim = res * 3
                    params.add('res', value=res, min=0.01,
                               max=res + res_lim)

                    # # Variável de normalização
                    # norm_lim = normalization_var * 0.5
                    # params.add('normal', value=normalization_var)

                    # Parametro na Normalization var
                    params.add('ytot_max', value=max(data.variables.ytot))
                    number_of_fit_variables = len(params.valuesdict())
                    minner = Minimizer(func2min, params, fcn_args=(
                        exp_x, exp_y, num_of_points, sat, peak, x, y, w, xs, ys, ws, energy_values, efficiency_values, enoffset))
                    result = minner.minimize()
                    # report_fit(result)

                    # Offset em energia a ser definido para o plot final das linhas
                    enoffset = result.params['xoff'].value
                    energy_offset.set(enoffset)
                    # Offset no yy a ser definido para o plot final das linhas
                    y0 = result.params['yoff'].value
                    yoffset.set(y0)
                    # Resolução experimental a ser definido para o plot final das linhas
                    res = result.params['res'].value
                    exp_resolution.set(res)
                    # normalization_var = result.params['normal'].value
                    ytot_max = result.params['ytot_max'].value

                    xfinal = np.array(np.linspace(
                        min(exp_x) - enoffset, max(exp_x) - enoffset, num=num_of_points))
                    data.variables.ytot, data.variables.yfinal, data.variables.yfinals = y_calculator(
                        sat, peak, xfinal, x, y, w, xs, ys, ws, res, energy_values, efficiency_values, enoffset)
                    normalization_var = normalizer(
                        y0, max(exp_y), ytot_max)
                    if messagebox.askyesno("Fit Saving", "Do you want to save this fit?"):
                        with open(file_namer("Fit", time_of_click, ".txt"), 'w') as file:
                            file.write(fit_report(result))
                        print(fit_report(result))
                    # residues_graph.plot(exp_x, np.array(result.residual))
                    # residues_graph.legend(title="Red.= " + "{:.5f}".format(result.redchi), loc='lower right')

                else:
                    messagebox.showerror(
                        "Error", "Autofit is only avaliable if an experimental spectrum is loaded")
            # ------------------------------------------------------------------------------------------------------------------------
            # Plot das linhas
            # print('Time of fit execution: --- %s seconds ---' % (time.time() - start_time))
            if sat == 'Diagram':
                for cs_index, cs in enumerate(ploted_cs):
                    for index, key in enumerate(the_dictionary):
                        if the_dictionary[key]["selected_state"]:
                            graph_area.plot(xfinal + enoffset, (np.array(data.variables.yfinal[cs_index * len(the_dictionary) + index]) * normalization_var) + y0, label=cs + ' ' + key, color=str(
                                col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                            graph_area.legend()
            elif sat == 'Satellites':
                for cs_index, cs in enumerate(ploted_cs):
                    for index, key in enumerate(the_dictionary):
                        if the_dictionary[key]["selected_state"]:
                            for l, m in enumerate(data.variables.yfinals[cs_index * len(the_dictionary) + index]):
                                # Excluir as linhas que nao foram seleccionados nos botoes
                                if max(m) != 0:
                                    graph_area.plot(xfinal + enoffset, (np.array(data.variables.yfinals[cs_index * len(the_dictionary) + index][l]) * normalization_var) + y0,
                                                    label=key + ' - ' + labeldict[label1[l]], color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                                    graph_area.legend()
            elif sat == 'Diagram + Satellites':
                for cs_index, cs in enumerate(ploted_cs):
                    for index, key in enumerate(the_dictionary):
                        if the_dictionary[key]["selected_state"]:
                            graph_area.plot(xfinal + enoffset, (np.array(data.variables.yfinal[cs_index * len(the_dictionary) + index]) * normalization_var) + y0, label=cs + ' ' + key, color=str(
                                col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                            graph_area.legend()

                    for index, key in enumerate(the_dictionary):
                        if the_dictionary[key]["selected_state"]:
                            for l, m in enumerate(data.variables.yfinals[cs_index * len(the_dictionary) + index]):
                                # Excluir as linhas que nao foram seleccionados nos botoes
                                if max(m) != 0:
                                    graph_area.plot(xfinal + enoffset, (np.array(data.variables.yfinals[cs_index * len(the_dictionary) + index][l]) * normalization_var) + y0, label=cs +
                                                    ' ' + key + ' - ' + labeldict[label1[l]], color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                                    graph_area.legend()
            elif sat == 'Auger':
                for cs_index, cs in enumerate(ploted_cs):
                    for index, key in enumerate(the_aug_dictionary):
                        if the_aug_dictionary[key]["selected_state"]:
                            graph_area.plot(xfinal + enoffset, (np.array(data.variables.yfinal[cs_index * len(the_aug_dictionary) + index]) * normalization_var) + y0, label=cs + ' ' + key, color=str(
                                col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                            graph_area.legend()
            if total == 'Total':
                graph_area.plot(xfinal + enoffset, (data.variables.ytot * normalization_var) + y0,
                                label='Total', ls='--', lw=2, color='k')  # Plot the simulation of all lines
                graph_area.legend()
            # ------------------------------------------------------------------------------------------------------------------------
            # Cálculo dos Residuos
            if load != 'No':
                # if load != 'No':
                # Definimos uma função que recebe um numero, e tendo como dados o que passamos à interp1d faz a sua interpolação
                # print(*ytot, sep=',')
                # Criar lista vazia para o gráfico de resí­duos
                y_interp = [0 for i in range(len(exp_x))]
                f_interpolate = interp1d(
                    xfinal + enoffset, (np.array(data.variables.ytot) * normalization_var) + y0, kind='cubic')
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
                        chi_sum += (y_res[g] ** 2) / \
                            ((exp_sigma[g] / max(exp_y))**2)
                    #     y_res[g] = (exp_y[g] / max(exp_y)) - y_interp[g]
                    # Somatório para o cálculo de chi quad

                data.variables.chi_sqrd = chi_sum / (len(exp_x) - number_of_fit_variables)
                residues_graph.plot(exp_x, y_res)
                print("Valor Manual Chi", data.variables.chi_sqrd)
                residues_graph.legend(
                    title="Red. \u03C7\u00B2 = " + "{:.5f}".format(data.variables.chi_sqrd))
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
            labels_per_columns = number_of_labels / \
                legend_columns  # Numero de entradas por coluna
            while labels_per_columns > 10:  # Se a priori for menos de 10 entradas por coluna, não acontece nada
                legend_columns += 1  # Se houver mais que 10 entradas por coluna, meto mais uma coluna
                # Recalculo o numero de entradas por coluna
                labels_per_columns = number_of_labels / legend_columns
            # Defino o numero de colunas na legenda = numero de colunas necessárias para não ter mais de 10 entradas por coluna
            graph_area.legend(ncol=legend_columns)

        f.canvas.draw()

    def on_key_event(event):  # NAO SEI BEM O QUE ISTO FAZ
        print('you pressed %s' % event.key)
        key_press_handler(event, canvas, toolbar)

    # NAO SEI BEM O QUE ISTO FAZ
    canvas.mpl_connect('key_press_event', on_key_event)

    def _quit():
        original = satelite_var.get()

        satelite_var.set('Diagram')

        for transition in the_dictionary:
            if the_dictionary[transition]["selected_state"]:
                dict_updater(transition)

        satelite_var.set('Auger')

        for transition in the_aug_dictionary:
            if the_aug_dictionary[transition]["selected_state"]:
                dict_updater(transition)

        satelite_var.set(original)

        sim.quit()  # stops mainloop
        sim.destroy()  # this is necessary on Windows to prevent
        # Fatal Python Error: PyEval_RestoreThread: NULL tstate

    def restarter():
        original = satelite_var.get()

        satelite_var.set('Diagram')

        for transition in the_dictionary:
            if the_dictionary[transition]["selected_state"]:
                dict_updater(transition)

        satelite_var.set('Auger')

        for transition in the_aug_dictionary:
            if the_aug_dictionary[transition]["selected_state"]:
                dict_updater(transition)

        satelite_var.set(original)

        sim.quit()  # stops mainloop
        sim.destroy()
        parent.destroy()
        main()  # this is necessary on Windows to prevent
        # Fatal Python Error: PyEval_RestoreThread: NULL tstate

    def load():  # funcao que muda o nome da variavel correspondente ao ficheiro experimental
        fname = askopenfilename(filetypes=(
            ("Spectra files", "*.csv *.txt"), ("All files", "*.*")))
        # Muda o nome da variavel loadvar para a string correspondente ao path do ficheiro seleccionado
        loadvar.set(fname)

    def load_effic_file():
        effic_fname = askopenfilename(filetypes=(
            ("Efficiency files", "*.csv"), ("All files", "*.*")))
        effic_var.set(effic_fname)

    def selected(event):
        text_T = drop_menu.get()  # Lê Texto da box com as transições
        # Faz update do dicionário com a transição lida
        dict_updater(text_T)
        to_print = ''  # Texto a imprimir no label com as transições selecionadas

        if satelite_var.get() != 'Auger':
            # Se a transição estiver selecionada:
            if the_dictionary[text_T]["selected_state"]:
                # é adicionada à lista de transições que vai para o label
                transition_list.append(text_T)
            # Se for descelecionada
            elif not the_dictionary[text_T]["selected_state"]:
                # é removida da lista que vai para o label
                transition_list.remove(text_T)
        else:
            # Se a transição estiver selecionada:
            if the_aug_dictionary[text_T]["selected_state"]:
                # é adicionada à lista de transições que vai para o label
                transition_list.append(text_T)
            # Se for descelecionada
            elif not the_aug_dictionary[text_T]["selected_state"]:
                # é removida da lista que vai para o label
                transition_list.remove(text_T)

        # Este for serve para colocar as vírgulas entre as transições que vão para o label
        for a, b in enumerate(transition_list):
            if len(transition_list) == a + 1:
                to_print += str(b) + ' '
            else:
                to_print += str(b) + ', '
        # Definimos o novo label
        label_text.set('Selected Transitions: ' + to_print)

    def enter_function(event):
        plot_stick(a)

    def reset_limits():
        number_points.set(500)
        x_max.set('Auto')
        x_min.set('Auto')

    def update_transition_dropdown():
        global transition_list

        if satelite_var.get() != 'Auger':
            drop_menu['values'] = [
                transition for transition in the_dictionary]
            if not any([the_dictionary[transition]["selected_state"] for transition in the_dictionary]):
                transition_list = []
                label_text.set('Select a Transition: ')
                drop_menu.set('Transitions:')
                for transition in the_aug_dictionary:
                    the_aug_dictionary[transition]["selected_state"] = False
        else:
            drop_menu['values'] = [
                transition for transition in the_aug_dictionary]
            if not any([the_aug_dictionary[transition]["selected_state"] for transition in the_aug_dictionary]):
                transition_list = []
                label_text.set('Select a Transition: ')
                drop_menu.set('Transitions:')
                for transition in the_dictionary:
                    the_dictionary[transition]["selected_state"] = False

    def configureCSMix():
        mixer = Toplevel(sim)
        mixer.title("Charge State Mixer")
        mixer.grab_set()  # Make this window the only interactable one until its closed

        mixer.geometry("700x300")

        import re

        def check_num(newval):
            return re.match('^(?:[0-9]*[.]?[0-9]*)$', newval) is not None
        check_num_wrapper = (mixer.register(check_num), '%P')

        # -------------------------------------------------------------------------------------------------------------------------------------------
        # RADIATIVE

        slidersRad = []
        CS_labelsRad = []
        PCS_order = [int(cs.split('intensity_')[1].split('.out')[0].split(
            '+')[-1]) for cs in radiative_files if '+' in cs]
        NCS_order = [int(cs.split('intensity_')[1].split('.out')[0].split(
            '-')[-1]) for cs in radiative_files if '+' not in cs]

        CS_mixEntriesRad = []

        labelRad = ttk.Label(
            mixer, text="Charge States With Radiative Transitions For Selected Atom:")
        labelRad.grid(column=0, row=0, columnspan=len(
            radiative_files), pady=40)

        if len(data.variables.PCS_radMixValues) == 0:
            for cs in radiative_files:
                if '+' in cs:
                    data.variables.PCS_radMixValues.append(StringVar())
                    CS_mixEntriesRad.append(ttk.Entry(
                        mixer, textvariable=data.variables.PCS_radMixValues[-1], validate='key', validatecommand=check_num_wrapper))
                    slidersRad.append(ttk.Scale(
                        mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=data.variables.PCS_radMixValues[-1]))
                    CS_labelsRad.append(
                        ttk.Label(mixer, text=cs.split('intensity_')[1].split('.out')[0]))
                    slidersRad[-1].set(0.0)
        else:
            i = 0
            for cs in radiative_files:
                if '+' in cs:
                    CS_mixEntriesRad.append(ttk.Entry(
                        mixer, textvariable=data.variables.PCS_radMixValues[i], validate='key', validatecommand=check_num_wrapper))
                    slidersRad.append(ttk.Scale(
                        mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=data.variables.PCS_radMixValues[i]))
                    CS_labelsRad.append(
                        ttk.Label(mixer, text=cs.split('intensity_')[1].split('.out')[0]))

                    i += 1

        if len(data.variables.NCS_radMixValues) == 0:
            for cs in radiative_files:
                if '+' not in cs:
                    data.variables.NCS_radMixValues.append(StringVar())
                    CS_mixEntriesRad.append(ttk.Entry(
                        mixer, textvariable=data.variables.NCS_radMixValues[-1], validate='key', validatecommand=check_num_wrapper))
                    slidersRad.append(ttk.Scale(
                        mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=data.variables.NCS_radMixValues[-1]))
                    CS_labelsRad.append(
                        ttk.Label(mixer, text=cs.split('intensity_')[1].split('.out')[0]))
                    slidersRad[-1].set(0.0)
        else:
            i = 0
            for cs in radiative_files:
                if '+' not in cs:
                    CS_mixEntriesRad.append(ttk.Entry(
                        mixer, textvariable=data.variables.NCS_radMixValues[i], validate='key', validatecommand=check_num_wrapper))
                    slidersRad.append(ttk.Scale(
                        mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=data.variables.NCS_radMixValues[i]))
                    CS_labelsRad.append(
                        ttk.Label(mixer, text=cs.split('intensity_')[1].split('.out')[0]))

                    i += 1

        initial_PCS_Order = PCS_order.copy()
        initial_NCS_Order = NCS_order.copy()
        colIndex = 0
        while len(NCS_order) > 0:
            idx = initial_NCS_Order.index(min(NCS_order))

            CS_labelsRad[idx].grid(
                column=colIndex, row=1, sticky=(N), pady=5)
            slidersRad[idx].grid(
                column=colIndex, row=2, sticky=(N, S), pady=5)
            CS_mixEntriesRad[idx].grid(
                column=colIndex, row=3, sticky=(W, E), padx=5)

            mixer.columnconfigure(colIndex, weight=1)

            colIndex += 1
            del NCS_order[NCS_order.index(min(NCS_order))]

        while len(PCS_order) > 0:
            idx = initial_PCS_Order.index(min(PCS_order))

            CS_labelsRad[idx].grid(
                column=colIndex, row=1, sticky=(N), pady=5)
            slidersRad[idx].grid(
                column=colIndex, row=2, sticky=(N, S), pady=5)
            CS_mixEntriesRad[idx].grid(
                column=colIndex, row=3, sticky=(W, E), padx=5)

            mixer.columnconfigure(colIndex, weight=1)

            colIndex += 1
            del PCS_order[PCS_order.index(min(PCS_order))]

        mixer.rowconfigure(2, weight=1)

        # ------------------------------------------------------------------------------------------------------------------------------------
        # AUGER

        if len(auger_files) > 0:
            mixer.geometry("800x600")

            slidersAug = []
            CS_labelsAug = []
            PCS_order = [int(cs.split('augrate_')[1].split('.out')[0].split(
                '+')[-1]) for cs in auger_files if '+' in cs]
            NCS_order = [int(cs.split('augrate_')[1].split('.out')[0].split(
                '-')[-1]) for cs in auger_files if '+' not in cs]

            CS_mixEntriesAug = []

            labelAug = ttk.Label(
                mixer, text="Charge States With Auger Transitions For Selected Atom:")
            labelAug.grid(column=0, row=4, columnspan=len(
                radiative_files), pady=40)

            if len(data.variables.PCS_augMixValues) == 0:
                for cs in auger_files:
                    if '+' in cs:
                        data.variables.PCS_augMixValues.append(StringVar())
                        CS_mixEntriesAug.append(ttk.Entry(
                            mixer, textvariable=data.variables.PCS_augMixValues[-1], validate='key', validatecommand=check_num_wrapper))
                        slidersAug.append(ttk.Scale(
                            mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=data.variables.PCS_augMixValues[-1]))
                        CS_labelsAug.append(
                            ttk.Label(mixer, text=cs.split('augrate_')[1].split('.out')[0]))
                        slidersAug[-1].set(0.0)
            else:
                i = 0
                for cs in auger_files:
                    if '+' in cs:
                        CS_mixEntriesAug.append(ttk.Entry(
                            mixer, textvariable=data.variables.PCS_augMixValues[i], validate='key', validatecommand=check_num_wrapper))
                        slidersAug.append(ttk.Scale(
                            mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=data.variables.PCS_augMixValues[i]))
                        CS_labelsAug.append(
                            ttk.Label(mixer, text=cs.split('augrate_')[1].split('.out')[0]))

                        i += 1

            if len(data.variables.NCS_augMixValues) == 0:
                for cs in auger_files:
                    if '+' not in cs:
                        data.variables.NCS_augMixValues.append(StringVar())
                        CS_mixEntriesAug.append(ttk.Entry(
                            mixer, textvariable=data.variables.NCS_augMixValues[-1], validate='key', validatecommand=check_num_wrapper))
                        slidersAug.append(ttk.Scale(
                            mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=data.variables.NCS_augMixValues[-1]))
                        CS_labelsAug.append(
                            ttk.Label(mixer, text=cs.split('augrate_')[1].split('.out')[0]))
                        slidersAug[-1].set(0.0)
            else:
                i = 0
                for cs in auger_files:
                    if '+' not in cs:
                        CS_mixEntriesAug.append(ttk.Entry(
                            mixer, textvariable=data.variables.NCS_augMixValues[i], validate='key', validatecommand=check_num_wrapper))
                        slidersAug.append(ttk.Scale(
                            mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=data.variables.NCS_augMixValues[i]))
                        CS_labelsAug.append(
                            ttk.Label(mixer, text=cs.split('augrate_')[1].split('.out')[0]))

                        i += 1

            initial_PCS_Order = PCS_order.copy()
            initial_NCS_Order = NCS_order.copy()
            colIndex = 0
            while len(NCS_order) > 0:
                idx = initial_NCS_Order.index(min(NCS_order))

                CS_labelsAug[idx].grid(
                    column=colIndex, row=5, sticky=(N), pady=5)
                slidersAug[idx].grid(
                    column=colIndex, row=6, sticky=(N, S), pady=5)
                CS_mixEntriesAug[idx].grid(
                    column=colIndex, row=7, sticky=(W, E), padx=5)

                mixer.columnconfigure(colIndex, weight=1)

                colIndex += 1
                del NCS_order[NCS_order.index(min(NCS_order))]

            while len(PCS_order) > 0:
                idx = initial_PCS_Order.index(min(PCS_order))

                CS_labelsAug[idx].grid(
                    column=colIndex, row=5, sticky=(N), pady=5)
                slidersAug[idx].grid(
                    column=colIndex, row=6, sticky=(N, S), pady=5)
                CS_mixEntriesAug[idx].grid(
                    column=colIndex, row=7, sticky=(W, E), padx=5)

                mixer.columnconfigure(colIndex, weight=1)

                colIndex += 1
                del PCS_order[PCS_order.index(min(PCS_order))]

            mixer.rowconfigure(6, weight=1)

        # ------------------------------------------------------------------------------------------------------------------------------------
        # Ion Population slider

        Ion_Populations = {}

        combined_x = []
        combined_y = []

        for i, cs in enumerate(ionpopdata[0]):
            Ion_Populations[cs + '_x'] = []
            Ion_Populations[cs + '_y'] = []

            col = i * 2

            for vals in ionpopdata[1:]:
                if '---' not in vals[col]:
                    combined_x.append(float(vals[col]))
                    combined_y.append(float(vals[col + 1]))
                    if float(vals[col]) not in Ion_Populations[cs + '_x']:
                        Ion_Populations[cs + '_x'].append(float(vals[col]))
                        Ion_Populations[cs +
                                        '_y'].append(float(vals[col + 1]))

        y_max = max(combined_y)
        for cs in ionpopdata[0]:
            Ion_Populations[cs + '_y'] = [pop * 100 /
                                          y_max for pop in Ion_Populations[cs + '_y']]

        Ion_Population_Functions = {}
        # linear interpolation because of "corners" in the distribution functions
        for cs in ionpopdata[0]:
            order = np.argsort(Ion_Populations[cs + '_x'])
            Ion_Population_Functions[cs] = interp1d(np.array(
                Ion_Populations[cs + '_x'])[order], np.array(Ion_Populations[cs + '_y'])[order], kind='linear')

        combined_x = list(set(combined_x))

        temperature_max = max(combined_x)
        temperature_min = min(combined_x)

        if len(auger_files) > 0:
            fig_row = 7
        else:
            fig_row = 4

        # Figura onde o gráfico vai ser desenhado
        # canvas para o gráfico do espectro
        f = Figure(figsize=(10, 5), dpi=100)
        # plt.style.use('ggplot') Estilo para os plots
        a = f.add_subplot(111)  # zona onde estara o gráfico
        a.set_xlabel('Temperature (K)')
        a.set_ylabel('Population')
        # ---------------------------------------------------------------------------------------------------------------
        # Frames onde se vão pôr a figura e os labels e botões e etc
        figure_frame = Frame(mixer, relief=GROOVE)  # frame para o gráfico

        figure_frame.grid(column=0, row=fig_row, columnspan=max(
            len(radiative_files), len(auger_files)), pady=20)

        canvas = FigureCanvasTkAgg(f, master=figure_frame)
        canvas.get_tk_widget().pack(fill=BOTH, expand=1)

        mixer.rowconfigure(fig_row, weight=1)

        temperature = StringVar()
        temperature.set(str(temperature_min))
        prev_line = a.axvline(x=float(temperature.get()), color='b')

        def update_temp_line(event, arg1, arg2):
            prev_line.set_xdata(float(temperature.get()))

            f.canvas.draw()
            f.canvas.flush_events()

            for cs in Ion_Population_Functions:
                if len(data.variables.PCS_radMixValues) > 0:
                    i = 0
                    for cs_file in radiative_files:
                        if cs in cs_file:
                            try:
                                data.variables.PCS_radMixValues[i].set(
                                    str(Ion_Population_Functions[cs](float(temperature.get()))))
                            except:
                                data.variables.PCS_radMixValues[i].set("0.0")

                            break

                        if '+' in cs:
                            i += 1

                if len(data.variables.NCS_radMixValues) > 0:
                    i = 0
                    for cs_file in radiative_files:
                        if cs in cs_file:
                            try:
                                data.variables.NCS_radMixValues[i].set(
                                    str(Ion_Population_Functions[cs](float(temperature.get()))))
                            except:
                                data.variables.NCS_radMixValues[i].set("0.0")

                            break

                        if '+' not in cs:
                            i += 1

            if len(auger_files) > 0:
                for cs in Ion_Population_Functions:
                    if len(data.variables.PCS_augMixValues) > 0:
                        i = 0
                        for cs_file in auger_files:
                            if cs in cs_file:
                                try:
                                    data.variables.PCS_augMixValues[i].set(
                                        str(Ion_Population_Functions[cs](float(temperature.get()))))
                                except:
                                    data.variables.PCS_augMixValues[i].set("0.0")

                                break

                            if '+' in cs:
                                i += 1

                    if len(data.variables.NCS_augMixValues) > 0:
                        i = 0
                        for cs_file in auger_files:
                            if cs in cs_file:
                                try:
                                    data.variables.NCS_augMixValues[i].set(
                                        str(Ion_Population_Functions[cs](float(temperature.get()))))
                                except:
                                    data.variables.NCS_augMixValues[i].set("0.0")

                                break

                            if '+' not in cs:
                                i += 1

        temperature.trace_add("write", update_temp_line)
        temp_slider = ttk.Scale(mixer, orient=HORIZONTAL, length=200,
                                from_=temperature_min, to=temperature_max, variable=temperature)
        temp_entry = ttk.Entry(
            mixer, textvariable=temperature, validate='key', validatecommand=check_num_wrapper)
        temp_slider.grid(column=0, row=fig_row + 1, columnspan=max(
            len(radiative_files), len(auger_files)) - 1, sticky=(W, E), padx=10, pady=20)
        temp_entry.grid(column=max(len(radiative_files), len(
            auger_files)) - 1, row=fig_row + 1, sticky=(W, E), padx=5)

        mixer.rowconfigure(fig_row + 1, weight=1)

        for cs in ionpopdata[0]:
            x_min = min(Ion_Populations[cs + '_x'])
            x_max = max(Ion_Populations[cs + '_x'])

            temp_new = np.arange(x_min, x_max, (x_max - x_min) / 100)
            pop_new = Ion_Population_Functions[cs](temp_new)

            a.plot(temp_new, pop_new, label=cs)

        a.legend()

    # Botão para correr a calculate quando se clica no enter
    sim.bind('<Return>', enter_function)
    # ---------------------------------------------------------------------------------------------------------------
    # DropList das transições, Labels e botão calculate a apresentar na janela
    drop_menu = ttk.Combobox(buttons_frame, value=[
                             transition for transition in the_dictionary], height=5, width=10)
    drop_menu.set('Transitions:')
    drop_menu.bind("<<ComboboxSelected>>", selected)
    drop_menu.grid(row=0, column=0)

    # Min Max e Nº Pontos
    ttk.Label(buttons_frame2, text="Points").pack(side=LEFT)
    points = ttk.Entry(buttons_frame2, width=7,
                       textvariable=number_points).pack(side=LEFT)
    ttk.Label(buttons_frame2, text="x Max").pack(side=LEFT)
    max_x = ttk.Entry(buttons_frame2, width=7,
                      textvariable=x_max).pack(side=LEFT)
    ttk.Label(buttons_frame2, text="x Min").pack(side=LEFT)
    min_x = ttk.Entry(buttons_frame2, width=7,
                      textvariable=x_min).pack(side=LEFT)
    ttk.Button(master=buttons_frame2, text="Reset",
               command=lambda: reset_limits()).pack(side=LEFT, padx=(30, 0))

    # Res, Offsets e Calculate
    # , font = ('Sans','10','bold'))  #definicoes botao "calculate"
    ttk.Style().configure('red/black.TButton', foreground='red', background='black')
    ttk.Button(master=buttons_frame3, text="Calculate", command=lambda: plot_stick(
        a), style='red/black.TButton').pack(side=RIGHT, padx=(30, 0))
    # yoffset
    res_entry = ttk.Entry(buttons_frame3, width=7,
                          textvariable=yoffset).pack(side=RIGHT)
    ttk.Label(buttons_frame3, text="y Offset").pack(side=RIGHT)
    # En. Offset
    res_entry = ttk.Entry(buttons_frame3, width=7, textvariable=energy_offset).pack(
        side=RIGHT, padx=(0, 30))
    ttk.Label(buttons_frame3, text="En. offset (eV)").pack(side=RIGHT)
    # Energy Resolution
    ttk.Label(buttons_frame3, text="Experimental Resolution (eV)").pack(
        side=LEFT)
    res_entry = ttk.Entry(buttons_frame3, width=7,
                          textvariable=exp_resolution).pack(side=LEFT)

    # Barra progresso
    progressbar = ttk.Progressbar(
        buttons_frame4, variable=progress_var, maximum=100)
    progressbar.pack(fill=X, expand=1)
    # ---------------------------------------------------------------------------------------------------------------
    # Menus
    my_menu = Menu(sim)
    sim.config(menu=my_menu)
    options_menu = Menu(my_menu, tearoff=0)
    stick_plot_menu = Menu(my_menu, tearoff=0)
    transition_type_menu = Menu(my_menu, tearoff=0)
    fit_type_menu = Menu(my_menu, tearoff=0)
    norm_menu = Menu(my_menu, tearoff=0)
    exc_mech_menu = Menu(my_menu, tearoff=0)
    # ---------------------------------------------------------------------------------------------------------------
    my_menu.add_cascade(label="Options", menu=options_menu)
    options_menu.add_checkbutton(
        label='Show Total Y', variable=totalvar, onvalue='Total', offvalue='No')
    options_menu.add_separator()
    options_menu.add_checkbutton(
        label='Log Scale Y Axis', variable=yscale_log, onvalue='Ylog', offvalue='No')
    options_menu.add_checkbutton(
        label='Log Scale X Axis', variable=xscale_log, onvalue='Xlog', offvalue='No')
    options_menu.add_separator()
    options_menu.add_command(
        label="Load Experimental Spectrum", command=load)
    options_menu.add_checkbutton(
        label='Perform Autofit', variable=autofitvar, onvalue='Yes', offvalue='No')
    options_menu.add_separator()
    options_menu.add_checkbutton(
        label="Import Detector Efficiency", command=load_effic_file)
    options_menu.add_separator()
    options_menu.add_command(label="Export Spectrum", command=lambda: write_to_xls(satelite_var.get(), xfinal, energy_offset.get(), yoffset.get(), exp_x, exp_y, residues_graph, radiative_files, auger_files, label1, time_of_click))
    options_menu.add_separator()
    options_menu.add_command(label="Choose New Element", command=restarter)
    options_menu.add_command(label="Quit", command=_quit)
    # ---------------------------------------------------------------------------------------------------------------
    my_menu.add_cascade(label="Spectrum Type", menu=stick_plot_menu)
    choice_var = StringVar(value='Simulation')
    stick_plot_menu.add_checkbutton(
        label='Stick', variable=choice_var, onvalue='Stick', offvalue='')
    stick_plot_menu.add_checkbutton(
        label='Simulation', variable=choice_var, onvalue='Simulation', offvalue='')
    stick_plot_menu.add_checkbutton(label='CS Mixture: Stick', variable=choice_var,
                                    onvalue='M_Stick', offvalue='', command=configureCSMix, state='disabled')
    stick_plot_menu.add_checkbutton(label='CS Mixture: Simulation', variable=choice_var,
                                    onvalue='M_Simulation', offvalue='', command=configureCSMix, state='disabled')
    if CS_exists:
        stick_plot_menu.entryconfigure(2, state=NORMAL)
        # Good TK documentation: https://tkdocs.com/tutorial/menus.html
        stick_plot_menu.entryconfigure(3, state=NORMAL)
    # ---------------------------------------------------------------------------------------------------------------
    my_menu.add_cascade(label="Transition Type", menu=transition_type_menu)
    satelite_var = StringVar(value='Diagram')
    transition_type_menu.add_checkbutton(
        label='Diagram', variable=satelite_var, onvalue='Diagram', offvalue='', command=update_transition_dropdown)
    transition_type_menu.add_checkbutton(
        label='Satellites', variable=satelite_var, onvalue='Satellites', offvalue='', command=update_transition_dropdown)
    transition_type_menu.add_checkbutton(label='Diagram + Satellites', variable=satelite_var,
                                         onvalue='Diagram + Satellites', offvalue='', command=update_transition_dropdown)
    transition_type_menu.add_checkbutton(
        label='Auger', variable=satelite_var, onvalue='Auger', offvalue='', command=update_transition_dropdown)
    # ---------------------------------------------------------------------------------------------------------------
    my_menu.add_cascade(label="Fit Type", menu=fit_type_menu)
    type_var = StringVar(value='Lorentzian')
    fit_type_menu.add_checkbutton(
        label='Voigt', variable=type_var, onvalue='Voigt', offvalue='')
    fit_type_menu.add_checkbutton(
        label='Lorentzian', variable=type_var, onvalue='Lorentzian', offvalue='')
    fit_type_menu.add_checkbutton(
        label='Gaussian', variable=type_var, onvalue='Gaussian', offvalue='')
    # ---------------------------------------------------------------------------------------------------------------
    my_menu.add_cascade(label="Normalization Options", menu=norm_menu)
    norm_menu.add_checkbutton(label='to Experimental Maximum',
                              variable=normalizevar, onvalue='ExpMax', offvalue='No')
    norm_menu.add_checkbutton(
        label='to Unity', variable=normalizevar, onvalue='One', offvalue='No')
    # ---------------------------------------------------------------------------------------------------------------
    # Apagar o state para tornar funcional
    my_menu.add_cascade(label="Excitation Mechanism",
                        menu=exc_mech_menu, state="disabled")
    exc_mech_var = StringVar(value='')
    exc_mech_menu.add_checkbutton(
        label='Nuclear Electron Capture', variable=exc_mech_var, onvalue='NEC', offvalue='')
    exc_mech_menu.add_checkbutton(
        label='Photoionization', variable=exc_mech_var, onvalue='PIon', offvalue='')
    exc_mech_menu.add_checkbutton(
        label='Electron Impact Ionization', variable=exc_mech_var, onvalue='EII', offvalue='')
    # ---------------------------------------------------------------------------------------------------------------
    sim.mainloop()