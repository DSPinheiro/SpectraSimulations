from tkinter import messagebox

from data.variables import labeldict, the_dictionary, the_aug_dictionary
import data.variables
import csv

# Função para dar nome aos ficheiros a gravar
def file_namer(simulation_or_fit, fit_time, extension):
    #    dt_string = fit_time.strftime("%d-%m-%Y %H:%M:%S")  # converte a data para string
    # converte a data para string
    dt_string = fit_time.strftime("%d%m%Y_%H%M%S")
    # Defino o nome conforme seja fit ou simulação,a data e hora e a extensão desejada
    file_name = simulation_or_fit + '_from_' + dt_string + extension
    return file_name



# Função para gaurdar os dados dos gráifocs simulados em excel
def write_to_xls(type_t, xfinal, enoffset, y0, exp_x, exp_y, residues_graph, radiative_files, auger_files, label1, date_and_time):
    print(date_and_time)
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
        first_line += ['Exp Energy (eV)', 'Intensity']

    if residues_graph != None:
        first_line += ['Residues (arb. units)', 'std+',
                       'std-', '', 'red chi 2']

    if len(data.variables.PCS_radMixValues) > 0 or len(data.variables.NCS_radMixValues) > 0 or len(data.variables.PCS_augMixValues) > 0 or len(data.variables.NCS_augMixValues) > 0:
        first_line += ['', 'Charge States', 'Percentage']

    if exp_x != None:
        matrix = [[None for x in range(len(first_line))]
                  for y in range(max(len(xfinal), len(exp_x)))]
    else:
        # Crio uma matriz vazia com o numero de colunas= tamanho da primeira linha e o numero de linhas = numero de pontos dos gráficos
        matrix = [[None for x in range(len(first_line))]
                  for y in range(len(xfinal))]
    
    # ---------------------------------------------------------------------------------------------------------------
    #  Preencho a primeira e segunda coluna com os valores de x e x + offset
    # começa no 1 porque a coluna 0 é a dos valores de x. Uso esta variável para ir avançando nas colunas
    transition_columns = 1

    if enoffset != 0:
        for i, x in enumerate(xfinal):
            matrix[i][0] = x
            matrix[i][1] = x + enoffset

        transition_columns += 1
    else:
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
        sigp, sigm, res = lines[0].get_ydata(
        ), lines[1].get_ydata(), lines[2].get_ydata()

        for i in range(len(exp_x)):
            matrix[i][transition_columns] = res[i]
            matrix[i][transition_columns + 1] = sigp[i]
            matrix[i][transition_columns + 2] = sigm[i]

        matrix[0][transition_columns + 4] = data.variables.chi_sqrd

        transition_columns += 5
    # ---------------------------------------------------------------------------------------------------------------
    if type_t != 'Auger':
        if len(data.variables.PCS_radMixValues) > 0 or len(data.variables.NCS_radMixValues) > 0:
            idx_p = 0
            idx_n = 0
            for i, cs in enumerate(radiative_files):
                matrix[i][transition_columns +
                          1] = cs.split('-intensity_')[1].split('.out')[0] + '_'

                if '+' in cs:
                    matrix[i][transition_columns +
                              2] = data.variables.PCS_radMixValues[idx_p].get()
                    idx_p += 1
                else:
                    matrix[i][transition_columns +
                              2] = data.variables.NCS_radMixValues[idx_n].get()
                    idx_n += 1
    else:
        if len(data.variables.PCS_augMixValues) > 0 or len(data.variables.NCS_augMixValues) > 0:
            idx_p = 0
            idx_n = 0

            matrix[1][transition_columns + 1] = "Auger Mix Values"

            for i, cs in enumerate(auger_files):
                matrix[i + 1][transition_columns +
                              1] = cs.split('-augrate_')[1].split('.out')[0] + '_'

                if '+' in cs:
                    matrix[i + 1][transition_columns +
                                  2] = data.variables.PCS_augMixValues[idx_p].get()
                    idx_p += 1
                else:
                    matrix[i + 1][transition_columns +
                                  2] = data.variables.NCS_augMixValues[idx_n].get()
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
                w1 = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
                w1.writerow(matrix[i])
        else:
            with open(file_title, 'a', newline='') as csvfile2:
                w1 = csv.writer(csvfile2, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
                w1.writerow(matrix[i])
    messagebox.showinfo("File Saved", "Data file has been saved")
