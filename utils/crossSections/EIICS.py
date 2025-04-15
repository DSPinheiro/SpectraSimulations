"""
Module that implements the functions for calculating the Electron Impact Ionization cross section using the MRBEB formula.
"""

from __future__ import annotations


import data.variables as generalVars

import numpy as np

from typing import List


# --------------------------------------------------------- #
#                                                           #
#         ELECTRON IMPACT IONIZATION CROSS SECTION          #
#                                                           #
# --------------------------------------------------------- #


def MRBEB(C: float, B: float, impactEnergy: float):
    """
    Function to calculate the electron impact cross section using the MRBEB model
    
        Args:
            C: effective nuclear shielding factor
            B: electron binding energy for the electron to be ionized
            impactEnergy: energy of the progectile electron
        
        Returns:
            SE: electron impact cross section
    """
    bl = B/generalVars.mc2
    t = impactEnergy/B
    tl = impactEnergy/generalVars.mc2
    beta2t = 1 - 1/((1+tl)**2)
    beta2b = 1 - 1/((1+bl)**2)
    c = (C/B)*2.0*generalVars.R
    Pre = (4.0*np.pi*generalVars.a0*generalVars.a0*generalVars.Z*generalVars.alpha**4)/((beta2t + c * beta2b)*2*bl)
    SE: float = Pre * (0.5*(np.log(beta2t/(1-beta2t)) - beta2t - np.log(2*bl))*(1.0- 1.0/(t*t)) + (1.0 - 1.0/t) - (np.log(t)/(t+1.0))*((1+2*tl)/((1+tl/2)**2)) + ((bl*bl*(t-1))/(2*(1+tl/2)**2)) )
    if(impactEnergy < B):
        SE = 0.0
    return SE


def Zeff(meanR: float):
    '''
        As per the definition given by Douglas Hartree
        the effective Z of an Hartree-Fock orbital is
        the mean radius of the hydrogen orbital divided
        by the mean radius of the target orbital
        
        Args:
            meanR: mean orbital radius occupied by the electron we want to ionize
        
        Returns:
            Zeff: effective nuclear charge of the orbital
    '''
    
    return generalVars.meanHR/meanR


def C(Zeff1: float, Zeff2: float, n1: int, n2: int):
    """
    Function to calculate the effective nuclear shielding factor
        
        Args:
            Zeff1: effective nuclear charge of the orbital we want to ionize
            Zeff2: effective nuclear charge of the orbital right after the one we want to ionize
            n1: principal quantum number of the orbital we want to ionize
            n2: principal quantum number of the orbital right after the one we want to ionize
        
        Returns:
            C: the effective nuclear shielding factor
    """
    return (0.3*Zeff1**2)/(2*n1**2) + (0.7*Zeff2**2)/(2*n2**2)


def get_Zeff(label: str):
    for i, line in enumerate(generalVars.meanRs):
        if line[0] == label:
            eff = Zeff(float(line[1]))
            
            if 'K' in line[0]:
                n = 1
            elif 'L' in line[0]:
                n = 2
            elif 'M' in line[0]:
                n = 3
            elif 'N' in line[0]:
                n = 4
            else:
                n = 5
            
            return eff, n
    
    return -1, -1


def setupMRBEB(labels: List[str] | None = []):
    label1 = []
    if labels != None:
        if labels != []:
            label1 = labels
        else:
            label1 = generalVars.label1
    else:
        label1 = generalVars.label1
    
    totalMRBEB = []
    
    for i, label in enumerate(label1[:-1]):
        Zeff1, n1 = get_Zeff(label)
        Zeff2, n2 = get_Zeff(label1[i + 1])
        totalMRBEB.append(lambda b, x: MRBEB(C(Zeff1, Zeff2, n1, n2), b, x))
    
    totalMRBEB.append(totalMRBEB[-1])
    
    for i, label in enumerate(label1[:-1]):
        Zeff1, n1 = get_Zeff(label)
        Zeff2, n2 = get_Zeff(label1[i + 1])
        generalVars.elementMRBEB[label] = lambda b, x: MRBEB(C(Zeff1, Zeff2, n1, n2), b, x) / sum(totals(b, x) for totals in totalMRBEB)
    
    generalVars.elementMRBEB[label1[-1]] = generalVars.elementMRBEB[label1[-2]]

    return generalVars.elementMRBEB
