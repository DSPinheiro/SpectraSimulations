"""
Module with profile functions for line simulation.
"""

from __future__ import annotations


#Import numpy
import numpy as np

from scipy.special import wofz


from typing import List
import numpy.typing as npt

from pybaselines import Baseline

import data.variables as generalVars

from utils.crossSections.energies import ComptonEnergy

from scipy.interpolate import interp1d

from scipy.special import erf


# --------------------------------------------------------- #
#                                                           #
#            MATH FUNCTIONS FOR LINE PROFILES               #
#                                                           #
# --------------------------------------------------------- #

# Gaussian profile
def G(T: npt.NDArray[np.float64], energy: float, intens: float, res: float, width: float):
    """ 
    Function to calculate the Gaussian line shape at x with HWHM alpha
        
        Args:
            T: list of x values for which we want the y values of the profile
            energy: x value of the profile center
            intens: hight of the profile
            res: experimental resolution to be added to the profile width
            width: natural width of the transition for the profile
        
        Returns:
            y: list of y values for each of the x values in T
    """
    y: npt.NDArray[np.float64] = intens * np.sqrt(np.log(2) / np.pi) / (res + width) * np.exp(-((T - energy) / (res + width)) ** 2 * np.log(2))
    
    return y

# Lorentzian profile
def L(T: npt.NDArray[np.float64], energy: float, intens: float, res: float, width: float):
    """ 
    Function to calculate the Lorentzian line shape at x with HWHM alpha
        
        Args:
            T: list of x values for which we want the y values of the profile
            energy: x value of the profile center
            intens: hight of the profile
            res: experimental resolution to be added to the profile width
            width: natural width of the transition for the profile
        
        Returns:
            y: list of y values for each of the x values in T
    """
    y: npt.NDArray[np.float64] = intens * (0.5 * (width + res) / np.pi) / ((T - energy) ** 2 + (0.5 * (width + res)) ** 2)
    
    return y

# Voigt profile
def V(T: npt.NDArray[np.float64], energy: float, intens: float, res: float, width: float):
    """ 
    Function to calculate the Voigt line shape at x with HWHM alpha
        
        Args:
            T: list of x values for which we want the y values of the profile
            energy: x value of the profile center
            intens: hight of the profile
            res: experimental resolution to be added to the profile width
            width: natural width of the transition for the profile
        
        Returns:
            y: list of y values for each of the x values in T
    """
    sigma: float = res / np.sqrt(2 * np.log(2))
    y: npt.NDArray[np.float64] = np.real(intens * wofz(complex(T - energy, width / 2) / sigma / np.sqrt(2))) / sigma / np.sqrt(2 * np.pi)
    
    return y

def background_SNIP(xvals: List[float], yvals: List[float],
                    decreasing: bool = False, max_half_window: int = int(len(generalVars.exp_x) / 15),
                    smooth_half_window: int = 1, num_points: int = 500, newx: List[float] = []):
    
    baseline_fitter = Baseline(xvals)
    
    bkg, _ = baseline_fitter.snip(yvals, max_half_window=max_half_window, decreasing=decreasing, smooth_half_window=smooth_half_window)
    
    for i, y in enumerate(bkg):
        if y > generalVars.exp_x[i]:
            bkg[i] = generalVars.exp_x[i]
    
    baseline_interp = interp1d(xvals, bkg, 'cubic', fill_value='extrapolate') # type: ignore
    vals_interp = interp1d(xvals, yvals, 'cubic', fill_value='extrapolate') # type: ignore
    
    base = []
    
    end_x = np.linspace(min(xvals), max(xvals), num_points) if newx == [] else newx
    for x in end_x:
        val = baseline_interp(x)
        exp = vals_interp(x)
        if exp < 0.0:
            exp = 0.0
        
        if val >= 0.0 and val <= exp:
            base.append(val)
        elif val > exp:
            base.append(exp)
        else:
            base.append(0.0)
    
    return base, bkg


def Gc(dE: npt.NDArray[np.float64], gain: float, sigma: float, fg: float):
    """
    Modified Gaussian function for the Compton peak profile
    
        Args:
            dE: list of x values, subtracted from the Compton energy, for which we want the y values of the profile
            gain: hight of the profile
            sigma: experimental resolution
            fg: modifier to the gaussian width
        
        Returns:
            y: list of y values for each of the x values in dE
    """
    
    y: npt.NDArray[np.float64] = gain / (np.sqrt(np.log(2) * np.pi) * sigma * fg) * np.exp(-(1/2) * (dE / (sigma * fg)) ** 2)
    
    return y

def Tail(dE: npt.NDArray[np.float64], gain: float, sigma: float, gamma: float):
    """
    Tail function for the Compton peak profile
    
        Args:
            dE: list of x values, subtracted from the Compton energy, for which we want the y values of the profile
            gain: hight of the profile
            sigma: experimental resolution
            gamma: tail slope
        
        Returns:
            y: list of y values for each of the x values in dE
    """

    y: npt.NDArray[np.float64] = gain / (2 * gamma * sigma * np.exp(- 1 / (2 * gamma ** 2))) * \
                                np.exp(dE / (gamma * sigma)) * \
                                erf((dE / (np.sqrt(2) * sigma)) + (1 / (np.sqrt(2) * gamma)))
    
    return y


def ComptonPeak(T: npt.NDArray[np.float64], E0: float, theta: float, gain: float, sigma: float, fg: float, fa: float, fb: float, gamma_a: float, gamma_b: float):
    """
    Function for the Compton peak profile
    From: https://analyticalsciencejournals.onlinelibrary.wiley.com/doi/pdf/10.1002/xrs.628
    
        Args:
            T: list of x values for which we want the y values of the profile
            E0: incident energy to use in this compton peak
            theta: detection angle for this compton peak
            gain: hight of the profile
            sigma: experimental resolution
            fg: modifier to the gaussian width
            fa: mixture modifier to the left tail of the profile
            fb: mixture modifier to the right tail of the profile
            gamma_a: left tail slope
            gamma_b: right tail slope
        
        Returns:
            y: list of y values for each of the x values in T
    """
    
    dE: npt.NDArray[np.float64] = T - ComptonEnergy(E0, theta)
    
    total = Gc(dE, gain, sigma, fg) + fa * Tail(dE, gain, sigma, gamma_a) + fb * Tail(-dE, gain, sigma, gamma_b)
    
    return total