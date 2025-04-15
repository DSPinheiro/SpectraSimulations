"""
Module with base window management functions.
"""

from __future__ import annotations

import data.variables as generalVars

import interface.variables as guiVars

from interface.updaters import dict_updater

#GUI Imports
from tkinter import Tk, Toplevel, Canvas
from tkinter import ttk
from tkinter.constants import *

# --------------------------------------------------------- #
#                                                           #
#               WINDOW MANAGEMENT FUNCTIONS                 #
#                                                           #
# --------------------------------------------------------- #

# Function to destroy the window and free memory properly
def destroy(window: Tk | Toplevel):
    """
    Function to destroy the window and free memory properly
    
        Args:
            window: the window to be disposed of
        
        Returns:
            Nothing, the window is disposed of and the program continues
    """
    window.destroy()

# Function to clear the window and free memory properly
def clear(window: Tk | Toplevel):
    """
    Function to destroy the window and free memory properly
    
        Args:
            window: the window to be disposed of
        
        Returns:
            Nothing, the window is disposed of and the program continues
    """
    for widget in window.winfo_children():
        widget.destroy()


# Function to deselect all selected transitions when exiting the simulation window
def _quit():
    """
    Private function to deselect all selected transitions when exiting the simulation window
        
        Args:
            
        
        Returns:
            Nothing, the transition dictionaries are reset and the simulation window is disposed of
    """
    original = guiVars.satelite_var.get() # type: ignore

    guiVars.satelite_var.set('Diagram') # type: ignore

    for transition in generalVars.the_dictionary:
        if generalVars.the_dictionary[transition]["selected_state"]:
            dict_updater(transition)

    guiVars.satelite_var.set('Auger') # type: ignore

    for transition in generalVars.the_aug_dictionary:
        if generalVars.the_aug_dictionary[transition]["selected_state"]:
            dict_updater(transition)

    guiVars.satelite_var.set(original) # type: ignore

    guiVars._parent.quit()  # stops mainloop # type: ignore
    guiVars._parent.destroy()  # this is necessary on Windows to prevent fatal Python Error: PyEval_RestoreThread: NULL tstate # type: ignore

# Function to deselect all selected transitions and restart the whole app
def restarter():
    """
    Private function to deselect all selected transitions and restart the whole application
        
        Args:
            
        
        Returns:
            Nothing, the transition dictionaries are reset and the tkinter windows are disposed of
    """
    original = guiVars.satelite_var.get() # type: ignore

    guiVars.satelite_var.set('Diagram') # type: ignore

    for transition in generalVars.the_dictionary:
        if generalVars.the_dictionary[transition]["selected_state"]:
            dict_updater(transition)

    guiVars.satelite_var.set('Auger') # type: ignore

    for transition in generalVars.the_aug_dictionary:
        if generalVars.the_aug_dictionary[transition]["selected_state"]:
            dict_updater(transition)

    guiVars.satelite_var.set(original) # type: ignore

    guiVars._parent.quit()  # stops mainloop # type: ignore
    guiVars._parent.destroy() # type: ignore
    main()  # this is necessary on Windows to prevent fatal Python Error: PyEval_RestoreThread: NULL tstate # type: ignore

# Based on
#   https://web.archive.org/web/20170514022131id_/http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame

class VerticalScrolledFrame(ttk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame.
    * Construct and pack/place/grid normally.
    * This frame only allows vertical scrolling.
    """
    def __init__(self, parent, *args, **kw):
        self.parent = parent
        
        ttk.Frame.__init__(self, parent, *args, **kw)

        # Create a canvas object and a vertical scrollbar for scrolling it.
        vscrollbar = ttk.Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = Canvas(self, bd=0, highlightthickness=0,
                           yscrollcommand=vscrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)

        # Reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)
        
        # Create a frame inside the canvas which will be scrolled with it.
        self.interior = interior = ttk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=NW)
        
        # Track changes to the canvas and frame width and sync them,
        # also updating the scrollbar.
        def _configure_interior(event):
            # Update the scrollbars to match the size of the inner frame.
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion=(0, 0, size[0], size[1]))
            
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the canvas's width to fit the inner frame.
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the inner frame's width to fill the canvas.
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)
        
        def _on_mousewheel(event):
            delta = event.delta
            canvas.yview_scroll(-1*delta, "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        interior.bind("<MouseWheel>", _on_mousewheel)
        vscrollbar.bind("<MouseWheel>", _on_mousewheel)