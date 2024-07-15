# GUI Imports
try:
    from tkinter import *
    print('\033[92m' + "Base Tkinter imported correctly!" + '\033[0m')
except:
    print('\033[91m' + "Error importing base Tkinter!" + '\033[0m')

try:
    from tkinter import ttk
    print('\033[92m' + "Tkinter elements imported correctly!" + '\033[0m')
except:
    print('\033[91m' + "Error importing Tkinter elements!" + '\033[0m')

try:
    from tkinter import messagebox
    print('\033[92m' + "Tkinter messagebox imported correctly!" + '\033[0m')
except:
    print('\033[91m' + "Error importing Tkinter messagebox!" + '\033[0m')

try:
    from tkinter.filedialog import askopenfilename
    print('\033[92m' + "Tkinter file picker imported correctly!" + '\033[0m')
except:
    print('\033[91m' + "Error importing Tkinter file picker!" + '\033[0m')

# OS Imports for paths, files and dates
try:
    import os
    print('\033[92m' + "OS package imported correctly!" + '\033[0m')
except:
    print('\033[91m' + "Error importing OS package. Something might be very wrong!" + '\033[0m')

try:
    import csv
    print('\033[92m' + "CSV file package imported correctly!" + '\033[0m')
except:
    print('\033[91m' + "Error importing CSV package. Is your python version outdated?" + '\033[0m')

try:
    from pathlib import Path
    print('\033[92m' + "PathLib package imported correctly!" + '\033[0m')
except:
    print('\033[91m' + "Error importing PathLib package. Is your python version outdated?" + '\033[0m')

try:
    from datetime import datetime
    print('\033[92m' + "Datetime package imported correctly!" + '\033[0m')
except:
    print('\033[91m' + "Error importing datetime package. Is your python version outdated?" + '\033[0m')

# Matplotlib imports for plotting
try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.backends._backend_tk import NavigationToolbar2Tk
    print('\033[92m' + "Matplotlib Tkinter backend compatibilities imported correctly!" + '\033[0m')
except:
    print('\033[91m' + "Error importing Matplotlib Tkinter backend compatibilities!" + '\033[0m')

try:
    from matplotlib.backend_bases import key_press_handler
    print('\033[92m' + "Matplotlib base key press handler backend imported correctly!" + '\033[0m')
except:
    print('\033[91m' + "Error importing Matplotlib base key press handler!" + '\033[0m')

try:
    from matplotlib.figure import Figure
    print('\033[92m' + "Matplotlib figure imported correctly!" + '\033[0m')
except:
    print('\033[91m' + "Error importing Matplotlib!" + '\033[0m')

try:
    from matplotlib import gridspec
    print('\033[92m' + "Matplotlib gridspec imported correctly!" + '\033[0m')
except:
    print('\033[91m' + "Error importing Matplotlib gridspec!" + '\033[0m')


# Numpy import, interpolation and fitting package
try:
    import numpy as np
    print('\033[92m' + "Numpy imported correctly!" + '\033[0m')
except:
    print('\033[91m' + "Error importing Numpy!" + '\033[0m')

try:
    from scipy.interpolate import interp1d
    print('\033[92m' + "Scipy interpolation package imported correctly!" + '\033[0m')
except:
    print('\033[91m' + "Error importing Scipy interpolation package!" + '\033[0m')

try:
    from lmfit import Minimizer, Parameters, report_fit, fit_report
    print('\033[92m' + "Lmfit package minimizer imported correctly!" + '\033[0m')
except:
    print('\033[91m' + "Error importing Lmfit minimizer!" + '\033[0m')


try:
    from iminuit import Minuit
    print('\033[92m' + "iMinuit package minimizer imported correctly!" + '\033[0m')
except:
    print('\033[91m' + "Error importing iMinuit minimizer!" + '\033[0m')

try:
    import mplcursors
    print('\033[92m' + "mplcursors package imported correctly!" + '\033[0m')
except:
    print('\033[91m' + "Error importing mplcursors!" + '\033[0m')

try:
    import scienceplots
    print('\033[92m' + "scienceplots (latex) package imported correctly!" + '\033[0m')
except:
    print('\033[91m' + "Error importing scienceplots (latex)!" + '\033[0m')

try:
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    print('\033[92m' + "sklearn package imported correctly!" + '\033[0m')
except:
    print('\033[91m' + "Error importing sklearn!" + '\033[0m')

try:
    import pybaselines
    print('\033[92m' + "pybaselines package imported correctly!" + '\033[0m')
except:
    print('\033[91m' + "Error importing pybaselines!" + '\033[0m')


try:
    import pybaselines
    print('\033[92m' + "pybaselines package imported correctly!" + '\033[0m')
except:
    print('\033[91m' + "Error importing pybaselines!" + '\033[0m')
