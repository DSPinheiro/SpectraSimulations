import os, sys
from datetime import datetime
import re




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
    "M\u03B3\u2081": {"low_level": "M3", "high_level": "N5", "selected_state": False, "readable_name": "Mgamma1"}}


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

    "M5N1N1": {"low_level": "M5", "high_level": "N1", "auger_level": "N1", "selected_state": False, "readable_name": "M5N1N1"}}




output_dir = '../output/'

if len(sys.argv) <= 2:
    print("Expected at least 2 arguments:")
    print("Spectrum file to be restricted.")
    print("[Optional] Minimum transition energy.")
    print("[Optional] Maximum transition energy.")
    print("List of transitions to filter.")
    exit(-1)
else:
    input_spectra = sys.argv[1]
    
    min_energy = -1.0
    max_energy = -1.0
    
    try:
        min_energy = float(sys.argv[2])
        max_energy = float(sys.argv[3])
        if min_energy > max_energy:
            print("Warning, minimum energy is lower than maximum energy, swapping them...")
            tmp = min_energy
            min_energy = max_energy
            max_energy = tmp
        
        transitions = sys.argv[4:]
    except ValueError:
        transitions = sys.argv[2:]
    
    if min_energy == -1.0 and max_energy == -1.0:
        print("No energy values were detected in the input arguments, proceding with no energy restrictions...")
    else:
        print("Restricting transition energies: " + str(min_energy) + " <= E <= " + str(max_energy))
    
    allowed_transition_shells = []
    
    available_transitions = [the_dictionary[key]['readable_name'] for key in the_dictionary]
    available_transitions += [the_aug_dictionary[key]['readable_name'] for key in the_aug_dictionary]
    
    for transition in transitions:
        if transition not in available_transitions:
            print("Unexpected transition requested: " + transition)
            print("The currently available transitions are: ")
            print(available_transitions)
            exit(-2)
        else:
            transition_details = {}
            for key in the_dictionary:
                if the_dictionary[key]['readable_name'] == transition:
                    transition_details = the_dictionary[key]

            if transition_details == {}:
                for key in the_aug_dictionary:
                    if the_aug_dictionary[key]['readable_name'] == transition:
                        transition_details = the_aug_dictionary[key]
            
            allowed_transition_shells.append((transition_details['low_level'], transition_details['high_level']))
    
    print("\nAllowed shell combinations:")
    print(allowed_transition_shells)
    print()


def bufcount(filename):
    f = open(filename)                  
    lines = 0
    buf_size = 1024 * 1024
    read_f = f.read # loop optimization

    buf = read_f(buf_size)
    while buf:
        lines += buf.count('\n')
        buf = read_f(buf_size)
        print("Total transition count: " + str(lines), end='\r')

    return lines

#Total number of transitions to process
transition_num = bufcount(output_dir + "/" + input_spectra) - 3

print()


def filterTransition(shell1, shell2, energy):
    transition_allowed = False
    
    for shells in allowed_transition_shells:
        if shell1 in shells[0] or shells[0] in shell1:
            if shell2 in shells[1] or shells[1] in shell2:
                transition_allowed = True
                break
    
    if transition_allowed:
        if min_energy == -1.0 and max_energy == -1.0:
            return True
        elif energy >= min_energy and energy <= max_energy:
            return True


finalTransitionCount = 0


with open(output_dir + "/" + input_spectra.split(".")[0] + "_restricted." + input_spectra.split(".")[1], "w") as restricted:
    with open(output_dir + "/" + input_spectra, "r") as spectrum:
        header = spectrum.readline()
        if "Date:" in header:
            header = header.split("Date:")[0] + "Date: "
            header += datetime.today().strftime('%d-%m-%Y') + "\n\n"
        else:
            header = "# Atomic number Z= N/A  Date:" + datetime.today().strftime('%d-%m-%Y') + "\n\n"
        
        restricted.write(header)
        
        spectrum.readline() # Empty line
        restricted.write(spectrum.readline())
        
        for i, line in enumerate(spectrum):
            
            print("Processing transition: " + str(i + 1) + "/" + str(transition_num), end='\r')
            
            vals = line.strip().split()
            
            Shelli = vals[1].strip()
            Shellf = vals[5].strip()
            Energies = float(vals[8].strip())
            
            if filterTransition(Shelli, Shellf, Energies):
                restricted.write(line)
                finalTransitionCount += 1


print("\n\nTotal count of restricted transitions: " + str(finalTransitionCount))