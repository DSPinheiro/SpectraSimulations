"""
Module with interface variables that hold the values displayed to the user in the GUI.
"""

from __future__ import annotations

from tkinter import StringVar, DoubleVar
from tkinter import ttk

from matplotlib.patches import Polygon

from typing import List, Dict


# --------------------------------------------------------- #
#                                                           #
#         DEFINE THE VARIABLES TO INITIALIZE LATER          #
#                                                           #
# --------------------------------------------------------- #

# -----------------------------------------------------------------------------------------------------------------------------
# Private variables to hold current parent, window and plotting spaces.
# The parent is required to know where the GUI variables need to be bound to
# Might cause some confusion but when we split the code it was easier to do this instead of passing these between the functions
_parent = None
"""
Private variable for the current tkinter parent object
"""
_a = None
"""
Private variable for the matplotlib plot area object
"""
_f = None
"""
Private variable for the matplotlib simulation figure object
"""
_residues_graph = None
"""
Private variable for the matplotlib simulation residues figure object
"""
_canvas = None
"""
Private variable for the matplotlib canvas
"""
_toolbar = None
"""
Private variable for the matplotlib toolbar
"""


# --------------------------------------------------------------------
# VARIABLES TO HOLD THE VALUES OF THE INTERFACE ENTRIES

# Variable to know if the total intensity needs to be shown
totalvar = None
"""
Variable to know if the total intensity needs to be shown
"""
# Variable to know if the total diagram intensity needs to be shown
totaldiagvar = None
"""
Variable to know if the total diagram intensity needs to be shown
"""
# Variable to know if the total satellite intensity needs to be shown
totalsatvar = None
"""
Variable to know if the total satellite intensity needs to be shown
"""
# Variable to know if the total shake-off intensity needs to be shown
totalshkoffvar = None
"""
Variable to know if the total shake-off intensity needs to be shown
"""
# Variable to know if the total shake-up intensity needs to be shown
totalshkupvar = None
"""
Variable to know if the total shake-up intensity needs to be shown
"""
# Variable to know if the total extra fit intensity needs to be shown
totalextrafitvar = None
"""
Variable to know if the total extra fitting components intensity needs to be shown
"""
# Variable to know if the y axis needs to be set as logarithmic
yscale_log = None
"""
Variable to know if the y axis needs to be set as logarithmic
"""
# Variable to know if the x axis needs to be set as logarithmic
xscale_log = None
"""
Variable to know if the x axis needs to be set as logarithmic
"""
# Variable to know if we need to perform an autofit  to the simulation
autofitvar = None
"""
Variable to know if we need to perform an autofit - lmfit to the simulation
"""

# Variable to know which normalization was chosen, if any
normalizevar = None
"""
Variable to know which normalization was chosen, if any
"""
# Variable to know where the experimental spectrum to load is located, if any
loadvar = None
"""
Variable to know where the experimental spectrum to load is located, if any
"""
# Variable to know where the detector efficiency to load is located, if any
effic_var = None
"""
Variable to know where the detector efficiency to load is located, if any
"""
# Variable to hold the value of the experimental resolution introduced by the user in the interface
exp_resolution = None
"""
Variable to hold the value of the experimental resolution introduced by the user in the interface
"""
# Variable to hold the value of the intensity offset introduced by the user in the interface
yoffset = None
"""
Variable to hold the value of the intensity offset introduced by the user in the interface
"""
# Variable to hold the value of the energy offset introduced by the user in the interface
energy_offset = None
"""
Variable to hold the value of the energy offset introduced by the user in the interface
"""
# Variable to hold the value of the satellite energy offset introduced by the user in the interface
sat_energy_offset = None
"""
Variable to hold the value of the satellite energy offset introduced by the user in the interface
"""
# Variable to hold the value of the shake-off energy offset introduced by the user in the interface
shkoff_energy_offset = None
"""
Variable to hold the value of the shake-off energy offset introduced by the user in the interface
"""
# Variable to hold the value of the shake-up energy offset introduced by the user in the interface
shkup_energy_offset = None
"""
Variable to hold the value of the shake-up energy offset introduced by the user in the interface
"""
# Variable to hold the value of the excitation/beam energy introduced by the user in the interface
excitation_energy = None
"""
Variable to hold the value of the excitation/beam energy introduced by the user in the interface
"""
# Variable to hold the value of the excitation/beam energy FWHM introduced by the user in the interface
excitation_energyFWHM = None
"""
Variable to hold the value of the excitation/beam energy FWHM introduced by the user in the interface
"""
# Variable to hold the flag to include cascades or not in the simulation
include_cascades = None
"""
Variable to hold the flag to include cascades or not in the simulation
"""
# Variable to hold the flag to separate the energy offsets or not in the simulation
separate_offsets = None
"""
Variable to hold the flag to separate the energy offsets or not in the simulation
"""
# Variable to hold the flag to also fit shake probabilities
fit_shake_prob = None
"""
Variable to hold the flag to also fit the shake probabilities
"""
# Variable to hold the flag to plot each 2J stick with a seperate color or not in the simulation
JJ_colors = None
"""
Variable to hold the flag to plot each 2J stick with a seperate color or not in the simulation
"""
# Variable to hold the number of points introduced by the user in the interface, to calculate the energy grid where we simulate the spectrum
number_points = None
"""
Variable to hold the number of points introduced by the user in the interface, to calculate the energy grid where we simulate the spectrum
"""
# Variable to hold the value of the maximum energy to simulate introduced by the user in the interface
x_max = None
"""
Variable to hold the value of the maximum energy to simulate introduced by the user in the interface
"""
# Variable to hold the value of the minimum energy to simulate introduced by the user in the interface
x_min = None
"""
Variable to hold the value of the minimum energy to simulate introduced by the user in the interface
"""
# Variable to hold the value of the progress to show in the progress bar at the bottom of the interface
progress_var = None
"""
Variable to hold the value of the progress to show in the progress bar at the bottom of the interface
"""
# Variable to hold the names of the transitions selected for the simulation
transition_list = []
"""
Variable to hold the names of the transitions selected for the simulation
"""
# Variable to hold the text to show in the interface corresponding to the transition_list
label_text = None
"""
Variable to hold the text to show in the interface corresponding to the transition_list
"""

# Variable to hold the values of 2j selected for the simulation
jj_list = []
"""
Variable to hold the values of 2j selected for the simulation
"""
# Variable to hold the text to show in the interface corresponding to the jj_list
jj_text = None
"""
Variable to hold the text to show in the interface corresponding to the jj_list
"""

# Variable to know which types of transitions to simulate (radiative, auger, satellites)
satelite_var = None
"""
Variable to know which types of transitions to simulate (radiative, auger, satellites)
"""
# Variable to know which type of simulation to perform (stick, simulation, with or without multiple charge states)
choice_var = None
"""
Variable to know which type of simulation to perform (stick, simulation, with or without multiple charge states)
"""
# Variable to know which type of profile we want to simulate fro each line
type_var = None
"""
Variable to know which type of profile we want to simulate fro each line
"""
# Variable to know which type of exiting mechanism we want to consider in the simulation (currently not implemented)
exc_mech_var = None
"""
Variable to know which type of exiting mechanism we want to consider in the simulation (currently not implemented)
"""

# Variable to know which type of baseline we want to use in the quantification
baseline_type = None
"""
Variable to know which type of baseline we want to use in the quantification
"""

# Variable to hold the value of the max window for the SNIP baseline in the quantification
max_window = None
"""
Variable to hold the value of the max window for the SNIP baseline in the quantification
"""

# Variable to hold the value of the smoothing window for the SNIP baseline in the quantification
smooth_window = None
"""
Variable to hold the value of the smoothing window for the SNIP baseline in the quantification
"""

# Variable to hold the flag for the iterating order in the SNIP baseline in the quantification
decreasing = None
"""
Variable to hold the flag for the iterating order in the SNIP baseline in the quantification
"""


#Mix Values of the various charge states used in the simulation
PCS_radMixValues: List[StringVar] = []
"""
Mixture values for the positive charge states when performing a radiative simulation
"""
NCS_radMixValues: List[StringVar] = []
"""
Mixture values for the negative charge states when performing a radiative simulation
"""
PCS_augMixValues: List[StringVar] = []
"""
Mixture values for the positive charge states when performing an auger simulation
"""
NCS_augMixValues: List[StringVar] = []
"""
Mixture values for the negative charge states when performing an auger simulation
"""

# Currently selected element list for quantification
elementList: List[tuple[int, str, str]] = []
"""
List of the currently selected element list for quantification
"""

# Currently plotted element span list for quantification
plotted_element_rois: List[Polygon] = []
"""
Currently plotted element span list for quantification
"""

# List of values used to hold the alpha coeficients for each element for the selected spectrum
alphaEntries: List[DoubleVar] = []
"""
List of values used to hold the alpha coeficients for each element for the selected spectrum
"""

# List of values used to hold the current quantity for each element for the selected spectrum
quantityLabels: List[DoubleVar] = []
"""
List of values used to hold the current quantity for each element for the selected spectrum
"""


# List of values used to hold the target amounts for each element for the selected spectrum
targetEntries: List[DoubleVar] = []
"""
List of values used to hold the target amounts for each element for the selected spectrum
"""

# List of values used to hold the low target amounts for each element for the selected spectrum
targetNegEntries: List[DoubleVar] = []
"""
List of values used to hold the low target amounts for each element for the selected spectrum
"""

# List of values used to hold the high target amounts for each element for the selected spectrum
targetPosEntries: List[DoubleVar] = []
"""
List of values used to hold the high target amounts for each element for the selected spectrum
"""

# Flag to control if we are showing the periodic table for the quantification interface
launched_ptable = False
"""
Flag to control if we are showing the periodic table for the quantification interface
"""

# Flag to control if we are showing the matrix parameters window for the quantification interface
launched_quantPars = False
"""
Flag to control if we are showing the matrix parameters window for the quantification interface
"""

# Dictionary to hold the randomly selected colors for each of the selected elements
elementColors: Dict[str, str] = {}
"""
Dictionary to hold the randomly selected colors for each of the selected elements
"""


# ---------------------------------------------------------------------
# VARIABLES TO HOLD SOME TKINTER WIDGETS

# Dropdown from where to choose the transitions to simulate
drop_menu = None
"""
Dropdown from where to choose the transitions to simulate
"""

# Dropdown from where to choose the initial state 2j values to simulate
drop_menu_2j = None
"""
Dropdown from where to choose the initial state 2j values to simulate
"""

# The total y menu cascade
total_menu = None
"""
The total y menu cascade
"""

# Dropdown from where to choose the spectrum to quantify
drop_spectra = None
"""
Dropdown from where to choose the spectrum to quantify
"""

# Dropdown from where to choose the xray tube spectrum for quantification
drop_tube_spectra = None
"""
Dropdown from where to choose the xray tube spectrum for quantification
"""

# Frame that holds the table with the quantification and parameters
table = None
"""
Frame that holds the table with the quantification and parameters
"""

# Dropdown from where to choose the quantification file to use for the selected spectrum
drop_quantConfs = None
"""
Dropdown from where to choose the quantification file to use for the selected spectrum
"""

# List of dropdowns for each element from where to choose the units
drop_units_list: List[ttk.Combobox] = []
"""
List of dropdowns for each element from where to choose the units
"""

# Current matpltolib figure axis handle
graph_area = None
"""
Current matpltolib figure axis handle
"""