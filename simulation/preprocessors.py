from __future__ import annotations

import interface.variables as guiVars
import data.variables as generalVars

from simulation.diagram import simu_diagram
from simulation.auger import simu_auger
from simulation.satellite import simu_sattelite

from simulation.initializers import initialize_XYW

from simulation.lineUpdater import updateRadTransitionVals, updateAugTransitionVals,\
                                    updateRadCSTrantitionsVals, updateAugCSTransitionsVals,\
                                    updateRadExcitationVals

from utils.misc.badReporters import simu_check_bads, simu_quantify_check_bads, Msimu_check_bads, report_MbadSelection

#Cross section functions import
from utils.crossSections.EIICS import setupMRBEB
from utils.crossSections.PhotoCS import setupELAMPhotoIoniz
from utils.crossSections.energies import setupFormationEnergies, setupPartialWidths
from utils.crossSections.energies import setupFormationEnergiesExc, setupPartialWidthsExc

#Shake values setup
from simulation.shake import setupShake, setupShakeExc

#Excitation yield ratios (from decays)
from simulation.mults import setupExcitationYields

from typing import List, Dict, Any


def process_ionization_shake_data(excitation: bool, quantify: bool):
    if not quantify:
        if generalVars.meanR_exists:
            setupMRBEB()
        if generalVars.ELAM_exists:
            setupELAMPhotoIoniz()

        if generalVars.shakeoff[0] != [''] and generalVars.shakeup[0] != ['']:
            setupShake()
        else:
            print("Skipping shake setup as no shake lines were read.")
        
        if len(generalVars.ionizationsrad) > 0 or len(generalVars.ionizationssat) > 0:
            setupFormationEnergies()
            setupPartialWidths()
        else:
            print("Skipping level data setup as no ground energy file was read.")

        if excitation:
            setupShakeExc()
            
            setupFormationEnergiesExc()
            setupPartialWidthsExc()
            
            setupExcitationYields()
    else:
        for element in guiVars.elementList:
            if element[1] in generalVars.meanR_exists_quant:
                if generalVars.meanR_exists_quant[element[1]]:
                    generalVars.elementMRBEB_quant[element[1]] = setupMRBEB(generalVars.label1_quant[element[1]])
            if generalVars.ELAM_exists:
                generalVars.ELAMPhotoSpline_quant[element[1]] = setupELAMPhotoIoniz(generalVars.ELAMelement_quant[element[1]])


            generalVars.shakeUPSplines_quant[element[1]], \
            generalVars.missing_shakeup_quant[element[1]], \
            generalVars.shake_relations_quant[element[1]], \
            generalVars.missing_shakeoff_quant[element[1]], \
            generalVars.shake_relations_quant[element[1]], \
            generalVars.shake_relations_quant[element[1]] = \
            setupShake(generalVars.linesatellites_quant[element[1]],
                       generalVars.lineshakeup_quant[element[1]],
                       generalVars.shakeoff_quant[element[1]],
                       generalVars.shakeup_quant[element[1]],
                       generalVars.label1_quant[element[1]],
                       generalVars.Shakeup_exists_quant[element[1]])
            
            generalVars.formationEnergies_quant[element[1]] = \
                setupFormationEnergies(generalVars.ionizationsrad_quant[element[1]],
                                        generalVars.ionizationssat_quant[element[1]],
                                        generalVars.ionizationsshakeup_quant[element[1]])
            generalVars.partialWidths_quant[element[1]] = \
                setupPartialWidths(generalVars.ionizationsrad_quant[element[1]],
                                    generalVars.ionizationssat_quant[element[1]],
                                    generalVars.ionizationsshakeup_quant[element[1]])


def process_simulation(shake_amps: dict = {}, prompt: bool = True,
                       headless_config: Dict[str, Any] = {}):
    if len(headless_config) == 0:
        sat: str = guiVars.satelite_var.get() # type: ignore
        beam: float = guiVars.excitation_energy.get() # type: ignore
        FWHM: float = guiVars.excitation_energyFWHM.get() # type: ignore
    else:
        if 'satelite_var' in headless_config:
            sat: str = headless_config['satelite_var']
        else:
            print("Error: No transition type chosen.")
            print("Please define the value for the satelite_var in the headless_config dictionary.")
            print("Stopping....")
            exit(-1)
        
        if 'excitation_energy' in headless_config:
            beam: float = headless_config['excitation_energy']
        else:
            print("Error: No excitation energy chosen.")
            print("Please define the value for the excitation_energy in the headless_config dictionary.")
            print("Stopping....")
            exit(-1)
        
        if 'excitation_energyFWHM' in headless_config:
            FWHM: float = headless_config['excitation_energyFWHM']
        else:
            print("Error: No FWHM chosen for the excitation energy beam.")
            print("Please define the value for the excitation_energyFWHM in the headless_config dictionary.")
            print("Stopping....")
            exit(-1)
    
    # Initialize the x, y and w arrays for both the non satellites and satellites (xs, ys, ws) transitions
    x, y, w, xs, ys, ws = initialize_XYW('Radiative')
    # Initialize the x, y and w arrays for both the non satellites and satellites (xs, ys, ws) transitions
    xe, ye, we, xse, yse, wse = initialize_XYW('Excitation', generalVars.rad_EXC)
    
    bad_selection = 0
    bad_selection_e = 0
    
    
    include_cascades: bool | None = None
    exc_mech_var: str = ''
    
    if len(headless_config) > 0:
        if 'include_cascades' in headless_config:
            include_cascades=headless_config['include_cascades']
        else:
            print("Error: No flag chosen for including cascades in the simulation.")
            print("Please define the value for the include_cascades in the headless_config dictionary.")
            print("Stopping....")
            exit(-1)
        if 'exc_mech_var' in headless_config:
            exc_mech_var=headless_config['exc_mech_var']
        else:
            print("Error: No excitation mechanism chosen for the simulation.")
            print("Please define the value for the exc_mech_var in the headless_config dictionary (available: 'EII', 'PIon', 'None').")
            print("Stopping....")
            exit(-1)
    
    # Radiative and Auger code has to be split due to the different dictionaries used for the transitions
    if sat != 'Auger':
        if 'Diagram' in sat or 'Satellites' in sat:
            # Read the selected transitions
            # In this case we first store all the values for the transitions and then we calculate the y values to be plotted according to a profile
            for index, transition in enumerate(generalVars.the_dictionary):
                if generalVars.the_dictionary[transition]["selected_state"]:
                    # Same filter as the sticks but we dont keep track of the number of selected transitions
                    _, low_level, high_level, diag_sim_val, sat_sim_val = updateRadTransitionVals(transition, 0, beam, FWHM)
                    
                    if 'Diagram' in sat:
                        # Store the values in a list containing all the transitions to simulate
                        x[index], y[index], w[index] = simu_diagram(diag_sim_val, beam, FWHM, shake_amps,
                                                                    include_cascades=include_cascades,
                                                                    exc_mech_var=exc_mech_var)
                    if 'Satellites' in sat:
                        # Store the values in a list containing all the transitions to simulate
                        xs[index], ys[index], ws[index] = simu_sattelite(sat_sim_val, low_level, high_level, beam, FWHM, shake_amps,
                                                                    include_cascades=include_cascades,
                                                                    exc_mech_var=exc_mech_var)
            
            # -------------------------------------------------------------------------------------------
            # Check if there are any transitions with missing rates
            bad_selection, bads = simu_check_bads(x, xs, True, prompt)
            for index in bads:
                x[index] = []
        if 'Excitation' in sat or 'ESat' in sat:
            bad_lines = {}

            # Loop the existing excitations
            for exc_index, exc in enumerate(generalVars.rad_EXC):
                # -------------------------------------------------------------------------------------------
                # Read the selected transitions
                # In this case we first store all the values for the transitions and then we calculate the y values to be plotted according to a profile
                for index, transition in enumerate(generalVars.the_dictionary):
                    if generalVars.the_dictionary[transition]["selected_state"]:
                        # Same as sticks but we dont care about the number of transitions
                        _, low_level, high_level, diag_sim_val, sat_sim_val = updateRadExcitationVals(transition, 0, beam, FWHM, exc_index, exc)
                        
                        if 'Excitation' in sat:
                            # Store the values in a list containing all the transitions and charge states to simulate
                            xe[exc_index * len(generalVars.the_dictionary) + index], ye[exc_index * len(generalVars.the_dictionary) + index], we[exc_index * len(generalVars.the_dictionary) + index] = simu_diagram(diag_sim_val, beam, FWHM, shake_amps, exc_index=exc_index,
                                                                                                                                                                                                                     include_cascades=include_cascades,
                                                                                                                                                                                                                     exc_mech_var=exc_mech_var)
                        if 'ESat' in sat:
                            # Store the values in a list containing all the charge states and transitions to simulate
                            xse[exc_index * len(generalVars.the_dictionary) + index], yse[exc_index * len(generalVars.the_dictionary) + index], wse[exc_index * len(generalVars.the_dictionary) + index] = simu_sattelite(sat_sim_val, low_level, high_level, beam, FWHM, shake_amps, exc_index=exc_index,
                                                                                                                                                                                                                            include_cascades=include_cascades,
                                                                                                                                                                                                                            exc_mech_var=exc_mech_var)
                # -------------------------------------------------------------------------------------------
                # Check if there are any transitions with missing rates
                bad_selection_e, bad_lines_e = Msimu_check_bads(exc_index, exc, xe, xse, True)
            if prompt:
                report_MbadSelection(bad_lines, generalVars.rad_EXC)
    else:
        # Initialize the x, y and w arrays for both the non satellites and satellites (xs, ys, ws) transitions
        x, y, w, xs, ys, ws = initialize_XYW('Auger')
        
        # Loop possible auger transitions
        for index, transition in enumerate(generalVars.the_aug_dictionary):
            if generalVars.the_aug_dictionary[transition]["selected_state"]:
                # Same as the stick but we dont care about the number of transitions
                _, aug_stick_val = updateAugTransitionVals(transition, 0)
                
                # Store the values in a list containing all the transitions to simulate
                x[index], y[index], w[index] = simu_auger(aug_stick_val, beam, FWHM, shake_amps)

        # -------------------------------------------------------------------------------------------
        # Check if there are any transitions with missing rates
        bad_selection, bads = simu_check_bads(x, xs, False, prompt)
        for index in bads:
            x[index] = []
    
    return x, y, w, xs, ys, ws, bad_selection, xe, ye, we, xse, yse, wse, bad_selection_e


def process_quantify_simu(shake_amps: dict = {}, prompt: bool = True):
    sat: str = guiVars.satelite_var.get() # type: ignore
    beam: float = guiVars.excitation_energy.get() # type: ignore
    FWHM: float = guiVars.excitation_energyFWHM.get() # type: ignore
    
    # Initialize the x, y and w arrays for both the non satellites and satellites (xs, ys, ws) transitions
    x, y, w, xs, ys, ws = initialize_XYW('Radiative Quant')
    
    for el_idx, element in enumerate(guiVars.elementList):
        if generalVars.verbose >= 3:
            print(element)
        
        # Read the selected transitions
        # In this case we first store all the values for the transitions and then we calculate the y values to be plotted according to a profile
        for index, transition in enumerate(generalVars.the_dictionary):
            if generalVars.the_dictionary[transition]["selected_state"]:
                if generalVars.verbose >= 3:
                    print([line.energy for line in generalVars.lineradrates_quant[element[1]][:50]]) # type: ignore
                
                # Same filter as the sticks but we dont keep track of the number of selected transitions
                _, low_level, high_level, diag_sim_val, sat_sim_val = \
                    updateRadTransitionVals(transition, 0, beam, FWHM,
                                            linelist=generalVars.lineradrates_quant[element[1]],
                                            linelist_sat=generalVars.linesatellites_quant[element[1]],
                                            linelist_up=generalVars.lineshakeup_quant[element[1]])
                
                if 'Diagram' in sat:
                    # Store the values in a list containing all the transitions to simulate
                    x[el_idx * len(generalVars.the_dictionary) + index], y[el_idx * len(generalVars.the_dictionary) + index], w[el_idx * len(generalVars.the_dictionary) + index] = simu_diagram(diag_sim_val, beam, FWHM, shake_amps, element[1])
                if 'Satellites' in sat:
                    # Store the values in a list containing all the transitions to simulate
                    xs[el_idx * len(generalVars.the_dictionary) + index], ys[el_idx * len(generalVars.the_dictionary) + index], ws[el_idx * len(generalVars.the_dictionary) + index] = simu_sattelite(sat_sim_val, low_level, high_level, beam, FWHM, shake_amps, element[1])
        
        # -------------------------------------------------------------------------------------------
        # Check if there are any transitions with missing rates
        bad_selection, bads = simu_quantify_check_bads(el_idx, element[1], x, xs, True, prompt)
        for index in bads:
            x[index] = []
    
    return x, y, w, xs, ys, ws, bad_selection


def process_Msimulation(shake_amps: dict = {}, prompt: bool = True):
    sat = guiVars.satelite_var.get() # type: ignore
    beam = guiVars.excitation_energy.get() # type: ignore
    FWHM = guiVars.excitation_energyFWHM.get() # type: ignore
    
    bad_selection = 0
    
    # Radiative and Auger code has to be split due to the different dictionaries used for the transitions
    if sat != 'Auger':
        # Initialize the charge states we have to loop through
        charge_states: List[str] = generalVars.rad_PCS + generalVars.rad_NCS

        # Before plotting we filter the charge state that need to be plotted (mix_val != 0)
        # And store the charge state values in this list
        ploted_cs: List[str] = []
        # Also store if the charge state is positive or negative
        cs_type: List[bool] = []

        # Loop the charge states
        for cs_index, cs in enumerate(charge_states):
            # Initialize the mixture value chosen for this charge state
            mix_val = '0.0'
            # Flag to check if this is a negative or positive charge state
            ncs = False

            # Check if this charge state is positive or negative and get the mix value
            if cs_index < len(generalVars.rad_PCS):
                mix_val = guiVars.PCS_radMixValues[cs_index].get()
            else:
                mix_val = guiVars.NCS_radMixValues[cs_index - len(generalVars.rad_PCS)].get()
                ncs = True

            # Check if the mix value is not 0, otherwise no need to plot the transitions for this charge state
            if mix_val != '0.0':
                ploted_cs.append(cs)
                cs_type.append(ncs)

        # Initialize the x, y and w arrays, taking into account the number of charge states to plot, for both the non satellites and satellites (xs, ys, ws) transitions
        x, y, w, xs, ys, ws = initialize_XYW('Radiative_CS', ploted_cs)


        bad_lines = {}
        
        # Loop the charge states to plot
        for cs_index, cs in enumerate(ploted_cs):
            # -------------------------------------------------------------------------------------------
            # Read the selected transitions
            # In this case we first store all the values for the transitions and then we calculate the y values to be plotted according to a profile
            for index, transition in enumerate(generalVars.the_dictionary):
                if generalVars.the_dictionary[transition]["selected_state"]:
                    # Same as sticks but we dont care about the number of transitions
                    _, low_level, high_level, diag_sim_val, sat_sim_val = updateRadCSTrantitionsVals(transition, 0, cs_type[cs_index], cs)
                    
                    if 'Diagram' in sat:
                        # Store the values in a list containing all the transitions and charge states to simulate
                        x[cs_index * len(generalVars.the_dictionary) + index], y[cs_index * len(generalVars.the_dictionary) + index], w[cs_index * len(generalVars.the_dictionary) + index] = simu_diagram(diag_sim_val, beam, FWHM, shake_amps)
                    if 'Satellites' in sat:
                        # Store the values in a list containing all the charge states and transitions to simulate
                        xs[cs_index * len(generalVars.the_dictionary) + index], ys[cs_index * len(generalVars.the_dictionary) + index], ws[cs_index * len(generalVars.the_dictionary) + index] = simu_sattelite(sat_sim_val, low_level, high_level, beam, FWHM, shake_amps)

            # -------------------------------------------------------------------------------------------
            # Check if there are any transitions with missing rates
            bad_selection, bad_lines = Msimu_check_bads(cs_index, cs, x, xs, True)
        
        if prompt:
            report_MbadSelection(bad_lines, ploted_cs)
    else:
        # Initialize the charge states we have to loop through
        charge_states = generalVars.aug_PCS + generalVars.aug_NCS

        # Before plotting we filter the charge state that need to be plotted (mix_val != 0)
        # And store the charge state values in this list
        ploted_cs = []
        # Also store if the charge state is positive or negative
        cs_type = []

        # Loop the charge states
        for cs_index, cs in enumerate(charge_states):
            # Initialize the mixture value chosen for this charge state
            mix_val = '0.0'
            # Flag to check if this is a negative or positive charge state
            ncs = False

            # Check if this charge state is positive or negative and get the mix value
            if cs_index < len(generalVars.aug_PCS):
                mix_val = guiVars.PCS_augMixValues[cs_index].get()
            else:
                mix_val = guiVars.NCS_augMixValues[cs_index - len(generalVars.aug_PCS)].get()
                ncs = True
            
            # Check if the mix value is not 0, otherwise no need to plot the transitions for this charge state
            if mix_val != '0.0':
                ploted_cs.append(cs)
                cs_type.append(ncs)

        # Initialize the x, y and w arrays, taking into account the number of charge states to plot, for both the non satellites and satellites (xs, ys, ws) transitions
        x, y, w, xs, ys, ws = initialize_XYW('Auger_CS', ploted_cs)
        
        bad_lines = {}
        
        # Loop the charge states to plot
        for cs_index, cs in enumerate(ploted_cs):
            # Loop the possible auger transitions
            for index, transition in enumerate(generalVars.the_aug_dictionary):
                if generalVars.the_aug_dictionary[transition]["selected_state"]:
                    # Same as stick but we dont care about the number of transitions
                    _, aug_sim_val = updateAugCSTransitionsVals(transition, 0, cs_type[cs_index], cs)
                    
                    # Store the values in a list containing all the transitions to simulate
                    x[cs_index * len(generalVars.the_aug_dictionary) + index], y[cs_index * len(generalVars.the_aug_dictionary) + index], w[cs_index * len(generalVars.the_aug_dictionary) + index] = simu_auger(aug_sim_val, beam, FWHM, shake_amps)

            # -------------------------------------------------------------------------------------------
            # Check if there are any transitions with missing rates
            bad_selection, bad_lines = Msimu_check_bads(cs_index, cs, x, xs, False)
        
        if prompt:
            report_MbadSelection(bad_lines, ploted_cs)
    
    
    return x, y, w, xs, ys, ws, bad_selection, ploted_cs