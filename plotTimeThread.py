import matplotlib.pyplot as plt
import subprocess
import time

x = []
y = []

ly = []

#execute for each number of jobs
for j in range(1, 11):
    #command = "time parallel -j" + str(j) + " test_func ::: " + ' '.join([str(v) for v in list(range(1000, 101001, 500))])
    command = "time parallel -j" + str(j) + " test_func ::: " + ' '.join(["5000"] * 1000)
    
    o, e = subprocess.Popen(['bash', '-c', command], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    x.append(j)
    
    tmp = e.decode('ascii').split()[1]
    
    y.append(int(tmp.split('m')[0]) * 60 + float(tmp.split('m')[1].split('s')[0]))
    ly.append(y[0] / j)
    
    time.sleep(1)

print(x)
print(y)

plt.plot(x, y, label = "Measured")
plt.plot(x, ly, label= "Linear")
plt.xlabel("Job Number")
plt.ylabel("Total Real Time (s)")

plt.legend()

plt.show()