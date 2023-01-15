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
    with open("Cu_spectrum_auger.txt", "r") as lines:
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
        if "1s" in Shellf[record]:
            Shellf[record] = Shellf[record].replace("1s", "K1").replace("_", "")
        
        if Shelli[record] == "2s":
            Shelli[record] = "L1"
        if "2s" in Shellf[record]:
            Shellf[record] = Shellf[record].replace("2s", "L1").replace("_", "")
        
        if Shelli[record] == "3s":
            Shelli[record] = "M1"
        if "3s" in Shellf[record]:
            Shellf[record] = Shellf[record].replace("3s", "M1").replace("_", "")
        
        if Shelli[record] == "4s":
            Shelli[record] = "N1"
        if "4s" in Shellf[record]:
            Shellf[record] = Shellf[record].replace("4s", "N1").replace("_", "")
        
        if Shelli[record] == "2p":
            if "2p4" in Configi[record]:
                Shelli[record] = "L2"
            elif "2p*2" in Configi[record]:
                Shelli[record] = "L3"
        if "2p" in Shellf[record]:
            if "2p*1" in Configf[record] and "2p4" in Configf[record]:
                Shellf[record] = Shellf[record].replace("2p", "L2").replace("_", "")
            elif "2p*2" in Configf[record] and "2p3" in Configf[record]:
                Shellf[record] = Shellf[record].replace("2p", "L3").replace("_", "")
            elif "2p4" in Configf[record] and "2p*1" not in Configf[record]:
                Shellf[record] = Shellf[record].replace("2p", "L2").replace("_", "")
            elif "2p2" in Configf[record]:
                Shellf[record] = Shellf[record].replace("2p", "L3").replace("_", "")
            elif "2p*1" in Configf[record] and "2p3" in Configf[record]:
                Shellf[record] = "L2L3"
        
        if Shelli[record] == "3p":
            if "3p4" in Configi[record]:
                Shelli[record] = "M2"
            elif "3p3" in Configi[record] or "3p2" in Configi[record]:
                Shelli[record] = "M3"
        if "3p" in Shellf[record]:
            if "3p*1" in Configf[record] and "3p4" in Configf[record]:
                Shellf[record] = Shellf[record].replace("3p", "M2").replace("_", "")
            elif "3p*2" in Configf[record] and "3p3" in Configf[record]:
                Shellf[record] = Shellf[record].replace("3p", "M3").replace("_", "")
            elif "3p4" in Configf[record] and "3p*1" not in Configf[record]:
                Shellf[record] = Shellf[record].replace("3p", "M2").replace("_", "")
            elif "3p2" in Configf[record]:
                Shellf[record] = Shellf[record].replace("3p", "M3").replace("_", "")
            elif "3p*1" in Configf[record] and "3p3" in Configf[record]:
                Shellf[record] = "M2M3"
        
        if Shelli[record] == "3d":
            if "3d*3" in Configi[record]:
                Shelli[record] = "M4"
            elif "3d*4" in Configi[record]:
                Shelli[record] = "M5"
        if "3d" in Shellf[record]:
            if "3d*3" in Configf[record] and "3d6" in Configf[record]:
                Shellf[record] = Shellf[record].replace("3d", "M4").replace("_", "")
            elif "3d*4" in Configf[record] and "3d5" in Configf[record]:
                Shellf[record] = Shellf[record].replace("3d", "M5").replace("_", "")
            elif "3d6" in Configf[record] and "3d*2" in Configf[record]:
                Shellf[record] = Shellf[record].replace("3d", "M4").replace("_", "")
            elif "3d4" in Configf[record]:
                Shellf[record] = Shellf[record].replace("3d", "M5").replace("_", "")
            elif "3d*3" in Configf[record] and "3d5" in Configf[record]:
                Shellf[record] = "M4M5"
        
    
    with open("29-augrate.out", "w") as output:
        output.write("# Atomic number Z= 29  Date:" + datetime.today().strftime('%d-%m-%Y') + "\n\n")
        output.write("# Number Shelli\t  2Ji\t\t  Eigi ---> \t Shellf\t  2Jf\t\t  Eigf\t\tEnergy(eV)\t\t\tBranchingRatio\t\t\t LevelRadYield\t\t Intensity(eV)\t\t\t Weight(%)\t\t  RadWidth(eV)\t\t  AugWidth(eV)\t\t  TotWidth(eV)\n")
        
        for i in range(len(Shelli)):
            output.write(f'\t{str(i+1):>2}\t{Shelli[i]:>5}\t{str(JJi[i]):>5}\t{Eigeni[i]:>10} ---> \t{Shellf[i]:>5}\t{str(JJf[i]):>5}\t{Eigenf[i]:>10}\t{Energies[i]:>18}\t{BranchingRatio[i]:>23}\t{LevelRadYield[i]:>18}\t{Intensity[i]:>18}\t{Weight[i]:>18}\t{RadWidth[i]:>18}\t{AugWidth[i]:>18}\t{TotWidth[i]:>18}\n')

if __name__ == "__main__":
   main()