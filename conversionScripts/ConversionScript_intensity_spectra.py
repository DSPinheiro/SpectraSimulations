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

#shift = "1eV"
#shiftType = "rel"

def main():
    with open("Cu_spectrum_diagram.txt", "r") as lines:
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

    for record in range(len(Shelli)):
        if Shelli[record] == "1s":
            Shelli[record] = "K1"
        if Shellf[record] == "1s":
            Shellf[record] = "K1"
        
        if Shelli[record] == "2s":
            Shelli[record] = "L1"
        if Shellf[record] == "2s":
            Shellf[record] = "L1"
        
        if Shelli[record] == "3s":
            Shelli[record] = "M1"
        if Shellf[record] == "3s":
            Shellf[record] = "M1"
        
        if Shelli[record] == "4s":
            Shelli[record] = "N1"
        if Shellf[record] == "4s":
            Shellf[record] = "N1"
        
        if Shelli[record] == "2p":
            if "2p4" in Configi[record]:
                Shelli[record] = "L2"
            elif "2p*2" in Configi[record]:
                Shelli[record] = "L3"
        if Shellf[record] == "2p":
            if "2p4" in Configf[record]:
                Shellf[record] = "L2"
            elif "2p*2" in Configf[record]:
                Shellf[record] = "L3"
        
        if Shelli[record] == "3p":
            if "3p4" in Configi[record]:
                Shelli[record] = "M2"
            elif "3p3" in Configi[record] or "3p2" in Configi[record]:
                Shelli[record] = "M3"
        if Shellf[record] == "3p":
            if "3p4" in Configf[record]:
                Shellf[record] = "M2"
            elif "3p3" in Configf[record] or "3p2" in Configf[record]:
                Shellf[record] = "M3"
        
        if Shelli[record] == "3d":
            if "3d*3" in Configi[record]:
                Shelli[record] = "M4"
            elif "3d*4" in Configi[record]:
                Shelli[record] = "M5"
        if Shellf[record] == "3d":
            if "3d*3" in Configf[record]:
                Shellf[record] = "M4"
            elif "3d*4" in Configf[record]:
                Shellf[record] = "M5"

    with open("29-intensity.out", "w") as output:
        output.write("# Atomic number Z= 29  Date:" + datetime.today().strftime('%d-%m-%Y') + "\n\n")
        output.write("# Number Shelli\t  2Ji\t\t  Eigi ---> \t Shellf\t  2Jf\t\t  Eigf\t\tEnergy(eV)\t\t\tBranchingRatio\t\t\t LevelRadYield\t\t Intensity(eV)\t\t\t Weight(%)\t\t  RadWidth(eV)\t\t  AugWidth(eV)\t\t  TotWidth(eV)\n")
        
        for i in range(len(Shelli)):
            output.write(f'\t{str(i+1):>2}\t{Shelli[i]:>5}\t{str(JJi[i]):>5}\t{Eigeni[i]:>10} ---> \t{Shellf[i]:>5}\t{str(JJf[i]):>5}\t{Eigenf[i]:>10}\t{Energies[i]:>18}\t{BranchingRatio[i]:>23}\t{LevelRadYield[i]:>18}\t{Intensity[i]:>18}\t{Weight[i]:>18}\t{RadWidth[i]:>18}\t{AugWidth[i]:>18}\t{TotWidth[i]:>18}\n')

if __name__ == "__main__":
   main()