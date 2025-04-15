from datetime import datetime
import sys

Configs = []

input_dir = '../../input/'
output_dir = '../../output/'

if len(sys.argv) != 5:
    print("Expected 4 arguments:")
    print("filename for the spectra file with the original format;")
    print("filename for the rates file with the original format;")
    print("filename for the output file which contains the conversion between formats;")
    print("filename for the spectra file with the new format.")
    exit(-1)

input_spectra = sys.argv[1]
input_rates = sys.argv[2]
conversion_file = sys.argv[3]
output_spectra = sys.argv[4]

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



brDict = {}

with open(input_dir + "/" + input_rates, "r") as rates:
    header = rates.readline().strip() #header line
    header = rates.readline().strip() #header line
    
    for i, line in enumerate(rates):
        values = line.strip().split("\t")
        
        Shelli = values[1].strip()
        JJi = values[3].strip()
        Eigeni = values[4].strip()
        Shellf = values[7].strip()
        JJf = values[9].strip()
        Eigenf = values[10].strip()
        
        BranchingRatio = values[16].strip()
        
        key = Shelli + "_" + JJi + "_" + Eigeni + "->" + Shellf + "_" + JJf + "_" + Eigenf
        
        brDict[key] = BranchingRatio



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
    
    key = Shelli + "_" + str(JJi) + "_" + Eigeni + "->" + Shellf + "_" + str(JJf) + "_" + Eigenf
    BranchingRatio = brDict[key]
    
    LevelRadYield = "0.0"
    Intensity = values[15].strip()
    Weight = "0.0"
    RadWidth = "0.0"
    AugWidth = "0.0"
    TotWidth = values[16].strip()
    
    
    return Shelli, LowerConfigi, JJi, Eigeni, Configi, Percentagei, Shellf, LowerConfigf, \
        JJf, Eigenf, Configf, Percentagef, Energies, BranchingRatio, LevelRadYield, Intensity, \
        Weight, RadWidth, AugWidth, TotWidth


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
transition_num = bufcount(input_dir + "/" + input_spectra) - 2

# Open the output file
with open(output_dir + "/" + output_spectra, "w") as output:
    # Write the header lines
    output.write("# Atomic number Z= 29  Date:" + datetime.today().strftime('%d-%m-%Y') + "\n\n")
    output.write("# Number Shelli\t  2Ji\t\t  Eigi ---> \t Shellf\t  2Jf\t\t  Eigf\t\tEnergy(eV)\t\t\tBranchingRatio\t\t\t LevelRadYield\t\t Intensity(eV)\t\t\t Weight(%)\t\t  RadWidth(eV)\t\t  AugWidth(eV)\t\t  TotWidth(eV)\n")
    
    # Open the input file
    with open(input_dir + "/" + input_spectra, "r") as lines:
        header = lines.readline().strip() #header line
        header = lines.readline().strip() #header line
        
        # Convert each line and write the new format to the output
        # This way we can convert any size file without worrying about RAM
        for i, line in enumerate(lines):
            print("Processing transition: " + str(i + 1) + "/" + str(transition_num), end='\r')
            
            Shelli, LowerConfigi, JJi, Eigeni, Configi, Percentagei, Shellf, LowerConfigf, \
            JJf, Eigenf, Configf, Percentagef, Energies, BranchingRatio, LevelRadYield, Intensity, \
            Weight, RadWidth, AugWidth, TotWidth = readLine(line)
            
            Shelli = convertShell(Shelli, JJi, Eigeni)
            Shellf = convertShell(Shellf, JJf, Eigenf)    
            
            output.write(f'\t{str(i+1):>2}\t{Shelli:>5}\t{str(JJi):>5}\t{Eigeni:>10} ---> \t{Shellf:>5}\t{str(JJf):>5}\t{Eigenf:>10}\t{Energies:>18}\t{BranchingRatio:>23}\t{LevelRadYield:>18}\t{Intensity:>18}\t{Weight:>18}\t{RadWidth:>18}\t{AugWidth:>18}\t{TotWidth:>18}\n')
