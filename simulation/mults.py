"""
Module with functions that calculate various multipliers for line intensities, such as excitation beam overlap and cascade boosts.
"""

from data.definitions import Line

import interface.variables as guiVars
import data.variables as generalVars

import math

import numpy as np

import scipy.integrate as integrate

from typing import List, Dict, Type

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
            pWidth = generalVars.partialWidths['diagram'][line.keyI()]
            formationEnergy = generalVars.formationEnergies['diagram'][line.keyI()] + pWidth
        else:
            pWidth = generalVars.partialWidths['satellite'][line.keyI()]
            formationEnergy = generalVars.formationEnergies['satellite'][line.keyI()] + pWidth
    else:
        # pWidth = FWHM
        pWidth = max(generalVars.partialWidths['shakeup'][line.keyI()], 1E-100)
        formationEnergy = generalVars.formationEnergies['shakeup'][line.keyI()] + pWidth
    
    
    def integrand(x):
        x1 = x[x > beam]
        x2 = x[x <= beam]
        
        l1 = (0.5 * pWidth / np.pi) / ((0.5 * pWidth) ** 2) * np.ones(len(x1))
        l2 = (0.5 * pWidth / np.pi) / (np.power((x2 - formationEnergy), 2) + (0.5 * pWidth) ** 2)
        g1 = (0.5 * pWidth / np.pi) / ((0.5 * pWidth) ** 2) * np.exp(-np.power(((x1 - beam) / FWHM), 2) * np.log(2))
        g2 = (0.5 * pWidth / np.pi) / ((0.5 * pWidth) ** 2) * np.ones(len(x2))
        
        r1 = np.minimum(l1, g1)
        r2 = np.minimum(l2, g2)
        
        return np.concatenate((r2, r1))
    
    x = np.linspace(formationEnergy - 100 * pWidth, formationEnergy + 100 * pWidth, 3001, endpoint=True)
    
    return integrate.simpson(integrand(x), x)
    # if formationEnergy > beam:
    #     return np.exp(-((formationEnergy - beam) / FWHM) ** 2 * np.log(2))
    # else:
    #     return 1.0


# Calculate the overlap for excitations between the beam energy profile and the energy necessary to reach the level
def get_overlap_exc(line: Line, beam: float, FWHM: float, exc_index: int) -> float:
    """
    Function to calculate for excitations the levels overlap with the beam energy profile.
    For excitations we keep the resonant nature of the lorentz, gaussian convolution
        
        Args:
            line: the excitation data line of the transition that we want to find the ionization energy
            beam: the beam energy introduced in the interface
            FWHM: the beam energy FWHM introduced in the interface

        Returns:
            overlap: the overlap
    """
    
    if beam <= 0.0:
        return 1.0
    
    if len(line.Shelli) <= 4:
        if len(line.Shelli) == 2:
            if line.keyI() not in generalVars.formationEnergies_exc[exc_index]['diagram']:
                print(f'{generalVars.rad_EXC[exc_index]} -> {line.keyI()}')
            
            formationEnergy = generalVars.formationEnergies_exc[exc_index]['diagram'][line.keyI()]
            pWidth = generalVars.partialWidths_exc[exc_index]['diagram'][line.keyI()]
            pWidth = max(pWidth, 1E-100)
        else:
            # print(f'{generalVars.rad_EXC[exc_index]} -> {line.keyI()}')
            formationEnergy = generalVars.formationEnergies_exc[exc_index]['satellite'][line.keyI()]
            pWidth = generalVars.partialWidths_exc[exc_index]['satellite'][line.keyI()]
            pWidth = max(pWidth, 1E-100)
    else:
        formationEnergy = generalVars.formationEnergies_exc[exc_index]['shakeup'][line.keyI()]
        pWidth = max(generalVars.partialWidths_exc[exc_index]['shakeup'][line.keyI()], 1E-100)
    
    pWidth /= 2.0
    pWidth *= 0.75
    
    def integrand(x):
        l = (0.5 * pWidth / np.pi) / (np.power((x - formationEnergy), 2) + (0.5 * pWidth) ** 2)
        g = (0.5 * pWidth / np.pi) / ((0.5 * pWidth) ** 2) * np.exp(-np.power(((x - beam) / FWHM), 2) * np.log(2))
        
        return np.minimum(l, g)
    
    x = np.linspace(formationEnergy - 100 * pWidth, formationEnergy + 100 * pWidth, 3001, endpoint=True)
    return integrate.simpson(integrand(x), x)


# Calculate the total yields and ratios for each existing excitation and level
def setupExcitationYields():
    for exc_index, _ in enumerate(generalVars.rad_EXC):
        generalVars.total_decayrates_exc.append(sum([line.rate for line in generalVars.linenurates_EXC[exc_index]]))
    
    for exc_index, _ in enumerate(generalVars.rad_EXC):
        generalVars.level_decayrates_exc.append({})
        for line in generalVars.linenurates_EXC[exc_index]:
            generalVars.level_decayrates_exc[exc_index][line.keyI()] = line.rate


# Calculate the excitaion ratio normalized for all loaded excitations
def get_ExcRatio(line: Line, exc_index: int) -> float:
    excitation_ratio: float = generalVars.total_decayrates_exc[exc_index] / sum(generalVars.total_decayrates_exc)
    
    if len(line.keyI().split("_")[0]) == 4:
        totalDirectDecays: float = sum([generalVars.level_decayrates_exc[exc_index][key] for key in generalVars.level_decayrates_exc[exc_index] if line.keyI()[:2] in key])
        avgDirectDecay: float = totalDirectDecays / sum([line.keyI()[:2] in key for key in generalVars.level_decayrates_exc[exc_index]])
        level_ratio: float = avgDirectDecay / sum(generalVars.level_decayrates_exc[exc_index][key] for key in generalVars.level_decayrates_exc[exc_index] if line.keyI()[:2] in key)
    else:
        if line.keyI() not in generalVars.level_decayrates_exc[exc_index]:
            print(f'{generalVars.rad_EXC[exc_index]} -> {line.keyI()}')
            print(generalVars.level_decayrates_exc[exc_index])

        level_ratio: float = generalVars.level_decayrates_exc[exc_index][line.keyI()] / sum(generalVars.level_decayrates_exc[exc_index][key] for key in generalVars.level_decayrates_exc[exc_index] if line.keyI()[:2] in key)
    
    return excitation_ratio * level_ratio


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