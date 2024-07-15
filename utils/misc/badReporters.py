"""
Module with functions that calculate and report back to the user when missing transition lines are selected.
"""

import data.variables as generalVars

#GUI Imports for warnings
from tkinter import messagebox


from typing import List, Dict, Tuple

# --------------------------------------------------------- #
#                                                           #
#   FUNCTIONS TO CALCULATE AND REPORT BAD USER SELECTIONS   #
#                                                           #
# --------------------------------------------------------- #


def report_MbadSelection(bad_lines: Dict[str, List[str]], ploted_cs: List[str]):
    """
    Function to format the text and create a window to report on the selected transitions that do not have data for each charge state.
        
        Args:
            bad_lines: dictionary to hold the lines that arent found for each charge state
            ploted_cs: expected charge states that need to be plotted.
        
        Returns:
            Nothing. The message box with the info is shown.
    """
    
    # As there are multiples charge state we need a more detailed feedback for which lines failed
    # First we build the text that is going to be shown
    text = "Transitions not available for:\n"
    for cs in bad_lines:
        text += cs + ": " + str(bad_lines[cs]) + "\n"

    messagebox.showwarning("Wrong Transition", text)

    # Even if one of the transitions is not plotted for on charge state we might still have
    # At least one charge state where that transition is plotted
    # For this we show if there are any transitions that were plotted 0 times
    # Check if all charge states have at least one transition that was not plotted
    if len(bad_lines) == len(ploted_cs):
        # Initialize the intersection
        intersection = list(bad_lines.values())[-1]
        # Calculate the intersection of all the charge states
        for cs in bad_lines:
            l1 = set(bad_lines[cs])
            intersection = list(l1.intersection(intersection))

        # Show the common transitions that were not plotted
        messagebox.showwarning("Common Transitions", str(intersection))
    else:
        messagebox.showwarning("Common Transitions", "Every transition is plotted for at least 1 charge state.")


def simu_check_bads(x: List[List[float]], xs: List[List[List[float]]], rad: bool = True, prompt: bool = True):
    """
    Function to check if any of the selected transitions do not have data.
    
        Args:
            x: energy values for each of the possible transitions
            xs: energy values for each of the possible radiative sattelite transitions for each radiative transition
            rad: flag to check for radiative (True) or auger (False) missing data
        
        Returns:
            bads: indexes of the missing transitions. The length of this list is also returned
    """
    bads: List[int] = []
    
    if rad:
        for index, transition in enumerate(generalVars.the_dictionary):
            if generalVars.the_dictionary[transition]["selected_state"]:
                if not x[index] and not any(xs[index]):
                    if prompt:
                        messagebox.showwarning("Wrong Transition", transition + " is not Available")
                    bads.append(index)
    else:
        for index, transition in enumerate(generalVars.the_aug_dictionary):
            if generalVars.the_aug_dictionary[transition]["selected_state"]:
                if not x[index]:
                    if prompt:
                        messagebox.showwarning("Wrong Auger Transition", transition + " is not Available")
                    bads.append(index)
    
    return len(bads), bads


def simu_quantify_check_bads(el_idx: int, element: str, x: List[List[float]], xs: List[List[List[float]]], rad: bool = True, prompt: bool = True):
    bads: List[int] = []
    
    if rad:
        # Read the selected transitions
        # In this case we first store all the values for the transitions and then we calculate the y values to be plotted according to a profile
        for index, transition in enumerate(generalVars.the_dictionary):
            if generalVars.the_dictionary[transition]["selected_state"]:
                if not x[el_idx * len(generalVars.the_dictionary) + index] and not any(xs[el_idx * len(generalVars.the_dictionary) + index]):
                    if prompt:
                        messagebox.showwarning("Wrong Transition", transition + " is not Available for" + element)
                    bads.append(el_idx * len(generalVars.the_dictionary) + index)
    else:
        # Read the selected transitions
        # In this case we first store all the values for the transitions and then we calculate the y values to be plotted according to a profile
        for index, transition in enumerate(generalVars.the_aug_dictionary):
            if generalVars.the_dictionary[transition]["selected_state"]:
                if not x[el_idx * len(generalVars.the_dictionary) + index]:
                    if prompt:
                        messagebox.showwarning("Wrong Transition", transition + " is not Available for" + element)
                    bads.append(el_idx * len(generalVars.the_dictionary) + index)
    
    return len(bads), bads


def Msimu_check_bads(cs_index: int, cs: str, x: List[List[float]], xs: List[List[List[float]]], rad: bool = True):
    """
    Function to check if any of the transitions do not have any data for the current charge state.
        
        Args:
            cs_index: index of the current charge state from the list of charge states to be plotted
            cs: current charge state label from the list of charge states to be plotted
            x: energy values for each of the possible transitions
            xs: energy values for each of the possible radiative sattelite transitions for each radiative transition
            rad: flag to check for radiative (True) or auger (False) missing data
        
        Returns:
            bad_selection: total number of transitions that had no data
            bad_lines: dictionary to hold the lines that arent found for each charge state 
    """
    bad_lines: Dict[str, List[str]] = {}
    bad_selection = 0
    
    if rad:
        for index, transition in enumerate(generalVars.the_dictionary):
            if generalVars.the_dictionary[transition]["selected_state"]:
                if not x[cs_index * len(generalVars.the_dictionary) + index] and not all(xs[cs_index * len(generalVars.the_dictionary) + index]):
                    if cs not in bad_lines:
                        bad_lines[cs] = [transition]
                    else:
                        bad_lines[cs].append(transition)

                    x[cs_index * len(generalVars.the_dictionary) + index] = []
                    bad_selection += 1
    else:
        for index, transition in enumerate(generalVars.the_aug_dictionary):
                    if generalVars.the_aug_dictionary[transition]["selected_state"]:
                        if not x[cs_index * len(generalVars.the_aug_dictionary) + index]:
                            if cs not in bad_lines:
                                bad_lines[cs] = [transition]
                            else:
                                bad_lines[cs].append(transition)

                            x[cs_index * len(generalVars.the_aug_dictionary) + index] = []
                            bad_selection += 1
    
    return bad_selection, bad_lines

