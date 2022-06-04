import csv
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from pathlib import Path
import os
import numpy as np
from matplotlib import gridspec
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from scipy.special import wofz
from scipy.interpolate import interp1d
from lmfit import Minimizer, Parameters, report_fit, fit_report
from datetime import datetime
import time
import matplotlib.pyplot as plt

dir_path = Path(str(os.getcwd()) + '/')  # os.getcwd retorna a directoria onde o cÃ³digo estÃ¡. Criamos um objecto tipo Path porque permite o programa ser corrido em qq OS
# https://medium.com/@ageitgey/python-3-quick-tip-the-easy-way-to-deal-with-file-paths-on-windows-mac-and-linux-11a072b58d5f site onde vi sobre isto GRV

# ---------------------------------------------------------------------------------------------------------------
labeldict = {'K1': '1s', 'L1': '2s', 'L2': '2p*', 'L3': '2p', 'M1': '3s', 'M2': '3p*', 'M3': '3p', 'M4': '3d*',
             'M5': '3d', 'N1': '4s', 'N2': '4p*', 'N3': '4p', 'N4': '4d*', 'N5': '4d', 'N6': '4f*', 'N7': '4f',
             'O1': '5s', 'O2': '5p*', 'O3': '5p', 'O4': '5d*', 'O5': '5d', 'O6': '5f*', 'O7': '5f', 'O8': '5g*',
             'O9': '5g', 'P1': '6s'}  # Acho que este dicionÃ¡rio serve sÃ³ para converter notaÃ§Ãµes FALTA: Confirmar com Mauro

the_dictionary = {
    "KL\u2081": {"low_level": "K1", "high_level": "L1", "selected_state": False, "readable_name": "KL1"}, #for ionic transitions
    "K\u03B1\u2081": {"low_level": "K1", "high_level": "L3", "selected_state": False, "readable_name": "Kalpha1"},
    "K\u03B1\u2082": {"low_level": "K1", "high_level": "L2", "selected_state": False, "readable_name": "Kalpha2"},
    "K\u03B2\u2081": {"low_level": "K1", "high_level": "M3", "selected_state": False, "readable_name": "Kbeta1"},
    "K\u03B2\u2082\u00B9": {"low_level": "K1", "high_level": "N3", "selected_state": False, "readable_name": "Kbeta2 1"},
    "K\u03B2\u2082\u00B2": {"low_level": "K1", "high_level": "N2", "selected_state": False, "readable_name": "Kbeta2 2"},
    "K\u03B2\u2083": {"low_level": "K1", "high_level": "M2", "selected_state": False, "readable_name": "Kbeta3"},
    "K\u03B2\u2084\u00B9": {"low_level": "K1", "high_level": "N5", "selected_state": False, "readable_name": "Kbeta4 1"},
    "K\u03B2\u2084\u00B2": {"low_level": "K1", "high_level": "N4", "selected_state": False, "readable_name": "Kbeta4 2"},
    "K\u03B2\u2085\u00B9": {"low_level": "K1", "high_level": "M5", "selected_state": False, "readable_name": "Kbeta5 1"},
    "K\u03B2\u2085\u00B2": {"low_level": "K1", "high_level": "M4", "selected_state": False, "readable_name": "Kbeta5 2"},
    "L\u03B1\u2081": {"low_level": "L3", "high_level": "M5", "selected_state": False, "readable_name": "Lalpha1"},
    "L\u03B1\u2082": {"low_level": "L3", "high_level": "M4", "selected_state": False, "readable_name": "Lalpha2"},
    "L\u03B2\u2081": {"low_level": "L2", "high_level": "M4", "selected_state": False, "readable_name": "Lbeta1"},
    "L\u03B2\u2083": {"low_level": "L1", "high_level": "M3", "selected_state": False, "readable_name": "Lbeta3"},
    "L\u03B2\u2084": {"low_level": "L1", "high_level": "M2", "selected_state": False, "readable_name": "Lbeta4"},
    "L\u03B2\u2086": {"low_level": "L3", "high_level": "N1", "selected_state": False, "readable_name": "Lbeta6"},
    "L\u03B2\u2089": {"low_level": "L1", "high_level": "M5", "selected_state": False, "readable_name": "Lbeta9"},
    "L\u03B2\u2081\u2080": {"low_level": "L1", "high_level": "M4", "selected_state": False, "readable_name": "Lbeta10"},
    "L\u03B2\u2081\u2087": {"low_level": "L2", "high_level": "M3", "selected_state": False, "readable_name": "Lbeta17"},
    "L\u03B3\u2081": {"low_level": "L2", "high_level": "N4", "selected_state": False, "readable_name": "Lgamma1"},
    "L\u03B3\u2082": {"low_level": "L1", "high_level": "N2", "selected_state": False, "readable_name": "Lgamma2"},
    "L\u03B3\u2083": {"low_level": "L1", "high_level": "N3", "selected_state": False, "readable_name": "Lgamma3"},
    "L\u03B3\u2084": {"low_level": "L1", "high_level": "O3", "selected_state": False, "readable_name": "Lgamma4"},
    "L\u03B3\u2082'": {"low_level": "L1", "high_level": "O2", "selected_state": False, "readable_name": "Lgamma2'"},
    "L\u03B3\u2085": {"low_level": "L2", "high_level": "N1", "selected_state": False, "readable_name": "Lgamma5"},
    "L\u03B3\u2086": {"low_level": "L2", "high_level": "O4", "selected_state": False, "readable_name": "Lgamma6"},
    "L\u03B3\u2088": {"low_level": "L2", "high_level": "O1", "selected_state": False, "readable_name": "Lgamma8"},
    "L\u03B7": {"low_level": "L2", "high_level": "M1", "selected_state": False, "readable_name": "Ln"},
    "Ll": {"low_level": "L3", "high_level": "M1", "selected_state": False, "readable_name": "Ll"},
    "Ls": {"low_level": "L3", "high_level": "M3", "selected_state": False, "readable_name": "Ls"},
    "Lt": {"low_level": "L3", "high_level": "M2", "selected_state": False, "readable_name": "Lt"},
    "M\u03B1\u2081": {"low_level": "M5", "high_level": "N7", "selected_state": False, "readable_name": "Malpha1"},
    "M\u03B1\u2082": {"low_level": "M5", "high_level": "N6", "selected_state": False, "readable_name": "Malpha2"},
    "M\u03B2": {"low_level": "M4", "high_level": "N6", "selected_state": False, "readable_name": "Mbeta"},
    "M\u03B3\u2081": {"low_level": "M3", "high_level": "N5", "selected_state": False, "readable_name": "Mgamma1"},
}  # DicionÃ¡rio onde estÃ£o guardadas as transiÃ§Ãµes. Cada valor do dicionÃ¡rio Ã© em si um dicionÃ¡rio (Nested dictionaries)


the_aug_dictionary = {
    "KL1L1": {"low_level": "K1", "high_level": "L1", "auger_level": "L1", "selected_state": False, "readable_name": "KL1L1"},
    "KL1L2": {"low_level": "K1", "high_level": "L1", "auger_level": "L2", "selected_state": False, "readable_name": "KL1L2"},
    "KL1L3": {"low_level": "K1", "high_level": "L1", "auger_level": "L3", "selected_state": False, "readable_name": "KL1L3"},
    "KL1M1": {"low_level": "K1", "high_level": "L1", "auger_level": "M1", "selected_state": False, "readable_name": "KL1M1"},
    "KL1M2": {"low_level": "K1", "high_level": "L1", "auger_level": "M2", "selected_state": False, "readable_name": "KL1M2"},
    "KL1M3": {"low_level": "K1", "high_level": "L1", "auger_level": "M3", "selected_state": False, "readable_name": "KL1M3"},
    "KL1M4": {"low_level": "K1", "high_level": "L1", "auger_level": "M4", "selected_state": False, "readable_name": "KL1M4"},
    "KL1M5": {"low_level": "K1", "high_level": "L1", "auger_level": "M5", "selected_state": False, "readable_name": "KL1M5"},
    "KL1N1": {"low_level": "K1", "high_level": "L1", "auger_level": "N1", "selected_state": False, "readable_name": "KL1N1"},
    "KL2L2": {"low_level": "K1", "high_level": "L2", "auger_level": "L2", "selected_state": False, "readable_name": "KL2L2"},
    "KL2L3": {"low_level": "K1", "high_level": "L2", "auger_level": "L3", "selected_state": False, "readable_name": "KL2L3"},
    "KL2M1": {"low_level": "K1", "high_level": "L2", "auger_level": "M1", "selected_state": False, "readable_name": "KL2M1"},
    "KL2M2": {"low_level": "K1", "high_level": "L2", "auger_level": "M2", "selected_state": False, "readable_name": "KL2M2"},
    "KL2M3": {"low_level": "K1", "high_level": "L2", "auger_level": "M3", "selected_state": False, "readable_name": "KL2M3"},
    "KL2M4": {"low_level": "K1", "high_level": "L2", "auger_level": "M4", "selected_state": False, "readable_name": "KL2M4"},
    "KL2M5": {"low_level": "K1", "high_level": "L2", "auger_level": "M5", "selected_state": False, "readable_name": "KL2M5"},
    "KL2N1": {"low_level": "K1", "high_level": "L2", "auger_level": "N1", "selected_state": False, "readable_name": "KL2N1"},
    "KL3L3": {"low_level": "K1", "high_level": "L3", "auger_level": "L3", "selected_state": False, "readable_name": "KL3L3"},
    "KL3M1": {"low_level": "K1", "high_level": "L3", "auger_level": "M1", "selected_state": False, "readable_name": "KL3M1"},
    "KL3M2": {"low_level": "K1", "high_level": "L3", "auger_level": "M2", "selected_state": False, "readable_name": "KL3M2"},
    "KL3M3": {"low_level": "K1", "high_level": "L3", "auger_level": "M3", "selected_state": False, "readable_name": "KL3M3"},
    "KL3M4": {"low_level": "K1", "high_level": "L3", "auger_level": "M4", "selected_state": False, "readable_name": "KL3M4"},
    "KL3M5": {"low_level": "K1", "high_level": "L3", "auger_level": "M5", "selected_state": False, "readable_name": "KL3M5"},
    "KL3N1": {"low_level": "K1", "high_level": "L3", "auger_level": "N1", "selected_state": False, "readable_name": "KL3N1"},
    "KM1M1": {"low_level": "K1", "high_level": "M1", "auger_level": "M1", "selected_state": False, "readable_name": "KM1M1"},
    "KM1M2": {"low_level": "K1", "high_level": "M1", "auger_level": "M2", "selected_state": False, "readable_name": "KM1M2"},
    "KM1M3": {"low_level": "K1", "high_level": "M1", "auger_level": "M3", "selected_state": False, "readable_name": "KM1M3"},
    "KM1M4": {"low_level": "K1", "high_level": "M1", "auger_level": "M4", "selected_state": False, "readable_name": "KM1M4"},
    "KM1M5": {"low_level": "K1", "high_level": "M1", "auger_level": "M5", "selected_state": False, "readable_name": "KM1M5"},
    "KM1N1": {"low_level": "K1", "high_level": "M1", "auger_level": "N1", "selected_state": False, "readable_name": "KM1N1"},
    "KM2M2": {"low_level": "K1", "high_level": "M2", "auger_level": "M2", "selected_state": False, "readable_name": "KM2M2"},
    "KM2M3": {"low_level": "K1", "high_level": "M2", "auger_level": "M3", "selected_state": False, "readable_name": "KM2M3"},
    "KM2M4": {"low_level": "K1", "high_level": "M2", "auger_level": "M4", "selected_state": False, "readable_name": "KM2M4"},
    "KM2M5": {"low_level": "K1", "high_level": "M2", "auger_level": "M5", "selected_state": False, "readable_name": "KM2M5"},
    "KM2N1": {"low_level": "K1", "high_level": "M2", "auger_level": "N1", "selected_state": False, "readable_name": "KM2N1"},
    "KM3M3": {"low_level": "K1", "high_level": "M3", "auger_level": "M3", "selected_state": False, "readable_name": "KM3M3"},
    "KM3M4": {"low_level": "K1", "high_level": "M3", "auger_level": "M4", "selected_state": False, "readable_name": "KM3M4"},
    "KM3M5": {"low_level": "K1", "high_level": "M3", "auger_level": "M5", "selected_state": False, "readable_name": "KM3M5"},
    "KM3N1": {"low_level": "K1", "high_level": "M3", "auger_level": "N1", "selected_state": False, "readable_name": "KM3N1"},
    "KM4M4": {"low_level": "K1", "high_level": "M4", "auger_level": "M4", "selected_state": False, "readable_name": "KM4M4"},
    "KM4M5": {"low_level": "K1", "high_level": "M4", "auger_level": "M5", "selected_state": False, "readable_name": "KM4M5"},
    "KM4N1": {"low_level": "K1", "high_level": "M4", "auger_level": "N1", "selected_state": False, "readable_name": "KM4N1"},
    "KM5M5": {"low_level": "K1", "high_level": "M5", "auger_level": "M5", "selected_state": False, "readable_name": "KM5M5"},
    "KM5N1": {"low_level": "K1", "high_level": "M5", "auger_level": "N1", "selected_state": False, "readable_name": "KM5N1"},
    "KN1N1": {"low_level": "K1", "high_level": "N1", "auger_level": "N1", "selected_state": False, "readable_name": "KN1N1"},
    
    "L1L2L2": {"low_level": "L1", "high_level": "L2", "auger_level": "L2", "selected_state": False, "readable_name": "L1L2L2"},
    "L1L2L3": {"low_level": "L1", "high_level": "L2", "auger_level": "L3", "selected_state": False, "readable_name": "L1L2L3"},
    "L1L2M1": {"low_level": "L1", "high_level": "L2", "auger_level": "M1", "selected_state": False, "readable_name": "L1L2M1"},
    "L1L2M2": {"low_level": "L1", "high_level": "L2", "auger_level": "M2", "selected_state": False, "readable_name": "L1L2M2"},
    "L1L2M3": {"low_level": "L1", "high_level": "L2", "auger_level": "M3", "selected_state": False, "readable_name": "L1L2M3"},
    "L1L2M4": {"low_level": "L1", "high_level": "L2", "auger_level": "M4", "selected_state": False, "readable_name": "L1L2M4"},
    "L1L2M5": {"low_level": "L1", "high_level": "L2", "auger_level": "M5", "selected_state": False, "readable_name": "L1L2M5"},
    "L1L2N1": {"low_level": "L1", "high_level": "L2", "auger_level": "N1", "selected_state": False, "readable_name": "L1L2N1"},
    "L1L3L3": {"low_level": "L1", "high_level": "L3", "auger_level": "L3", "selected_state": False, "readable_name": "L1L3L3"},
    "L1L3M1": {"low_level": "L1", "high_level": "L3", "auger_level": "M1", "selected_state": False, "readable_name": "L1L3M1"},
    "L1L3M2": {"low_level": "L1", "high_level": "L3", "auger_level": "M2", "selected_state": False, "readable_name": "L1L3M2"},
    "L1L3M3": {"low_level": "L1", "high_level": "L3", "auger_level": "M3", "selected_state": False, "readable_name": "L1L3M3"},
    "L1L3M4": {"low_level": "L1", "high_level": "L3", "auger_level": "M4", "selected_state": False, "readable_name": "L1L3M4"},
    "L1L3M5": {"low_level": "L1", "high_level": "L3", "auger_level": "M5", "selected_state": False, "readable_name": "L1L3M5"},
    "L1L3N1": {"low_level": "L1", "high_level": "L3", "auger_level": "N1", "selected_state": False, "readable_name": "L1L3N1"},
    "L1M1M1": {"low_level": "L1", "high_level": "M1", "auger_level": "M1", "selected_state": False, "readable_name": "L1M1M1"},
    "L1M1M2": {"low_level": "L1", "high_level": "M1", "auger_level": "M2", "selected_state": False, "readable_name": "L1M1M2"},
    "L1M1M3": {"low_level": "L1", "high_level": "M1", "auger_level": "M3", "selected_state": False, "readable_name": "L1M1M3"},
    "L1M1M4": {"low_level": "L1", "high_level": "M1", "auger_level": "M4", "selected_state": False, "readable_name": "L1M1M4"},
    "L1M1M5": {"low_level": "L1", "high_level": "M1", "auger_level": "M5", "selected_state": False, "readable_name": "L1M1M5"},
    "L1M1N1": {"low_level": "L1", "high_level": "M1", "auger_level": "N1", "selected_state": False, "readable_name": "L1M1N1"},
    "L1M2M2": {"low_level": "L1", "high_level": "M2", "auger_level": "M2", "selected_state": False, "readable_name": "L1M2M2"},
    "L1M2M3": {"low_level": "L1", "high_level": "M2", "auger_level": "M3", "selected_state": False, "readable_name": "L1M2M3"},
    "L1M2M4": {"low_level": "L1", "high_level": "M2", "auger_level": "M4", "selected_state": False, "readable_name": "L1M2M4"},
    "L1M2M5": {"low_level": "L1", "high_level": "M2", "auger_level": "M5", "selected_state": False, "readable_name": "L1M2M5"},
    "L1M2N1": {"low_level": "L1", "high_level": "M2", "auger_level": "N1", "selected_state": False, "readable_name": "L1M2N1"},
    "L1M3M3": {"low_level": "L1", "high_level": "M3", "auger_level": "M3", "selected_state": False, "readable_name": "L1M3M3"},
    "L1M3M4": {"low_level": "L1", "high_level": "M3", "auger_level": "M4", "selected_state": False, "readable_name": "L1M3M4"},
    "L1M3M5": {"low_level": "L1", "high_level": "M3", "auger_level": "M5", "selected_state": False, "readable_name": "L1M3M5"},
    "L1M3N1": {"low_level": "L1", "high_level": "M3", "auger_level": "N1", "selected_state": False, "readable_name": "L1M3N1"},
    "L1M4M4": {"low_level": "L1", "high_level": "M4", "auger_level": "M4", "selected_state": False, "readable_name": "L1M4M4"},
    "L1M4M5": {"low_level": "L1", "high_level": "M4", "auger_level": "M5", "selected_state": False, "readable_name": "L1M4M5"},
    "L1M4N1": {"low_level": "L1", "high_level": "M4", "auger_level": "N1", "selected_state": False, "readable_name": "L1M4N1"},
    "L1M5M5": {"low_level": "L1", "high_level": "M5", "auger_level": "M5", "selected_state": False, "readable_name": "L1M5M5"},
    "L1M5N1": {"low_level": "L1", "high_level": "M5", "auger_level": "N1", "selected_state": False, "readable_name": "L1M5N1"},
    "L1N1N1": {"low_level": "L1", "high_level": "N1", "auger_level": "N1", "selected_state": False, "readable_name": "L1N1N1"},
    
    "L2L3L3": {"low_level": "L2", "high_level": "L3", "auger_level": "L3", "selected_state": False, "readable_name": "L2L3L3"},
    "L2L3M1": {"low_level": "L2", "high_level": "L3", "auger_level": "M1", "selected_state": False, "readable_name": "L2L3M1"},
    "L2L3M2": {"low_level": "L2", "high_level": "L3", "auger_level": "M2", "selected_state": False, "readable_name": "L2L3M2"},
    "L2L3M3": {"low_level": "L2", "high_level": "L3", "auger_level": "M3", "selected_state": False, "readable_name": "L2L3M3"},
    "L2L3M4": {"low_level": "L2", "high_level": "L3", "auger_level": "M4", "selected_state": False, "readable_name": "L2L3M4"},
    "L2L3M5": {"low_level": "L2", "high_level": "L3", "auger_level": "M5", "selected_state": False, "readable_name": "L2L3M5"},
    "L2L3N1": {"low_level": "L2", "high_level": "L3", "auger_level": "N1", "selected_state": False, "readable_name": "L2L3N1"},
    "L2M1M1": {"low_level": "L2", "high_level": "M1", "auger_level": "M1", "selected_state": False, "readable_name": "L2M1M1"},
    "L2M1M2": {"low_level": "L2", "high_level": "M1", "auger_level": "M2", "selected_state": False, "readable_name": "L2M1M2"},
    "L2M1M3": {"low_level": "L2", "high_level": "M1", "auger_level": "M3", "selected_state": False, "readable_name": "L2M1M3"},
    "L2M1M4": {"low_level": "L2", "high_level": "M1", "auger_level": "M4", "selected_state": False, "readable_name": "L2M1M4"},
    "L2M1M5": {"low_level": "L2", "high_level": "M1", "auger_level": "M5", "selected_state": False, "readable_name": "L2M1M5"},
    "L2M1N1": {"low_level": "L2", "high_level": "M1", "auger_level": "N1", "selected_state": False, "readable_name": "L2M1N1"},
    "L2M2M2": {"low_level": "L2", "high_level": "M2", "auger_level": "M2", "selected_state": False, "readable_name": "L2M2M2"},
    "L2M2M3": {"low_level": "L2", "high_level": "M2", "auger_level": "M3", "selected_state": False, "readable_name": "L2M2M3"},
    "L2M2M4": {"low_level": "L2", "high_level": "M2", "auger_level": "M4", "selected_state": False, "readable_name": "L2M2M4"},
    "L2M2M5": {"low_level": "L2", "high_level": "M2", "auger_level": "M5", "selected_state": False, "readable_name": "L2M2M5"},
    "L2M2N1": {"low_level": "L2", "high_level": "M2", "auger_level": "N1", "selected_state": False, "readable_name": "L2M2N1"},
    "L2M3M3": {"low_level": "L2", "high_level": "M3", "auger_level": "M3", "selected_state": False, "readable_name": "L2M3M3"},
    "L2M3M4": {"low_level": "L2", "high_level": "M3", "auger_level": "M4", "selected_state": False, "readable_name": "L2M3M4"},
    "L2M3M5": {"low_level": "L2", "high_level": "M3", "auger_level": "M5", "selected_state": False, "readable_name": "L2M3M5"},
    "L2M3N1": {"low_level": "L2", "high_level": "M3", "auger_level": "N1", "selected_state": False, "readable_name": "L2M3N1"},
    "L2M4M4": {"low_level": "L2", "high_level": "M4", "auger_level": "M4", "selected_state": False, "readable_name": "L2M4M4"},
    "L2M4M5": {"low_level": "L2", "high_level": "M4", "auger_level": "M5", "selected_state": False, "readable_name": "L2M4M5"},
    "L2M4N1": {"low_level": "L2", "high_level": "M4", "auger_level": "N1", "selected_state": False, "readable_name": "L2M4N1"},
    "L2M5M5": {"low_level": "L2", "high_level": "M5", "auger_level": "M5", "selected_state": False, "readable_name": "L2M5M5"},
    "L2M5N1": {"low_level": "L2", "high_level": "M5", "auger_level": "N1", "selected_state": False, "readable_name": "L2M5N1"},
    "L2N1N1": {"low_level": "L2", "high_level": "N1", "auger_level": "N1", "selected_state": False, "readable_name": "L2N1N1"},
    
    "L3M1M1": {"low_level": "L3", "high_level": "M1", "auger_level": "M1", "selected_state": False, "readable_name": "L3M1M1"},
    "L3M1M2": {"low_level": "L3", "high_level": "M1", "auger_level": "M2", "selected_state": False, "readable_name": "L3M1M2"},
    "L3M1M3": {"low_level": "L3", "high_level": "M1", "auger_level": "M3", "selected_state": False, "readable_name": "L3M1M3"},
    "L3M1M4": {"low_level": "L3", "high_level": "M1", "auger_level": "M4", "selected_state": False, "readable_name": "L3M1M4"},
    "L3M1M5": {"low_level": "L3", "high_level": "M1", "auger_level": "M5", "selected_state": False, "readable_name": "L3M1M5"},
    "L3M1N1": {"low_level": "L3", "high_level": "M1", "auger_level": "N1", "selected_state": False, "readable_name": "L3M1N1"},
    "L3M2M2": {"low_level": "L3", "high_level": "M2", "auger_level": "M2", "selected_state": False, "readable_name": "L3M2M2"},
    "L3M2M3": {"low_level": "L3", "high_level": "M2", "auger_level": "M3", "selected_state": False, "readable_name": "L3M2M3"},
    "L3M2M4": {"low_level": "L3", "high_level": "M2", "auger_level": "M4", "selected_state": False, "readable_name": "L3M2M4"},
    "L3M2M5": {"low_level": "L3", "high_level": "M2", "auger_level": "M5", "selected_state": False, "readable_name": "L3M2M5"},
    "L3M2N1": {"low_level": "L3", "high_level": "M2", "auger_level": "N1", "selected_state": False, "readable_name": "L3M2N1"},
    "L3M3M3": {"low_level": "L3", "high_level": "M3", "auger_level": "M3", "selected_state": False, "readable_name": "L3M3M3"},
    "L3M3M4": {"low_level": "L3", "high_level": "M3", "auger_level": "M4", "selected_state": False, "readable_name": "L3M3M4"},
    "L3M3M5": {"low_level": "L3", "high_level": "M3", "auger_level": "M5", "selected_state": False, "readable_name": "L3M3M5"},
    "L3M3N1": {"low_level": "L3", "high_level": "M3", "auger_level": "N1", "selected_state": False, "readable_name": "L3M3N1"},
    "L3M4M4": {"low_level": "L3", "high_level": "M4", "auger_level": "M4", "selected_state": False, "readable_name": "L3M4M4"},
    "L3M4M5": {"low_level": "L3", "high_level": "M4", "auger_level": "M5", "selected_state": False, "readable_name": "L3M4M5"},
    "L3M4N1": {"low_level": "L3", "high_level": "M4", "auger_level": "N1", "selected_state": False, "readable_name": "L3M4N1"},
    "L3M5M5": {"low_level": "L3", "high_level": "M5", "auger_level": "M5", "selected_state": False, "readable_name": "L3M5M5"},
    "L3M5N1": {"low_level": "L3", "high_level": "M5", "auger_level": "N1", "selected_state": False, "readable_name": "L3M5N1"},
    "L3N1N1": {"low_level": "L3", "high_level": "N1", "auger_level": "N1", "selected_state": False, "readable_name": "L3N1N1"},
    
    "M1M2M2": {"low_level": "M1", "high_level": "M2", "auger_level": "M2", "selected_state": False, "readable_name": "M1M2M2"},
    "M1M2M3": {"low_level": "M1", "high_level": "M2", "auger_level": "M3", "selected_state": False, "readable_name": "M1M2M3"},
    "M1M2M4": {"low_level": "M1", "high_level": "M2", "auger_level": "M4", "selected_state": False, "readable_name": "M1M2M4"},
    "M1M2M5": {"low_level": "M1", "high_level": "M2", "auger_level": "M5", "selected_state": False, "readable_name": "M1M2M5"},
    "M1M2N1": {"low_level": "M1", "high_level": "M2", "auger_level": "N1", "selected_state": False, "readable_name": "M1M2N1"},
    "M1M3M3": {"low_level": "M1", "high_level": "M3", "auger_level": "M3", "selected_state": False, "readable_name": "M1M3M3"},
    "M1M3M4": {"low_level": "M1", "high_level": "N3", "auger_level": "M4", "selected_state": False, "readable_name": "M1M3M4"},
    "M1M3M5": {"low_level": "M1", "high_level": "N3", "auger_level": "M5", "selected_state": False, "readable_name": "M1M3M5"},
    "M1M3N1": {"low_level": "M1", "high_level": "M3", "auger_level": "N1", "selected_state": False, "readable_name": "M1M3N1"},
    "M1M4M4": {"low_level": "M1", "high_level": "M4", "auger_level": "M4", "selected_state": False, "readable_name": "M1M4M4"},
    "M1M4M5": {"low_level": "M1", "high_level": "M4", "auger_level": "M5", "selected_state": False, "readable_name": "M1M4M5"},
    "M1M4N1": {"low_level": "M1", "high_level": "M4", "auger_level": "N1", "selected_state": False, "readable_name": "M1M4N1"},
    "M1M5M5": {"low_level": "M1", "high_level": "M5", "auger_level": "M5", "selected_state": False, "readable_name": "M1M5M5"},
    "M1M5N1": {"low_level": "M1", "high_level": "M5", "auger_level": "N1", "selected_state": False, "readable_name": "M1M5N1"},
    "M1N1N1": {"low_level": "M1", "high_level": "N1", "auger_level": "N1", "selected_state": False, "readable_name": "M1N1N1"},
    
    "M2M3M3": {"low_level": "M2", "high_level": "M3", "auger_level": "M3", "selected_state": False, "readable_name": "M2M3M3"},
    "M2M3M4": {"low_level": "M2", "high_level": "M3", "auger_level": "M4", "selected_state": False, "readable_name": "M2M3M4"},
    "M2M3M5": {"low_level": "M2", "high_level": "M3", "auger_level": "M5", "selected_state": False, "readable_name": "M2M3M5"},
    "M2M3N1": {"low_level": "M2", "high_level": "M3", "auger_level": "N1", "selected_state": False, "readable_name": "M2M3N1"},
    "M2M4M4": {"low_level": "M2", "high_level": "M4", "auger_level": "M4", "selected_state": False, "readable_name": "M2M4M4"},
    "M2M4M5": {"low_level": "M2", "high_level": "M4", "auger_level": "M5", "selected_state": False, "readable_name": "M2M4M5"},
    "M2M4N1": {"low_level": "M2", "high_level": "M4", "auger_level": "N1", "selected_state": False, "readable_name": "M2M4N1"},
    "M2M5M5": {"low_level": "M2", "high_level": "M5", "auger_level": "M5", "selected_state": False, "readable_name": "M2M5M5"},
    "M2M5N1": {"low_level": "M2", "high_level": "M5", "auger_level": "N1", "selected_state": False, "readable_name": "M2M5N1"},
    "M2N1N1": {"low_level": "M2", "high_level": "N1", "auger_level": "N1", "selected_state": False, "readable_name": "M2N1N1"},
    
    "M3M4M4": {"low_level": "M3", "high_level": "M4", "auger_level": "M4", "selected_state": False, "readable_name": "M3M4M4"},
    "M3M4M5": {"low_level": "M3", "high_level": "M4", "auger_level": "M5", "selected_state": False, "readable_name": "M3M4M5"},
    "M3M4N1": {"low_level": "M3", "high_level": "M4", "auger_level": "N1", "selected_state": False, "readable_name": "M3M4N1"},
    "M3M5M5": {"low_level": "M3", "high_level": "M5", "auger_level": "M5", "selected_state": False, "readable_name": "M3M5M5"},
    "M3M5N1": {"low_level": "M3", "high_level": "M5", "auger_level": "N1", "selected_state": False, "readable_name": "M3M5N1"},
    "M3N1N1": {"low_level": "M3", "high_level": "N1", "auger_level": "N1", "selected_state": False, "readable_name": "M3N1N1"},
    
    "M4M5M5": {"low_level": "M4", "high_level": "M5", "auger_level": "M5", "selected_state": False, "readable_name": "M4M5M5"},
    "M4M5N1": {"low_level": "M4", "high_level": "M5", "auger_level": "N1", "selected_state": False, "readable_name": "M4M5N1"},
    "M4N1N1": {"low_level": "M4", "high_level": "N1", "auger_level": "N1", "selected_state": False, "readable_name": "M4N1N1"},
    
    "M5N1N1": {"low_level": "M5", "high_level": "N1", "auger_level": "N1", "selected_state": False, "readable_name": "M5N1N1"},
}  # DicionÃ¡rio onde estÃ£o guardadas as transiÃ§Ãµes Auger. Cada valor do dicionÃ¡rio Ã© em si um dicionÃ¡rio (Nested dictionaries)

chi_sqrd = 0

PCS_radMixValues = []
NCS_radMixValues = []
PCS_augMixValues = []
NCS_augMixValues = []

# ---------------------------------------------------------------------------------------------------------------
def destroy(window):
    window.destroy()


# ---------------------------------------------------------------------------------------------------------------
# FunÃ§Ã£o para dar nome aos ficheiros a gravar
def file_namer(simulation_or_fit, fit_time, extension):
#    dt_string = fit_time.strftime("%d-%m-%Y %H:%M:%S")  # converte a data para string
    dt_string = fit_time.strftime("%d%m%Y_%H%M%S")  # converte a data para string
    file_name = simulation_or_fit + '_from_' + dt_string + extension  # Defino o nome conforme seja fit ou simulaÃ§Ã£o,a data e hora e a extensÃ£o desejada
    return file_name


# ---------------------------------------------------------------------------------------------------------------
# FunÃ§Ã£o para gaurdar os dados dos grÃ¡ifocs simulados em excel
def write_to_xls(type_t, xfinal, yfinal, yfinals, ytot, enoffset, y0, exp_x, exp_y, residues_graph, radiative_files, auger_files, label1, date_and_time):
    print(date_and_time)
    file_title = file_namer("Simulation",date_and_time,".csv")
    first_line = ['Energy (eV)']  # Crio aquela que vai ser a primeira linha da matriz. Crio sÃ³ a primeira coluna e depois adiciono as outras
    
    if enoffset != 0:
        first_line += ['Energy Off (eV)'] #adicionar a coluna com o offset de energia calculado
    
    if y0 != 0:
        first_line += ['Intensity Off'] #adicionar a coluna com o offset de energia calculado
    
    # ---------------------------------------------------------------------------------------------------------------
    # Corro o dicionÃ¡rio e se a transiÃ§Ã£o estiver selecionada e tiver dados, adiciono o seu nome Ã  primeira linha. Idem para as satÃ©lites
    if type_t != 'Auger':
        for index, transition in enumerate(the_dictionary):
            if the_dictionary[transition]["selected_state"]:
                if max(yfinal[index]) != 0:
                    first_line += [the_dictionary[transition]["readable_name"]]
                for l, m in enumerate(yfinals[index]):
                    if max(m) != 0:
                        first_line += [the_dictionary[transition]["readable_name"] + '-' + labeldict[label1[l]]]
    else:
        for index, transition in enumerate(the_aug_dictionary):
            if the_aug_dictionary[transition]["selected_state"]:
                if max(yfinal[index]) != 0:
                    first_line += [the_aug_dictionary[transition]["readable_name"]]
                for l, m in enumerate(yfinals[index]):
                    if max(m) != 0:
                        first_line += [the_aug_dictionary[transition]["readable_name"] + '-' + labeldict[label1[l]]]
    # ---------------------------------------------------------------------------------------------------------------
    first_line += ['Total']  # Adiciono a ultima coluna que terÃ¡ o total
    
    if exp_x != None and exp_y != None:
        first_line += ['Exp Energy (eV)', 'Intensity']
    
    if residues_graph != None:
        first_line += ['Residues (arb. units)', 'std+', 'std-', '', 'red chi 2']
    
    if len(PCS_radMixValues) > 0 or len(NCS_radMixValues) > 0 or len(PCS_augMixValues) > 0 or len(NCS_augMixValues) > 0:
        first_line += ['', 'Charge States', 'Percentage']
    
    if exp_x != None:
        matrix = [[None for x in range(len(first_line))] for y in range(max(len(xfinal), len(exp_x)))]
    else:
        matrix = [[None for x in range(len(first_line))] for y in range(len(xfinal))]  # Crio uma matriz vazia com o numero de colunas= tamanho da primeira linha e o numero de linhas = numero de pontos dos grÃ¡ficos
    # ---------------------------------------------------------------------------------------------------------------
    #  Preencho a primeira e segunda coluna com os valores de x e x + offset
    transition_columns = 1  # comeÃ§a no 1 porque a coluna 0 Ã© a dos valores de x. Uso esta variÃ¡vel para ir avanÃ§ando nas colunas
    
    if enoffset != 0:
        for i, x in enumerate(xfinal):
            matrix[i][0] = x
            matrix[i][1] = x + enoffset
        
        transition_columns += 1
    else:
        for i, x in enumerate(xfinal):
            matrix[i][0] = x
    # ---------------------------------------------------------------------------------------------------------------
    # Preencho as colunas dos valores yy
    for i, y in enumerate(yfinal):  # Corro todas as transiÃ§Ãµes
        if max(y) != 0 or any(yfinals[i]) != 0:  # Se houver diagrama ou satÃ©lite
            for row in range(len(y)):  # Corro todos os valores da diagrama e adiciono-os Ã  linha correspondente
                matrix[row][transition_columns] = y[row]
            if max(y) != 0:  # NÃ£o tenho a certeza que este if Ã© necessÃ¡rio porque acho que jÃ¡ verifiquei isto antes
                transition_columns += 1
            for j, ys in enumerate(yfinals[i]):  # Mesma ideia que para a diagrama
                if max(ys) != 0:
                    for row in range(len(y)):
                        matrix[row][transition_columns] = ys[row]
                    transition_columns += 1
    # ---------------------------------------------------------------------------------------------------------------
    # Preencho os valores de ytotal
    if enoffset != 0:
        for j in range(len(ytot)):
            matrix[j][transition_columns] = ytot[j]
            matrix[j][transition_columns] = ytot[j] + y0
    
        transition_columns += 1
    else:
        for j in range(len(ytot)):
            matrix[j][transition_columns] = ytot[j]
    
    transition_columns += 1
    # ---------------------------------------------------------------------------------------------------------------
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
        lines = residues_graph.get_lines()
        sigp, sigm, res = lines[0].get_ydata(), lines[1].get_ydata(), lines[2].get_ydata()
        
        for i in range(len(exp_x)):
            matrix[i][transition_columns] = res[i]
            matrix[i][transition_columns + 1] = sigp[i]
            matrix[i][transition_columns + 2] = sigm[i]
    
        matrix[0][transition_columns + 4] = chi_sqrd
        
        transition_columns += 5
    # ---------------------------------------------------------------------------------------------------------------
    if type_t != 'Auger':
        if len(PCS_radMixValues) > 0 or len(NCS_radMixValues) > 0:
            idx_p = 0
            idx_n = 0
            for i, cs in enumerate(radiative_files):
                matrix[i][transition_columns + 1] = cs.split('-intensity_')[1].split('.out')[0] + '_'
                
                if '+' in cs:
                    matrix[i][transition_columns + 2] = PCS_radMixValues[idx_p].get()
                    idx_p += 1
                else:
                    matrix[i][transition_columns + 2] = NCS_radMixValues[idx_n].get()
                    idx_n += 1
    else:
        if len(PCS_augMixValues) > 0 or len(NCS_augMixValues) > 0:
            idx_p = 0
            idx_n = 0
            
            matrix[1][transition_columns + 1] = "Auger Mix Values"
            
            for i, cs in enumerate(auger_files):
                matrix[i + 1][transition_columns + 1] = cs.split('-augrate_')[1].split('.out')[0] + '_'
                
                if '+' in cs:
                    matrix[i + 1][transition_columns + 2] = PCS_augMixValues[idx_p].get()
                    idx_p += 1
                else:
                    matrix[i + 1][transition_columns + 2] = NCS_augMixValues[idx_n].get()
                    idx_n += 1
    # ---------------------------------------------------------------------------------------------------------------
    matrix = [first_line] + matrix  # Adiciono a linha com os nomes das trnaisÃ§Ãµes Ã  matriz
    # ---------------------------------------------------------------------------------------------------------------
    # Util para imprimir a matriz na consola e fazer testes
    # for row in matrix:
    #     print(' '.join(map(str, row)))
    # ---------------------------------------------------------------------------------------------------------------
    # Escrita para o ficheiro. Se for a primeira linha da matriz, abrimos como write, se nÃ£o, abrimos como append porque sÃ³ queremos adicionar ao fim do ficheiro
    for i, item in enumerate(matrix):
        if i == 0:
            with open(file_title, 'w', newline='') as csvfile:
                w1 = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                w1.writerow(matrix[i])
        else:
            with open(file_title, 'a', newline='') as csvfile2:
                w1 = csv.writer(csvfile2, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                w1.writerow(matrix[i])
    messagebox.showinfo("File Saved", "Data file has been saved")


# ---------------------------------------------------------------------------------------------------------------
# FunÃ§Ãµes que fazem o cÃ¡lculo das riscas a ser plotadas FALTA: Mal explicado e sem comentÃ¡rios nas funÃ§Ãµes em si
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
        y[i] = np.real(intens * wofz(complex(T[i] - energy, width/2) / sigma / np.sqrt(2))) / sigma \
               / np.sqrt(2 * np.pi)
    return (y)


# ---------------------------------------------------------------------------------------------------------------
# FunÃ§Ã£o que corre depois de escolher a opÃ§Ã£o na janela que surge depois da tabela periÃ³dica
def calculate(element, ap, parent):
    time_of_click = datetime.now()  # Obtenho o a data e hora exacta para dar nome aos ficheiros a gravar
    # Em versÃµes anteriores recebiamos apenas o z do elemento, mas para poder ter acesso ao nome, recebe-se um vetor com nome e numero
    z = element[0]
    element_name = element[1]
    # print(z, element_name)
    if ap == 1:
        yields_file = dir_path / str(z) / (str(z) + '-yields.out')  # Caminho do ficheiro na pasta com o nome igual ao numero atomico que tem as yields
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
            ttk.Button(master=atdatayields, text='Back', command=lambda: destroy(atdata)).grid(column=12, row=1, sticky=W, columnspan=2)  # botao que destroi esta janela
            ttk.Button(master=atdatayields, text='Exit', command=lambda: destroy(atdata)).grid(column=12, row=2, sticky=W, columnspan=2)  # botao que destroi esta janela

            NR = False  # Variavel que diz se ja se esta a ler a parte nao radiativa do ficheiro yields
            n1 = 1  # contadores para escrever os yields em linhas sequencialmente distribuidas
            n2 = 1
            n3 = 1
            for i, j in enumerate(lineyields):  # Ciclo sobre todas as linhas do ficheiro yields para ler todos os yields FY, AY, CKY
                # print(j)
                # print(j[0])
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
    elif ap == 2:
        try:
            radrates_file = dir_path / str(z) / (str(z) + '-radrate.out')  # Caminho do ficheiro na pasta com o nome igual ao numero atomico que tem as yields
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
            ttk.Button(master=atdatayields, text='Back', command=lambda: destroy(atdata)).grid(column=12, row=1, sticky=W, columnspan=2)  # botao que destroi esta janela
            ttk.Button(master=atdatayields, text='Exit', command=lambda: destroy(atdata)).grid(column=12, row=2, sticky=W, columnspan=2)  # botao que destroi esta janela
        except FileNotFoundError:
            messagebox.showerror("Error", "Required File is Missing")
    # ---------------------------------------------------------------------------------------------------------------
    elif ap == 3:
        messagebox.showwarning("Not Possible", "Function not defined")
    # ---------------------------------------------------------------------------------------------------------------
    elif ap == 4:  # OpÃ§Ã£o Spectra Simulation
        radrates_file = dir_path / str(z) / (str(z) + '-intensity.out')  # Caminho do ficheiro na pasta com o nome igual ao numero atomico que tem as intensidades
        try:
            with open(radrates_file, 'r') as radrates:  # Abrir o ficheiro
                lineradrates = [x.strip('\n').split() for x in radrates.readlines()]  # Escrever todas as linhas no ficheiro como uma lista
                lineradrates = list(filter(None, lineradrates))  # Remover as linhas compostas apenas por celulas vazias
                del lineradrates[0:2]
        except FileNotFoundError:
            messagebox.showwarning("Error", "Diagram File is not Avaliable")

        satellites_file = dir_path / str(z) / (str(z) + '-satinty.out')  # Caminho do ficheiro na pasta com o nome igual ao numero atomico que tem as satelites
        try:
            with open(satellites_file, 'r') as satellites:  # Abrir o ficheiro
                linesatellites = [x.strip('\n').split() for x in satellites.readlines()]  # Escrever todas as linhas no ficheiro como uma lista
                linesatellites = list(filter(None, linesatellites))  # Remover as linhas compostas apenas por celulas vazias
                del linesatellites[0:2]  # Tira as linhas que tÃªm o nome das variÃ¡veis e etc
        except FileNotFoundError:
            messagebox.showwarning("Error", "Satellites File is not Avaliable")

        augrates_file = dir_path / str(z) / (str(z) + '-augrate.out')  # Caminho do ficheiro na pasta com o nome igual ao numero atomico que tem as satelites
        try:
            with open(augrates_file, 'r') as augrates:  # Abrir o ficheiro
                lineauger = [x.strip('\n').split() for x in augrates.readlines()]  # Escrever todas as linhas no ficheiro como uma lista
                lineauger = list(filter(None, lineauger))  # Remover as linhas compostas apenas por celulas vazias
                del lineauger[0:2]  # Tira as linhas que tÃªm o nome das variÃ¡veis e etc
        except FileNotFoundError:
            messagebox.showwarning("Error", "Auger Rates File is not Avaliable")

        shakeweights_file = dir_path / str(z) / (str(z) + '-shakeweights.out')  # Caminho do ficheiro na pasta com o nome igual ao numero atomico que tem as satelites
        try:
            with open(shakeweights_file, 'r') as shakeweights_f:  # Abrir o ficheiro
                shakeweights_m = [x.strip('\n').split(',') for x in shakeweights_f.readlines()]  # Escrever todas as linhas no ficheiro como uma lista
                shakeweights = []
                label1 = []
                for i, j in enumerate(shakeweights_m):
                    # Neste for corremos as linhas todas guardadas em shakeweights_m e metemos os valores numÃ©ricos no shakeweights
                    shakeweights.append(float(shakeweights_m[i][1]))
                for k, l in enumerate(shakeweights_m):
                    # Neste for corremos as linhas todas guardadas em shakeweights_m e metemos os rotulos no label 1
                    label1.append(shakeweights_m[k][0])
        except FileNotFoundError:
            messagebox.showwarning("Error", "Shake Weigth File is not Avaliable")
        
        CS_exists = False # Flag para ativar ou desativar a opção no menu (algures nas linhas ~1500)
        Ionpop_exists = False
        if os.path.isdir(dir_path / str(z) / 'Charge_States'): # Verificar se existe a pasta com os varios CS para o atomo escolhido
            CS_exists = True
            radiative_files = [f for f in os.listdir(dir_path / str(z) / 'Charge_States') if os.path.isfile(os.path.join(dir_path / str(z) / 'Charge_States', f)) and '-intensity_' in f]
            
            lineradrates_PCS = []
            lineradrates_NCS = []
            
            rad_PCS = []
            rad_NCS = []
            
            for radfile in radiative_files:
                rad_tmp_file = dir_path / str(z) / 'Charge_States' / radfile  # Caminho do ficheiro na pasta com o nome igual ao numero atomico que tem as intensidades
                try:
                    with open(rad_tmp_file, 'r') as radrates:  # Abrir o ficheiro
                        if '+' in radfile:
                            lineradrates_PCS.append([x.strip('\n').split() for x in radrates.readlines()])  # Escrever todas as linhas no ficheiro como uma lista
                            lineradrates_PCS[-1] = list(filter(None, lineradrates_PCS[-1]))  # Remover as linhas compostas apenas por celulas vazias
                            del lineradrates_PCS[-1][0:2]
                            rad_PCS.append('+' + radfile.split('+')[1].split('.')[0])
                        else:
                            lineradrates_NCS.append([x.strip('\n').split() for x in radrates.readlines()])  # Escrever todas as linhas no ficheiro como uma lista
                            lineradrates_NCS[-1] = list(filter(None, lineradrates_NCS[-1]))  # Remover as linhas compostas apenas por celulas vazias
                            del lineradrates_NCS[-1][0:2]
                            rad_NCS.append('-' + radfile.split('-')[1].split('.')[0])
                except FileNotFoundError:
                    messagebox.showwarning("Error", "Charge State File is not Avaliable: " + radfile)
            
            auger_files = [f for f in os.listdir(dir_path / str(z) / 'Charge_States') if os.path.isfile(os.path.join(dir_path / str(z) / 'Charge_States', f)) and '-augrate_' in f]
            
            lineaugrates_PCS = []
            lineaugrates_NCS = []
            
            aug_PCS = []
            aug_NCS = []
            
            for augfile in auger_files:
                aug_tmp_file = dir_path / str(z) / 'Charge_States' / augfile  # Caminho do ficheiro na pasta com o nome igual ao numero atomico que tem as intensidades
                try:
                    with open(aug_tmp_file, 'r') as augrates:  # Abrir o ficheiro
                        if '+' in augfile:
                            lineaugrates_PCS.append([x.strip('\n').split() for x in augrates.readlines()])  # Escrever todas as linhas no ficheiro como uma lista
                            lineaugrates_PCS[-1] = list(filter(None, lineaugrates_PCS[-1]))  # Remover as linhas compostas apenas por celulas vazias
                            del lineaugrates_PCS[-1][0:2]
                            aug_PCS.append('+' + radfile.split('+')[1].split('.')[0])
                        else:
                            lineaugrates_NCS.append([x.strip('\n').split() for x in augrates.readlines()])  # Escrever todas as linhas no ficheiro como uma lista
                            lineaugrates_NCS[-1] = list(filter(None, lineaugrates_NCS[-1]))  # Remover as linhas compostas apenas por celulas vazias
                            del lineaugrates_NCS[-1][0:2]
                            aug_NCS.append('-' + radfile.split('-')[1].split('.')[0])
                except FileNotFoundError:
                    messagebox.showwarning("Error", "Charge State File is not Avaliable: " + augfile)
            
            sat_files = [f for f in os.listdir(dir_path / str(z) / 'Charge_States') if os.path.isfile(os.path.join(dir_path / str(z) / 'Charge_States', f)) and '-satinty_' in f]
            
            linesatellites_PCS = []
            linesatellites_NCS = []
            
            sat_PCS = []
            sat_NCS = []
            
            for satfile in sat_files:
                sat_tmp_file = dir_path / str(z) / 'Charge_States' / satfile  # Caminho do ficheiro na pasta com o nome igual ao numero atomico que tem as intensidades
                try:
                    with open(sat_tmp_file, 'r') as satrates:  # Abrir o ficheiro
                        if '+' in satfile:
                            linesatellites_PCS.append([x.strip('\n').split() for x in satrates.readlines()])  # Escrever todas as linhas no ficheiro como uma lista
                            linesatellites_PCS[-1] = list(filter(None, linesatellites_PCS[-1]))  # Remover as linhas compostas apenas por celulas vazias
                            del linesatellites_PCS[-1][0:2]
                            sat_PCS.append('+' + satfile.split('+')[1].split('.')[0])
                        else:
                            linesatellites_NCS.append([x.strip('\n').split() for x in satrates.readlines()])  # Escrever todas as linhas no ficheiro como uma lista
                            linesatellites_NCS[-1] = list(filter(None, linesatellites_NCS[-1]))  # Remover as linhas compostas apenas por celulas vazias
                            del linesatellites_NCS[-1][0:2]
                            sat_NCS.append('-' + satfile.split('-')[1].split('.')[0])
                except FileNotFoundError:
                    messagebox.showwarning("Error", "Charge State File is not Avaliable: " + satfile)
            
            if len(linesatellites_NCS) != len(lineradrates_NCS) or len(linesatellites_PCS) != len(lineradrates_PCS):
                messagebox.showwarning("Error", "Missmatch of radiative and satellite files for Charge State mixture: " + str(len(lineradrates_NCS) + len(lineradrates_PCS)) + " radiative and " + str(len(linesatellites_NCS) + len(linesatellites_PCS)) + " satellite files found.")
            
            ionpop_file = dir_path / str(z) / (str(z) + '-ionpop.out')  # Caminho do ficheiro na pasta com o nome igual ao numero atomico que tem as satelites
            try:
                with open(ionpop_file, 'r') as ionpop:  # Abrir o ficheiro
                    ionpopdata = [x.strip('\n').split() for x in ionpop.readlines()]  # Escrever todas as linhas no ficheiro como uma lista
                    ionpopdata = list(filter(None, ionpopdata))  # Remover as linhas compostas apenas por celulas vazias
                Ionpop_exists = True
            except FileNotFoundError:
                messagebox.showwarning("Error", "Ion Population File is not Avaliable")
        
        # ---------------------------------------------------------------------------------------------------------------
        # Criamos uma nova janela onde aparecerÃ£o os grÃ¡ficostodos (TopLevel porque nÃ£o podem haver duas janelas tk abertas ao mesmo tempo)
        # E definimos o seu titulo
        sim = Toplevel(master=parent)
        sim.title("Spectrum Simulation")
        # Criamos um "panel" onde vamos colocar o canvas para fazer o plot do grÃ¡fico. Panels sÃ£o necessÃ¡rios para a janela poder mudar de tamanho
        panel_1 = PanedWindow(sim, orient=VERTICAL)
        panel_1.pack(fill=BOTH, expand=1)
        # ---------------------------------------------------------------------------------------------------------------
        # Figura onde o grÃ¡fico vai ser desenhado
        f = Figure(figsize=(10, 5), dpi=100)  # canvas para o grafico do espectro
        # plt.style.use('ggplot') Estilo para os plots
        a = f.add_subplot(111)  # zona onde estara o grafico
        a.set_xlabel('Energy (eV)')
        a.set_ylabel('Intensity (arb. units)')
        # ---------------------------------------------------------------------------------------------------------------
        # Frames onde se vÃ£o por a figura e os labels e botÃµes e etc
        figure_frame = Frame(panel_1, relief=GROOVE)  # frame para o grafico
        panel_1.add(figure_frame)
        canvas = FigureCanvasTkAgg(f, master=figure_frame)
        canvas.get_tk_widget().pack(fill=BOTH, expand=1)

        panel_2 = PanedWindow(sim, orient=VERTICAL)
        panel_2.pack(fill=X, expand=0)

        toolbar_frame = Frame(panel_2, bd=1, relief=GROOVE)
        panel_2.add(toolbar_frame)
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)

        full_frame = Frame(panel_2, relief=GROOVE)  # Frame transiÃ§Ãµes
        panel_2.add(full_frame)
        buttons_frame = Frame(full_frame, bd=1, relief=GROOVE)  # Frame transiÃ§Ãµes
        buttons_frame.pack(fill=BOTH, expand=1)
        buttons_frame2 = Frame(full_frame, bd=1, relief=GROOVE)  # Max, min & Points Frame
        buttons_frame2.pack(fill=BOTH, expand=1)
        buttons_frame3 = Frame(full_frame, bd=1, relief=GROOVE)  # Frame  yoffset, Energy offset e Calculate
        buttons_frame3.pack(fill=BOTH, expand=1)
        buttons_frame4 = Frame(full_frame)  # Frame Barra Progresso
        buttons_frame4.pack(fill=BOTH, expand=1)

        # ---------------------------------------------------------------------------------------------------------------
        # VariÃ¡veis
        totalvar = StringVar()  # VariÃ¡vel que define se apresentamos o ytot(soma de todas as riscas) no grÃ¡fico
        totalvar.set('No')  # inicializamos Total como nÃ£o, porque sÃ³ se apresenta se o utilizador escolher manualmente
        yscale_log = StringVar()  # VariÃ¡vel que define se o eixo y Ã© apresentado com escala logaritmica ou nÃ£o
        yscale_log.set('No')  # Inicializamos a No porque sÃ³  se apresenta assim se o utilizador escolher manualmente
        xscale_log = StringVar()  # VariÃ¡vel que define se o eixo y Ã© apresentado com escala logaritmica ou nÃ£o
        xscale_log.set('No')  # Inicializamos a No porque sÃ³  se apresenta assim se o utilizador escolher manualmente
        autofitvar = StringVar()  # VariÃ¡vel que define se o fit se faz automÃ¡ticamente ou nÃ£o
        autofitvar.set('No')  # Inicializamos a No porque sÃ³ faz fit automÃ¡tico se o utilizador quiser
        normalizevar = StringVar()  # VariÃ¡vel que define como se normalizam os grÃ¡ficos (3 opÃ§Ãµes atÃ© agora: nÃ£o normalizar, normalizar Ã  unidade, ou ao mÃ¡ximo do espectro experimental)
        normalizevar.set('No')  # inicializamos Normalize a no, porque sÃ³ se normaliza se o utilizador escolher
        loadvar = StringVar()  # VariÃ¡vel que define se se carrega um expectro experimental. A string, caso se queira carregar o espectro, muda para o path do ficheiro do espectro
        loadvar.set('No')  # inicializamos Load a no, porque sÃ³ se carrega ficheiro se o utilizador escolher
        effic_var = StringVar()
        effic_var.set("No")

        exp_resolution = DoubleVar(value=1.0)  # Float correspondente a resolucao experimental
        yoffset = DoubleVar(value=0.0)  # Float correspondente ao fundo experimental
        energy_offset = DoubleVar(value=0.0)  # Float correspondente a resolucao experimental
        number_points = IntVar(value=500)  # Numero de pontos a plotar na simulaÃ§Ã£o
        x_max = StringVar()  # Controlo do x MÃ¡ximo a entrar no grÃ¡fico
        x_max.set('Auto')
        x_min = StringVar()  # Controlo do x MÃ­nimo a entrar no grÃ¡fico
        x_min.set('Auto')
        progress_var = DoubleVar()  # Float que da a percentagem de progresso

        global transition_list  # Usada na funÃ§Ã£o Selected
        transition_list = []
        label_text = StringVar()  # Texto com as transiÃ§Ãµes selecionadas a apresentar no ecrÃ£
        label_text.set('Select a Transition: ')  # Antes de se selecionar alguma transiÃ§Ã£o aparece isto
        trans_lable = Label(buttons_frame, textvariable=label_text).grid(row=0, column=1)

        # ---------------------------------------------------------------------------------------------------------------
        # FunÃ§Ã£o para alterar o estado de uma transiÃ§Ã£o que seja selecionada na GUI
        def dict_updater(transition):
            if satelite_var.get() != 'Auger':
                # O "Estado actual" que as riscas tÃªm quando esta funÃ§Ã£o corre Ã© o oposto daquele que estÃ¡ definido no dicionÃ¡rio, porque a funÃ§Ã£o sÃ³ corre se clicarmos para mudar
                current_state = not the_dictionary[transition]["selected_state"]
                # Alteramos o estado das riscas para o estado actual
                the_dictionary[transition]["selected_state"] = current_state
            else:
                # O "Estado actual" que as riscas tÃªm quando esta funÃ§Ã£o corre Ã© o oposto daquele que estÃ¡ definido no dicionÃ¡rio, porque a funÃ§Ã£o sÃ³ corre se clicarmos para mudar
                current_state = not the_aug_dictionary[transition]["selected_state"]
                # Alteramos o estado das riscas para o estado actual
                the_aug_dictionary[transition]["selected_state"] = current_state

        # ---------------------------------------------------------------------------------------------------------------
        # FunÃ§Ãµes
        def detector_efficiency(energy_values, efficiency_values, xfinal, enoffset):
            interpolated_effic = [0 for i in range(len(xfinal))]
            effic_interpolation = interp1d(energy_values, np.array(efficiency_values)/100)
            for i, energy in enumerate(xfinal+enoffset):
                interpolated_effic[i] = effic_interpolation(energy)
                print(interpolated_effic[i], energy)
            return interpolated_effic

        def normalizer(y0, expy_max, ytot_max):
            normalize = normalizevar.get()
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

        def y_calculator(transition_type, fit_type, xfinal, x, y, w, xs, ys, ws, res, energy_values, efficiency_values,enoffset):
            global ytot, yfinal, yfinals
            yfinal = [[0 for i in range(len(xfinal))] for j in range(len(x))]  # Criar uma lista de listas cheia de zeros que ira ser o yfinal para diagrama
            ytot = [0 for i in range(len(xfinal))]
            yfinals = [[[0 for n in range(len(xfinal))] for i in label1] for j in range(len(xs))]  # Criar uma lista de listas cheia de zeros que ira ser o yfinal para satellites
            if transition_type == 'Diagram':
                b1 = 0
                for j, k in enumerate(y):
                    # Ciclo sobre todas as riscas para somar um pico (voigt, lorentz ou gauss) para cada individual
                    for i, n in enumerate(k):
                        if fit_type == 'Voigt':
                            yfinal[j] = np.add(yfinal[j], V(xfinal, x[j][i], y[j][i], res, w[j][i]))
                        elif fit_type == 'Lorentzian':
                            yfinal[j] = np.add(yfinal[j], L(xfinal, x[j][i], y[j][i], res, w[j][i]))
                        elif fit_type == 'Gaussian':
                            yfinal[j] = np.add(yfinal[j], G(xfinal, x[j][i], y[j][i], res, w[j][i]))
                        b1 += 100 / (len(y) * len(k))
                        progress_var.set(b1)
                        sim.update_idletasks()
                    if k != []:  # Excluir as linhas que nao foram seleccionados nos botoes
                        ytot = np.add(ytot, yfinal[j])

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
                                yfinals[j][l] = np.add(yfinals[j][l], V(xfinal, xs[j][l][i], ys[j][l][i], res, ws[j][l][i]))
                            elif fit_type == 'Lorentzian':
                                yfinals[j][l] = np.add(yfinals[j][l], L(xfinal, xs[j][l][i], ys[j][l][i], res, ws[j][l][i]))
                            elif fit_type == 'Gaussian':
                                yfinals[j][l] = np.add(yfinals[j][l], G(xfinal, xs[j][l][i], ys[j][l][i], res, ws[j][l][i]))
                            b1 += 100 / (len(ys) * len(label1) * len(m))
                            progress_var.set(b1)
                            sim.update_idletasks()
                        if m != []:  # Excluir as linhas que nao foram seleccionados nos botoes
                            ytot = np.add(ytot, yfinals[j][l])
                b1 = 100
                progress_var.set(b1)
                sim.update_idletasks()
            elif transition_type == 'Diagram + Satellites':
                b1 = 0
                for j, k in enumerate(y):
                    # Ciclo sobre todas as riscas para somar um pico (voigt, lorentz ou gauss) para cada individual
                    for i, n in enumerate(k):
                        if fit_type == 'Voigt':
                            yfinal[j] = np.abs(np.add(yfinal[j], V(xfinal, x[j][i], y[j][i], res, w[j][i])))
                        elif fit_type == 'Lorentzian':
                            yfinal[j] = np.abs(np.add(yfinal[j], L(xfinal, x[j][i], y[j][i], res, w[j][i])))
                        elif fit_type == 'Gaussian':
                            yfinal[j] = np.abs(np.add(yfinal[j], G(xfinal, x[j][i], y[j][i], res, w[j][i])))
                        b1 += 200 / (len(y) * len(k))
                        progress_var.set(b1)
                        sim.update_idletasks()
                    if k != []:  # Excluir as linhas que nao foram seleccionados nos botoes
                        ytot = np.add(ytot, yfinal[j])

                b1 = 50
                progress_var.set(b1)
                sim.update_idletasks()
                for j, k in enumerate(ys):
                    for l, m in enumerate(ys[j]):
                        # Ciclo sobre todas as riscas para somar um pico (voigt, lorentz ou gauss) para cada individual
                        for i, n in enumerate(m):
                            if fit_type == 'Voigt':
                                yfinals[j][l] = np.abs(np.add(yfinals[j][l], V(xfinal, xs[j][l][i], ys[j][l][i], res, ws[j][l][i])))
                            elif fit_type == 'Lorentzian':
                                yfinals[j][l] = np.abs(np.add(yfinals[j][l], L(xfinal, xs[j][l][i], ys[j][l][i], res, ws[j][l][i])))
                            elif fit_type == 'Gaussian':
                                yfinals[j][l] = np.abs(np.add(yfinals[j][l], G(xfinal, xs[j][l][i], ys[j][l][i], res, ws[j][l][i])))
                            b1 += 100 / (len(ys) * len(label1) * len(m))
                            progress_var.set(b1)
                            sim.update_idletasks()
                        if m != []:  # Excluir as linhas que nao foram seleccionados nos botoes
                            ytot = np.add(ytot, yfinals[j][l])
                b1 = 100
                progress_var.set(b1)
                sim.update_idletasks()
            elif transition_type == 'Auger':
                yfinal = [[0 for i in range(len(xfinal))] for j in range(len(x))]  # Criar uma lista de listas cheia de zeros que ira ser o yfinal para diagrama
                ytot = [0 for i in range(len(xfinal))]
                yfinals = [[[0 for n in range(len(xfinal))] for i in label1] for j in range(len(xs))]  # Criar uma lista de listas cheia de zeros que ira ser o yfinal para satellites
            
                b1 = 0
                for j, k in enumerate(y):
                    # Ciclo sobre todas as riscas para somar um pico (voigt, lorentz ou gauss) para cada individual
                    for i, n in enumerate(k):
                        if fit_type == 'Voigt':
                            yfinal[j] = np.add(yfinal[j], V(xfinal, x[j][i], y[j][i], res, w[j][i]))
                        elif fit_type == 'Lorentzian':
                            yfinal[j] = np.add(yfinal[j], L(xfinal, x[j][i], y[j][i], res, w[j][i]))
                        elif fit_type == 'Gaussian':
                            yfinal[j] = np.add(yfinal[j], G(xfinal, x[j][i], y[j][i], res, w[j][i]))
                        b1 += 100 / (len(y) * len(k))
                        progress_var.set(b1)
                        sim.update_idletasks()
                    if k != []:  # Excluir as linhas que nao foram seleccionados nos botoes
                        ytot = np.add(ytot, yfinal[j])

                b1 = 100
                progress_var.set(b1)
                sim.update_idletasks()
            
            if effic_var.get() != 'No':
                detector_effi = detector_efficiency(energy_values, efficiency_values, xfinal, enoffset)
                return ytot*np.array(detector_effi), yfinal*np.array(detector_effi), yfinals*np.array(detector_effi)
            else:
                return ytot, yfinal, yfinals

        def func2min(params, exp_x, exp_y, num_of_points, sat, peak, x, y, w, xs, ys, ws, energy_values, efficiency_values,enoffset):
            global xfinal
            normalize = normalizevar.get()
            y_interp = [0 for i in range(len(exp_x))]
            xoff = params['xoff']
            y0 = params['yoff']
            res = params['res']
            ytot_max = params['ytot_max']
            xfinal = np.array(np.linspace(min(exp_x) - xoff, max(exp_x) - xoff, num=num_of_points))
            ytot, yfinal, yfinals = y_calculator(sat, peak, xfinal, x, y, w, xs, ys, ws, res, energy_values, efficiency_values,enoffset)
            normalization_var = normalizer(y0, max(exp_y), ytot_max)
            # print(xoff, res, y0, normalization_var)
            # print(xoff, res, y0, ytot_max)
            f_interpolate = interp1d(xfinal + xoff, np.array(ytot * normalization_var) + y0, kind='cubic')  # Falta adicionar o y0
            for g, h in enumerate(exp_x):
                # Obtemos o valor de y interpolado pela funÃ§Ã£o definida a cima
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
            elif spec_type == 'Auger':
                y = [float(row[11]) * (1 - 0.01 * sum(shakeweights)) for row in transition_values]  # *float(row[11])*float(row[9])
                y.insert(0, 0)
                y.append(0)
                a.stem(x, y, markerfmt=' ', linefmt=str(col2[np.random.randint(0, 7)][0]), label=str(transition), use_line_collection=True)
                a.legend(loc='best', numpoints=1)
            elif spec_type == 'Diagram_CS':
                y = [float(row[11]) * (1 - 0.01 * sum(shakeweights)) * float(row[-1]) for row in transition_values]  # *float(row[11])*float(row[9])
                y.insert(0, 0)
                y.append(0)
                a.stem(x, y, markerfmt=' ', linefmt=str(col2[np.random.randint(0, 7)][0]), label=str(transition), use_line_collection=True)
                a.legend(loc='best', numpoints=1)
            elif spec_type == 'Satellites_CS':
                sy_points = [float(float(row[11]) * 0.01 * shakeweights[ind] * float(row[-1])) for row in transition_values]  # *float(row[11])*float(row[9])
                sy_points.insert(0, 0)
                sy_points.append(0)
                a.stem(x, sy_points, markerfmt=' ', linefmt=str(col2[np.random.randint(0, 7)][0]), label=transition + ' - ' + labeldict[key], use_line_collection=True)  # Plot a stemplot
                a.legend(loc='best', numpoints=1)
            elif spec_type == 'Auger_CS':
                y = [float(row[11]) * (1 - 0.01 * sum(shakeweights)) * float(row[-1]) for row in transition_values]  # *float(row[11])*float(row[9])
                y.insert(0, 0)
                y.append(0)
                a.stem(x, y, markerfmt=' ', linefmt=str(col2[np.random.randint(0, 7)][0]), label=str(transition), use_line_collection=True)
                a.legend(loc='best', numpoints=1)
            a.legend(title=element_name, title_fontsize='large')
            # --------------------------------------------------------------------------------------------------------------------------
            # Tratamento da Legenda
            a.legend(title=element_name)
            number_of_labels = len(a.legend().get_texts())  # Descubro quantas entradas vai ter a legenda
            legend_columns = 1  # Inicialmente hÃ¡ uma coluna, mas vou fazer contas para ter 10 itens por coluna no mÃ¡ximo
            labels_per_columns = number_of_labels / legend_columns  # Numero de entradas por coluna
            while labels_per_columns > 10:  # Se a priori for menos de 10 entradas por coluna, nÃ£o acontece nada
                legend_columns += 1  # Se houver mais que 10 entradas por coluna, meto mais uma coluna
                labels_per_columns = number_of_labels / legend_columns  # Recalculo o numero de entradas por coluna
            a.legend(ncol=legend_columns)  # Defino o numero de colunas na legenda = numero de colunas necessÃ¡rias para nÃ£o ter mais de 10 entradas por coluna

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
                # Duas variÃ¡veis que servem para ver se hÃ¡ alguma transiÃ§Ã£o mal escolhida. A primeira serve para saber o numero total de transiÃµes escolhidas e a segunda para anotar quantas tranisÃ§Ãµes erradas se escolheram
                num_of_transitions = 0
                bad_selection = 0
                if sat != 'Auger':
                    for transition in the_dictionary:
                        # Se a transiÃ§Ã£o estiver selecionada:
                        if the_dictionary[transition]["selected_state"]:
                            num_of_transitions += 1
                            # Estas variÃ¡veis servem sÃ³ para nÃ£o ter de escrever o acesso ao valor do dicionÃ¡rio todas as vezes
                            low_level = the_dictionary[transition]["low_level"]
                            high_level = the_dictionary[transition]["high_level"]
                            diag_stick_val = [line for line in lineradrates if line[1] in low_level and line[5] == high_level and float(line[8]) != 0]  # Cada vez que o for corre, lÃª o ficheiro de uma transiÃ§Ã£o
                            # for u in range(len(diag_stick_val)):
                            #     if diag_stick_val[u][1] in low_level:
                            #         print(diag_stick_val[u][1], low_level)
                            sat_stick_val = [line for line in linesatellites if low_level in line[1] and high_level in line[5] and float(line[8]) != 0]
                            # -------------------------------------------------------------------------------------------
                            if sat == 'Diagram':
                                if not diag_stick_val:  # Se nÃ£o ouver dados no vetor da diagrama
                                    diag_stick_val = [['0' for i in range(16)]]  # Crio um vector de zeros para o programa continuar a correr (Em string porque estava a dar um erro qq quando punha em int)(range 16 porque Ã© o tamanho da
                                    # linha do ficheiro que supostamente preencheria este vertor)
                                    messagebox.showwarning("Wrong Transition", transition + " is not Available")  # Mostro no ecrÃ£ a transiÃ§Ã£o errada que escolheram
                                    bad_selection += 1  # incremento o numero de transiÃ§Ãµes "mal" escolhidas
                                stem_ploter(diag_stick_val, transition, 'Diagram', 0, 0)
                            elif sat == 'Satellites':
                                if not sat_stick_val:  # Se nÃ£o ouver nada no vetor das satelites
                                    sat_stick_val = [['0' for i in range(16)]]
                                    messagebox.showwarning("Wrong Transition", transition + " is not Available")  # Mostro no ecrÃ£ a transiÃ§Ã£o errada que escolheram
                                    bad_selection += 1  # incremento o numero de transiÃ§Ãµes "mal" escolhidas
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
                                if not diag_stick_val:  # Se nÃ£o ouver dados no vetor da diagrama
                                    diag_stick_val = [['0' for i in range(16)]]  # Crio um vector de zeros para o programa continuar a correr (Em string porque estava a dar um erro qq quando punha em int)(range 16 porque Ã© o tamanho da
                                    # linha do ficheiro que supostamente preencheria este vertor)
                                    messagebox.showwarning("Wrong Transition", "Diagram info. for " + transition + " is not Available")  # Mostro no ecrÃ£ a transiÃ§Ã£o errada que escolheram
                                    bad_selection += 1  # incremento o numero de transiÃ§Ãµes "mal" escolhidas
                                stem_ploter(diag_stick_val, transition, 'Diagram', 0, 0)
                                if not sat_stick_val:  # Se nÃ£o ouver nada no vetor das satelites
                                    sat_stick_val = [['0' for i in range(16)]]
                                    messagebox.showwarning("Wrong Transition", "Satellites info.  for " + transition + " is not Available")  # Mostro no ecrÃ£ a transiÃ§Ã£o errada que escolheram
                                    bad_selection += 1  # incremento o numero de transiÃ§Ãµes "mal" escolhidas
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
                else:
                    for transition in the_aug_dictionary:
                        # Se a transiÃ§Ã£o estiver selecionada:
                        if the_aug_dictionary[transition]["selected_state"]:
                            num_of_transitions += 1
                            low_level = the_aug_dictionary[transition]["low_level"]
                            high_level = the_aug_dictionary[transition]["high_level"]
                            auger_level = the_aug_dictionary[transition]["auger_level"]
                            
                            aug_stick_val = [line for line in lineauger if low_level in line[1] and high_level in line[5][:2] and auger_level in line[5][2:4] and float(line[8]) != 0]
                            
                            if not aug_stick_val:  # Se nÃ£o ouver dados no vetor da diagrama
                                aug_stick_val = [['0' for i in range(16)]]  # Crio um vector de zeros para o programa continuar a correr (Em string porque estava a dar um erro qq quando punha em int)(range 16 porque Ã© o tamanho da
                                # linha do ficheiro que supostamente preencheria este vertor)
                                messagebox.showwarning("Wrong Transition", "Auger info. for " + transition + " is not Available")  # Mostro no ecrÃ£ a transiÃ§Ã£o errada que escolheram
                                bad_selection += 1  # incremento o numero de transiÃ§Ãµes "mal" escolhidas
                            stem_ploter(aug_stick_val, transition, 'Auger', 0, 0)
                        
                        graph_area.set_xlabel('Energy (eV)')
                        graph_area.set_ylabel('Intensity (arb. units)')
                
                
                if num_of_transitions == 0:
                    messagebox.showerror("No Transition", "No transition was chosen")
                elif bad_selection != 0:
                    messagebox.showerror("Wrong Transition", "You chose " + str(bad_selection) + " invalid transition(s)")
            # --------------------------------------------------------------------------------------------------------------------------
            elif spectype == 'M_Stick':
                # Duas variÃ¡veis que servem para ver se hÃ¡ alguma transiÃ§Ã£o mal escolhida. A primeira serve para saber o numero total de transiÃµes escolhidas e a segunda para anotar quantas tranisÃ§Ãµes erradas se escolheram
                num_of_transitions = 0
                bad_selection = 0
                if sat != 'Auger':
                    charge_states = rad_PCS + rad_NCS
                    
                    for cs_index, cs in enumerate(charge_states):
                        mix_val = '0.0'
                        ncs = False
                        
                        if cs_index < len(rad_PCS):
                            mix_val = PCS_radMixValues[cs_index].get()
                        else:
                            mix_val = NCS_radMixValues[cs_index - len(rad_PCS)].get()
                            ncs = True
                        if mix_val != '0.0':
                            for transition in the_dictionary:
                                # Se a transiÃ§Ã£o estiver selecionada:
                                if the_dictionary[transition]["selected_state"]:
                                    num_of_transitions += 1
                                    # Estas variÃ¡veis servem sÃ³ para nÃ£o ter de escrever o acesso ao valor do dicionÃ¡rio todas as vezes
                                    low_level = the_dictionary[transition]["low_level"]
                                    high_level = the_dictionary[transition]["high_level"]
                                    
                                    if not ncs:
                                        diag_stick_val = [line + [PCS_radMixValues[i].get()] for i, linerad in enumerate(lineradrates_PCS) for line in linerad if line[1] in low_level and line[5] == high_level and float(line[8]) != 0 and rad_PCS[i] == cs]  # Cada vez que o for corre, lÃª o ficheiro de uma transiÃ§Ã£o
                                    else:
                                        diag_stick_val = [line + [NCS_radMixValues[i].get()] for i, linerad in enumerate(lineradrates_NCS) for line in linerad if line[1] in low_level and line[5] == high_level and float(line[8]) != 0 and rad_NCS[i] == cs]
                                    
                                    if not ncs:
                                        sat_stick_val = [line + [PCS_radMixValues[i].get()] for i, linesat in enumerate(linesatellites_PCS) for line in linesat if low_level in line[1] and high_level in line[5] and float(line[8]) != 0 and sat_PCS[i] == cs]
                                    else:
                                        sat_stick_val = [line + [NCS_radMixValues[i].get()] for i, linesat in enumerate(linesatellites_NCS) for line in linesat if low_level in line[1] and high_level in line[5] and float(line[8]) != 0 and sat_NCS[i] == cs]
                                        # -------------------------------------------------------------------------------------------
                                    if sat == 'Diagram':
                                        if not diag_stick_val:  # Se nÃ£o ouver dados no vetor da diagrama
                                            diag_stick_val = [['0' for i in range(16)]]  # Crio um vector de zeros para o programa continuar a correr (Em string porque estava a dar um erro qq quando punha em int)(range 16 porque Ã© o tamanho da
                                            # linha do ficheiro que supostamente preencheria este vertor)
                                            messagebox.showwarning("Wrong Transition", transition + " is not Available for charge state: " + cs)  # Mostro no ecrÃ£ a transiÃ§Ã£o errada que escolheram
                                            bad_selection += 1  # incremento o numero de transiÃ§Ãµes "mal" escolhidas
                                        stem_ploter(diag_stick_val, cs + ' ' + transition, 'Diagram_CS', 0, 0)
                                    elif sat == 'Satellites':
                                        if not sat_stick_val:  # Se nÃ£o ouver nada no vetor das satelites
                                            sat_stick_val = [['0' for i in range(16)]]
                                            messagebox.showwarning("Wrong Transition", transition + " is not Available for charge state: " + cs)  # Mostro no ecrÃ£ a transiÃ§Ã£o errada que escolheram
                                            bad_selection += 1  # incremento o numero de transiÃ§Ãµes "mal" escolhidas
                                        b1 = 0
                                        for ind, key in enumerate(label1):
                                            sat_stick_val_ind1 = [line for line in sat_stick_val if low_level + key in line[1] and key + high_level in line[5]]
                                            sat_stick_val_ind2 = [line for line in sat_stick_val if low_level + key in line[1] and high_level + key in line[5] and key != high_level]
                                            sat_stick_val_ind3 = [line for line in sat_stick_val if key + low_level in line[1] and key + high_level in line[5]]
                                            sat_stick_val_ind4 = [line for line in sat_stick_val if key + low_level in line[1] and high_level + key in line[5] and key != high_level]
                                            sat_stick_val_ind = sat_stick_val_ind1 + sat_stick_val_ind2 + sat_stick_val_ind3 + sat_stick_val_ind4
                                            if len(sat_stick_val_ind) > 1:
                                                stem_ploter(sat_stick_val_ind, cs + ' ' + transition, 'Satellites_CS', ind, key)
                                            b1 += 100 / len(label1)
                                            progress_var.set(b1)
                                            sim.update_idletasks()
                                    elif sat == 'Diagram + Satellites':
                                        if not diag_stick_val:  # Se nÃ£o ouver dados no vetor da diagrama
                                            diag_stick_val = [['0' for i in range(16)]]  # Crio um vector de zeros para o programa continuar a correr (Em string porque estava a dar um erro qq quando punha em int)(range 16 porque Ã© o tamanho da
                                            # linha do ficheiro que supostamente preencheria este vertor)
                                            messagebox.showwarning("Wrong Transition", "Diagram info. for " + transition + " is not Available")  # Mostro no ecrÃ£ a transiÃ§Ã£o errada que escolheram
                                            bad_selection += 1  # incremento o numero de transiÃ§Ãµes "mal" escolhidas
                                        stem_ploter(diag_stick_val, cs + ' ' + transition, 'Diagram_CS', 0, 0)
                                        if not sat_stick_val:  # Se nÃ£o ouver nada no vetor das satelites
                                            sat_stick_val = [['0' for i in range(16)]]
                                            messagebox.showwarning("Wrong Transition", "Satellites info.  for " + transition + " is not Available")  # Mostro no ecrÃ£ a transiÃ§Ã£o errada que escolheram
                                            bad_selection += 1  # incremento o numero de transiÃ§Ãµes "mal" escolhidas
                                        b1 = 0
                                        for ind, key in enumerate(label1):
                                            sat_stick_val_ind1 = [line for line in sat_stick_val if low_level + key in line[1] and key + high_level in line[5]]
                                            sat_stick_val_ind2 = [line for line in sat_stick_val if low_level + key in line[1] and high_level + key in line[5] and key != high_level]
                                            sat_stick_val_ind3 = [line for line in sat_stick_val if key + low_level in line[1] and key + high_level in line[5]]
                                            sat_stick_val_ind4 = [line for line in sat_stick_val if key + low_level in line[1] and high_level + key in line[5] and key != high_level]
                                            sat_stick_val_ind = sat_stick_val_ind1 + sat_stick_val_ind2 + sat_stick_val_ind3 + sat_stick_val_ind4
                                            if len(sat_stick_val_ind) > 1:
                                                stem_ploter(sat_stick_val_ind, cs + ' ' + transition, 'Satellites_CS', ind, key)
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
                            mix_val = PCS_augMixValues[cs_index].get()
                        else:
                            mix_val = NCS_augMixValues[cs_index - len(aug_PCS)].get()
                            ncs = True
                        if mix_val != '0.0':
                            for transition in the_aug_dictionary:
                                # Se a transiÃ§Ã£o estiver selecionada:
                                if the_aug_dictionary[transition]["selected_state"]:
                                    num_of_transitions += 1
                                    low_level = the_aug_dictionary[transition]["low_level"]
                                    high_level = the_aug_dictionary[transition]["high_level"]
                                    auger_level = the_aug_dictionary[transition]["auger_level"]
                                    
                                    if not ncs:
                                        aug_stick_val = [line + [PCS_augMixValues[i].get()] for i, lineaug in enumerate(lineaugrates_PCS) for line in lineaug if low_level in line[1] and high_level in line[5][:2] and auger_level in line[5][2:4] and float(line[8]) != 0 and aug_PCS[i] == cs]
                                    else:
                                        aug_stick_val = [line + [NCS_augMixValues[i].get()] for i, lineaug in enumerate(lineaugrates_NCS) for line in lineaug if low_level in line[1] and high_level in line[5][:2] and auger_level in line[5][2:4] and float(line[8]) != 0 and aug_PCS[i] == cs]
                                    
                                    if not aug_stick_val:  # Se nÃ£o ouver dados no vetor da diagrama
                                        aug_stick_val = [['0' for i in range(16)]]  # Crio um vector de zeros para o programa continuar a correr (Em string porque estava a dar um erro qq quando punha em int)(range 16 porque Ã© o tamanho da
                                        # linha do ficheiro que supostamente preencheria este vertor)
                                        messagebox.showwarning("Wrong Transition", "Auger info. for " + transition + " is not Available for charge state: " + cs)  # Mostro no ecrÃ£ a transiÃ§Ã£o errada que escolheram
                                        bad_selection += 1  # incremento o numero de transiÃ§Ãµes "mal" escolhidas
                                    stem_ploter(aug_stick_val, cs + ' ' + transition, 'Auger_CS', 0, 0)
                                
                                graph_area.set_xlabel('Energy (eV)')
                                graph_area.set_ylabel('Intensity (arb. units)')
                
                
                if num_of_transitions == 0:
                    messagebox.showerror("No Transition", "No transition was chosen")
                elif bad_selection != 0:
                    messagebox.showerror("Wrong Transition", "You chose " + str(bad_selection) + " invalid transition(s)")
            # --------------------------------------------------------------------------------------------------------------------------
            elif spectype == 'Simulation':
                # VariÃ¡vel para contar as transiÃ§Ãµes erradas
                bad_selection = 0
                
                if sat != 'Auger':
                    # -------------------------------------------------------------------------------------------
                    # Leitura dos valores das transiÃ§Ãµes selecionadas
                    # Contrariamente ao spectype == 'Stick' onde os plots sÃ£o feitos quando se trata de cada risca, aqui,
                    # o  que se faz Ã© obter os valores necessÃ¡rios para os plots. NÃ£o se faz nenhum plot em si dentro deste ciclo.
                    for index, transition in enumerate(the_dictionary):
                        if the_dictionary[transition]["selected_state"]:
                            low_level = the_dictionary[transition]["low_level"]  # orbital da lacuna no inÃ­cio da transiÃ§Ã£o
                            high_level = the_dictionary[transition]["high_level"]  # orbital da lacuna no fim da transiÃ§Ã£o
                            diag_sim_val = [line for line in lineradrates if line[1] in low_level and line[5] == high_level and float(line[8]) != 0]  # Guarda para uma lista as linhas do ficheiro que se referem Ã  trasiÃ§Ã£o transition
                            sat_sim_val = [line for line in linesatellites if low_level in line[1] and high_level in line[5] and float(line[8]) != 0]  # Guarda para uma lista as linhas do ficheiro que se referem Ã s satÃ©lites de transition
                            
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
                                    sat_sim_val_ind2 = [line for line in sat_sim_val if low_level + key in line[1] and high_level + key in line[5] and key != high_level]
                                    sat_sim_val_ind3 = [line for line in sat_sim_val if key + low_level in line[1] and key + high_level in line[5]]
                                    sat_sim_val_ind4 = [line for line in sat_sim_val if key + low_level in line[1] and high_level + key in line[5] and key != high_level]
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
                                ka1s = [line for line in linesatellites if 'K1' in line[1] and 'L3' in line[5] and float(line[8]) != 0]
                                for ind, key in enumerate(label1):
                                    sat_sim_val_ind1 = [line for line in sat_sim_val if low_level + key in line[1] and key + high_level in line[5]]
                                    sat_sim_val_ind2 = [line for line in sat_sim_val if low_level + key in line[1] and high_level + key in line[5] and key != high_level]
                                    sat_sim_val_ind3 = [line for line in sat_sim_val if key + low_level in line[1] and key + high_level in line[5]]
                                    sat_sim_val_ind4 = [line for line in sat_sim_val if key + low_level in line[1] and high_level + key in line[5] and key != high_level]
                                    sat_sim_val_ind = sat_sim_val_ind1 + sat_sim_val_ind2 + sat_sim_val_ind3 + sat_sim_val_ind4
                                    if len(sat_sim_val_ind) > 1:
                                        x1s = [float(row[8]) for row in sat_sim_val_ind]
                                        y1s = [float(float(row[11]) * shakeweights[ind]) for row in sat_sim_val_ind]
                                        w1s = [float(row[15]) for row in sat_sim_val_ind]
                                        xs[index][ind] = x1s
                                        ys[index][ind] = y1s
                                        ws[index][ind] = w1s
                    # -------------------------------------------------------------------------------------------
                    # Verificar se se selecionaram transiÃ§Ãµes indÃ­sponÃ­veis
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
                    xs = [[[] for i in label1] for j in x]
                    ys = [[[] for i in label1] for j in y]
                    ws = [[[] for i in label1] for j in w]
                    
                    for index, transition in enumerate(the_aug_dictionary):
                        if the_aug_dictionary[transition]["selected_state"]:
                            low_level = the_aug_dictionary[transition]["low_level"]  # orbital da lacuna no inÃ­cio da transiÃ§Ã£o
                            high_level = the_aug_dictionary[transition]["high_level"]  # orbital da lacuna no fim da transiÃ§Ã£o
                            auger_level = the_aug_dictionary[transition]["auger_level"]
                            
                            aug_sim_val = [line for line in lineauger if low_level in line[1] and high_level in line[5][:2] and auger_level in line[5][2:4] and float(line[8]) != 0]  # Guarda para uma lista as linhas do ficheiro que se referem Ã  trasiÃ§Ã£o transition
                            
                            x1 = [float(row[8]) for row in aug_sim_val]
                            y1 = [float(row[9]) * (1 - sum(shakeweights)) for row in aug_sim_val]
                            w1 = [float(row[10]) for row in aug_sim_val]
                            x[index] = x1
                            y[index] = y1
                            w[index] = w1
                    
                    # -------------------------------------------------------------------------------------------
                    # Verificar se se selecionaram transiÃ§Ãµes indÃ­sponÃ­veis
                    for index, transition in enumerate(the_aug_dictionary):
                        if the_aug_dictionary[transition]["selected_state"]:
                            if not x[index]:
                                messagebox.showwarning("Wrong Auger Transition", transition + " is not Available")
                                x[index] = []
                                bad_selection += 1

                # -------------------------------------------------------------------------------------------
                # ObtenÃ§Ã£o do valor de xfinal a usar nos cÃ¡clulos dos yy (caso nÃ£o seja selecionado um espectro experimental, porque se fo xfinal Ã© mudado)
                # (Calcular a dispersÃ£o em energia das varias riscas para criar o array de valores de x a plotar em funcao desta dispersÃ£o e da resoluÃ§Ã£o experimental)
                try:
                    if sat == 'Diagram':
                        deltaE = []
                        for j, k in enumerate(x):  # Percorremos as listas guardadas em x. k Ã© a lista e i o indice onde ela estÃ¡ guardada em x.
                            if k != []:  # Se a lista nÃ£o estiver vazia, guardamos em deltaE a diferenÃ§a entre o seu valor mÃ¡ximo e mÃ­nimo
                                deltaE.append(max(x[j]) - min(x[j]))
                        
                        max_value = max([max(x[i]) for i in range(len(x)) if x[i] != []]) + 4 * max([max(w[i]) for i in range(len(w)) if w[i] != []])
                        min_value = min([min(x[i]) for i in range(len(x)) if x[i] != []]) - 4 * max([max(w[i]) for i in range(len(w)) if w[i] != []])

                    elif sat == 'Satellites' or sat == 'Diagram + Satellites':
                        deltaE = []
                        for j, k in enumerate(xs):  # Ciclo sobre os elementos de x (ka1, ka2, kb1, etc... 7 no total)
                            for l, m in enumerate(xs[j]):
                                if m != []:
                                    deltaE.append(max(m) - min(m))
                        max_value = max(
                            [max(xs[i][j]) for i in range(len(xs)) for j in range(len(xs[i])) if xs[i][j] != []]) + max([max(ws[i][j]) for i in range(len(ws)) for j in range(len(ws[i])) if ws[i][j] != []])  # valor max de todos os elementos de xs (satt) que tem 7 linhas(ka1, ka2, etc) e o tamanho da lista label1 dentro de cada linha
                        min_value = min([min(xs[i][j]) for i in range(len(xs)) for j in range(len(xs[i])) if xs[i][j] != []]) - max([max(ws[i][j]) for i in range(len(ws)) for j in range(len(ws[i])) if ws[i][j] != []])
                    
                    elif sat == 'Auger':
                        deltaE = []
                        for j, k in enumerate(x):  # Percorremos as listas guardadas em x. k Ã© a lista e i o indice onde ela estÃ¡ guardada em x.
                            if k != []:  # Se a lista nÃ£o estiver vazia, guardamos em deltaE a diferenÃ§a entre o seu valor mÃ¡ximo e mÃ­nimo
                                deltaE.append(max(x[j]) - min(x[j]))
                        
                        max_value = max([max(x[i]) for i in range(len(x)) if x[i] != []]) + 4 * max([max(w[i]) for i in range(len(w)) if w[i] != []])
                        min_value = min([min(x[i]) for i in range(len(x)) if x[i] != []]) - 4 * max([max(w[i]) for i in range(len(w)) if w[i] != []])
                    # Definimos o x MÃ­nimo que queremos plotar. Pode ser definido automÃ¡ticamente ou pelo valor x_mn
                    if x_mn == 'Auto':  # x_mn Ã© inicializado a Auto, da primeira vez que o programa corre isto Ã© verdade
                        if res <= 0.2 * (min(deltaE)):
                            array_input_min = min_value - 2 * min(deltaE)
                        else:
                            array_input_min = min_value - 2 * res * min(deltaE)
                    else:
                        array_input_min = float(x_mn) - enoffset
                    # Definimos o x MÃ¡ximo que queremos plotar. Pode ser definido automÃ¡ticamente ou pelo valor x_mx
                    if x_mx == 'Auto':  # x_mx Ã© inicializado a Auto, da primeira vez que o programa corre isto Ã© verdade
                        if res <= 0.2 * (min(deltaE)):
                            array_input_max = max_value + 2 * min(deltaE)
                        else:
                            array_input_max = max_value + 2 * res * (min(deltaE))
                    else:
                        array_input_max = float(x_mx) - enoffset
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
                    exp_spectrum = list(csv.reader(open(load, 'r', encoding='utf-8-sig')))  # Carregar a matriz do espectro experimental do ficheiro escolhido no menu
                    for i, it in enumerate(exp_spectrum):
                        for j, itm in enumerate(exp_spectrum[i]):  # Transformar os valores do espectro experimental para float
                            if exp_spectrum[i][j] != '':
                                exp_spectrum[i][j] = float(itm)
                    xe = np.array([float(row[0]) for row in exp_spectrum])
                    ye = np.array([float(row[1]) for row in exp_spectrum])
                    if len(exp_spectrum[0]) >= 3: #Se o espectro experimental tiver 3 colunas a terceira sera a incerteza
                        sigma_exp = np.array([float(row[2]) for row in exp_spectrum])
                    else:  #Caso contrario utiliza-se raiz do numero de contagens como a incerteza de cada ponto
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

                    xfinal = np.array(np.linspace(min(exp_x) - enoffset, max(exp_x) - enoffset, num=num_of_points))
                    
                    if normalize == 'One':
                        graph_area.scatter(exp_x, exp_y / max(exp_y), marker='.', label='Exp.')  # Plot dos dados experimentais normalizados Ã  unidade
                        residues_graph.plot(exp_x, np.array(exp_sigma) / max(exp_y), 'k--')  # Plot do desvio padrÃ£o no grÃ¡fico dos resÃ­duos (linha positiva)
                        residues_graph.plot(exp_x, -np.array(exp_sigma) / max(exp_y), 'k--')  # Plot do desvio padrÃ£o no grÃ¡fico dos resÃ­duos (linha negativa)
                    else:
                        graph_area.scatter(exp_x, exp_y, marker='.', label='Exp.')  # Plot dos dados experimentais
                        residues_graph.plot(exp_x, np.array(exp_sigma), 'k--')  # Plot do desvio padrÃ£o no grÃ¡fico dos resÃ­duos (linha positiva)
                        residues_graph.plot(exp_x, -np.array(exp_sigma), 'k--')  # Plot do desvio padrÃ£o no grÃ¡fico dos resÃ­duos (linha negativa)

                    graph_area.legend()

                # ---------------------------------------------------------------------------------------------------------------
                # Leitura dos valores da eficÃ¡cia do detector:
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
                # VariÃ¡veis necessÃ¡rias para os cÃ¡lcuos dos y e para os plots:
                ytot, yfinal, yfinals = y_calculator(sat, peak, xfinal, x, y, w, xs, ys, ws, res,energy_values, efficiency_values,enoffset)

                # ---------------------------------------------------------------------------------------------------------------
                # CÃ¡lculo da variÃ¡vel de notificaÃ§Ã£o:
                # O cÃ¡lculo Ã© feito na funÃ§Ã£o normalizer, e Ã© lÃ¡ que Ã© lida a escolha de normalizaÃ§Ã£o do utilizador. Aqui sÃ³ passamos dados para a funÃ§ao
                if load != 'No':
                    normalization_var = normalizer(y0, max(exp_y), max(ytot))
                else:
                    if normalizevar.get() == 'ExpMax':  # Se tentarem normalizar ao maximo experimental sem terem carregado espectro
                        messagebox.showwarning("No experimental spectrum is loaded", "Choose different normalization option")  # Apresenta aviso
                        normalizevar.set('No')  # Define a variavel global de normalizaÃ§Ã£o para nÃ£o normalizar
                    normalization_var = normalizer(y0, 1, max(ytot))
                # ---------------------------------------------------------------------------------------------------------------
                # Autofit:
                # start_time = time.time()
                if autofit == 'Yes':
                    # Fazemos fit apenas se houver um grÃ¡fico experimental carregado
                    if load != 'No':

                        # Criar os parametros que vÃ£o ser otimizados
                        params = Parameters()

                        # Offset em energia
                        xoff_lim = (max(exp_x) - min(exp_x)) * 0.1  # O offset vai variar entre o valor introduzido +/- 10% do tamanho do grÃ¡fico
                        params.add('xoff', value=enoffset, min=enoffset - xoff_lim, max=enoffset + xoff_lim)

                        # Offset no yy
                        yoff_lim = (max(exp_y) - min(exp_y)) * 0.1
                        params.add('yoff', value=y0, min=y0 - yoff_lim, max=y0 + yoff_lim)

                        # ResoluÃ§Ã£o experimental
                        res_lim = res * 3
                        params.add('res', value=res, min=0.01, max=res + res_lim)

                        # # VariÃ¡vel de normalizaÃ§Ã£o
                        # norm_lim = normalization_var * 0.5
                        # params.add('normal', value=normalization_var)

                        # Parametro na Normalization var
                        params.add('ytot_max', value=max(ytot))
                        number_of_fit_variables = len(params.valuesdict())
                        minner = Minimizer(func2min, params, fcn_args=(exp_x, exp_y, num_of_points, sat, peak, x, y, w, xs, ys, ws, energy_values, efficiency_values,enoffset))
                        result = minner.minimize()
                        # report_fit(result)

                        # Offset em energia a ser definido para o plot final das linhas
                        enoffset = result.params['xoff'].value
                        energy_offset.set(enoffset)
                        # Offset no yy a ser definido para o plot final das linhas
                        y0 = result.params['yoff'].value
                        yoffset.set(y0)
                        # ResoluÃ§Ã£o experimental a ser definido para o plot final das linhas
                        res = result.params['res'].value
                        exp_resolution.set(res)
                        # normalization_var = result.params['normal'].value
                        ytot_max = result.params['ytot_max'].value

                        xfinal = np.array(np.linspace(min(exp_x) - enoffset, max(exp_x) - enoffset, num=num_of_points))
                        ytot, yfinal, yfinals = y_calculator(sat, peak, xfinal, x, y, w, xs, ys, ws, res, energy_values, efficiency_values,enoffset)
                        normalization_var = normalizer(y0, max(exp_y), ytot_max)
                        if messagebox.askyesno("Fit Saving", "Do you want to save this fit?"):
                            with open(file_namer("Fit", time_of_click, ".txt"), 'w') as file:
                                file.write(fit_report(result))
                            print(fit_report(result))
                        # residues_graph.plot(exp_x, np.array(result.residual))
                        # residues_graph.legend(title="Red.= " + "{:.5f}".format(result.redchi), loc='lower right')

                    else:
                        messagebox.showerror("Error", "Autofit is only avaliable if an experimental spectrum is loaded")
                # ------------------------------------------------------------------------------------------------------------------------
                # Plot das linhas
                # print('Time of fit execution: --- %s seconds ---' % (time.time() - start_time))
                if sat == 'Diagram':
                    for index, key in enumerate(the_dictionary):
                        if the_dictionary[key]["selected_state"]:
                            graph_area.plot(xfinal + enoffset, (np.array(yfinal[index]) * normalization_var) + y0, label=key, color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                            graph_area.legend()
                elif sat == 'Satellites':
                    for index, key in enumerate(the_dictionary):
                        if the_dictionary[key]["selected_state"]:
                            for l, m in enumerate(yfinals[index]):
                                if max(m) != 0:  # Excluir as linhas que nao foram seleccionados nos botoes
                                    graph_area.plot(xfinal + enoffset, (np.array(yfinals[index][l]) * normalization_var) + y0, label=key + ' - ' + labeldict[label1[l]], color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                                    graph_area.legend()
                elif sat == 'Diagram + Satellites':
                    for index, key in enumerate(the_dictionary):
                        if the_dictionary[key]["selected_state"]:
                            graph_area.plot(xfinal + enoffset, (np.array(yfinal[index]) * normalization_var) + y0, label=key, color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                            graph_area.legend()

                    for index, key in enumerate(the_dictionary):
                        if the_dictionary[key]["selected_state"]:
                            for l, m in enumerate(yfinals[index]):
                                if max(m) != 0:  # Excluir as linhas que nao foram seleccionados nos botoes
                                    graph_area.plot(xfinal + enoffset, (np.array(yfinals[index][l]) * normalization_var) + y0, label=key + ' - ' + labeldict[label1[l]], color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                                    graph_area.legend()
                elif sat == 'Auger':
                    for index, key in enumerate(the_aug_dictionary):
                        if the_aug_dictionary[key]["selected_state"]:
                            graph_area.plot(xfinal + enoffset, (np.array(yfinal[index]) * normalization_var) + y0, label=key, color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                            graph_area.legend()
                if total == 'Total':
                    graph_area.plot(xfinal + enoffset, (ytot * normalization_var) + y0, label='Total', ls='--', lw=2, color='k')  # Plot the simulation of all lines
                    graph_area.legend()
                # ------------------------------------------------------------------------------------------------------------------------
                # CÃ¡lculo dos Residuos
                if load != 'No':
                    # if load != 'No':
                    # Definimos uma funÃ§Ã£o que recebe um numero, e tendo como dados o que passamos Ã  interp1d faz a sua interpolaÃ§Ã£o
                    # print(*ytot, sep=',')
                    y_interp = [0 for i in range(len(exp_x))]  # Criar lista vazia para o grÃ¡fico de resÃ­duos
                    f_interpolate = interp1d(xfinal + enoffset, (np.array(ytot) * normalization_var) + y0, kind='cubic')
                    # Vetor para guardar o y dos residuos (nÃ£o precisamos de guardar o x porque Ã© igual ao exp_x
                    y_res = [0 for x in range(len(exp_x))]
                    # VariÃ¡vel para a soma do chi quadrado
                    chi_sum = 0
                    # Percorremos todos os valores de x
                    for g, h in enumerate(exp_x):
                        # Obtemos o valor de y interpolado pela funÃ§Ã£o definida a cima
                        y_interp[g] = f_interpolate(h)
                        # CÃ¡lculamos o y dos residuos subtraindo o interpolado ao experimental
                        if normalize == 'ExpMax' or normalize == 'No':
                            y_res[g] = (exp_y[g] - y_interp[g]) 
                            #y_res[g] = y_interp[g] - exp_y[g]                  ORIGINAL CODE
                            chi_sum += (y_res[g] ** 2) / ((exp_sigma[g]**2))
                        elif normalize == 'One':
                            y_res[g] = ((exp_y[g] / max(exp_y)) - y_interp[g])
                            #y_res[g] = y_interp[g] - (exp_y[g] / max(exp_y))           ORGINAL CODE
                            chi_sum += (y_res[g] **2) / ((exp_sigma[g]/ max(exp_y))**2) 
                        #     y_res[g] = (exp_y[g] / max(exp_y)) - y_interp[g]
                        # SomatÃ³rio para o cÃ¡lculo de chi quad
                    global chi_sqrd
                    chi_sqrd = chi_sum / (len(exp_x) - number_of_fit_variables)
                    residues_graph.plot(exp_x, y_res)
                    print("Valor Manual Chi", chi_sqrd)
                    residues_graph.legend(title="Red. \u03C7\u00B2 = " + "{:.5f}".format(chi_sqrd))
                # ------------------------------------------------------------------------------------------------------------------------
                # DefiniÃ§Ã£o do label do eixo yy e, consoante haja ou nÃ£o um grÃ¡fico de resÃ­duos, do eixo  xx
                graph_area.set_ylabel('Intensity (arb. units)')
                graph_area.legend(title=element_name, title_fontsize='large')
                if load == 'No':
                    graph_area.set_xlabel('Energy (eV)')
                # ------------------------------------------------------------------------------------------------------------------------
                # Controlo do numero de entradas na legenda
                number_of_labels = len(graph_area.legend().get_texts())  # Descubro quantas entradas vai ter a legenda
                legend_columns = 1  # Inicialmente hÃ¡ uma coluna, mas vou fazer contas para ter 10 itens por coluna no mÃ¡ximo
                labels_per_columns = number_of_labels / legend_columns  # Numero de entradas por coluna
                while labels_per_columns > 10:  # Se a priori for menos de 10 entradas por coluna, nÃ£o acontece nada
                    legend_columns += 1  # Se houver mais que 10 entradas por coluna, meto mais uma coluna
                    labels_per_columns = number_of_labels / legend_columns  # Recalculo o numero de entradas por coluna
                graph_area.legend(ncol=legend_columns)  # Defino o numero de colunas na legenda = numero de colunas necessÃ¡rias para nÃ£o ter mais de 10 entradas por coluna
            #--------------------------------------------------------------------------------------------------------------------------------------
            elif spectype == 'M_Simulation':
                # VariÃ¡vel para contar as transiÃ§Ãµes erradas
                bad_selection = 0
                
                bad_lines = {}
                
                if sat != 'Auger':
                    # -------------------------------------------------------------------------------------------
                    # Leitura dos valores das transiÃ§Ãµes selecionadas
                    # Contrariamente ao spectype == 'Stick' onde os plots sÃ£o feitos quando se trata de cada risca, aqui,
                    # o  que se faz Ã© obter os valores necessÃ¡rios para os plots. NÃ£o se faz nenhum plot em si dentro deste ciclo.
                    charge_states = rad_PCS + rad_NCS
                    
                    ploted_cs = []
                    
                    for cs_index, cs in enumerate(charge_states):
                        mix_val = '0.0'
                        ncs = False
                        
                        if cs_index < len(rad_PCS):
                            mix_val = PCS_radMixValues[cs_index].get()
                        else:
                            mix_val = NCS_radMixValues[cs_index - len(rad_PCS)].get()
                            ncs = True
                        
                        if mix_val != '0.0':
                            ploted_cs.append(cs)
                        
                    x = [[] for i in range(len(the_dictionary) * len(ploted_cs))]
                    y = [[] for i in range(len(the_dictionary) * len(ploted_cs))]
                    w = [[] for i in range(len(the_dictionary) * len(ploted_cs))]
                    xs = [[[] for i in label1] for j in x]
                    ys = [[[] for i in label1] for j in y]
                    ws = [[[] for i in label1] for j in w]
                    
                    for cs_index, cs in enumerate(ploted_cs):
                        for index, transition in enumerate(the_dictionary):
                            if the_dictionary[transition]["selected_state"]:
                                low_level = the_dictionary[transition]["low_level"]  # orbital da lacuna no inÃ­cio da transiÃ§Ã£o
                                high_level = the_dictionary[transition]["high_level"]  # orbital da lacuna no fim da transiÃ§Ã£o
                                
                                if not ncs:
                                    diag_sim_val = [line + [PCS_radMixValues[i].get()] for i, linerad in enumerate(lineradrates_PCS) for line in linerad if line[1] in low_level and line[5] == high_level and float(line[8]) != 0 and rad_PCS[i] == cs]  # Guarda para uma lista as linhas do ficheiro que se referem Ã  trasiÃ§Ã£o transition
                                else:
                                    diag_sim_val = [line + [NCS_radMixValues[i].get()] for i, linerad in enumerate(lineradrates_NCS) for line in linerad if line[1] in low_level and line[5] == high_level and float(line[8]) != 0 and rad_NCS[i] == cs]
                                
                                if not ncs:
                                    sat_sim_val = [line + [PCS_radMixValues[rad_PCS.index(sat_PCS[i])].get()] for i, linesat in enumerate(linesatellites_PCS) for line in linesat if low_level in line[1] and high_level in line[5] and float(line[8]) != 0 and sat_PCS[i] == cs]  # Guarda para uma lista as linhas do ficheiro que se referem Ã s satÃ©lites de transition
                                else:
                                    sat_sim_val = [line + [NCS_radMixValues[rad_NCS.index(sat_NCS[i])].get()] for i, linesat in enumerate(linesatellites_NCS) for line in linesat if low_level in line[1] and high_level in line[5] and float(line[8]) != 0 and sat_NCS[i] == cs]  # Guarda para uma lista as linhas do ficheiro que se referem Ã s satÃ©lites de transition
                                
                                if sat == 'Diagram':
                                    x1 = [float(row[8]) for row in diag_sim_val]
                                    y1 = [float(row[11]) * (1 - sum(shakeweights)) * float(row[-1]) for row in diag_sim_val]
                                    w1 = [float(row[15]) for row in diag_sim_val]
                                    x[cs_index * len(the_dictionary) + index] = x1
                                    y[cs_index * len(the_dictionary) + index] = y1
                                    w[cs_index * len(the_dictionary) + index] = w1
                                elif sat == 'Satellites':
                                    for ind, key in enumerate(label1):
                                        sat_sim_val_ind1 = [line for line in sat_sim_val if low_level + key in line[1] and key + high_level in line[5]]
                                        sat_sim_val_ind2 = [line for line in sat_sim_val if low_level + key in line[1] and high_level + key in line[5] and key != high_level]
                                        sat_sim_val_ind3 = [line for line in sat_sim_val if key + low_level in line[1] and key + high_level in line[5]]
                                        sat_sim_val_ind4 = [line for line in sat_sim_val if key + low_level in line[1] and high_level + key in line[5] and key != high_level]
                                        sat_sim_val_ind = sat_sim_val_ind1 + sat_sim_val_ind2 + sat_sim_val_ind3 + sat_sim_val_ind4
                                        if len(sat_sim_val_ind) > 1:
                                            x1s = [float(row[8]) for row in sat_sim_val_ind]
                                            y1s = [float(float(row[11]) * shakeweights[ind] * float(row[-1])) for row in sat_sim_val_ind]
                                            w1s = [float(row[15]) for row in sat_sim_val_ind]
                                            xs[cs_index * len(the_dictionary) + index][ind] = x1s
                                            ys[cs_index * len(the_dictionary) + index][ind] = y1s
                                            ws[cs_index * len(the_dictionary) + index][ind] = w1s
                                elif sat == 'Diagram + Satellites':
                                    x1 = [float(row[8]) for row in diag_sim_val]
                                    y1 = [float(row[11]) * (1 - sum(shakeweights)) * float(row[-1]) for row in diag_sim_val]
                                    w1 = [float(row[15]) for row in diag_sim_val]
                                    x[cs_index * len(the_dictionary) + index] = x1
                                    y[cs_index * len(the_dictionary) + index] = y1
                                    w[cs_index * len(the_dictionary) + index] = w1
                                    # ---------------------------------------------------------------------------------------------------------------------
                                    for ind, key in enumerate(label1):
                                        sat_sim_val_ind1 = [line for line in sat_sim_val if low_level + key in line[1] and key + high_level in line[5]]
                                        sat_sim_val_ind2 = [line for line in sat_sim_val if low_level + key in line[1] and high_level + key in line[5] and key != high_level]
                                        sat_sim_val_ind3 = [line for line in sat_sim_val if key + low_level in line[1] and key + high_level in line[5]]
                                        sat_sim_val_ind4 = [line for line in sat_sim_val if key + low_level in line[1] and high_level + key in line[5] and key != high_level]
                                        sat_sim_val_ind = sat_sim_val_ind1 + sat_sim_val_ind2 + sat_sim_val_ind3 + sat_sim_val_ind4
                                        
                                        if len(sat_sim_val_ind) > 1:
                                            x1s = [float(row[8]) for row in sat_sim_val_ind]
                                            y1s = [float(float(row[11]) * shakeweights[ind] * float(row[-1])) for row in sat_sim_val_ind]
                                            w1s = [float(row[15]) for row in sat_sim_val_ind]
                                            xs[cs_index * len(the_dictionary) + index][ind] = x1s
                                            ys[cs_index * len(the_dictionary) + index][ind] = y1s
                                            ws[cs_index * len(the_dictionary) + index][ind] = w1s
                        # -------------------------------------------------------------------------------------------
                        # Verificar se se selecionaram transiÃ§Ãµes indÃ­sponÃ­veis
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
                    charge_states = aug_PCS + aug_NCS
                    
                    ploted_cs = []
                    
                    for cs_index, cs in enumerate(charge_states):
                        mix_val = '0.0'
                        ncs = False
                        
                        if cs_index < len(aug_PCS):
                            mix_val = PCS_augMixValues[cs_index].get()
                        else:
                            mix_val = NCS_augMixValues[cs_index - len(aug_PCS)].get()
                            ncs = True
                        if mix_val != '0.0':
                            ploted_cs.append(cs)
                    
                    x = [[] for i in range(len(the_aug_dictionary) * len(ploted_cs))]
                    y = [[] for i in range(len(the_aug_dictionary) * len(ploted_cs))]
                    w = [[] for i in range(len(the_aug_dictionary) * len(ploted_cs))]            
                    xs = [[[] for i in label1] for j in x]
                    ys = [[[] for i in label1] for j in y]
                    ws = [[[] for i in label1] for j in w]
                    
                    for cs_index, cs in enumerate(ploted_cs):
                        for index, transition in enumerate(the_aug_dictionary):
                            if the_aug_dictionary[transition]["selected_state"]:
                                low_level = the_aug_dictionary[transition]["low_level"]  # orbital da lacuna no inÃ­cio da transiÃ§Ã£o
                                high_level = the_aug_dictionary[transition]["high_level"]  # orbital da lacuna no fim da transiÃ§Ã£o
                                auger_level = the_aug_dictionary[transition]["auger_level"]
                                
                                if not ncs:
                                    aug_sim_val = [line + [PCS_augMixValues[i].get()] for i, lineaug in enumerate(lineaugrates_PCS) for line in lineaug if low_level in line[1] and high_level in line[5][:2] and auger_level in line[5][2:4] and float(line[8]) != 0 and aug_PCS[i] == cs]  # Guarda para uma lista as linhas do ficheiro que se referem Ã  trasiÃ§Ã£o transition
                                else:
                                    aug_sim_val = [line + [NCS_augMixValues[i].get()] for i, lineaug in enumerate(lineaugrates_NCS) for line in lineaug if low_level in line[1] and high_level in line[5][:2] and auger_level in line[5][2:4] and float(line[8]) != 0 and aug_NCS[i] == cs]  # Guarda para uma lista as linhas do ficheiro que se referem Ã  trasiÃ§Ã£o transition
                                
                                x1 = [float(row[8]) for row in aug_sim_val]
                                y1 = [float(row[9]) * (1 - sum(shakeweights)) * float(row[-1]) for row in aug_sim_val]
                                w1 = [float(row[10]) for row in aug_sim_val]
                                x[cs_index * len(the_aug_dictionary) + index] = x1
                                y[cs_index * len(the_aug_dictionary) + index] = y1
                                w[cs_index * len(the_aug_dictionary) + index] = w1
                        
                        # -------------------------------------------------------------------------------------------
                        # Verificar se se selecionaram transiÃ§Ãµes indÃ­sponÃ­veis
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
                # ObtenÃ§Ã£o do valor de xfinal a usar nos cÃ¡clulos dos yy (caso nÃ£o seja selecionado um espectro experimental, porque se fo xfinal Ã© mudado)
                # (Calcular a dispersÃ£o em energia das varias riscas para criar o array de valores de x a plotar em funcao desta dispersÃ£o e da resoluÃ§Ã£o experimental)
                try:
                    if sat == 'Diagram':
                        deltaE = []
                        for j, k in enumerate(x):  # Percorremos as listas guardadas em x. k Ã© a lista e i o indice onde ela estÃ¡ guardada em x.
                            if k != []:  # Se a lista nÃ£o estiver vazia, guardamos em deltaE a diferenÃ§a entre o seu valor mÃ¡ximo e mÃ­nimo
                                deltaE.append(max(x[j]) - min(x[j]))
                        
                        max_value = max([max(x[i]) for i in range(len(x)) if x[i] != []]) + 4 * max([max(w[i]) for i in range(len(w)) if w[i] != []])
                        min_value = min([min(x[i]) for i in range(len(x)) if x[i] != []]) - 4 * max([max(w[i]) for i in range(len(w)) if w[i] != []])

                    elif sat == 'Satellites' or sat == 'Diagram + Satellites':
                        deltaE = []
                        for j, k in enumerate(xs):  # Ciclo sobre os elementos de x (ka1, ka2, kb1, etc... 7 no total)
                            for l, m in enumerate(xs[j]):
                                if m != []:
                                    deltaE.append(max(m) - min(m))
                        max_value = max(
                            [max(xs[i][j]) for i in range(len(xs)) for j in range(len(xs[i])) if xs[i][j] != []]) + max([max(ws[i][j]) for i in range(len(ws)) for j in range(len(ws[i])) if ws[i][j] != []])  # valor max de todos os elementos de xs (satt) que tem 7 linhas(ka1, ka2, etc) e o tamanho da lista label1 dentro de cada linha
                        min_value = min([min(xs[i][j]) for i in range(len(xs)) for j in range(len(xs[i])) if xs[i][j] != []]) - max([max(ws[i][j]) for i in range(len(ws)) for j in range(len(ws[i])) if ws[i][j] != []])
                    
                    elif sat == 'Auger':
                        deltaE = []
                        for j, k in enumerate(x):  # Percorremos as listas guardadas em x. k Ã© a lista e i o indice onde ela estÃ¡ guardada em x.
                            if k != []:  # Se a lista nÃ£o estiver vazia, guardamos em deltaE a diferenÃ§a entre o seu valor mÃ¡ximo e mÃ­nimo
                                deltaE.append(max(x[j]) - min(x[j]))
                        
                        max_value = max([max(x[i]) for i in range(len(x)) if x[i] != []]) + 4 * max([max(w[i]) for i in range(len(w)) if w[i] != []])
                        min_value = min([min(x[i]) for i in range(len(x)) if x[i] != []]) - 4 * max([max(w[i]) for i in range(len(w)) if w[i] != []])
                    # Definimos o x MÃ­nimo que queremos plotar. Pode ser definido automÃ¡ticamente ou pelo valor x_mn
                    if x_mn == 'Auto':  # x_mn Ã© inicializado a Auto, da primeira vez que o programa corre isto Ã© verdade
                        if res <= 0.2 * (min(deltaE)):
                            array_input_min = min_value - 2 * min(deltaE)
                        else:
                            array_input_min = min_value - 2 * res * min(deltaE)
                    else:
                        array_input_min = float(x_mn) - enoffset
                    # Definimos o x MÃ¡ximo que queremos plotar. Pode ser definido automÃ¡ticamente ou pelo valor x_mx
                    if x_mx == 'Auto':  # x_mx Ã© inicializado a Auto, da primeira vez que o programa corre isto Ã© verdade
                        if res <= 0.2 * (min(deltaE)):
                            array_input_max = max_value + 2 * min(deltaE)
                        else:
                            array_input_max = max_value + 2 * res * (min(deltaE))
                    else:
                        array_input_max = float(x_mx) - enoffset
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
                    exp_spectrum = list(csv.reader(open(load, 'r', encoding='utf-8-sig')))  # Carregar a matriz do espectro experimental do ficheiro escolhido no menu
                    for i, it in enumerate(exp_spectrum):
                        for j, itm in enumerate(exp_spectrum[i]):  # Transformar os valores do espectro experimental para float
                            if exp_spectrum[i][j] != '':
                                exp_spectrum[i][j] = float(itm)
                    xe = np.array([float(row[0]) for row in exp_spectrum])
                    ye = np.array([float(row[1]) for row in exp_spectrum])
                    if len(exp_spectrum[0]) >= 3: #Se o espectro experimental tiver 3 colunas a terceira sera a incerteza
                        sigma_exp = np.array([float(row[2]) for row in exp_spectrum])
                    else:  #Caso contrario utiliza-se raiz do numero de contagens como a incerteza de cada ponto
                        sigma_exp = np.sqrt(ye)
                        sigma_exp[sigma_exp == 0] = np.min(sigma_exp[sigma_exp != 0]) #replace zeros with the min unceartanty to prevent an inf chi sqr
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

                    xfinal = np.array(np.linspace(min(exp_x) - enoffset, max(exp_x) - enoffset, num=num_of_points))
                    
                    if normalize == 'One':
                        graph_area.scatter(exp_x, exp_y / max(exp_y), marker='.', label='Exp.')  # Plot dos dados experimentais normalizados Ã  unidade
                        residues_graph.plot(exp_x, np.array(exp_sigma) / max(exp_y), 'k--')  # Plot do desvio padrÃ£o no grÃ¡fico dos resÃ­duos (linha positiva)
                        residues_graph.plot(exp_x, -np.array(exp_sigma) / max(exp_y), 'k--')  # Plot do desvio padrÃ£o no grÃ¡fico dos resÃ­duos (linha negativa)
                    else:
                        graph_area.scatter(exp_x, exp_y, marker='.', label='Exp.')  # Plot dos dados experimentais
                        residues_graph.plot(exp_x, np.array(exp_sigma), 'k--')  # Plot do desvio padrÃ£o no grÃ¡fico dos resÃ­duos (linha positiva)
                        residues_graph.plot(exp_x, -np.array(exp_sigma), 'k--')  # Plot do desvio padrÃ£o no grÃ¡fico dos resÃ­duos (linha negativa)

                    graph_area.legend()

                # ---------------------------------------------------------------------------------------------------------------
                # Leitura dos valores da eficÃ¡cia do detector:
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
                # VariÃ¡veis necessÃ¡rias para os cÃ¡lcuos dos y e para os plots:
                ytot, yfinal, yfinals = y_calculator(sat, peak, xfinal, x, y, w, xs, ys, ws, res,energy_values, efficiency_values,enoffset)

                # ---------------------------------------------------------------------------------------------------------------
                # CÃ¡lculo da variÃ¡vel de notificaÃ§Ã£o:
                # O cÃ¡lculo Ã© feito na funÃ§Ã£o normalizer, e Ã© lÃ¡ que Ã© lida a escolha de normalizaÃ§Ã£o do utilizador. Aqui sÃ³ passamos dados para a funÃ§ao
                if load != 'No':
                    normalization_var = normalizer(y0, max(exp_y), max(ytot))
                else:
                    if normalizevar.get() == 'ExpMax':  # Se tentarem normalizar ao maximo experimental sem terem carregado espectro
                        messagebox.showwarning("No experimental spectrum is loaded", "Choose different normalization option")  # Apresenta aviso
                        normalizevar.set('No')  # Define a variavel global de normalizaÃ§Ã£o para nÃ£o normalizar
                    normalization_var = normalizer(y0, 1, max(ytot))
                # ---------------------------------------------------------------------------------------------------------------
                # Autofit:
                # start_time = time.time()
                if autofit == 'Yes':
                    # Fazemos fit apenas se houver um grÃ¡fico experimental carregado
                    if load != 'No':

                        # Criar os parametros que vÃ£o ser otimizados
                        params = Parameters()

                        # Offset em energia
                        xoff_lim = (max(exp_x) - min(exp_x)) * 0.1  # O offset vai variar entre o valor introduzido +/- 10% do tamanho do grÃ¡fico
                        params.add('xoff', value=enoffset, min=enoffset - xoff_lim, max=enoffset + xoff_lim)

                        # Offset no yy
                        yoff_lim = (max(exp_y) - min(exp_y)) * 0.1
                        params.add('yoff', value=y0, min=y0 - yoff_lim, max=y0 + yoff_lim)

                        # ResoluÃ§Ã£o experimental
                        res_lim = res * 3
                        params.add('res', value=res, min=0.01, max=res + res_lim)

                        # # VariÃ¡vel de normalizaÃ§Ã£o
                        # norm_lim = normalization_var * 0.5
                        # params.add('normal', value=normalization_var)

                        # Parametro na Normalization var
                        params.add('ytot_max', value=max(ytot))
                        number_of_fit_variables = len(params.valuesdict())
                        minner = Minimizer(func2min, params, fcn_args=(exp_x, exp_y, num_of_points, sat, peak, x, y, w, xs, ys, ws, energy_values, efficiency_values,enoffset))
                        result = minner.minimize()
                        # report_fit(result)

                        # Offset em energia a ser definido para o plot final das linhas
                        enoffset = result.params['xoff'].value
                        energy_offset.set(enoffset)
                        # Offset no yy a ser definido para o plot final das linhas
                        y0 = result.params['yoff'].value
                        yoffset.set(y0)
                        # ResoluÃ§Ã£o experimental a ser definido para o plot final das linhas
                        res = result.params['res'].value
                        exp_resolution.set(res)
                        # normalization_var = result.params['normal'].value
                        ytot_max = result.params['ytot_max'].value

                        xfinal = np.array(np.linspace(min(exp_x) - enoffset, max(exp_x) - enoffset, num=num_of_points))
                        ytot, yfinal, yfinals = y_calculator(sat, peak, xfinal, x, y, w, xs, ys, ws, res, energy_values, efficiency_values,enoffset)
                        normalization_var = normalizer(y0, max(exp_y), ytot_max)
                        if messagebox.askyesno("Fit Saving", "Do you want to save this fit?"):
                            with open(file_namer("Fit", time_of_click, ".txt"), 'w') as file:
                                file.write(fit_report(result))
                            print(fit_report(result))
                        # residues_graph.plot(exp_x, np.array(result.residual))
                        # residues_graph.legend(title="Red.= " + "{:.5f}".format(result.redchi), loc='lower right')

                    else:
                        messagebox.showerror("Error", "Autofit is only avaliable if an experimental spectrum is loaded")
                # ------------------------------------------------------------------------------------------------------------------------
                # Plot das linhas
                # print('Time of fit execution: --- %s seconds ---' % (time.time() - start_time))
                if sat == 'Diagram':
                    for cs_index, cs in enumerate(ploted_cs):
                        for index, key in enumerate(the_dictionary):
                            if the_dictionary[key]["selected_state"]:
                                graph_area.plot(xfinal + enoffset, (np.array(yfinal[cs_index * len(the_dictionary) + index]) * normalization_var) + y0, label=cs + ' ' + key, color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                                graph_area.legend()
                elif sat == 'Satellites':
                    for cs_index, cs in enumerate(ploted_cs):
                        for index, key in enumerate(the_dictionary):
                            if the_dictionary[key]["selected_state"]:
                                for l, m in enumerate(yfinals[cs_index * len(the_dictionary) + index]):
                                    if max(m) != 0:  # Excluir as linhas que nao foram seleccionados nos botoes
                                        graph_area.plot(xfinal + enoffset, (np.array(yfinals[cs_index * len(the_dictionary) + index][l]) * normalization_var) + y0, label=key + ' - ' + labeldict[label1[l]], color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                                        graph_area.legend()
                elif sat == 'Diagram + Satellites':
                    for cs_index, cs in enumerate(ploted_cs):
                        for index, key in enumerate(the_dictionary):
                            if the_dictionary[key]["selected_state"]:
                                graph_area.plot(xfinal + enoffset, (np.array(yfinal[cs_index * len(the_dictionary) + index]) * normalization_var) + y0, label=cs + ' ' + key, color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                                graph_area.legend()
                        
                        for index, key in enumerate(the_dictionary):
                            if the_dictionary[key]["selected_state"]:
                                for l, m in enumerate(yfinals[cs_index * len(the_dictionary) + index]):
                                    if max(m) != 0:  # Excluir as linhas que nao foram seleccionados nos botoes
                                        graph_area.plot(xfinal + enoffset, (np.array(yfinals[cs_index * len(the_dictionary) + index][l]) * normalization_var) + y0, label=cs + ' ' + key + ' - ' + labeldict[label1[l]], color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                                        graph_area.legend()
                elif sat == 'Auger':
                    for cs_index, cs in enumerate(ploted_cs):
                        for index, key in enumerate(the_aug_dictionary):
                            if the_aug_dictionary[key]["selected_state"]:
                                graph_area.plot(xfinal + enoffset, (np.array(yfinal[cs_index * len(the_aug_dictionary) + index]) * normalization_var) + y0, label=cs + ' ' + key, color=str(col2[np.random.randint(0, 7)][0]))  # Plot the simulation of all lines
                                graph_area.legend()
                if total == 'Total':
                    graph_area.plot(xfinal + enoffset, (ytot * normalization_var) + y0, label='Total', ls='--', lw=2, color='k')  # Plot the simulation of all lines
                    graph_area.legend()
                # ------------------------------------------------------------------------------------------------------------------------
                # CÃ¡lculo dos Residuos
                if load != 'No':
                    # if load != 'No':
                    # Definimos uma funÃ§Ã£o que recebe um numero, e tendo como dados o que passamos Ã  interp1d faz a sua interpolaÃ§Ã£o
                    # print(*ytot, sep=',')
                    y_interp = [0 for i in range(len(exp_x))]  # Criar lista vazia para o grÃ¡fico de resÃ­duos
                    f_interpolate = interp1d(xfinal + enoffset, (np.array(ytot) * normalization_var) + y0, kind='cubic')
                    # Vetor para guardar o y dos residuos (nÃ£o precisamos de guardar o x porque Ã© igual ao exp_x
                    y_res = [0 for x in range(len(exp_x))]
                    # VariÃ¡vel para a soma do chi quadrado
                    chi_sum = 0
                    # Percorremos todos os valores de x
                    for g, h in enumerate(exp_x):
                        # Obtemos o valor de y interpolado pela funÃ§Ã£o definida a cima
                        y_interp[g] = f_interpolate(h)
                        # CÃ¡lculamos o y dos residuos subtraindo o interpolado ao experimental
                        if normalize == 'ExpMax' or normalize == 'No':
                            y_res[g] = (exp_y[g] - y_interp[g]) 
                            #y_res[g] = y_interp[g] - exp_y[g]                  ORIGINAL CODE
                            chi_sum += (y_res[g] ** 2) / ((exp_sigma[g]**2))
                        elif normalize == 'One':
                            y_res[g] = ((exp_y[g] / max(exp_y)) - y_interp[g])
                            #y_res[g] = y_interp[g] - (exp_y[g] / max(exp_y))           ORGINAL CODE
                            chi_sum += (y_res[g] **2) / ((exp_sigma[g]/ max(exp_y))**2) 
                        #     y_res[g] = (exp_y[g] / max(exp_y)) - y_interp[g]
                        # SomatÃ³rio para o cÃ¡lculo de chi quad
                    
                    chi_sqrd = chi_sum / (len(exp_x) - number_of_fit_variables)
                    residues_graph.plot(exp_x, y_res)
                    print("Valor Manual Chi", chi_sqrd)
                    residues_graph.legend(title="Red. \u03C7\u00B2 = " + "{:.5f}".format(chi_sqrd))
                # ------------------------------------------------------------------------------------------------------------------------
                # DefiniÃ§Ã£o do label do eixo yy e, consoante haja ou nÃ£o um grÃ¡fico de resÃ­duos, do eixo  xx
                graph_area.set_ylabel('Intensity (arb. units)')
                graph_area.legend(title=element_name, title_fontsize='large')
                if load == 'No':
                    graph_area.set_xlabel('Energy (eV)')
                # ------------------------------------------------------------------------------------------------------------------------
                # Controlo do numero de entradas na legenda
                number_of_labels = len(graph_area.legend().get_texts())  # Descubro quantas entradas vai ter a legenda
                legend_columns = 1  # Inicialmente hÃ¡ uma coluna, mas vou fazer contas para ter 10 itens por coluna no mÃ¡ximo
                labels_per_columns = number_of_labels / legend_columns  # Numero de entradas por coluna
                while labels_per_columns > 10:  # Se a priori for menos de 10 entradas por coluna, nÃ£o acontece nada
                    legend_columns += 1  # Se houver mais que 10 entradas por coluna, meto mais uma coluna
                    labels_per_columns = number_of_labels / legend_columns  # Recalculo o numero de entradas por coluna
                graph_area.legend(ncol=legend_columns)  # Defino o numero de colunas na legenda = numero de colunas necessÃ¡rias para nÃ£o ter mais de 10 entradas por coluna
            
            f.canvas.draw()

        def on_key_event(event):  # NAO SEI BEM O QUE ISTO FAZ
            print('you pressed %s' % event.key)
            key_press_handler(event, canvas, toolbar)

        canvas.mpl_connect('key_press_event', on_key_event)  # NAO SEI BEM O QUE ISTO FAZ

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
            fname = askopenfilename(filetypes=(("Spectra files", "*.csv *.txt"), ("All files", "*.*")))
            loadvar.set(fname)  # Muda o nome da variavel loadvar para a string correspondente ao path do ficheiro seleccionado

        def load_effic_file():
            effic_fname = askopenfilename(filetypes =(("Efficiency files", "*.csv"), ("All files", "*.*")))
            effic_var.set(effic_fname)

        def selected(event):
            text_T = drop_menu.get()  # LÃª Texto da box com as transiÃ§Ãµes
            dict_updater(text_T)  # Faz update do dicionÃ¡rio com a transiÃ§Ã£o lida
            to_print = ''  # Texto a imprimir no label com as transiÃ§Ãµes selecionadas
            
            if satelite_var.get() != 'Auger':
                if the_dictionary[text_T]["selected_state"]:  # Se a transiÃ§Ã£o estiver selecionada:
                    transition_list.append(text_T)  # Ã‰ adicionada Ã  lista de transiÃ§Ãµes que vai para o label
                elif not the_dictionary[text_T]["selected_state"]:  # Se for descelecionada
                    transition_list.remove(text_T)  # Ã‰ removida da lista que vai para o label
            else:
                if the_aug_dictionary[text_T]["selected_state"]:  # Se a transiÃ§Ã£o estiver selecionada:
                    transition_list.append(text_T)  # Ã‰ adicionada Ã  lista de transiÃ§Ãµes que vai para o label
                elif not the_aug_dictionary[text_T]["selected_state"]:  # Se for descelecionada
                    transition_list.remove(text_T)  # Ã‰ removida da lista que vai para o label
            
            for a, b in enumerate(transition_list):  # Este for serve para colocar as virgulas entre as transiÃ§Ãµes que vÃ£o para o label
                if len(transition_list) == a + 1:
                    to_print += str(b) + ' '
                else:
                    to_print += str(b) + ', '
            label_text.set('Selected Transitions: ' + to_print)  # Definimos o novo label

        def enter_function(event):
            plot_stick(a)

        def reset_limits():
            number_points.set(500)
            x_max.set('Auto')
            x_min.set('Auto')
        
        def update_transition_dropdown():
            global transition_list
            
            if satelite_var.get() != 'Auger':
                drop_menu['values'] = [transition for transition in the_dictionary]
                if not any([the_dictionary[transition]["selected_state"] for transition in the_dictionary]):
                    transition_list = []
                    label_text.set('Select a Transition: ')
                    drop_menu.set('Transitions:')
                    for transition in the_aug_dictionary:
                        the_aug_dictionary[transition]["selected_state"] = False
            else:
                drop_menu['values'] = [transition for transition in the_aug_dictionary]
                if not any([the_aug_dictionary[transition]["selected_state"] for transition in the_aug_dictionary]):
                    transition_list = []
                    label_text.set('Select a Transition: ')
                    drop_menu.set('Transitions:')
                    for transition in the_dictionary:
                        the_dictionary[transition]["selected_state"] = False
            

        def configureCSMix():
            global PCS_radMixValues, NCS_radMixValues, PCS_augMixValues, NCS_augMixValues
            
            mixer = Toplevel(sim)
            mixer.title("Charge State Mixer")
            mixer.grab_set() # Make this window the only interactable one until its closed
            
            mixer.geometry("700x300")
            
            import re
            def check_num(newval):
                return re.match('^(?:[0-9]*[.]?[0-9]*)$', newval) is not None
            check_num_wrapper = (mixer.register(check_num), '%P')
            
            # -------------------------------------------------------------------------------------------------------------------------------------------
            # RADIATIVE
            
            
            slidersRad = []
            CS_labelsRad = []
            PCS_order = [int(cs.split('intensity_')[1].split('.out')[0].split('+')[-1]) for cs in radiative_files if '+' in cs]
            NCS_order = [int(cs.split('intensity_')[1].split('.out')[0].split('-')[-1]) for cs in radiative_files if '+' not in cs]
            
            CS_mixEntriesRad = []
            
            labelRad = ttk.Label(mixer, text = "Charge States With Radiative Transitions For Selected Atom:")
            labelRad.grid(column=0, row=0, columnspan=len(radiative_files), pady=40)
            
            if len(PCS_radMixValues) == 0:
                for cs in radiative_files:
                    if '+' in cs:
                        PCS_radMixValues.append(StringVar())
                        CS_mixEntriesRad.append(ttk.Entry(mixer, textvariable=PCS_radMixValues[-1], validate='key', validatecommand=check_num_wrapper))
                        slidersRad.append(ttk.Scale(mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=PCS_radMixValues[-1]))
                        CS_labelsRad.append(ttk.Label(mixer, text = cs.split('intensity_')[1].split('.out')[0]))
                        slidersRad[-1].set(0.0)
            else:
                i = 0
                for cs in radiative_files:
                    if '+' in cs:
                        CS_mixEntriesRad.append(ttk.Entry(mixer, textvariable=PCS_radMixValues[i], validate='key', validatecommand=check_num_wrapper))                        
                        slidersRad.append(ttk.Scale(mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=PCS_radMixValues[i]))
                        CS_labelsRad.append(ttk.Label(mixer, text = cs.split('intensity_')[1].split('.out')[0]))
                        
                        i += 1
            
            if len(NCS_radMixValues) == 0:
                for cs in radiative_files:
                    if '+' not in cs:
                        NCS_radMixValues.append(StringVar())                        
                        CS_mixEntriesRad.append(ttk.Entry(mixer, textvariable=NCS_radMixValues[-1], validate='key', validatecommand=check_num_wrapper))
                        slidersRad.append(ttk.Scale(mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=NCS_radMixValues[-1]))
                        CS_labelsRad.append(ttk.Label(mixer, text = cs.split('intensity_')[1].split('.out')[0]))
                        slidersRad[-1].set(0.0)
            else:
                i = 0
                for cs in radiative_files:
                    if '+' not in cs:
                        CS_mixEntriesRad.append(ttk.Entry(mixer, textvariable=NCS_radMixValues[i], validate='key', validatecommand=check_num_wrapper))
                        slidersRad.append(ttk.Scale(mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=NCS_radMixValues[i]))                        
                        CS_labelsRad.append(ttk.Label(mixer, text = cs.split('intensity_')[1].split('.out')[0]))
                        
                        i += 1
                
            initial_PCS_Order = PCS_order.copy()
            initial_NCS_Order = NCS_order.copy()
            colIndex = 0
            while len(NCS_order) > 0:
                idx = initial_NCS_Order.index(min(NCS_order))
                
                CS_labelsRad[idx].grid(column=colIndex, row=1, sticky=(N), pady=5)
                slidersRad[idx].grid(column=colIndex, row=2, sticky=(N,S), pady=5)
                CS_mixEntriesRad[idx].grid(column=colIndex, row=3, sticky=(W,E), padx=5)
                
                mixer.columnconfigure(colIndex, weight=1)
                
                colIndex += 1
                del NCS_order[NCS_order.index(min(NCS_order))]
            
            while len(PCS_order) > 0:
                idx = initial_PCS_Order.index(min(PCS_order))
                
                CS_labelsRad[idx].grid(column=colIndex, row=1, sticky=(N), pady=5)
                slidersRad[idx].grid(column=colIndex, row=2, sticky=(N,S), pady=5)
                CS_mixEntriesRad[idx].grid(column=colIndex, row=3, sticky=(W,E), padx=5)
                
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
                PCS_order = [int(cs.split('augrate_')[1].split('.out')[0].split('+')[-1]) for cs in auger_files if '+' in cs]
                NCS_order = [int(cs.split('augrate_')[1].split('.out')[0].split('-')[-1]) for cs in auger_files if '+' not in cs]
                
                CS_mixEntriesAug = []
                
                labelAug = ttk.Label(mixer, text = "Charge States With Auger Transitions For Selected Atom:")
                labelAug.grid(column=0, row=4, columnspan=len(radiative_files), pady=40)
                
                if len(PCS_augMixValues) == 0:
                    for cs in auger_files:
                        if '+' in cs:
                            PCS_augMixValues.append(StringVar())
                            CS_mixEntriesAug.append(ttk.Entry(mixer, textvariable=PCS_augMixValues[-1], validate='key', validatecommand=check_num_wrapper))
                            slidersAug.append(ttk.Scale(mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=PCS_augMixValues[-1]))
                            CS_labelsAug.append(ttk.Label(mixer, text = cs.split('augrate_')[1].split('.out')[0]))
                            slidersAug[-1].set(0.0)
                else:
                    i = 0
                    for cs in auger_files:
                        if '+' in cs:
                            CS_mixEntriesAug.append(ttk.Entry(mixer, textvariable=PCS_augMixValues[i], validate='key', validatecommand=check_num_wrapper))                        
                            slidersAug.append(ttk.Scale(mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=PCS_augMixValues[i]))
                            CS_labelsAug.append(ttk.Label(mixer, text = cs.split('augrate_')[1].split('.out')[0]))
                            
                            i += 1
                
                if len(NCS_augMixValues) == 0:
                    for cs in auger_files:
                        if '+' not in cs:
                            NCS_augMixValues.append(StringVar())                        
                            CS_mixEntriesAug.append(ttk.Entry(mixer, textvariable=NCS_augMixValues[-1], validate='key', validatecommand=check_num_wrapper))
                            slidersAug.append(ttk.Scale(mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=NCS_augMixValues[-1]))
                            CS_labelsAug.append(ttk.Label(mixer, text = cs.split('augrate_')[1].split('.out')[0]))
                            slidersAug[-1].set(0.0)
                else:
                    i = 0
                    for cs in auger_files:
                        if '+' not in cs:
                            CS_mixEntriesAug.append(ttk.Entry(mixer, textvariable=NCS_augMixValues[i], validate='key', validatecommand=check_num_wrapper))
                            slidersAug.append(ttk.Scale(mixer, orient=VERTICAL, length=200, from_=100.0, to=0.0, variable=NCS_augMixValues[i]))                        
                            CS_labelsAug.append(ttk.Label(mixer, text = cs.split('augrate_')[1].split('.out')[0]))
                            
                            i += 1
                    
                initial_PCS_Order = PCS_order.copy()
                initial_NCS_Order = NCS_order.copy()
                colIndex = 0
                while len(NCS_order) > 0:
                    idx = initial_NCS_Order.index(min(NCS_order))
                    
                    CS_labelsAug[idx].grid(column=colIndex, row=5, sticky=(N), pady=5)
                    slidersAug[idx].grid(column=colIndex, row=6, sticky=(N,S), pady=5)
                    CS_mixEntriesAug[idx].grid(column=colIndex, row=7, sticky=(W,E), padx=5)
                    
                    mixer.columnconfigure(colIndex, weight=1)
                    
                    colIndex += 1
                    del NCS_order[NCS_order.index(min(NCS_order))]
                
                while len(PCS_order) > 0:
                    idx = initial_PCS_Order.index(min(PCS_order))
                    
                    CS_labelsAug[idx].grid(column=colIndex, row=5, sticky=(N), pady=5)
                    slidersAug[idx].grid(column=colIndex, row=6, sticky=(N,S), pady=5)
                    CS_mixEntriesAug[idx].grid(column=colIndex, row=7, sticky=(W,E), padx=5)
                    
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
                            Ion_Populations[cs + '_y'].append(float(vals[col + 1]))
                
            
            y_max = max(combined_y)
            for cs in ionpopdata[0]:
                Ion_Populations[cs + '_y'] = [pop * 100 / y_max for pop in Ion_Populations[cs + '_y']]
            
            Ion_Population_Functions = {}
            #linear interpolation because of "corners" in the distribution functions
            for cs in ionpopdata[0]:
                order = np.argsort(Ion_Populations[cs + '_x'])
                Ion_Population_Functions[cs] = interp1d(np.array(Ion_Populations[cs + '_x'])[order], np.array(Ion_Populations[cs + '_y'])[order], kind='linear')
            
            combined_x = list(set(combined_x))
            
            temperature_max = max(combined_x)
            temperature_min = min(combined_x)
            
            if len(auger_files) > 0:
                fig_row = 7
            else:
                fig_row = 4
            
            # Figura onde o grÃ¡fico vai ser desenhado
            f = Figure(figsize=(10, 5), dpi=100)  # canvas para o grafico do espectro
            # plt.style.use('ggplot') Estilo para os plots
            a = f.add_subplot(111)  # zona onde estara o grafico
            a.set_xlabel('Temperature (K)')
            a.set_ylabel('Population')
            # ---------------------------------------------------------------------------------------------------------------
            # Frames onde se vÃ£o por a figura e os labels e botÃµes e etc
            figure_frame = Frame(mixer, relief=GROOVE)  # frame para o grafico
            
            figure_frame.grid(column=0, row=fig_row, columnspan=max(len(radiative_files), len(auger_files)), pady=20)
            
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
                    if len(PCS_radMixValues) > 0:
                        i = 0
                        for cs_file in radiative_files:
                            if cs in cs_file:
                                try:
                                    PCS_radMixValues[i].set(str(Ion_Population_Functions[cs](float(temperature.get()))))
                                except:
                                    PCS_radMixValues[i].set("0.0")
                                
                                break
                        
                            if '+' in cs:
                                i += 1
                        
                    if len(NCS_radMixValues) > 0:
                        i = 0
                        for cs_file in radiative_files:
                            if cs in cs_file:
                                try:
                                    NCS_radMixValues[i].set(str(Ion_Population_Functions[cs](float(temperature.get()))))
                                except:
                                    NCS_radMixValues[i].set("0.0")
                                
                                break
                            
                            if '+' not in cs:
                                i += 1
                
                if len(auger_files) > 0:
                    for cs in Ion_Population_Functions:
                        if len(PCS_augMixValues) > 0:
                            i = 0
                            for cs_file in auger_files:
                                if cs in cs_file:
                                    try:
                                        PCS_augMixValues[i].set(str(Ion_Population_Functions[cs](float(temperature.get()))))
                                    except:
                                        PCS_augMixValues[i].set("0.0")
                                    
                                    break
                            
                                if '+' in cs:
                                    i += 1
                            
                        if len(NCS_augMixValues) > 0:
                            i = 0
                            for cs_file in auger_files:
                                if cs in cs_file:
                                    try:
                                        NCS_augMixValues[i].set(str(Ion_Population_Functions[cs](float(temperature.get()))))
                                    except:
                                        NCS_augMixValues[i].set("0.0")
                                    
                                    break
                                
                                if '+' not in cs:
                                    i += 1
            
            temperature.trace_add("write", update_temp_line)
            temp_slider = ttk.Scale(mixer, orient=HORIZONTAL, length=200, from_=temperature_min, to=temperature_max, variable=temperature)
            temp_entry = ttk.Entry(mixer, textvariable=temperature, validate='key', validatecommand=check_num_wrapper)
            temp_slider.grid(column=0, row=fig_row + 1, columnspan=max(len(radiative_files), len(auger_files)) - 1, sticky=(W,E), padx=10, pady=20)
            temp_entry.grid(column=max(len(radiative_files), len(auger_files)) - 1, row=fig_row + 1, sticky=(W,E), padx=5)
            
            mixer.rowconfigure(fig_row + 1, weight=1)
            
            for cs in ionpopdata[0]:
                x_min = min(Ion_Populations[cs + '_x'])
                x_max = max(Ion_Populations[cs + '_x'])
                
                temp_new = np.arange(x_min, x_max, (x_max - x_min) / 100)
                pop_new = Ion_Population_Functions[cs](temp_new)
                
                a.plot(temp_new, pop_new, label=cs)
            
            a.legend()
        
        sim.bind('<Return>', enter_function)  # BotÃ£o para correr a calculate quando se clica no enter
        # ---------------------------------------------------------------------------------------------------------------
        # DropList das transiÃ§Ãµes, Labels e botÃ£o calculate a apresentar na janela
        drop_menu = ttk.Combobox(buttons_frame, value=[transition for transition in the_dictionary], height=5, width=10)
        drop_menu.set('Transitions:')
        drop_menu.bind("<<ComboboxSelected>>", selected)
        drop_menu.grid(row=0, column=0)

        # Min Max e NÂº Pontos
        ttk.Label(buttons_frame2, text="Points").pack(side=LEFT)
        points = ttk.Entry(buttons_frame2, width=7, textvariable=number_points).pack(side=LEFT)
        ttk.Label(buttons_frame2, text="x Max").pack(side=LEFT)
        max_x = ttk.Entry(buttons_frame2, width=7, textvariable=x_max).pack(side=LEFT)
        ttk.Label(buttons_frame2, text="x Min").pack(side=LEFT)
        min_x = ttk.Entry(buttons_frame2, width=7, textvariable=x_min).pack(side=LEFT)
        ttk.Button(master=buttons_frame2, text="Reset", command=lambda: reset_limits()).pack(side=LEFT, padx=(30, 0))

        # Res, Offsets e Calculate
        ttk.Style().configure('red/black.TButton', foreground='red', background='black')  # , font = ('Sans','10','bold'))  #definicoes botao "calculate"
        ttk.Button(master=buttons_frame3, text="Calculate", command=lambda: plot_stick(a), style='red/black.TButton').pack(side=RIGHT, padx=(30, 0))
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
        options_menu.add_checkbutton(label='Show Total Y', variable=totalvar, onvalue='Total', offvalue='No')
        options_menu.add_separator()
        options_menu.add_checkbutton(label='Log Scale Y Axis', variable=yscale_log, onvalue='Ylog', offvalue='No')
        options_menu.add_checkbutton(label='Log Scale X Axis', variable=xscale_log, onvalue='Xlog', offvalue='No')
        options_menu.add_separator()
        options_menu.add_command(label="Load Experimental Spectrum", command=load)
        options_menu.add_checkbutton(label='Perform Autofit', variable=autofitvar, onvalue='Yes', offvalue='No')
        options_menu.add_separator()
        options_menu.add_checkbutton(label = "Import Detector Efficiency", command = load_effic_file)
        options_menu.add_separator()
        options_menu.add_command(label="Export Spectrum", command=lambda: write_to_xls(satelite_var.get(), xfinal, yfinal, yfinals, ytot, energy_offset.get(), yoffset.get(), exp_x, exp_y, residues_graph, radiative_files, auger_files, label1, time_of_click))
        options_menu.add_separator()
        options_menu.add_command(label="Choose New Element", command=restarter)
        options_menu.add_command(label="Quit", command=_quit)
        # ---------------------------------------------------------------------------------------------------------------
        my_menu.add_cascade(label="Spectrum Type", menu=stick_plot_menu)
        choice_var = StringVar(value='Simulation')
        stick_plot_menu.add_checkbutton(label='Stick', variable=choice_var, onvalue='Stick', offvalue='')
        stick_plot_menu.add_checkbutton(label='Simulation', variable=choice_var, onvalue='Simulation', offvalue='')
        stick_plot_menu.add_checkbutton(label='CS Mixture: Stick', variable=choice_var, onvalue='M_Stick', offvalue='', command=configureCSMix, state='disabled')
        stick_plot_menu.add_checkbutton(label='CS Mixture: Simulation', variable=choice_var, onvalue='M_Simulation', offvalue='', command=configureCSMix, state='disabled')
        if CS_exists:
            stick_plot_menu.entryconfigure(2, state=NORMAL)
            stick_plot_menu.entryconfigure(3, state=NORMAL) # Good TK documentation: https://tkdocs.com/tutorial/menus.html
        # ---------------------------------------------------------------------------------------------------------------
        my_menu.add_cascade(label="Transition Type", menu=transition_type_menu)
        satelite_var = StringVar(value='Diagram')
        transition_type_menu.add_checkbutton(label='Diagram', variable=satelite_var, onvalue='Diagram', offvalue='', command=update_transition_dropdown)
        transition_type_menu.add_checkbutton(label='Satellites', variable=satelite_var, onvalue='Satellites', offvalue='', command=update_transition_dropdown)
        transition_type_menu.add_checkbutton(label='Diagram + Satellites', variable=satelite_var, onvalue='Diagram + Satellites', offvalue='', command=update_transition_dropdown)
        transition_type_menu.add_checkbutton(label='Auger', variable=satelite_var, onvalue='Auger', offvalue='', command=update_transition_dropdown)
        # ---------------------------------------------------------------------------------------------------------------
        my_menu.add_cascade(label="Fit Type", menu=fit_type_menu)
        type_var = StringVar(value='Lorentzian')
        fit_type_menu.add_checkbutton(label='Voigt', variable=type_var, onvalue='Voigt', offvalue='')
        fit_type_menu.add_checkbutton(label='Lorentzian', variable=type_var, onvalue='Lorentzian', offvalue='')
        fit_type_menu.add_checkbutton(label='Gaussian', variable=type_var, onvalue='Gaussian', offvalue='')
        # ---------------------------------------------------------------------------------------------------------------
        my_menu.add_cascade(label="Normalization Options", menu=norm_menu)
        norm_menu.add_checkbutton(label='to Experimental Maximum', variable=normalizevar, onvalue='ExpMax', offvalue='No')
        norm_menu.add_checkbutton(label='to Unity', variable=normalizevar, onvalue='One', offvalue='No')
        # ---------------------------------------------------------------------------------------------------------------
        my_menu.add_cascade(label="Excitation Mechanism", menu=exc_mech_menu, state="disabled")  # Apagar o state para tornar funcional
        exc_mech_var = StringVar(value='')
        exc_mech_menu.add_checkbutton(label='Nuclear Electron Capture', variable=exc_mech_var, onvalue='NEC', offvalue='')
        exc_mech_menu.add_checkbutton(label='Photoionization', variable=exc_mech_var, onvalue='PIon', offvalue='')
        exc_mech_menu.add_checkbutton(label='Electron Impact Ionization', variable=exc_mech_var, onvalue='EII', offvalue='')
        # ---------------------------------------------------------------------------------------------------------------
        sim.mainloop()
    return 0


def params(z):  # Definicoes relacionadas com a segunda janela (depois da tabela periodica)
    parameters = Tk()  # Abrir uma janela com botoes que seleccionam o que calcular (yields, widths, cross sections e simulacao)
    parameters.title("Atomic Parameters")  # nome da janela

    check_var = IntVar()  # variavel que vai dar o valor do botao seleccionado (yields=1, widths=2, cross sections=3, simulacao=4)
    check_var.set(1)  # initialize (o botao 1, yields, comeca seleccionado por defeito)
    # ---------------------------------------------------------------------------------------------------------------
    # Propriedades da janela
    subelem = ttk.Frame(parameters, padding="3 3 12 12")
    subelem.grid(column=0, row=0, sticky=(N, W, E, S))
    subelem.columnconfigure(0, weight=1)
    subelem.rowconfigure(0, weight=1)
    # ---------------------------------------------------------------------------------------------------------------
    # BotÃµes
    ttk.Button(subelem, text="Get", command=lambda: calculate(z, check_var.get(), parameters)).grid(column=6, row=5, sticky=E, columnspan=2)  # este botao faz correr a funcao calculate
    ttk.Button(subelem, text="Exit", command=lambda: destroy(parameters)).grid(column=6, row=6, sticky=E, columnspan=2)  # este botao fecha a janela
    ttk.Radiobutton(subelem, text='Yields', variable=check_var, value=1).grid(column=0, row=5, sticky=W)
    ttk.Radiobutton(subelem, text='Level Widths', variable=check_var, value=2).grid(column=1, row=5, sticky=W)
    ttk.Radiobutton(subelem, text='Cross Sections', variable=check_var, value=3).grid(column=0, row=6, sticky=W)
    ttk.Radiobutton(subelem, text='Spectra Simulations', variable=check_var, value=4).grid(column=1, row=6, sticky=W)
    ttk.Label(subelem, text="Which parameters do you want to retrieve?").grid(column=0, row=4, sticky=W, columnspan=2)

    subelem.mainloop()


class App(Tk):
    def __init__(self):
        Tk.__init__(self)

        def quit_window(z):
            self.destroy()
            params(z)

        self.title("Periodic Table of the Elements")

        self.topLabel = Label(self, text="", font=20)
        self.topLabel.grid(row=2, column=3, columnspan=10)

        self.Label1 = Label(self, text="Click the element for which you would like to obtain the atomic parameters.", font=22)
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
            Button(self, text=element[3], width=5, height=2, bg=element[5], command=lambda i=i: quit_window([(i + 1), per_table[i][2]])).grid(row=element[6], column=element[7])

        for child in self.winfo_children(): child.grid_configure(padx=3, pady=3)

        self.mainloop()


def main():
    a = App()


if __name__ == "__main__":
    main()
