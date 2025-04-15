"""
GUI Application entry point.
The first window with the periodic table is defined here, as well as the following window where we select the atomic parameters to simulate.
We make use of Tkinter for the application interface, and several other modules for data manipulation and plotting.
"""

from __future__ import annotations

#GUI Imports
from tkinter import * # type: ignore
from tkinter import ttk

#OS Imports for paths and files
import os
from pathlib import Path

from data.variables import per_table

from aps.initializers import calculate

import logging
logging.getLogger().setLevel(logging.CRITICAL)


#GUI utils: clear window
from interface.base import clear

# Get the full path of the directory where the program is running
dir_path = Path(str(os.getcwd()) + '/')
"""
Full path of the directory where the program is running
"""

_userLine = None

# ---------------------------------------------------------------------------------------------------------------
# Configurate the window that apears after the periodic table where we choose the atomic parameters we want
def PTable(dir_path: Path, root: Tk, ap: int = -1):
    """
    Function that creates and configures the interface where we select the elements we want to simulate and quantify.
        
        Args:
            root: root element for the tk app
        
        Returns:
            Nothing this is just a wrapper for the window creation
    """
    # Set title
    root.title("Periodic Table of the Elements")
    
    root.resizable(False, False)
    
    root.geometry('850x450')

    
    # ---------------------------------------------------------------------------------------------------------------
    # Setup the window frame and grid system
    subelem = ttk.Frame(root, padding="3 3 12 12")
    """
    Window frame object
    """
    subelem.grid(column=0, row=0, sticky=(N, W, E, S)) # type: ignore
    subelem.columnconfigure(0, weight=1)
    subelem.rowconfigure(0, weight=1)
    
    
    # Set the labels and spacing around the periodic table that will be created using the grid system
    topLabel = Label(subelem, text="", font=20) # type: ignore
    topLabel.grid(row=2, column=3, columnspan=10)

    Label1 = Label(subelem, text="Click the element for which you would like to obtain the atomic parameters.", font=22) # type: ignore
    Label1.grid(row=0, column=0, columnspan=18)

    Label2 = Label(subelem, text="", font=20) # type: ignore
    Label2.grid(row=8, column=0, columnspan=18)

    Label3 = Label(subelem, text="* Lanthanoids", font=20) # type: ignore
    Label3.grid(row=9, column=1, columnspan=2)

    Label4 = Label(subelem, text="** Actinoids", font=20) # type: ignore
    Label4.grid(row=10, column=1, columnspan=2)

    for i, element in enumerate(per_table):
        Button(subelem, text=element[3], width=5, height=2, bg=element[5], command=lambda i=i: calculate(dir_path, ((i + 1), per_table[i][2]), ap, root, _userLine)).grid(row=element[6], column=element[7]) # type: ignore
    
    
    # Configure padding around the buttons
    for child in subelem.winfo_children():
        child.grid_configure(padx=0, pady=0)
    

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
        The first window is also defined here where we select the atomic parameters we wish to fetch.
            
            Args:
                self: the application object
            
            Returns:
                Nothing, we just initialize the class variables
        """
        # Default Tkinter window initialization
        Tk.__init__(self)

        # Default Tkinter window closing + create the next window where we choose the atomic parameters we want
        def quit_window(ap: int):
            """
            Function to dispose of the window and launch the window to select the element in the periodic table
                Parameters:
                    ap: atomic parameters to fetch
                
                Returns:
                    Nothing, the window is disposed of and a new one is launched
            """
            clear(self)
            
            if ap == 3:
                calculate(dir_path, (-1, ''), ap, self)
            else:
                PTable(dir_path, self, ap=ap)

        
        # Window title
        self.title("Atomic Parameters")

        self.geometry('330x75')
        
        self.resizable(False, False)
        
        # Variable to know which atomic parameter was selected
        check_var = IntVar()
        """
        Interface variable which identifies the atomic parameter selected.
            1 = Yields
            2 = Level Widths
            3 = Quantify XRF
            4 = Spectra Simulations
        """
        # Initialize as 1 (yields)
        check_var.set(1)
        
        
        # ---------------------------------------------------------------------------------------------------------------
        # Buttons and label for the interface
        ttk.Button(self, text="Get", command=lambda: quit_window(check_var.get())).grid(column=6, row=5, sticky=E, columnspan=2)
        ttk.Button(self, text="Exit", command=lambda: self.destroy()).grid(column=6, row=6, sticky=E, columnspan=2)
        ttk.Radiobutton(self, text='Yields', variable=check_var, value=1).grid(column=0, row=5, sticky=W)
        ttk.Radiobutton(self, text='Level Widths', variable=check_var, value=2).grid(column=1, row=5, sticky=W)
        ttk.Radiobutton(self, text='XRF Quantification', variable=check_var, value=3).grid(column=0, row=6, sticky=W)
        ttk.Radiobutton(self, text='Spectra Simulations', variable=check_var, value=4).grid(column=1, row=6, sticky=W)
        ttk.Label(self, text="Which parameters do you want to retrieve?").grid(column=0, row=4, sticky=W, columnspan=2)


        # Initialize the interface's main loop
        self.mainloop()


def main(userLine = None):
    """
    Main function entry point where we instantiate the application.
    """
    global _userLine
    _userLine = userLine
    
    a = App()


if __name__ == "__main__":
    main()
