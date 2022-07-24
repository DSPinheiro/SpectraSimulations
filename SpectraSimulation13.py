"""
Application entry point.
The first window with the periodic table is defined here, as well as the following window where we select the atomic parameters to simulate.
We make use of Tkinter for the application interface, and several other modules for data manipulation and plotting.
"""

# GUI Imports
from tkinter import *
from tkinter import ttk

# OS Imports for paths and files
import os
from pathlib import Path

# Module Imports: Atomic Parameter Selection
from aps.Yields import fetchYields
from aps.LvlWidths import fetchWidths
from aps.CrossSections import fetchSections
from aps.SpecSimu import simulateSpectra

# Static data import: periodic table values
from data.variables import per_table

# GUI utils: destroy window
from utils.interface import destroy

# Get the full path of the directory where the program is running
dir_path = Path(str(os.getcwd()) + '/')
"""
Full path of the directory where the program is running
"""

# ---------------------------------------------------------------------------------------------------------------
# Function to choose the type of atomic parameters we want to fetch after selecting the element


def calculate(element, ap, parent):
    """
    Function that launches the correct atomic parameter simulation after selection on the interface.

        Args:
            element: list with the z value of the element to simulate and the name of the element
            ap: integer identifying which atomic parameter was selected in the interface
            parent: parent window object, i.e. the master window where we bind following graphical objects to

        Returns:
            If the function executed correctly it will return 0 (C style)
    """
    if ap == 1:
        fetchYields(dir_path, element)
    # ---------------------------------------------------------------------------------------------------------------
    elif ap == 2:
        fetchWidths(dir_path, element)
    # ---------------------------------------------------------------------------------------------------------------
    elif ap == 3:
        fetchSections(dir_path, element)
    # ---------------------------------------------------------------------------------------------------------------
    elif ap == 4:
        simulateSpectra(dir_path, element, parent)
    return 0

# ---------------------------------------------------------------------------------------------------------------
# Configurate the window that apears after the periodic table where we choose the atomic parameters we want


def params(element):
    """
    Function that creates and configures the interface where we select which atomic parameters we want to simulate.

        Args:
            element: list with the z value of the element to simulate and the name of the element

        Returns:
            Nothing this is just a wrapper for the window creation
    """
    # Create new window to select the atomic parameters
    parameters = Tk()
    """Window object"""

    # Window title
    parameters.title("Atomic Parameters")

    # Variable to know which atomic parameter was selected
    check_var = IntVar()
    """
    Interface variable which identifies the atomic parameter selected.
        1 = Yields
        2 = Level Widths
        3 = Cross Sections
        4 = Spectra Simulations
    """

    # Initialize as 1 (yields)
    check_var.set(1)

    # ---------------------------------------------------------------------------------------------------------------
    # Setup the window frame and grid system
    subelem = ttk.Frame(parameters, padding="3 3 12 12")
    """Window frame object"""

    subelem.grid(column=0, row=0, sticky=(N, W, E, S))
    subelem.columnconfigure(0, weight=1)
    subelem.rowconfigure(0, weight=1)

    # ---------------------------------------------------------------------------------------------------------------
    # Buttons and label for the interface
    ttk.Button(subelem, text="Get", command=lambda: calculate(element, check_var.get(), parameters)).grid(column=6, row=5, sticky=E, columnspan=2)
    ttk.Button(subelem, text="Exit", command=lambda: destroy(parameters)).grid(column=6, row=6, sticky=E, columnspan=2)
    ttk.Radiobutton(subelem, text='Yields', variable=check_var, value=1).grid(column=0, row=5, sticky=W)
    ttk.Radiobutton(subelem, text='Level Widths', variable=check_var, value=2).grid(column=1, row=5, sticky=W)
    ttk.Radiobutton(subelem, text='Cross Sections', variable=check_var, value=3).grid(column=0, row=6, sticky=W)
    ttk.Radiobutton(subelem, text='Spectra Simulations', variable=check_var, value=4).grid(column=1, row=6, sticky=W)
    ttk.Label(subelem, text="Which parameters do you want to retrieve?").grid(column=0, row=4, sticky=W, columnspan=2)

    subelem.mainloop()

# ---------------------------------------------------------------------------------------------------------------
# Define our Tkinter GUI application entry point


class App(Tk):
    """
    Main application class.
    This is the Tkinter interface application entry point
    """

    # Define how to initialize the window
    def __init__(self):
        """
        Initialization function for the application.
        The first window is also defined here where we show a periodic table from which we can select the element we want to simulate.

            Args:
                self: the application object

            Returns:
                Nothing, we just initialize the class variables
        """
        # Default Tkinter window initialization
        Tk.__init__(self)

        # Default Tkinter window closing + create the next window where we choose the atomic parameters we want
        def quit_window(element):
            """
            Function to dispose of the window and launch the window to select the atomic parameters
                Parameters:
                    element: list with the z value of the element to simulate and the name of the element

                Returns:
                    Nothing, the window is disposed of and a new one is launched
            """
            self.destroy()
            params(element)

        # Set title
        self.title("Periodic Table of the Elements")

        # Set the labels and spacing around the periodic table that will be created using the grid system
        self.topLabel = Label(self, text="", font=20)
        self.topLabel.grid(row=2, column=3, columnspan=10)

        self.Label1 = Label(self, text="Click the element for which you would like to obtain the atomic parameters.", font=22)
        self.Label1.grid(row=0, column=0, columnspan=18)

        self.Label2 = Label(self, text="", font=20)
        self.Label2.grid(row=8, column=0, columnspan=18)

        self.Label3 = Label(self, text="* Lanthanoids", font=20)
        self.Label3.grid(row=9, column=1, columnspan=2)

        self.Label4 = Label(self, text="** Actinoids", font=20)
        self.Label4.grid(row=10, column=1, columnspan=2)

        # Create all buttons for the periodic table with a loop
        for i, element in enumerate(per_table):
            Button(self, text=element[3], width=5, height=2, bg=element[5],command=lambda i=i: quit_window([(i + 1), per_table[i][2]])).grid(row=element[6], column=element[7])

        # Configure padding around the buttons
        for child in self.winfo_children():
            child.grid_configure(padx=3, pady=3)

        # Initialize the interface's main loop
        self.mainloop()


def main():
    """
    Main function entry point where we instantiate the application.
    """
    a = App()


if __name__ == "__main__":
    main()
