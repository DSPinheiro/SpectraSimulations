with open("29-satinty_4s.out", 'w') as monopolarSat:
    
    monopolarSat.write("# Atomic number Z= 29  Date:11-01-2023\n\n")
    monopolarSat.write("# Number Shelli	  2Ji		  Eigi ---> 	 Shellf	  2Jf		  Eigf		Energy(eV)			BranchingRatio			 LevelRadYield		 Intensity(eV)			 Weight(%)		  RadWidth(eV)		  AugWidth(eV)		  TotWidth(eV)\n")
    
    with open("29-satinty_4s_full.out", 'r') as fullSat:
        fullSat.readline()
        fullSat.readline()
        fullSat.readline()
        
        for line in fullSat.readlines():
            if line.split()[1][2:] == 'K1' or line.split()[1][2:] == 'L1' or line.split()[1][2:] == 'M1':
                if int(line.split()[2]) == 0 or int(line.split()[2]) == 2:
                    monopolarSat.write(line)