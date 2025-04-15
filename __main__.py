from pathlib import Path
from runpy import run_path

pkg_dir = Path(__file__).resolve().parent

def launchGUI():
    script_pth = pkg_dir / "SpectraSimulation.py"
    run_path(str(script_pth), run_name="__main__")

def launchHeadless():
    script_pth = pkg_dir / "SpectraSimulation_headless.py"
    run_path(str(script_pth), run_name="__main__")