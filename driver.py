import os
import pandas as pd
import matplotlib.pyplot as plt
import csv
import shutil as util
import time
import random

Analyze_folder = "Analysis"
final_file = 'final.csv'
analyze_file = 'temp.csv'
Output_folder = "output_vr_rev"
TotalTests = 10

def run():
	# Here we do multiple runs with varying values of r, d, w, tp and tl and report the observations in the form
	# of both csv and plots.
	algorithm = "vr_revisited_new.da"
	output_file = Output_folder + "/" + "validation.csv"
	output_heading = ['Num Clients', 'Max failures', 'Num of Req/Client' ,'C_Timeout','R_Timeout','Liveness', 'Correctness', 'Avg Latency', 'Exec Time', 'WallClock Time(ms)']
	dataframe = pd.DataFrame(columns = output_heading)
	df_list = []

	# with open(output_file, mode='w+') as file:
	# 	writer = csv.writer(file)
	# 	writer.writerow(output_heading)
	f = 2
	c = 3
	req = 5
	c_tout = 10
	r_tout = 5
	c = random.sample(range(1, 50),TotalTests)


	for testNum in range(1,TotalTests+1):

		# c = random.randint(1,10)
		# req = random.randint(1,10)
		# c_tout = random.randint(10,20)
		# r_tout = random.randint(5,c_tout)


		headings = ['Correctness', 'Avg Latency', 'Exec Time', 'WallClock Time(ms)']
		with open(analyze_file, mode='a') as file:
			writer = csv.writer(file)
			writer.writerow(headings)

		cmd = str('python -m da' + " " + algorithm + " " + str(f) + " " + str(c[testNum-1]) + " " + str(req) + " "  + str(c_tout) + " " + str(r_tout))
		os.system(cmd)
		print("Done Analyzing")
		df = pd.read_csv(analyze_file, nrows=None)


		isCorrect = "True" if df['Correctness'].astype(int).sum() > 0 else 0
		isLive = "True"
		avg_latency = df['Avg Latency'].sum()
		exec_time = df['Exec Time'].sum()
		wallclock = df['WallClock Time(ms)'].sum()
		output_row = [c[testNum-1], f, req, c_tout, r_tout, isLive, isCorrect, avg_latency, exec_time, wallclock]
		df_list.append(output_row)

		# with open(output_file, mode='a') as file:
		# 	writer = csv.writer(file)
		# 	writer.writerow(output_row)

		del df
		os.remove(analyze_file)

	dataframe = pd.DataFrame(df_list, columns= output_heading)
	dataframe = dataframe.sort_values('Num Clients')
	dataframe.to_csv(output_file)
	print(dataframe.head(TotalTests))


	x = dataframe['Num Clients']
	y = dataframe['Exec Time']

	y1 = dataframe['Avg Latency']
		
	plt.plot(x,y, linewidth=2.0, label="Exec. Time")
	plt.plot(x, y1, linewidth= 1.0, label="Avg Latency")

	plt.xlabel('Num Clients')
	plt.ylabel('time')
	plt.title('Performance Analysis with Num Clients')
	plt.legend(loc='upper left')
	plt.show()

if __name__ == "__main__":
	if os.path.exists(Analyze_folder):
		util.rmtree(Analyze_folder)
	if os.path.exists(Output_folder):
		util.rmtree(Output_folder)
	if os.path.exists(analyze_file):
		os.remove(analyze_file)

	os.mkdir(Analyze_folder)
	os.mkdir(Output_folder)
	run()
