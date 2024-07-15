"""
Module with functions that initialize general list and objects required in the simulation.
"""

from data.variables import the_dictionary, the_aug_dictionary
import data.variables as generalVars
import interface.variables as guiVars

from typing import List


# ---------------------------------------------------------------------- #
#                                                                        #
#            FUNCTIONS TO PREPARE INITIALIZE SIMULATION LISTS            #
#                                                                        #
# ---------------------------------------------------------------------- #


def initialize_XYW(type_simu: str, ploted_cs: List[str] = []):
    """
    Function to initialize the lists that hold the data for all transitions to be simulated.
    
        Args:
            type_simu: type of lists to initialize depending of the simulation
            ploted_cs: list of the charge states to be ploted in this simulation
        
        Returns:
            x: energy values for each of the possible radiative transitions
            y: intensity values for each of the possible radiative transitions
            w: natural width values for each of the possible radiative transitions
            xs: energy values for each of the possible radiative satellite transitions
            ys: intensity values for each of the possible radiative satellite transitions
            ws: natural width values for each of the possible radiative satellite transitions
    """
    
    if 'Radiative' in type_simu:
        trans_dict = the_dictionary
    else:
        trans_dict = the_aug_dictionary
    
    if 'CS' in type_simu:
        cs_mult = len(ploted_cs)
    else:
        cs_mult = 1
    
    if 'Quant' in type_simu:
        element_count = len(guiVars.elementList)
    else:
        element_count = 1
    
    x: List[List[float]] = [[] for _ in range(len(trans_dict) * cs_mult * element_count)]
    y: List[List[float]] = [[] for _ in range(len(trans_dict) * cs_mult * element_count)]
    w: List[List[float]] = [[] for _ in range(len(trans_dict) * cs_mult * element_count)]
    
    xs: List[List[List[float]]] = []
    for _ in x:
        xs.append([])
        for _ in generalVars.label1:
            xs[-1].append([])
            xs[-1].append([])
    
    ys: List[List[List[float]]] = []
    for _ in y:
        ys.append([])
        for _ in generalVars.label1:
            ys[-1].append([])
            ys[-1].append([])
    
    ws: List[List[List[float]]] = []
    for _ in w:
        ws.append([])
        for _ in generalVars.label1:
            ws[-1].append([])
            ws[-1].append([])
    
    return x, y, w, xs, ys, ws
    
