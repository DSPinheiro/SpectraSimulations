from datetime import datetime
import sys
import re

# USAGE:
# Run the script with 2 input parameters:
# The filepath to the diagram file calculated by the MCDF script that you want to convert.
# The ground state jj configuration of the atomic system. (Orbitals separated by spaces, use "" in the terminal to input as 1 argument)

# We use this configuration to compare with the electron population in the ionized orbitals and figure out which jj orbital was ionized.
# Sometimes this is not possible due to the nature of the MCDF calculations, where multiple jj configurations are mixed, particularly for auger or satellite transitions.

def convert_inten(file, ground):
    
    # Initial configuration lists
    Shelli = []
    JJi = []
    Eigeni = []
    Configi = []
    Percentagei = []
    
    # Final configuration lists
    Shellf = []
    JJf = []
    Eigenf = []
    Configf = []
    Percentagef = []

    #Transition data lists - ALL VALUES IN eV WHEN APPLICABLE
    Energies = []
    BranchingRatio = []
    LevelRadYield = []
    Intensity = []
    Weight = []
    RadWidth = []
    AugWidth = []
    TotWidth = []
    
    # Dictionary with the groud state configuration
    GroundStateConfig = {}
    
    for term in ground.split():
        tmp = term
        ne = re.sub("[^0-9]", " ", tmp)
        n = ne.split()[0]
        e = ne.split()[1]
        orb = term.split(n)[1].split(e)[0]
        
        GroundStateConfig[n + orb] = int(e)
    print(GroundStateConfig)
    
    with open(file, "r") as lines:
        header = lines.readline().strip() #header line
        
        for i, line in enumerate(lines):
            values = line.strip().split("\t")
            
            # Initial Configuration
            Shelli.append(values[1].strip())
            JJi.append(int(values[3].strip()))
            Eigeni.append(values[4].strip())
            Configi.append(values[5].strip())
            
            try:
                Percentagei.append(float(values[6].strip()))
            except ValueError:
                Percentagei.append(0.0)
            
            # Final Configuration
            Shellf.append(values[7].strip())
            JJf.append(int(values[9].strip()))
            Eigenf.append(values[10].strip())
            Configf.append(values[11].strip())
            
            try:
                Percentagef.append(float(values[12].strip()))
            except ValueError:
                Percentagef.append(0.0)
            
            # Transition Data
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
        elif Shelli[record] == "2s":
            Shelli[record] = "L1"
        elif Shelli[record] == "3s":
            Shelli[record] = "M1"
        elif Shelli[record] == "4s":
            Shelli[record] = "N1"
        elif Shelli[record] == "2p":
            Confi = Configi[record]
            if "2p*" in Confi and "2p" in Confi.replace("2p*", ""):
                Confi = Configi[record]
                ep_ = int(Confi.split("2p*")[1].split()[0])
                ep = int(Confi.replace("2p*", "").split("2p")[1].split()[0])
            elif "2p*" not in GroundStateConfig:
                ep_ = 0
                ep = int(Confi.split("2p")[1].split()[0])
            else:
                ep_ = int(Confi.split("2p*")[1].split()[0])
                ep = 0
            
            if "2p*" in GroundStateConfig and "2p" in GroundStateConfig:
                if ep_ == GroundStateConfig["2p*"] - 1:
                    Shelli[record] = "L2"
                elif ep == GroundStateConfig["2p"] - 1:
                    Shelli[record] = "L3"
                else:
                    # Default case for when we cant determine the ionized jj orbital
                    Shelli[record] = "L2"
            elif "2p*" not in GroundStateConfig:
                if ep_ == 0:
                    Shelli[record] = "L3"
                else:
                    Shelli[record] = "L2"
            else:
                Shelli[record] = "L2"
        elif Shelli[record] == "3p":
            Confi = Configi[record]
            if "3p*" in Confi and "3p" in Confi.replace("3p*", ""):
                Confi = Configi[record]
                ep_ = int(Confi.split("3p*")[1].split()[0])
                ep = int(Confi.replace("3p*", "").split("3p")[1].split()[0])
            elif "3p*" not in GroundStateConfig:
                ep_ = 0
                ep = int(Confi.split("3p")[1].split()[0])
            else:
                ep_ = int(Confi.split("3p*")[1].split()[0])
                ep = 0
            
            if "3p*" in GroundStateConfig and "3p" in GroundStateConfig:
                if ep_ == GroundStateConfig["3p*"] - 1:
                    Shelli[record] = "M2"
                elif ep == GroundStateConfig["3p"] - 1:
                    Shelli[record] = "M3"
                else:
                    # Default case for when we cant determine the ionized jj orbital
                    Shelli[record] = "M2"
            elif "3p*" not in GroundStateConfig:
                if ep_ == 0:
                    Shelli[record] = "M3"
                else:
                    Shelli[record] = "M2"
            else:
                Shelli[record] = "M2"
        elif Shelli[record] == "3d":
            Confi = Configi[record]
            if "3d*" in Confi and "3d" in Confi.replace("3d*", ""):
                Confi = Configi[record]
                ed_ = int(Confi.split("3d*")[1].split()[0])
                ed = int(Confi.replace("3d*", "").split("3d")[1].split()[0])
            elif "3d*" not in GroundStateConfig:
                ed_ = 0
                ed = int(Confi.split("3d")[1].split()[0])
            else:
                ed_ = int(Confi.split("3d*")[1].split()[0])
                ed = 0
            
            if "3d*" in GroundStateConfig and "3d" in GroundStateConfig:
                if ed_ == GroundStateConfig["3d*"] - 1:
                    Shelli[record] = "M4"
                elif ed == GroundStateConfig["3d"] - 1:
                    Shelli[record] = "M5"
                else:
                    # Default case for when we cant determine the ionized jj orbital
                    Shelli[record] = "M4"
            elif "3d*" not in GroundStateConfig:
                if ed_ == 0:
                    Shelli[record] = "M5"
                else:
                    Shelli[record] = "M4"
            else:
                Shelli[record] = "M4"
        else:
            print("Orbital conversion not implemented for: " + Shelli[record])
        
        if Shellf[record] == "1s":
            Shellf[record] = "K1"
        elif Shellf[record] == "2s":
            Shellf[record] = "L1"
        elif Shellf[record] == "3s":
            Shellf[record] = "M1"
        elif Shellf[record] == "4s":
            Shellf[record] = "N1"
        elif Shellf[record] == "2p":
            Conff = Configf[record]
            if "2p*" in Conff and "2p" in Conff.replace("2p*", ""):
                Conff = Configf[record]
                ep_ = int(Conff.split("2p*")[1].split()[0])
                ep = int(Conff.replace("2p*", "").split("2p")[1].split()[0])
            elif "2p*" not in GroundStateConfig:
                ep_ = 0
                ep = int(Conff.split("2p")[1].split()[0])
            else:
                ep_ = int(Conff.split("2p*")[1].split()[0])
                ep = 0
            
            if "2p*" in GroundStateConfig and "2p" in GroundStateConfig:
                if ep_ == GroundStateConfig["2p*"] - 1:
                    Shellf[record] = "L2"
                elif ep == GroundStateConfig["2p"] - 1:
                    Shellf[record] = "L3"
                else:
                    # Default case for when we cant determine the ionized jj orbital
                    Shellf[record] = "L2"
            elif "2p*" not in GroundStateConfig:
                if ep_ == 0:
                    Shellf[record] = "L3"
                else:
                    Shellf[record] = "L2"
            else:
                Shellf[record] = "L2"
        elif Shellf[record] == "3p":
            Conff = Configf[record]
            if "3p*" in Conff and "3p" in Conff.replace("3p*", ""):
                Conff = Configf[record]
                ep_ = int(Conff.split("3p*")[1].split()[0])
                ep = int(Conff.replace("3p*", "").split("3p")[1].split()[0])
            elif "3p*" not in GroundStateConfig:
                ep_ = 0
                ep = int(Conff.split("3p")[1].split()[0])
            else:
                ep_ = int(Conff.split("3p*")[1].split()[0])
                ep = 0
            
            if "3p*" in GroundStateConfig and "3p" in GroundStateConfig:
                if ep_ == GroundStateConfig["3p*"] - 1:
                    Shellf[record] = "M2"
                elif ep == GroundStateConfig["3p"] - 1:
                    Shellf[record] = "M3"
                else:
                    # Default case for when we cant determine the ionized jj orbital
                    Shellf[record] = "M2"
            elif "3p*" not in GroundStateConfig:
                if ep_ == 0:
                    Shellf[record] = "M3"
                else:
                    Shellf[record] = "M2"
            else:
                Shellf[record] = "M2"
        elif Shellf[record] == "3d":
            Conff = Configf[record]
            if "3d*" in Conff and "3d" in Conff.replace("3d*", ""):
                Conff = Configf[record]
                ed_ = int(Conff.split("3d*")[1].split()[0])
                ed = int(Conff.replace("3d*", "").split("3d")[1].split()[0])
            elif "3d*" not in GroundStateConfig:
                ed_ = 0
                ed = int(Conff.split("3d")[1].split()[0])
            else:
                ed_ = int(Conff.split("3d*")[1].split()[0])
                ed = 0
            
            if "3d*" in GroundStateConfig and "3d" in GroundStateConfig:
                if ed_ == GroundStateConfig["3d*"] - 1:
                    Shellf[record] = "M4"
                elif ed == GroundStateConfig["3d"] - 1:
                    Shellf[record] = "M5"
                else:
                    # Default case for when we cant determine the ionized jj orbital
                    Shellf[record] = "M4"
            elif "3d*" not in GroundStateConfig:
                if ed_ == 0:
                    Shellf[record] = "M5"
                else:
                    Shellf[record] = "M4"
            else:
                Shellf[record] = "M4"
        else:
            print("Orbital conversion not implemented for: " + Shellf[record])


    with open(file.split(".txt")[0] + "_converted.out", "w") as output:
        output.write("# Atomic number Z= 26  Date:" + datetime.today().strftime('%d-%m-%Y') + "\n\n")
        output.write("# Number Shelli\t  2Ji\t\t  Eigi ---> \t Shellf\t  2Jf\t\t  Eigf\t\tEnergy(eV)\t\t\tBranchingRatio\t\t\t LevelRadYield\t\t Intensity(eV)\t\t\t Weight(%)\t\t  RadWidth(eV)\t\t  AugWidth(eV)\t\t  TotWidth(eV)\n")
        
        for i in range(len(Shelli)):
            output.write(f'\t{str(i+1):>2}\t{Shelli[i]:>5}\t{str(JJi[i]):>5}\t{Eigeni[i]:>10} ---> \t{Shellf[i]:>5}\t{str(JJf[i]):>5}\t{Eigenf[i]:>10}\t{Energies[i]:>18}\t{BranchingRatio[i]:>23}\t{LevelRadYield[i]:>18}\t{Intensity[i]:>18}\t{Weight[i]:>18}\t{RadWidth[i]:>18}\t{AugWidth[i]:>18}\t{TotWidth[i]:>18}\n')

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Expected file to convert in input and ground state configuration... terminating.")
        exit()
    
    file = sys.argv[1]
    ground = sys.argv[2]
    convert_inten(file, ground)