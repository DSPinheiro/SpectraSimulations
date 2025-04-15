"""
Module that holds various global level data variables for the simulations.
Here we have variables that are only initialized and are later filled by data from files or simulation calculations
As well as static variables that are used to list fixed data such as transition labels and periodic table values.
No functions should be defined in this module.
"""

from __future__ import annotations
from typing import List, Dict, Tuple

from data.definitions import Line

import numpy as np
import numpy.typing as npt



# --------------------------------------------- #
#                                               #
#                  DATA LINES                   #
#                                               #
# --------------------------------------------- #
# region

#########################
###     MCDF DATA     ###
#########################
# region

# RATES DATA (NEUTRAL)
# region

#Raw data read from the radiative transitions file to be simulated
lineradrates: List[Line] = []
"""
Data from the radiative spectrum read from file
"""
#Raw data read from the satellite transitions file to be simulated
linesatellites: List[Line] = []
"""
Data from the satellite spectrum read from file
"""
#Raw data read from the auger transitions file to be simulated
lineauger: List[Line] = []
"""
Data from the auger spectrum read from file
"""
#Raw data read from the shake-up transitions file to be simulated, for each orbital the shake-up electron is promoted to
lineshakeup: List[Line] = []
"""
Data from the shake-up spectrum read from file for each orbital the shake-up electron is promoted to
"""
#Raw data read from the shake-up file to be simulated
shakeup: List[List[str]] = []
"""
Shake-up probabilities read from file
"""
#Raw data read from the shake-off file to be simulated
shakeoff: List[List[str]] = []
"""
Shake-off probabilities read from file
"""

# endregion

# RATES DATA (IONS)
# region

#Raw data read from the radiative transitions files to be simulated, for each charge state split by positive and negative CS
lineradrates_PCS: List[List[Line]] = []
"""
Data from the radiative spectrum read from file for each of the positive charge states
"""
lineradrates_NCS: List[List[Line]] = []
"""
Data from the radiative spectrum read from file for each of the negative charge states
"""
#Raw data read from the auger transitions files to be simulated, for each charge state split by positive and negative CS
lineaugrates_PCS: List[List[Line]] = []
"""
Data from the auger spectrum read from file for each of the positive charge states
"""
lineaugrates_NCS: List[List[Line]] = []
"""
Data from the auger spectrum read from file for each of the negative charge states
"""
#Raw data read from the satellite transitions files to be simulated, for each charge state split by positive and negative CS
linesatellites_PCS: List[List[Line]] = []
"""
Data from the satellite spectrum read from file for each of the positive charge states
"""
linesatellites_NCS: List[List[Line]] = []
"""
Data from the satellite spectrum read from file for each of the negative charge states
"""

# endregion

# RATES DATA (EXCITATIONS)
# region

#Raw data read from the radiative transitions files to be simulated, for each excitation
lineradrates_EXC: List[List[Line]] = []
"""
Data from the radiative spectrum read from file for each excitation
"""
#Raw data read from the satellite transitions files to be simulated, for each excitation
linesatellites_EXC: List[List[Line]] = []
"""
Data from the satellite spectrum read from file for each excitation
"""
#Raw data read from the shake-up transitions file to be simulated, for each orbital the shake-up electron is promoted to
lineshakeup_EXC: List[List[Line]] = []
"""
Data from the shake-up spectrum read from file for each orbital the shake-up electron is promoted to
"""
#Raw data read from the shake-up file to be simulated
shakeup_exc: List[List[List[str]]] = []
"""
Shake-up probabilities read from file
"""
#Raw data read from the shake-off file to be simulated
shakeoff_exc: List[List[List[str]]] = []
"""
Shake-off probabilities read from file
"""
#Raw data read from the neutral transitions files to be simulated, for each excitation (excitation probability)
linenurates_EXC: List[List[Line]] = []
"""
Data from the neutral decay spectrum read from file for each excitation
"""


# endregion

# RATES DATA (QUANTIFICATION)
# region

#Raw data read from the radiative transitions files to be simulated, for each selected element for quantification
lineradrates_quant: Dict[str, List[Line] | None] = {}
"""
Data from the radiative spectrum read from file for each selected element for quantification
"""
#Raw data read from the satellite transitions files to be simulated, for each selected element for quantification
linesatellites_quant: Dict[str, List[Line] | None] = {}
"""
Data from the satellite spectrum read from file for each selected element for quantification
"""
#Raw data read from the shake-up transitions file to be simulated, for each orbital the shake-up electron is promoted to
lineshakeup_quant: Dict[str, List[Line] | None] = {}
"""
Data from the shake-up spectrum read from file for each orbital the shake-up electron is promoted to
"""

#Raw data read from the shake-up file to be simulated
shakeup_quant: Dict[str, List[List[str]]] = {}
"""
Shake-up probabilities read from file
"""

#Raw data read from the shake-off file to be simulated
shakeoff_quant: Dict[str, List[List[str]] | None] = {}
"""
Shake-off probabilities read from file
"""

# endregion

# POPULATION DATA (IONS)
# region

#Raw data read from the ion population file
ionpopdata: List[List[str]] = []
"""
Data read from the ion populations file
"""

# endregion

# IONIZATION DATA (SINGLE)
# region

#Raw data read from the 1 hole ionization energies file
ionizationsrad: List[Line] = []
"""
Data from the ionization energies file for 1 hole radiative transitions
"""
#Raw data read from the 2 hole ionization energies file
ionizationssat: List[Line] = []
"""
Data from the ionization energies file for 2 hole radiative transitions
"""
#Raw data read from the shake-up ionization energies file to be simulated, for each orbital the shake-up electron is promoted to
ionizationsshakeup: List[Line] = []
"""
Data from the shake-up ionization energies read from file for each orbital the shake-up electron is promoted to
"""

# endregion


# IONIZATION DATA (EXCITATIONS)
# region

#Raw data read from the 1 hole ionization energies file
ionizationsrad_exc: List[List[Line]] = []
"""
Data from the ionization energies file for 1 hole radiative transitions
"""
#Raw data read from the 2 hole ionization energies file
ionizationssat_exc: List[List[Line]] = []
"""
Data from the ionization energies file for 2 hole radiative transitions
"""
#Raw data read from the shake-up ionization energies file to be simulated, for each orbital the shake-up electron is promoted to
ionizationsshakeup_exc: List[List[Line]] = []
"""
Data from the shake-up ionization energies read from file for each orbital the shake-up electron is promoted to
"""
#Total decay rates summed for all levels of each excitation
total_decayrates_exc: List[float] = []
"""
Total decay rates summed for all levels of each excitation
"""

#Total decay rates summed for all levels of each excitation
level_decayrates_exc: List[Dict[str, float]] = []
"""
Total decay rates summed for all levels of each excitation
"""

# endregion


# IONIZATION DATA (QUANTIFICATION)
# region

#Raw data read from the 1 hole ionization energies file
ionizationsrad_quant: Dict[str, List[Line] | None] = {}
"""
Data from the ionization energies file for 1 hole radiative transitions
"""

#Raw data read from the 2 hole ionization energies file
ionizationssat_quant: Dict[str, List[Line] | None] = {}
"""
Data from the ionization energies file for 2 hole radiative transitions
"""
#Raw data read from the shake-up ionization energies file to be simulated, for each orbital the shake-up electron is promoted to
ionizationsshakeup_quant: Dict[str, List[Line] | None] = {}
"""
Data from the shake-up ionization energies read from file for each orbital the shake-up electron is promoted to
"""

# endregion

# WIDTHS DATA (SINGLE)
# region

#Raw data read from the diagram rates file
diagramwidths: List[Line] = []
"""
Data from the diagram rates with partial widths file for this element
"""
#Raw data read from the auger rates file
augerwidths: List[Line] = []
"""
Data from the auger rates with partial widths file for this element
"""
#Raw data read from the satellite rates file
satellitewidths: List[Line] = []
"""
Data from the satellite rates with partial widths file for this element
"""
#Raw data read from the shakeup rates file
shakeupwidths: List[Line] = []
"""
Data from the shake-up rates with partial widths file for this element
"""

#Dictionary to hold the partial widths for each level to calculate the overlap integral with the excitation beam
partialWidths: Dict[str, Dict[str, float]] = {}
"""
Dictionary to hold the partial widths for each level to calculate the overlap integral with the excitation beam
"""

# endregion

# WIDTHS DATA (EXCITATIONS)
# region

#Raw data read from the diagram rates file
diagramwidths_exc: List[List[Line]] = []
"""
Data from the diagram rates with partial widths file for this element
"""
#Raw data read from the auger rates file
augerwidths_exc: List[List[Line]] = []
"""
Data from the auger rates with partial widths file for this element
"""
#Raw data read from the satellite rates file
satellitewidths_exc: List[List[Line]] = []
"""
Data from the satellite rates with partial widths file for this element
"""
#Raw data read from the shakeup rates file
shakeupwidths_exc: List[List[Line]] = []
"""
Data from the shake-up rates with partial widths file for this element
"""

#Dictionary to hold the partial widths for each level to calculate the overlap integral with the excitation beam
partialWidths_exc: List[Dict[str, Dict[str, float]]] = [{}]
"""
Dictionary to hold the partial widths for each level to calculate the overlap integral with the excitation beam
"""

# endregion

# WIDTHS DATA (QUANTIFICATION)
# region

#Raw data read from the diagram rates file
diagramwidths_quant: Dict[str, List[Line] | None] = {}
"""
Data from the diagram rates with partial widths file for this element
"""

#Raw data read from the satellite rates file
satellitewidths_quant: Dict[str, List[Line] | None] = {}
"""
Data from the satellite rates with partial widths file for this element
"""
#Raw data read from the shakeup rates file
shakeupwidths_quant: Dict[str, List[Line] | None] = {}
"""
Data from the shake-up rates with partial widths file for this element
"""

#Dictionary to hold the partial widths for each level to calculate the overlap integral with the excitation beam
partialWidths_quant: Dict[str, Dict[str, Dict[str, float]]] = {}
"""
Dictionary to hold the partial widths for each level to calculate the overlap integral with the excitation beam
"""

# endregion

# IONIZATION DATA (SINGLE)
# region

#Raw data read from the mean radius file
meanRs: List[List[str]] = []
"""
Data read from the mean radius file
"""

#Dictionary to hold the functions to calculate the MRBEB cross section with the parameters for each shell
elementMRBEB = {}
"""
Functions to calculate the MRBEB cross section with the parameters for each shell
"""
#Dictionary to hold the formation energies for each level to calculate cross sections with the parameters
formationEnergies: Dict[str, Dict[str, float]] = {}
"""
Formation energies to calculate cross sections. Optimized to use in filtering loops
"""

#Photo absorption spline interpolation to use for the cross section calculation
ELAMPhotoSpline = None
"""
Spline interpolation to use when calculating the cross section
"""

# endregion

# IONIZATION DATA (EXCITATIONS)
# region

#Dictionary to hold the formation energies for each level to calculate cross sections with the parameters
formationEnergies_exc: List[Dict[str, Dict[str, float]]] = [{}]
"""
Formation energies to calculate cross sections. Optimized to use in filtering loops
"""

#Photo absorption spline interpolation to use for the cross section calculation
ELAMPhotoSpline_exc = None
"""
Spline interpolation to use when calculating the cross section
"""

# endregion

# IONIZATION DATA (QUANTIFICATION)
# region

#Flag to check if a file containing the meanRs data for MRBEB cross section exists
meanRs_quant: Dict[str, List[List[str]] | None] = {}
"""
Flag for if a meanRs file was found. Disables MRBEB cross section option
"""

#Dictionary to hold the functions to calculate the MRBEB cross section with the parameters for each shell
elementMRBEB_quant = {}
"""
Functions to calculate the MRBEB cross section with the parameters for each shell
"""
#Dictionary to hold the formation energies for each level to calculate cross sections with the parameters
formationEnergies_quant: Dict[str, Dict[str, Dict[str, float]]] = {}
"""
Formation energies to calculate cross sections. Optimized to use in filtering loops
"""

#Photo absorption spline interpolation to use for the cross section calculation
ELAMPhotoSpline_quant = {}
"""
Spline interpolation to use when calculating the cross section
"""

# endregion

# SHAKE DATA (SINGLE)
# region

#Values of the missing shakeup probability calculated from the existing shakeup transitions
#These values are added to the shakeup probability to fullfill 100% total spectral intensity
missing_shakeup: Dict[str, float] = {}
"""
Values of the missing shakeup probability calculated from the existing shakeup transitions
"""
#Value of the averaged missing shakeoff probability calculated from the existing shakeoff transitions
#These value is added to the shakeoff probability to fullfill 100% total spectral intensity
missing_shakeoff: float = 0.0
"""
Values of the missing shakeoff probability calculated from the existing shakeoff transitions
"""

#Dictionary to control the total shake-up probabilities present in the simulation
control_shakeup = {}
"""
Dictionary to control the total shake-up probabilities present in the simulation.
Mainly used for debug
"""
#Dictionary to control the total shake-off probabilities present in the simulation
control_shakeoff = {}
"""
Dictionary to control the total shake-off probabilities present in the simulation.
Mainly used for debug
"""

# Variable to store the realtionships between shake probabilities for each shell
# This is used to manintain the relationships during the shake fitting algorithm
shake_relations = {}
"""
Variable to store the realtionships between shake probabilities for each shell.
This is used to manintain the relationships during the shake fitting algorithm
"""

# Variable to hold the existing shakeups in the spectrum
existing_shakeups = {}
"""
Variable to hold the existing shakeups in the spectrum
"""
# Variable to hold the existing shakeoffs in the spectrum
existing_shakeoffs = {}
"""
Variable to hold the existing shakeoffs in the spectrum
"""

#Dictionary to hold the splines for the shake-up probabilities as a function of the excited orbital n
shakeUPSplines = {}
"""
Splines for the shake-up probabilities as a function of the excited orbital n
"""

#Dictionary to hold the ratios for each loaded excited shake-up orbital. This was intensity independent of existing shake-ups
totalShakeOrbRatios = {}
"""
Dictionary to hold the ratios for each loaded excited shake-up orbital. This was intensity independent of existing shake-ups.
This happens because the original MCDF spectrum is calculated seperatly for each excited orbital
"""


# endregion

# SHAKE DATA (EXCITATIONS)
# region

#Values of the missing shakeup probability calculated from the existing shakeup transitions
#These values are added to the shakeup probability to fullfill 100% total spectral intensity
missing_shakeup_exc: List[Dict[str, float]] = [{}]
"""
Values of the missing shakeup probability calculated from the existing shakeup transitions
"""
#Value of the averaged missing shakeoff probability calculated from the existing shakeoff transitions
#These value is added to the shakeoff probability to fullfill 100% total spectral intensity
missing_shakeoff_exc: List[float] = [0.0]
"""
Values of the missing shakeoff probability calculated from the existing shakeoff transitions
"""

#Dictionary to control the total shake-up probabilities present in the simulation
control_shakeup_exc = [{}]
"""
Dictionary to control the total shake-up probabilities present in the simulation.
Mainly used for debug
"""
#Dictionary to control the total shake-off probabilities present in the simulation
control_shakeoff_exc = [{}]
"""
Dictionary to control the total shake-off probabilities present in the simulation.
Mainly used for debug
"""

# Variable to store the realtionships between shake probabilities for each shell
# This is used to manintain the relationships during the shake fitting algorithm
shake_relations_exc = [{}]
"""
Variable to store the realtionships between shake probabilities for each shell.
This is used to manintain the relationships during the shake fitting algorithm
"""

# Variable to hold the existing shakeups in the spectrum
existing_shakeups_exc = [{}]
"""
Variable to hold the existing shakeups in the spectrum
"""
# Variable to hold the existing shakeoffs in the spectrum
existing_shakeoffs_exc = [{}]
"""
Variable to hold the existing shakeoffs in the spectrum
"""

#Dictionary to hold the splines for the shake-up probabilities as a function of the excited orbital n
shakeUPSplines_exc = [{}]
"""
Splines for the shake-up probabilities as a function of the excited orbital n
"""

# endregion

# SHAKE DATA (QUANTIFICATION)
# region

#Values of the missing shakeup probability calculated from the existing shakeup transitions
#These values are added to the shakeup probability to fullfill 100% total spectral intensity
missing_shakeup_quant: Dict[str, Dict[str, float]] = {}
"""
Values of the missing shakeup probability calculated from the existing shakeup transitions
"""
#Value of the averaged missing shakeoff probability calculated from the existing shakeoff transitions
#These value is added to the shakeoff probability to fullfill 100% total spectral intensity
missing_shakeoff_quant: Dict[str, float] = {}
"""
Values of the missing shakeoff probability calculated from the existing shakeoff transitions
"""

#Dictionary to control the total shake-up probabilities present in the simulation
control_shakeup_quant = {}
"""
Dictionary to control the total shake-up probabilities present in the simulation.
Mainly used for debug
"""
#Dictionary to control the total shake-off probabilities present in the simulation
control_shakeoff_quant = {}
"""
Dictionary to control the total shake-off probabilities present in the simulation.
Mainly used for debug
"""

# Variable to store the realtionships between shake probabilities for each shell
# This is used to manintain the relationships during the shake fitting algorithm
shake_relations_quant = {}
"""
Variable to store the realtionships between shake probabilities for each shell.
This is used to manintain the relationships during the shake fitting algorithm
"""

# Variable to hold the existing shakeups in the spectrum
existing_shakeups_quant = {}
"""
Variable to hold the existing shakeups in the spectrum
"""
# Variable to hold the existing shakeoffs in the spectrum
existing_shakeoffs_quant = {}
"""
Variable to hold the existing shakeoffs in the spectrum
"""

#Dictionary to hold the splines for the shake-up probabilities as a function of the excited orbital n
shakeUPSplines_quant = {}
"""
Splines for the shake-up probabilities as a function of the excited orbital n
"""

# endregion

# endregion

#########################
###      DB DATA      ###
#########################
# region

# GENERAL
# region

#NIST Xray line database data
NIST_Data: List[List[str]] = []
"""
List with the lines read from the full NIST XRay line database
"""

# ROIS for the clustered NIST xray line data
NIST_ROIS: Dict[str, List[Tuple[float, float]]] = {}
"""
ROIS for the clustered NIST xray line data
"""

#Raw data read from the shake wheights file to be simulated
shakeweights: List[float] = []
"""
Shake weights read from file
"""

# endregion

# SINGLE
# region

#Raw data read from the ELAM database file for the selected element
ELAMelement: List[str] = []
"""
Data from the ELAM database file for this element
"""

# endregion

# QUANTIFICATION
# region

#Raw data read from the ELAM database file for the selected element
ELAMelement_quant: Dict[str, List[str]] = {}
"""
Data from the ELAM database file for this element
"""

# endregion

# endregion

# endregion

# --------------------------------------------- #
#                                               #
#           QUANTIFICATION PARAMETERS           #
#                                               #
# --------------------------------------------- #
# region

weightFractions: List[List[float]] = []

total_weight: float = 0.0

# endregion

# --------------------------------------------- #
#                                               #
#             SIMULATED SPECTRA Ys              #
#                                               #
# --------------------------------------------- #
# region

# IONIZATION
# region

#Final y of the simulated spectrum (Rad or Aug, no satellite) for each transition
yfinal: List[List[float]] | npt.NDArray[np.float64] = []
"""
Final y values calculated for each of the simulated transitions
"""
#Total y of the simulated spectrum summed over all simulated lines
ytot: List[float] | npt.NDArray[np.float64] = []
"""
Final total y values for all simulated transitions
"""
#Total y of the simulated spectrum summed over all simulated diagram lines
ydiagtot: List[float] | npt.NDArray[np.float64] = []
"""
Final total y values for all simulated diagram transitions
"""
#Total y of the simulated spectrum summed over all simulated satellite lines
ysattot: List[float] | npt.NDArray[np.float64] = []
"""
Final total y values for all simulated satellite transitions
"""
#Total y of the simulated spectrum summed over all simulated shake-off lines
yshkofftot: List[float] | npt.NDArray[np.float64] = []
"""
Final total y values for all simulated shake-off transitions
"""
#Total y of the simulated spectrum summed over all simulated shake-up lines
yshkuptot: List[float] | npt.NDArray[np.float64] = []
"""
Final total y values for all simulated shake-up transitions
"""
#Final y of the simulated satellite lines for each Rad transition
yfinals: List[List[List[float]]] | npt.NDArray[np.float64] = []
"""
Final y values calculated for each of the possible satellite transitions in each of the simulated diagram transitions
"""
#Total y of each extra component for fitting
yextras: npt.NDArray[np.float64] = np.array([np.array([])])
"""
Final total y of each extra component for fitting
"""
#Total y of all extra fitting components
yextrastot: npt.NDArray[np.float64] = np.array([])
"""
Final total y of all extra fitting components
"""
#Final x of the simulated spectrum for each transition
xfinal: npt.NDArray[np.float64] = np.array([])
"""
Final x values calculated for the simulation
"""

# endregion

# EXCITATION
# region

#Final y of the simulated spectrum (Rad or Aug, no satellite) for each transition
yfinal_exc: List[List[float]] | npt.NDArray[np.float64] = []
"""
Final y values calculated for each of the simulated transitions
"""
#Total y of the simulated spectrum summed over all simulated lines
ytot_exc: List[float] | npt.NDArray[np.float64] = []
"""
Final total y values for all simulated transitions
"""
#Total y of the simulated spectrum summed over all simulated diagram lines
ydiagtot_exc: List[float] | npt.NDArray[np.float64] = []
"""
Final total y values for all simulated diagram transitions
"""
#Total y of the simulated spectrum summed over all simulated satellite lines
ysattot_exc: List[float] | npt.NDArray[np.float64] = []
"""
Final total y values for all simulated satellite transitions
"""
#Total y of the simulated spectrum summed over all simulated shake-off lines
yshkofftot_exc: List[float] | npt.NDArray[np.float64] = []
"""
Final total y values for all simulated shake-off transitions
"""
#Total y of the simulated spectrum summed over all simulated shake-up lines
yshkuptot_exc: List[float] | npt.NDArray[np.float64] = []
"""
Final total y values for all simulated shake-up transitions
"""
#Final y of the simulated satellite lines for each Rad transition
yfinals_exc: List[List[List[float]]] | npt.NDArray[np.float64] = []
"""
Final y values calculated for each of the possible satellite transitions in each of the simulated diagram transitions
"""
#Total y of each extra component for fitting
yextras_exc: npt.NDArray[np.float64] = np.array([np.array([])])
"""
Final total y of each extra component for fitting
"""
#Total y of all extra fitting components
yextrastot_exc: npt.NDArray[np.float64] = np.array([])
"""
Final total y of all extra fitting components
"""
#Final x of the simulated spectrum for each transition
xfinal_exc: npt.NDArray[np.float64] = np.array([])
"""
Final x values calculated for the simulation
"""

# endregion


#Currently plotted baseline used for quantification, in the same grid as the plotted experimental spectrum
currentBaseline: List[float] = []
"""
Currently plotted baseline used for quantification, in the same grid as the plotted experimental spectrum
"""

# endregion

# --------------------------------------------- #
#                                               #
#               EXPERIMENTAL DATA               #
#                                               #
# --------------------------------------------- #
# region

#Loaded experimental spectrum x values
exp_x: List[float] | npt.NDArray[np.float64] = []
"""
Loaded experimental x values
"""
#Loaded experimental spectrum y values
exp_y: List[float] | npt.NDArray[np.float64] = []
"""
Loaded experimental y values
"""
#Loaded experimental spectrum y error values
exp_sigma: List[float] | npt.NDArray[np.float64] = []
"""
Loaded experimental y error values
"""

# endregion

# --------------------------------------------- #
#                                               #
#               FILE NAMES / PATHS              #
#                                               #
# --------------------------------------------- #
# region

# IONS
# region

#File names of the radiative transitions for each charge state found
radiative_files: List[str] = []
"""
Names of the radiative rates files for each charge state found
"""
#File names of the auger transitions for each charge state found
auger_files: List[str] = []
"""
Names of the auger rates files for each charge state found
"""
#File names of the satellite transitions for each charge state found
sat_files: List[str] = []
"""
Names of the satellite rates files for each charge state found
"""

# endregion


# EXCITATIONS
# region

#File names of the radiative transitions for each excitation found
radiative_exc_files: List[str] = []
"""
Names of the radiative rates files for each excitation found
"""
#File names of the auger transitions for each excitation found
auger_exc_files: List[str] = []
"""
Names of the auger rates files for each excitation found
"""
#File names of the satellite transitions for each excitation found
sat_exc_files: List[str] = []
"""
Names of the satellite rates files for each excitation found
"""

# endregion

# endregion

# --------------------------------------------- #
#                                               #
#                     FLAGS                     #
#                                               #
# --------------------------------------------- #
# region

# SINGLE
# region

#Flag to check if a file containing the ion population data is present
Ionpop_exists = False
"""
Flag for if an ion population file was found. Not currently in used
"""

#Flag to check if a file containing the meanRs data for MRBEB cross section exists
meanR_exists = False
"""
Flag for if a meanRs file was found. Disables MRBEB cross section option
"""

#Flag to check if a file containing the ELAM database for photoionization cross section exists
ELAM_exists = False
"""
Flag for if the ELAM database file was found. Disables photoionization cross section option
"""

#Flag to check if a file containing the shake-up data exists
Shakeup_exists = False
"""
Flag for if the shake-up file was found. Disables shake-up and uses full shake probabilities for shake-off lines
"""

#Flag to check if a file containing the NIST database for XRay lines exists
NIST_exists = False
"""
Flag for if the NIST database file was found.
"""

#Flag to check if a file containing the NIST database for the clusters of XRay lines exists
NIST_clusters_exists = False
"""
Flag for if the clustered NIST database file was found.
"""

# endregion

# EXCITATIONS
# region

#Flag to check if a file containing the meanRs data for MRBEB cross section exists
meanR_exists_exc: List[bool] = [False]
"""
Flag for if a meanRs file was found. Disables MRBEB cross section option
"""

#Flag to check if a file containing the shake-up data exists
Shakeup_exists_exc: List[bool] = [False]
"""
Flag for if the shake-up file was found. Disables shake-up and uses full shake probabilities for shake-off lines
"""

# endregion

# QUANTIFICATION
# region

#Flag to check if a file containing the meanRs data for MRBEB cross section exists
meanR_exists_quant: Dict[str, bool] = {}
"""
Flag for if a meanRs file was found. Disables MRBEB cross section option
"""

#Flag to check if a file containing the ELAM database for photoionization cross section exists
ELAM_exists_quant: Dict[str, bool] = {}
"""
Flag for if the ELAM database file was found. Disables photoionization cross section option
"""

#Flag to check if a file containing the shake-up data exists
Shakeup_exists_quant: Dict[str, bool] = {}
"""
Flag for if the shake-up file was found. Disables shake-up and uses full shake probabilities for shake-off lines
"""

# endregion

# endregion


# --------------------------------------------- #
#                                               #
#             CONSOLE CONTROL VARS              #
#                                               #
# --------------------------------------------- #
# region

# Verbose level of console logging for the program
verbose = 2

# endregion

# --------------------------------------------- #
#                                               #
#                  MATRIX DATA                  #
#                                               #
# --------------------------------------------- #
# region

#Boost multipliers for the radiative cascades
radBoostMatrixDict: Dict[str, float] = {}
"""
Boost multiplier Data for the diagram transition cascades
"""
#Boost multipliers for the auger cascades
augBoostMatrixDict: Dict[str, float] = {}
"""
Boost multiplier Data for the auger transition cascades
"""
#Boost multipliers for the satellite cascades
satBoostMatrixDict: Dict[str, float] = {}
"""
Boost multiplier Data for the satellite transition cascades
"""

# endregion

# --------------------------------------------- #
#                                               #
#                CONTROL STRINGS                #
#                                               #
# --------------------------------------------- #
# region

# SHAKES (SINGLE)
# region

#Variable to store the labels read from the shake weights file
label1: List[str] = []
"""
Shake labels read from file
"""

#List of labels corresponding to the shake probabilities we want to fit
shakes_to_fit: List[str] = []
"""
List of labels corresponding to the shake probabilities we want to fit
"""

# endregion

# SHAKES (EXCITATIONS)
# region

#Variable to store the labels read from the shake weights file
label1_exc: List[List[str]] = []
"""
Shake labels read from file
"""

# endregion

# SHAKES (QUANTIFICATION)
# region

#Variable to store the labels read from the shake weights file
label1_quant: Dict[str, List[str] | None] = {}
"""
Shake labels read from file
"""

#List of labels corresponding to the shake probabilities we want to fit
shakes_to_fit_quant: Dict[str, List[str]] = {}
"""
List of labels corresponding to the shake probabilities we want to fit
"""

# endregion

# IONS
# region

#Order of the charge states read and stored in the previous variables
rad_PCS: List[str] = []
"""
List with the order that the positive charge states were read for the radiative rates
"""
rad_NCS: List[str] = []
"""
List with the order that the negative charge states were read for the radiative rates
"""

#Order of the charge states read and stored in the previous variables
aug_PCS: List[str] = []
"""
List with the order that the positive charge states were read for the auger rates
"""
aug_NCS: List[str] = []
"""
List with the order that the negative charge states were read for the auger rates
"""

#Order of the charge states read and stored in the previous variables
sat_PCS: List[str] = []
"""
List with the order that the positive charge states were read for the satellite rates
"""
sat_NCS: List[str] = []
"""
List with the order that the negative charge states were read for the satellite rates
"""

# endregion

# EXCITATIONS
# region

#List with the available radiative excitations for this element
rad_EXC: List[str] = []
"""
List with the available radiative excitations for this element
"""
#List with the available satellite excitations for this element
sat_EXC: List[str] = []
"""
List with the available satellite excitations for this element
"""

# endregion

# JJ VALUES
# region

#2J values to be simulated
jj_vals: List[int] = []
"""
2J values to be simulated
"""
# Dictionary to hold the current set of colors for each 2J value (toggled in the interface)
colors_2J = {}
"""
Dictionary to hold the current set of colors for each 2J value (toggled in the interface)
"""

# endregion

# ELEMENT
# region

#Value of the current elements Z
Z = 0
"""
Z value of the current element
"""

#Current elements name
element_name = None
"""
Element name to use when sending the data to plot
"""

# endregion

# QUANTIFICATION
# region

#List of the currently loaded experimental spectra for quantification
currentSpectraList: List[str] = []
"""
List of the currently loaded experimental spectra for quantification
"""

#List of the currently loaded Xray tube spectra for quantification
currentTubeSpectraList: List[str] = []
"""
List of the currently loaded Xray tube spectra for quantification
"""

#List of the existing configurations for quantification
existingQuantConfs: List[str] = []
"""
List of the existing configurations for quantification
"""

#List of the existing elements Z (determined by the existing directories for each Z)
existingElements: List[int] = []
"""
List of the existing elements Z (determined by the existing directories for each Z)
"""

#Dictionary to hold the data of the currently loaded quantification configuration
currentQuantConfig: Dict[str, float] = {}
"""
Dictionary to hold the data of the currently loaded quantification configuration
"""

#Dictionary to hold the data specific to the spectra used to determine the quantification configuration
currentQuantConfigSpectra: Dict[str, Dict[str, Tuple[float, float, float, int]]] = {}
"""
Dictionary to hold the data specific to the spectra used to determine the quantification configuration.
Format:
spectrum name -> {element name -> [target, target -, target +, unit idx]}
"""

# endregion

# endregion

# --------------------------------------------- #
#                                               #
#              FITTING CONTROL VARS             #
#                                               #
# --------------------------------------------- #
# region

#Chi^2 of the current fit
chi_sqrd = 0
"""
Current value of the reduced chi^2 calculated in the current simulation
"""
#Extra fitting components configured in the "Additional fitting functions" interface
extra_fitting_functions: Dict[str, Dict[str, float]] = {}
"""
Extra fitting components configured in the "Additional fitting functions" interface, stored in a dictionary to add in the fitting algorithm
"""

# endregion

# --------------------------------------------- #
#                                               #
#             PREDEFINED DATA VALUES            #
#                                               #
# --------------------------------------------- #
# region

#Mean radius of hydrogen
meanHR = 3 * 0.52918*10**-10 / 2
"""
Hydrogen mean radius to calculate the MRBEB electron impact cross sections
"""
#Value of the speed of light squared multiplyed by the electron mass
mc2 = 510998.9461
"""
Value of the speed of light squared multiplyed by the electron mass for relativistic calculations
"""
#Value of the physical constant alpha
alpha = 1.0/137.035999084
"""
Value of the fine structure constant
"""
#Value of Bohrs radius
a0 = 0.52918*10**-10
"""
Value of Bohrs radius
"""
#Value of the Rydberg energy
R = 13.6057
"""
Value of the Rydberg energy
"""

#Value of the excitation beam energy when the user value for the beam is 0. This is only used to calculate the ratios, assuming all channels are open.
defaultBeam = 1E10 #eV
"""
Value of the excitation beam energy when the user value for the beam is 0.
This is only used to calculate the ratios, assuming all channels are open.
"""

# Console code for clearing the current line and resetting the console
clearLine = '\r\x1b[K'
"""
Console code for clearing the current line and resetting the console
"""

#List of the used weight units to present in the quantification window
weightUnits: List[str] = ['w%', 'ppm', 'mg/kg', 'g/kg', 'ug/kg']
"""
List of the used weight units to present in the quantification window
"""


#Correspondence between Siegbahn notation and relativistic orbitals
labeldict = {'K1': '1s', 'L1': '2s', 'L2': '2p*', 'L3': '2p', 'M1': '3s', 'M2': '3p*', 'M3': '3p', 'M4': '3d*',
             'M5': '3d', 'N1': '4s', 'N2': '4p*', 'N3': '4p', 'N4': '4d*', 'N5': '4d', 'N6': '4f*', 'N7': '4f',
             'O1': '5s', 'O2': '5p*', 'O3': '5p', 'O4': '5d*', 'O5': '5d', 'O6': '5f*', 'O7': '5f', 'O8': '5g*',
             'O9': '5g', 'P1': '6s'}
"""
Correspondence between Siegbahn notation and relativistic orbitals
"""


# Radiative transition dictionary. This is used to list, select and control which transitions are to be simulated
the_dictionary: Dict[str, Dict[str, str | bool]] = {
    # for ionic transitions
    "KL\u2081": {"low_level": "K1", "high_level": "L1", "selected_state": False, "readable_name": "KL1", "latex_name": "KL$_1$"},
    "K\u03B1\u2081": {"low_level": "K1", "high_level": "L3", "selected_state": False, "readable_name": "Kalpha1", "latex_name": "K$\\alpha_1$"},
    "K\u03B1\u2082": {"low_level": "K1", "high_level": "L2", "selected_state": False, "readable_name": "Kalpha2", "latex_name": "K$\\alpha_2$"},
    "K\u03B2\u2081": {"low_level": "K1", "high_level": "M3", "selected_state": False, "readable_name": "Kbeta1", "latex_name": "K$\\beta_1$"},
    "K\u03B2\u2082\u00B9": {"low_level": "K1", "high_level": "N3", "selected_state": False, "readable_name": "Kbeta2 1", "latex_name": "K$\\beta_{12}$"},
    "K\u03B2\u2082\u00B2": {"low_level": "K1", "high_level": "N2", "selected_state": False, "readable_name": "Kbeta2 2", "latex_name": "K$\\beta_{22}$"},
    "K\u03B2\u2083": {"low_level": "K1", "high_level": "M2", "selected_state": False, "readable_name": "Kbeta3", "latex_name": "K$\\beta_{3}$"},
    "K\u03B2\u2084\u00B9": {"low_level": "K1", "high_level": "N5", "selected_state": False, "readable_name": "Kbeta4 1", "latex_name": "K$\\beta_{41}$"},
    "K\u03B2\u2084\u00B2": {"low_level": "K1", "high_level": "N4", "selected_state": False, "readable_name": "Kbeta4 2", "latex_name": "K$\\beta_{42}$"},
    "K\u03B2\u2085\u00B9": {"low_level": "K1", "high_level": "M5", "selected_state": False, "readable_name": "Kbeta5 1", "latex_name": "K$\\beta_{51}$"},
    "K\u03B2\u2085\u00B2": {"low_level": "K1", "high_level": "M4", "selected_state": False, "readable_name": "Kbeta5 2", "latex_name": "K$\\beta_{52}$"},
    "L\u03B2\u2084": {"low_level": "L1", "high_level": "M2", "selected_state": False, "readable_name": "Lbeta4", "latex_name": "L$\\beta_{4}$"},
    "L\u03B2\u2083": {"low_level": "L1", "high_level": "M3", "selected_state": False, "readable_name": "Lbeta3", "latex_name": "L$\\beta_{3}$"},
    "L\u03B2\u2081\u2080": {"low_level": "L1", "high_level": "M4", "selected_state": False, "readable_name": "Lbeta10", "latex_name": "L$\\beta_{10}$"},
    "L\u03B2\u2089": {"low_level": "L1", "high_level": "M5", "selected_state": False, "readable_name": "Lbeta9", "latex_name": "L$\\beta_{9}$"},
    "L\u03B3\u2082": {"low_level": "L1", "high_level": "N2", "selected_state": False, "readable_name": "Lgamma2", "latex_name": "L$\\gamma_{2}$"},
    "L\u03B3\u2083": {"low_level": "L1", "high_level": "N3", "selected_state": False, "readable_name": "Lgamma3", "latex_name": "L$\\gamma_{3}$"},
    "L\u03B3\u2082'": {"low_level": "L1", "high_level": "O2", "selected_state": False, "readable_name": "Lgamma2'", "latex_name": "L$\\beta_{2'}$"},
    "L\u03B3\u2084": {"low_level": "L1", "high_level": "O3", "selected_state": False, "readable_name": "Lgamma4", "latex_name": "L$\\gamma_{4}$"},
    "L\u03B7": {"low_level": "L2", "high_level": "M1", "selected_state": False, "readable_name": "Ln", "latex_name": "L$\\eta$"},
    "L\u03B2\u2081\u2087": {"low_level": "L2", "high_level": "M3", "selected_state": False, "readable_name": "Lbeta17", "latex_name": "L$\\beta_{17}$"},
    "L\u03B2\u2081": {"low_level": "L2", "high_level": "M4", "selected_state": False, "readable_name": "Lbeta1", "latex_name": "L$\\beta_{1}$"},
    "L\u03B3\u2085": {"low_level": "L2", "high_level": "N1", "selected_state": False, "readable_name": "Lgamma5", "latex_name": "L$\\gamma_{5}$"},
    "L\u03B3\u2081": {"low_level": "L2", "high_level": "N4", "selected_state": False, "readable_name": "Lgamma1", "latex_name": "L$\\gamma_{1}$"},
    "L\u03B3\u2088": {"low_level": "L2", "high_level": "O1", "selected_state": False, "readable_name": "Lgamma8", "latex_name": "L$\\gamma_{8}$"},
    "L\u03B3\u2086": {"low_level": "L2", "high_level": "O4", "selected_state": False, "readable_name": "Lgamma6", "latex_name": "L$\\gamma_{6}$"},
    "Ll": {"low_level": "L3", "high_level": "M1", "selected_state": False, "readable_name": "Ll", "latex_name": "L$l$"},
    "Lt": {"low_level": "L3", "high_level": "M2", "selected_state": False, "readable_name": "Lt", "latex_name": "L$t$"},
    "Ls": {"low_level": "L3", "high_level": "M3", "selected_state": False, "readable_name": "Ls", "latex_name": "L$s$"},
    "L\u03B1\u2082": {"low_level": "L3", "high_level": "M4", "selected_state": False, "readable_name": "Lalpha2", "latex_name": "L$\\alpha_{2}$"},
    "L\u03B1\u2081": {"low_level": "L3", "high_level": "M5", "selected_state": False, "readable_name": "Lalpha1", "latex_name": "L$\\alpha_{1}$"},
    "L\u03B2\u2086": {"low_level": "L3", "high_level": "N1", "selected_state": False, "readable_name": "Lbeta6", "latex_name": "L$\\beta_{6}$"},
    "L\u03B2\u2081\u2085": {"low_level": "L3", "high_level": "N4", "selected_state": False, "readable_name": "Lbeta15", "latex_name": "L$\\beta_{15}$"},
    "L\u03B2\u2082": {"low_level": "L3", "high_level": "N5", "selected_state": False, "readable_name": "Lbeta2", "latex_name": "L$\\beta_{2}$"},
    "Lu'": {"low_level": "L3", "high_level": "N6", "selected_state": False, "readable_name": "Lu'", "latex_name": "L$\\mu'$"},
    "Lu": {"low_level": "L3", "high_level": "N7", "selected_state": False, "readable_name": "Lu", "latex_name": "L$\\mu$"},
    "L\u03B2\u2087": {"low_level": "L3", "high_level": "O1", "selected_state": False, "readable_name": "Lbeta7", "latex_name": "L$\\beta_{7}$"},
    "M\u03B3\u2081": {"low_level": "M3", "high_level": "N5", "selected_state": False, "readable_name": "Mgamma1", "latex_name": "M$\\gamma_{1}$"},
    "M\u03B2": {"low_level": "M4", "high_level": "N6", "selected_state": False, "readable_name": "Mbeta", "latex_name": "M$\\beta$"},
    "M\u03B1\u2082": {"low_level": "M5", "high_level": "N6", "selected_state": False, "readable_name": "Malpha2", "latex_name": "M$\\alpha_{2}$"},
    "M\u03B1\u2081": {"low_level": "M5", "high_level": "N7", "selected_state": False, "readable_name": "Malpha1", "latex_name": "L$\\alpha_{1}$"}}
"""
Radiative transition dictionary. This is used to list, select and control which transitions are to be simulated
"""


# Auger transition dictionary. This is used to list, select and control which transitions are to be simulated
the_aug_dictionary: Dict[str, Dict[str, str | bool]] = {
    "KL1L1": {"low_level": "K1", "high_level": "L1", "auger_level": "L1", "selected_state": False, "readable_name": "KL1L1", "latex_name": "KL$_1$L$_1$"},
    "KL1L2": {"low_level": "K1", "high_level": "L1", "auger_level": "L2", "selected_state": False, "readable_name": "KL1L2", "latex_name": "KL$_1$L$_2$"},
    "KL1L3": {"low_level": "K1", "high_level": "L1", "auger_level": "L3", "selected_state": False, "readable_name": "KL1L3", "latex_name": "KL$_1$L$_3$"},
    "KL1M1": {"low_level": "K1", "high_level": "L1", "auger_level": "M1", "selected_state": False, "readable_name": "KL1M1", "latex_name": "KL$_1$M$_1$"},
    "KL1M2": {"low_level": "K1", "high_level": "L1", "auger_level": "M2", "selected_state": False, "readable_name": "KL1M2", "latex_name": "KL$_1$M$_2$"},
    "KL1M3": {"low_level": "K1", "high_level": "L1", "auger_level": "M3", "selected_state": False, "readable_name": "KL1M3", "latex_name": "KL$_1$M$_3$"},
    "KL1M4": {"low_level": "K1", "high_level": "L1", "auger_level": "M4", "selected_state": False, "readable_name": "KL1M4", "latex_name": "KL$_1$M$_4$"},
    "KL1M5": {"low_level": "K1", "high_level": "L1", "auger_level": "M5", "selected_state": False, "readable_name": "KL1M5", "latex_name": "KL$_1$M$_5$"},
    "KL1N1": {"low_level": "K1", "high_level": "L1", "auger_level": "N1", "selected_state": False, "readable_name": "KL1N1", "latex_name": "KL$_1$N$_1$"},
    "KL2L2": {"low_level": "K1", "high_level": "L2", "auger_level": "L2", "selected_state": False, "readable_name": "KL2L2", "latex_name": "KL$_2$L$_2$"},
    "KL2L3": {"low_level": "K1", "high_level": "L2", "auger_level": "L3", "selected_state": False, "readable_name": "KL2L3", "latex_name": "KL$_2$L$_3$"},
    "KL2M1": {"low_level": "K1", "high_level": "L2", "auger_level": "M1", "selected_state": False, "readable_name": "KL2M1", "latex_name": "KL$_2$M$_1$"},
    "KL2M2": {"low_level": "K1", "high_level": "L2", "auger_level": "M2", "selected_state": False, "readable_name": "KL2M2", "latex_name": "KL$_2$M$_2$"},
    "KL2M3": {"low_level": "K1", "high_level": "L2", "auger_level": "M3", "selected_state": False, "readable_name": "KL2M3", "latex_name": "KL$_2$M$_3$"},
    "KL2M4": {"low_level": "K1", "high_level": "L2", "auger_level": "M4", "selected_state": False, "readable_name": "KL2M4", "latex_name": "KL$_2$M$_4$"},
    "KL2M5": {"low_level": "K1", "high_level": "L2", "auger_level": "M5", "selected_state": False, "readable_name": "KL2M5", "latex_name": "KL$_2$M$_5$"},
    "KL2N1": {"low_level": "K1", "high_level": "L2", "auger_level": "N1", "selected_state": False, "readable_name": "KL2N1", "latex_name": "KL$_2$N$_1$"},
    "KL3L3": {"low_level": "K1", "high_level": "L3", "auger_level": "L3", "selected_state": False, "readable_name": "KL3L3", "latex_name": "KL$_3$L$_3$"},
    "KL3M1": {"low_level": "K1", "high_level": "L3", "auger_level": "M1", "selected_state": False, "readable_name": "KL3M1", "latex_name": "KL$_3$M$_1$"},
    "KL3M2": {"low_level": "K1", "high_level": "L3", "auger_level": "M2", "selected_state": False, "readable_name": "KL3M2", "latex_name": "KL$_3$M$_2$"},
    "KL3M3": {"low_level": "K1", "high_level": "L3", "auger_level": "M3", "selected_state": False, "readable_name": "KL3M3", "latex_name": "KL$_3$M$_3$"},
    "KL3M4": {"low_level": "K1", "high_level": "L3", "auger_level": "M4", "selected_state": False, "readable_name": "KL3M4", "latex_name": "KL$_3$M$_4$"},
    "KL3M5": {"low_level": "K1", "high_level": "L3", "auger_level": "M5", "selected_state": False, "readable_name": "KL3M5", "latex_name": "KL$_3$M$_5$"},
    "KL3N1": {"low_level": "K1", "high_level": "L3", "auger_level": "N1", "selected_state": False, "readable_name": "KL3N1", "latex_name": "KL$_3$N$_1$"},
    "KM1M1": {"low_level": "K1", "high_level": "M1", "auger_level": "M1", "selected_state": False, "readable_name": "KM1M1", "latex_name": "KM$_1$M$_1$"},
    "KM1M2": {"low_level": "K1", "high_level": "M1", "auger_level": "M2", "selected_state": False, "readable_name": "KM1M2", "latex_name": "KM$_1$M$_2$"},
    "KM1M3": {"low_level": "K1", "high_level": "M1", "auger_level": "M3", "selected_state": False, "readable_name": "KM1M3", "latex_name": "KM$_1$M$_3$"},
    "KM1M4": {"low_level": "K1", "high_level": "M1", "auger_level": "M4", "selected_state": False, "readable_name": "KM1M4", "latex_name": "KM$_1$M$_4$"},
    "KM1M5": {"low_level": "K1", "high_level": "M1", "auger_level": "M5", "selected_state": False, "readable_name": "KM1M5", "latex_name": "KM$_1$M$_5$"},
    "KM1N1": {"low_level": "K1", "high_level": "M1", "auger_level": "N1", "selected_state": False, "readable_name": "KM1N1", "latex_name": "KM$_1$N$_1$"},
    "KM2M2": {"low_level": "K1", "high_level": "M2", "auger_level": "M2", "selected_state": False, "readable_name": "KM2M2", "latex_name": "KM$_2$M$_2$"},
    "KM2M3": {"low_level": "K1", "high_level": "M2", "auger_level": "M3", "selected_state": False, "readable_name": "KM2M3", "latex_name": "KM$_2$M$_3$"},
    "KM2M4": {"low_level": "K1", "high_level": "M2", "auger_level": "M4", "selected_state": False, "readable_name": "KM2M4", "latex_name": "KM$_2$M$_4$"},
    "KM2M5": {"low_level": "K1", "high_level": "M2", "auger_level": "M5", "selected_state": False, "readable_name": "KM2M5", "latex_name": "KM$_2$M$_5$"},
    "KM2N1": {"low_level": "K1", "high_level": "M2", "auger_level": "N1", "selected_state": False, "readable_name": "KM2N1", "latex_name": "KM$_2$N$_1$"},
    "KM3M3": {"low_level": "K1", "high_level": "M3", "auger_level": "M3", "selected_state": False, "readable_name": "KM3M3", "latex_name": "KM$_3$M$_3$"},
    "KM3M4": {"low_level": "K1", "high_level": "M3", "auger_level": "M4", "selected_state": False, "readable_name": "KM3M4", "latex_name": "KM$_3$M$_4$"},
    "KM3M5": {"low_level": "K1", "high_level": "M3", "auger_level": "M5", "selected_state": False, "readable_name": "KM3M5", "latex_name": "KM$_3$M$_5$"},
    "KM3N1": {"low_level": "K1", "high_level": "M3", "auger_level": "N1", "selected_state": False, "readable_name": "KM3N1", "latex_name": "KM$_3$N$_1$"},
    "KM4M4": {"low_level": "K1", "high_level": "M4", "auger_level": "M4", "selected_state": False, "readable_name": "KM4M4", "latex_name": "KM$_4$M$_4$"},
    "KM4M5": {"low_level": "K1", "high_level": "M4", "auger_level": "M5", "selected_state": False, "readable_name": "KM4M5", "latex_name": "KM$_4$M$_5$"},
    "KM4N1": {"low_level": "K1", "high_level": "M4", "auger_level": "N1", "selected_state": False, "readable_name": "KM4N1", "latex_name": "KM$_4$N$_1$"},
    "KM5M5": {"low_level": "K1", "high_level": "M5", "auger_level": "M5", "selected_state": False, "readable_name": "KM5M5", "latex_name": "KM$_5$M$_5$"},
    "KM5N1": {"low_level": "K1", "high_level": "M5", "auger_level": "N1", "selected_state": False, "readable_name": "KM5N1", "latex_name": "KM$_5$N$_1$"},
    "KN1N1": {"low_level": "K1", "high_level": "N1", "auger_level": "N1", "selected_state": False, "readable_name": "KN1N1", "latex_name": "KN$_1$N$_1$"},

    "L1L2L2": {"low_level": "L1", "high_level": "L2", "auger_level": "L2", "selected_state": False, "readable_name": "L1L2L2", "latex_name": "L$_1$L$_2$L$_2$"},
    "L1L2L3": {"low_level": "L1", "high_level": "L2", "auger_level": "L3", "selected_state": False, "readable_name": "L1L2L3", "latex_name": "L$_1$L$_2$L$_3$"},
    "L1L2M1": {"low_level": "L1", "high_level": "L2", "auger_level": "M1", "selected_state": False, "readable_name": "L1L2M1", "latex_name": "L$_1$L$_2$M$_1$"},
    "L1L2M2": {"low_level": "L1", "high_level": "L2", "auger_level": "M2", "selected_state": False, "readable_name": "L1L2M2", "latex_name": "L$_1$L$_2$M$_2$"},
    "L1L2M3": {"low_level": "L1", "high_level": "L2", "auger_level": "M3", "selected_state": False, "readable_name": "L1L2M3", "latex_name": "L$_1$L$_2$M$_3$"},
    "L1L2M4": {"low_level": "L1", "high_level": "L2", "auger_level": "M4", "selected_state": False, "readable_name": "L1L2M4", "latex_name": "L$_1$L$_2$M$_4$"},
    "L1L2M5": {"low_level": "L1", "high_level": "L2", "auger_level": "M5", "selected_state": False, "readable_name": "L1L2M5", "latex_name": "L$_1$L$_2$M$_5$"},
    "L1L2N1": {"low_level": "L1", "high_level": "L2", "auger_level": "N1", "selected_state": False, "readable_name": "L1L2N1", "latex_name": "L$_1$L$_2$N$_1$"},
    "L1L3L3": {"low_level": "L1", "high_level": "L3", "auger_level": "L3", "selected_state": False, "readable_name": "L1L3L3", "latex_name": "L$_1$L$_3$L$_3$"},
    "L1L3M1": {"low_level": "L1", "high_level": "L3", "auger_level": "M1", "selected_state": False, "readable_name": "L1L3M1", "latex_name": "L$_1$L$_3$M$_1$"},
    "L1L3M2": {"low_level": "L1", "high_level": "L3", "auger_level": "M2", "selected_state": False, "readable_name": "L1L3M2", "latex_name": "L$_1$L$_3$M$_2$"},
    "L1L3M3": {"low_level": "L1", "high_level": "L3", "auger_level": "M3", "selected_state": False, "readable_name": "L1L3M3", "latex_name": "L$_1$L$_3$M$_3$"},
    "L1L3M4": {"low_level": "L1", "high_level": "L3", "auger_level": "M4", "selected_state": False, "readable_name": "L1L3M4", "latex_name": "L$_1$L$_3$M$_4$"},
    "L1L3M5": {"low_level": "L1", "high_level": "L3", "auger_level": "M5", "selected_state": False, "readable_name": "L1L3M5", "latex_name": "L$_1$L$_3$M$_5$"},
    "L1L3N1": {"low_level": "L1", "high_level": "L3", "auger_level": "N1", "selected_state": False, "readable_name": "L1L3N1", "latex_name": "L$_1$L$_3$N$_1$"},
    "L1M1M1": {"low_level": "L1", "high_level": "M1", "auger_level": "M1", "selected_state": False, "readable_name": "L1M1M1", "latex_name": "L$_1$M$_1$M$_1$"},
    "L1M1M2": {"low_level": "L1", "high_level": "M1", "auger_level": "M2", "selected_state": False, "readable_name": "L1M1M2", "latex_name": "L$_1$M$_1$M$_2$"},
    "L1M1M3": {"low_level": "L1", "high_level": "M1", "auger_level": "M3", "selected_state": False, "readable_name": "L1M1M3", "latex_name": "L$_1$M$_1$M$_3$"},
    "L1M1M4": {"low_level": "L1", "high_level": "M1", "auger_level": "M4", "selected_state": False, "readable_name": "L1M1M4", "latex_name": "L$_1$M$_1$M$_4$"},
    "L1M1M5": {"low_level": "L1", "high_level": "M1", "auger_level": "M5", "selected_state": False, "readable_name": "L1M1M5", "latex_name": "L$_1$M$_1$M$_5$"},
    "L1M1N1": {"low_level": "L1", "high_level": "M1", "auger_level": "N1", "selected_state": False, "readable_name": "L1M1N1", "latex_name": "L$_1$M$_1$N$_1$"},
    "L1M2M2": {"low_level": "L1", "high_level": "M2", "auger_level": "M2", "selected_state": False, "readable_name": "L1M2M2", "latex_name": "L$_1$M$_2$M$_2$"},
    "L1M2M3": {"low_level": "L1", "high_level": "M2", "auger_level": "M3", "selected_state": False, "readable_name": "L1M2M3", "latex_name": "L$_1$M$_2$M$_3$"},
    "L1M2M4": {"low_level": "L1", "high_level": "M2", "auger_level": "M4", "selected_state": False, "readable_name": "L1M2M4", "latex_name": "L$_1$M$_2$M$_4$"},
    "L1M2M5": {"low_level": "L1", "high_level": "M2", "auger_level": "M5", "selected_state": False, "readable_name": "L1M2M5", "latex_name": "L$_1$M$_2$M$_5$"},
    "L1M2N1": {"low_level": "L1", "high_level": "M2", "auger_level": "N1", "selected_state": False, "readable_name": "L1M2N1", "latex_name": "L$_1$M$_2$N$_1$"},
    "L1M3M3": {"low_level": "L1", "high_level": "M3", "auger_level": "M3", "selected_state": False, "readable_name": "L1M3M3", "latex_name": "L$_1$M$_3$M$_3$"},
    "L1M3M4": {"low_level": "L1", "high_level": "M3", "auger_level": "M4", "selected_state": False, "readable_name": "L1M3M4", "latex_name": "L$_1$M$_3$M$_4$"},
    "L1M3M5": {"low_level": "L1", "high_level": "M3", "auger_level": "M5", "selected_state": False, "readable_name": "L1M3M5", "latex_name": "L$_1$M$_3$M$_5$"},
    "L1M3N1": {"low_level": "L1", "high_level": "M3", "auger_level": "N1", "selected_state": False, "readable_name": "L1M3N1", "latex_name": "L$_1$M$_3$N$_1$"},
    "L1M4M4": {"low_level": "L1", "high_level": "M4", "auger_level": "M4", "selected_state": False, "readable_name": "L1M4M4", "latex_name": "L$_1$M$_4$M$_4$"},
    "L1M4M5": {"low_level": "L1", "high_level": "M4", "auger_level": "M5", "selected_state": False, "readable_name": "L1M4M5", "latex_name": "L$_1$M$_4$M$_5$"},
    "L1M4N1": {"low_level": "L1", "high_level": "M4", "auger_level": "N1", "selected_state": False, "readable_name": "L1M4N1", "latex_name": "L$_1$M$_4$N$_1$"},
    "L1M5M5": {"low_level": "L1", "high_level": "M5", "auger_level": "M5", "selected_state": False, "readable_name": "L1M5M5", "latex_name": "L$_1$M$_5$M$_5$"},
    "L1M5N1": {"low_level": "L1", "high_level": "M5", "auger_level": "N1", "selected_state": False, "readable_name": "L1M5N1", "latex_name": "L$_1$M$_5$N$_1$"},
    "L1N1N1": {"low_level": "L1", "high_level": "N1", "auger_level": "N1", "selected_state": False, "readable_name": "L1N1N1", "latex_name": "L$_1$N$_1$N$_1$"},

    "L2L3L3": {"low_level": "L2", "high_level": "L3", "auger_level": "L3", "selected_state": False, "readable_name": "L2L3L3", "latex_name": "L$_2$L$_3$L$_3$"},
    "L2L3M1": {"low_level": "L2", "high_level": "L3", "auger_level": "M1", "selected_state": False, "readable_name": "L2L3M1", "latex_name": "L$_2$L$_3$M$_1$"},
    "L2L3M2": {"low_level": "L2", "high_level": "L3", "auger_level": "M2", "selected_state": False, "readable_name": "L2L3M2", "latex_name": "L$_2$L$_3$M$_2$"},
    "L2L3M3": {"low_level": "L2", "high_level": "L3", "auger_level": "M3", "selected_state": False, "readable_name": "L2L3M3", "latex_name": "L$_2$L$_3$M$_3$"},
    "L2L3M4": {"low_level": "L2", "high_level": "L3", "auger_level": "M4", "selected_state": False, "readable_name": "L2L3M4", "latex_name": "L$_2$L$_3$M$_4$"},
    "L2L3M5": {"low_level": "L2", "high_level": "L3", "auger_level": "M5", "selected_state": False, "readable_name": "L2L3M5", "latex_name": "L$_2$L$_3$M$_5$"},
    "L2L3N1": {"low_level": "L2", "high_level": "L3", "auger_level": "N1", "selected_state": False, "readable_name": "L2L3N1", "latex_name": "L$_2$L$_3$N$_1$"},
    "L2M1M1": {"low_level": "L2", "high_level": "M1", "auger_level": "M1", "selected_state": False, "readable_name": "L2M1M1", "latex_name": "L$_2$M$_1$M$_1$"},
    "L2M1M2": {"low_level": "L2", "high_level": "M1", "auger_level": "M2", "selected_state": False, "readable_name": "L2M1M2", "latex_name": "L$_2$M$_1$M$_2$"},
    "L2M1M3": {"low_level": "L2", "high_level": "M1", "auger_level": "M3", "selected_state": False, "readable_name": "L2M1M3", "latex_name": "L$_2$M$_1$M$_3$"},
    "L2M1M4": {"low_level": "L2", "high_level": "M1", "auger_level": "M4", "selected_state": False, "readable_name": "L2M1M4", "latex_name": "L$_2$M$_1$M$_4$"},
    "L2M1M5": {"low_level": "L2", "high_level": "M1", "auger_level": "M5", "selected_state": False, "readable_name": "L2M1M5", "latex_name": "L$_2$M$_1$M$_5$"},
    "L2M1N1": {"low_level": "L2", "high_level": "M1", "auger_level": "N1", "selected_state": False, "readable_name": "L2M1N1", "latex_name": "L$_2$M$_1$N$_1$"},
    "L2M2M2": {"low_level": "L2", "high_level": "M2", "auger_level": "M2", "selected_state": False, "readable_name": "L2M2M2", "latex_name": "L$_2$M$_2$M$_2$"},
    "L2M2M3": {"low_level": "L2", "high_level": "M2", "auger_level": "M3", "selected_state": False, "readable_name": "L2M2M3", "latex_name": "L$_2$M$_2$M$_3$"},
    "L2M2M4": {"low_level": "L2", "high_level": "M2", "auger_level": "M4", "selected_state": False, "readable_name": "L2M2M4", "latex_name": "L$_2$M$_2$M$_4$"},
    "L2M2M5": {"low_level": "L2", "high_level": "M2", "auger_level": "M5", "selected_state": False, "readable_name": "L2M2M5", "latex_name": "L$_2$M$_2$M$_5$"},
    "L2M2N1": {"low_level": "L2", "high_level": "M2", "auger_level": "N1", "selected_state": False, "readable_name": "L2M2N1", "latex_name": "L$_2$M$_2$N$_1$"},
    "L2M3M3": {"low_level": "L2", "high_level": "M3", "auger_level": "M3", "selected_state": False, "readable_name": "L2M3M3", "latex_name": "L$_2$M$_3$M$_3$"},
    "L2M3M4": {"low_level": "L2", "high_level": "M3", "auger_level": "M4", "selected_state": False, "readable_name": "L2M3M4", "latex_name": "L$_2$M$_3$M$_4$"},
    "L2M3M5": {"low_level": "L2", "high_level": "M3", "auger_level": "M5", "selected_state": False, "readable_name": "L2M3M5", "latex_name": "L$_2$M$_3$M$_5$"},
    "L2M3N1": {"low_level": "L2", "high_level": "M3", "auger_level": "N1", "selected_state": False, "readable_name": "L2M3N1", "latex_name": "L$_2$M$_3$N$_1$"},
    "L2M4M4": {"low_level": "L2", "high_level": "M4", "auger_level": "M4", "selected_state": False, "readable_name": "L2M4M4", "latex_name": "L$_2$M$_4$M$_4$"},
    "L2M4M5": {"low_level": "L2", "high_level": "M4", "auger_level": "M5", "selected_state": False, "readable_name": "L2M4M5", "latex_name": "L$_2$M$_4$M$_5$"},
    "L2M4N1": {"low_level": "L2", "high_level": "M4", "auger_level": "N1", "selected_state": False, "readable_name": "L2M4N1", "latex_name": "L$_2$M$_4$N$_1$"},
    "L2M5M5": {"low_level": "L2", "high_level": "M5", "auger_level": "M5", "selected_state": False, "readable_name": "L2M5M5", "latex_name": "L$_2$M$_5$M$_5$"},
    "L2M5N1": {"low_level": "L2", "high_level": "M5", "auger_level": "N1", "selected_state": False, "readable_name": "L2M5N1", "latex_name": "L$_2$M$_5$N$_1$"},
    "L2N1N1": {"low_level": "L2", "high_level": "N1", "auger_level": "N1", "selected_state": False, "readable_name": "L2N1N1", "latex_name": "L$_2$N$_1$N$_1$"},

    "L3M1M1": {"low_level": "L3", "high_level": "M1", "auger_level": "M1", "selected_state": False, "readable_name": "L3M1M1", "latex_name": "L$_3$M$_1$M$_1$"},
    "L3M1M2": {"low_level": "L3", "high_level": "M1", "auger_level": "M2", "selected_state": False, "readable_name": "L3M1M2", "latex_name": "L$_3$M$_1$M$_2$"},
    "L3M1M3": {"low_level": "L3", "high_level": "M1", "auger_level": "M3", "selected_state": False, "readable_name": "L3M1M3", "latex_name": "L$_3$M$_1$M$_3$"},
    "L3M1M4": {"low_level": "L3", "high_level": "M1", "auger_level": "M4", "selected_state": False, "readable_name": "L3M1M4", "latex_name": "L$_3$M$_1$M$_4$"},
    "L3M1M5": {"low_level": "L3", "high_level": "M1", "auger_level": "M5", "selected_state": False, "readable_name": "L3M1M5", "latex_name": "L$_3$M$_1$M$_5$"},
    "L3M1N1": {"low_level": "L3", "high_level": "M1", "auger_level": "N1", "selected_state": False, "readable_name": "L3M1N1", "latex_name": "L$_3$M$_1$N$_1$"},
    "L3M2M2": {"low_level": "L3", "high_level": "M2", "auger_level": "M2", "selected_state": False, "readable_name": "L3M2M2", "latex_name": "L$_3$M$_2$M$_2$"},
    "L3M2M3": {"low_level": "L3", "high_level": "M2", "auger_level": "M3", "selected_state": False, "readable_name": "L3M2M3", "latex_name": "L$_3$M$_2$M$_3$"},
    "L3M2M4": {"low_level": "L3", "high_level": "M2", "auger_level": "M4", "selected_state": False, "readable_name": "L3M2M4", "latex_name": "L$_3$M$_2$M$_4$"},
    "L3M2M5": {"low_level": "L3", "high_level": "M2", "auger_level": "M5", "selected_state": False, "readable_name": "L3M2M5", "latex_name": "L$_3$M$_2$M$_5$"},
    "L3M2N1": {"low_level": "L3", "high_level": "M2", "auger_level": "N1", "selected_state": False, "readable_name": "L3M2N1", "latex_name": "L$_3$M$_2$N$_1$"},
    "L3M3M3": {"low_level": "L3", "high_level": "M3", "auger_level": "M3", "selected_state": False, "readable_name": "L3M3M3", "latex_name": "L$_3$M$_3$M$_3$"},
    "L3M3M4": {"low_level": "L3", "high_level": "M3", "auger_level": "M4", "selected_state": False, "readable_name": "L3M3M4", "latex_name": "L$_3$M$_3$M$_4$"},
    "L3M3M5": {"low_level": "L3", "high_level": "M3", "auger_level": "M5", "selected_state": False, "readable_name": "L3M3M5", "latex_name": "L$_3$M$_3$M$_5$"},
    "L3M3N1": {"low_level": "L3", "high_level": "M3", "auger_level": "N1", "selected_state": False, "readable_name": "L3M3N1", "latex_name": "L$_3$M$_3$N$_1$"},
    "L3M4M4": {"low_level": "L3", "high_level": "M4", "auger_level": "M4", "selected_state": False, "readable_name": "L3M4M4", "latex_name": "L$_3$M$_4$M$_4$"},
    "L3M4M5": {"low_level": "L3", "high_level": "M4", "auger_level": "M5", "selected_state": False, "readable_name": "L3M4M5", "latex_name": "L$_3$M$_4$M$_5$"},
    "L3M4N1": {"low_level": "L3", "high_level": "M4", "auger_level": "N1", "selected_state": False, "readable_name": "L3M4N1", "latex_name": "L$_3$M$_4$N$_1$"},
    "L3M5M5": {"low_level": "L3", "high_level": "M5", "auger_level": "M5", "selected_state": False, "readable_name": "L3M5M5", "latex_name": "L$_3$M$_5$M$_5$"},
    "L3M5N1": {"low_level": "L3", "high_level": "M5", "auger_level": "N1", "selected_state": False, "readable_name": "L3M5N1", "latex_name": "L$_3$M$_5$N$_1$"},
    "L3N1N1": {"low_level": "L3", "high_level": "N1", "auger_level": "N1", "selected_state": False, "readable_name": "L3N1N1", "latex_name": "L$_3$N$_1$N$_1$"},

    "M1M2M2": {"low_level": "M1", "high_level": "M2", "auger_level": "M2", "selected_state": False, "readable_name": "M1M2M2", "latex_name": "M$_1$M$_2$M$_2$"},
    "M1M2M3": {"low_level": "M1", "high_level": "M2", "auger_level": "M3", "selected_state": False, "readable_name": "M1M2M3", "latex_name": "M$_1$M$_2$M$_3$"},
    "M1M2M4": {"low_level": "M1", "high_level": "M2", "auger_level": "M4", "selected_state": False, "readable_name": "M1M2M4", "latex_name": "M$_1$M$_2$M$_4$"},
    "M1M2M5": {"low_level": "M1", "high_level": "M2", "auger_level": "M5", "selected_state": False, "readable_name": "M1M2M5", "latex_name": "M$_1$M$_2$M$_5$"},
    "M1M2N1": {"low_level": "M1", "high_level": "M2", "auger_level": "N1", "selected_state": False, "readable_name": "M1M2N1", "latex_name": "M$_1$M$_2$N$_1$"},
    "M1M3M3": {"low_level": "M1", "high_level": "M3", "auger_level": "M3", "selected_state": False, "readable_name": "M1M3M3", "latex_name": "M$_1$M$_3$M$_3$"},
    "M1M3M4": {"low_level": "M1", "high_level": "N3", "auger_level": "M4", "selected_state": False, "readable_name": "M1M3M4", "latex_name": "M$_1$M$_3$M$_4$"},
    "M1M3M5": {"low_level": "M1", "high_level": "N3", "auger_level": "M5", "selected_state": False, "readable_name": "M1M3M5", "latex_name": "M$_1$M$_3$M$_5$"},
    "M1M3N1": {"low_level": "M1", "high_level": "M3", "auger_level": "N1", "selected_state": False, "readable_name": "M1M3N1", "latex_name": "M$_1$M$_3$N$_1$"},
    "M1M4M4": {"low_level": "M1", "high_level": "M4", "auger_level": "M4", "selected_state": False, "readable_name": "M1M4M4", "latex_name": "M$_1$M$_4$M$_4$"},
    "M1M4M5": {"low_level": "M1", "high_level": "M4", "auger_level": "M5", "selected_state": False, "readable_name": "M1M4M5", "latex_name": "M$_1$M$_4$M$_5$"},
    "M1M4N1": {"low_level": "M1", "high_level": "M4", "auger_level": "N1", "selected_state": False, "readable_name": "M1M4N1", "latex_name": "M$_1$M$_4$N$_1$"},
    "M1M5M5": {"low_level": "M1", "high_level": "M5", "auger_level": "M5", "selected_state": False, "readable_name": "M1M5M5", "latex_name": "M$_1$M$_5$M$_5$"},
    "M1M5N1": {"low_level": "M1", "high_level": "M5", "auger_level": "N1", "selected_state": False, "readable_name": "M1M5N1", "latex_name": "M$_1$M$_5$N$_1$"},
    "M1N1N1": {"low_level": "M1", "high_level": "N1", "auger_level": "N1", "selected_state": False, "readable_name": "M1N1N1", "latex_name": "M$_1$N$_1$N$_1$"},

    "M2M3M3": {"low_level": "M2", "high_level": "M3", "auger_level": "M3", "selected_state": False, "readable_name": "M2M3M3", "latex_name": "M$_2$M$_3$M$_3$"},
    "M2M3M4": {"low_level": "M2", "high_level": "M3", "auger_level": "M4", "selected_state": False, "readable_name": "M2M3M4", "latex_name": "M$_2$M$_3$M$_4$"},
    "M2M3M5": {"low_level": "M2", "high_level": "M3", "auger_level": "M5", "selected_state": False, "readable_name": "M2M3M5", "latex_name": "M$_2$M$_3$M$_5$"},
    "M2M3N1": {"low_level": "M2", "high_level": "M3", "auger_level": "N1", "selected_state": False, "readable_name": "M2M3N1", "latex_name": "M$_2$M$_3$N$_1$"},
    "M2M4M4": {"low_level": "M2", "high_level": "M4", "auger_level": "M4", "selected_state": False, "readable_name": "M2M4M4", "latex_name": "M$_2$M$_4$M$_4$"},
    "M2M4M5": {"low_level": "M2", "high_level": "M4", "auger_level": "M5", "selected_state": False, "readable_name": "M2M4M5", "latex_name": "M$_2$M$_4$M$_5$"},
    "M2M4N1": {"low_level": "M2", "high_level": "M4", "auger_level": "N1", "selected_state": False, "readable_name": "M2M4N1", "latex_name": "M$_2$M$_4$N$_1$"},
    "M2M5M5": {"low_level": "M2", "high_level": "M5", "auger_level": "M5", "selected_state": False, "readable_name": "M2M5M5", "latex_name": "M$_2$M$_5$M$_5$"},
    "M2M5N1": {"low_level": "M2", "high_level": "M5", "auger_level": "N1", "selected_state": False, "readable_name": "M2M5N1", "latex_name": "M$_2$M$_5$N$_1$"},
    "M2N1N1": {"low_level": "M2", "high_level": "N1", "auger_level": "N1", "selected_state": False, "readable_name": "M2N1N1", "latex_name": "M$_2$N$_1$N$_1$"},

    "M3M4M4": {"low_level": "M3", "high_level": "M4", "auger_level": "M4", "selected_state": False, "readable_name": "M3M4M4", "latex_name": "M$_3$M$_4$M$_4$"},
    "M3M4M5": {"low_level": "M3", "high_level": "M4", "auger_level": "M5", "selected_state": False, "readable_name": "M3M4M5", "latex_name": "M$_3$M$_4$M$_5$"},
    "M3M4N1": {"low_level": "M3", "high_level": "M4", "auger_level": "N1", "selected_state": False, "readable_name": "M3M4N1", "latex_name": "M$_3$M$_4$N$_1$"},
    "M3M5M5": {"low_level": "M3", "high_level": "M5", "auger_level": "M5", "selected_state": False, "readable_name": "M3M5M5", "latex_name": "M$_3$M$_5$M$_5$"},
    "M3M5N1": {"low_level": "M3", "high_level": "M5", "auger_level": "N1", "selected_state": False, "readable_name": "M3M5N1", "latex_name": "M$_3$M$_5$N$_1$"},
    "M3N1N1": {"low_level": "M3", "high_level": "N1", "auger_level": "N1", "selected_state": False, "readable_name": "M3N1N1", "latex_name": "M$_3$N$_1$N$_1$"},

    "M4M5M5": {"low_level": "M4", "high_level": "M5", "auger_level": "M5", "selected_state": False, "readable_name": "M4M5M5", "latex_name": "M$_4$M$_5$M$_5$"},
    "M4M5N1": {"low_level": "M4", "high_level": "M5", "auger_level": "N1", "selected_state": False, "readable_name": "M4M5N1", "latex_name": "M$_4$M$_5$N$_1$"},
    "M4N1N1": {"low_level": "M4", "high_level": "N1", "auger_level": "N1", "selected_state": False, "readable_name": "M4N1N1", "latex_name": "M$_4$N$_1$N$_1$"},

    "M5N1N1": {"low_level": "M5", "high_level": "N1", "auger_level": "N1", "selected_state": False, "readable_name": "M5N1N1", "latex_name": "M$_5$N$_1$N$_1$"}}
"""
Auger transition dictionary. This is used to list, select and control which transitions are to be simulated
"""

#Values to initialize the periodic table (First window)
per_table: List[List[float | str]] = [[1, 1.0079, ' Hydrogen ', ' H ', 0.09, 'grey', 1, 1, ' 1s1 ', 13.5984],
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
             [118, 277, ' Ununoctium ', ' Uuo ', '?', 'grey', 7, 18, ' ', '?'] ]
"""
Values to initialize the periodic table (First window)
"""

# endregion

# --------------------------------------------- #
#                                               #
#             PACKAGE USER OVERRIDES            #
#                                               #
# --------------------------------------------- #
# region

userLine: type[Line] | None = None

# endregion