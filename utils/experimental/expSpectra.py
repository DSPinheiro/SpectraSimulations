"""
Module with functions to setup the experimental spectra for the simulation
"""

import data.variables as generalVars

from typing import List
import numpy as np

# --------------------------------------------------------- #
#                                                           #
#    FUNCTIONS TO USE AND CONFIGURE EXPERIMENTAL SPECTRA    #
#                                                           #
# --------------------------------------------------------- #

# Extract x, y and sigma values from the read experimental file
def extractExpVals(exp_spectrum: List[List[str]]):
    """
    Function to extract x, y and sigma values from the read experimental file
        
        Args:
            exp_spectrum: list with the experimental spectrum to be handled
        
        Returns:
            xe: energy values of the experimental spectrum
            ye: intensity values of the experimental spectrum
            sigma_exp: error values of the experimental spectrum (sqrt(intensity) by default if no data is provided)
    """
    # for i, it in enumerate(exp_spectrum):
    #     # Convert the loaded values to float. Update this to a map function?
    #     for j, itm in enumerate(exp_spectrum[i]):
    #         if exp_spectrum[i][j] != '':
    #             exp_spectrum[i][j] = float(itm)
    
    # Split the values into x and y
    xe = [float(row[0]) for row in exp_spectrum]
    ye = [float(row[1]) for row in exp_spectrum]
    
    # If the spectrum has 3 columns of data then use the third column as the uncertainty
    if len(exp_spectrum[0]) >= 3:
        sigma_exp = [float(row[2]) for row in exp_spectrum]
    else:
        # Otherwise use the sqrt of the count number
        sigma_exp = list(np.sqrt(ye))
    
    if xe != list(set(xe)):
        if generalVars.verbose >= 2:
            print("Detected duplicate x values in the experimental spectrum. Removing them to work with interpolation algorithms...")
        
        to_del = []
        to_del_vals = []
        for i, x in enumerate(xe):
            if list(xe).count(x) > 1 and x not in to_del_vals:
                to_del.append(i)
                to_del_vals.append(x)
        
        deleted = 0
        for i in to_del:
            del xe[i - deleted]
            del ye[i - deleted]
            del sigma_exp[i - deleted]
            deleted += 1
    
    # Make sure the spectrum data is sorted in ascending order
    tmp = list(zip(xe, ye, sigma_exp))
    tmp.sort(key=lambda x: x[0])
    
    xe = np.array([x for x, y, e in tmp])
    ye = np.array([y for x, y, e in tmp])
    sigma_exp = np.array([e for x, y, e in tmp])
    
    
    return xe, ye, sigma_exp


