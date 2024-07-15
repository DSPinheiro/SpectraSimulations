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


def ComptonEnergy(E0: float, theta: float):
    # Calculate the Compton energy for an incident radiation energy and angle
    
    return E0 / (1 + (E0 / (generalVars.mc2)) * (1 - np.cos(theta)))