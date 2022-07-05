import subprocess
import time

x = []
y = []

#execute for each number of jobs
for j in range(1, 11):
    #command = "time parallel -j" + str(j) + " test_func ::: " + ' '.join([str(v) for v in list(range(1000, 101001, 500))])
    command = "time parallel -j" + str(j) + " test_func ::: " + ' '.join(["5000"] * 1000)
    
    o, e = subprocess.Popen(['bash', '-c', command], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    x.append(j)
    
    tmp = e.decode('ascii').split()[1]
    
    y.append(int(tmp.split('m')[0]) * 60 + float(tmp.split('m')[1].split('s')[0]))
    
    time.sleep(1)

print(x)
print(y)