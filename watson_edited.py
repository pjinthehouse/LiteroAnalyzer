import json
from ibm_watson import ToneAnalyzerV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import matplotlib.pyplot as plt
import numpy as np
import os
from scipy.interpolate import make_interp_spline
from characterExtraction_new import *

import plotly.graph_objects as go
import plotly.offline as pyo
from main4 import *

import string
import yake
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem.porter import PorterStemmer


def authenticate():
	authenticator = IAMAuthenticator('01AdkMDUVfcymV8Jddv5_kGwTra9xkb3g8G3MdcNns_Y')
	tone_analyzer = ToneAnalyzerV3(
	    version='2016-05-19',
	    authenticator=authenticator
	)

	tone_analyzer.set_service_url('https://api.eu-gb.tone-analyzer.watson.cloud.ibm.com/instances/1650d3fb-2d04-4950-9efa-1b45ec529820')
	return tone_analyzer

def character_personality_plot(character, tone_analyzer, image_name, loc, mc, d, main_text, trait_list):

	'''
	f = open(loc+"/sentenceAnalysis.json",)
	temp = json.load(f)
	sentences = temp[character][0]
	#print("SENTENCES :    ", sentences)
	text =''
		#sentences = sentences[:10]
	for sentence in sentences:
		sentence = sentence.replace("\n",'') + " "
		text+=sentence

	tone_analysis = tone_analyzer.tone(
				{'text': text},
				content_type='application/json',
				tones = ['emotion', 'social', 'language']
			).get_result()
		
	doc_tones= tone_analysis["document_tone"]["tone_categories"]

	if image_name == 'switch':
		return doc_tones
	'''

	lit = Literature(main_text, loc)

	social_arr={"Openness":[],"Conscientiousness":[],"Extraversion":[],"Agreeableness":[],"Emotional Range":[]}
	emotion_arr={"Anger":[], "Disgust":[], "Fear":[], "Joy":[], "Sadness":[] }
	language_arr={"Analytical":[], "Confident":[], "Tentative":[]}
	x=[]

	for chapter_num in lit.chapterNums:
		chapter_text = readText(loc+"/split_chapters/"+chapter_num+".txt")
		sentenceList = splitIntoSentences(chapter_text)
		print("##########################",sentenceList)
		sentenceListnew=[]
		for sentence in sentenceList:
			sentence = sentence.replace("\n",'')
			sentenceListnew.append(sentence)
		characterSentences = compare_lists_new(sentenceListnew, mc, d)
		sentences = characterSentences[character]
		print("Chapter_num ______ SENTENCES :    ",chapter_num, len(sentences))
		if len(sentences)==0:
			continue
		'''
		text =''
		for sentence in sentences:
			sentence = sentence.replace("\n",'') + " "
			text+=sentence
		'''

		social_arr_temp={"Openness":[],"Conscientiousness":[],"Extraversion":[],"Agreeableness":[],"Emotional Range":[]}
		emotion_arr_temp={"Anger":[], "Disgust":[], "Fear":[], "Joy":[], "Sadness":[] }
		language_arr_temp={"Analytical":[], "Confident":[], "Tentative":[]}



		text =''
		nos=0

		for sentence in sentences:
			sentence = sentence.replace("\n",'') + " "
			nos+=1
			text+=sentence

			if len(text)>50000:
				tone_analysis = tone_analyzer.tone(
							{'text': text},
							content_type='application/json',
							tones = ['emotion', 'social', 'language']
						).get_result()
				
				doc_tones = tone_analysis["document_tone"]["tone_categories"]
				x.append(chapter_num)

				for i in doc_tones[0]["tones"]:
					emotion_arr_temp[i["tone_name"]].append((i["score"],nos))
				for i in doc_tones[2]["tones"]:
					social_arr_temp[i["tone_name"]].append((i["score"],nos))
				for i in doc_tones[1]["tones"]:
					language_arr_temp[i["tone_name"]].append((i["score"],nos))

				text=''
				nos=0

			print(nos, len(text))

		if nos!=0:
			tone_analysis = tone_analyzer.tone(
								{'text': text},
								content_type='application/json',
								tones = ['emotion', 'social', 'language']
							).get_result()

			doc_tones = tone_analysis["document_tone"]["tone_categories"]
			x.append(chapter_num)
			print("doc_tones: ",doc_tones[0])
			for i in doc_tones[0]["tones"]:
				emotion_arr_temp[i["tone_name"]].append((i["score"],nos))
			for i in doc_tones[2]["tones"]:
				social_arr_temp[i["tone_name"]].append((i["score"],nos))
			for i in doc_tones[1]["tones"]:
				language_arr_temp[i["tone_name"]].append((i["score"],nos))


		for i in social_arr_temp:
			temp_temp=0
			k=0
			for j in social_arr_temp[i]:
				print(j)
				temp_temp += j[0] * j[1]
				k+=j[1]
			social_arr[i].append(temp_temp/k)

		for i in emotion_arr_temp:
			temp_temp=0
			k=0
			for j in emotion_arr_temp[i]:
				temp_temp += j[0] * j[1]
				k+=j[1]
			emotion_arr[i].append(temp_temp/k)

		for i in language_arr_temp:
			temp_temp=0
			k=0
			for j in language_arr_temp[i]:
				temp_temp += j[0] * j[1]
				k+=j[1]
			language_arr[i].append(temp_temp/k)

	x = list(set(x))
	x.sort()
	arr=[]
	for i in emotion_arr:
		arr.append(sum(emotion_arr[i])/len(emotion_arr[i]))
	arr=[*arr,arr[0]]

	legend = ['Anger','Disgust','Fear','Joy','Sadness']
	legend = [*legend, legend[0]]
	
	fig = go.Figure(data=[go.Scatterpolar(r=arr, theta=legend, name='Emotion')],layout=go.Layout(title=go.layout.Title(text=str(character)+" emotions"),polar={'radialaxis': {'visible': True}},showlegend=True))

	#pyo.plot(fig)
	fig.write_image("static/"+image_name+"_radar_emotion.png")

	###############################################################################
	arr=[]
	for i in social_arr:
		arr.append(sum(social_arr[i])/len(social_arr[i]))
	arr=[*arr,arr[0]]

	legend = ["Openness","Conscientiousness","Extraversion","Agreeableness","Emotional Range"]
	legend = [*legend, legend[0]]
	
	fig = go.Figure(data=[go.Scatterpolar(r=arr, theta=legend, name='Social')],layout=go.Layout(title=go.layout.Title(text=str(character)+" social traits"),polar={'radialaxis': {'visible': True}},showlegend=True))

	#pyo.plot(fig)
	fig.write_image("static/"+image_name+"_radar_social.png")

	###############################################################################
	arr=[]
	for i in language_arr:
		arr.append(sum(language_arr[i])/len(language_arr[i]))
	arr=[*arr,arr[0]]

	legend = ["Analytical", "Confident", "Tentative"]
	legend = [*legend, legend[0]]
	
	fig = go.Figure(data=[go.Scatterpolar(r=arr, theta=legend, name='Language')],layout=go.Layout(title=go.layout.Title(text=str(character)+" language traits"),polar={'radialaxis': {'visible': True}},showlegend=True))

	#pyo.plot(fig)
	fig.write_image("static/"+image_name+"_radar_language.png")

	###############################################################################
	print(emotion_arr,social_arr,language_arr)
	######################################################################################################################
	#print(emotion_arr)
	'''
	emotion_arr_2={"Anger":[], "Disgust":[], "Fear":[], "Joy":[], "Sadness":[] }
	social_arr_2={"Openness":[],"Conscientiousness":[],"Extraversion":[],"Agreeableness":[],"Emotional Range":[]}
	language_arr_2={"Analytical":[], "Confident":[], "Tentative":[]}
	# print(len(emotion_arr["Anger"]))

	
	for i in emotion_arr:
		j=0
		#k =int(len(emotion_arr[i])/10)
		k =int(len(emotion_arr[i])/z)
		while j<len(emotion_arr[i]):
			#print(j,k)
			avg_temp = sum(emotion_arr[i][j:j+k])/k
			emotion_arr_2[i].append(avg_temp)
			j+=k

	#print(emotion_arr_2)
	for key in emotion_arr_2:
		emotion_arr_2[key].pop()
	'''
	#x=list([i+1 for i in range(len(emotion_arr["Anger"]))])

	try:
		plt.clf()
	except:
		pass
	if len(emotion_arr)==1:
		plt.scatter(x,emotion_arr[0][1])
	else:
		emotion_legend=[]
		for i,key in enumerate(emotion_arr):
			if key in trait_list:
				#X_Y_Spline = make_interp_spline(x, np.array(emotion_arr[key]))
				#X_ = np.linspace(x.min(), x.max(), 500)
				#Y_ = X_Y_Spline(X_)
				plt.scatter(x,emotion_arr[key])
				plt.plot(x,emotion_arr[key])
				emotion_legend.append(key)

	plt.legend(emotion_legend)
	plt.title(str(character))
	#plt.show()
	#f= plt.figure()
	#f.set_figwidth(100)
	#f.set_figheight(10)
	'''static = os.path.join(loc, 'static/')
	os.mkdir(static)
	print("loc = ",loc)
	plt.savefig(static+image_name)'''
	plt.savefig('static/'+image_name+'_emotion.png')


	

	#---------------------------------emotion----------------------------------------------------------

	#x=np.array([i+1 for i in range(len(social_arr["Openness"]))])
	plt.clf()
	if len(social_arr)==1:
		plt.scatter(x,social_arr[0][1])
	else:
		social_legend=[]
		for i,key in enumerate(social_arr):
			if key in trait_list:
				#X_Y_Spline = make_interp_spline(x, np.array(social_arr[key]))
				#X_ = np.linspace(x.min(), x.max(), 500)
				#Y_ = X_Y_Spline(X_)
				plt.scatter(x,social_arr[key])
				plt.plot(x,social_arr[key])
				social_legend.append(key)


	plt.legend(social_legend)
	plt.title(str(character))
	#plt.show()
	'''static = os.path.join(loc, 'static/')
	os.mkdir(static)
	print("loc = ",loc)
	plt.savefig(static+image_name)'''
	#plt.show()
	plt.savefig('static/'+image_name+'_social.png')



	###-----------------------------------------language---------------------------------------------------------

	#x=np.array([i+1 for i in range(len(language_arr["Analytical"]))])

	 
	# Returns evenly spaced numbers
	# over a specified interval.
	
	plt.clf()
	if len(language_arr)==1:
		plt.scatter(x,language_arr[0][1])
	else:
		lang_legend=[]
		for i,key in enumerate(language_arr):
			if key in trait_list:
				#X_Y_Spline = make_interp_spline(x, np.array(language_arr[key]))
				#X_ = np.linspace(x.min(), x.max(), 500)
				#Y_ = X_Y_Spline(X_)
				plt.scatter(x,language_arr[key])
				plt.plot(x,language_arr[key])
				lang_legend.append(key)


	plt.legend(lang_legend)
	plt.title(str(character))
	#plt.show()
	'''static = os.path.join(loc, 'static/')
	os.mkdir(static)
	print("loc = ",loc)
	plt.savefig(static+image_name)'''
	plt.savefig('static/'+image_name+'_language.png')


	x={}
	y={}
	z={}
	if image_name=="switch":
		for i in emotion_arr:
			x[i]= sum(emotion_arr[i])/len(emotion_arr[i])
		for i in social_arr:
			y[i]= sum(social_arr[i])/len(social_arr[i])
		for i in language_arr:
			z[i]= sum(language_arr[i])/len(language_arr[i])

	return x,y,z


def keyword_extraction(text):

  text_p = "".join([char for char in text if char not in string.punctuation])

  words = word_tokenize(text_p)
  stop_words = stopwords.words('english')
  filtered_words = [word for word in words if word not in stop_words]

  text3 = ''
  for i in filtered_words:
    text3 = text3 + " " + i.strip()

  kw_extractor = yake.KeywordExtractor()
  keywords = kw_extractor.extract_keywords(text3)

  # The below parameters are the default values
  language = "en"
  max_ngram_size = 1
  deduplication_thresold = 0.7
  deduplication_algo = 'seqm'
  windowSize = 3
  numOfKeywords = 100000000000

  custom_kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_thresold, dedupFunc=deduplication_algo, windowsSize=windowSize, top=numOfKeywords, features=None)
  keywords = custom_kw_extractor.extract_keywords(text3)

  return keywords


def func(temp1, stop_words):
  tagged=[]
  for i in temp1:
      
    # Word tokenizers is used to find the words 
    # and punctuation in a string
      wordsList = nltk.word_tokenize(i[0])
    
      # removing stop words from wordList
      wordsList = [w for w in wordsList if not w in stop_words] 
    
      #  Using a Tagger. Which is part-of-speech 
      # tagger or POS-tagger. 
      t = nltk.pos_tag(wordsList)
      tagged.append(t)
  return tagged



def adjectives(character, main_text, loc, mc, d):
	lit = Literature(main_text, loc)
	for chapter_num in lit.chapterNums:
		chapter_text = readText(loc+"/split_chapters/"+chapter_num+".txt")
		sentenceList = splitIntoSentences(chapter_text)
		characterSentences = compare_lists_new(sentenceList, mc, d)
		sentences = characterSentences[character]
		print("Chapter_num ______ SENTENCES :    ",chapter_num, len(sentences))
		if len(sentences)==0:
			continue
		text =''
		for sentence in sentences:
			sentence = sentence.replace("\n",'') + " "
			text+=sentence

	#sentences = nltk.sent_tokenize(text)
	#tokenizedSentences = [nltk.word_tokenize(sentence) for sentence in sentences]
	#taggedSentences = [nltk.pos_tag(sentence) for sentence in tokenizedSentences]
	#taggedSentences


	stop_words = set(stopwords.words('english'))

	keywords = keyword_extraction(text)
	p=[(i[0],1) for i in keywords]
	pp=[]
	for i in func(p, stop_words):
		if i[0][1]=='JJ':
			pp.append(i[0][0])

	tempp=[]
	for i in keywords:
		if i[0] in pp:
			tempp.append(i)
	t2=[]
	for i in func(tempp, stop_words):
		if i[0][1]=='JJ':
			t2.append((i[0][0], 1))
	
	return sorted(t2, key=lambda t: t[1], reverse=False)[:5]
