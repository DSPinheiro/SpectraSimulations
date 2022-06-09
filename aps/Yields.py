#GUI Imports
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

#File IO Imports
from utils.fileIO import file_namer, write_to_xls

#GUI utils: destroy window
from utils.interface import destroy


def fetchYields(dir_path, z):
    # Caminho do ficheiro na pasta com o nome igual ao numero atomico que tem as yields
    yields_file = dir_path / str(z) / (str(z) + '-yields.out')
    try:
        with open(yields_file, 'r') as yields:  # Abrir o ficheiro
            # Escrever todas as linhas no
            lineyields = [x.strip('\n').split() for x in yields.readlines()]
            # ficheiro como uma lista
            # Remover as linhas compostas apenas por celulas vazias
            lineyields = list(filter(None, lineyields))
        # criar uma janela onde serao apresentados os resultados dos yields, widths, cross sections ou spectra simulations
        atdata = Toplevel()
        # titulo da janela
        atdata.title("Fluorescence and nonRadiative Yields")
        # Criar uma grelha dentro da janela onde serao inseridos os dados
        atdatayields = ttk.Frame(atdata, padding="3 3 12 12")
        atdatayields.grid(column=0, row=0, sticky=(N, W, E, S))
        atdatayields.columnconfigure(0, weight=1)
        atdatayields.rowconfigure(0, weight=1)
        # Labels dos dados na janela
        # Label abaixo do qual serao escritos os resultados dos fluorescence yields
        ttk.Label(atdatayields, text="Fluorescence Yields").grid(column=0, row=0, sticky=W, columnspan=2)
        # Label abaixo do qual serao escritos os resultados dos auger yields
        ttk.Label(atdatayields, text="Auger Yields").grid(column=5, row=0, sticky=W, columnspan=2)
        # Label abaixo do qual serao escritos os resultados dos coster kronig yields
        ttk.Label(atdatayields, text="Coster-Kronig Yields").grid(column=8, row=0, sticky=W, columnspan=2)
        ttk.Button(master=atdatayields, text='Export', command=lambda: write_to_xls(1)).grid(column=12, row=0, sticky=W, columnspan=2)  # botao que exporta os resultados para um xls
        ttk.Button(master=atdatayields, text='Back', command=lambda: destroy(atdata)).grid(column=12, row=1, sticky=W, columnspan=2)  # botao que destroi esta janela
        ttk.Button(master=atdatayields, text='Exit', command=lambda: destroy(atdata)).grid(column=12, row=2, sticky=W, columnspan=2)  # botao que destroi esta janela

        NR = False  # Variavel que diz se ja se esta a ler a parte nao radiativa do ficheiro yields
        n1 = 1  # contadores para escrever os yields em linhas sequencialmente distribuidas
        n2 = 1
        n3 = 1
        # Ciclo sobre todas as linhas do ficheiro yields para ler todos os yields FY, AY, CKY
        for i, j in enumerate(lineyields):
            # print(j)
            # print(j[0])
            if j[1] == 'FLyield' and j[0] != '':
                print('FY_' + j[0], '=', j[2])
                ttk.Label(atdatayields, text='FY_' + j[0] + '=' + j[2]).grid(column=0, row=n1, sticky=W, columnspan=2)
                n1 = n1 + 1
            if j[1] == 'NRyield' and j[0] != '':
                print('AY_' + j[0], '=', j[2])
                ttk.Label(atdatayields, text='AY_' + j[0] + '=' + j[2]).grid(column=5, row=n2, sticky=W, columnspan=2)
                n2 = n2 + 1
        for i, j in enumerate(lineyields):
            if j[1] == 'Non' and j[2] == 'Radiative' and j[3] == 'Yields':
                NR = True
            if j[0] == 'L1' and j[2] == 'L2' and NR == True:
                print('fL12_', '=', j[3])
                ttk.Label(atdatayields, text='fL12_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                n3 = n3 + 1
            if j[0] == 'L1' and j[2] == 'L3' and NR == True:
                print('fL13_', '=', j[3])
                ttk.Label(atdatayields, text='fL13_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                n3 = n3 + 1
            if j[0] == 'L2' and j[2] == 'L3' and NR == True:
                print('fL23_', '=', j[3])
                ttk.Label(atdatayields, text='fL23_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                n3 = n3 + 1
            if j[0] == 'M1' and j[2] == 'M2' and NR == True:
                print('fM12_', '=', j[3])
                ttk.Label(atdatayields, text='fM12_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                n3 = n3 + 1
            if j[0] == 'M1' and j[2] == 'M3' and NR == True:
                print('fM13_', '=', j[3])
                ttk.Label(atdatayields, text='fM13_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                n3 = n3 + 1
            if j[0] == 'M1' and j[2] == 'M4' and NR == True:
                print('fM14_', '=', j[3])
                ttk.Label(atdatayields, text='fM14_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                n3 = n3 + 1
            if j[0] == 'M1' and j[2] == 'M5' and NR == True:
                print('fM15_', '=', j[3])
                ttk.Label(atdatayields, text='fM15_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                n3 = n3 + 1
            if j[0] == 'M2' and j[2] == 'M3' and NR == True:
                print('fM23_', '=', j[3])
                ttk.Label(atdatayields, text='fM23_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                n3 = n3 + 1
            if j[0] == 'M2' and j[2] == 'M4' and NR == True:
                print('fM24_', '=', j[3])
                ttk.Label(atdatayields, text='fM24_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                n3 = n3 + 1
            if j[0] == 'M2' and j[2] == 'M5' and NR == True:
                print('fM25_', '=', j[3])
                ttk.Label(atdatayields, text='fM25_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                n3 = n3 + 1
            if j[0] == 'M3' and j[2] == 'M4' and NR == True:
                print('fM34_', '=', j[3])
                ttk.Label(atdatayields, text='fM34_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                n3 = n3 + 1
            if j[0] == 'M3' and j[2] == 'M5' and NR == True:
                print('fM35_', '=', j[3])
                ttk.Label(atdatayields, text='fM35_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                n3 = n3 + 1
            if j[0] == 'M4' and j[2] == 'M5' and NR == True:
                print('fM45_', '=', j[3])
                ttk.Label(atdatayields, text='fM45_' + '=' + j[3]).grid(column=8, row=n3, sticky=W, columnspan=2)
                n3 = n3 + 1
    except FileNotFoundError:
        messagebox.showerror("Error", "Required File is Missing")