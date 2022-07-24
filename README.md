
[//]: # (If you want to render this markdown in your browser you can install the Markdown Preview Plus extension)

# SpectraSimulations
Latestest version of the spectra simulation program, including simulation for ionic mixtures. 

## Install instructions (Anaconda)

First install the anaconda distribution for your system.
This will install the most recent python distribution and several other programs such as the spyder editor, as well as manage your python environments.

These enviornments provide you a clean install of python where you can install different versions of python, and different sets of packages without worrying about compatibility issues.

You can follow the installation instructions on the official [Anaconda website](https://docs.anaconda.com/anaconda/install/).

## Install instructions (package requirements)

After you have confirmed your python installation is working properlly install the required packages using the provided requirements.txt file.

You can install this in the default environment as these packages are often used in most python programs, alternatively you can create a new conda environment to install these packages with the command:

	conda create --name SpecSim python=3.8

and to activate the environment on windows:

	activate SpecSim

on linux or mac:

	source activate SpecSim

Finally, to install the packages:

    pip install -r requirements.txt

After, execute the test script "importTest.py" to make sure everything is properly installed.

The output is color coded, so if every line is green everything should be correct.
