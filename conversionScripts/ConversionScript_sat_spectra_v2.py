from datetime import datetime
import sys

Shelli = []
JJi = []
Eigeni = []
Configi = []
Percentagei = []

Shellf = []
JJf = []
Eigenf = []
Configf = []
Percentagef = []

#ALL VALUES IN eV WHEN APPLICABLE
Energies = []
BranchingRatio = []
LevelRadYield = []
Intensity = []
Weight = []
RadWidth = []
AugWidth = []
TotWidth = []

Configs = []


def main():
    with open("Cu_5d_spectrum_sat.txt", "r") as lines:
        header = lines.readline().strip() #header line
        #print(header.split("\t"))
        for i, line in enumerate(lines):
            values = line.strip().split("\t")
            #print(values)
            
            Shelli.append(values[1].strip())
            JJi.append(int(values[3].strip()))
            Eigeni.append(values[4].strip())
            Configi.append(values[5].strip())
            
            try:
                Percentagei.append(float(values[6].strip()))
            except ValueError:
                Percentagei.append(0.0)
            
            Shellf.append(values[7].strip())
            JJf.append(int(values[9].strip()))
            Eigenf.append(values[10].strip())
            Configf.append(values[11].strip())
            
            try:
                Percentagef.append(float(values[12].strip()))
            except ValueError:
                Percentagef.append(0.0)
            
            Energies.append(values[13].strip())
            BranchingRatio.append("0.0")
            LevelRadYield.append("0.0")
            Intensity.append(values[15].strip())
            Weight.append("0.0")
            RadWidth.append("0.0")
            AugWidth.append("0.0")
            TotWidth.append(values[16].strip())
    
    with open("29-groundsatenergy_5d.out", "r") as levels:
        levels.readline().strip() #header line
        levels.readline().strip() #header line
        levels.readline().strip() #header line
        
        for line in levels:
            values = line.strip().split()
            Configs.append(values)
    
    for record, shell in enumerate(Shelli):
        foundi = False
        foundf = False
        for conf in Configs:
            if conf[2] == shell and int(conf[3]) == JJi[record] and conf[4] == Eigeni[record]:
                Shelli[record] = conf[1]
                foundi = True
            if conf[2] == Shellf[record] and int(conf[3]) == JJf[record] and conf[4] == Eigenf[record]:
                Shellf[record] = conf[1]
                foundf = True
            
            if foundi and foundf:
                break
    
    with open("29-satinty_5d.out", "w") as output:
        output.write("# Atomic number Z= 29  Date:" + datetime.today().strftime('%d-%m-%Y') + "\n\n")
        output.write("# Number Shelli\t  2Ji\t\t  Eigi ---> \t Shellf\t  2Jf\t\t  Eigf\t\tEnergy(eV)\t\t\tBranchingRatio\t\t\t LevelRadYield\t\t Intensity(eV)\t\t\t Weight(%)\t\t  RadWidth(eV)\t\t  AugWidth(eV)\t\t  TotWidth(eV)\n")
        
        for i in range(len(Shelli)):
            output.write(f'\t{str(i+1):>2}\t{Shelli[i]:>5}\t{str(JJi[i]):>5}\t{Eigeni[i]:>10} ---> \t{Shellf[i]:>5}\t{str(JJf[i]):>5}\t{Eigenf[i]:>10}\t{Energies[i]:>18}\t{BranchingRatio[i]:>23}\t{LevelRadYield[i]:>18}\t{Intensity[i]:>18}\t{Weight[i]:>18}\t{RadWidth[i]:>18}\t{AugWidth[i]:>18}\t{TotWidth[i]:>18}\n')

if __name__ == "__main__":
   main()