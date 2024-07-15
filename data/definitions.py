"""
Module with classes that are used in the simulation and data processing
"""

# --------------------------------------------------------- #
#                                                           #
#        OBJECT DEFENITIONS TO USE IN THE SIMULATION        #
#                                                           #
# --------------------------------------------------------- #

from __future__ import annotations


import data.variables as generalVars


from typing import List, Dict


class Line():
    """
    Class to hold the lines read from file
    """
    def __init__(self, Num: int = 0, Shelli: str = '', jji: int = 0, eigvi: int = 0,
                 Shellf: str = '', jjf: int = 0, eigvf: int = 0,
                 energy: float = 0.0, br: float = 0.0, levelRadYield: float = 0.0,
                 intensity: float = 0.0, weight: float = 0.0, radWidth: float = 0.0,
                 augWidth: float = 0.0, totalWidth: float = 0.0, line: str = ''):
        if line == '':
            self.Num = Num
            self.Shelli = Shelli
            self.jji = jji
            self.eigvi = eigvi
            self.Shellf = Shellf
            self.jjf = jjf
            self.eigvf = eigvf
            self.energy = energy
            self.br = br
            self.levelRadYield = levelRadYield
            self.intensity = intensity
            self.weight = weight
            self.radWidth = radWidth
            self.augWidth = augWidth
            self.totalWidth = totalWidth
        else:
            vals = line.strip().split()
            if len(vals) == 16:
                self.Num = int(vals[0])
                self.Shelli = vals[1].strip()
                self.jji = int(vals[2])
                self.eigvi = int(vals[3])
                self.Shellf = vals[5].strip()
                self.jjf = int(vals[6])
                self.eigvf = int(vals[7])
                self.energy = float(vals[8])
                self.br = float(vals[9])
                self.levelRadYield = float(vals[10])
                self.intensity = float(vals[11])
                self.weight = float(vals[12])
                self.radWidth = float(vals[13])
                self.augWidth = float(vals[14])
                self.totalWidth = float(vals[15])
            elif len(vals) == 11:
                self.Num = int(vals[0])
                self.Shelli = vals[1].strip()
                self.jji = int(vals[2])
                self.eigvi = int(vals[3])
                try:
                    self.eigvf = int(vals[7])
                    self.Shellf = vals[5].strip()
                    self.jjf = int(vals[6])
                    self.energy = float(vals[8])
                    self.intensity = float(vals[9])
                    self.totalWidth = float(vals[10])
                except:
                    self.convOverlap = [vals[7].split(">")[0] + ">", float(vals[7].split(">")[1])]
                    self.percent = float(vals[8])
                    self.acc = float(vals[9])
                    self.diff = float(vals[10])
            elif len(vals) == 12:
                self.Num = int(vals[0])
                self.Shelli = vals[1]
                self.jji = int(vals[2])
                self.eigvi = int(vals[3])
                self.energy = float(vals[4])
                self.gEnergy = float(vals[5])
                self.totalWidth = float(vals[6])
                self.br = float(vals[7])
                self.convOverlap = [vals[8].split(">")[0] + ">", float(vals[8].split(">")[1])]
                self.percent = float(vals[9])
                self.acc = float(vals[10])
                self.diff = float(vals[11])
            elif len(vals) == 7 or len(vals) == 8:
                self.Num = int(vals[0])
                self.Shelli = vals[1]
                self.jji = int(vals[2])
                self.eigvi = int(vals[3])
                self.energy = float(vals[4])
                self.gEnergy = float(vals[5])
                self.totalWidth = float(vals[6])
                if len(vals) == 8:
                    self.br = float(vals[7])
            else:
                print(vals)
                raise RuntimeError("Error reading line from file. Unexpected format with " + str(len(vals) - (len(vals) >= 11)) + " values to process")

    
    def setOverlap(self, overlap: float):
        self.overlap = overlap
        
        return self
    
    def setDiagramOverlap(self, overlap: float):
        self.diagramOverlap = overlap
        
        return self
    
    def setMixValue(self, mix: float):
        self.mix = mix
        
        return self

    def filterLevel(self, low_level: str, high_level: str, auger_level: str = '', *, strict: str) -> bool:
        if auger_level == '':
            if strict != 'h' and strict != 'l' and strict != 'hl' and strict != 'na' and strict != 'hia':
                raise RuntimeError("Error: Wrong parameters passed to filterLevel function of Line (Radiative).")
        else:
            if strict != 'h' and strict != 'l' and strict != 'hl' and strict != 'na' and strict != 'ha' and strict != 'la' and strict != 'hla' and strict != 'hia':
                raise RuntimeError("Error: Wrong parameters passed to filterLevel function of Line (Auger).")
        
        if self.energy == 0:
            return False
        
        if strict == 'h':
            if auger_level == '':
                return (self.Shelli in low_level or low_level in self.Shelli) and self.Shellf == high_level
            else:
                return (self.Shelli in low_level or low_level in self.Shelli) and self.Shellf[:2] == high_level and (self.Shellf[2:4] in auger_level or auger_level in self.Shellf[2:4])
        elif strict == 'hia':
            if auger_level == '':
                return (self.Shelli in low_level or low_level in self.Shelli) and (self.Shellf[:2] == high_level)
            else:
                return (self.Shelli in low_level or low_level in self.Shelli) and (self.Shellf[:2] == high_level) and (self.Shellf[2:4] in auger_level or auger_level in self.Shellf[2:4])
        elif strict == 'l':
            if auger_level == '':
                return self.Shelli == low_level and (self.Shellf in high_level or high_level in self.Shellf)
            else:
                return self.Shelli == low_level and (self.Shellf[:2] in high_level or high_level in self.Shellf[:2]) and (self.Shellf[2:4] in auger_level or auger_level in self.Shellf[2:4])
        elif strict == 'hl':
            if auger_level == '':
                return self.Shelli == low_level and self.Shellf == high_level
            else:
                return self.Shelli == low_level and self.Shellf[:2] == high_level and (self.Shellf[2:4] in auger_level or auger_level in self.Shellf[2:4])
        elif strict == 'na':
            if auger_level == '':
                return (self.Shelli in low_level or low_level in self.Shelli) and (self.Shellf in high_level or high_level in self.Shellf)
            else:
                return (self.Shelli in low_level or low_level in self.Shelli) and (self.Shellf[:2] in high_level or high_level in self.Shellf[:2]) and (self.Shellf[2:4] in auger_level or auger_level in self.Shellf[2:4])
        elif strict == 'ha':
            return (self.Shelli in low_level or low_level in self.Shelli) and self.Shellf[:2] == high_level and self.Shellf[2:4] == auger_level
        elif strict == 'la':
            return self.Shelli == low_level and (self.Shellf[:2] in high_level or high_level in self.Shellf[:2]) and self.Shellf[2:4] == auger_level
        elif strict == 'hla':
            return self.Shelli == low_level and self.Shellf[:2] == high_level and self.Shellf[2:4] == auger_level
    
    def filterJJI(self) -> bool:
        return self.jji in generalVars.jj_vals
    
    def filterInitialState(self, *args) -> bool:
        if len(args) == 1:
            if isinstance(args[0], list) or isinstance(args[0], tuple):
                if len(args[0]) == 3:
                    return self.Shelli == args[0][0] and self.jji == args[0][1] and self.eigvi == args[0][2]
            elif isinstance(args[0], Line):
                return self.Shelli == args[0].Shelli and self.jji == args[0].jji and self.eigvi == args[0].eigvi
        elif len(args) == 3:
            return self.Shelli == args[0] and self.jji == args[1] and self.eigvi == args[2]
        
        print("Warning: bad arguments at initial state match: " + self.Shelli + ", " + str(self.jji) + ", " + str(self.eigvi))
        print("With arguments: " + str(args))
        return False
    
    def filterFinalState(self, *args) -> bool:
        if len(args) == 1:
            if isinstance(args[0], list) or isinstance(args[0], tuple):
                if len(args[0]) == 3:
                    return self.Shellf == args[0][0] and self.jjf == args[0][1] and self.eigvf == args[0][2]
            elif isinstance(args[0], Line):
                try:
                    return self.Shellf == args[0].Shellf and self.jjf == args[0].jjf and self.eigvf == args[0].eigvf
                except AttributeError:
                    return self.Shellf == args[0].Shelli and self.jjf == args[0].jji and self.eigvf == args[0].eigvi
        elif len(args) == 3:
            return self.Shellf == args[0] and self.jjf == args[1] and self.eigvf == args[2]
        
        print("Warning: bad arguments at final state match: " + self.Shellf + ", " + str(self.jjf) + ", " + str(self.eigvf))
        print("With arguments: " + str(args))
        return False
    
    def labelI(self):
        return self.Shelli + " " + str(self.jji) + " " + str(self.eigvi)
    
    def labelF(self):
        return self.Shellf + " " + str(self.jjf) + " " + str(self.eigvf)
    
    def key(self):
        return self.labelI() + "->" + self.labelF()

    def keyI(self):
        return self.Shelli + "_" + str(self.jji) + "_" + str(self.eigvi)
    
    def keyF(self):
        return self.Shellf + "_" + str(self.jjf) + "_" + str(self.eigvf)
    
    def match(self, other):
        if hasattr(self, 'Shellf') and hasattr(other, 'Shellf'):
            if self.Shelli == other.Shelli and self.jji == other.jji and self.eigvi == other.eigvi \
               and self.Shellf == other.Shellf and self.jjf == other.jjf and self.eigvf == other.eigvf :
                return True
        elif hasattr(self, 'Shellf') and not hasattr(other, 'Shellf') or not hasattr(self, 'Shellf') and hasattr(other, 'Shellf'):
            return False
        else:
            if self.Shelli == other.Shelli and self.jji == other.jji and self.eigvi == other.eigvi:
                return True
    
    def effectiveIntensity(self, beam: float, FWHM: float, crossSection,
                           include_cascades: bool, boost_type: str, key: str = '',
                           shake_amps: dict = {}, shakeoff_lines: List[List[str]] | None = [],
                           shakeup_lines: List[List[str]] | None = [],
                           shakeup_splines = {}, shake_missing: Dict[str, float] = {},
                           alpha: float = 1.0) -> float:
        from simulation.shake import calculateTotalShake, get_shakeoff, get_shakeup
        from simulation.mults import get_overlap
        
        if boost_type == 'diagram':
            boostDict = generalVars.radBoostMatrixDict
        elif boost_type == 'auger':
            boostDict = generalVars.augBoostMatrixDict
        elif boost_type == 'satellite':
            boostDict = generalVars.satBoostMatrixDict
        elif boost_type == 'shakeup':
            boostDict = generalVars.satBoostMatrixDict #temp solution
        else:
            print("Error on selected boost type for effective intensity calculation: " + boost_type)
            raise RuntimeError("Available boost types as diagram, auger and satellite")
        
        crossKey = self.Shelli if key == '' else key
        
        beamEnergy = beam if beam > 0.0 else generalVars.defaultBeam
        
        absIntensity = self.intensity
        boostMult = boostDict[self.key()] if include_cascades and self.key() in boostDict else 0.0
        overlapMult = get_overlap(self, beamEnergy, FWHM) if beam > 0.0 else 1.0
        crossMult = crossSection[crossKey](generalVars.formationEnergies[boost_type][self.keyI()], generalVars.defaultBeam) if type(crossSection) != type(1.0) and beam <= 0.0 else crossSection
        mixMult = self.mix if hasattr(self, 'mix') else 1.0
        diagramMult = (1 - calculateTotalShake(self.jji, shake_amps, shakeoff_lines, shakeup_lines)) if boost_type == 'diagram' or boost_type == 'auger' else 1.0
        shakeoffMult = self.diagramOverlap * get_shakeoff(key, shakeoff_lines) if boost_type == 'satellite' else 1.0
        shakeupMult = self.diagramOverlap * get_shakeup(key, self.Shelli[4:], self.jji, shakeup_splines, shake_missing) if boost_type == 'shakeup' else 1.0
        if len(shake_amps) > 0:
            shakeoffMod = shake_amps['shake_amp_' + key] if "shake_amp_" + key in shake_amps else 1.0 if boost_type == 'satellite' else 1.0
            shakeupMod = shake_amps['shakeup_amp_' + key] if "shakeup_amp_" + key in shake_amps else 1.0 if boost_type == 'shakeup' else 1.0
        else:
            shakeoffMod = 1.0
            shakeupMod = 1.0
        
        # if boost_type == 'satellite':
        #     generalVars.control_shakeoff[key] = get_shakeoff(key)
        # if boost_type == 'shakeup':
        #     generalVars.control_shakeup[key + "_" + str(self.jji) + "_" + self.Shelli[4:-1]] = get_shakeup(key, self.Shelli[4:], self.jji)
        
        # if boost_type == 'shakeup' and shakeupMult > 0.0:# and 'M2' in self.Shelli:
        #     with open("shakeup_debug.txt", "a") as f:
        #         f.write(self.key() + ": " + str(absIntensity) + ', ' + \
        #         str(crossMult) + ', ' + \
        #         str(boostMult) + ', ' + \
        #         str(diagramMult) + ', ' + \
        #         str(mixMult) + ', ' + \
        #         str(overlapMult) + ', ' + \
        #         str(shakeoffMult) + ', ' + \
        #         str(shakeupMult) + "\n")
        
        # Effective intensity = direct decay + cascade decay (boost mult)
        return absIntensity * \
            (crossMult * diagramMult * mixMult * overlapMult * \
            shakeoffMod * shakeoffMult * shakeupMod * shakeupMult + \
            boostMult) * \
            alpha