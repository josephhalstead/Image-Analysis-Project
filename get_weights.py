from __future__ import division
import pandas
import matplotlib.pyplot as plt
import numpy as np
import peakutils
from scipy import stats
import math
import os
import csv
from datetime import datetime

##########################################################################################################################################
# This python script is part of a image analysis pipeline for analysing agarose gel images.                                              #
#                                                                                                                                        #
# The script takes a series of text files containing XY data from gel lanes. These text files are created by an imagej macro.            #
#																																		 #
# The script calculates a standard curve based on the DNA ladder and then uses this to calculate the molecular weight of the bands seen  #
# in other lanes. Requires the installation of peakutils.                                                                                #
#                                                                                                                                        #
# Inputs required = 1)path to folder containing imagej created textfiles, 2) DNA ladder information                                      #
#                                                                                                                                        #
# Outputs = CSV file containing peaks data.                                                                                              #
#                                                                                                                                        #
##########################################################################################################################################


def get_peaks(file, thres_num, minimum, max_STD):

	#This function finds the peaks in data given to it.
    #Only used on sample lanes not ladder lane.
    #Variables thres_num and minimum cam be adjusted if neccecary.

	x= pandas.read_csv(file, delim_whitespace=True)

	x = x.ix[1:] #First row in bad so remove

	np_array = np.array(x["Y"])

	plt.plot(np_array)
	plt.show()

	base = peakutils.baseline(np_array,2) #remove baseline to get better peak calling

	indexes = peakutils.indexes(np_array,thres=thres_num, min_dist=minimum) # find peaks


	#print indexes

	rf = indexes/max_STD

	return rf

def generate_standard_curve(file, ladder):

	#Finds peaks in ladder lane and calculates STD curve.
	#This can then be used to calculate the molecular weight of samples


	x= pandas.read_csv(file, delim_whitespace=True)
	x = x.ix[1:]
	np_array = np.array(x["Y"])
	base = peakutils.baseline(np_array,2)
	indexes = peakutils.indexes(np_array,thres=0.1, min_dist=25) #Adjust these if peak calling fails for ladder lane!


	#plt.plot(np_array)
	#plt.show()

	print indexes

	if len(indexes) == len(ladder): #If we have found the wrong number of peaks

		max_STD =  len(np_array)
		rf = indexes/len(np_array)
		ladder = np.array(ladder)
		ladder = np.log(ladder) #gets logs for log(molecular weights) vs distance linear regression.
		
		slope, intercept, r_value, pvalue, std_err = stats.linregress(rf,ladder) #Do some linear regression to get line statistics

		return [slope, intercept, r_value, max_STD]

	else:

		return "Error"

def get_mol_weights(file, thres_num, minimum, STD_curve, max_STD):
	
	#For data from a particular lane get the molecular weights using the standard surve created by generate_standard_curve()

	peaks = get_peaks(file, thres_num, minimum, max_STD)

	mol_weights =[]

	slope = STD_curve[0]
	intercept = STD_curve[1]

	for peak in peaks:

		mol_weights.append(np.exp((slope*peak)+intercept))

	return mol_weights


def get_all_mol_weights(folder, thres_num, minimum, STD_file, STD_details):

	#Apply get_mol_weights to all files in a folder.

	mol_weights =[]

	files_in_folder = []
	
	for fn in os.listdir(folder):
		files_in_folder.append(fn)

	curve_path = folder+STD_file

	curve = generate_standard_curve(curve_path, STD_details) #make STD curve from file

	max_STD = curve[3]

	if curve == "Error":

		return "Error in creating standard curve (Wrong number of peaks). Try adjusting peak calling parameters"

	else:

		for file in files_in_folder:

			if file <> STD_file: #ignore this file

				file_path = folder+file

				mol_weights.append([file]+get_mol_weights(file_path, thres_num,minimum, curve, max_STD))
		return mol_weights

def create_CSV(mol_weights, file_name):

	#outputs data to CSV file for further use.

	with open(file_name, "wb") as csvfile:
		spamwriter = csv.writer(csvfile, delimiter= " ", quotechar = "|")

		for row in mol_weights:

			spamwriter.writerow(row)


#what settings to use for samples 0.2, 25/20 best so far.
molecular_weights = get_all_mol_weights("/home/cuser/Documents/Image Analysis/Validation/Data/united2/", 0.1, 3, "2016-2-16-Lane-1.txt",[8576, 7427, 6101, 4899, 3639, 2799])

file_name = "Results-"+str(datetime.now())[:10] + ".csv"

create_CSV(molecular_weights,file_name )

#generate_standard_curve("/home/cuser/Documents/Image Analysis/File Dump/2016-2-3-Lane-1.txt",[8576, 7427, 6101, 4899, 3639, 2799] )


#get_peaks("/home/cuser/Documents/Image Analysis/File Dump/2016-2-3-Lane-2.txt", 0.2, 20,619) 
#[8576, 7427, 6101, 4899, 3639, 2799]