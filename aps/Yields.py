"""
Module that implements the fluorescence and non radiative yields interface.
First we search and read all the required files to calculate the selected element's yields.
Second we initialize the Tkinter interface and present the values calculated from the input data
"""

#GUI Imports
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

#File IO Imports
from utils.fileIO import file_namer, write_to_xls

#GUI utils: destroy window
from utils.interface import destroy


def fetchYields(dir_path, z):
    """
    Function to run the yields interface
        
        Args:
            dir_path: full path to the location where the application is ran
            z: z value of the element to simulate
            
        Returns:
            Nothing, we just setup the interface and all commands are bound and performed through the interface
    """
    # This can be moved to the fileIO module later
    # Path to the file with the yields for this element
    yields_file = dir_path / str(z) / (str(z) + '-yields.out')
    """
    Variable with the full path to the yields file of this element
    """
    try:
        with open(yields_file, 'r') as yields:
            # Write the lines into a list
            lineyields = [x.strip('\n').split() for x in yields.readlines()]
            """
            Variable to hold the yields data that was read from the file
            """
            # Remove empty strings from possible uneven formating
            lineyields = list(filter(None, lineyields))
        
        # Create a window to display the yields
        atdata = Toplevel()
        """
        Variable to hold the tkinter yields window object
        """
        # Window title
        atdata.title("Fluorescence and nonRadiative Yields")
        
        # Make a frame in the window and initialize a grid positioning and resising for the results
        atdatayields = ttk.Frame(atdata, padding="3 3 12 12")
        """
        Frame with the grid system that will be used to position the data in the interface
        """
        atdatayields.grid(column=0, row=0, sticky=(N, W, E, S))
        atdatayields.columnconfigure(0, weight=1)
        atdatayields.rowconfigure(0, weight=1)
        
        # Label objects to show the various types of yields
        ttk.Label(atdatayields, text="Fluorescence Yields").grid(column=0, row=0, sticky=W, columnspan=2)
        ttk.Label(atdatayields, text="Auger Yields").grid(column=5, row=0, sticky=W, columnspan=2)
        ttk.Label(atdatayields, text="Coster-Kronig Yields").grid(column=8, row=0, sticky=W, columnspan=2)
        
        # Buttons for the export and program flow functions
        ttk.Button(master=atdatayields, text='Export', command=lambda: write_to_xls(1)).grid(column=12, row=0, sticky=W, columnspan=2)
        ttk.Button(master=atdatayields, text='Back', command=lambda: destroy(atdata)).grid(column=12, row=1, sticky=W, columnspan=2)
        ttk.Button(master=atdatayields, text='Exit', command=lambda: destroy(atdata)).grid(column=12, row=2, sticky=W, columnspan=2)

        # Variable to control if we show the non radiative yields
        NR = False
        """
        Variable to control if we show the non radiative yields
        """
        # Row counter for the fluorescence yields position
        n1 = 1
        """
        Row counter for the fluorescence yields position
        """
        # Row counter for the Auger yields position
        n2 = 1
        """
        Row counter for the Auger yields position
        """
        # Row counter for the Coster-Kronig yields position
        n3 = 1
        """
        Row counter for the Coster-Kronig yields position
        """
        
        # Loop the lines of the file and read the yields
        for j in lineyields:
            if j[1] == 'FLyield' and j[0] != '':
                print('FY_' + j[0], '=', j[2])
                ttk.Label(atdatayields, text='FY_' + j[0] + '=' + j[2]).grid(column=0, row=n1, sticky=W, columnspan=2)
                n1 = n1 + 1
            elif j[1] == 'NRyield' and j[0] != '':
                print('AY_' + j[0], '=', j[2])
                ttk.Label(atdatayields, text='AY_' + j[0] + '=' + j[2]).grid(column=5, row=n2, sticky=W, columnspan=2)
                n2 = n2 + 1
            elif j[1] == 'Non' and j[2] == 'Radiative' and j[3] == 'Yields':
                NR = True
            
            if j[0] == 'L1' and j[2] == 'L2' and NR == True:
                print('fL12_', '=', j[3])
                ttk.Label(atdatayields, text='fL12_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                n3 = n3 + 1
            elif j[0] == 'L1' and j[2] == 'L3' and NR == True:
                print('fL13_', '=', j[3])
                ttk.Label(atdatayields, text='fL13_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                n3 = n3 + 1
            elif j[0] == 'L2' and j[2] == 'L3' and NR == True:
                print('fL23_', '=', j[3])
                ttk.Label(atdatayields, text='fL23_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                n3 = n3 + 1
            elif j[0] == 'M1' and j[2] == 'M2' and NR == True:
                print('fM12_', '=', j[3])
                ttk.Label(atdatayields, text='fM12_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                n3 = n3 + 1
            elif j[0] == 'M1' and j[2] == 'M3' and NR == True:
                print('fM13_', '=', j[3])
                ttk.Label(atdatayields, text='fM13_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                n3 = n3 + 1
            elif j[0] == 'M1' and j[2] == 'M4' and NR == True:
                print('fM14_', '=', j[3])
                ttk.Label(atdatayields, text='fM14_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                n3 = n3 + 1
            elif j[0] == 'M1' and j[2] == 'M5' and NR == True:
                print('fM15_', '=', j[3])
                ttk.Label(atdatayields, text='fM15_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                n3 = n3 + 1
            elif j[0] == 'M2' and j[2] == 'M3' and NR == True:
                print('fM23_', '=', j[3])
                ttk.Label(atdatayields, text='fM23_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                n3 = n3 + 1
            elif j[0] == 'M2' and j[2] == 'M4' and NR == True:
                print('fM24_', '=', j[3])
                ttk.Label(atdatayields, text='fM24_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                n3 = n3 + 1
            elif j[0] == 'M2' and j[2] == 'M5' and NR == True:
                print('fM25_', '=', j[3])
                ttk.Label(atdatayields, text='fM25_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                n3 = n3 + 1
            elif j[0] == 'M3' and j[2] == 'M4' and NR == True:
                print('fM34_', '=', j[3])
                ttk.Label(atdatayields, text='fM34_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                n3 = n3 + 1
            elif j[0] == 'M3' and j[2] == 'M5' and NR == True:
                print('fM35_', '=', j[3])
                ttk.Label(atdatayields, text='fM35_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                n3 = n3 + 1
            elif j[0] == 'M4' and j[2] == 'M5' and NR == True:
                print('fM45_', '=', j[3])
                ttk.Label(atdatayields, text='fM45_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                n3 = n3 + 1
    except FileNotFoundError:
        messagebox.showerror("Error", "Required File is Missing")