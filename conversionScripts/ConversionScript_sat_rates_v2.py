from datetime import datetime
import sys

Shelli = []
LowerConfigi = []
JJi = []
Eigeni = []
Configi = []
Percentagei = []

Shellf = []
LowerConfigf = []
JJf = []
Eigenf = []
Configf = []
Percentagef = []

#ALL VALUES IN eV WHEN APPLICABLE
Energies = []
Rate = []
Width = []
MultipoleNum = []
TotRateIS = []
BranchingRatio = []
MultipoleRates = []

h = 4.135667696 * 10**(-15)

Configs = []

def main():
    with open("Cu_rates_satellites_4s.txt", "r") as lines:
        header = lines.readline().strip() #header line
        #print(header.split("\t"))
        for i, line in enumerate(lines):
            values = line.strip().split("\t")
            
            Shelli.append(values[1].strip())
            LowerConfigi.append(values[2].strip())
            JJi.append(int(values[3].strip()))
            Eigeni.append(values[4].strip())
            Configi.append(values[5].strip())
            try:
                Percentagei.append(float(values[6].strip()))
            except:
                Percentagei.append(float(0.0))
            
            Shellf.append(values[7].strip())
            LowerConfigf.append(values[8].strip())
            JJf.append(int(values[9].strip()))
            Eigenf.append(values[10].strip())
            Configf.append(values[11].strip())
            try:
                Percentagef.append(float(values[12].strip()))
            except:
                Percentagef.append(float(0.0))
            
            Energies.append(values[13].strip())
            Rate.append(values[14].strip())
            Width.append(float(Rate[-1]) * h)
            MultipoleNum.append(values[15].strip())
            TotRateIS.append(values[16].strip())
            BranchingRatio.append(values[17].strip())
            MultipoleRates.append("\t".join(values[18:]).strip())
    
    with open("29-groundsatenergy_4s.out", "r") as levels:
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

    with open("29-satrate_4s.out", "w") as output:
        output.write("# Atomic number Z= 29  Date:" + datetime.today().strftime('%d-%m-%Y') + "\n\n")
        output.write("# Register Shelli\t2Ji\t\tEigi\t ---> \t Shellf\t\t2Jf\t\tEigf\tEnergy(eV)\t\t\tRate(s-1)\t\tWidth(eV)\n")
        
        for i in range(len(Shelli)):
            output.write(f'\t{str(i+1):<3}\t{Shelli[i]:>5}\t{str(JJi[i]):>5}\t{Eigeni[i]:>6}\t\t ---> \t{Shellf[i]:>5}\t{str(JJf[i]):>5}\t{Eigenf[i]:>6}\t\t{Energies[i]:<18}\t{Rate[i]:<15}\t{Width[i]:<15}\n')

if __name__ == "__main__":
   main()