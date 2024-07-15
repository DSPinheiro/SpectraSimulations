import sys


input_dir = '../../input/'
output_dir = '../../output/'

if len(sys.argv) != 4:
    print("Expected 3 arguments:")
    print("filename for the auger rates file in seigbahn notation;")
    print("filename for the radiative rates file in seigbahn notation;")
    print("filename for the output file of the 'masterConverter.py' script, which contains the conversion between formats;")
    exit(-1)

input_rates_aug = sys.argv[1]
input_rates_rad = sys.argv[2]
conversion_file = sys.argv[3]

Configs = []
headings = []

with open(output_dir + "/" + conversion_file, "r") as lines:
    headings.append(lines.readline()) #header line
    headings.append(lines.readline()) #header line
    headings.append(lines.readline()) #header line
    
    for i, line in enumerate(lines):
        values = line.strip().split()
        Configs.append(values)


RadShelli = []
RadJJi = []
RadShellf = []
RadJJf = []
RadRate = []


AugShelli = []
AugJJi = []
AugShellf = []
AugJJf = []
AugEigvf = []
AugRate = []

BR = []


with open(output_dir + "/" + input_rates_rad, "r") as intFile:
    intFile.readline()
    intFile.readline()
    intFile.readline()
    
    for line in intFile:
        values = line.strip().split()
        values = list(filter(None, values))
        
        RadShelli.append(values[1].strip())
        RadJJi.append(values[2].strip())
        
        RadShellf.append(values[5].strip())
        RadJJf.append(values[6].strip())
        
        RadRate.append(values[9].strip())

with open(output_dir + "/" + input_rates_aug, "r") as augFile:
    augFile.readline()
    augFile.readline()
    augFile.readline()
    
    for line in augFile:
        values = line.strip().split()
        values = list(filter(None, values))
        
        AugShelli.append(values[1].strip())
        AugJJi.append(values[2].strip())
        
        AugShellf.append(values[5].strip())
        AugJJf.append(values[6].strip())
        AugEigvf.append(values[7].strip())
        
        AugRate.append(values[9].strip())


for conf in Configs:
    radShells = []
    
    for i, s in enumerate(AugShelli):
        if s not in radShells and AugShellf[i] == conf[1] and AugJJf[i] == conf[2] and AugEigvf[i] == conf[3]:
            radShells.append(s)
    
    RadTotRate = sum([float(rate) * (int(RadJJi[i]) + 1) for i, rate in enumerate(RadRate) if RadShelli[i] in radShells])
    AugTotRate = sum([float(rate) * (int(AugJJi[i]) + 1) for i, rate in enumerate(AugRate) if AugShelli[i] in radShells])
    
    AugSARate = sum([float(rate) * (int(AugJJi[i]) + 1) for i, rate in enumerate(AugRate) if AugShellf[i] == conf[1] and AugJJf[i] == conf[2] and AugEigvf[i] == conf[3]])
    
    if radShells:
        BR.append(AugSARate / (RadTotRate + AugTotRate))
    else:
        BR.append(0)
    
    conf.insert(8, str(BR[-1]))
    # print(conf[1] + " " + conf[2] + " " + conf[3] + ": BR = auger(" + str(AugSARate) + ") / radiative(" + str(RadTotRate) + ") + auger(" + str(AugTotRate) + ") = " + str(BR[-1]))


with open(output_dir + "/" + conversion_file, "w") as cfg:
    for header in headings:
        cfg.write(header)
    
    for conf in Configs:
        cfg.write('\t'.join(conf) + "\n")