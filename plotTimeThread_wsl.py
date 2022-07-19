import subprocess
import matplotlib.pyplot as plt

x = []
y = []

ly = []
diffy = []

for j in range(1, 11):
	command = "time parallel -j" + str(j) + " test_func ::: " + ' '.join(["5000"] * 1000)
	
	e = subprocess.run(command, shell=True, executable='/bin/bash', capture_output=True).stderr.decode('utf-8')
	
	tmp = e.split()[1]
	
	x.append(j)
	y.append(int(tmp.split('m')[0]) * 60 + float(tmp.split('m')[1].split('s')[0]))
	ly.append(y[0] / j)
	
	diffy.append(y[-1] - ly[-1])

print("Done!")
input()

print(x)
print(y)
print(ly)
print(diffy)

plt.plot(x, y, label="Measured")
plt.plot(x, ly, label="Linear")
plt.xlabel("Job Number")
plt.ylabel("Total Real Time (s)")

plt.legend()

plt.show()

plt.plot(x, diffy, label="Scheduling Time")
plt.xlabel("Job Number")
plt.ylabel("Time Difference (s)")

plt.legend()

plt.show()
