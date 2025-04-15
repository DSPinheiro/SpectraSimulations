"""
Headless Application entry point.
Runs the simulation program without GUI, using a dictionary for configuring the simulation
"""

import sys
import os
from pathlib import Path


from data.variables import per_table

from data.wrappers import InitializeUserDefinitions, CheckCS, CheckExcitation, InitializeMCDFData, \
                        InitializeMCDFDataExc, InitializeDBData

from interface.updaters import dict_updater

from simulation.simulation import simulate


from typing import Dict, Any


dir_path = Path(str(os.getcwd()) + '/')
"""
Full path of the directory where the program is running
"""

def startHeadless(headless_config: Dict[str, Any] = {}, userLine = None):
    """
    Function to start the simulation program in headless mode
        Args:
            headless_config: dictionary with the simulation configuration
            userLine: Line object that the user can configure to change most simulation logic (see data.definitions)
        
        Returns:
            Nothing this is just a wrapper for the simulation start
    """
    if len(headless_config) == 0:
        headless_config = {'at_num': 29,
                        'choice_var': 'Simulation',
                        'satelite_var': 'Excitation',
                        'excitation_energy': 9010.183210546724,
                        'excitation_energyFWHM': 0.2,
                        'number_points': 500,
                        'x_max': 8070,
                        'x_min': 8010,
                        'energy_offset': 0.0,
                        'sat_energy_offset': 0.0,
                        'seperate_offsets': False,
                        'shkoff_energy_offset': 0.0,
                        'shkup_energy_offset': 0.0,
                        'exp_resolution': 0.3,
                        'loadvar': 'No',
                        'effic_var': 'No',
                        'type_var': 'Lorentzian',
                        'yoffset': 0.0,
                        'transitions': ['K\u03B1\u2081', 'K\u03B1\u2082'],
                        'include_cascades': False,
                        'exc_mech_var': 'None',
                        'normalizevar': 'No',
                        'autofitvar': 'LMFit',
                        'make_grid': True,
                        'threads': 4,
                        'offset': 0,
                        }
    
    # Choose the transitions to simulate in the headless_config
    # Check the data.variables file dictionaries for the correct keys
    for transition in headless_config['transitions']:
        dict_updater(transition, headless_config['satelite_var'])
    
    atomic_num = headless_config['at_num']
    
    element = (atomic_num, str(per_table[atomic_num - 1][2]))
    # -----------------------------------------------------------------------#
    #                                                                        #
    #                   INITIALIZE USER DEFINITIONS                          #
    #                                                                        #
    #------------------------------------------------------------------------#
    
    InitializeUserDefinitions(userLine)
    
    # ----------------------------------------------------------------------------------------------#
    #                                                                                               #
    #                   INITIALIZE AND READ DATA FROM THE PREDEFINED FILES                          #
    #                                                                                               #
    #-----------------------------------------------------------------------------------------------#
    
    # Variable to activate or deactivate the charge state simulation in the interface menu
    CS_exists = CheckCS(dir_path, element, False)
    """
    Variable to control if this element has transition rates for different charge states
    """
    # Variable to activate or deactivate the excitation simulation in the interface menu
    Exc_exists = CheckExcitation(dir_path, element, False)
    """
    Variable to control if this element has transition rates for different excitations
    """
    
    InitializeMCDFData(dir_path, element, gui=False)
    InitializeMCDFDataExc(dir_path, element, gui=False)
    InitializeDBData(dir_path, element, gui=False)
    
    exc = "Excitation" in headless_config['satelite_var']
    
    if 'make_grid' in headless_config:
        if headless_config['make_grid']:
            from multiprocessing.pool import Pool
            from copy import deepcopy
            
            with Pool(headless_config['threads']) as pool:
                arg_list = []
                for i in range(headless_config['threads']):
                    new_config = deepcopy(headless_config)
                    arg_list.append((dir_path, None, None, None, exc, False, new_config))
                    arg_list[i][-1]['offset'] = i
                
                pool.starmap(simulate, arg_list)
        else:
            simulate(dir_path, None, None, None,
                    excitation = exc, quantify = False, headless_config = headless_config)
    else:
        simulate(dir_path, None, None, None,
                    excitation = exc, quantify = False, headless_config = headless_config)


if __name__ == "__main__":
    startHeadless()