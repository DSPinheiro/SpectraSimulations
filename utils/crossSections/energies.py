"""
Module with functions to initialize helper variables to optimize the line filtering and intensity calculation
"""

from __future__ import annotations


import data.variables as generalVars

from data.definitions import Line

import numpy as np

from typing import List


def setupFormationEnergies(irad: List[Line] | None = [], isat: List[Line] | None = [], iup: List[Line] | None = []):
    ionizationsrad = []
    if irad != None:
        if irad != []:
            ionizationsrad = irad
        else:
            ionizationsrad = generalVars.ionizationsrad
    else:
        ionizationsrad = generalVars.ionizationsrad
    
    ionizationssat = []
    if isat != None:
        if isat != []:
            ionizationssat = isat
        else:
            ionizationssat = generalVars.ionizationssat
    else:
        ionizationssat = generalVars.ionizationssat
    
    ionizationsshakeup = []
    if iup != None:
        if iup != []:
            ionizationsshakeup = iup
        else:
            ionizationsshakeup = generalVars.ionizationsshakeup
    else:
        ionizationsshakeup = generalVars.ionizationsshakeup
    
    if type(ionizationsrad) != type(None):
        generalVars.formationEnergies['diagram'] = {}
        generalVars.formationEnergies['auger'] = {}
        for level in ionizationsrad:
            generalVars.formationEnergies['diagram'][level.keyI()] = level.gEnergy
            generalVars.formationEnergies['auger'][level.keyI()] = level.gEnergy
    
    if type(ionizationssat) != type(None):
        generalVars.formationEnergies['satellite'] = {}
        for level in ionizationssat:
            generalVars.formationEnergies['satellite'][level.keyI()] = level.gEnergy
    
    if type(ionizationsshakeup) != type(None):
        generalVars.formationEnergies['shakeup'] = {}
        for level in ionizationsshakeup:
            generalVars.formationEnergies['shakeup'][level.keyI()] = level.gEnergy
    
    return generalVars.formationEnergies

def setupFormationEnergiesExc(irad: List[List[Line]] | None = [], isat: List[List[Line]] | None = [], iup: List[List[Line]] | None = []):
    ionizationsrad = []
    if irad != None:
        if irad != []:
            ionizationsrad = irad
        else:
            ionizationsrad = generalVars.ionizationsrad_exc
    else:
        ionizationsrad = generalVars.ionizationsrad_exc
    
    ionizationssat = []
    if isat != None:
        if isat != []:
            ionizationssat = isat
        else:
            ionizationssat = generalVars.ionizationssat_exc
    else:
        ionizationssat = generalVars.ionizationssat_exc
    
    ionizationsshakeup = []
    if iup != None:
        if iup != []:
            ionizationsshakeup = iup
        else:
            ionizationsshakeup = generalVars.ionizationsshakeup_exc
    else:
        ionizationsshakeup = generalVars.ionizationsshakeup_exc
    
    if type(ionizationsrad) != type(None):
        for exc_index, levels in enumerate(ionizationsrad):
            generalVars.formationEnergies_exc.append({})
            generalVars.formationEnergies_exc.append({})
            
            generalVars.formationEnergies_exc[exc_index]['diagram'] = {}
            generalVars.formationEnergies_exc[exc_index]['auger'] = {}
            
            for level in levels:
                generalVars.formationEnergies_exc[exc_index]['diagram'][level.keyI()] = level.gEnergy
                generalVars.formationEnergies_exc[exc_index]['auger'][level.keyI()] = level.gEnergy
    
    if type(ionizationssat) != type(None):
        for exc_index, levels in enumerate(ionizationssat):
            generalVars.formationEnergies_exc.append({})
            generalVars.formationEnergies_exc[exc_index]['satellite'] = {}
            for level in levels:
                # print(f'{generalVars.sat_EXC[exc_index]} -> {level.keyI()}')
                generalVars.formationEnergies_exc[exc_index]['satellite'][level.keyI()] = level.gEnergy
    
    if type(ionizationsshakeup) != type(None):
        for exc_index, levels in enumerate(ionizationsshakeup):
            generalVars.formationEnergies_exc.append({})
            generalVars.formationEnergies_exc[exc_index]['shakeup'] = {}
            for level in levels:
                generalVars.formationEnergies_exc[exc_index]['shakeup'][level.keyI()] = level.gEnergy
    
    return generalVars.formationEnergies_exc


def setupPartialWidths(irad: List[Line] | None = [], isat: List[Line] | None = [], iup: List[Line] | None = []):
    ionizationsrad = []
    if irad != None:
        if irad != []:
            ionizationsrad = irad
        else:
            ionizationsrad = generalVars.ionizationsrad
    else:
        ionizationsrad = generalVars.ionizationsrad
    
    ionizationssat = []
    if isat != None:
        if isat != []:
            ionizationssat = isat
        else:
            ionizationssat = generalVars.ionizationssat
    else:
        ionizationssat = generalVars.ionizationssat
    
    ionizationsshakeup = []
    if iup != None:
        if iup != []:
            ionizationsshakeup = iup
        else:
            ionizationsshakeup = generalVars.ionizationsshakeup
    else:
        ionizationsshakeup = generalVars.ionizationsshakeup
    
    if type(ionizationsrad) != type(None):
        generalVars.partialWidths['diagram'] = {}
        generalVars.partialWidths['auger'] = {}
        for level in ionizationsrad:
            generalVars.partialWidths['diagram'][level.keyI()] = level.totalWidth
            generalVars.partialWidths['auger'][level.keyI()] = level.totalWidth
    
    if type(ionizationssat) != type(None):
        generalVars.partialWidths['satellite'] = {}
        for level in ionizationssat:
            generalVars.partialWidths['satellite'][level.keyI()] = level.totalWidth
    
    if type(ionizationsshakeup) != type(None):
        generalVars.partialWidths['shakeup'] = {}
        for level in ionizationsshakeup:
            generalVars.partialWidths['shakeup'][level.keyI()] = level.totalWidth
    
    return generalVars.partialWidths


def setupPartialWidthsExc(irad: List[List[Line]] | None = [], isat: List[List[Line]] | None = [], iup: List[List[Line]] | None = []):
    ionizationsrad = []
    if irad != None:
        if irad != []:
            ionizationsrad = irad
        else:
            ionizationsrad = generalVars.ionizationsrad_exc
    else:
        ionizationsrad = generalVars.ionizationsrad_exc
    
    ionizationssat = []
    if isat != None:
        if isat != []:
            ionizationssat = isat
        else:
            ionizationssat = generalVars.ionizationssat_exc
    else:
        ionizationssat = generalVars.ionizationssat_exc
    
    ionizationsshakeup = []
    if iup != None:
        if iup != []:
            ionizationsshakeup = iup
        else:
            ionizationsshakeup = generalVars.ionizationsshakeup_exc
    else:
        ionizationsshakeup = generalVars.ionizationsshakeup_exc
    
    if type(ionizationsrad) != type(None):
        for exc_index, levels in enumerate(ionizationsrad):
            generalVars.partialWidths_exc.append({})
            generalVars.partialWidths_exc.append({})
            generalVars.partialWidths_exc[exc_index]['diagram'] = {}
            generalVars.partialWidths_exc[exc_index]['auger'] = {}
            for level in levels:
                generalVars.partialWidths_exc[exc_index]['diagram'][level.keyI()] = level.totalWidth
                generalVars.partialWidths_exc[exc_index]['auger'][level.keyI()] = level.totalWidth
    
    if type(ionizationssat) != type(None):
        for exc_index, levels in enumerate(ionizationssat):
            generalVars.partialWidths_exc.append({})
            generalVars.partialWidths_exc[exc_index]['satellite'] = {}
            for level in levels:
                generalVars.partialWidths_exc[exc_index]['satellite'][level.keyI()] = level.totalWidth
    
    if type(ionizationsshakeup) != type(None):
        for exc_index, levels in enumerate(ionizationsshakeup):
            generalVars.partialWidths_exc.append({})
            generalVars.partialWidths_exc[exc_index]['shakeup'] = {}
            for level in levels:
                generalVars.partialWidths_exc[exc_index]['shakeup'][level.keyI()] = level.totalWidth
    
    return generalVars.partialWidths_exc



def ComptonEnergy(E0: float, theta: float):
    # Calculate the Compton energy for an incident radiation energy and angle
    
    return E0 / (1 + (E0 / (generalVars.mc2)) * (1 - np.cos(theta)))