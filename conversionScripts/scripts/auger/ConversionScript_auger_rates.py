from datetime import datetime
import sys

h = 4.135667696 * 10**(-15)

Configs = []

input_dir = '../../input/'
output_dir = '../../output/'

if len(sys.argv) != 4:
    print("Expected 3 arguments:")
    print("filename for the transition rates file with the original format;")
    print("filename for the output file of the 'fetchTotalEnergies.py' script, which contains the conversion between formats;")
    print("filename for the transition rates file with the new format.")
    exit(-1)

input_rates = sys.argv[1]
conversion_file = sys.argv[2]
output_rates = sys.argv[3]

# Read the conversion file
with open(output_dir + "/" + conversion_file, "r") as levels:
    levels.readline().strip() #header line
    levels.readline().strip() #header line
    levels.readline().strip() #header line
    
    for line in levels:
        values = line.strip().split()
        Configs.append(values)

Conversion_dict = {}
for conf in Configs:
    Conversion_dict[conf[2] + "_" + conf[3] + "_" + conf[4]] = conf[1]


def convertShell(shell, jj, eigv):
    return Conversion_dict[shell + "_" + str(jj) + "_" + str(eigv)]


def readLine(line):
    values = line.strip().split("\t")
    
    Shelli = values[1].strip()
    LowerConfigi = values[2].strip()
    JJi = int(values[3].strip())
    Eigeni = values[4].strip()
    Configi = values[5].strip()
    try:
        Percentagei = float(values[6].strip())
    except:
        Percentagei = float(0.0)
    
    Shellf = values[7].strip()
    LowerConfigf = values[8].strip()
    JJf = int(values[9].strip())
    Eigenf = values[10].strip()
    Configf = values[11].strip()
    try:
        Percentagef = float(values[12].strip())
    except:
        Percentagef = float(0.0)
    
    Energies = values[13].strip()
    Rate = values[14].strip()
    try:
        Width = float(Rate[-1]) * h
    except:
        Width = 0.0
    
    TotRateIS = values[15].strip()
    BranchingRatio = values[16].strip()
    
    return Shelli, LowerConfigi, JJi, Eigeni, Configi, Percentagei, Shellf, LowerConfigf, \
        JJf, Eigenf, Configf, Percentagef, Energies, Rate, Width, TotRateIS, BranchingRatio


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
transition_num = bufcount(input_dir + "/" + input_rates) - 2

# Open the output file
with open(output_dir + "/" + output_rates, "w") as output:
    # Write the header lines
    output.write("# Atomic number Z= 29  Date:" + datetime.today().strftime('%d-%m-%Y') + "\n\n")
    output.write("# Register Shelli\t2Ji\t\tEigi\t ---> \t Shellf\t\t2Jf\t\tEigf\tEnergy(eV)\t\t\tRate(s-1)\t\tWidth(eV)\n")
    
    # Open the input file
    with open(input_dir + "/" + input_rates, "r") as lines:
        header = lines.readline().strip() #header line
        header = lines.readline().strip() #header line
        
        # Convert each line and write the new format to the output
        # This way we can convert any size file without worrying about RAM
        for i, line in enumerate(lines):
            # print(line)
            print("Processing transition: " + str(i + 1) + "/" + str(transition_num), end='\r')
            
            Shelli, LowerConfigi, JJi, Eigeni, Configi, Percentagei, Shellf, LowerConfigf, \
            JJf, Eigenf, Configf, Percentagef, Energies, Rate, Width, TotRateIS, \
            BranchingRatio = readLine(line)
            
            Shelli = convertShell(Shelli, JJi, Eigeni)
            Shellf = convertShell(Shellf, JJf, Eigenf)
            
            output.write(f'\t{str(i+1):<3}\t{Shelli:>5}\t{str(JJi):>5}\t{Eigeni:>6}\t\t ---> \t{Shellf:>5}\t{str(JJf):>5}\t{Eigenf:>6}\t\t{Energies:<18}\t{Rate:<15}\t{Width:<15}\n')