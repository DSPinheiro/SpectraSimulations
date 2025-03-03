import os, sys
from datetime import date
import re

h = 4.135667696 * 10**(-15)

ground_config = "1s2 2s2 2p*2 2p4 3s2 3p*2 3p4 3d*4 3d6 4s1"
# ground_config = "1s2 2s2 2p*2 2p4 3s2 3p*2 3p4 3d*4 3d6 4s2 4p*2 4p4 4d*4 4d6 5s2"
# ground_energy = -155311.29670 # <- Cd(err) | Cu -> -44961.88335
ground_energy = -44961.88335
Z = 29

input_dir = '../input/'
output_dir = '../output/'

eig_keywrd = "eig_"
eig_offset = 0

header_count = 1

arguments = {}

flags = ["-rs", "-as", "-itr", "-cfg", "-otr", "-is", "-os", "-t", "-br"]

if "-rs" not in sys.argv or "-itr" not in sys.argv or "-cfg" not in sys.argv or \
    "-otr" not in sys.argv or "-t" not in sys.argv:
    # -rs -as -itr -cfg -otr -is -os -t -br
    print("Unexpected flags in arguments. The available flags for the arguments are:")
    print("-rs: input directory with the calculated configurations;")
    print("-as: [Optional, auger] input directory with the calculated configurations for the final states;")
    print("-itr: input transition rates filename.")
    print("-otr: output transition rates filename.")
    print("-cfg: output configurations filename.")
    print("-is: [Optional] input spectrum filename.")
    print("-os: [Optional] output spectrum filename.")
    print("-t: transition type to convert (excitation, diagram, auger).")
    print("-br: [Optional] corresponding auger rates file for the branching ratio calculation.")
    exit(-1)
else:
    for i, arg in enumerate(sys.argv[1:]):
        if arg in flags:
            arguments[arg] = sys.argv[1:][i + 1]
    
    if arguments["-t"] != 'diagram' and arguments["-t"] != 'auger' and arguments["-t"] != 'excitation':
        print("Unsupported transition type requested: " + arguments["-t"])
        print("Supported types are diagram and auger.")
        exit(-2)
    
    if arguments["-t"] == 'auger' and "-as" not in arguments:
        print("Requested conversion of auger transitions but did not provide arguments for final state configurations.")
        exit(-3)


siegbahn = {
            '1s': 'K1',
            
            '2s': 'L1', '2p*': 'L2', '2p': 'L3',
            
            '3s': 'M1', '3p*': 'M2', '3p': 'M3', '3d*': 'M4', '3d': 'M5',
            
            '4s': 'N1', '4p*': 'N2', '4p': 'N3', '4d*': 'N4', '4d': 'N5', '4f*': 'N6', '4f': 'N7',
            
            '5s': 'O1', '5p*': 'O2', '5p': 'O3', '5d*': 'O4', '5d': 'O5', '5f*': 'O6', '5f': 'O7',
                '5g*': 'O8', '5g': 'O9',
            
            '6s': 'P1', '6p*': 'P2', '6p': 'P3', '6d*': 'P4', '6d': 'P5', '6f*': 'P6', '6f': 'P7',
                '6g*': 'P8', '6g': 'P9', '6h*': 'P10', '6h': 'P11',
            
            '7s': 'Q1', '7p*': 'Q2', '7p': 'Q3', '7d*': 'Q4', '7d': 'Q5', '7f*': 'Q6', '7f': 'Q7',
                '7g*': 'Q8', '7g': 'Q9', '7h*': 'Q10', '7h': 'Q11', '7i*': 'Q12', '7i': 'Q13',
            
            '8s': 'R1', '8p*': 'R2', '8p': 'R3', '8d*': 'R4', '8d': 'R5', '8f*': 'R6', '8f': 'R7',
                '8g*': 'R8', '8g': 'R9', '8h*': 'R10', '8h': 'R11', '8i*': 'R12', '8i': 'R13',
                '8j*': 'R14', '8j': 'R15',
            
            '9s': 'S1', '9p*': 'S2', '9p': 'S3', '9d*': 'S4', '9d': 'S5', '9f*': 'S6','9f': 'S7',
                '9g*': 'S8', '9g': 'S9', '9h*': 'S10', '9h': 'S11', '9i*': 'S12', '9i': 'S13',
                '9j*': 'S14', '9j': 'S15', '9k*': 'S16', '9k': 'S17',
            
            '10s': 'T1', '10p*': 'T2', '10p': 'T3', '10d*': 'T4', '10d': 'T5', '10f*': 'T6',
                '10f': 'T7', '10g*': 'T8', '10g': 'T9', '10h*': 'T10', '10h': 'T11', '10i*': 'T12',
                '10i': 'T13', '10j*': 'T14', '10j': 'T15', '10k*': 'T16', '10k': 'T17',
                '10l*': 'T18', '10l': 'T19'
            }


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


def get_occupations(config):
    shells = config.split()
    
    occupations = {}
    
    for shell in shells:
        n, l, e = list(filter(None, re.split('(\d+)',shell)))
        
        occupations[n + l] = int(e)
    
    return occupations

def checkOutput(file: str, detailed: bool = False):
    """Returns:
        Tuple[bool, str, float, str, float, float, float, float]: 8 return arguments for:
        
        flag to control if the output is complete.\n
        string with the failed orbital label, if any.\n
        value of the largest wavefunction overlap.\n
        string with the jj coupled electron configuration with highest weight.\n
        largest weight, corresponding to the jj coupled configuration.\n
        cycle accuracy.\n
        energy difference.\n
        welton energy of the atomic state.\n
    """
    first: bool = False
    firstOver: bool = False
    
    Diff: float = -1.0
    
    welt: float = 0.0
    
    Overlaps = []
    OverlapsDetail = []
    
    percents = []
    highest_percent: float = 100.0
    
    accuracy: float = 0.0
    
    higher_config: str = ''
    
    failed_orbital: str = ''
    
    remaining_orbs: str = ''
    
    good_overlaps: bool = True
    
    with open(file, "r") as output:
        outputContent = output.readlines()
        
        try:
            for i, line in enumerate(outputContent):
                if "Configuration(s)" in line and " 1 " in line:
                    higher_config = outputContent[i + 1].strip()
                
                if "Common to all configurations" in line:
                    higher_config = line.replace("Common to all configurations", "").strip()
                
                if "List of jj configurations with a weight >= 0.01%" in line:
                    cnt = i + 1
                    while True:
                        if outputContent[cnt] == "\n":
                            break
                        else:
                            try:
                                percent = float(outputContent[cnt].strip().split()[-2])
                            except ValueError:
                                break
                            
                            percents.append((' '.join(outputContent[cnt].strip().split()[:-2]), percent))
                        
                        cnt += 1
                    
                    if percents != []:
                        highest = max(percents, key=lambda x: x[1])
                        remaining_orbs = highest[0]
                        highest_percent = highest[1]
                
                if "Variation of eigenenergy for the last" in line:
                    cnt = i + 1
                    while True:
                        if outputContent[cnt] == "\n":
                            break
                        else:
                            accuracy = round(float(outputContent[cnt].strip().split()[-1]), 6)
                        
                        cnt += 1
                
                if "Overlap integrals" in line and not firstOver and first:
                    firstOver = True
                    cnt = i + 1
                    while True:
                        if outputContent[cnt] == "\n" or "Using Bethe Log for SE of n=" in outputContent[cnt]:
                            break
                        else:
                            try:
                                if detailed:
                                    OverlapsDetail.append(''.join([t.strip() for t in outputContent[cnt].strip().split()[:4]]))
                                
                                Overlaps.append(float(outputContent[cnt].strip().split()[3]))
                            except ValueError:
                                good_overlaps = False
                            try:
                                if detailed:
                                    OverlapsDetail.append(''.join([t.strip() for t in outputContent[cnt].strip().split()[4:]]))
                                
                                Overlaps.append(float(outputContent[cnt].strip().split()[-1]))
                            except ValueError:
                                good_overlaps = False
                        
                        cnt += 1
                
                if "ETOT (a.u.)" in line and not first:
                    first = True
                    Diff = abs(round(float(outputContent[i + 1].split()[1]) - float(outputContent[i + 1].split()[2]), 6))
                
                if "Etot_(Welt.)=" in line:
                    welt = float(line.strip().split()[3])
                
                if "For orbital" in line:
                    failed_orbital = line.strip().split()[-1].strip()
        except IndexError:
            print("Error reading output file for state: " + file)

    higher_config += ' ' + remaining_orbs
    
    if not good_overlaps:
        print("Error reading overlaps for: " + file)
    
    if detailed:
        return first, failed_orbital, OverlapsDetail[Overlaps.index(max(Overlaps, key=lambda x: abs(x)))] if len(Overlaps) > 0 else "< NA | NA > 1.0", higher_config, highest_percent, accuracy, Diff, welt
    
    return first, failed_orbital, max(Overlaps, key=lambda x: abs(x)) if len(Overlaps) > 0 else 1.0, higher_config, highest_percent, accuracy, Diff, welt



ground_occupations = get_occupations(ground_config)


total_configs = sum(
        [sum(
            [sum(
                    [1 for dir3 in os.listdir(input_dir + arguments["-rs"] + "/" + dir1 + "/" + dir2)
                    if eig_keywrd in dir3]
                ) 
            for dir2 in os.listdir(input_dir + arguments["-rs"] + "/" + dir1)
            if '2jj_' in dir2]
            ) 
        for dir1 in os.listdir(input_dir + arguments["-rs"])]
    )

if arguments["-t"] == 'auger':
    total_configs += sum(
        [sum(
            [sum(
                    [1 for dir3 in os.listdir(input_dir + arguments["-as"] + "/" + dir1 + "/" + dir2)
                    if eig_keywrd in dir3]
                ) 
            for dir2 in os.listdir(input_dir + arguments["-as"] + "/" + dir1)
            if '2jj_' in dir2]
            ) 
        for dir1 in os.listdir(input_dir + arguments["-as"])]
    )
    

print("Found a total number of " + str(total_configs) + " eigenstates in " + ("the input directory." if arguments["-t"] == "diagram" else "both input directories"))

def bufcount(filename):
    f = open(filename)                  
    lines = 0
    buf_size = 1024 * 1024
    read_f = f.read # loop optimization

    buf = read_f(buf_size)
    while buf:
        lines += buf.count('\n')
        buf = read_f(buf_size)
        print("Total transition count: " + str(lines), end='\r')

    return lines

#Total number of transitions to process
transition_num = bufcount(input_dir + "/" + arguments["-itr"]) - 2

print("\nDetermining partial widths from rates file...")

# Add the partial widths
partialWidths = {}
with open(input_dir + "/" + arguments["-itr"], "r") as lines:
    for _ in range(header_count):
        header = lines.readline().strip() #header line
    #print(header.split("\t"))
    for i, line in enumerate(lines):
        # print(line)
        print("Processing rate: " + str(i + 1) + "/" + str(transition_num), end='\r')
        
        values = line.strip().split("\t")
        
        Shelli = values[1].strip()
        JJi = values[3].strip()
        Eigeni = values[4].strip()
        
        try:
            Width = float(values[14].strip()) * h
        except ValueError:
            Width = 0.0
        
        key = Shelli + '_' + JJi + '_' + Eigeni
        
        if key in partialWidths:
            partialWidths[key] += Width
        else:
            partialWidths[key] = Width
# print(partialWidths)

print("\nWriting master files with the notation conversion, level energies and partial widths...")

with open(output_dir + arguments["-cfg"].split(".")[0] + "_master." + arguments["-cfg"].split(".")[1], 'w') as out:
    with open(output_dir + arguments["-cfg"], 'w') as out_clean:
        out.write("# Atomic number Z= " + str(Z) + "  Date:" + date.today().strftime("%d-%m-%Y") + "\n\n")
        out.write("# Number	Shelli	ShellLS 2Ji	Eigi	Total Energy (eV)	Ground Energy(eV)	Partial Width (eV)  Branching Ratio  Overlap   Percentage (%)  Accuracy   Energy Diff (eV)\n")
        
        out_clean.write("# Atomic number Z= " + str(Z) + "  Date:" + date.today().strftime("%d-%m-%Y") + "\n\n")
        out_clean.write("# Number	Shelli	2Ji	Eigi	Total Energy (eV)	Ground Energy(eV)	Partial Width (eV)  Branching Ratio  Overlap   Percentage (%)  Accuracy   Energy Diff (eV)\n")
        
        register = 0
        
        # Initial states configurations
        for dir1 in os.listdir(input_dir + arguments["-rs"]):
            for dir2 in os.listdir(input_dir + arguments["-rs"] + "/" + dir1):
                if '2jj_' in dir2:
                    for dir3 in os.listdir(input_dir + arguments["-rs"] + "/" + dir1 + "/" + dir2):
                        if eig_keywrd in dir3:
                            input_file = input_dir + arguments["-rs"] + "/" + dir1 + "/" + dir2 + "/" + dir3 + "/" + dir1 + '_' + dir2.split('2jj_')[1] + '_' + dir3.split(eig_keywrd)[1] + '.f06'
                            if os.path.exists(input_file):
                                register += 1
                                
                                print("Computing level: " + str(register) + "/" + str(total_configs), end="\r")
                                
                                _, _, overlap, _, percent, acc, diff, _ = checkOutput(input_file, True)
                                
                                value = False
                                with open(input_file, 'r') as f:
                                    for line in f:
                                        if 'Etot_(Welt.)=' in line:
                                            elements = line.strip().split()
                                            if len(elements) >= 4:
                                                value = elements[3]
                                                break
                                
                                highest_identifier = search_highest_percentage(input_file, 'List of jj configurations with a weight >= 0.01%', 'Configuration(s)         1 to         1')
                                
                                #Fetch the partial width for this level
                                key = dir1 + '_' + dir2.split("2jj_")[1] + '_' + str(int(dir3.split(eig_keywrd)[1]) + eig_offset)
                                
                                if key in partialWidths:
                                    partialWidth = partialWidths[key]
                                else:
                                    # print("\nMissing partial widths for level: " + key)
                                    partialWidth = 0.0
                                
                                shells = dir1
                                if highest_identifier and value:
                                    #Calculate the relevant occupation numbers for this configuration
                                    occupations = get_occupations(highest_identifier)
                                    
                                    #Calculate the differences between the ground occupations and these ones
                                    diffs = {}
                                    for key in occupations:
                                        if key in ground_occupations:
                                            diffs[key] = occupations[key] - ground_occupations[key]
                                        else:
                                            diffs[key] = occupations[key]
                                    
                                    #Replace the notations for the shells where the occupations changed
                                    keys = [key for key in diffs if diffs[key] != 0]
                                    for key in keys:
                                        if '-' in shells:
                                            shells_pre = shells.split("-")[0]
                                            shells_pre = shells_pre.replace(key.replace("*", ''), siegbahn[key], 1)
                                            shells = shells_pre + '-' + shells.split('-')[1]
                                        else:
                                            shells = shells.replace(key.replace("*", ''), siegbahn[key], 1)
                                    
                                    #Replace any inconclusive occupations left, with the first found
                                    for shell in siegbahn:
                                        if '-' in shells:
                                            shells_pre = shells.split("-")[0]
                                            shells_pre = shells_pre.replace(shell.replace("*", ''), siegbahn[shell])
                                            shells = shells_pre + '-' + shells.split('-')[1]
                                        else:
                                            shells = shells.replace(shell.replace("*", ''), siegbahn[shell])
                                    
                                    #Remove the separators from the original format
                                    shells = shells.replace('_', '')
                                    shells = shells.replace('-', '')
                                    
                                    out.write(f'\t{register}\t\t{shells}\t {dir1}\t {dir2.split("2jj_")[1]}\t {int(dir3.split(eig_keywrd)[1]) + eig_offset}\t\t{value}\t\t{round(float(value) - ground_energy, 5)}\t\t{partialWidth}\t0.0\t\t{overlap}\t\t{percent}\t\t{acc}\t\t{diff}\n')
                                    out_clean.write(f'\t{register}\t\t{shells}\t {dir2.split("2jj_")[1]}\t {int(dir3.split(eig_keywrd)[1]) + eig_offset}\t\t{value}\t\t{round(float(value) - ground_energy, 5)}\t\t{partialWidth}\t0.0\t\t{overlap}\t\t{percent}\t\t{acc}\t\t{diff}\n')
                                elif value:
                                    # No multi configuration weights, i.e. only one configuration for this level
                                    #Replace any inconclusive occupations left, with the first found
                                    for shell in siegbahn:
                                        if '-' in shells:
                                            shells_pre = shells.split("-")[0]
                                            shells_pre = shells_pre.replace(shell.replace("*", ''), siegbahn[shell])
                                            shells = shells_pre + '-' + shells.split('-')[1]
                                        else:
                                            shells = shells.replace(shell.replace("*", ''), siegbahn[shell])
                                    
                                    #Remove the separators from the original format
                                    shells = shells.replace('_', '')
                                    shells = shells.replace('-', '')
                                    
                                    out.write(f'\t{register}\t\t{shells}\t {dir1}\t {dir2.split("2jj_")[1]}\t {int(dir3.split(eig_keywrd)[1]) + eig_offset}\t\t{value}\t\t{round(float(value) - ground_energy, 5)}\t\t{partialWidth}\t0.0\t\t{overlap}\t\t{percent}\t\t{acc}\t\t{diff}\n')
                                    out_clean.write(f'\t{register}\t\t{shells}\t {dir2.split("2jj_")[1]}\t {int(dir3.split(eig_keywrd)[1]) + eig_offset}\t\t{value}\t\t{round(float(value) - ground_energy, 5)}\t\t{partialWidth}\t0.0\t\t{overlap}\t\t{percent}\t\t{acc}\t\t{diff}\n')
                                elif highest_identifier:
                                    #Calculate the relevant occupation numbers for this configuration
                                    occupations = get_occupations(highest_identifier)
                                    
                                    #Calculate the differences between the ground occupations and these ones
                                    diffs = {}
                                    for key in occupations:
                                        if key in ground_occupations:
                                            diffs[key] = occupations[key] - ground_occupations[key]
                                        else:
                                            diffs[key] = occupations[key]
                                    
                                    #Replace the notations for the shells where the occupations changed
                                    keys = [key for key in diffs if diffs[key] != 0]
                                    for key in keys:
                                        if '-' in shells:
                                            shells_pre = shells.split("-")[0]
                                            shells_pre = shells_pre.replace(key.replace("*", ''), siegbahn[key], 1)
                                            shells = shells_pre + '-' + shells.split('-')[1]
                                        else:
                                            shells = shells.replace(key.replace("*", ''), siegbahn[key], 1)
                                    
                                    #Replace any inconclusive occupations left, with the first found
                                    for shell in siegbahn:
                                        if '-' in shells:
                                            shells_pre = shells.split("-")[0]
                                            shells_pre = shells_pre.replace(shell.replace("*", ''), siegbahn[shell])
                                            shells = shells_pre + '-' + shells.split('-')[1]
                                        else:
                                            shells = shells.replace(shell.replace("*", ''), siegbahn[shell])
                                    
                                    #Remove the separators from the original format
                                    shells = shells.replace('_', '')
                                    shells = shells.replace('-', '')
                                    
                                    out.write(f'\t{register}\t\t{shells}\t {dir1}\t {dir2.split("2jj_")[1]}\t {int(dir3.split(eig_keywrd)[1]) + eig_offset}\t\t{overlap}\t\t{percent}\t\t{acc}\t\t{diff}\t\tBUG!!!!!\n')
                                    out_clean.write(f'\t{register}\t\t{shells}\t {dir2.split("2jj_")[1]}\t {int(dir3.split(eig_keywrd)[1]) + eig_offset}\t\t{overlap}\t\t{percent}\t\t{acc}\t\t{diff}\t\tBUG!!!!!\n')
                            else:
                                print(f"{input_file} not found!")
        
        # Final states configurations
        if arguments["-t"] == "auger":
            for dir1 in os.listdir(input_dir + arguments["-as"]):
                for dir2 in os.listdir(input_dir + arguments["-as"] + "/" + dir1):
                    if '2jj_' in dir2:
                        for dir3 in os.listdir(input_dir + arguments["-as"] + "/" + dir1 + "/" + dir2):
                            if eig_keywrd in dir3:
                                input_file = input_dir + arguments["-as"] + "/" + dir1 + "/" + dir2 + "/" + dir3 + "/" + dir1 + '_' + dir2.split('2jj_')[1] + '_' + dir3.split(eig_keywrd)[1] + '.f06'
                                if os.path.exists(input_file):
                                    register += 1
                                    
                                    print("Computing level: " + str(register) + "/" + str(total_configs), end="\r")
                                    
                                    _, _, overlap, _, percent, acc, diff, _ = checkOutput(input_file, True)
                                    
                                    value = False
                                    with open(input_file, 'r') as f:
                                        for line in f:
                                            if 'Etot_(Welt.)=' in line:
                                                elements = line.strip().split()
                                                if len(elements) >= 4:
                                                    value = elements[3]
                                                    break
                                    
                                    highest_identifier = search_highest_percentage(input_file, 'List of jj configurations with a weight >= 0.01%', 'Configuration(s)         1 to         1')
                                    
                                    #Fetch the partial width for this level
                                    key = dir1 + '_' + dir2.split("2jj_")[1] + '_' + str(int(dir3.split(eig_keywrd)[1]) + eig_offset)
                                    if key in partialWidths:
                                        partialWidth = partialWidths[key]
                                    else:
                                        # print("\nMissing partial widths for level: " + key)
                                        partialWidth = 0.0
                                    
                                    shells = dir1
                                    if highest_identifier and value:
                                        #Calculate the relevant occupation numbers for this configuration
                                        occupations = get_occupations(highest_identifier)
                                        
                                        #Calculate the differences between the ground occupations and these ones
                                        diffs = {}
                                        for key in occupations:
                                            if key in ground_occupations:
                                                diffs[key] = occupations[key] - ground_occupations[key]
                                            else:
                                                diffs[key] = occupations[key]
                                        
                                        #Replace the notations for the shells where the occupations changed
                                        keys = [key for key in diffs if diffs[key] != 0]
                                        for key in keys:
                                            if '-' in shells:
                                                shells_pre = shells.split("-")[0]
                                                shells_pre = shells_pre.replace(key.replace("*", ''), siegbahn[key], 1)
                                                shells = shells_pre + '-' + shells.split('-')[1]
                                            else:
                                                shells = shells.replace(key.replace("*", ''), siegbahn[key], 1)
                                        
                                        #Replace any inconclusive occupations left, with the first found
                                        for shell in siegbahn:
                                            if '-' in shells:
                                                shells_pre = shells.split("-")[0]
                                                shells_pre = shells_pre.replace(shell.replace("*", ''), siegbahn[shell])
                                                shells = shells_pre + '-' + shells.split('-')[1]
                                            else:
                                                shells = shells.replace(shell.replace("*", ''), siegbahn[shell])
                                        
                                        #Remove the separators from the original format
                                        shells = shells.replace('_', '')
                                        shells = shells.replace('-', '')
                                        
                                        out.write(f'\t{register}\t\t{shells}\t {dir1}\t {dir2.split("2jj_")[1]}\t {int(dir3.split(eig_keywrd)[1]) + eig_offset}\t\t{value}\t\t{round(float(value) - ground_energy, 5)}\t\t{partialWidth}\t0.0\t\t{overlap}\t\t{percent}\t\t{acc}\t\t{diff}\n')
                                        out_clean.write(f'\t{register}\t\t{shells}\t {dir2.split("2jj_")[1]}\t {int(dir3.split(eig_keywrd)[1]) + eig_offset}\t\t{value}\t\t{round(float(value) - ground_energy, 5)}\t\t{partialWidth}\t0.0\t\t{overlap}\t\t{percent}\t\t{acc}\t\t{diff}\n')
                                    elif value:
                                        # No multi configuration weights, i.e. only one configuration for this level
                                        #Replace any inconclusive occupations left, with the first found
                                        for shell in siegbahn:
                                            if '-' in shells:
                                                shells_pre = shells.split("-")[0]
                                                shells_pre = shells_pre.replace(shell.replace("*", ''), siegbahn[shell])
                                                shells = shells_pre + '-' + shells.split('-')[1]
                                            else:
                                                shells = shells.replace(shell.replace("*", ''), siegbahn[shell])
                                        
                                        #Remove the separators from the original format
                                        shells = shells.replace('_', '')
                                        shells = shells.replace('-', '')
                                        
                                        out.write(f'\t{register}\t\t{shells}\t {dir1}\t {dir2.split("2jj_")[1]}\t {int(dir3.split(eig_keywrd)[1]) + eig_offset}\t\t{value}\t\t{round(float(value) - ground_energy, 5)}\t\t{partialWidth}\t0.0\t\t{overlap}\t\t{percent}\t\t{acc}\t\t{diff}\n')
                                        out_clean.write(f'\t{register}\t\t{shells}\t {dir2.split("2jj_")[1]}\t {int(dir3.split(eig_keywrd)[1]) + eig_offset}\t\t{value}\t\t{round(float(value) - ground_energy, 5)}\t\t{partialWidth}\t0.0\t\t{overlap}\t\t{percent}\t\t{acc}\t\t{diff}\n')
                                    elif highest_identifier:
                                        #Calculate the relevant occupation numbers for this configuration
                                        occupations = get_occupations(highest_identifier)
                                        
                                        #Calculate the differences between the ground occupations and these ones
                                        diffs = {}
                                        for key in occupations:
                                            if key in ground_occupations:
                                                diffs[key] = occupations[key] - ground_occupations[key]
                                            else:
                                                diffs[key] = occupations[key]
                                        
                                        #Replace the notations for the shells where the occupations changed
                                        keys = [key for key in diffs if diffs[key] != 0]
                                        for key in keys:
                                            if '-' in shells:
                                                shells_pre = shells.split("-")[0]
                                                shells_pre = shells_pre.replace(key.replace("*", ''), siegbahn[key], 1)
                                                shells = shells_pre + '-' + shells.split('-')[1]
                                            else:
                                                shells = shells.replace(key.replace("*", ''), siegbahn[key], 1)
                                        
                                        #Replace any inconclusive occupations left, with the first found
                                        for shell in siegbahn:
                                            if '-' in shells:
                                                shells_pre = shells.split("-")[0]
                                                shells_pre = shells_pre.replace(shell.replace("*", ''), siegbahn[shell])
                                                shells = shells_pre + '-' + shells.split('-')[1]
                                            else:
                                                shells = shells.replace(shell.replace("*", ''), siegbahn[shell])
                                        
                                        #Remove the separators from the original format
                                        shells = shells.replace('_', '')
                                        shells = shells.replace('-', '')
                                        
                                        out.write(f'\t{register}\t\t{shells}\t {dir1}\t {dir2.split("2jj_")[1]}\t {int(dir3.split(eig_keywrd)[1]) + eig_offset}\t\t{overlap}\t\t{percent}\t\t{acc}\t\t{diff}\t\tBUG!!!!!\n')
                                        out_clean.write(f'\t{register}\t\t{shells}\t {dir2.split("2jj_")[1]}\t {int(dir3.split(eig_keywrd)[1]) + eig_offset}\t\t{overlap}\t\t{percent}\t\t{acc}\t\t{diff}\t\tBUG!!!!!\n')
                                else:
                                    print(f"{input_file} not found!")

    
print("\nWriting the rates file with the new format and notation...")

if arguments["-t"] == 'diagram':
    os.chdir("./diagram")
    os.system("python ConversionScript_intensity_rates.py " + arguments["-itr"] + " " + arguments["-cfg"].split(".")[0] + "_master." + arguments["-cfg"].split(".")[1] + " " + arguments["-otr"])
elif arguments["-t"] == 'excitation':
    os.chdir("./excitation")
    os.system("python ConversionScript_intensity_rates.py " + arguments["-itr"] + " " + arguments["-cfg"].split(".")[0] + "_master." + arguments["-cfg"].split(".")[1] + " " + arguments["-otr"])
elif arguments["-t"] == 'auger':
    os.chdir("./auger")
    os.system("python ConversionScript_auger_rates.py " + arguments["-itr"] + " " + arguments["-cfg"].split(".")[0] + "_master." + arguments["-cfg"].split(".")[1] + " " + arguments["-otr"])

print()

if "-is" in arguments and "-os" in arguments:
    print("\nWriting the spectrum file with the new format and notation...")

    if arguments["-t"] == 'diagram':
        os.system("python ConversionScript_intensity_spectra.py " + arguments["-is"] + " " + arguments["-itr"] + " " + arguments["-cfg"].split(".")[0] + "_master." + arguments["-cfg"].split(".")[1] + " " + arguments["-os"])
    elif arguments["-t"] == 'excitation':
        os.system("python ConversionScript_excitation_spectra.py " + arguments["-is"] + " " + arguments["-itr"] + " " + arguments["-cfg"].split(".")[0] + "_master." + arguments["-cfg"].split(".")[1] + " " + arguments["-os"])
    elif arguments["-t"] == 'auger':
        os.system("python ConversionScript_auger_spectra.py " + arguments["-is"] + " " + arguments["-itr"] + " " + arguments["-cfg"].split(".")[0] + "_master." + arguments["-cfg"].split(".")[1] + " " + arguments["-os"])

    print()

if "-br" in arguments:
    print("\nUpdating conversion file with the total branching ratios for cascade calculations...")
    if arguments["-t"] == 'diagram':
        os.system("python Calculate_diagram_BR.py " + arguments["-otr"] + " " + arguments["-br"] + " " + arguments["-cfg"])
    elif arguments["-t"] == 'excitation':
        os.system("python Calculate_excitation_BR.py " + arguments["-otr"] + " " + arguments["-br"] + " " + arguments["-cfg"])
    elif arguments["-t"] == 'auger':
        os.system("python Calculate_auger_BR.py " + arguments["-otr"] + " " + arguments["-br"] + " " + arguments["-cfg"])

    print()