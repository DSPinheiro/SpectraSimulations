
[//]: # (If you want to render this markdown in your browser you can install the Markdown Preview Plus extension)

# SpectraSimulations
Latestest version of the spectra simulation program, including simulation for ionic mixtures.
WIP - Quantification of XRF spectra


## Install instructions

This package is easily installed though pip:

```
pip install SpectraSimulations
```

You may also download the github repo for this package [here](https://github.com/DSPinheiro/SpectraSimulations)
Be warned that the repository code may be broken at times due to experimental features. The pip package should always be functional.

## Simulations

In this section I will describe the predefined paths used to read each type of simulation data.
If you properly installed the package, you should have access to the command script SpectraSimulations. This will lauch the default GUI.
The program will read data from predefined paths, relative to the directory where it was lauched from.
This means you can setup your workspace where ever you would like. The data for each element is stored in a directory with the respective atomic number, which will be loaded when you select the element to simulate.
Inside each of these directories, the program looks for predefined files, namely:

<ol>
	<li>Spectrum Files
		<ul>
			<li>&lt;at>-intensity.out - intensities, energies and widths for radiative transitions produced by ionization</li>
			<li>&lt;at>-satinty.out - intensities, energies and widths for satellite (shake-off processes) transitions produced by ionization</li>
			<li>&lt;at>-augrate.out - intensities, energies and widths for auger transitions produced by ionization</li>
			<li>&lt;at>-shakeupinty.out - intensities, energies and widths for shake-up transitions produced by ionization</li>
		</ul>
	</li>
	<li>Rates Files
		<ul>
			<li>&lt;at>-radrate.out - rates, energies and widths for radiative transitions produced by ionization</li>
			<li>&lt;at>-satrate.out - rates, energies and widths for satellite transitions produced by ionization</li>
			<li>&lt;at>-augerrate.out - rates, energies and widths for auger transitions produced by ionization</li>
			<li>&lt;at>-shakeuprates.out - rates, energies and widths for shake-up transitions produced by ionization</li>
		</ul>
	</li>
	<li>Shake Process Probabilites
		<ul>
			<li>&lt;at>-shakeoff.out - labels and probabilities for the shake-off process resulting from ionization</li>
			<li>&lt;at>-shakeup.out - labels and probabilities for the shake-up process resulting from ionization</li>
		</ul>
	</li>
	<li>Level Data
		<ul>
			<li>&lt;at>-grounddiagenergy.out - formation energies and level widths for 1 hole levels</li>
			<li>&lt;at>-groundsatenergy.out - formation energies and level widths for 2 hole levels</li>
			<li>&lt;at>-groundshakeupenergy.out - formation energies and level widths for shake-up levels</li>
		</ul>
	</li>
	<li>Excitation CrossSections
		<ul>
			<li>&lt;at>-meanR.out - labels and orbital mean radius for the neutral configuration (<a href="http://dx.doi.org/10.1016/j.ijms.2011.12.003">MRBEB</a> calculations)</li>
		</ul>
	</li>
</ol>

where &lt;at> is the atomic number of the element. This is the basic data file structure. Other calculations are also implemented, namely: Charge State Mixture and Excitations.
For each of these calculations a separate subdirectory is searched inside the element's directory: "Charge_States" and "Excitations" respectively.
The file structure for each is similar, with minor modifications. For the charge states, each set of files is identified with the respective charge state, i.e.:

&lt;at>-intensity.out &rarr; &lt;at>-intensity_&lt;cs>.out

This &lt;cs> identifier also takes into account if this is a positive or negative ion, i.e. &lt;cs> = "+5" or &lt;cs> = "-5" are correct.

For the excitation calculation, each set of files is identified by the excited orbital, i.e.:

&lt;at>-intensity.out &rarr; &lt;at>-intensity_&lt;orb>.out

The &lt;orb> identifier can be any LS orbital such as &lt;orb> = "4p".

An example file "29-intensity.out" is provided with the installation in the directory "29". Further examples will be added in the next weeks.

In adition to these files, some small database files are also included in the install directory under the "dbs" directory.
If you copy this directory to your workspace they will be automatically loaded.

## Development

At the moment you can write your own script where the simulation program is initialized by importing the package:

```python
from SpectraSimulations import SpectraSimulation

if __name__ == '__main__':
    SpectraSimulation.main()
```

For now there is not much you can modify unless you directly modify the package code. Nonetheless, the core intensity calculation and data line processing can be modifyed by the used. In the script, before starting the simulation you can override the Line class:

```python
from __future__ import annotations

from typing import List, Dict

from SpectraSimulations.data.definitions import Line

import SpectraSimulations.data.variables as generalVars

class userLine(Line):
    def effectiveIntensity(self, beam: float, FWHM: float, crossSection,
                            include_cascades: bool, boost_type: str, key: str = '',
                            shake_amps: dict = {}, shakeoff_lines: List[List[str]] | None = [],
                            shakeup_lines: List[List[str]] | None = [],
                            shakeup_splines = {}, shake_missing: Dict[str, float] = {},
                            alpha: float = 1.0, exc_index: int = -1) -> float:
        
		print("Custom Effective Intensity Used...")

        from SpectraSimulations.simulation.shake import calculateTotalShake, get_shakeoff, get_shakeup
        from SpectraSimulations.simulation.shake import get_shakeoff_exc, get_shakeup_exc
        from SpectraSimulations.simulation.mults import get_overlap, get_overlap_exc
        
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
        if exc_index == -1:
            overlapMult = get_overlap(self, beamEnergy, FWHM) if beam > 0.0 else 1.0 # type: ignore
        else:
            overlapMult = get_overlap_exc(self, beamEnergy, FWHM, exc_index) if beam > 0.0 else 1.0 # type: ignore
        crossMult = crossSection[crossKey](generalVars.formationEnergies[boost_type][self.keyI()], generalVars.defaultBeam) if type(crossSection) != type(1.0) and beam <= 0.0 else crossSection
        mixMult = self.mix if hasattr(self, 'mix') else 1.0
        
        if len(generalVars.shakeoff) > 0 and len(generalVars.shakeup) > 0:
            diagramMult = (1 - calculateTotalShake(self.jji, shake_amps, shakeoff_lines, shakeup_lines)) if boost_type == 'diagram' or boost_type == 'auger' else 1.0
        else:
            diagramMult = 1.0
        
        if exc_index == -1:
            shakeoffMult = self.diagramOverlap * get_shakeoff(key, shakeoff_lines) if boost_type == 'satellite' else 1.0
            shakeupMult = self.diagramOverlap * get_shakeup(key, self.Shelli[4:], self.jji, shakeup_splines, shake_missing) if boost_type == 'shakeup' else 1.0
        else:
            shakeoffMult = self.diagramOverlap * get_shakeoff_exc(key, exc_index, shakeoff_lines) if boost_type == 'satellite' else 1.0
            shakeupMult = self.diagramOverlap * get_shakeup_exc(key, self.Shelli[4:], self.jji, exc_index, shakeup_splines, shake_missing) if boost_type == 'shakeup' else 1.0
        if len(shake_amps) > 0:
            shakeoffMod = shake_amps['shake_amp_' + key] if "shake_amp_" + key in shake_amps else 1.0 if boost_type == 'satellite' else 1.0
            shakeupMod = shake_amps['shakeup_amp_' + key] if "shakeup_amp_" + key in shake_amps else 1.0 if boost_type == 'shakeup' else 1.0
        else:
            shakeoffMod = 1.0
            shakeupMod = 1.0
        
        # Effective intensity = direct decay + cascade decay (boost mult)
        return absIntensity * \
            (crossMult * diagramMult * mixMult * overlapMult * \
            shakeoffMod * shakeoffMult * shakeupMod * shakeupMult + \
            boostMult) * \
            alpha
```

In this example the userLine class inherits the default Line class and the effectiveIntensity function is overridden. This function is called to calculate all line intensities in the simulation, for every calculation type. This way we can customize it to our needs. The code in the example is the exact same as the one used in the package. The new Line class is then passed to the simulation in the main call:

```python
SpectraSimulation.main(userLine)
```


If you would like to further understand the code and customize it, a full documentation is available [here](readthedocs).
User customization of the simulations is not fully implemented and tested. If you would like to contribute, the [github repo](https://github.com/DSPinheiro/SpectraSimulations) is ~~ir~~regularly updated.