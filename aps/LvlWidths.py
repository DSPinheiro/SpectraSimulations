#GUI Imports
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

#File IO Imports
from utils.fileIO import file_namer, write_to_xls

#GUI utils: destroy window
from utils.interface import destroy


def fetchWidths(dir_path, z):
    try:
        # Caminho do ficheiro na pasta com o nome igual ao numero atomico que tem as yields
        radrates_file = dir_path / str(z) / (str(z) + '-radrate.out')
        with open(radrates_file, 'r') as radrates:  # Abrir o ficheiro
            # Escrever todas as linhas no ficheiro como uma lista
            generalVars.lineradrates = [x.strip('\n').split() for x in radrates.readlines()]
            # Remover as linhas compostas apenas por celulas vazias
            generalVars.lineradrates = list(filter(None, generalVars.lineradrates))

        # criar uma janela onde serao apresentados os resultados dos yields, widths, cross sections ou spectra
        # simulations
        atdata = Toplevel()
        atdata.title("Level and Line Widths")  # titulo da janela
        # Criar uma grelha dentro da janela onde serao inseridos os dados
        atdatayields = ttk.Frame(atdata, padding="3 3 12 12")
        atdatayields.grid(column=0, row=0, sticky=(N, W, E, S))
        atdatayields.columnconfigure(0, weight=1)
        atdatayields.rowconfigure(0, weight=1)
        # Labels dos dados na janela
        # Label abaixo do qual serao escritos os resultados dos level widths
        ttk.Label(atdatayields, text="Level Widths").grid(
            column=0, row=0, sticky=W, columnspan=2)
        # Label abaixo do qual serao escritos os resultados das line widths
        ttk.Label(atdatayields, text="Line Widths").grid(
            column=5, row=0, sticky=W, columnspan=2)
        ttk.Button(master=atdatayields, text='Export', command=lambda: write_to_xls(2)).grid(
            column=12, row=0, sticky=W, columnspan=2)  # botao que exporta os resultados para um xls
        ttk.Button(master=atdatayields, text='Back', command=lambda: destroy(atdata)).grid(
            column=12, row=1, sticky=W, columnspan=2)  # botao que destroi esta janela
        ttk.Button(master=atdatayields, text='Exit', command=lambda: destroy(atdata)).grid(
            column=12, row=2, sticky=W, columnspan=2)  # botao que destroi esta janela
    except FileNotFoundError:
        messagebox.showerror("Error", "Required File is Missing")