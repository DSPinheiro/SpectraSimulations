from tkinter import *
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib import gridspec
from matplotlib.backend_bases import key_press_handler

from data.variables import labeldict, the_dictionary, the_aug_dictionary
import data.variables as generalVars

from utils.fileIO import load, load_effic_file, loadExp

from utils.functions import y_calculator, func2min, stem_ploter, plot_stick


import numpy as np
from scipy.interpolate import interp1d

parent = None

totalvar = None
yscale_log = None
xscale_log = None
autofitvar = None
normalizevar = None
loadvar = None
effic_var = None
exp_resolution = None
yoffset = None
energy_offset = None
number_points = None
x_max = None
x_min = None
progress_var = None
transition_list = []
label_text = None
trans_lable = None

drop_menu = None
points = None
max_x = None
min_x = None
res_entry = None
progressbar = None

satelite_var = None
choice_var = None
type_var = None
exc_mech_var = None


_a = None
_sim = None
_f = None

def destroy(window):
    window.destroy()

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
    sim.destroy()  # this is necessary on Windows to prevent fatal Python Error: PyEval_RestoreThread: NULL tstate


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
    main()  # this is necessary on Windows to prevent fatal Python Error: PyEval_RestoreThread: NULL tstate


def on_key_event(event):
    print('you pressed %s' % event.key)
    key_press_handler(event, canvas, toolbar)


def enter_function(event):
    plot_stick(_sim, _f, _a)


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


def reset_limits():
    global number_points, x_max, x_min
    
    number_points.set(500)
    x_max.set('Auto')
    x_min.set('Auto')


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


def update_transition_dropdown():
    global transition_list
    
    if satelite_var.get() != 'Auger':
        drop_menu['values'] = [transition for transition in the_dictionary]
        if not any([the_dictionary[transition]["selected_state"] for transition in the_dictionary]):
            label_text.set('Select a Transition: ')
            drop_menu.set('Transitions:')
            for transition in the_aug_dictionary:
                the_aug_dictionary[transition]["selected_state"] = False
    else:
        drop_menu['values'] = [transition for transition in the_aug_dictionary]
        if not any([the_aug_dictionary[transition]["selected_state"] for transition in the_aug_dictionary]):
            label_text.set('Select a Transition: ')
            drop_menu.set('Transitions:')
            for transition in the_dictionary:
                the_dictionary[transition]["selected_state"] = False



def configureSimuPlot(parent):
    global _a, _f
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

    _a = a
    _f = f
    
    return sim, panel_1, f, a, figure_frame, canvas


def configureButtonArea(sim, canvas):
    panel_2 = PanedWindow(sim, orient=VERTICAL)
    panel_2.pack(fill=X, expand=0)

    toolbar_frame = Frame(panel_2, bd=1, relief=GROOVE)
    panel_2.add(toolbar_frame)
    toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)

    full_frame = Frame(panel_2, relief=GROOVE)  # Frame transições
    panel_2.add(full_frame)
    buttons_frame = Frame(full_frame, bd=1, relief=GROOVE)  # Frame transições
    buttons_frame.pack(fill=BOTH, expand=1)
    # Max, min & Points Frame
    buttons_frame2 = Frame(full_frame, bd=1, relief=GROOVE)
    buttons_frame2.pack(fill=BOTH, expand=1)
    # Frame  yoffset, Energy offset e Calculate
    buttons_frame3 = Frame(full_frame, bd=1, relief=GROOVE)
    buttons_frame3.pack(fill=BOTH, expand=1)
    buttons_frame4 = Frame(full_frame)  # Frame Barra Progresso
    buttons_frame4.pack(fill=BOTH, expand=1)

    return panel_2, toolbar_frame, toolbar, full_frame, buttons_frame, buttons_frame2, buttons_frame3, buttons_frame4


def setupVars(p):
    global parent, totalvar, yscale_log, xscale_log, autofitvar, normalizevar, loadvar, effic_var
    global exp_resolution, yoffset, energy_offset, number_points, x_max, x_min, progress_var, label_text
    global satelite_var, choice_var, type_var, exc_mech_var
    
    parent = p
    # ---------------------------------------------------------------------------------------------------------------
    # Variáveis
    # Variável que define se apresentamos o ytot(soma de todas as riscas) no gráfico
    totalvar = StringVar(master = parent)
    # inicializamos Total como não, porque só se apresenta se o utilizador escolher manualmente
    totalvar.set('No')
    # Variável que define se o eixo y é apresentado com escala logaritmica ou não
    yscale_log = StringVar(master = parent)
    # Inicializamos a No porque só  se apresenta assim se o utilizador escolher manualmente
    yscale_log.set('No')
    # Variável que define se o eixo y é apresentado com escala logaritmica ou não
    xscale_log = StringVar(master = parent)
    # Inicializamos a No porque só  se apresenta assim se o utilizador escolher manualmente
    xscale_log.set('No')
    autofitvar = StringVar(master = parent)  # Variável que define se o fit se faz automáticamente ou não
    # Inicializamos a No porque só faz fit automático se o utilizador quiser
    autofitvar.set('No')
    normalizevar = StringVar(master = parent)  # Variável que define como se normalizam os gráficos (3 opções até agora: não normalizar, normalizar à unidade, ou ao máximo do espectro experimental)
    # inicializamos Normalize a no, porque só se normaliza se o utilizador escolher
    normalizevar.set('No')
    loadvar = StringVar(master = parent)  # Variável que define se se carrega um expectro experimental. A string, caso se queira carregar o espectro, muda para o path do ficheiro do espectro
    # inicializamos Load a no, porque só se carrega ficheiro se o utilizador escolher
    loadvar.set('No')
    effic_var = StringVar(master = parent)
    effic_var.set("No")

    # Float correspondente a resolucao experimental
    exp_resolution = DoubleVar(master = parent, value=1.0)
    # Float correspondente ao fundo experimental
    yoffset = DoubleVar(master = parent, value=0.0)
    # Float correspondente a resolucao experimental
    energy_offset = DoubleVar(master = parent, value=0.0)
    # Numero de pontos a plotar na simulação
    number_points = IntVar(master = parent, value=500)
    x_max = StringVar(master = parent)  # Controlo do x Máximo a entrar no gráfico
    x_max.set('Auto')
    x_min = StringVar(master = parent)  # Controlo do x Mí­nimo a entrar no gráfico
    x_min.set('Auto')
    progress_var = DoubleVar(master = parent)  # Float que da a percentagem de progresso
    
    label_text = StringVar(master = parent)  # Texto com as transições selecionadas a apresentar no ecrã
    
    satelite_var = StringVar(value='Diagram')
    
    choice_var = StringVar(value='Simulation')
    
    type_var = StringVar(value='Lorentzian')
    
    exc_mech_var = StringVar(value='')
 


def setupButtonArea(buttons_frame, buttons_frame2, buttons_frame3, buttons_frame4):
    global trans_lable, drop_menu, points, max_x, min_x, res_entry, progressbar, transition_list
    
    # Antes de se selecionar alguma transição aparece isto
    label_text.set('Select a Transition: ')
    trans_lable = Label(buttons_frame, textvariable=label_text).grid(row=0, column=1)
    
    
    # DropList das transições, Labels e botão calculate a apresentar na janela
    drop_menu = ttk.Combobox(buttons_frame, value=[transition for transition in the_dictionary], height=5, width=10)
    drop_menu.set('Transitions:')
    drop_menu.bind("<<ComboboxSelected>>", selected)
    drop_menu.grid(row=0, column=0)
    
    # Min Max e Nº Pontos
    ttk.Label(buttons_frame2, text="Points").pack(side=LEFT)
    points = ttk.Entry(buttons_frame2, width=7, textvariable=number_points).pack(side=LEFT)
    ttk.Label(buttons_frame2, text="x Max").pack(side=LEFT)
    max_x = ttk.Entry(buttons_frame2, width=7, textvariable=x_max).pack(side=LEFT)
    ttk.Label(buttons_frame2, text="x Min").pack(side=LEFT)
    min_x = ttk.Entry(buttons_frame2, width=7, textvariable=x_min).pack(side=LEFT)
    ttk.Button(master=buttons_frame2, text="Reset", command=lambda: reset_limits()).pack(side=LEFT, padx=(30, 0))

    # Res, Offsets e Calculate
    # , font = ('Sans','10','bold'))  #definicoes botao "calculate"
    ttk.Style().configure('red/black.TButton', foreground='red', background='black')
    ttk.Button(master=buttons_frame3, text="Calculate", command=lambda: plot_stick(_sim, _f, _a), style='red/black.TButton').pack(side=RIGHT, padx=(30, 0))
    # yoffset
    res_entry = ttk.Entry(buttons_frame3, width=7, textvariable=yoffset).pack(side=RIGHT)
    ttk.Label(buttons_frame3, text="y Offset").pack(side=RIGHT)
    # En. Offset
    res_entry = ttk.Entry(buttons_frame3, width=7, textvariable=energy_offset).pack(side=RIGHT, padx=(0, 30))
    ttk.Label(buttons_frame3, text="En. offset (eV)").pack(side=RIGHT)
    # Energy Resolution
    ttk.Label(buttons_frame3, text="Experimental Resolution (eV)").pack(side=LEFT)
    res_entry = ttk.Entry(buttons_frame3, width=7, textvariable=exp_resolution).pack(side=LEFT)

    # Barra progresso
    progressbar = ttk.Progressbar(buttons_frame4, variable=progress_var, maximum=100)
    progressbar.pack(fill=X, expand=1)


def setupMenus(sim, CS_exists):
    global totalvar, yscale_log, xscale_log, autofitvar, energy_offset, yoffset, normalizevar, satelite_var, choice_var, type_var, exc_mech_var, _sim
    global loadvar, effic_var
    
    _sim = sim
    
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
    options_menu.add_checkbutton(label='Show Total Y', variable=totalvar, onvalue='Total', offvalue='No')
    options_menu.add_separator()
    options_menu.add_checkbutton(label='Log Scale Y Axis', variable=yscale_log, onvalue='Ylog', offvalue='No')
    options_menu.add_checkbutton(label='Log Scale X Axis', variable=xscale_log, onvalue='Xlog', offvalue='No')
    options_menu.add_separator()
    options_menu.add_command(label="Load Experimental Spectrum", command=lambda: load(loadvar))
    options_menu.add_checkbutton(label='Perform Autofit', variable=autofitvar, onvalue='Yes', offvalue='No')
    options_menu.add_separator()
    options_menu.add_checkbutton(label="Import Detector Efficiency", command=lambda: load_effic_file(effic_var))
    options_menu.add_separator()
    options_menu.add_command(label="Export Spectrum", command=lambda: write_to_xls(satelite_var.get(), xfinal, energy_offset.get(), yoffset.get(), exp_x, exp_y, residues_graph, radiative_files, auger_files, generalVars.label1, time_of_click))
    options_menu.add_separator()
    options_menu.add_command(label="Choose New Element", command=restarter)
    options_menu.add_command(label="Quit", command=_quit)
    # ---------------------------------------------------------------------------------------------------------------
    my_menu.add_cascade(label="Spectrum Type", menu=stick_plot_menu)
    stick_plot_menu.add_checkbutton(label='Stick', variable=choice_var, onvalue='Stick', offvalue='')
    stick_plot_menu.add_checkbutton(label='Simulation', variable=choice_var, onvalue='Simulation', offvalue='')
    stick_plot_menu.add_checkbutton(label='CS Mixture: Stick', variable=choice_var, onvalue='M_Stick', offvalue='', command=lambda: configureCSMix(sim), state='disabled')
    stick_plot_menu.add_checkbutton(label='CS Mixture: Simulation', variable=choice_var, onvalue='M_Simulation', offvalue='', command=lambda: configureCSMix(sim), state='disabled')
    if CS_exists:
        stick_plot_menu.entryconfigure(2, state=NORMAL)
        # Good TK documentation: https://tkdocs.com/tutorial/menus.html
        stick_plot_menu.entryconfigure(3, state=NORMAL)
    # ---------------------------------------------------------------------------------------------------------------
    my_menu.add_cascade(label="Transition Type", menu=transition_type_menu)
    
    transition_type_menu.add_checkbutton(label='Diagram', variable=satelite_var, onvalue='Diagram', offvalue='', command=update_transition_dropdown)
    transition_type_menu.add_checkbutton(label='Satellites', variable=satelite_var, onvalue='Satellites', offvalue='', command=update_transition_dropdown)
    transition_type_menu.add_checkbutton(label='Diagram + Satellites', variable=satelite_var, onvalue='Diagram + Satellites', offvalue='', command=update_transition_dropdown)
    transition_type_menu.add_checkbutton(label='Auger', variable=satelite_var, onvalue='Auger', offvalue='', command=update_transition_dropdown)
    # ---------------------------------------------------------------------------------------------------------------
    my_menu.add_cascade(label="Fit Type", menu=fit_type_menu)
    fit_type_menu.add_checkbutton(label='Voigt', variable=type_var, onvalue='Voigt', offvalue='')
    fit_type_menu.add_checkbutton(label='Lorentzian', variable=type_var, onvalue='Lorentzian', offvalue='')
    fit_type_menu.add_checkbutton(label='Gaussian', variable=type_var, onvalue='Gaussian', offvalue='')
    # ---------------------------------------------------------------------------------------------------------------
    my_menu.add_cascade(label="Normalization Options", menu=norm_menu)
    norm_menu.add_checkbutton(label='to Experimental Maximum', variable=normalizevar, onvalue='ExpMax', offvalue='No')
    norm_menu.add_checkbutton(label='to Unity', variable=normalizevar, onvalue='One', offvalue='No')
    # ---------------------------------------------------------------------------------------------------------------
    # Apagar o state para tornar funcional
    my_menu.add_cascade(label="Excitation Mechanism", menu=exc_mech_menu, state="disabled")
    exc_mech_menu.add_checkbutton(label='Nuclear Electron Capture', variable=exc_mech_var, onvalue='NEC', offvalue='')
    exc_mech_menu.add_checkbutton(label='Photoionization', variable=exc_mech_var, onvalue='PIon', offvalue='')
    exc_mech_menu.add_checkbutton(label='Electron Impact Ionization', variable=exc_mech_var, onvalue='EII', offvalue='')



def configureCSMix(sim):
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
    PCS_order = [int(cs.split('intensity_')[1].split('.out')[0].split('+')[-1]) for cs in generalVars.radiative_files if '+' in cs]
    NCS_order = [int(cs.split('intensity_')[1].split('.out')[0].split('-')[-1]) for cs in generalVars.radiative_files if '+' not in cs]

    CS_mixEntriesRad = []

    labelRad = ttk.Label(mixer, text="Charge States With Radiative Transitions For Selected Atom:")
    labelRad.grid(column=0, row=0, columnspan=len(generalVars.radiative_files), pady=40)

    if len(generalVars.PCS_radMixValues) == 0:
        for cs in generalVars.radiative_files:
            if '+' in cs:
                generalVars.PCS_radMixValues.append(StringVar())
                CS_mixEntriesRad.append(ttk.Entry(mixer, textvariable=generalVars.PCS_radMixValues[-1], validate='key', validatecommand=check_num_wrapper))
                slidersRad.append(ttk.Scale(mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=generalVars.PCS_radMixValues[-1]))
                CS_labelsRad.append(ttk.Label(mixer, text=cs.split('intensity_')[1].split('.out')[0]))
                slidersRad[-1].set(0.0)
    else:
        i = 0
        for cs in generalVars.radiative_files:
            if '+' in cs:
                CS_mixEntriesRad.append(ttk.Entry(mixer, textvariable=generalVars.PCS_radMixValues[i], validate='key', validatecommand=check_num_wrapper))
                slidersRad.append(ttk.Scale(mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=generalVars.PCS_radMixValues[i]))
                CS_labelsRad.append(ttk.Label(mixer, text=cs.split('intensity_')[1].split('.out')[0]))

                i += 1

    if len(generalVars.NCS_radMixValues) == 0:
        for cs in generalVars.radiative_files:
            if '+' not in cs:
                generalVars.NCS_radMixValues.append(StringVar())
                CS_mixEntriesRad.append(ttk.Entry(mixer, textvariable=generalVars.NCS_radMixValues[-1], validate='key', validatecommand=check_num_wrapper))
                slidersRad.append(ttk.Scale(mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=generalVars.NCS_radMixValues[-1]))
                CS_labelsRad.append(ttk.Label(mixer, text=cs.split('intensity_')[1].split('.out')[0]))
                slidersRad[-1].set(0.0)
    else:
        i = 0
        for cs in generalVars.radiative_files:
            if '+' not in cs:
                CS_mixEntriesRad.append(ttk.Entry(mixer, textvariable=generalVars.NCS_radMixValues[i], validate='key', validatecommand=check_num_wrapper))
                slidersRad.append(ttk.Scale(mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=generalVars.NCS_radMixValues[i]))
                CS_labelsRad.append(ttk.Label(mixer, text=cs.split('intensity_')[1].split('.out')[0]))

                i += 1

    initial_PCS_Order = PCS_order.copy()
    initial_NCS_Order = NCS_order.copy()
    colIndex = 0
    while len(NCS_order) > 0:
        idx = initial_NCS_Order.index(min(NCS_order))

        CS_labelsRad[idx].grid(column=colIndex, row=1, sticky=(N), pady=5)
        slidersRad[idx].grid(column=colIndex, row=2, sticky=(N, S), pady=5)
        CS_mixEntriesRad[idx].grid(column=colIndex, row=3, sticky=(W, E), padx=5)

        mixer.columnconfigure(colIndex, weight=1)

        colIndex += 1
        del NCS_order[NCS_order.index(min(NCS_order))]

    while len(PCS_order) > 0:
        idx = initial_PCS_Order.index(min(PCS_order))

        CS_labelsRad[idx].grid(column=colIndex, row=1, sticky=(N), pady=5)
        slidersRad[idx].grid(column=colIndex, row=2, sticky=(N, S), pady=5)
        CS_mixEntriesRad[idx].grid(column=colIndex, row=3, sticky=(W, E), padx=5)

        mixer.columnconfigure(colIndex, weight=1)

        colIndex += 1
        del PCS_order[PCS_order.index(min(PCS_order))]

    mixer.rowconfigure(2, weight=1)

    # ------------------------------------------------------------------------------------------------------------------------------------
    # AUGER

    if len(generalVars.auger_files) > 0:
        mixer.geometry("800x600")

        slidersAug = []
        CS_labelsAug = []
        PCS_order = [int(cs.split('augrate_')[1].split('.out')[0].split('+')[-1]) for cs in generalVars.auger_files if '+' in cs]
        NCS_order = [int(cs.split('augrate_')[1].split('.out')[0].split('-')[-1]) for cs in generalVars.auger_files if '+' not in cs]

        CS_mixEntriesAug = []

        labelAug = ttk.Label(
            mixer, text="Charge States With Auger Transitions For Selected Atom:")
        labelAug.grid(column=0, row=4, columnspan=len(generalVars.radiative_files), pady=40)

        if len(generalVars.PCS_augMixValues) == 0:
            for cs in generalVars.auger_files:
                if '+' in cs:
                    generalVars.PCS_augMixValues.append(StringVar())
                    CS_mixEntriesAug.append(ttk.Entry(mixer, textvariable=generalVars.PCS_augMixValues[-1], validate='key', validatecommand=check_num_wrapper))
                    slidersAug.append(ttk.Scale(mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=generalVars.PCS_augMixValues[-1]))
                    CS_labelsAug.append(ttk.Label(mixer, text=cs.split('augrate_')[1].split('.out')[0]))
                    slidersAug[-1].set(0.0)
        else:
            i = 0
            for cs in generalVars.auger_files:
                if '+' in cs:
                    CS_mixEntriesAug.append(ttk.Entry(mixer, textvariable=generalVars.PCS_augMixValues[i], validate='key', validatecommand=check_num_wrapper))
                    slidersAug.append(ttk.Scale(mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=generalVars.PCS_augMixValues[i]))
                    CS_labelsAug.append(ttk.Label(mixer, text=cs.split('augrate_')[1].split('.out')[0]))

                    i += 1

        if len(generalVars.NCS_augMixValues) == 0:
            for cs in generalVars.auger_files:
                if '+' not in cs:
                    generalVars.NCS_augMixValues.append(StringVar())
                    CS_mixEntriesAug.append(ttk.Entry(mixer, textvariable=generalVars.NCS_augMixValues[-1], validate='key', validatecommand=check_num_wrapper))
                    slidersAug.append(ttk.Scale(mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=generalVars.NCS_augMixValues[-1]))
                    CS_labelsAug.append(ttk.Label(mixer, text=cs.split('augrate_')[1].split('.out')[0]))
                    slidersAug[-1].set(0.0)
        else:
            i = 0
            for cs in generalVars.auger_files:
                if '+' not in cs:
                    CS_mixEntriesAug.append(ttk.Entry(mixer, textvariable=generalVars.NCS_augMixValues[i], validate='key', validatecommand=check_num_wrapper))
                    slidersAug.append(ttk.Scale(mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=generalVars.NCS_augMixValues[i]))
                    CS_labelsAug.append(ttk.Label(mixer, text=cs.split('augrate_')[1].split('.out')[0]))

                    i += 1

        initial_PCS_Order = PCS_order.copy()
        initial_NCS_Order = NCS_order.copy()
        colIndex = 0
        while len(NCS_order) > 0:
            idx = initial_NCS_Order.index(min(NCS_order))

            CS_labelsAug[idx].grid(column=colIndex, row=5, sticky=(N), pady=5)
            slidersAug[idx].grid(column=colIndex, row=6, sticky=(N, S), pady=5)
            CS_mixEntriesAug[idx].grid(column=colIndex, row=7, sticky=(W, E), padx=5)

            mixer.columnconfigure(colIndex, weight=1)

            colIndex += 1
            del NCS_order[NCS_order.index(min(NCS_order))]

        while len(PCS_order) > 0:
            idx = initial_PCS_Order.index(min(PCS_order))

            CS_labelsAug[idx].grid(column=colIndex, row=5, sticky=(N), pady=5)
            slidersAug[idx].grid(column=colIndex, row=6, sticky=(N, S), pady=5)
            CS_mixEntriesAug[idx].grid(column=colIndex, row=7, sticky=(W, E), padx=5)

            mixer.columnconfigure(colIndex, weight=1)

            colIndex += 1
            del PCS_order[PCS_order.index(min(PCS_order))]

        mixer.rowconfigure(6, weight=1)

    # ------------------------------------------------------------------------------------------------------------------------------------
    # Ion Population slider

    Ion_Populations = {}

    combined_x = []
    combined_y = []

    for i, cs in enumerate(generalVars.ionpopdata[0]):
        Ion_Populations[cs + '_x'] = []
        Ion_Populations[cs + '_y'] = []

        col = i * 2

        for vals in generalVars.ionpopdata[1:]:
            if '---' not in vals[col]:
                combined_x.append(float(vals[col]))
                combined_y.append(float(vals[col + 1]))
                if float(vals[col]) not in Ion_Populations[cs + '_x']:
                    Ion_Populations[cs + '_x'].append(float(vals[col]))
                    Ion_Populations[cs +'_y'].append(float(vals[col + 1]))

    y_max = max(combined_y)
    for cs in generalVars.ionpopdata[0]:
        Ion_Populations[cs + '_y'] = [pop * 100 / y_max for pop in Ion_Populations[cs + '_y']]

    Ion_Population_Functions = {}
    # linear interpolation because of "corners" in the distribution functions
    for cs in generalVars.ionpopdata[0]:
        order = np.argsort(Ion_Populations[cs + '_x'])
        Ion_Population_Functions[cs] = interp1d(np.array(Ion_Populations[cs + '_x'])[order], np.array(Ion_Populations[cs + '_y'])[order], kind='linear')

    combined_x = list(set(combined_x))

    temperature_max = max(combined_x)
    temperature_min = min(combined_x)

    if len(generalVars.auger_files) > 0:
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

    figure_frame.grid(column=0, row=fig_row, columnspan=max(len(generalVars.radiative_files), len(generalVars.auger_files)), pady=20)

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
            if len(generalVars.PCS_radMixValues) > 0:
                i = 0
                for cs_file in generalVars.radiative_files:
                    if cs in cs_file:
                        try:
                            generalVars.PCS_radMixValues[i].set(str(Ion_Population_Functions[cs](float(temperature.get()))))
                        except:
                            generalVars.PCS_radMixValues[i].set("0.0")

                        break

                    if '+' in cs:
                        i += 1

            if len(generalVars.NCS_radMixValues) > 0:
                i = 0
                for cs_file in generalVars.radiative_files:
                    if cs in cs_file:
                        try:
                            generalVars.NCS_radMixValues[i].set(str(Ion_Population_Functions[cs](float(temperature.get()))))
                        except:
                            generalVars.NCS_radMixValues[i].set("0.0")

                        break

                    if '+' not in cs:
                        i += 1

        if len(generalVars.auger_files) > 0:
            for cs in Ion_Population_Functions:
                if len(generalVars.PCS_augMixValues) > 0:
                    i = 0
                    for cs_file in generalVars.auger_files:
                        if cs in cs_file:
                            try:
                                generalVars.PCS_augMixValues[i].set(str(Ion_Population_Functions[cs](float(temperature.get()))))
                            except:
                                generalVars.PCS_augMixValues[i].set("0.0")

                            break

                        if '+' in cs:
                            i += 1

                if len(generalVars.NCS_augMixValues) > 0:
                    i = 0
                    for cs_file in generalVars.auger_files:
                        if cs in cs_file:
                            try:
                                generalVars.NCS_augMixValues[i].set(str(Ion_Population_Functions[cs](float(temperature.get()))))
                            except:
                                generalVars.NCS_augMixValues[i].set("0.0")

                            break

                        if '+' not in cs:
                            i += 1

    temperature.trace_add("write", update_temp_line)
    temp_slider = ttk.Scale(mixer, orient=HORIZONTAL, length=200, from_=temperature_min, to=temperature_max, variable=temperature)
    temp_entry = ttk.Entry(mixer, textvariable=temperature, validate='key', validatecommand=check_num_wrapper)
    temp_slider.grid(column=0, row=fig_row + 1, columnspan=max(len(generalVars.radiative_files), len(generalVars.auger_files)) - 1, sticky=(W, E), padx=10, pady=20)
    temp_entry.grid(column=max(len(generalVars.radiative_files), len(generalVars.auger_files)) - 1, row=fig_row + 1, sticky=(W, E), padx=5)

    mixer.rowconfigure(fig_row + 1, weight=1)

    for cs in generalVars.ionpopdata[0]:
        x_min = min(Ion_Populations[cs + '_x'])
        x_max = max(Ion_Populations[cs + '_x'])

        temp_new = np.arange(x_min, x_max, (x_max - x_min) / 100)
        pop_new = Ion_Population_Functions[cs](temp_new)

        a.plot(temp_new, pop_new, label=cs)
    
    
    a.legend()



def setupExpPlot(f, load, element_name):
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
    
    # Carregar a matriz do espectro experimental do ficheiro escolhido no menu
    exp_spectrum = loadExp(load)
    
    return graph_area, residues_graph, exp_spectrum



def plotExp(graph_area, residues_graph, exp_x, exp_y, exp_sigma, normalize):
    if normalize == 'One':
        # Plot dos dados experimentais normalizados à unidade
        graph_area.scatter(exp_x, exp_y / max(exp_y), marker='.', label='Exp.')
        # Plot do desvio padrão no gráfico dos resí­duos (linha positiva)
        residues_graph.plot(exp_x, np.array(exp_sigma) / max(exp_y), 'k--')
        # Plot do desvio padrão no gráfico dos resí­duos (linha negativa)
        residues_graph.plot(exp_x, -np.array(exp_sigma) / max(exp_y), 'k--')
    else:
        # Plot dos dados experimentais
        graph_area.scatter(exp_x, exp_y, marker='.', label='Exp.')
        # Plot do desvio padrão no gráfico dos resí­duos (linha positiva)
        residues_graph.plot(exp_x, np.array(exp_sigma), 'k--')
        # Plot do desvio padrão no gráfico dos resí­duos (linha negativa)
        residues_graph.plot(exp_x, -np.array(exp_sigma), 'k--')

    graph_area.legend()