#GUI Imports
from tkinter import *
from tkinter import ttk

#OS Imports for paths and files
import os
from pathlib import Path

#Module Imports: Atomic Parameter Selection
from aps.Yields import fetchYields
from aps.LvlWidths import fetchWidths
from aps.CrossSections import fetchSections
from aps.SpecSimu import simulateSpectra

#Static data import: periodic table values
from data.variables import per_table

#GUI utils: destroy window
from utils.interface import destroy

# os.getcwd retorna a directoria onde o código está. Criamos um objecto tipo Path porque permite o programa ser corrido em qq OS
dir_path = Path(str(os.getcwd()) + '/')
# https://medium.com/@ageitgey/python-3-quick-tip-the-easy-way-to-deal-with-file-paths-on-windows-mac-and-linux-11a072b58d5f site onde vi sobre isto GRV


# ---------------------------------------------------------------------------------------------------------------
# Função que corre depois de escolher a opção na janela que surge depois da tabela periódica
def calculate(element, ap, parent):
    
    if ap == 1:
        fetchYields(dir_path, z)
    # ---------------------------------------------------------------------------------------------------------------
    elif ap == 2:
        fetchWidths(dir_path, z)
    # ---------------------------------------------------------------------------------------------------------------
    elif ap == 3:
        fetchSections(dir_path, z)
    # ---------------------------------------------------------------------------------------------------------------
    elif ap == 4:  # Opção Spectra Simulation
        simulateSpectra(dir_path, element, parent)
    return 0


def params(z):  # Definições relacionadas com a segunda janela (depois da tabela periódica)
    parameters = Tk()  # Abrir uma janela com botoes que seleccionam o que calcular (yields, widths, cross sections e simulação)
    parameters.title("Atomic Parameters")  # nome da janela

    # variável que vai dar o valor do botao seleccionado (yields=1, widths=2, cross sections=3, simulacao=4)
    check_var = IntVar()
    # initialize (o botao 1, yields, começa selecionado por defeito)
    check_var.set(1)
    # ---------------------------------------------------------------------------------------------------------------
    # Propriedades da janela
    subelem = ttk.Frame(parameters, padding="3 3 12 12")
    subelem.grid(column=0, row=0, sticky=(N, W, E, S))
    subelem.columnconfigure(0, weight=1)
    subelem.rowconfigure(0, weight=1)
    # ---------------------------------------------------------------------------------------------------------------
    # Botões
    ttk.Button(subelem, text="Get", command=lambda: calculate(z, check_var.get(), parameters)).grid(
        column=6, row=5, sticky=E, columnspan=2)  # este botao faz correr a funcao calculate
    ttk.Button(subelem, text="Exit", command=lambda: destroy(parameters)).grid(
        column=6, row=6, sticky=E, columnspan=2)  # este botao fecha a janela
    ttk.Radiobutton(subelem, text='Yields', variable=check_var,
                    value=1).grid(column=0, row=5, sticky=W)
    ttk.Radiobutton(subelem, text='Level Widths', variable=check_var,
                    value=2).grid(column=1, row=5, sticky=W)
    ttk.Radiobutton(subelem, text='Cross Sections',
                    variable=check_var, value=3).grid(column=0, row=6, sticky=W)
    ttk.Radiobutton(subelem, text='Spectra Simulations',
                    variable=check_var, value=4).grid(column=1, row=6, sticky=W)
    ttk.Label(subelem, text="Which parameters do you want to retrieve?").grid(
        column=0, row=4, sticky=W, columnspan=2)

    subelem.mainloop()


class App(Tk):
    def __init__(self):
        Tk.__init__(self)

        def quit_window(z):
            self.destroy()
            params(z)

        self.title("Periodic Table of the Elements")

        self.topLabel = Label(self, text="", font=20)
        self.topLabel.grid(row=2, column=3, columnspan=10)

        self.Label1 = Label(
            self, text="Click the element for which you would like to obtain the atomic parameters.", font=22)
        self.Label1.grid(row=0, column=0, columnspan=18)

        self.Label2 = Label(self, text="", font=20)
        self.Label2.grid(row=8, column=0, columnspan=18)

        self.Label3 = Label(self, text="* Lanthanoids", font=20)
        self.Label3.grid(row=9, column=1, columnspan=2)

        self.Label4 = Label(self, text="** Actinoids", font=20)
        self.Label4.grid(row=10, column=1, columnspan=2)

        
        # create all buttons with a loop
        for i, element in enumerate(per_table):
            #        print(element[1])
            Button(self, text=element[3], width=5, height=2, bg=element[5], command=lambda i=i: quit_window(
                [(i + 1), per_table[i][2]])).grid(row=element[6], column=element[7])

        for child in self.winfo_children():
            child.grid_configure(padx=3, pady=3)

        self.mainloop()


def main():
    a = App()


if __name__ == "__main__":
    main()
