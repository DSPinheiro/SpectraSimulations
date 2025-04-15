"""
Package containg the interface related modules that create and manage the GUI
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import matplotlib.pyplot as plt
import scienceplots

plt.style.use("science")