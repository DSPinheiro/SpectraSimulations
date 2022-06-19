#Chi^2 of the current fit
chi_sqrd = 0

#Mix Values of the various charge states used in the simulation
PCS_radMixValues = []
NCS_radMixValues = []
PCS_augMixValues = []
NCS_augMixValues = []

#Final y of the simulated spectrum (Rad or Aug, no satellite) for each transition
yfinal = []
#Total y of the simulated spectrum summed over all simulated lines
ytot = []
#Final y of the simulated satellite lines for each Rad transition
yfinals = []

#File names of the radiative transitions for each charge state found
radiative_files = []
#File names of the auger transitions for each charge state found
auger_files = []

#Raw data read from the radiative transitions file to be simulated
lineradrates = []
#Raw data read from the satellite transitions file to be simulated
linesatellites = []
#Raw data read from the auger transitions file to be simulated
lineauger = []
#Raw data read from the shake wheights file to be simulated
shakeweights = []
#Variable to store the labels read from the shake weights file
label1 = []


#Raw data read from the radiative transitions files to be simulated, for each charge state split by positive and negative CS
lineradrates_PCS = []
lineradrates_NCS = []
#Order of the charge states read and stored in the previous variables
rad_PCS = []
rad_NCS = []

#Raw data read from the auger transitions files to be simulated, for each charge state split by positive and negative CS
lineaugrates_PCS = []
lineaugrates_NCS = []
#Order of the charge states read and stored in the previous variables
aug_PCS = []
aug_NCS = []

#Raw data read from the satellite transitions files to be simulated, for each charge state split by positive and negative CS
linesatellites_PCS = []
linesatellites_NCS = []
#Order of the charge states read and stored in the previous variables
sat_PCS = []
sat_NCS = []

#Flag to check if a file containing the ion population data is present
Ionpop_exists = False
#Raw data read from the ion population file
ionpopdata = []

#Correspondence between Siegbahn notation and relativistic orbitals
labeldict = {'K1': '1s', 'L1': '2s', 'L2': '2p*', 'L3': '2p', 'M1': '3s', 'M2': '3p*', 'M3': '3p', 'M4': '3d*',
             'M5': '3d', 'N1': '4s', 'N2': '4p*', 'N3': '4p', 'N4': '4d*', 'N5': '4d', 'N6': '4f*', 'N7': '4f',
             'O1': '5s', 'O2': '5p*', 'O3': '5p', 'O4': '5d*', 'O5': '5d', 'O6': '5f*', 'O7': '5f', 'O8': '5g*',
             'O9': '5g', 'P1': '6s'}


# Radiative transition dictionary. This is used to list, select and control which transitions are to be simulated
the_dictionary = {
    # for ionic transitions
    "KL\u2081": {"low_level": "K1", "high_level": "L1", "selected_state": False, "readable_name": "KL1"},
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
}


# Auger transition dictionary. This is used to list, select and control which transitions are to be simulated
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
}

#Values to initialize the periodic table (First window)
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
