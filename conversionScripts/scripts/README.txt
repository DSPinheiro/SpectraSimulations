Use the masterConverter.py script first and don't forget to change the ground configuration and energy at the top of the script.
You will need the directory with the configuration calculations.
This script will compile information about each configuration/level used in the transitions later on, including the conversion between formats.
It will also calculate energies and widths necessary for more detailed simulations.
This script will later on be included in the calculation running script in the cluster.
In this way we only need to download 1 file from the cluster instead of a full directory.

After running this script for the configuration type you would like to convert, you can run the conversion scripts for the transitions involving these configurations.