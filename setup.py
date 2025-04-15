from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='SpectraSimulation',
    version='0.2.0',    
    description='Simulation Program for calculating synthetic spectra from theoretical data.',
    url='https://github.com/DSPinheiro/SpectraSimulations',
    author='Daniel Pinheiro',
    author_email='ds.pinheiro@campus.fct.unl.pt',
    license='MIT',
    
    packages=['SpectraSimulations',
                'SpectraSimulations.aps',
                'SpectraSimulations.data',
                'SpectraSimulations.interface',
                'SpectraSimulations.simulation',
                'SpectraSimulations.utils',
                    'SpectraSimulations.utils.crossSections',
                    'SpectraSimulations.utils.experimental',
                    'SpectraSimulations.utils.misc',
                'SpectraSimulations.conversionScripts',
                    'SpectraSimulations.conversionScripts.scripts',
                        'SpectraSimulations.conversionScripts.scripts.auger',
                        'SpectraSimulations.conversionScripts.scripts.diagram',
                        'SpectraSimulations.conversionScripts.scripts.excitation',
            ],

    include_package_data=True,
    package_data={"SpectraSimulations": ["dbs/*.txt", "29/*.out"]},
    
    install_requires=['tk',
                      'numpy',
                      'scipy',
                      'lmfit',
                      'matplotlib',
                      'plotly',
                      'mplcursors',
                      'scikit-learn',
                      'pybaselines',
                      'iminuit',
                      'scienceplots',
                      ],
    
    entry_points={'console_scripts': ['SpectraSimulations=SpectraSimulations.__main__:launchGUI',
                                      'SpectraSimulations_headless=SpectraSimulations.__main__:launchHeadless'],},
    
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',  
        'Operating System :: OS Independent',        
        'Programming Language :: Python :: 3',
    ],
    
    long_description=long_description,
    long_description_content_type='text/markdown'
)