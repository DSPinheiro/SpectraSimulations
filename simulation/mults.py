"""
Module with functions that calculate various multipliers for line intensities, such as excitation beam overlap and cascade boosts.
"""

from data.definitions import Line

import interface.variables as guiVars
import data.variables as generalVars

import math

import numpy as np

import scipy.integrate as integrate

from typing import List, Dict

# --------------------------------------------------------- #
#                                                           #
#        FUNCTIONS TO CALCULATE INTENSITY MULTIPLIERS       #
#                                                           #
# --------------------------------------------------------- #

# Calculate the overlap between the beam energy profile and the energy necessary to reach the level
def get_overlap(line: Line, beam: float, FWHM: float) -> float:
    """
    Function to calculate the levels overlap with the beam energy profile
        
        Args:
            line: the data line of the transition that we want to find the ionization energy
            beam: the beam energy introduced in the interface
            FWHM: the beam energy FWHM introduced in the interface
            shakeup: orbital where the shake-up electron ends in. If empty it is not a shake-up transition

        Returns:
            overlap: the overlap
    """
    
    if beam <= 0.0:
        return 1.0
    
    if len(line.Shelli) <= 4:
        if len(line.Shelli) == 2:
            formationEnergy = generalVars.formationEnergies['diagram'][line.keyI()]
            pWidth = generalVars.partialWidths['diagram'][line.keyI()]
        else:
            formationEnergy = generalVars.formationEnergies['satellite'][line.keyI()]
            pWidth = generalVars.partialWidths['satellite'][line.keyI()]
    else:
        formationEnergy = generalVars.formationEnergies['shakeup'][line.keyI()]
        pWidth = max(generalVars.partialWidths['shakeup'][line.keyI()], 1E-100)
    
    
    def integrand(x):
        l = (0.5 * pWidth / np.pi) / ((x - formationEnergy) ** 2 + (0.5 * pWidth) ** 2)
        
        if x > beam:
            g = (0.5 * pWidth / np.pi) / ((0.5 * pWidth) ** 2) * np.exp(-((x - beam) / FWHM) ** 2 * np.log(2))
        else:
            g = (0.5 * pWidth / np.pi) / ((0.5 * pWidth) ** 2)
        
        return min(l, g)
    
    x = np.linspace(formationEnergy - 100 * pWidth, formationEnergy + 100 * pWidth, 3001, endpoint=True)
    return integrate.simpson([integrand(x1) for x1 in x], x)

# Find the branching ratio from Auger process of a higher shell for the satellite transition
def get_AugerBR(line: Line):
    """
    Function to find the branching ratio for a satellite transition from the Auger process of a higher shell
        
        Args:
            line: the data line of the transition that we want to find the branching ratio
        
        Returns:
            BR: the branching ratio
    """
    if generalVars.ionizationssat is not None:
        for level in generalVars.ionizationssat:
                if line.filterInitialState(level):
                    return level.br
    
    return 0.0


# Find the branching ratio from Diagram process of a higher shell for the diagram transition
def get_DiagramBR(line: Line):
    """
    Function to find the branching ratio for a diagram transition from the Diagram process of a higher shell
        
        Args:
            line: the data line of the transition that we want to find the branching ratio
        
        Returns:
            BR: the branching ratio
    """
    if generalVars.ionizationsrad is not None:
        for level in generalVars.ionizationsrad:
                if line.filterInitialState(level):
                    return level.br
    
    return 0.0


def get_cascadeBoost(cascadeType: str):
    
    Initials: List[str] = []
    Finals: List[str] = []
    MatrixDict: Dict[str, float] = {}
    
    if cascadeType == 'diagram':
        if len(generalVars.radBoostMatrixDict) == 0:
            for level in generalVars.diagramwidths:
                initial = level.labelI()
                final = level.labelF()
                Initials.append(initial)
                Finals.append(final)
                
                MatrixDict[level.key()] = level.intensity
                
                cascades = [[initial]]
                cascadesBRs = [[get_DiagramBR(level)]]
                
                casc_idx = 0
                depth = 0
                
                while True:
                    depth_found = False
                    curr_cascade = cascades[casc_idx].copy()
                    
                    for line in generalVars.lineradrates:
                        if line.labelF() == cascades[casc_idx][depth] and not depth_found:
                            cascades[casc_idx].append(line.labelI())
                            depth += 1
                            depth_found = True
                            
                            cascadesBRs[casc_idx].append(get_DiagramBR(line))
                        elif line.labelF() == cascades[casc_idx][depth] and depth_found:
                            cascades.append([line.labelF(), line.labelI()])
                            cascadesBRs.append([get_DiagramBR(line)])
                    
                    if curr_cascade == cascades[casc_idx]:
                        if len(cascades) > casc_idx + 1:
                            casc_idx += 1
                            depth = 1
                        else:
                            break
                
                root_cascade_idx = 0
                totalBoosts_perCascade: Dict[str, float] = {}
                knots: Dict[str, int] = {}
                for i, cascade in enumerate(cascades):
                    if cascade[0] == initial:
                        root_cascade_idx = i
                    else:
                        if cascade[0] not in totalBoosts_perCascade:
                            totalBoosts_perCascade[cascade[0]] = math.prod([br + 1 for br in cascadesBRs[i]])
                            knots[cascade[0]] = 0
                        else:
                            knots[cascade[0]] += 1
                            totalBoosts_perCascade[cascade[0] + "_" + str(knots[cascade[0]])] = math.prod([br + 1 for br in cascadesBRs[i]])

                totalBoost = 0.0
                for l in cascades[root_cascade_idx][::-1]:
                    i = cascades[root_cascade_idx].index(l)
                    if l in totalBoosts_perCascade:
                        preCascadeBoost = totalBoosts_perCascade[l] - 1
                        
                        if l in knots:
                            for knot in range(knots[l]):
                                preCascadeBoost += totalBoosts_perCascade[l + "_" + str(knot)] - 1
                            
                            totalBoost += math.prod(cascadesBRs[root_cascade_idx][i:]) + preCascadeBoost
                    else:
                        totalBoost = (totalBoost + 1) * (cascadesBRs[root_cascade_idx][i] + 1) - 1
                
                generalVars.radBoostMatrixDict[level.key()] = totalBoost
        else:
            for level in generalVars.diagramwidths:
                initial = level.labelI()
                final = level.labelF()
                Initials.append(initial)
                Finals.append(final)
                
                MatrixDict[level.key()] = level.intensity
    elif cascadeType == 'auger':
        if len(generalVars.augBoostMatrixDict) == 0:
            for level in generalVars.augerwidths:
                initial = level.labelI()
                final = level.labelF()
                Initials.append(initial)
                Finals.append(final)
                
                MatrixDict[level.key()] = level.intensity
                
                cascades = [[initial]]
                cascadesBRs = [[get_DiagramBR(level)]]
                
                casc_idx = 0
                depth = 0
                
                while True:
                    depth_found = False
                    curr_cascade = cascades[casc_idx].copy()
                    
                    for line in generalVars.lineauger:
                        if line.labelF() == cascades[casc_idx][depth] and not depth_found:
                            cascades[casc_idx].append(line.labelI())
                            depth += 1
                            depth_found = True
                            
                            cascadesBRs[casc_idx].append(get_DiagramBR(line))
                        elif line.labelF() == cascades[casc_idx][depth] and depth_found:
                            cascades.append([line.labelF(), line.labelI()])
                            cascadesBRs.append([get_DiagramBR(line)])
                    
                    for line in generalVars.lineradrates:
                        if line.labelF() == cascades[casc_idx][depth] and not depth_found:
                            cascades[casc_idx].append(line.labelI())
                            depth += 1
                            depth_found = True
                            
                            cascadesBRs[casc_idx].append(get_DiagramBR(line))
                        elif line.labelF() == cascades[casc_idx][depth] and depth_found:
                            cascades.append([line.labelF(), line.labelI()])
                            cascadesBRs.append([get_DiagramBR(line)])
                    
                    if curr_cascade == cascades[casc_idx]:
                        if len(cascades) > casc_idx + 1:
                            casc_idx += 1
                            depth = 1
                        else:
                            break
                
                root_cascade_idx = 0
                totalBoosts_perCascade: Dict[str, float] = {}
                knots: Dict[str, int] = {}
                for i, cascade in enumerate(cascades):
                    if cascade[0] == initial:
                        root_cascade_idx = i
                    else:
                        if cascade[0] not in totalBoosts_perCascade:
                            totalBoosts_perCascade[cascade[0]] = math.prod([br + 1 for br in cascadesBRs[i]])
                            knots[cascade[0]] = 0
                        else:
                            knots[cascade[0]] += 1
                            totalBoosts_perCascade[cascade[0] + "_" + str(knots[cascade[0]])] = math.prod([br + 1 for br in cascadesBRs[i]])

                totalBoost = 0.0
                for l in cascades[root_cascade_idx][::-1]:
                    i = cascades[root_cascade_idx].index(l)
                    if l in totalBoosts_perCascade:
                        preCascadeBoost = totalBoosts_perCascade[l] - 1
                        
                        if l in knots:
                            for knot in range(knots[l]):
                                preCascadeBoost += totalBoosts_perCascade[l + "_" + str(knot)] - 1
                            
                            totalBoost += math.prod(cascadesBRs[root_cascade_idx][i:]) + preCascadeBoost
                    else:
                        totalBoost = (totalBoost + 1) * (cascadesBRs[root_cascade_idx][i] + 1) - 1
                
                generalVars.augBoostMatrixDict[level.key()] = totalBoost
        else:
            for level in generalVars.augerwidths:
                initial = level.labelI()
                final = level.labelF()
                Initials.append(initial)
                Finals.append(final)
                
                MatrixDict[level.key()] = level.intensity
    elif cascadeType == 'satellite':
        if len(generalVars.satBoostMatrixDict) == 0:
            for level in generalVars.satellitewidths:
                initial = level.labelI()
                final = level.labelF()
                Initials.append(initial)
                Finals.append(final)
                
                MatrixDict[level.key()] = level.intensity
                
                cascades = [[initial]]
                cascadesBRs = [[get_AugerBR(level)]]
                
                casc_idx = 0
                depth = 0
                
                while True:
                    depth_found = False
                    curr_cascade = cascades[casc_idx].copy()
                    
                    for line in generalVars.linesatellites:
                        if line.labelF() == cascades[casc_idx][depth] and not depth_found:
                            cascades[casc_idx].append(line.labelI())
                            depth += 1
                            depth_found = True
                            
                            cascadesBRs[casc_idx].append(get_AugerBR(line))
                        elif line.labelF() == cascades[casc_idx][depth] and depth_found:
                            cascades.append([line.labelF(), line.labelI()])
                            cascadesBRs.append([get_AugerBR(line)])
                    
                    for line in generalVars.lineauger:
                        if line.labelF() == cascades[casc_idx][depth] and not depth_found:
                            cascades[casc_idx].append(line.labelI())
                            depth += 1
                            depth_found = True
                            
                            cascadesBRs[casc_idx].append(get_DiagramBR(line))
                        elif line.labelF() == cascades[casc_idx][depth] and depth_found:
                            cascades.append([line.labelF(), line.labelI()])
                            cascadesBRs.append([get_DiagramBR(line)])
                    
                    for line in generalVars.lineradrates:
                        if line.labelF() == cascades[casc_idx][depth] and not depth_found:
                            cascades[casc_idx].append(line.labelI())
                            depth += 1
                            depth_found = True
                            
                            cascadesBRs[casc_idx].append(get_DiagramBR(line))
                        elif line.labelF() == cascades[casc_idx][depth] and depth_found:
                            cascades.append([line.labelF(), line.labelI()])
                            cascadesBRs.append([get_DiagramBR(line)])
                    
                    if curr_cascade == cascades[casc_idx]:
                        if len(cascades) > casc_idx + 1:
                            casc_idx += 1
                            depth = 1
                        else:
                            break
                
                root_cascade_idx = 0
                totalBoosts_perCascade: Dict[str, float] = {}
                knots: Dict[str, int] = {}
                for i, cascade in enumerate(cascades):
                    if cascade[0] == initial:
                        root_cascade_idx = i
                    else:
                        if cascade[0] not in totalBoosts_perCascade:
                            totalBoosts_perCascade[cascade[0]] = math.prod([br + 1 for br in cascadesBRs[i]])
                            knots[cascade[0]] = 0
                        else:
                            knots[cascade[0]] += 1
                            totalBoosts_perCascade[cascade[0] + "_" + str(knots[cascade[0]])] = math.prod([br + 1 for br in cascadesBRs[i]])

                totalBoost = 0.0
                for l in cascades[root_cascade_idx][::-1]:
                    i = cascades[root_cascade_idx].index(l)
                    if l in totalBoosts_perCascade:
                        preCascadeBoost = totalBoosts_perCascade[l] - 1
                        
                        if l in knots:
                            for knot in range(knots[l]):
                                preCascadeBoost += totalBoosts_perCascade[l + "_" + str(knot)] - 1
                            
                            totalBoost += math.prod(cascadesBRs[root_cascade_idx][i:]) + preCascadeBoost
                    else:
                        totalBoost = (totalBoost + 1) * (cascadesBRs[root_cascade_idx][i] + 1) - 1
                
                generalVars.satBoostMatrixDict[level.key()] = totalBoost
    else:
        raise RuntimeError("Error: unexpected cascade boost type: " + cascadeType + ". Implemented types are diagram, auger and satellite.")
    
    
    return Initials, Finals, MatrixDict