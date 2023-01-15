from datetime import datetime
import sys

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

def main():
    with open("29-satrate_5d.out", "r") as lines:
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
            
    
    with open("../29/Shake_up/29-groundsatenergy_5d.out", "r") as lines:
        header = lines.readline().strip() #header line
        lines.readline().strip() #header line
        lines.readline().strip() #header line
        #print(header.split("\t"))
        for i, line in enumerate(lines):
            values = line.strip().split()
            print(values)
            Configs.append(values)
    
    for conf in Configs:
        totalWidth = 0.0
        
        for i, s in enumerate(Shelli):
            if s == conf[1] and JJi[i] == conf[2] and Eigeni[i] == conf[3]:
                totalWidth += float(Width[i])
        
        print(totalWidth)




if __name__ == "__main__":
   main()