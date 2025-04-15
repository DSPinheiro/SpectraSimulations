import sys


input_dir = '../../input/'
output_dir = '../../output/'

if len(sys.argv) != 5:
    print("Expected 4 arguments:")
    print("filename for the rates file in seigbahn notation;")
    print("filename for the output file of the 'masterConverter.py' script, which contains the conversion between formats;")
    print("filename for the spectra file with the new format.")
    exit(-1)

input_rates = sys.argv[1]
conversion_file = sys.argv[2]
output_rates = sys.argv[3]

Configs = []


with open(output_dir + "/" + conversion_file, "r") as lines:
    header = lines.readline().strip() #header line
    lines.readline().strip() #header line
    lines.readline().strip() #header line
    
    for i, line in enumerate(lines):
        values = line.strip().split()
        Configs.append(values)


Shelli = []
JJi = []
Eigeni = []

Shellf = []
JJf = []
Eigenf = []

#ALL VALUES IN eV WHEN APPLICABLE
Energies = []
Rate = []
Width = []

Configs = []

with open(input_dir + "/" + input_rates, "r") as lines:
    header = lines.readline().strip() #header line
    lines.readline().strip() #header line
    lines.readline().strip() #header line
    #print(header.split("\t"))
    for i, line in enumerate(lines):
        values = line.strip().split()
        #print(values)
        
        Shelli.append(values[1].strip())
        JJi.append(values[2].strip())
        Eigeni.append(values[3].strip())
        
        Shellf.append(values[5].strip())
        JJf.append(values[6].strip())
        Eigenf.append(values[7].strip())
        
        Energies.append(values[8].strip())
        Rate.append(values[9].strip())
        Width.append(values[10].strip())
        

for conf in Configs:
    totalWidth = 0.0
    
    for i, s in enumerate(Shelli):
        if s == conf[1] and JJi[i] == conf[2] and Eigeni[i] == conf[3]:
            totalWidth += float(Width[i])
    
    print(totalWidth)