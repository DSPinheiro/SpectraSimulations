from numpy import linspace
from utils.functions import G, L, V, V2
from utils.fileIO import readRates
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from tkinter import Tk, Label, StringVar, IntVar, messagebox, Radiobutton, LEFT, W, Toplevel


def task_3():
    x = linspace(-5, 5, 500)
    u = 0
    intens = 1
    res = 0
    width = 1
    fraction = .3

    fig = plt.figure()
    ax = fig.subplots()
    ax.plot(x, V(x, u, intens, res, width, fraction),
            "r-", label="Pseudo-voigt profile")
    ax.plot(x, G(x, u, intens, res, width), "b:", label="Gaussian profile")
    ax.plot(x, L(x, u, intens, res, width), "g--", label="Lorentzian profile")
    ax.plot(x, V2(x, u, intens, res, width/2.5), "k-", label="Voigt profile")
    ax.legend()

    ax_slide = plt.axes([.25, .9, .65, .03])
    #ax_slide2 = plt.axes([.25, .85, .65, .03])
    #ax_slide3 = plt.axes([.25, .8, .65, .03])
    v_factor = Slider(ax_slide, "Pseudo-Voigt Factor", valmin=0,
                      valmax=1, valinit=fraction, valstep=.05)
    #v_intens = Slider(ax_slide2, "Intens", valmin=0, valmax=2, valinit=intens, valstep=.05)
    #v_width = Slider(ax_slide3, "Width", valmin=0, valmax=4, valinit=width, valstep=.05)

    def update(val):
        ax.clear()
        ax.plot(x, V(x, u, intens, res, width, v_factor.val),
                "r-", label="Pseudo-voigt profile")
        ax.plot(x, G(x, u, intens, res, width), "b:", label="Gaussian profile")
        ax.plot(x, L(x, u, intens, res, width),
                "g--", label="Lorentzian profile")
        ax.plot(x, V2(x, u, intens, res, width/2.5),
                "k-", label="Voigt profile")
        ax.legend()
        fig.canvas.draw_idle()
    v_factor.on_changed(update)
    # v_intens.on_changed(update)
    # v_width.on_changed(update)
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

    def ShowChoice():
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
                    command=ShowChoice,
                    value=val).pack(anchor=W)

    root.mainloop()


if __name__ == "__main__":
    main()
