"""
Module with the plotting functions.
"""

import data.variables as generalVars

import interface.variables as guiVars

import numpy as np

from matplotlib.pyplot import Axes
from matplotlib.markers import MarkerStyle

import mplcursors

from typing import List, Dict


# --------------------------------------------------------- #
#                                                           #
#                   FUNCTIONS TO PLOT DATA                  #
#                                                           #
# --------------------------------------------------------- #

# Set of colors to choose from when plotting
col2 = [["#440154"], ["#440256"], ["#450457"], ["#450559"], ["#46075a"], ["#46085c"], ["#460a5d"], ["#460b5e"], ["#470d60"], ["#470e61"], ["#471063"], ["#471164"], ["#471365"], ["#481467"], ["#481668"], ["#481769"], ["#48186a"], ["#481a6c"], ["#481b6d"], ["#481c6e"], ["#481d6f"], ["#481f70"], ["#482071"], ["#482173"], ["#482374"], ["#482475"], ["#482576"], ["#482677"], ["#482878"], ["#482979"], ["#472a7a"], ["#472c7a"], ["#472d7b"], ["#472e7c"], ["#472f7d"], ["#46307e"], ["#46327e"], ["#46337f"], ["#463480"], ["#453581"], ["#453781"], ["#453882"], ["#443983"], ["#443a83"], ["#443b84"], ["#433d84"], ["#433e85"], ["#423f85"], ["#424086"], ["#424186"], ["#414287"], ["#414487"], ["#404588"], ["#404688"], ["#3f4788"], ["#3f4889"], ["#3e4989"], ["#3e4a89"], ["#3e4c8a"], ["#3d4d8a"], ["#3d4e8a"], ["#3c4f8a"], ["#3c508b"], ["#3b518b"], ["#3b528b"], ["#3a538b"], ["#3a548c"], ["#39558c"], ["#39568c"], ["#38588c"], ["#38598c"], ["#375a8c"], ["#375b8d"], ["#365c8d"], ["#365d8d"], ["#355e8d"], ["#355f8d"], ["#34608d"], ["#34618d"], ["#33628d"], ["#33638d"], ["#32648e"], ["#32658e"], ["#31668e"], ["#31678e"], ["#31688e"], ["#30698e"], ["#306a8e"], ["#2f6b8e"], ["#2f6c8e"], ["#2e6d8e"], ["#2e6e8e"], ["#2e6f8e"], ["#2d708e"], ["#2d718e"], ["#2c718e"], ["#2c728e"], ["#2c738e"], ["#2b748e"], ["#2b758e"], ["#2a768e"], ["#2a778e"], ["#2a788e"], ["#29798e"], ["#297a8e"], ["#297b8e"], ["#287c8e"], ["#287d8e"], ["#277e8e"], ["#277f8e"], ["#27808e"], ["#26818e"], ["#26828e"], ["#26828e"], ["#25838e"], ["#25848e"], ["#25858e"], ["#24868e"], ["#24878e"], ["#23888e"], ["#23898e"], ["#238a8d"], ["#228b8d"], ["#228c8d"], ["#228d8d"], ["#218e8d"], ["#218f8d"], ["#21908d"], ["#21918c"], ["#20928c"], ["#20928c"], ["#20938c"], ["#1f948c"], ["#1f958b"], ["#1f968b"], ["#1f978b"], ["#1f988b"], ["#1f998a"], ["#1f9a8a"], ["#1e9b8a"], ["#1e9c89"], ["#1e9d89"], ["#1f9e89"], ["#1f9f88"], ["#1fa088"], ["#1fa188"], ["#1fa187"], ["#1fa287"], ["#20a386"], ["#20a486"], ["#21a585"], ["#21a685"], ["#22a785"], ["#22a884"], ["#23a983"], ["#24aa83"], ["#25ab82"], ["#25ac82"], ["#26ad81"], ["#27ad81"], ["#28ae80"], ["#29af7f"], ["#2ab07f"], ["#2cb17e"], ["#2db27d"], ["#2eb37c"], ["#2fb47c"], ["#31b57b"], ["#32b67a"], ["#34b679"], ["#35b779"], ["#37b878"], ["#38b977"], ["#3aba76"], ["#3bbb75"], ["#3dbc74"], ["#3fbc73"], ["#40bd72"], ["#42be71"], ["#44bf70"], ["#46c06f"], ["#48c16e"], ["#4ac16d"], ["#4cc26c"], ["#4ec36b"], ["#50c46a"], ["#52c569"], ["#54c568"], ["#56c667"], ["#58c765"], ["#5ac864"], ["#5cc863"], ["#5ec962"], ["#60ca60"], ["#63cb5f"], ["#65cb5e"], ["#67cc5c"], ["#69cd5b"], ["#6ccd5a"], ["#6ece58"], ["#70cf57"], ["#73d056"], ["#75d054"], ["#77d153"], ["#7ad151"], ["#7cd250"], ["#7fd34e"], ["#81d34d"], ["#84d44b"], ["#86d549"], ["#89d548"], ["#8bd646"], ["#8ed645"], ["#90d743"], ["#93d741"], ["#95d840"], ["#98d83e"], ["#9bd93c"], ["#9dd93b"], ["#a0da39"], ["#a2da37"], ["#a5db36"], ["#a8db34"], ["#aadc32"], ["#addc30"], ["#b0dd2f"], ["#b2dd2d"], ["#b5de2b"], ["#b8de29"], ["#bade28"], ["#bddf26"], ["#c0df25"], ["#c2df23"], ["#c5e021"], ["#c8e020"], ["#cae11f"], ["#cde11d"], ["#d0e11c"], ["#d2e21b"], ["#d5e21a"], ["#d8e219"], ["#dae319"], ["#dde318"], ["#dfe318"], ["#e2e418"], ["#e5e419"], ["#e7e419"], ["#eae51a"], ["#ece51b"], ["#efe51c"], ["#f1e51d"], ["#f4e61e"], ["#f6e620"], ["#f8e621"], ["#fbe723"], ["#fde725"]]
"""
Set of colors to choose from when plotting
"""


def select_color():
    return str(col2[np.random.randint(0, len(col2))][0])

# Stick plotter. Plots a stick for the transition
def stem_ploter(a: Axes, x: List[float], y: List[float], JJ: List[int], transition: str, spec_type: str, ind: int = 0, key: str = '', x_up: List[float] = [], y_up: List[float] = [], JJ_up: List[int] = []):
    """
    Stick plotter function. Plots a stick for the transition
        
        Args:
            a: matplotlib axes object where to plot the stems
            x: list of the transition energies
            y: list of the transition intensities
            JJ: list of the transition 2js
            transition: the selected transition to plot
            spec_type: simulation type selected in the interface (diagram, satellite, auger, diagram_cs, satellite_cs, auger_cs)
            ind: shake level index to use when plotting a satellite transition
            key: shake level label to use when plotting a satellite transition
            x_up: list of the shake-up transition energies
            y_up: list of the shake-up transition intensities
            JJ_up: list of the shake-up transition 2js
        
        Returns:
            Nothing, the transition is plotted and the interface is updated
    """
    
    JJs = list(set(JJ))
    JJs_up = list(set(JJ_up))
    
    ys: List[List[float]] = [[] for _ in JJs]
    ys_up: List[List[float]] = [[] for _ in JJs_up]
    xs: List[List[float]] = [[] for _ in JJs]
    xs_up: List[List[float]] = [[] for _ in JJs_up]
    
    if guiVars.JJ_colors.get(): # type: ignore
        for h, j in enumerate(JJ):
            if j not in generalVars.colors_2J:
                generalVars.colors_2J[j] = select_color()

            i = JJs.index(j)
            ys[i].append(y[h])
            xs[i].append(x[h])
        
        for h, j in enumerate(JJ_up):
            if j not in generalVars.colors_2J:
                generalVars.colors_2J[j] = select_color()

            i = JJs_up.index(j)
            ys_up[i].append(y_up[h])
            xs_up[i].append(x_up[h])
    
    # Add extra values before and after to make the y start and terminate on 0
    max_value = max(x) if len(x) > 0 else 0.0
    min_value = min(x) if len(x) > 0 else 0.0
    delta = (min_value + max_value) / 2.0
    
    x_tmp = x.copy()
    
    if guiVars.x_min.get() == "Auto": # type: ignore
        x_tmp.insert(0, min_value - delta * 0.2)
        y.insert(0, 0)
    else:
        a.set_xlim(xmin=float(guiVars.x_min.get())) # type: ignore
    
    if guiVars.x_max.get() == "Auto": # type: ignore
        x_tmp.append(max_value + delta * 0.2)
        y.append(0)
    else:
        a.set_xlim(xmax=float(guiVars.x_max.get())) # type: ignore
    
    
    tr_readable = str(generalVars.the_dictionary[transition]['readable_name'])
    tr_latex = str(generalVars.the_dictionary[transition]['latex_name'])
    
    # Calculate the y's weighted with the shake weights depending on the spectrum type and plot the sticks
    # In the case of charge state simulation the y's are also weighted by the selected mixture percentages
    if spec_type == 'Diagram' or spec_type == 'Auger':
        with open("debug_sticks.txt", "a") as debug:
            debug.write("\nDiagram Sticks:\n\n")
            debug.write(tr_readable + "\n")
        if not guiVars.JJ_colors.get(): # type: ignore
            with open("debug_sticks.txt", "a") as debug:
                for x1, y1 in zip(x_tmp, y):
                    debug.write(str(x1) + ", " + str(y1) + "\n")
            a.stem(x_tmp, y, markerfmt=' ', linefmt=select_color(), label=tr_latex, use_line_collection=True)
            a.legend(loc='best', numpoints=1)
        else:
            for i in range(len(xs)):
                a.stem(xs[i], ys[i], markerfmt=' ', linefmt=str(generalVars.colors_2J[JJ[i]]), label=tr_latex + "_" + str(JJ[i]), use_line_collection=True)
                a.legend(loc='best', numpoints=1)
    elif spec_type == 'Satellites':
        if not guiVars.JJ_colors.get(): # type: ignore
            if len(x_tmp) > 0 and len(y) > 0:
                with open("debug_sticks.txt", "a") as debug:
                    debug.write("\nShake-off Sticks:\n\n")
                    debug.write(tr_readable + ' - ' + generalVars.labeldict[key] + "\n")
                    for x1, y1 in zip(x_tmp, y):
                        debug.write(str(x1) + ", " + str(y1) + "\n")
                a.stem(x_tmp, y, markerfmt=' ', linefmt=select_color(), label=tr_latex + ' - ' + generalVars.labeldict[key], use_line_collection=True)  # Plot a stemplot
                a.legend(loc='best', numpoints=1)
            
            if len(x_up) > 0 and len(y_up) > 0:
                with open("debug_sticks.txt", "a") as debug:
                    debug.write("\nShake-up Sticks:\n\n")
                    debug.write(tr_readable + ' - ' + generalVars.labeldict[key] + ' - shakeup\n')
                    for x1, y1 in zip(x_up, y_up):
                        debug.write(str(x1) + ", " + str(y1) + "\n")
                a.stem(x_up, y_up, markerfmt=' ', linefmt=select_color(), label=tr_latex + ' - ' + generalVars.labeldict[key] + ' - shakeup', use_line_collection=True)  # Plot a stemplot
                a.legend(loc='best', numpoints=1)
        else:
            if len(xs) > 0 and len(ys) > 0 and len(JJ) > 0:
                for i in range(len(xs)):
                    a.stem(xs[i], ys[i], markerfmt=' ', linefmt=str(generalVars.colors_2J[JJ[i]]), label=tr_latex + ' - ' + generalVars.labeldict[key] + '_' + str(JJ[i]), use_line_collection=True)  # Plot a stemplot
                    a.legend(loc='best', numpoints=1)
                
            if len(x_up) > 0 and len(y_up) > 0 and len(JJ_up) > 0:
                for i in range(len(xs_up)):
                    a.stem(xs_up[i], ys_up[i], markerfmt=' ', linefmt=str(generalVars.colors_2J[JJ_up[i]]), label=tr_latex + ' - ' + generalVars.labeldict[key] + ' - shakeup_' + str(JJ_up[i]), use_line_collection=True)  # Plot a stemplot
                    a.legend(loc='best', numpoints=1)
    elif spec_type == 'Diagram_CS' or spec_type == 'Auger_CS':
        if not guiVars.JJ_colors.get(): # type: ignore
            a.stem(x_tmp, y, markerfmt=' ', linefmt=select_color(), label=tr_latex, use_line_collection=True)
            a.legend(loc='best', numpoints=1)
        else:
            for i in range(len(xs)):
                a.stem(xs[i], ys[i], markerfmt=' ', linefmt=str(generalVars.colors_2J[JJ[i]]), label=tr_latex + "_" + str(JJ[i]), use_line_collection=True)
                a.legend(loc='best', numpoints=1)
    elif spec_type == 'Satellites_CS':
        if not guiVars.JJ_colors.get(): # type: ignore
            a.stem(x_tmp, y, markerfmt=' ', linefmt=select_color(), label=tr_latex + ' - ' + generalVars.labeldict[key], use_line_collection=True)  # Plot a stemplot
            a.legend(loc='best', numpoints=1)
            
            a.stem(x_up, y_up, markerfmt=' ', linefmt=select_color(), label=tr_latex + ' - ' + generalVars.labeldict[key] + ' - shakeup', use_line_collection=True)  # Plot a stemplot
            a.legend(loc='best', numpoints=1)
        else:
            for i in range(len(xs_up)):
                a.stem(xs[i], ys[i], markerfmt=' ', linefmt=str(generalVars.colors_2J[JJ[i]]), label=tr_latex + ' - ' + generalVars.labeldict[key] + "_" + str(JJ[i]), use_line_collection=True)  # Plot a stemplot
                a.legend(loc='best', numpoints=1)
                
                a.stem(xs_up[i], ys_up[i], markerfmt=' ', linefmt=str(generalVars.colors_2J[JJ_up[i]]), label=tr_latex + ' - ' + generalVars.labeldict[key] + ' - shakeup_' + str(JJ_up[i]), use_line_collection=True)  # Plot a stemplot
                a.legend(loc='best', numpoints=1)
    
    # --------------------------------------------------------------------------------------------------------------------------
    # Automatic legend formating
    a.legend(title=generalVars.element_name, title_fontsize='large')
    a.legend(title=generalVars.element_name)
    # Number of total labels to place in the legend
    number_of_labels = len(a.legend().get_texts())
    # Initialize the numeber of legend columns
    legend_columns = 1
    # Initialize the number of legends in each columns
    labels_per_columns = number_of_labels / legend_columns
    
    # While we have more than 25 labels per column
    while labels_per_columns >= 25:
        # Add one more column
        legend_columns += 1
        # Recalculate the number of labels per column
        labels_per_columns = number_of_labels / legend_columns
    
    # Place the legend with the final number of columns
    a.legend(ncol=legend_columns)
    
    return a

# Profile simulation plotter. Plots the transitions with a line profile shape
def simu_plot(sat: str, graph_area: Axes, normalization_var: float, y0: float, plotSimu: bool = True):
    """
    Function to plot the simulation values according to the selected transition types.
    
        Args:
            sat: simulation type selected in the interface (diagram, satellite, auger)
            graph_area: matplotlib graph to plot the simulated transitions
            normalization_var: normalization multiplier to normalize intensity when plotting
            y0: intensity offset user value from the interface
        
        Returns:
            graph_area. The updated interface graph_area object.
    """
    
    totalDiagInt = []
    if 'Diagram' in sat:
        for index, key in enumerate(generalVars.the_dictionary):
            if generalVars.the_dictionary[key]["selected_state"]:
                totalDiagInt.append(sum(generalVars.yfinal[index]))
                if plotSimu:
                    # Plot the selected transition
                    label = generalVars.the_dictionary[key]["latex_name"]
                    graph_area.plot(generalVars.xfinal, (np.array(generalVars.yfinal[index]) * normalization_var) + y0, label=label, gid=key, color=select_color())  # Plot the simulation of all lines
    if 'Satellites' in sat:
        totalShakeoffInt = {}
        totalShakeupInt = {}
        totalShakeoffInt_2p = []
        totalShakeupInt_2p = []
        for index, key in enumerate(generalVars.the_dictionary):
            if generalVars.the_dictionary[key]["selected_state"]:
                for l, m in enumerate(generalVars.yfinals[index]):
                    # Dont plot the satellites that have a max y value of 0
                    if max(m) != 0:
                        label = str(generalVars.the_dictionary[key]["latex_name"])
                        if l < len(generalVars.label1):
                            if "2p" in generalVars.labeldict[generalVars.label1[l]]:
                                totalShakeoffInt_2p.append(sum(m))
                            totalShakeoffInt[label + ' - ' + generalVars.labeldict[generalVars.label1[l]]] = sum(m)
                        else:
                            if "2p" in generalVars.labeldict[generalVars.label1[l - len(generalVars.label1)]]:
                                totalShakeupInt_2p.append(sum(m))
                            totalShakeupInt[label + ' - ' + generalVars.labeldict[generalVars.label1[l - len(generalVars.label1)]] + ' - shake-up'] = sum(m)
                        if plotSimu:
                            # Plot the selected transition
                            if l < len(generalVars.label1):
                                graph_area.plot(generalVars.xfinal, (np.array(generalVars.yfinals[index][l]) * normalization_var) + y0, label=label + ' - ' + generalVars.labeldict[generalVars.label1[l]], gid=key + ' - ' + generalVars.labeldict[generalVars.label1[l]], color=select_color())  # Plot the simulation of all lines
                            else:
                                graph_area.plot(generalVars.xfinal, (np.array(generalVars.yfinals[index][l]) * normalization_var) + y0, label=label + ' - ' + generalVars.labeldict[generalVars.label1[l - len(generalVars.label1)]] + ' - shake-up', gid=key + ' - ' + generalVars.labeldict[generalVars.label1[l - len(generalVars.label1)]] + ' - shake-up', color=select_color())  # Plot the simulation of all lines
        shkoff = '; '.join([key + ": " + str(totalShakeoffInt[key]) for key in totalShakeoffInt])
        shkup = '; '.join([key + ": " + str(totalShakeupInt[key]) for key in totalShakeupInt])
        print(str(guiVars.excitation_energy.get()) + "; " + str(sum(totalDiagInt)) + "; " + shkoff + "; " + shkup) # type: ignore
        with open("spectraInts_modOvrlp_sameWidth.txt", "a") as intsFile:
            intsFile.write(str(guiVars.excitation_energy.get()) + "; Diagram: " + str(sum(totalDiagInt)) + "; " + shkoff + "; " + shkup + "\n") # type: ignore
    if sat == 'Auger':
        for index, key in enumerate(generalVars.the_aug_dictionary):
            if generalVars.the_aug_dictionary[key]["selected_state"]:
                if plotSimu:
                    # Plot the selected transition
                    label = generalVars.the_dictionary[key]["latex_name"]
                    graph_area.plot(generalVars.xfinal, (np.array(generalVars.yfinal[index]) * normalization_var) + y0, label=label, gid=key, color=select_color())  # Plot the simulation of all lines
    
    if plotSimu:
        if guiVars.totalvar.get() == 'Total': # type: ignore
            # Plot the selected transition
            graph_area.plot(generalVars.xfinal, (np.array(generalVars.ytot) * normalization_var) + y0, label='Total', gid='Total', ls='--', lw=2, color='k')  # Plot the simulation of all lines
        if guiVars.totaldiagvar.get() == 'Total': # type: ignore
            # Plot the selected transition
            graph_area.plot(generalVars.xfinal, (np.array(generalVars.ydiagtot) * normalization_var) + y0, label='Total Diagram', gid='Total Diagram', ls='--', lw=2, color='r')  # Plot the simulation of all lines
        if guiVars.totalsatvar.get() == 'Total': # type: ignore
            # Plot the selected transition
            graph_area.plot(generalVars.xfinal, (np.array(generalVars.ysattot) * normalization_var) + y0, label='Total Satellite', gid='Total Satellite', ls='--', lw=2, color='b')  # Plot the simulation of all lines
        if guiVars.totalshkoffvar.get() == 'Total': # type: ignore
            # Plot the selected transition
            graph_area.plot(generalVars.xfinal, (np.array(generalVars.yshkofftot) * normalization_var) + y0, label='Total Shake-off', gid='Total Shake-off', ls='--', lw=2, color='g')  # Plot the simulation of all lines
        if guiVars.totalshkupvar.get() == 'Total': # type: ignore
            # Plot the selected transition
            graph_area.plot(generalVars.xfinal, (np.array(generalVars.yshkuptot) * normalization_var) + y0, label='Total Shake-up', gid='Total Shake-up', ls='--', lw=2, color='m')  # Plot the simulation of all lines
        
        if len(generalVars.yextras) > 0:
            for i, key in enumerate(generalVars.extra_fitting_functions):
                graph_area.plot(generalVars.xfinal, (np.array(generalVars.yextras[i]) * normalization_var) + y0, label=key, gid=key, ls=':', lw=2, color=select_color())
            
            if guiVars.totalextrafitvar.get() == 'Total': # type: ignore
                graph_area.plot(generalVars.xfinal, (np.array(generalVars.yextrastot) * normalization_var) + y0, label='Total Extra Fit', gid='Total Extra Fit', ls='--', lw=2, color='y')
        
        lines = graph_area.get_lines()
        
        cursor = mplcursors.cursor(lines, hover=True)
        cursor.connect('add', lambda sel: sel.annotation.set_text(sel.artist.get_label()))
    
        graph_area.legend()
    
    return graph_area


# Profile simulation plotter for charge state mixtures. Plots the transitions with a line profile shape
def Esimu_plot(exc: List[str], sat: str, graph_area: Axes,
               normalization_var: float, y0: float, plotSimu: bool = True):
    """
    Function to plot the simulation values according to the selected transition types.
    
        Args:
            exc: list of the excitations to be plotted
            sat: simulation type selected in the interface (diagram, satellite, auger)
            graph_area: matplotlib graph to plot the simulated transitions
            normalization_var: normalization multiplier to normalize intensity when plotting
            y0: intensity offset user value from the interface
            total: flag from the interface to plot the total intensity
        
        Returns:
            Nothing. The interface is updated with the new simulation data.
    """
    
    totalDiagInt = {}
    if 'Excitation' in sat:
        for exc_index, exc_orb in enumerate(exc):
            for index, key in enumerate(generalVars.the_dictionary):
                if generalVars.the_dictionary[key]["selected_state"]:
                    label = str(generalVars.the_dictionary[key]["latex_name"])
                    totalDiagInt[exc_orb + ' ' + label] = sum(generalVars.yfinal_exc[exc_index * len(generalVars.the_dictionary) + index])
                    # print(generalVars.yfinal_exc[exc_index * len(generalVars.the_dictionary) + index])
                    if plotSimu:
                        # Plot the selected transition
                        label = str(generalVars.the_dictionary[key]["latex_name"])
                        graph_area.plot(generalVars.xfinal, (np.array(generalVars.yfinal_exc[exc_index * len(generalVars.the_dictionary) + index]) * normalization_var) + y0, label=exc_orb + ' ' + label, gid=exc_orb + ' ' + key, color=select_color())  # Plot the simulation of all lines
    totalSatInt = {}
    if 'ESat' in sat:
        for exc_index, exc_orb in enumerate(exc):
            for index, key in enumerate(generalVars.the_dictionary):
                if generalVars.the_dictionary[key]["selected_state"]:
                    for l, m in enumerate(generalVars.yfinals_exc[exc_index * len(generalVars.the_dictionary) + index]):
                        # Dont plot the satellites that have a max y value of 0
                        if max(m) != 0:
                            label = str(generalVars.the_dictionary[key]["latex_name"])
                            totalSatInt[exc_orb + " " + label + " - " + generalVars.labeldict[generalVars.label1[l]]] = sum(generalVars.yfinals_exc[exc_index * len(generalVars.the_dictionary) + index][l])
                            if plotSimu:
                                # Plot the selected transition
                                label = str(generalVars.the_dictionary[key]["latex_name"])
                                # graph_area.plot(generalVars.xfinal, (np.array(generalVars.yfinals_exc[exc_index * len(generalVars.the_dictionary) + index][l]) * normalization_var) + y0, label=exc_orb + ' ' + label + ' - ' + generalVars.labeldict[generalVars.label1_exc[exc_index][l]], gid=exc_orb + ' ' + key + ' - ' + generalVars.labeldict[generalVars.label1_exc[exc_index][l]], color=select_color())  # Plot the simulation of all lines
                                graph_area.plot(generalVars.xfinal, (np.array(generalVars.yfinals_exc[exc_index * len(generalVars.the_dictionary) + index][l]) * normalization_var) + y0, label=exc_orb + ' ' + label + ' - ' + generalVars.labeldict[generalVars.label1[l]], gid=exc_orb + ' ' + key + ' - ' + generalVars.labeldict[generalVars.label1[l]], color=select_color())  # Plot the simulation of all lines
    diags = '; '.join([key + ": " + str(totalDiagInt[key]) for key in totalDiagInt])
    sats = '; '.join([key + ": " + str(totalSatInt[key]) for key in totalSatInt])
    print(str(guiVars.excitation_energy.get()) + "; " + diags + "; " + sats) # type: ignore
    with open("spectraInts_excitation_widthMod.txt", "a") as intsFile:
        intsFile.write(str(guiVars.excitation_energy.get()) + "; " + diags + ("; " if len(sats) > 0 else "") + sats + "\n") # type: ignore
    
    if sat == 'Auger':
        for exc_index, exc_orb in enumerate(exc):
            for index, key in enumerate(generalVars.the_aug_dictionary):
                if generalVars.the_aug_dictionary[key]["selected_state"]:
                    if plotSimu:
                        # Plot the selected transition
                        label = str(generalVars.the_dictionary[key]["latex_name"])
                        graph_area.plot(generalVars.xfinal, (np.array(generalVars.yfinal_exc[exc_index * len(generalVars.the_aug_dictionary) + index]) * normalization_var) + y0, label=exc_orb + ' ' + label, gid=exc_orb + ' ' + key, color=select_color())  # Plot the simulation of all lines
    
    if plotSimu:
        if guiVars.totalvar.get() == 'Total': # type: ignore
            # Plot the selected transition
            graph_area.plot(generalVars.xfinal, (np.array(generalVars.ytot_exc) * normalization_var) + y0, label='Total', gid='Total', ls='--', lw=2, color='k')  # Plot the simulation of all lines
        if guiVars.totaldiagvar.get() == 'Total': # type: ignore
            # Plot the selected transition
            graph_area.plot(generalVars.xfinal, (np.array(generalVars.ydiagtot_exc) * normalization_var) + y0, label='Total Diagram', gid='Total Diagram', ls='--', lw=2, color='r')  # Plot the simulation of all lines
        if guiVars.totalsatvar.get() == 'Total': # type: ignore
            # Plot the selected transition
            graph_area.plot(generalVars.xfinal, (np.array(generalVars.ysattot_exc) * normalization_var) + y0, label='Total Satellite', gid='Total Satellite', ls='--', lw=2, color='b')  # Plot the simulation of all lines
        if guiVars.totalshkoffvar.get() == 'Total': # type: ignore
            # Plot the selected transition
            graph_area.plot(generalVars.xfinal, (np.array(generalVars.yshkofftot_exc) * normalization_var) + y0, label='Total Shake-off', gid='Total Shake-off', ls='--', lw=2, color='g')  # Plot the simulation of all lines
        if guiVars.totalshkupvar.get() == 'Total': # type: ignore
            # Plot the selected transition
            graph_area.plot(generalVars.xfinal, (np.array(generalVars.yshkuptot_exc) * normalization_var) + y0, label='Total Shake-up', gid='Total Shake-up', ls='--', lw=2, color='m')  # Plot the simulation of all lines
        
        if len(generalVars.yextras) > 0:
            for i, key in enumerate(generalVars.extra_fitting_functions):
                graph_area.plot(generalVars.xfinal, (np.array(generalVars.yextras[i]) * normalization_var) + y0, label=key, gid=key, ls=':', lw=2, color=select_color())
            
            if guiVars.totalextrafitvar.get() == 'Total': # type: ignore
                graph_area.plot(generalVars.xfinal, (np.array(generalVars.yextrastot) * normalization_var) + y0, label='Total Extra Fit', gid='Total Extra Fit', ls='--', lw=2, color='y')
    
        lines = graph_area.get_lines()
        
        cursor = mplcursors.cursor(lines, hover=True)
        cursor.connect('add', lambda sel: sel.annotation.set_text(sel.artist.get_label()))
        
        graph_area.legend()
    
    return graph_area


# Profile simulation plotter for charge state mixtures. Plots the transitions with a line profile shape
def Msimu_plot(ploted_cs: List[str], sat: str, graph_area: Axes,
               normalization_var: float, y0: float):
    """
    Function to plot the simulation values according to the selected transition types.
    
        Args:
            ploted_cs: list of the charge states to be plotted
            sat: simulation type selected in the interface (diagram, satellite, auger)
            graph_area: matplotlib graph to plot the simulated transitions
            normalization_var: normalization multiplier to normalize intensity when plotting
            y0: intensity offset user value from the interface
            total: flag from the interface to plot the total intensity
        
        Returns:
            Nothing. The interface is updated with the new simulation data.
    """
    
    if 'Diagram' in sat:
        for cs_index, cs in enumerate(ploted_cs):
            for index, key in enumerate(generalVars.the_dictionary):
                if generalVars.the_dictionary[key]["selected_state"]:
                    # Plot the selected transition
                    graph_area.plot(generalVars.xfinal, (np.array(generalVars.yfinal[cs_index * len(generalVars.the_dictionary) + index]) * normalization_var) + y0, label=cs + ' ' + key, gid=cs + ' ' + key, color=select_color())  # Plot the simulation of all lines
                    graph_area.legend()
    if 'Satellites' in sat:
        for cs_index, cs in enumerate(ploted_cs):
            for index, key in enumerate(generalVars.the_dictionary):
                if generalVars.the_dictionary[key]["selected_state"]:
                    for l, m in enumerate(generalVars.yfinals[cs_index * len(generalVars.the_dictionary) + index]):
                        # Dont plot the satellites that have a max y value of 0
                        if max(m) != 0:
                            # Plot the selected transition
                            graph_area.plot(generalVars.xfinal, (np.array(generalVars.yfinals[cs_index * len(generalVars.the_dictionary) + index][l]) * normalization_var) + y0, label=cs + ' ' + key + ' - ' + generalVars.labeldict[generalVars.label1[l]], gid=cs + ' ' + key + ' - ' + generalVars.labeldict[generalVars.label1[l]], color=select_color())  # Plot the simulation of all lines
                            graph_area.legend()
    if sat == 'Auger':
        for cs_index, cs in enumerate(ploted_cs):
            for index, key in enumerate(generalVars.the_aug_dictionary):
                if generalVars.the_aug_dictionary[key]["selected_state"]:
                    # Plot the selected transition
                    graph_area.plot(generalVars.xfinal, (np.array(generalVars.yfinal[cs_index * len(generalVars.the_aug_dictionary) + index]) * normalization_var) + y0, label=cs + ' ' + key, gid=cs + ' ' + key, color=select_color())  # Plot the simulation of all lines
                    graph_area.legend()
    if guiVars.totalvar.get() == 'Total': # type: ignore
        # Plot the selected transition
        graph_area.plot(generalVars.xfinal, (np.array(generalVars.ytot) * normalization_var) + y0, label='Total', gid='Total', ls='--', lw=2, color='k')  # Plot the simulation of all lines
        graph_area.legend()
    if guiVars.totaldiagvar.get() == 'Total': # type: ignore
        # Plot the selected transition
        graph_area.plot(generalVars.xfinal, (np.array(generalVars.ydiagtot) * normalization_var) + y0, label='Total Diagram', gid='Total Diagram', ls='--', lw=2, color='r')  # Plot the simulation of all lines
        graph_area.legend()
    if guiVars.totalsatvar.get() == 'Total': # type: ignore
        # Plot the selected transition
        graph_area.plot(generalVars.xfinal, (np.array(generalVars.ysattot) * normalization_var) + y0, label='Total Satellite', gid='Total Satellite', ls='--', lw=2, color='b')  # Plot the simulation of all lines
        graph_area.legend()
    if guiVars.totalshkoffvar.get() == 'Total': # type: ignore
        # Plot the selected transition
        graph_area.plot(generalVars.xfinal, (np.array(generalVars.yshkofftot) * normalization_var) + y0, label='Total Shake-off', gid='Total Shake-off', ls='--', lw=2, color='g')  # Plot the simulation of all lines
        graph_area.legend()
    if guiVars.totalshkupvar.get() == 'Total': # type: ignore
        # Plot the selected transition
        graph_area.plot(generalVars.xfinal, (np.array(generalVars.yshkuptot) * normalization_var) + y0, label='Total Shake-up', gid='Total Shake-up', ls='--', lw=2, color='m')  # Plot the simulation of all lines
        graph_area.legend()
    
    if len(generalVars.yextras) > 0:
        for i, key in enumerate(generalVars.extra_fitting_functions):
            graph_area.plot(generalVars.xfinal, (np.array(generalVars.yextras[i]) * normalization_var) + y0, label=key, gid=key, ls=':', lw=2, color=select_color())
            graph_area.legend()
        
        if guiVars.totalextrafitvar.get() == 'Total': # type: ignore
            graph_area.plot(generalVars.xfinal, (np.array(generalVars.yextrastot) * normalization_var) + y0, label='Total Extra Fit', gid='Total Extra Fit', ls='--', lw=2, color='y')
            graph_area.legend()

    lines = graph_area.get_lines()
    cursor = mplcursors.cursor(lines, hover=True)
    cursor.connect('add', lambda sel: sel.annotation.set_text(sel.artist.get_label()))
    
    return graph_area

# Profile simulation plotter for charge state mixtures. Plots the transitions with a line profile shape
def Qsimu_plot(elementList: List[str], sat: str, graph_area: Axes,
               normalization_var: float, y0: float, plotSimu: bool = True, baseline: bool = True):
    """
    Function to plot the simulation values according to the selected transition types.
    
        Args:
            elementList: list of the elements to be plotted
            sat: simulation type selected in the interface (diagram, satellite, auger)
            graph_area: matplotlib graph to plot the simulated transitions
            normalization_var: normalization multiplier to normalize intensity when plotting
            y0: intensity offset user value from the interface
            total: flag from the interface to plot the total intensity
        
        Returns:
            Nothing. The interface is updated with the new simulation data.
    """
    
    to_add = []
    if baseline:
        to_add = generalVars.currentBaseline
    else:
        to_add = [0.0] * len(generalVars.xfinal)
    
    if 'Diagram' in sat:
        for index, key in enumerate(generalVars.the_dictionary):
            for el_index, el in enumerate(elementList):
                if generalVars.the_dictionary[key]["selected_state"]:
                    if plotSimu:
                        # Plot the selected transition
                        label = str(generalVars.the_dictionary[key]["latex_name"])
                        graph_area.plot(generalVars.xfinal, (np.array(generalVars.yfinal[el_index * len(generalVars.the_dictionary) + index]) * normalization_var + to_add) + y0, label=el[1] + ' ' + label, gid=el[1] + ' ' + key, color=select_color())  # Plot the simulation of all lines
                        graph_area.legend()
    if 'Satellites' in sat:
        for index, key in enumerate(generalVars.the_dictionary):
            for el_index, el in enumerate(elementList):
                if generalVars.the_dictionary[key]["selected_state"]:
                    for l, m in enumerate(generalVars.yfinals[el_index * len(generalVars.the_dictionary) + index]):
                        # Dont plot the satellites that have a max y value of 0
                        if max(m) != 0:
                            # Plot the selected transition
                            if plotSimu:
                                label = str(generalVars.the_dictionary[key]["latex_name"])
                                graph_area.plot(generalVars.xfinal, (np.array(generalVars.yfinals[el_index * len(generalVars.the_dictionary) + index][l]) * normalization_var + to_add) + y0, label=el[1] + ' ' + label + ' - ' + generalVars.labeldict[generalVars.label1[l]], gid=el[1] + ' ' + key + ' - ' + generalVars.labeldict[generalVars.label1[l]], color=select_color())  # Plot the simulation of all lines
                                graph_area.legend()
    if sat == 'Auger':
        for index, key in enumerate(generalVars.the_aug_dictionary):
            for el_index, el in enumerate(elementList):
                if generalVars.the_aug_dictionary[key]["selected_state"]:
                    if plotSimu:
                        # Plot the selected transition
                        label = str(generalVars.the_dictionary[key]["latex_name"])
                        graph_area.plot(generalVars.xfinal, (np.array(generalVars.yfinal[el_index * len(generalVars.the_aug_dictionary) + index]) * normalization_var + to_add) + y0, label=el[1] + ' ' + label, gid=el[1] + ' ' + key, color=select_color())  # Plot the simulation of all lines
                        graph_area.legend()
    
    for el_index, el in enumerate(elementList):
        if guiVars.totalvar.get() == 'Total': # type: ignore
            # Plot the selected transition
            if plotSimu:
                label = str(generalVars.the_dictionary[key]["latex_name"])
                graph_area.plot(generalVars.xfinal, (np.array(generalVars.ytot) * normalization_var + to_add) + y0, label='Total ' + el[1], gid='Total ' + el[1], ls='--', lw=2, color='k')  # Plot the simulation of all lines
                graph_area.legend()
        if guiVars.totaldiagvar.get() == 'Total': # type: ignore
            # Plot the selected transition
            if plotSimu:
                label = str(generalVars.the_dictionary[key]["latex_name"])
                graph_area.plot(generalVars.xfinal, (np.array(generalVars.ydiagtot) * normalization_var + to_add) + y0, label='Total Diagram ' + el[1], gid='Total Diagram ' + el[1], ls='--', lw=2, color='r')  # Plot the simulation of all lines
                graph_area.legend()
        if guiVars.totalsatvar.get() == 'Total': # type: ignore
            # Plot the selected transition
            if plotSimu:
                label = str(generalVars.the_dictionary[key]["latex_name"])
                graph_area.plot(generalVars.xfinal, (np.array(generalVars.ysattot) * normalization_var + to_add) + y0, label='Total Satellite ' + el[1], gid='Total Satellite ' + el[1], ls='--', lw=2, color='b')  # Plot the simulation of all lines
                graph_area.legend()
        if guiVars.totalshkoffvar.get() == 'Total': # type: ignore
            # Plot the selected transition
            if plotSimu:
                label = str(generalVars.the_dictionary[key]["latex_name"])
                graph_area.plot(generalVars.xfinal, (np.array(generalVars.yshkofftot) * normalization_var + to_add) + y0, label='Total Shake-off ' + el[1], gid='Total Shake-off ' + el[1], ls='--', lw=2, color='g')  # Plot the simulation of all lines
                graph_area.legend()
        if guiVars.totalshkupvar.get() == 'Total': # type: ignore
            # Plot the selected transition
            if plotSimu:
                label = str(generalVars.the_dictionary[key]["latex_name"])
                graph_area.plot(generalVars.xfinal, (np.array(generalVars.yshkuptot) * normalization_var + to_add) + y0, label='Total Shake-up ' + el[1], gid='Total Shake-up ' + el[1], ls='--', lw=2, color='m')  # Plot the simulation of all lines
                graph_area.legend()
        
        if len(generalVars.yextras) > 0:
            for i, key in enumerate(generalVars.extra_fitting_functions):
                if plotSimu:
                    label = str(generalVars.the_dictionary[key]["latex_name"])
                    graph_area.plot(generalVars.xfinal, (np.array(generalVars.yextras[i]) * normalization_var + to_add) + y0, label=el[1] + ' ' + label, gid=key, ls=':', lw=2, color=select_color())
                    graph_area.legend()
            
            if guiVars.totalextrafitvar.get() == 'Total': # type: ignore
                if plotSimu:
                    label = str(generalVars.the_dictionary[key]["latex_name"])
                    graph_area.plot(generalVars.xfinal, (np.array(generalVars.yextrastot) * normalization_var + to_add) + y0, label='Total Extra Fit ' + el[1], gid='Total Extra Fit', ls='--', lw=2, color='y')
                    graph_area.legend()

    lines = graph_area.get_lines()
    cursor = mplcursors.cursor(lines, hover=True)
    cursor.connect('add', lambda sel: sel.annotation.set_text(sel.artist.get_label()))
    
    graph_area.figure.canvas.draw_idle()
    
    return graph_area

# Function to plot the experimental data and std deviation on the residue plot
def plotExp(graph_area: Axes, residues_graph: Axes, exp_x: List[float], exp_y: List[float], exp_sigma: List[float], normalize: str):
    """
    Function to plot the experimental data and std deviation on the residue plot
    
        Args:
            graph_area: new matplotlib plot configured to make space for the residue graph
            residues_graph: matplotlib plot for the residue data
            exp_x: energy values from the experimental spectrum
            exp_y: intensity values from the experimental spectrum
            exp_sigma: error values from the experimental spectrum
            normalize: normalization type selected in the interface
        
        Returns:
            Nothing, the function plots the normalized experimental spectrum in the simulation plot and the experimental errors in the residue plot
    """
    if normalize == 'One':
        # Plot experimental data normalized to unity
        graph_area.scatter(np.array(exp_x), np.array(exp_y) / max(exp_y), marker=MarkerStyle('.'), label='Exp.')
        # Plot std deviation in the residue graph (positive line)
        residues_graph.plot(np.array(exp_x), np.array(exp_sigma) / max(exp_y), 'k--')
        # Plot std deviation in the residue graph (negative line)
        residues_graph.plot(np.array(exp_x), -np.array(exp_sigma) / max(exp_y), 'k--')
    else:
        # Plot experimental data with the current normalization
        graph_area.scatter(np.array(exp_x), np.array(exp_y), marker=MarkerStyle('.'), label='Exp.')
        # Plot std deviation in the residue graph (positive line)
        residues_graph.plot(np.array(exp_x), np.array(exp_sigma), 'k--')
        # Plot std deviation in the residue graph (negative line)
        residues_graph.plot(np.array(exp_x), -np.array(exp_sigma), 'k--')
    
    graph_area.legend()
    
    graph_area.figure.canvas.draw_idle()


# Function to plot the experimental baseline data on the experimental plot
def plotBaseline(graph_area: Axes, base_x: List[float], base_y: List[float], base_type: str = "SNIP"):
    """
    Function to plot the experimental baseline data on the experimental plot
    
        Args:
            graph_area: new matplotlib plot configured to make space for the residue graph
            base_x: energy values from the baseline
            base_y: intensity values from the baseline
            base_type: baseline type, i.e. SNIP, etc
        
        Returns:
            Nothing, the function plots the baseline in the simulation plot
    """
    for c in graph_area.get_lines():
        if c.get_gid() == 'baseline':
            c.remove()
    for c in graph_area.collections:
        if c.get_gid() == 'baseline':
            c.remove()
    
    # Plot experimental data with the current normalization
    graph_area.plot(np.array(base_x), np.array(base_y), label=base_type + ' Baseline', gid='baseline', alpha=0.4)
    graph_area.fill_between(np.array(base_x), np.array(base_y), 0, color='blue', gid='baseline', alpha=0.4) # type: ignore
    
    generalVars.currentBaseline = base_y
    
    graph_area.legend()
    
    graph_area.figure.canvas.draw_idle()


def format_legend(graph_area: Axes):
    """
    Function to format the legend.
    
        Args:
            graph_area: matplotlib graph to plot the simulated transitions
        
        Returns:
            Nothing. The legend is formated and updated on the interface.
    """
    
    # Number of total labels to place in the legend
    number_of_labels = len(graph_area.legend().get_texts())
    # Initialize the numeber of legend columns
    legend_columns = 1
    # Initialize the number of legends in each columns
    labels_per_columns = number_of_labels / legend_columns
    # While we have more than 10 labels per column
    while labels_per_columns > 15:
        # Add one more column
        legend_columns += 1
        # Recalculate the number of labels per column
        labels_per_columns = number_of_labels / legend_columns
    
    # Place the legend with the final number of columns
    graph_area.legend(ncol=legend_columns)



def plot_elements_roi(graph_area: Axes, colors: Dict[str, str]):
    for roi in guiVars.plotted_element_rois:
        roi.remove()
    
    guiVars.plotted_element_rois.clear()
    
    for element in guiVars.elementList:
        color = colors[element[1]]
        first = True
        
        for roi in generalVars.NIST_ROIS[element[1].strip()]:
            if roi[0] >= min(generalVars.exp_x) and roi[1] <= max(generalVars.exp_x):
                if first:
                    span = graph_area.axvspan(roi[0], roi[1], color=color, alpha=0.1, label=element[1].strip(), gid=element[1].strip())
                    graph_area.annotate(element[1], ((roi[1] + roi[0]) / 2.1, 0.95 * max(generalVars.exp_y)), color=color)
                    first = False
                else:
                    span = graph_area.axvspan(roi[0], roi[1], color=color, alpha=0.1, gid=element[1].strip())
                    graph_area.annotate(element[1], ((roi[1] + roi[0]) / 2.1, 0.95 * max(generalVars.exp_y)), color=color)
                
                
                guiVars.plotted_element_rois.append(span)
    
    graph_area.legend()

    graph_area.figure.canvas.draw_idle()