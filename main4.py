import argparse
import os
import pickle
import re
from tqdm import tqdm
from nameparser import HumanName
from itertools import product

import matplotlib.pyplot as plt
import networkx as nx



class Literature():

	def __init__(self,text, loc):
		self.loc = loc
		self.filename='ip.txt'
		self.text=text
		self.lines=self.text.split('\n')
		self.headings=self.getHeadings()

		self.chapters=self.getChapterContent()
		self.chapterNums = 1

		# print(len(self.chapters))

		self.splitChapters()

	def splitChapters(self):

		numbers = range(1,len(self.chapters)+1)
		maxNum = max(numbers)
		maxDigits = len(str(maxNum))
		self.chapterNums = [str(number).zfill(maxDigits) for number in numbers]
		
		print("chapterNums: ", self.chapterNums)

		basename=os.path.basename(self.filename)
		noExt = os.path.splitext(basename)[0]

		outDir = self.loc + "/split_chapters"

		# print(basename,noExt,outDir)

		if os.path.exists(outDir):
			for i in os.listdir(outDir):
				try:
					os.remove(outDir+'/'+i)
				except:
					for j in os.listdir(outDir+'/'+i):
						os.remove(outDir+'/'+i+'/'+j)
						
					os.rmdir(outDir+'/'+i)
			os.rmdir(outDir)
		os.mkdir(outDir)

		for num,chapter in zip(self.chapterNums,self.chapters):
			path = outDir + '/' + num + '.txt'

			# print("chapter before: ",chapter)
			chapter = '\n'.join(chapter)
			# print("chapter after: ",chapter)

			with open(path,'w') as f:
				f.write(chapter)


	def getChapterContent(self):
		chapters=[]

		lastHeading = len(self.headings) -1
		for i,headingLocation in enumerate(self.headings):
			if i != lastHeading:
				nextHeading = self.headings[i+1]
				chapters.append(self.lines[headingLocation+1:nextHeading])
		return chapters

	def getHeadings(self):

		# Considering forms of headings

		#Form : Chapter I, Chapter 1, Chapter the First, Chapter.1

		arabicNumerals = '\d+'

		romanNumerals = '(?=[MDCLXVI])M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})'

		numberWordsByTens = ['twenty', 'thirty', 'forty', 'fifty', 'sixty',
                              'seventy', 'eighty', 'ninety']

		numberWords = ['one', 'two', 'three', 'four', 'five', 'six',
                       'seven', 'eight', 'nine', 'ten', 'eleven',
                       'twelve', 'thirteen', 'fourteen', 'fifteen',
                       'sixteen', 'seventeen', 'eighteen', 'nineteen'] + numberWordsByTens

		numberWordsPat = '(' + '|'.join(numberWords) + ')'

		ordinalNumberWordsByTens = ['twentieth', 'thirtieth', 'fortieth', 'fiftieth', 
                                    'sixtieth', 'seventieth', 'eightieth', 'ninetieth'] + numberWordsByTens

		ordinalNumberWords = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 
                              'seventh', 'eighth', 'ninth', 'twelfth', 'last'] + \
                             [numberWord + 'th' for numberWord in numberWords] + ordinalNumberWordsByTens

		ordinalsPat = '(the )?(' + '|'.join(ordinalNumberWords) + ')'

		enumeratorsList = [arabicNumerals, romanNumerals, numberWordsPat, ordinalsPat] 

		enumerators = '(' + '|'.join(enumeratorsList) + ')'

		form = 'chapter ' + enumerators

		#Form 2 : II. THE ASTROLOGER

		enumerators2 = romanNumerals
		seperators = '(\. | )'
		title_format = '[A-Z][A-Z]'
		form2 = enumerators2 + seperators + title_format

		pattern = re.compile(form,re.IGNORECASE)
		pattern2 = re.compile(form2)

		headings = []

		for i,line in enumerate(self.lines):
			if pattern.match(line) is not None:
				headings.append(i)

			elif pattern2.match(line) is not None:
				headings.append(i)
		
		headings.append(len(self.lines)-1)

		# print(headings)
		return headings
