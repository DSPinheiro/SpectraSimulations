import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from tkinter import Tk, IntVar, Label, Radiobutton, LEFT, W, Toplevel, StringVar, messagebox, OptionMenu
from numpy import linspace

import data.variables as generalVars
from utils.functions import G, L, pseudoV, updateRadTransitionVals, calculateResidues
from utils.fileIO import readRates


def test_pseudo_voigt():
    u = 3104.17
    x = linspace(u-5, u+5, 400)
    offset = 0
    intens = 2
    res = 0
    gaussian_width = 1
    lorentzian_width = 1
    fraction = .2
    global file_loaded, exp, gaussian, lorentzian, voigt
    file_loaded = False

    hw = []
    counts = []
    counts_err = []
    with open("exp-SIMPA-ECRIS.csv", 'r') as file:
        for line in file.readlines():
            row = line.split(',')
            hw.append(float(row[0]))
            counts.append(float(row[1]))
            counts_err.append(float(row[3]))

    fig = plt.figure(figsize=(12, 6))
    fig.canvas.manager.set_window_title('Pseudo-Voigt profile')
    ax = fig.add_subplot(111)
    fig.subplots_adjust(left=.1, bottom=.35)

    gaussian, = ax.plot(x, offset + G(x, u, intens, res, gaussian_width), "b:", label="Gaussian profile")
    lorentzian, = ax.plot(x, offset + L(x, u, intens, res, lorentzian_width), "g--", label="Lorentzian profile")
    voigt, = ax.plot(x, offset + pseudoV(x, u, intens, res, gaussian_width, lorentzian_width, fraction), "r-", label="Pseudo-voigt profile")
    ax.set_xlabel('Energy (eV)')
    ax.set_ylabel('Counts/s')
    ax.legend()

    offset_slider_ax = fig.add_axes([.15, .25, .65, .03])
    offset_slider = Slider(offset_slider_ax, 'Offset', 0, 2, valinit=offset, valstep=.05)
    intensity_slider_ax = fig.add_axes([.15, .20, .65, .03])
    intensity_slider = Slider(intensity_slider_ax, 'Intensity', 1, 20, valinit=intens, valstep=.05)
    fraction_slider_ax = fig.add_axes([.15, .15, .65, .03])
    fraction_slider = Slider(fraction_slider_ax, 'Pseudo-Voigt fraction', 0, 1, valinit=fraction, valstep=.05)
    gaussian_width_slider_ax = fig.add_axes([.15, .1, .65, .03])
    gaussian_width_slider = Slider(gaussian_width_slider_ax, 'Gaussian width', .05, 2, valinit=gaussian_width, valstep=.05)
    lorentzian_width_slider_ax = fig.add_axes([.15, .05, .65, .03])
    lorentzian_width_slider = Slider(lorentzian_width_slider_ax, 'Lorentzian width', .05, 2, valinit=lorentzian_width, valstep=.05)

    def sliders_on_changed(_):
        if file_loaded:
            generalVars.ytot = pseudoV(x, u, intensity_slider.val, res, gaussian_width_slider.val, lorentzian_width_slider.val, fraction_slider.val)
            red_chi_sum = calculateResidues(hw, counts, counts_err, x, 0, 1, 'No', offset_slider.val, 5, None)
            ax.legend(title=r"$\chi_{red}^2 = $" + "{:.2f}".format(red_chi_sum))
        else:
            gaussian.set_ydata(offset_slider.val + G(x, u, intensity_slider.val, res, gaussian_width_slider.val))
            lorentzian.set_ydata(offset_slider.val + L(x, u, intensity_slider.val, res, gaussian_width_slider.val))
        voigt.set_ydata(offset_slider.val + pseudoV(x, u, intensity_slider.val, res, gaussian_width_slider.val, lorentzian_width_slider.val, fraction_slider.val))
        ax.relim()
        ax.autoscale_view()
        fig.canvas.draw_idle()
    fraction_slider.on_changed(sliders_on_changed)
    intensity_slider.on_changed(sliders_on_changed)
    gaussian_width_slider.on_changed(sliders_on_changed)
    lorentzian_width_slider.on_changed(sliders_on_changed)
    offset_slider.on_changed(sliders_on_changed)

    load_button_ax = fig.add_axes([.85, .25, .1, .04])
    load_button = Button(load_button_ax, 'Load file', hovercolor='0.975')

    def load_data_on_clicked(_):
        global file_loaded, exp, exp_err
        if file_loaded: return
        exp, = ax.plot(hw, counts, 'ko', linewidth=.75, markersize=3, label='Experimental data', mfc='none')
        exp_err = ax.errorbar(hw, counts, yerr=counts_err, fmt='none', ecolor='k', elinewidth=.5, capsize=1, zorder=1)
        gaussian.remove()
        lorentzian.remove()
        generalVars.ytot = pseudoV(x, u, intensity_slider.val, res, gaussian_width_slider.val, lorentzian_width_slider.val, fraction_slider.val)
        red_chi_sum = calculateResidues(hw, counts, counts_err, x, 0, 1, 'No', offset_slider.val, 5, None)
        ax.legend(title=r"$\chi_{red}^2 = $" + "{:.2f}".format(red_chi_sum))
        file_loaded = True
    load_button.on_clicked(load_data_on_clicked)

    reset_button_ax = fig.add_axes([.85, .2, 0.1, .04])
    reset_button = Button(reset_button_ax, 'Reset', hovercolor='0.975')

    def reset_button_on_clicked(_):
        global file_loaded, gaussian, lorentzian, voigt
        if file_loaded:
            exp.remove()
            exp_err.remove()
            gaussian, = ax.plot(x, offset + G(x, u, intens, res, gaussian_width), "b:", label="Gaussian profile")
            lorentzian, = ax.plot(x, offset + L(x, u, intens, res, lorentzian_width), "g--", label="Lorentzian profile")
            voigt.set_zorder(20)
            ax.legend(title="")
        file_loaded = False
        fraction_slider.reset()
        intensity_slider.reset()
        gaussian_width_slider.reset()
        lorentzian_width_slider.reset()
        offset_slider.reset()
        fig.canvas.draw_idle()
    reset_button.on_clicked(reset_button_on_clicked)

    plt.show()


def test_read_rates():
    try:
        root = Tk()
        root.title("Iron data files")

        intensity_lines = readRates("26/26-intensity.out")
        print("Intensity lines:\n")
        print(intensity_lines[:5])

        intensity_title = StringVar()
        intensity_label = Label(root, textvariable=intensity_title)
        intensity_title.set("Intensity file: 26-intensity.out")
        intensity_label.grid(row=1, column=1, padx=40)

        col_names = ('# Number', 'Shelli', '2Ji', 'Eigi', '--->', 'Shellf', '2Jf', 'Eigf',
                     'Energy(eV)', 'BranchingRatio', 'LevelRadYield', 'Intensity (eV)',
                     'Weight (%)', 'RadWidth (eV)', 'AugWidth (eV)', 'TotWidth (eV)')
        for i, col_name in enumerate(col_names, start=1):
            Label(root, text=col_name).grid(row=3, column=i, padx=40)

        table = ['\t'.join(line) for line in intensity_lines[:10]]
        for i, row in enumerate(table, start=4):
            for j, _ in enumerate(col_names, start=0):
                if j >= len(row.split('\t')):
                    break
                Label(root, text=row.split('\t')[j]).grid(row=i, column=j+1)

        augrate_lines = readRates("26/26-augrate.out")
        print("\nAuger rates:\n")
        print(intensity_lines[:5])

        augrate_title = StringVar()
        augrate_label = Label(root, textvariable=augrate_title)
        augrate_title.set("Auger rates file: 26-augrate.out")
        augrate_label.grid(row=14, column=1, padx=40)

        col_names = ('# Record', 'Shelli', '2Ji', 'Eigi', '--->', 'Shellf',
                     '2Jf', 'Eigf', 'Energy (eV)', 'Rate (1/s)', 'Width (eV)')
        for i, col_name in enumerate(col_names, start=1):
            Label(root, text=col_name).grid(row=15, column=i, padx=40)

        table = ['\t'.join(line) for line in augrate_lines[:10]]
        for i, row in enumerate(table, start=16):
            for j, _ in enumerate(col_names, start=0):
                if j >= len(row.split('\t')):
                    break
                Label(root, text=row.split('\t')[j]).grid(row=i, column=j+1)

        root.mainloop()

    except Exception as e:
        messagebox.showerror("Error", str(e))


def test_update_trans_vals():
    try:
        root = Tk()
        root.title("Read transition values")
        root.geometry("800x250")

        generalVars.lineradrates = readRates("26/26-intensity.out")
        generalVars.linesatellites = readRates("26/26-augrate.out")

        intensity_title = StringVar()
        intensity_label = Label(root, textvariable=intensity_title)
        intensity_title.set("Intensity file: 26-intensity.out\nAuger file: 26-augrate.out")
        intensity_label.grid(row=1, column=2, padx=40, sticky="W")

        def runOption(_):
            option = clicked.get()
            num_of_transitions, low_level, high_level, diag_stick_val, sat_stick_val = updateRadTransitionVals(
                option, 0)
            Label(root, text=option).grid(row=3, column=2, sticky="W")
            Label(root, text=str(num_of_transitions)).grid(
                row=4, column=2, sticky="W")
            Label(root, text=str(low_level)).grid(
                row=5, column=2, sticky="W")
            Label(root, text=str(high_level)).grid(
                row=6, column=2, sticky="W")
            Label(root, text=str(diag_stick_val[:2]).replace(
                "], [", "],\n[")).grid(row=7, column=2, sticky="W")
            Label(root, text=str(sat_stick_val[:2]).replace(
                "], [", "],\n[")).grid(row=8, column=2, sticky="W")

        options = [transition for transition in generalVars.the_dictionary]
        clicked = StringVar()

        Label(root, text="Choose transition: ").grid(row=2, column=1, sticky="E")
        drop_menu = OptionMenu(root, clicked, *options, command=runOption)
        drop_menu.grid(row=2, column=2, sticky="W")

        Label(root, text="Transition: ").grid(row=3, column=1, sticky="E")
        Label(root, text="Number of transitions: ").grid(row=4, column=1, sticky="E")
        Label(root, text="Low level: ").grid(row=5, column=1, sticky="E")
        Label(root, text="High level: ").grid(row=6, column=1, sticky="E")
        Label(root, text="Diagram stick val: ").grid(row=7, column=1, sticky="E")
        Label(root, text="Sattelite transintions: ").grid(row=8, column=1, sticky="E")

        root.mainloop()

    except Exception as e:
        messagebox.showerror("Error", str(e))


def main():
    root = Tk()
    root.title("Tester")

    v = IntVar()
    v.set(1)

    options = [("Pseudo-Voigt profile fit", 1),
               ("Read database file", 2),
               ("Test the radiative and satellite rates updater", 3)]

    def run_choice():
        option = v.get()
        root.destroy()
        if option == 1:
            test_pseudo_voigt()
        elif option == 2:
            test_read_rates()
        elif option == 3:
            test_update_trans_vals()

    Label(root,
          text="Choose the task:\n",
          justify=LEFT,
          padx=20).pack()

    for option, val in options:
        Radiobutton(root,
                    text=option,
                    padx=20,
                    variable=v,
                    command=run_choice,
                    value=val).pack(anchor=W)

    root.mainloop()


if __name__ == "__main__":
    main()
