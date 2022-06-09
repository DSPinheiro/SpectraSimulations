#GUI Imports for warnings and interface to select files
from tkinter import messagebox
from tkinter.filedialog import askopenfilename

#Data import for variable management
from data.variables import labeldict, the_dictionary, the_aug_dictionary
import data.variables

#CSV reader import for reading and exporting data
import csv

#OS Imports for file paths
import os


# ----------------------------------------------------- #
#                                                       #
#                   EXPORT FUNCTIONS                    #
#                                                       #
# ----------------------------------------------------- #

# Função para dar nome aos ficheiros a gravar
def file_namer(simulation_or_fit, fit_time, extension):
    # converte a data para string
    dt_string = fit_time.strftime("%d%m%Y_%H%M%S")
    # Defino o nome conforme seja fit ou simulação,a data e hora e a extensão desejada
    file_name = simulation_or_fit + '_from_' + dt_string + extension
    
    return file_name


# Função para guardar os dados dos gráficos simulados em excel
def write_to_xls(type_t, xfinal, enoffset, y0, exp_x, exp_y, residues_graph, radiative_files, auger_files, label1, date_and_time):
    #Print the timestamp of the simulation
    print(date_and_time)
    
    #Generate filename to save the data
    file_title = file_namer("Simulation", date_and_time, ".csv")
    
    # Crio aquela que vai ser a primeira linha da matriz. Crio só a primeira coluna e depois adiciono as outras
    first_line = ['Energy (eV)']

    if enoffset != 0:
        # adicionar a coluna com o offset de energia calculado
        first_line += ['Energy Off (eV)']

    # ---------------------------------------------------------------------------------------------------------------
    # Corro o dicionário e se a transição estiver selecionada e tiver dados, adiciono o seu nome à primeira linha. Idem para as satélites
    if type_t != 'Auger':
        for index, transition in enumerate(the_dictionary):
            if the_dictionary[transition]["selected_state"]:
                if max(data.variables.yfinal[index]) != 0:
                    first_line += [the_dictionary[transition]["readable_name"]]
                for l, m in enumerate(data.variables.yfinals[index]):
                    if max(m) != 0:
                        first_line += [the_dictionary[transition]
                                       ["readable_name"] + '-' + labeldict[label1[l]]]
    else:
        for index, transition in enumerate(the_aug_dictionary):
            if the_aug_dictionary[transition]["selected_state"]:
                if max(data.variables.yfinal[index]) != 0:
                    first_line += [the_aug_dictionary[transition]
                                   ["readable_name"]]
                for l, m in enumerate(data.variables.yfinals[index]):
                    if max(m) != 0:
                        first_line += [the_aug_dictionary[transition]
                                       ["readable_name"] + '-' + labeldict[label1[l]]]
    # ---------------------------------------------------------------------------------------------------------------
    
    first_line += ['Total']  # Adiciono a ultima coluna que terá o total
    
    if y0 != 0:
        # adicionar a coluna com o offset de intensidade calculado
        first_line += ['Total Off']
    
    if exp_x != None and exp_y != None:
        # adicionar as colunas com a energia e intensidade experimentais
        first_line += ['Exp Energy (eV)', 'Intensity']

    if residues_graph != None:
        # adicionar as colunas com os residuos calculados
        first_line += ['Residues (arb. units)', 'std+', 'std-', '', 'red chi 2']

    if len(data.variables.PCS_radMixValues) > 0 or len(data.variables.NCS_radMixValues) > 0 or len(data.variables.PCS_augMixValues) > 0 or len(data.variables.NCS_augMixValues) > 0:
        # adicionar uma coluna de separação e as colunas com a mistura de charge states
        first_line += ['', 'Charge States', 'Percentage']

    # Crio uma matriz vazia com o numero de colunas= tamanho da primeira linha e o numero de linhas = numero de pontos dos gráficos
    if exp_x != None:
        matrix = [[None for x in range(len(first_line))] for y in range(max(len(xfinal), len(exp_x)))]
    else:
        matrix = [[None for x in range(len(first_line))] for y in range(len(xfinal))]
    
    # ---------------------------------------------------------------------------------------------------------------
    #  Preencho a primeira e segunda coluna com os valores de x e x + offset
    # começa no 1 porque a coluna 0 é a dos valores de x. Uso esta variável para ir avançando nas colunas
    transition_columns = 1

    if enoffset != 0:
        #Write the x and x + offset values in the matrix
        for i, x in enumerate(xfinal):
            matrix[i][0] = x
            matrix[i][1] = x + enoffset

        transition_columns += 1
    else:
        #Write the x values in the matrix
        for i, x in enumerate(xfinal):
            matrix[i][0] = x
    
    # ---------------------------------------------------------------------------------------------------------------
    # Preencho as colunas dos valores yy
    for i, y in enumerate(data.variables.yfinal):  # Corro todas as transições
        # Se houver diagrama ou satélite
        if max(y) != 0:
            # Corro todos os valores da diagrama e adiciono-os à linha correspondente
            for row in range(len(y)):
                matrix[row][transition_columns] = y[row]
            
            transition_columns += 1
        
        if any(data.variables.yfinals[i]) != 0:
            # Mesma ideia que para a diagrama
            for j, ys in enumerate(data.variables.yfinals[i]):
                if max(ys) != 0:
                    for row in range(len(y)):
                        matrix[row][transition_columns] = ys[row]
                    
                    transition_columns += 1
    
    # ---------------------------------------------------------------------------------------------------------------
    # Preencho os valores de ytotal
    if y0 != 0:
        for j in range(len(data.variables.ytot)):
            matrix[j][transition_columns] = data.variables.ytot[j]
            matrix[j][transition_columns + 1] = data.variables.ytot[j] + y0
    
        transition_columns += 1
    else:
        for j in range(len(data.variables.ytot)):
            matrix[j][transition_columns] = data.variables.ytot[j]

    transition_columns += 1
    
    # ---------------------------------------------------------------------------------------------------------------
    # Preencher of valores do espetro experimental
    if exp_x == None and exp_y == None:
        print("No experimental spectrum loaded. Skipping...")
    else:
        for i in range(len(exp_x)):
            matrix[i][transition_columns] = exp_x[i]
            matrix[i][transition_columns + 1] = exp_y[i]

        transition_columns += 2
    
    # ---------------------------------------------------------------------------------------------------------------
    # Retrieve the residue data from the graph object
    if residues_graph == None:
        print("No residues calculated. Skipping...")
    else:
        lines = residues_graph.get_lines()
        sigp, sigm, res = lines[0].get_ydata(), lines[1].get_ydata(), lines[2].get_ydata()

        for i in range(len(exp_x)):
            matrix[i][transition_columns] = res[i]
            matrix[i][transition_columns + 1] = sigp[i]
            matrix[i][transition_columns + 2] = sigm[i]

        matrix[0][transition_columns + 4] = data.variables.chi_sqrd

        transition_columns += 5
    
    # ---------------------------------------------------------------------------------------------------------------
    # Write the mix values in the matrix
    if type_t != 'Auger':
        if len(data.variables.PCS_radMixValues) > 0 or len(data.variables.NCS_radMixValues) > 0:
            idx_p = 0
            idx_n = 0
            for i, cs in enumerate(radiative_files):
                matrix[i][transition_columns + 1] = cs.split('-intensity_')[1].split('.out')[0] + '_'

                if '+' in cs:
                    matrix[i][transition_columns + 2] = data.variables.PCS_radMixValues[idx_p].get()
                    idx_p += 1
                else:
                    matrix[i][transition_columns + 2] = data.variables.NCS_radMixValues[idx_n].get()
                    idx_n += 1
    else:
        if len(data.variables.PCS_augMixValues) > 0 or len(data.variables.NCS_augMixValues) > 0:
            idx_p = 0
            idx_n = 0

            matrix[1][transition_columns + 1] = "Auger Mix Values"

            for i, cs in enumerate(auger_files):
                matrix[i + 1][transition_columns + 1] = cs.split('-augrate_')[1].split('.out')[0] + '_'

                if '+' in cs:
                    matrix[i + 1][transition_columns + 2] = data.variables.PCS_augMixValues[idx_p].get()
                    idx_p += 1
                else:
                    matrix[i + 1][transition_columns + 2] = data.variables.NCS_augMixValues[idx_n].get()
                    idx_n += 1
    
    # ---------------------------------------------------------------------------------------------------------------
    # Adiciono a linha com os nomes das trnaisções à matriz
    matrix = [first_line] + matrix
    
    # ---------------------------------------------------------------------------------------------------------------
    # Util para imprimir a matriz na consola e fazer testes
    # for row in matrix:
    #     print(' '.join(map(str, row)))
    
    # ---------------------------------------------------------------------------------------------------------------
    # Escrita para o ficheiro. Se for a primeira linha da matriz, abrimos como write, se não, abrimos como append porque só queremos adicionar ao fim do ficheiro
    for i, item in enumerate(matrix):
        if i == 0:
            with open(file_title, 'w', newline='') as csvfile:
                w1 = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                w1.writerow(matrix[i])
        else:
            with open(file_title, 'a', newline='') as csvfile2:
                w1 = csv.writer(csvfile2, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                w1.writerow(matrix[i])
    messagebox.showinfo("File Saved", "Data file has been saved")



# ----------------------------------------------------- #
#                                                       #
#       LOAD EXPERIMENTAL AND EFFICIENCY DATA           #
#                                                       #
# ----------------------------------------------------- #

# Funcao que muda o nome da variavel correspondente ao ficheiro experimental
def load(loadvar):
    # Lauch a file picker interface
    fname = askopenfilename(filetypes=(("Spectra files", "*.csv *.txt"), ("All files", "*.*")))
    # Muda o nome da variavel loadvar para a string correspondente ao path do ficheiro seleccionado
    loadvar.set(fname)


# Funcao que muda o nome da variavel correspondente ao ficheiro com a efficiencia do detetor
def load_effic_file(effic_var):
    # Lauch a file picker interface
    effic_fname = askopenfilename(filetypes=(("Efficiency files", "*.csv"), ("All files", "*.*")))
    # Muda o nome da variavel effic_var para a string correspondente ao path do ficheiro seleccionado
    effic_var.set(effic_fname)


# Funcao para ler o ficheiro experimental em formato csv e retornar em formato de lista
def loadExp(file):
    return list(csv.reader(open(file, 'r', encoding='utf-8-sig')))



# ----------------------------------------------------- #
#                                                       #
#                  READ RATES FILES                     #
#                                                       #
# ----------------------------------------------------- #

# Read the radiative rates file and return a list with the data
def readRadRates(radrates_file):
    try:
        with open(radrates_file, 'r') as radrates:  # Abrir o ficheiro
            # Escrever todas as linhas no ficheiro como uma lista
            lineradrates = [x.strip('\n').split() for x in radrates.readlines()]
            # Remover as linhas compostas apenas por celulas vazias
            lineradrates = list(filter(None, lineradrates))
            del lineradrates[0:2]
            
            return lineradrates
    except FileNotFoundError:
        messagebox.showwarning("Error", "Diagram File is not Avaliable")


# Read the satellite rates file and return a list with the data
def readSatRates(satellites_file):
    try:
        with open(satellites_file, 'r') as satellites:  # Abrir o ficheiro
            # Escrever todas as linhas no ficheiro como uma lista
            linesatellites = [x.strip('\n').split() for x in satellites.readlines()]
            # Remover as linhas compostas apenas por celulas vazias
            linesatellites = list(filter(None, linesatellites))
            # Tira as linhas que têm o nome das variáveis e etc
            del linesatellites[0:2]
            
            return linesatellites
    except FileNotFoundError:
        messagebox.showwarning("Error", "Satellites File is not Avaliable")


# Read the auger rates file and return a list with the data
def readAugRates(augrates_file):
    try:
        with open(augrates_file, 'r') as augrates:  # Abrir o ficheiro
            # Escrever todas as linhas no ficheiro como uma lista
            lineauger = [x.strip('\n').split() for x in augrates.readlines()]
            # Remover as linhas compostas apenas por celulas vazias
            lineauger = list(filter(None, lineauger))
            # Tira as linhas que têm o nome das variáveis e etc
            del lineauger[0:2]
            
            return lineauger
    except FileNotFoundError:
        messagebox.showwarning("Error", "Auger Rates File is not Avaliable")


# Read the shake weights file and return a list with the data and a list with the labels
def readShakeWeights(shakeweights_file):
    try:
        with open(shakeweights_file, 'r') as shakeweights_f:  # Abrir o ficheiro
            # Escrever todas as linhas no ficheiro como uma lista
            shakeweights_m = [x.strip('\n').split(',') for x in shakeweights_f.readlines()]
            shakeweights = []
            label1 = []
            for i, j in enumerate(shakeweights_m):
                # Neste for corremos as linhas todas guardadas em shakeweights_m e metemos os valores numéricos no shakeweights
                shakeweights.append(float(shakeweights_m[i][1]))
            for k, l in enumerate(shakeweights_m):
                # Neste for corremos as linhas todas guardadas em shakeweights_m e metemos os rotulos no label 1
                label1.append(shakeweights_m[k][0])
            
            
            return shakeweights, label1
    except FileNotFoundError:
        messagebox.showwarning("Error", "Shake Weigth File is not Avaliable")



# ----------------------------------------------------- #
#                                                       #
#    READ RATES AND IONPOP FILES FOR CHARGE STATES      #
#                                                       #
# ----------------------------------------------------- #

# Search the Charge_States folder for all radiative rate files and return a list with their names
def searchRadChargeStates(dir_path, z):
    radiative_files = []
    # Loop all files in the folder
    for f in os.listdir(dir_path / str(z) / 'Charge_States'):
        # If the name format matches a radiative rates files then append it to the list
        if os.path.isfile(os.path.join(dir_path / str(z) / 'Charge_States', f)) and '-intensity_' in f:
            radiative_files.append(f)
    
    return radiative_files


# Search the Charge_States folder for all auger rate files and return a list with their names
def searchAugChargeStates(dir_path, z):
    auger_files = []
    
    # Loop all files in the folder
    for f in os.listdir(dir_path / str(z) / 'Charge_States'):
        # If the name format matches an auger rates files then append it to the list
        if os.path.isfile(os.path.join(dir_path / str(z) / 'Charge_States', f)) and '-augrate_' in f:
            auger_files.append(f)
    
    return auger_files


# Search the Charge_States folder for all satellite rate files and return a list with their names
def searchSatChargeStates(dir_path, z):
    sat_files = []
    
    # Loop all files in the folder
    for f in os.listdir(dir_path / str(z) / 'Charge_States'):
        # If the name format matches an satellite rates files then append it to the list
        if os.path.isfile(os.path.join(dir_path / str(z) / 'Charge_States', f)) and '-satinty_' in f:
            sat_files.append(f)
    
    return sat_files


# Read the radiative rates files in the radiative_files list and return a a list with the data split by positive and negative charge states.
# Also return a list with the order in which the data was stored in the lists
def readRadChargeStates(radiative_files, dir_path, z):
    lineradrates_PCS = []
    lineradrates_NCS = []

    rad_PCS = []
    rad_NCS = []

    # Loop for each radiative file
    for radfile in radiative_files:
        # Caminho do ficheiro na pasta com o nome igual ao numero atomico que tem as intensidades
        rad_tmp_file = dir_path / str(z) / 'Charge_States' / radfile
        try:
            with open(rad_tmp_file, 'r') as radrates:  # Abrir o ficheiro
                if '+' in radfile:
                    # Escrever todas as linhas no ficheiro como uma lista
                    lineradrates_PCS.append([x.strip('\n').split() for x in radrates.readlines()])
                    # Remover as linhas compostas apenas por celulas vazias
                    lineradrates_PCS[-1] = list(filter(None, lineradrates_PCS[-1]))
                    del lineradrates_PCS[-1][0:2]
                    rad_PCS.append('+' + radfile.split('+')[1].split('.')[0])
                else:
                    # Escrever todas as linhas no ficheiro como uma lista
                    lineradrates_NCS.append([x.strip('\n').split() for x in radrates.readlines()])
                    # Remover as linhas compostas apenas por celulas vazias
                    lineradrates_NCS[-1] = list(filter(None, lineradrates_NCS[-1]))
                    del lineradrates_NCS[-1][0:2]
                    rad_NCS.append('-' + radfile.split('-')[1].split('.')[0])
        except FileNotFoundError:
            messagebox.showwarning("Error", "Charge State File is not Avaliable: " + radfile)
    
    return lineradrates_PCS, lineradrates_NCS, rad_PCS, rad_NCS


# Read the auger rates files in the auger_files list and return a a list with the data split by positive and negative charge states.
# Also return a list with the order in which the data was stored in the lists
def readAugChargeStates(auger_files, dir_path, z):
    lineaugrates_PCS = []
    lineaugrates_NCS = []

    aug_PCS = []
    aug_NCS = []

    # Loop for each auger file
    for augfile in auger_files:
        # Caminho do ficheiro na pasta com o nome igual ao numero atomico que tem as intensidades
        aug_tmp_file = dir_path / str(z) / 'Charge_States' / augfile
        try:
            with open(aug_tmp_file, 'r') as augrates:  # Abrir o ficheiro
                if '+' in augfile:
                    # Escrever todas as linhas no ficheiro como uma lista
                    lineaugrates_PCS.append([x.strip('\n').split() for x in augrates.readlines()])
                    # Remover as linhas compostas apenas por celulas vazias
                    lineaugrates_PCS[-1] = list(filter(None, lineaugrates_PCS[-1]))
                    del lineaugrates_PCS[-1][0:2]
                    aug_PCS.append('+' + radfile.split('+')[1].split('.')[0])
                else:
                    # Escrever todas as linhas no ficheiro como uma lista
                    lineaugrates_NCS.append([x.strip('\n').split() for x in augrates.readlines()])
                    # Remover as linhas compostas apenas por celulas vazias
                    lineaugrates_NCS[-1] = list(filter(None, lineaugrates_NCS[-1]))
                    del lineaugrates_NCS[-1][0:2]
                    aug_NCS.append('-' + radfile.split('-')[1].split('.')[0])
        except FileNotFoundError:
            messagebox.showwarning("Error", "Charge State File is not Avaliable: " + augfile)
    
    return lineaugrates_PCS, lineaugrates_NCS, aug_PCS, aug_NCS


# Read the satellite rates files in the sat_files list and return a a list with the data split by positive and negative charge states.
# Also return a list with the order in which the data was stored in the lists
def readSatChargeStates(sat_files, dir_path, z):
    linesatellites_PCS = []
    linesatellites_NCS = []

    sat_PCS = []
    sat_NCS = []

    # Loop for each satellite file
    for satfile in sat_files:
        # Caminho do ficheiro na pasta com o nome igual ao numero atomico que tem as intensidades
        sat_tmp_file = dir_path / str(z) / 'Charge_States' / satfile
        try:
            with open(sat_tmp_file, 'r') as satrates:  # Abrir o ficheiro
                if '+' in satfile:
                    # Escrever todas as linhas no ficheiro como uma lista
                    linesatellites_PCS.append([x.strip('\n').split() for x in satrates.readlines()])
                    # Remover as linhas compostas apenas por celulas vazias
                    linesatellites_PCS[-1] = list(filter(None, linesatellites_PCS[-1]))
                    del linesatellites_PCS[-1][0:2]
                    sat_PCS.append('+' + satfile.split('+')[1].split('.')[0])
                else:
                    # Escrever todas as linhas no ficheiro como uma lista
                    linesatellites_NCS.append([x.strip('\n').split() for x in satrates.readlines()])
                    # Remover as linhas compostas apenas por celulas vazias
                    linesatellites_NCS[-1] = list(filter(None, linesatellites_NCS[-1]))
                    del linesatellites_NCS[-1][0:2]
                    sat_NCS.append('-' + satfile.split('-')[1].split('.')[0])
        except FileNotFoundError:
            messagebox.showwarning("Error", "Charge State File is not Avaliable: " + satfile)
    
    return linesatellites_PCS, linesatellites_NCS, sat_PCS, sat_NCS


# Read the ion population file and return a list with the raw data
def readIonPop(ionpop_file):
    try:
        with open(ionpop_file, 'r') as ionpop:  # Abrir o ficheiro
            # Escrever todas as linhas no ficheiro como uma lista
            ionpopdata = [x.strip('\n').split() for x in ionpop.readlines()]
            # Remover as linhas compostas apenas por celulas vazias
            ionpopdata = list(filter(None, ionpopdata))
        
        return True, ionpopdata
    except FileNotFoundError:
        messagebox.showwarning("Error", "Ion Population File is not Avaliable")