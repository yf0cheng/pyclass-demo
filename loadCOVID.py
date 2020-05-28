# -*- coding: utf-8 -*-
"""

Title: Dataset loader and conditioner for COVID dataset
    
Created on Mon Mar 16 17:44:29 2020

@author: Ujjawal.K.Panchal & Manny Ko

"""
import os, gzip, time, pickle
from collections import defaultdict
import PIL
from PIL import Image
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

#import our packages
from pyutils import dirutils, folderiter


class COVIDDataset():
	""" our CustomDataset for COVID """
	kPathologies = ['ARDS', 'Bacterial Pneumonia', 'COVID-19', 'Chlamydophila', 'Fungal Pneumonia', 'Klebsiella', 'Legionella', 'MERS', 'No Finding', 'Pneumocystis', 'Pneumonia', 'SARS', 'Streptococcus', 'Viral Pneumonia']

	def __init__(
		self, 
		root, kDataType='CSV'	#meta data contained in a .csv
	):
		self.root = root
		self.size = 0
		self.pixels = []
		self.labels = []
		self.load()

	def __getitem__(self, index):
		""" Return a data pair (e.g. image and filename) """
		return self.pixels[index], self.filenames[index]

	def __len__(self):
		# You should change 0 to the total size of your dataset.
		return self.size		

	def load(self):
		filelist = []		#this will be used to store files that pass the filters

		folderiter.folder_iter(
			root,
			functor,
			context = filelist,
			folder_filter = ourfolder_filter,	#filter out all folders that do not have 'input' in it
			file_filter   = file_filter,		#filter out all files except .png
			logging=False
		)
		self.finalize(filelist, kLoad=True)

	def finalize(self, filelist, kLoad=False):
		self.size = len(filelist)
		self.filelist = sorted(filelist)

		#2: load CSV for metadata (and labels)
		csvfilepath = self.root + 'metadata.csv'
		self.metadata, self.ids, self.filenames, self.pathologies = load_clean_META(self, csvfilepath)

		#1: load all the images
		missing = 0
		images = []
		filenames = []
		i = 0
		root = self.root + 'images/'
		for file in self.filenames:
			try:
				im = Image.open(root + file)
			except:
				missing += 1 	#ignore those we removed (for demo)
			else:	
				images.append(im)
				filenames.append(self.filenames[i])
		i += 1
					
		print(f"len(images) {len(images)}")			
		self.pixels = images
		self.filenames = filenames
		self.size = len(images)

def load_clean_META(dataset, csvfilepath, kLogging=False):
	""" 
	old dataset is 150 observations - 104 cov and 46 non cov
	"""
	df = pd.read_csv(csvfilepath)
	selPA = df.loc[df['view'] == 'PA']
	
	filenames = selPA['filename']
	ids = selPA['patientid']

	pathologies = defaultdict(int)
	covid = 0
	total = 0
	for index, row in selPA.iterrows():
		id = row['patientid']
		finding = row['finding']
		view = row['view']
		filename = row['filename']

		pathologies[finding] += 1

		if "COVID-19" in finding:
			covid += 1
		total += 1
	if kLogging:
		print(f"PA {total}, covid {covid}")
		print(f"{pathologies}")

	return df, ids, filenames, pathologies

def onehot(pathologies):
	pass

def ourfolder_filter(subdir):
	""" folder filter for the images """
	ourfolders = {
		'images',
	}
	subd = os.path.basename(subdir)

	if folderiter.deffolder_filter(subdir) and subd in ourfolders:
		return True		#this is one of our folders
	return False

def file_filter(file):
	""" extension filter for the images """
	ourextensions = {
		'.png',
		'.jpg',
		'.jpeg',
	}
	ext = os.path.splitext(file)[-1].lower()
	#print(ext)
	result = folderiter.deffile_filter(file) and (ext in ourextensions)

	return result

def csv_filter(file):
	result = folderiter.deffile_filter(file) and (ext in ourextensions)

def functor(filepath, context):
	filelist = context
	#print(f"  functor({filepath})")
	filelist.append(filepath)

if __name__ == '__main__':
	root = 'covid-chestxray-dataset/'
	filelist = []		#this will be used to store files that pass the filters

	#1: use our COVIDDataset to load
	coviddata = COVIDDataset(root, kDataType='CSV')
	
	print(f"coviddata {len(coviddata)}")
	#print(set(coviddata.filenames))
	print(coviddata.pathologies, len(coviddata))


	#plot it using seaborn
	# https://seaborn.pydata.org/tutorial/axis_grids.html
	#sns.set(style="ticks")

	#g = sns.PairGrid(coviddata.metadata)
	#g.map(plt.scatter)
	#plt.show()
	
	#fig = plt.figure()
	#fig.suptitle('COVID-19 IEEE dataset (subset of 10)', fontsize=16)
	plt.style.use('seaborn-whitegrid')

	#plt.subplots: https://matplotlib.org/3.2.1/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure.suptitle

	#fig, axarr = plt.subplots(2, 5)
	# Label the axes
	#axarr.set(title='COVID-19 IEEE dataset (subset of 10)',
		#ylabel='y label', xlabel='xaxis label')

	# https://matplotlib.org/3.2.1/tutorials/introductory/images.html
		
	fig_size = plt.rcParams.get('figure.figsize')

	fig_size[0] = 10	#10" wide
	fig_size[1] = 6		#6" tall
	plt.rcParams["figure.figsize"] = fig_size

	#2: 5x2
	per_row = 5
	layout = (2, per_row)		#2 rows, 5 cols
	f, axarr = plt.subplots(*layout)
	f.suptitle('COVID-19 IEEE dataset (subset of 10)', fontsize=16)
	print(f"axarr.shape {axarr.shape}")

	#2.1: populate the subplots 
	for i in range(0, len(coviddata)):
		row, col = divmod(i, per_row)
		img, filename = coviddata[i]
		#print(filename)
		#axarr[0, i].set_title(filename)
		axarr[row, col].imshow(img, cmap='gray')
	plt.show()
