"""
Module with analysis functions for the element to be simulated.
These functions prepare the data that is used in the tools menu in the interface.
"""

from __future__ import annotations


#Data import for variable management
import data.variables as generalVars

#GUI utils for interface variables
import interface.variables as guiVars


from simulation.mults import get_cascadeBoost

import numpy as np

from typing import List, Dict
import numpy.typing as npt


import copy


# --------------------------------------------------------- #
#                                                           #
# FUNCTIONS TO PREPARE ANALYSIS DATA FOR COMPANION WINDOWS  #
#                                                           #
# --------------------------------------------------------- #


def prepareBoostMatrices():
    radInitials, radFinals, radMatrixDict = get_cascadeBoost('diagram')
    
    radInitials = list(set(radInitials))
    radFinals = list(set(radFinals))
    
    radInitials.sort()
    radFinals.sort()
    
    radData: npt.NDArray[np.float64] = np.zeros((len(radInitials), len(radFinals)))
    radDataExtra: npt.NDArray[np.float64] = np.zeros((len(radInitials), len(radFinals)))
    
    for i, initial in enumerate(radInitials):
        for j, final in enumerate(radFinals):
            key = initial + "->" + final
            
            if key in radMatrixDict:
                radData[i, j] = generalVars.radBoostMatrixDict[key]
                radDataExtra[i, j] = radMatrixDict[key] * (1 + generalVars.radBoostMatrixDict[key])
    
    print("Done Radiative Boosts")
    
    
    augInitials, augFinals, augMatrixDict = get_cascadeBoost('auger')
    
    augInitials = list(set(augInitials))
    augFinals = list(set(augFinals))
    
    augInitials.sort()
    augFinals.sort()
    
    augData: npt.NDArray[np.float64] = np.zeros((len(augInitials), len(augFinals)))
    augDataExtra: npt.NDArray[np.float64] = np.zeros((len(augInitials), len(augFinals)))
    
    for i, initial in enumerate(augInitials):
        for j, final in enumerate(augFinals):
            key = initial + "->" + final
            
            if key in augMatrixDict:
                augData[i, j] = generalVars.augBoostMatrixDict[key]
                augDataExtra[i, j] = augMatrixDict[key] * (1 + generalVars.augBoostMatrixDict[key])
    
    print("Done Auger Boosts")
    
    
    satInitials, satFinals, satMatrixDict = get_cascadeBoost('satellite')
    
    satInitials = list(set(satInitials))
    satFinals = list(set(satFinals))
    
    satInitials.sort()
    satFinals.sort()
    
    satData: npt.NDArray[np.float64] = np.zeros((len(satInitials), len(satFinals)))
    satDataExtra: npt.NDArray[np.float64] = np.zeros((len(satInitials), len(satFinals)))
    
    for i, initial in enumerate(satInitials):
        for j, final in enumerate(satFinals):
            key = initial + "->" + final
            
            if key in satMatrixDict:
                satData[i, j] = generalVars.satBoostMatrixDict[key]
                satDataExtra[i, j] = satMatrixDict[key] * (1 + generalVars.satBoostMatrixDict[key])
    
    print("Done Satellite Boosts")
    
    
    return radInitials, radFinals, radData, radDataExtra, \
            augInitials, augFinals, augData, augDataExtra, \
            satInitials, satFinals, satData, satDataExtra
    

def prepareRateMatrices():
    radInitials: List[str] = []
    radFinals: List[str] = []
    radMatrixDict: Dict[str, float] = {}
    
    for line in generalVars.diagramwidths:
        initial = line.labelI()
        final = line.labelF()
        radInitials.append(initial)
        radFinals.append(final)
        
        radMatrixDict[line.key()] = line.intensity
    
    radInitials = list(set(radInitials))
    radFinals = list(set(radFinals))
    
    radInitials.sort()
    radFinals.sort()
    
    radData: npt.NDArray[np.float64] = np.zeros((len(radInitials), len(radFinals)))
    
    for i, initial in enumerate(radInitials):
        for j, final in enumerate(radFinals):
            key = initial + "->" + final
            
            if key in radMatrixDict:
                radData[i, j] = radMatrixDict[key]
    
    
    
    augInitials: List[str] = []
    augFinals: List[str] = []
    augMatrixDict: Dict[str, float] = {}
    
    for line in generalVars.augerwidths:
        initial = line.labelI()
        final = line.labelF()
        augInitials.append(initial)
        augFinals.append(final)
        
        augMatrixDict[line.key()] = line.intensity
    
    augInitials = list(set(augInitials))
    augFinals = list(set(augFinals))
    
    augInitials.sort()
    augFinals.sort()
    
    augData: npt.NDArray[np.float64] = np.zeros((len(augInitials), len(augFinals)))
    
    for i, initial in enumerate(augInitials):
        for j, final in enumerate(augFinals):
            key = initial + "->" + final
            
            if key in augMatrixDict:
                augData[i, j] = augMatrixDict[key]
    
    
    
    satInitials: List[str] = []
    satFinals: List[str] = []
    satMatrixDict: Dict[str, float] = {}
    
    for line in generalVars.satellitewidths:
        initial = line.labelI()
        final = line.labelF()
        satInitials.append(initial)
        satFinals.append(final)
        
        satMatrixDict[line.key()] = line.intensity
    
    satInitials = list(set(satInitials))
    satFinals = list(set(satFinals))
    
    satInitials.sort()
    satFinals.sort()
    
    satData: npt.NDArray[np.float64] = np.zeros((len(satInitials), len(satFinals)))
    
    for i, initial in enumerate(satInitials):
        for j, final in enumerate(satFinals):
            key = initial + "->" + final
            
            if key in satMatrixDict:
                satData[i, j] = satMatrixDict[key]
    
    
    return radInitials, radFinals, radData, \
            augInitials, augFinals, augData, \
            satInitials, satFinals, satData


def computeCascadeGraph(cascadeType: str):
    nodes: List[Dict[str, int | float | str]] = []
    edges: List[Dict[str, int | float]] = []
    
    hOffset = 1
    vOffset = 1
    
    if cascadeType == "diagram":
        for line in generalVars.lineradrates:
            if line.energy > 0.0:
                fStateEnergy = [level.energy for level in generalVars.ionizationsrad if line.filterFinalState(level)][0]
                
                node_f: Dict[str, int | float | str] = {}
                node_f['x'] = line.jjf * hOffset
                node_f['y'] = fStateEnergy * vOffset
                node_f['label'] = line.labelF()
                node_f['Energy'] = fStateEnergy
                
                
                if node_f not in nodes:
                    nodes.append(node_f)
                
                iStateEnergy = [level.energy for level in generalVars.ionizationsrad if line.filterInitialState(level)][0]
                
                appendInitial = False
                node_i: Dict[str, int | float | str] = {}
                node_i['x'] = line.jji * hOffset
                node_i['y'] = iStateEnergy * vOffset
                node_i['label'] = line.labelI()
                node_i['Energy'] = iStateEnergy
                
                
                EcrossSection = guiVars.exc_mech_var.get() # type: ignore
                crossSection = 1.0
                x = 0
                maxFormation = max(generalVars.ionizationsrad, key=lambda x: x.gEnergy).gEnergy
                for level in generalVars.ionizationsrad:
                    if line.filterInitialState(level):
                        x = guiVars.excitation_energy.get() # type: ignore
                        formationEnergy = level.gEnergy
                        if x == 0:
                            x = maxFormation * 100
                        
                        if EcrossSection == 'EII':
                            crossSection = generalVars.elementMRBEB[line.Shelli](formationEnergy, x)
                        elif EcrossSection == 'PIon':
                            crossSection = generalVars.ELAMPhotoSpline(np.log(x)) # type: ignore
                        
                        break
                
                if node_i not in nodes:
                    appendInitial = True
                else:
                    idx = nodes.index(node_i)
                    if 'beam' not in nodes[idx]:
                        nodes[idx]['beam'] = x
                        nodes[idx]['cross'] = crossSection
                        nodes[idx]['type'] = EcrossSection
                
                node_i['beam'] = x
                node_i['cross'] = crossSection
                node_i['type'] = EcrossSection
                
                if appendInitial and node_i not in nodes:
                    nodes.append(node_i)
                
                edge: Dict[str, int | float] = {}
                
                edge['final'] = nodes.index(node_f)
                edge['initial'] = nodes.index(node_i)
                
                edge['energy'] = line.energy
                edge['rate'] = line.intensity
                edge['width'] = line.totalWidth
                
                edges.append(edge)
        
        
        maxX = max(nodes, key=lambda x: x['x'])['x'] * hOffset
        maxY = max(nodes, key=lambda x: x['y'])['y'] * vOffset
        
        
        sorted_nodes = copy.deepcopy(nodes)
        sorted_nodes.sort(key=lambda x: x['y'])
        
        for j, node in enumerate(sorted_nodes):
            i = nodes.index(node)
            nodes[i]['y'] -= nodes[i]['y'] + j * vOffset # type: ignore
        
        for node in nodes:
            node['x'] /= maxX # type: ignore
            node['y'] /= maxY # type: ignore
    elif cascadeType == "satellite":
        for line in generalVars.linesatellites:
            if line.energy > 0.0:
                fStateEnergy = [level.energy for level in generalVars.ionizationssat if line.filterFinalState(level)][0]
                
                node_f = {}
                node_f['x'] = line.jjf * hOffset
                node_f['y'] = fStateEnergy * vOffset
                node_f['label'] = line.labelF()
                node_f['Energy'] = fStateEnergy
                
                
                if node_f not in nodes:
                    nodes.append(node_f)
                
                iStateEnergy = [level.energy for level in generalVars.ionizationssat if line.filterInitialState(level)][0]
                
                appendInitial = False
                node_i = {}
                node_i['x'] = line.jji * hOffset
                node_i['y'] = iStateEnergy * vOffset
                node_i['label'] = line.labelI()
                node_i['Energy'] = iStateEnergy
                
                
                EcrossSection = guiVars.exc_mech_var.get() # type: ignore
                crossSection = 1.0
                x = 0
                maxFormation = max(generalVars.ionizationssat, key=lambda x: x.gEnergy).gEnergy
                for level in generalVars.ionizationssat:
                    if line.filterInitialState(level):
                        x = guiVars.excitation_energy.get() # type: ignore
                        formationEnergy = level.gEnergy
                        if x == 0:
                            x = maxFormation * 100
                        
                        if EcrossSection == 'EII':
                            crossSection = generalVars.elementMRBEB[line.Shelli[:2]](formationEnergy, x)
                        elif EcrossSection == 'PIon':
                            crossSection = generalVars.ELAMPhotoSpline(np.log(x)) # type: ignore
                        
                        break
                
                if node_i not in nodes:
                    appendInitial = True
                else:
                    idx = nodes.index(node_i)
                    if 'beam' not in nodes[idx]:
                        nodes[idx]['beam'] = x
                        nodes[idx]['cross'] = crossSection
                        nodes[idx]['type'] = EcrossSection
                
                node_i['beam'] = x
                node_i['cross'] = crossSection
                node_i['type'] = EcrossSection
                
                if appendInitial and node_i not in nodes:
                    nodes.append(node_i)
                                
                edge = {}
                
                edge['final'] = nodes.index(node_f)
                edge['initial'] = nodes.index(node_i)
                
                edge['energy'] = line.energy
                edge['rate'] = line.intensity
                edge['width'] = line.totalWidth
                
                edges.append(edge)
        
        add_auger = True
        if add_auger:
            for line in generalVars.lineauger:
                if line.energy > 0.0:
                    iStateEnergy = [level.energy for level in generalVars.ionizationsrad if line.filterInitialState(level)][0]
                    
                    appendInitial = False
                    node_i = {}
                    node_i['x'] = line.jji * hOffset
                    node_i['y'] = iStateEnergy * vOffset
                    node_i['label'] = line.labelI()
                    node_i['Energy'] = iStateEnergy                
                    
                    
                    EcrossSection = guiVars.exc_mech_var.get() # type: ignore
                    crossSection = 1.0
                    x = 0
                    maxFormation = max(generalVars.ionizationsrad, key=lambda x: x.gEnergy).gEnergy
                    for level in generalVars.ionizationsrad:
                        if line.filterInitialState(level):
                            x = guiVars.excitation_energy.get() # type: ignore
                            formationEnergy = level.gEnergy
                            if x == 0:
                                x = maxFormation * 100
                            
                            if EcrossSection == 'EII':
                                crossSection = generalVars.elementMRBEB[line.Shelli](formationEnergy, x)
                            elif EcrossSection == 'PIon':
                                crossSection = generalVars.ELAMPhotoSpline(np.log(x)) # type: ignore
                            
                            break
                    
                    if node_i not in nodes:
                        appendInitial = True
                    else:
                        idx = nodes.index(node_i)
                        if 'beam' not in nodes[idx]:
                            nodes[idx]['beam'] = x
                            nodes[idx]['cross'] = crossSection
                            nodes[idx]['type'] = EcrossSection
                            nodes[idx]['aug'] = 0
                            
                    
                    node_i['beam'] = x
                    node_i['cross'] = crossSection
                    node_i['type'] = EcrossSection
                    
                    if appendInitial and node_i not in nodes:
                        node_i['aug'] = 0
                        if node_i not in nodes:
                            nodes.append(node_i)
                    
                    edge = {}
                    
                    for i, node in enumerate(nodes):
                        if node['label'] == line.labelF():
                            edge['final'] = i
                    
                    if 'final' in edge:
                        edge['initial'] = nodes.index(node_i)
                        
                        edge['energy'] = line.energy
                        edge['rate'] = line.intensity
                        edge['width'] = line.totalWidth
                        
                        edges.append(edge)
        
        add_dia = True
        if add_dia:
            for line in generalVars.lineradrates:
                if line.energy > 0.0:
                    iStateEnergy = [level.energy for level in generalVars.ionizationsrad if line.filterInitialState(level)][0]
                    
                    appendInitial = False
                    node_i = {}
                    node_i['x'] = line.jji * hOffset
                    node_i['y'] = iStateEnergy * vOffset
                    node_i['label'] = line.labelI()
                    node_i['Energy'] = iStateEnergy                
                    
                    
                    EcrossSection = guiVars.exc_mech_var.get() # type: ignore
                    crossSection = 1.0
                    x = 0
                    maxFormation = max(generalVars.ionizationsrad, key=lambda x: x.gEnergy).gEnergy
                    for level in generalVars.ionizationsrad:
                        if line.filterInitialState(level):
                            x = guiVars.excitation_energy.get() # type: ignore
                            formationEnergy = level.gEnergy
                            if x == 0:
                                x = maxFormation * 100
                            
                            if EcrossSection == 'EII':
                                crossSection = generalVars.elementMRBEB[line.Shelli](formationEnergy, x)
                            elif EcrossSection == 'PIon':
                                crossSection = generalVars.ELAMPhotoSpline(np.log(x)) # type: ignore
                            
                            break
                    
                    if node_i not in nodes:
                        appendInitial = True
                    else:
                        idx = nodes.index(node_i)
                        if 'beam' not in nodes[idx]:
                            nodes[idx]['beam'] = x
                            nodes[idx]['cross'] = crossSection
                            nodes[idx]['type'] = EcrossSection
                            nodes[idx]['dia'] = 0
                            
                    
                    node_i['beam'] = x
                    node_i['cross'] = crossSection
                    node_i['type'] = EcrossSection
                    
                    if appendInitial and node_i not in nodes:
                        node_i['aug'] = 0
                        if node_i not in nodes:
                            del node_i['aug']
                            node_i['dia'] = 0
                            nodes.append(node_i)
                    
                    edge = {}
                    
                    for i, node in enumerate(nodes):
                        if node['label'] == line.labelF():
                            edge['final'] = i
                    
                    if 'final' in edge:
                        edge['initial'] = nodes.index(node_i)
                        
                        edge['energy'] = line.energy
                        edge['rate'] = line.intensity
                        edge['width'] = line.totalWidth
                        
                        edges.append(edge)
        
        
        maxX = max(nodes, key=lambda x: x['x'])['x'] * hOffset
        maxY = max(nodes, key=lambda x: x['y'])['y'] * vOffset

        sorted_nodes = copy.deepcopy(nodes)
        sorted_nodes.sort(key=lambda x: x['y'])
        
        for j, node in enumerate(sorted_nodes):
            i = nodes.index(node)
            nodes[i]['y'] -= nodes[i]['y'] + j * vOffset # type: ignore
        
        for node in nodes:
            node['x'] /= maxX # type: ignore
            node['y'] /= maxY # type: ignore
    elif cascadeType == 'auger':
        for line in generalVars.lineauger:
            if line.energy > 0.0:
                fStateEnergy = [level.energy for level in generalVars.ionizationssat if line.filterFinalState(level)][0]
                
                node_f = {}
                node_f['x'] = line.jjf * hOffset
                node_f['y'] = fStateEnergy * vOffset
                node_f['label'] = line.labelF()
                node_f['Energy'] = fStateEnergy
                
                
                if node_f not in nodes:
                    nodes.append(node_f)
                
                iStateEnergy = [level.energy for level in generalVars.ionizationsrad if line.filterInitialState(level)][0]
                
                appendInitial = False
                node_i = {}
                node_i['x'] = line.jji * hOffset
                node_i['y'] = iStateEnergy * vOffset
                node_i['label'] = line.labelI()
                node_i['Energy'] = iStateEnergy
                
                
                EcrossSection = guiVars.exc_mech_var.get() # type: ignore
                crossSection = 1.0
                x = 0
                maxFormation = max(generalVars.ionizationsrad, key=lambda x: x.gEnergy).gEnergy
                for level in generalVars.ionizationsrad:
                    if line.filterInitialState(level):
                        x = guiVars.excitation_energy.get() # type: ignore
                        formationEnergy = level.gEnergy
                        if x == 0:
                            x = maxFormation * 100
                        
                        if EcrossSection == 'EII':
                            crossSection = generalVars.elementMRBEB[line.Shelli](formationEnergy, x)
                        elif EcrossSection == 'PIon':
                            crossSection = generalVars.ELAMPhotoSpline(np.log(x)) # type: ignore
                        
                        break
                
                if node_i not in nodes:
                    appendInitial = True
                else:
                    idx = nodes.index(node_i)
                    if 'beam' not in nodes[idx]:
                        nodes[idx]['beam'] = x
                        nodes[idx]['cross'] = crossSection
                        nodes[idx]['type'] = EcrossSection
                
                node_i['beam'] = x
                node_i['cross'] = crossSection
                node_i['type'] = EcrossSection
                
                if appendInitial and node_i not in nodes:
                    nodes.append(node_i)
                                
                edge = {}
                
                edge['final'] = nodes.index(node_f)
                edge['initial'] = nodes.index(node_i)
                
                edge['energy'] = line.energy
                edge['rate'] = line.intensity
                edge['width'] = line.totalWidth
                
                edges.append(edge)
        
        
        add_dia = True
        if add_dia:
            for line in generalVars.lineradrates:
                if line.energy > 0.0:
                    iStateEnergy = [level.energy for level in generalVars.ionizationsrad if line.filterInitialState(level)][0]
                    
                    appendInitial = False
                    node_i = {}
                    node_i['x'] = line.jji * hOffset
                    node_i['y'] = iStateEnergy * vOffset
                    node_i['label'] = line.labelI()
                    node_i['Energy'] = iStateEnergy                
                    
                    
                    EcrossSection = guiVars.exc_mech_var.get() # type: ignore
                    crossSection = 1.0
                    x = 0
                    maxFormation = max(generalVars.ionizationsrad, key=lambda x: x.gEnergy).gEnergy
                    for level in generalVars.ionizationsrad:
                        if line.filterInitialState(level):
                            x = guiVars.excitation_energy.get() # type: ignore
                            formationEnergy = level.gEnergy
                            if x == 0:
                                x = maxFormation * 100
                            
                            if EcrossSection == 'EII':
                                crossSection = generalVars.elementMRBEB[line.Shelli](formationEnergy, x)
                            elif EcrossSection == 'PIon':
                                crossSection = generalVars.ELAMPhotoSpline(np.log(x)) # type: ignore
                            
                            break
                    
                    if node_i not in nodes:
                        appendInitial = True
                    else:
                        idx = nodes.index(node_i)
                        if 'beam' not in nodes[idx]:
                            nodes[idx]['beam'] = x
                            nodes[idx]['cross'] = crossSection
                            nodes[idx]['type'] = EcrossSection
                            nodes[idx]['dia'] = 0
                            
                    
                    node_i['beam'] = x
                    node_i['cross'] = crossSection
                    node_i['type'] = EcrossSection
                    
                    if appendInitial and node_i not in nodes:
                        node_i['dia'] = 0
                        if node_i not in nodes:
                            nodes.append(node_i)
                    
                    edge = {}
                    
                    for i, node in enumerate(nodes):
                        if node['label'] == line.labelF():
                            edge['final'] = i
                    
                    if 'final' in edge:
                        edge['initial'] = nodes.index(node_i)
                        
                        edge['energy'] = line.energy
                        edge['rate'] = line.intensity
                        edge['width'] = line.totalWidth
                        
                        edges.append(edge)
        
        
        maxX = max(nodes, key=lambda x: x['x'])['x'] * hOffset
        maxY = max(nodes, key=lambda x: x['y'])['y'] * vOffset

        
        sorted_nodes = copy.deepcopy(nodes)
        sorted_nodes.sort(key=lambda x: x['y'])
        
        for j, node in enumerate(sorted_nodes):
            i = nodes.index(node)
            nodes[i]['y'] -= nodes[i]['y'] + j * vOffset # type: ignore
        
        for node in nodes:
            node['x'] /= maxX # type: ignore
            node['y'] /= maxY # type: ignore
    else:
        raise RuntimeError("Error: Unrecognized cascade type: " + cascadeType + ". Allowed types are diagram, satellite or auger.")
    
    return nodes, edges


def analyseConvergence():
    radInitials: List[str] = []
    radFinals: List[str] = []
    radMatrixDict: Dict[str, Dict] = {}
    
    radConvPars: Dict[str, Dict] = {}
    for line in generalVars.ionizationsrad:
        radConvPars[line.labelI()] = {
                    "overlap": line.convOverlap,
                    "percent": line.percent,
                    "accuracy": line.acc,
                    "diff": line.diff,
                    "ucv": abs(line.convOverlap[1] * (line.acc if line.acc != 0 else 1.0) * (line.diff if  line.diff != 0 else 1.0))
                }
    
    for line in generalVars.diagramwidths:
        initial = line.labelI()
        final = line.labelF()
        radInitials.append(initial)
        radFinals.append(final)
        
        radMatrixDict[line.key()] = {
            "initial": radConvPars[initial],
            "final": radConvPars[final],
            "ucv": line.intensity * (radConvPars[initial]["ucv"] + radConvPars[final]["ucv"]),
            "rate": line.intensity
        }
    
    radInitials = list(set(radInitials))
    radFinals = list(set(radFinals))
    
    radInitials.sort()
    radFinals.sort()
    
    
    satInitials: List[str] = []
    satFinals: List[str] = []
    satMatrixDict: Dict[str, Dict] = {}
    
    satConvPars: Dict[str, Dict] = {}
    for line in generalVars.ionizationssat:
        satConvPars[line.labelI()] = {
                    "overlap": line.convOverlap,
                    "percent": line.percent,
                    "accuracy": line.acc,
                    "diff": line.diff,
                    "ucv": abs(line.convOverlap[1] * (line.acc if line.acc != 0 else 1.0) * (line.diff if  line.diff != 0 else 1.0))
                }
    
    for line in generalVars.satellitewidths:
        initial = line.labelI()
        final = line.labelF()
        satInitials.append(initial)
        satFinals.append(final)
        
        satMatrixDict[line.key()] = {
            "initial": satConvPars[initial],
            "final": satConvPars[final],
            "rate": line.intensity,
            "ucv": line.intensity * (satConvPars[initial]["ucv"] + satConvPars[final]["ucv"]),
            "rate": line.intensity
        }
    
    satInitials = list(set(satInitials))
    satFinals = list(set(satFinals))
    
    satInitials.sort()
    satFinals.sort()
    
    
    return radInitials, radFinals, radMatrixDict, \
            satInitials, satFinals, satMatrixDict