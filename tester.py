from numpy import linspace, array, append
from utils.functions import G, L, V, V2
from utils.fileIO import readRates
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from tkinter import Tk, Label, StringVar, IntVar, messagebox, Radiobutton, LEFT, W, Toplevel


def task_3():
    x = linspace(3100, 3107, 140)
    u = 3104.17
    intens = 2
    res = 0
    gaussian_width = .5
    lorentzian_width = .5
    fraction = .3

    hw = array([])
    counts = array([])
    counts_err = array([])
    with open("exp-SIMPA-ECRIS_2.csv", 'r') as file:
        for line in file.readlines():
            row = line.split(',')
            hw = append(hw, float(row[0]))
            counts = append(counts, float(row[1]))
            counts_err = append(counts_err, float(row[3]))

    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(111)
    fig.subplots_adjust(left=.25, bottom=.35)

    ax.plot(hw, counts, 'ko', linewidth=.75, markersize=3, label='Experimental data', mfc='none')
    ax.errorbar(hw, counts, yerr=counts_err, fmt='none', ecolor='k', elinewidth=.5, capsize=1, zorder=1)
    ax.plot(x, G(x, u, intens, res, gaussian_width), "b:", label="Gaussian profile")
    ax.plot(x, L(x, u, intens, res, lorentzian_width), "g--", label="Lorentzian profile")
    ax.plot(x, V(x, u, intens, res, gaussian_width, lorentzian_width, fraction), "r-", label="Pseudo-voigt profile")
    #ax.plot(hw, V2(hw, u, intens, res, width/2.5), "k-", label="Voigt profile")
    ax.set_xlabel('Energy (eV)')
    ax.set_ylabel('Counts/s')
    ax.legend()

    u_slider_ax = fig.add_axes([.25, .25, .65, .03])
    u_slider = Slider(u_slider_ax, 'Pseudo-Voigt fraction', 0, 1, valinit=fraction, valstep=.01)
    intensity_slider_ax = fig.add_axes([.25, .20, .65, .03])
    intensity_slider = Slider(intensity_slider_ax, 'Intensity', 1, 20, valinit=intens, valstep=.1)
    gaussian_width_slider_ax = fig.add_axes([.25, .15, .65, .03])
    gaussian_width_slider = Slider(gaussian_width_slider_ax, 'Gaussian width', .05, 5, valinit=gaussian_width, valstep=.05)
    lorentzian_width_slider_ax = fig.add_axes([.25, .1, .65, .03])
    lorentzian_width_slider = Slider(lorentzian_width_slider_ax, 'Lorentzian width', .05, 5, valinit=lorentzian_width, valstep=.05)

    def sliders_on_changed(val):
        ax.clear()
        ax.plot(hw, counts, 'ko', linewidth=.75, markersize=3, label='Experimental data', mfc='none')
        ax.errorbar(hw, counts, yerr=counts_err, fmt='none', ecolor='k', elinewidth=.5, capsize=1, zorder=1)
        ax.plot(x, G(x, u, intensity_slider.val, res, gaussian_width_slider.val), "b:", label="Gaussian profile")
        ax.plot(x, L(x, u, intensity_slider.val, res, lorentzian_width_slider.val), "g--", label="Lorentzian profile")
        ax.plot(x, V(x, u, intensity_slider.val, res, gaussian_width_slider.val, lorentzian_width_slider.val, u_slider.val), "r-", label="Pseudo-voigt profile")
        #ax.plot(hw, V2(hw, u_slider.val, intensity_slider.val, res, width/2.5), "k-", label="Voigt profile")
        ax.set_xlabel('Energy (eV)')
        ax.set_ylabel('Counts/s')
        ax.legend()
        fig.canvas.draw_idle()
    u_slider.on_changed(sliders_on_changed)
    intensity_slider.on_changed(sliders_on_changed)
    gaussian_width_slider.on_changed(sliders_on_changed)
    lorentzian_width_slider.on_changed(sliders_on_changed)

    reset_button_ax = fig.add_axes([0.8, 0.025, 0.1, 0.04])
    reset_button = Button(reset_button_ax, 'Reset', hovercolor='0.975')
    def reset_button_on_clicked(mouse_event):
        u_slider.reset()
        intensity_slider.reset()
    reset_button.on_clicked(reset_button_on_clicked)

    plt.show()


def task_4_1():
    try:
        root = Toplevel()
        root.title("Copper")

        intensity_lines = readRates("29/29-intensity.out")
        intensity_title = StringVar()
        intensity_label = Label(root, textvariable=intensity_title)
        intensity_title.set("Intensity file: 29-intensity.out")
        intensity_label.grid(row=1, column=1, padx=40)
        col_names = ('# Number', 'Shelli', '2Ji', 'Eigi', '--->', 'Shellf', '2Jf', 'Eigf', 'Energy(eV)', 'BranchingRatio', 'LevelRadYield',
                     'Intensity (eV)', 'Weight (%)', 'RadWidth (eV)', 'AugWidth (eV)', 'TotWidth (eV)')
        for i, col_name in enumerate(col_names, start=1):
            Label(root, text=col_name).grid(row=3, column=i, padx=40)

        table = ['\t'.join(line) for line in intensity_lines[:10]]
        for i, row in enumerate(table, start=4):
            for j, col in enumerate(col_names, start=0):
                Label(root, text=row.split('\t')[j]).grid(row=i, column=j+1)

        augrate_lines = readRates("29/29-augrate.out")
        augrate_title = StringVar()
        augrate_label = Label(root, textvariable=augrate_title)
        augrate_title.set("\nAugrate file: 29-augrate.out")
        augrate_label.grid(row=14, column=1, padx=40)
        col_names = ('# Record', 'Shelli', '2Ji', 'Eigi', '--->', 'Shellf',
                     '2Jf', 'Eigf', 'Energy (eV)', 'Rate (1/s)', 'Width (eV)')
        for i, col_name in enumerate(col_names, start=1):
            Label(root, text=col_name).grid(row=15, column=i, padx=40)

        table = ['\t'.join(line) for line in augrate_lines[:10]]
        for i, row in enumerate(table, start=16):
            for j, col in enumerate(col_names, start=0):
                Label(root, text=row.split('\t')[j]).grid(row=i, column=j+1)

        root.mainloop()

    except Exception as e:
        messagebox.showerror("Error", str(e))


def main():
    root = Tk()

    v = IntVar()
    v.set(1)  # initializing the choice, i.e. Python

    languages = [("Task 3", 3),
                 ("Task 4", 4.1)]

    def show_choice():
        option = v.get()
        if option == 3:
            task_3()
        elif option == 4.1:
            task_4_1()

    Label(root,
          text="Choose task:",
          justify=LEFT,
          padx=20).pack()

    for language, val in languages:
        Radiobutton(root,
                    text=language,
                    padx=20,
                    variable=v,
                    command=show_choice,
                    value=val).pack(anchor=W)

    root.mainloop()


if __name__ == "__main__":
    task_3()
