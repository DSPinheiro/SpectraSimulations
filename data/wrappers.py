"""
Module with wrapper functions to initialize sets of data elements.
"""

from __future__ import annotations

from tkinter import messagebox

#OS Imports for files paths
import os
from pathlib import Path

#Data Imports for variable management
import data.variables as generalVars

#File IO Imports
from utils.misc.fileIO import readRates, readIonizationEnergies, readWidths, readMeanR, readELAMelement
from utils.misc.fileIO import searchChargeStates, readChargeStates, readIonPop, readShake

#FileIO utils
from utils.misc.fileIO import load, loadQuantConfigs, readNISTXrayLines, readNISTClusterLines, findElements


from typing import List, Dict



def InitializeMCDFData(dir_path: Path, element: tuple[int, str], filter: Dict[str, bool] = {}):
    # Retrieve the z and name of the element to simulate
    z: int = element[0]
    """
    Variable with the z value of the element to simulate
    """
    element_name: str = element[1]
    """
    Variable with the element name to simulate
    """
    
    # Initialize the element name for the functions module
    generalVars.element_name = element_name
    generalVars.Z = z
    
    if generalVars.verbose >= 3:
        print(element_name)
        print(z)
    
    # ------------------------------------------------- #
    #                                                   #
    #                   FILE PATHS                      #
    #                                                   #
    # ------------------------------------------------- #
    
    
    # Path to the radiative rates file for this element
    radrates_file = dir_path / str(z) / (str(z) + '-intensity.out')
    """
    Variable with the full path to the radiative rates file of this element
    """
    
    if generalVars.verbose >= 3:
        print(radrates_file)
    
    # Path to the satellite rates file for this element
    satellites_file = dir_path / str(z) / (str(z) + '-satinty.out')
    """
    Variable with the full path to the satellite rates file of this element
    """
    
    # Path to the auger rates file for this element
    augrates_file = dir_path / str(z) / (str(z) + '-augrate.out')
    """
    Variable with the full path to the auger rates file of this element
    """
    
    # Path to the shake-up file for this element
    shakeup_file = dir_path / str(z) / (str(z) + '-shakeup.out')
    """
    Variable with the full path to the shake-up file of this element
    """
    
    # Path to the shake-up rates file for this element
    shakeuprates_file = dir_path / str(z) / (str(z) + '-shakeupinty.out')
    """
    Variable with the full path to the shake-up rates file of this element
    """
    
    # Path to the shake-off file for this element
    shakeoff_file = dir_path / str(z) / (str(z) + '-shakeoff.out')
    """
    Variable with the full path to the shake-off file of this element
    """
    
    # Path to the 1 hole ionization energies energies file for this element
    ioniz_file = dir_path / str(z) / (str(z) + '-grounddiagenergy.out')
    """
    Variable with the full path to the 1 hole ionization energies file of this element
    """
    
    # Path to the 2 hole ionization energies energies file for this element
    ioniz_file = dir_path / str(z) / (str(z) + '-groundsatenergy.out')
    """
    Variable with the full path to the 2 hole ionization energies file of this element
    """
    
    # Path to the 2 hole ionization energies energies file for this element
    ioniz_file = dir_path / str(z) / (str(z) + '-groundshakeupenergy.out')
    """
    Variable with the full path to the shake-up ionization energies file of this element
    """
    
    # Path to the diagram rates with partial widths file for this element
    radrateswidths_file = dir_path / str(z) / (str(z) + '-radrate.out')
    """
    Variable with the full path to the diagram rates with partial widths file for this element
    """
    
    # Path to the auger rates with partial widths file for this element
    augrateswidths_file = dir_path / str(z) / (str(z) + '-augerrate.out')
    """
    Variable with the full path to the auger rates with partial widths file for this element
    """
    
    # Path to the satellite rates with partial widths file for this element
    satrateswidths_file = dir_path / str(z) / (str(z) + '-satrate.out')
    """
    Variable with the full path to the satellite rates with partial widths file for this element
    """
    
    # Path to the satellite rates with partial widths file for this element
    shakeuprateswidths_file = dir_path / str(z) / (str(z) + '-shakeuprates.out')
    """
    Variable with the full path to the shake-up rates with partial widths file for this element
    """
    
    # Path to the mean radius file for this element
    meanRs_file = dir_path / str(z) / (str(z) + '-meanR.out')
    """
    Variable with the full path to the mean radius file for this element
    """
    
    
    # ------------------------------------------------- #
    #                                                   #
    #                   READ FILES                      #
    #                                                   #
    # ------------------------------------------------- #
    
    # Read the rates file
    if "rad" in filter:
        if filter["rad"]:
            generalVars.lineradrates = readRates(radrates_file)
    else:
        generalVars.lineradrates = readRates(radrates_file)
    
    
    # Read the rates file
    if "sat" in filter:
        if filter["sat"]:
            generalVars.linesatellites = readRates(satellites_file)
    else:
        generalVars.linesatellites = readRates(satellites_file)
    
    # Read the rates file
    if "aug" in filter:
        if filter["aug"]:
            generalVars.lineauger = readRates(augrates_file)
    else:
        generalVars.lineauger = readRates(augrates_file)
    
    # Read the shake-up file
    if "up" in filter:
        if filter["up"]:
            generalVars.shakeup, _ = readShake(shakeup_file)
    else:
        generalVars.shakeup, _ = readShake(shakeup_file)
    
    # Read the rates file
    if "up" in filter:
        if filter["up"]:
            generalVars.lineshakeup = readRates(shakeuprates_file)
            
            if generalVars.lineshakeup is None:
                generalVars.Shakeup_exists = False
            else:
                generalVars.Shakeup_exists = True
        else:
            generalVars.Shakeup_exists = False
    else:
        generalVars.lineshakeup = readRates(shakeuprates_file)
        
        if generalVars.lineshakeup is None:
            generalVars.Shakeup_exists = False
        else:
            generalVars.Shakeup_exists = True
    
    # Read the shake-off file
    if "sat" in filter:
        if filter["sat"]:
            generalVars.shakeoff, generalVars.label1 = readShake(shakeoff_file)
    else:
        generalVars.shakeoff, generalVars.label1 = readShake(shakeoff_file)
    
    # Read the ionization energies energies file
    if "irad" in filter:
        if filter["irad"]:
            generalVars.ionizationsrad = readIonizationEnergies(ioniz_file)
    else:
        generalVars.ionizationsrad = readIonizationEnergies(ioniz_file)
    
    # Read the ionization energies energies file
    if "isat" in filter:
        if filter["isat"]:
            generalVars.ionizationssat = readIonizationEnergies(ioniz_file)
    else:
        generalVars.ionizationssat = readIonizationEnergies(ioniz_file)
    
    # Read the ionization energies energies file
    if "iup" in filter:
        if filter["iup"]:
            generalVars.ionizationsshakeup = readIonizationEnergies(ioniz_file)
    else:
        generalVars.ionizationsshakeup = readIonizationEnergies(ioniz_file)

    # Read the diagram rates file
    if "dw" in filter:
        if filter["dw"]:
            generalVars.diagramwidths = readWidths(radrateswidths_file)
    else:
        generalVars.diagramwidths = readWidths(radrateswidths_file)
    
    # Read the auger rates file
    if "aw" in filter:
        if filter["aw"]:
            generalVars.augerwidths = readWidths(augrateswidths_file)
    else:
        generalVars.augerwidths = readWidths(augrateswidths_file)
    
    # Read the satellite rates file
    if "sw" in filter:
        if filter["sw"]:
            generalVars.satellitewidths = readWidths(satrateswidths_file)
    else:
        generalVars.satellitewidths = readWidths(satrateswidths_file)
    
    # Read the satellite rates file
    if "upw" in filter:
        if filter["upw"]:
            generalVars.shakeupwidths = readWidths(shakeuprateswidths_file)
    else:
        generalVars.shakeupwidths = readWidths(shakeuprateswidths_file)
    
    # Read the mean radius file
    if "rs" in filter:
        if filter["rs"]:
            generalVars.meanRs = readMeanR(meanRs_file)
    else:
        generalVars.meanRs = readMeanR(meanRs_file)
    
    
    return generalVars.lineradrates, generalVars.linesatellites, generalVars.lineauger, generalVars.shakeup, generalVars.lineshakeup, generalVars.Shakeup_exists, generalVars.shakeoff, generalVars.label1, generalVars.ionizationsrad, generalVars.ionizationssat, generalVars.ionizationsshakeup, generalVars.diagramwidths, generalVars.augerwidths, generalVars.satellitewidths, generalVars.shakeupwidths, generalVars.meanRs


def CleanElementsMCDFData(elements: List[tuple[int, str, str]]):
    els = [el[1] for el in elements]
    
    to_del = []
    for el in generalVars.lineradrates_quant:
        if el not in els:
            to_del.append(el)
    for el in to_del:
        del generalVars.lineradrates_quant[el]
    
    to_del = []
    for el in generalVars.linesatellites_quant:
        if el not in els:
            to_del.append(el)
    for el in to_del:
        del generalVars.linesatellites_quant[el]
    
    to_del = []
    for el in generalVars.lineshakeup_quant:
        if el not in els:
            to_del.append(el)
    for el in to_del:
        del generalVars.lineshakeup_quant[el]
    
    to_del = []
    for el in generalVars.shakeoff_quant:
        if el not in els:
            to_del.append(el)
    for el in to_del:
        del generalVars.shakeoff_quant[el]
    
    to_del = []
    for el in generalVars.shakeup_quant:
        if el not in els:
            to_del.append(el)
    for el in to_del:
        del generalVars.shakeup_quant[el]
    
    to_del = []
    for el in generalVars.Shakeup_exists_quant:
        if el not in els:
            to_del.append(el)
    for el in to_del:
        del generalVars.Shakeup_exists_quant[el]
    
    to_del = []
    for el in generalVars.label1_quant:
        if el not in els:
            to_del.append(el)
    for el in to_del:
        del generalVars.label1_quant[el]
    
    to_del = []
    for el in generalVars.ionizationsrad_quant:
        if el not in els:
            to_del.append(el)
    for el in to_del:
        del generalVars.ionizationsrad_quant[el]
    
    to_del = []
    for el in generalVars.ionizationssat_quant:
        if el not in els:
            to_del.append(el)
    for el in to_del:
        del generalVars.ionizationssat_quant[el]
    
    to_del = []
    for el in generalVars.ionizationsshakeup_quant:
        if el not in els:
            to_del.append(el)
    for el in to_del:
        del generalVars.ionizationsshakeup_quant[el]
    
    to_del = []
    for el in generalVars.diagramwidths_quant:
        if el not in els:
            to_del.append(el)
    for el in to_del:
        del generalVars.diagramwidths_quant[el]
    
    to_del = []
    for el in generalVars.satellitewidths_quant:
        if el not in els:
            to_del.append(el)
    for el in to_del:
        del generalVars.satellitewidths_quant[el]
    
    to_del = []
    for el in generalVars.shakeupwidths_quant:
        if el not in els:
            to_del.append(el)
    for el in to_del:
        del generalVars.shakeupwidths_quant[el]
    
    to_del = []
    for el in generalVars.meanRs_quant:
        if el not in els:
            to_del.append(el)
    for el in to_del:
        del generalVars.meanRs_quant[el]
    

def UpdateElementsMCDFData(dir_path: Path, elements: List[tuple[int, str, str]]):
    if generalVars.verbose >= 3:
        print(elements)
        if ' Cu ' in generalVars.lineradrates_quant:
            print([line.energy for line in generalVars.lineradrates_quant[' Cu '][:50]]) # type: ignore
    
    if generalVars.verbose >= 3:
        print(generalVars.lineradrates_quant.keys())
    
    CleanElementsMCDFData(elements)
    
    if generalVars.verbose >= 3:
        print(generalVars.lineradrates_quant.keys())
    
    for element in elements:
        element_name: str = element[1]
        """
        Variable with the element name to simulate
        """
        
        if generalVars.verbose >= 3:
            print(element_name)
        
        filter = {"rad": element_name not in generalVars.lineradrates_quant,
                  "sat": element_name not in generalVars.linesatellites_quant,
                  "aug": False,
                  "up": element_name not in generalVars.lineshakeup_quant,
                  "irad": element_name not in generalVars.ionizationsrad_quant,
                  "isat": element_name not in generalVars.ionizationssat_quant,
                  "iup": element_name not in generalVars.ionizationsshakeup_quant,
                  "dw": element_name not in generalVars.diagramwidths_quant,
                  "sw": element_name not in generalVars.satellitewidths_quant,
                  "aw": False,
                  "upw": element_name not in generalVars.shakeupwidths_quant,
                  "rs": element_name not in generalVars.meanRs_quant}
        
        if generalVars.verbose >= 3:
            print(filter)
        
        data = InitializeMCDFData(dir_path, element[:2], filter)
        
        if filter['rad']:
            generalVars.lineradrates_quant[element_name] = data[0]
        if filter['sat']:
            generalVars.linesatellites_quant[element_name] = data[1]
            generalVars.shakeoff_quant[element_name] = data[6]
            generalVars.label1_quant[element_name] = data[7]
        if filter['up']:
            generalVars.shakeup_quant[element_name] = data[3]
            generalVars.lineshakeup_quant[element_name] = data[4]
            generalVars.Shakeup_exists_quant[element_name] = data[5]
        if filter['irad']:
            generalVars.ionizationsrad_quant[element_name] = data[8]
        if filter['isat']:
            generalVars.ionizationssat_quant[element_name] = data[9]
        if filter['iup']:
            generalVars.ionizationsshakeup_quant[element_name] = data[10]
        if filter['dw']:
            generalVars.diagramwidths_quant[element_name] = data[11]
        if filter['sw']:
            generalVars.satellitewidths_quant[element_name] = data[13]
        if filter['upw']:
            generalVars.shakeupwidths_quant[element_name] = data[14]
        if filter['rs']:
            generalVars.meanRs_quant[element_name] = data[15]
    
    if generalVars.verbose >= 3:
        print([line.energy for line in generalVars.lineradrates_quant[' Cu '][:50]]) # type: ignore



def InitializeDBData(dir_path: Path, element: tuple[int, str]):
    # Retrieve the z and name of the element to simulate
    z: int = element[0]
    """
    Variable with the z value of the element to simulate
    """
    element_name: str = element[1]
    """
    Variable with the element name to simulate
    """
    
    # Path to the ELAM database file
    ELAM_file = dir_path / 'dbs' / 'ElamDB12.txt'
    """
    Variable with the full path ELAM database file
    """
    # Read the ELAM database File
    generalVars.ELAMelement = readELAMelement(ELAM_file, z)


def CheckCS(dir_path: Path, element: tuple[int, str]):
    # Retrieve the z and name of the element to simulate
    z: int = element[0]
    """
    Variable with the z value of the element to simulate
    """
    element_name: str = element[1]
    """
    Variable with the element name to simulate
    """
    
    CS_exists: bool = False
    
    if os.path.isdir(dir_path / str(z) / 'Charge_States'):
        CS_exists = True
        
        # Search for the existing radiative files inside the charge states folder
        generalVars.radiative_files = searchChargeStates(dir_path, z, '-intensity_')
        # Load the raw data from the found files and the order in which they were loaded
        generalVars.lineradrates_PCS, generalVars.lineradrates_NCS, generalVars.rad_PCS, generalVars.rad_NCS = readChargeStates(generalVars.radiative_files, dir_path, z)

        # Search for the existing auger files inside the charge states folder
        generalVars.auger_files = searchChargeStates(dir_path, z, '-augrate_')
        # Load the raw data from the found files and the order in which they were loaded
        generalVars.lineaugrates_PCS, generalVars.lineaugrates_NCS, generalVars.aug_PCS, generalVars.aug_NCS = readChargeStates(generalVars.auger_files, dir_path, z)

        # Search for the existing satellite files inside the charge states folder
        generalVars.sat_files = searchChargeStates(dir_path, z, '-satinty_')
        # Load the raw data from the found files and the order in which they were loaded
        generalVars.linesatellites_PCS, generalVars.linesatellites_NCS, generalVars.sat_PCS, generalVars.sat_NCS = readChargeStates(generalVars.sat_files, dir_path, z)


        # Check for a missmatch in the read radiative and satellite files.
        # There should be 1 satellite for each radiative file if you want to simulate a full rad + sat spectrum
        # Otherwise, if you know what you are doing just ignore the warning
        if len(generalVars.linesatellites_NCS) != len(generalVars.lineradrates_NCS) or len(generalVars.linesatellites_PCS) != len(generalVars.lineradrates_PCS):
            messagebox.showwarning("Warning", "Missmatch of radiative and satellite files for Charge State mixture: " + str(len(generalVars.lineradrates_NCS) + len(generalVars.lineradrates_PCS)) + " radiative and " + str(len(generalVars.linesatellites_NCS) + len(generalVars.linesatellites_PCS)) + " satellite files found.")

        # Path to the ion population file file for this element
        ionpop_file = dir_path / str(z) / (str(z) + '-ionpop.out')
        """
        Variable with the full path to the ion population file of this element
        """
        # Check if the ion population data exists and load it
        generalVars.Ionpop_exists, generalVars.ionpopdata = readIonPop(ionpop_file)
    
    return CS_exists


def InitializeQuantData(dir_path: Path):
    generalVars.currentSpectraList = load(set=False, title="Choose one or more Experimental Spectra to Quantify")
    generalVars.currentTubeSpectraList = load(set=False, title="Choose one or more Xray Tube Spectra to Quantify")
    generalVars.NIST_Data = readNISTXrayLines(dir_path / "dbs" / "NIST_XrayLines.txt")
    readNISTClusterLines(dir_path / "dbs" / "NIST_LineClusters.txt")
    generalVars.existingQuantConfs = loadQuantConfigs(dir_path / "quantConfigs")
    
    generalVars.existingElements = findElements(dir_path)
    
    # Code to print the generated clusters if necessary
    # with open(dir_path / "dbs" / "NIST_LineClusters.txt", "w") as clusters:
    #     for el in generalVars.NIST_ROIS:
    #         rois = "\t".join([",".join([str(r) for r in roi]) for roi in generalVars.NIST_ROIS[el]])
    #         clusters.write(f'{el}\t{rois}\n')