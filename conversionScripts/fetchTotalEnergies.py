import os

ground_energy = -44961.88335

root_dir = '5d\\auger'
output_file = '29-groundsatenergy_5d.out'

def search_highest_percentage(file, string1, string2):
    highest_percentage = 0
    highest_identifier = ""
    flag = 0
    with open(file, 'r') as f:
        for line in f:
            if string1 in line:
                flag = 1
                continue
            if flag == 1:
                if line.strip() == "":
                    break
                
                vals = line.strip().split()
                identifier = ' '.join(vals[:-2])
                percentage = vals[-2]
                
                if float(percentage) > highest_percentage:
                    highest_percentage = float(percentage)
                    highest_identifier = identifier
        
    with open(file, 'r') as f:
        if flag == 1:
            return highest_identifier
        else:
            flag = 0
            for line in f:
                if string2 in line:
                    flag = 1
                    continue
                if flag == 1:
                    return line.strip()
    
    return None

register = 0

with open(output_file, 'w') as out:
    out.write("# Atomic number Z= 29  Date:10-1-2023\n\n")
    out.write("# Number	Shelli	ShellLS 2Ji	Eigi	Total Energy (eV)	Ground Energy(eV)	Partial Width (eV)\n")
    
    for dir1 in os.listdir(root_dir):
        for dir2 in os.listdir(os.path.join(root_dir, dir1)):
            if '2jj_' in dir2:
                for dir3 in os.listdir(os.path.join(root_dir, dir1, dir2)):
                    if 'eig_' in dir3:
                        input_file = os.path.join(root_dir, dir1, dir2, dir3, dir1 + '_' + dir2.split('2jj_')[1] + '_' + dir3.split('eig_')[1] + '.f06')
                        if os.path.exists(input_file):
                            register += 1
                            
                            with open(input_file, 'r') as f:
                                for line in f:
                                    if 'Etot_(Welt.)=' in line:
                                        elements = line.strip().split()
                                        if len(elements) >= 4:
                                            value = elements[3]
                                            break
                                
                            highest_identifier = search_highest_percentage(input_file, 'List of jj configurations with a weight >= 0.01%', 'Configuration(s)         1 to         1')
                            
                            if highest_identifier and value:
                                shells = dir1
                                
                                shells = shells.replace('1s', 'K1')
                                shells = shells.replace('2s', 'L1')
                                shells = shells.replace('3s', 'M1')
                                shells = shells.replace('4s', 'N1')
                                
                                if '2p' in shells:
                                    if '2p*2' in highest_identifier:
                                        shells = shells.replace('2p', 'L3', 1)
                                        
                                        if '2p' in shells:
                                            shells = 'L3L3'
                                    elif '2p4' in highest_identifier:
                                        shells = shells.replace('2p', 'L2', 1)
                                        
                                        if '2p' in shells:
                                            shells = 'L2L2'
                                    else:
                                        shells = 'L2L3'
                                if '3p' in shells:
                                    if '3p*2' in highest_identifier:
                                        shells = shells.replace('3p', 'M3', 1)
                                    
                                        if '3p' in shells:
                                            shells = 'M3M3'
                                    elif '3p4' in highest_identifier:
                                        shells = shells.replace('3p', 'M2', 1)
                                        
                                        if '3p' in shells:
                                            shells = 'M2M2'
                                    else:
                                        shells = 'M2M3'
                                if '3d' in shells:
                                    if '3d*4' in highest_identifier:
                                        shells = shells.replace('3d', 'M5', 1)
                                        
                                        if '3d' in shells:
                                            shells = 'M5M5'
                                    elif '3d6' in highest_identifier:
                                        shells = shells.replace('3d', 'M4', 1)
                                    
                                        if '3d' in shells:
                                            shells = 'M4M4'
                                    else:
                                        shells = 'M4M5'
                                
                                shells = shells.replace('_', '')
                                
                                out.write(f'\t{register}\t\t{shells}\t {dir1}\t {dir2.split("2jj_")[1]}\t {int(dir3.split("eig_")[1]) + 1}\t\t{value}\t\t{round(float(value) - ground_energy, 5)}\n')
                            elif value:
                                out.write(f'\t{register}\t\t{shells}\t {dir1}\t {dir2.split("2jj_")[1]}\t {int(dir3.split("eig_")[1]) + 1}\t\t{value}\t\t{round(float(value) - ground_energy, 5)}\tBUG!!!!!\n')
                            elif highest_identifier:
                                out.write(f'\t{register}\t\t{shells}\t {dir1}\t {dir2.split("2jj_")[1]}\t {int(dir3.split("eig_")[1]) + 1}\t\tBUG!!!!!\n')
                        else:
                            print(f"{input_file} not found!")