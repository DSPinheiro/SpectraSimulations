"""
Module that implements the line and level widths interface.
The interface barebones is implemented but no data is being processed and shown.
"""

#GUI Imports
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

#File IO Imports
from utils.fileIO import file_namer, write_to_xls

#GUI utils: destroy window
from utils.interface import destroy


def fetchWidths(dir_path, z):
    """
    Function to run the cross sections interface
        
        Args:
            dir_path: full path to the location where the application is ran
            z: z value of the element to simulate
            
        Returns:
            Not fully implemented, only the base interface
    """
    try:
        # This can be moved to the fileIO module later
        # Path to the file with the widths for this element
        radrates_file = dir_path / str(z) / (str(z) + '-radrate.out')
        with open(radrates_file, 'r') as radrates:
            # Write the lines into a list
            generalVars.lineradrates = [x.strip('\n').split() for x in radrates.readlines()]
            # Remove empty strings from possible uneven formating
            generalVars.lineradrates = list(filter(None, generalVars.lineradrates))

        # Create a window to display the widths
        atdata = Toplevel()
        """
        Variable to hold the tkinter widths window object
        """
        # Window title
        atdata.title("Level and Line Widths")
        
        # Make a frame in the window and initialize a grid positioning and resising for the results
        atdatayields = ttk.Frame(atdata, padding="3 3 12 12")
        """
        Frame with the grid system that will be used to position the data in the interface
        """
        atdatayields.grid(column=0, row=0, sticky=(N, W, E, S))
        atdatayields.columnconfigure(0, weight=1)
        atdatayields.rowconfigure(0, weight=1)
        
        # Label objects to show the level and line widths
        ttk.Label(atdatayields, text="Level Widths").grid(column=0, row=0, sticky=W, columnspan=2)
        ttk.Label(atdatayields, text="Line Widths").grid(column=5, row=0, sticky=W, columnspan=2)
        
        # Buttons for the export and program flow functions
        ttk.Button(master=atdatayields, text='Export', command=lambda: write_to_xls(2)).grid(column=12, row=0, sticky=W, columnspan=2)
        ttk.Button(master=atdatayields, text='Back', command=lambda: destroy(atdata)).grid(column=12, row=1, sticky=W, columnspan=2)
        ttk.Button(master=atdatayields, text='Exit', command=lambda: destroy(atdata)).grid(column=12, row=2, sticky=W, columnspan=2)
        
        # NOT FURTHER IMPLEMENTED
        
    except FileNotFoundError:
        messagebox.showerror("Error", "Required File is Missing")