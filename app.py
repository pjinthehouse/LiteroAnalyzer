from flask import * 
from characterExtraction_new import *
from watson_edited import *
from main4 import *
import os, time, sqlite3, hashlib
app = Flask(__name__)  
import PyPDF2
from graph_final import *
import time


loc = ''
fpath = ''
dir_name=''
uname = ''
tone_analyzer=''
characters=''

text=''
mc=''
d=''
tl=''

lit = ''
names = ''

class A:
	def is_valid(self, uname, password):
		con = sqlite3.connect('database2.db')
		cur = con.cursor()
		cur.execute('SELECT userId, password FROM users')
		data = cur.fetchall()
		con.close()
		print(data)
		for row in data:
			if row[0] == uname and row[1] == password:
				return True
		return False

@app.route('/')
def home():
	return render_template("home.html", title="LiteroAnalyzer - Home")
	
@app.route('/home')
def home1():
	return render_template("home1.html", title="LiteroAnalyzer - Home")
	
@app.route('/signup', methods = ['GET', 'POST'])
def signup():
	return render_template("signup.html", title="LiteroAnalyzer - SignUp")
	
@app.route('/signing_up', methods = ['POST'])
def add_user():
	global uname
	uname = request.form.get('Uname')
	pwd = request.form.get('Password')
	name = request.form.get('name')
	email = request.form.get('email')
	c_pwd = request.form.get('c_Password')
	if c_pwd!=pwd:
		return render_template('signup.html', title="LiteroAnalyzer - SignUp")
	else:
		con = sqlite3.connect('database2.db')
		cur = con.cursor()
		user = (uname, pwd, email, name)
		sql = '''INSERT INTO users(userId, password, email, fullName) values(?,?,?,?)'''
		cur.execute(sql, user) 
		con.commit()
		con.close()
		return redirect(url_for('upload'))                                          

@app.route('/login', methods = ['GET', 'POST'])
def login():
	return render_template("login.html", title="LiteroAnalyzer - Login")

@app.route('/upload', methods = ['POST', 'GET'])  
def upload():  
	if request.method == 'POST':
		global uname
		uname = request.form.get('Uname')
		password = request.form.get('Pass')
		a = A()
		valid = a.is_valid(uname, password)
		if valid:
			
			return render_template("file_upload_form.html", title="LiteroAnalyzer - UploadText")  
		else:
			return render_template("login.html", title="LiteroAnalyzer - Login")
	else:
		return render_template("file_upload_form.html", title="LiteroAnalyzer - UploadText")
		
@app.route('/check_characters', methods = ['POST'])
def check_characters():
	if request.method == 'POST':
		start = time.time()  
		f = request.files['file']
		path = "user_sessions/"
		global loc
		global uname
		loc1 = "static/"
		if os.path.exists(loc1):
		    for i in os.listdir(loc1):
		    	if i.startswith(uname):
		    		try:
		    			os.remove(loc1+'/'+i)
		    		except Exception:
		    			for j in os.listdir(loc1+'/'+i):
		    				os.remove(loc1+'/'+i+'/'+j)
		    			os.rmdir(loc1+'/'+i)
		loc=os.path.join(path, uname)
		if os.path.exists(loc):
			for i in os.listdir(loc):
				try:
					os.remove(loc+'/'+i)
				except Exception:
					for j in os.listdir(loc+'/'+i):
						try:
							os.remove(loc+'/'+i+'/'+j)
						except Exception:
							os.remove(loc+i+'/'+j)
					os.rmdir(loc+'/'+i)
			os.rmdir(loc)
		os.mkdir(loc)
		global fpath
		f_name=f.filename
		if f_name.endswith(".txt"):
			fpath=os.path.join(loc,"ip.txt")
			f.save(fpath)
			
		if f_name.endswith(".pdf"):
			fpath_pdf=os.path.join(loc,"ip.pdf")
			f.save(fpath_pdf)
			pdffileobj=open(fpath_pdf,'rb')
			pdfreader=PyPDF2.PdfFileReader(pdffileobj)
			x=pdfreader.numPages
			# pdffileobj.close()
			fpath=os.path.join(loc,"ip.txt")
			file1=open(fpath,"a")
			for page_count in range(x):
				page = pdfreader.getPage(page_count)
				page_data = page.extractText()
				file1.write(page_data)	
			file1.close()
			pdffileobj.close()
	global text
	global d
	global mc
	global tl
	text = readText(fpath)
	entityNames = getCharacters(text)
	d, mc, tl = mergeNames_count(entityNames)

	global tone_analyzer
	tone_analyzer = authenticate()
	end = time.time()
	print("Time taken to upload a text: ",end - start,"seconds")
	mc.sort()
	return render_template("check_characters.html", names=mc, title="LiteroAnalyzer - CheckCharacters")

@app.route('/select', methods = ['POST'])
def select():
	global names
	names = request.form.getlist('yes')
	extra_characters = request.form.get("extra_characters").split(',')
	print(extra_characters)
	global mc
	if 'all' not in names:
		mc=names
	
	for i in extra_characters:
		if i!='':
			mc.append(i)
	mc.sort()
	return render_template("select.html", title="LiteroAnalyzer - Select")  
	
character_name=''
@app.route('/personality_profiling', methods=['POST', 'GET'])
def personality_profiling():
	if request.method == 'POST':
		global fpath
		global loc
		global text
		global mc
		global d
		sentenceList = splitIntoSentences(text)
		characterSentences = compare_lists_new(sentenceList, mc, d)
		print(list(characterSentences))
		temp = characterSentences['Bhishma']
		with open("bhishma.txt","w") as f:
			f.write(str(temp))
		sentenceAnalysis = defaultdict(list,[(k, [characterSentences[k], 0]) for k in characterSentences])
		writeToJSON(sentenceAnalysis, loc)
		global characters
		characters = mc
		return render_template("personality_profiling.html", names= mc, title="LiteroAnalyzer - PersonalityProfiling", traits = ['Anger', 'Sadness', 'Disgust', 'Fear', 'Joy', 'Openness', 'Conscientiousness', "Extraversion", "Agreeableness", "Emotional Range", "Analytical", "Confident", "Tentative"])

@app.route("/emotion_analysis", methods = ['POST'])
def emotion_analysis():
	emotion_ranks={"Anger":[], "Disgust":[], "Fear":[], "Joy":[], "Sadness":[] }
	language_ranks={"Analytical":[], "Confident":[], "Tentative":[]}
	social_ranks={"Openness":[],"Conscientiousness":[],"Extraversion":[],"Agreeableness":[],"Emotional Range":[]}
	for character_name in characters:
		global tone_analyzer
		#print(type(tone_analyzer))
		print(character_name)
		global mc
		global d
		global text
		traits = ['Anger', 'Sadness', 'Disgust', 'Fear', 'Joy', 'Openness', 'Conscientiousness', "Extraversion", "Agreeableness", "Emotional Range", "Analytical", "Confident", "Tentative"]
		x,y,z =character_personality_plot(character_name, tone_analyzer, 'switch', loc, mc, d, text, traits)
		#print("1) ",x[0])
		for i in x:
			emotion_ranks[i].append((x[i],character_name))
		for i in y:
			social_ranks[i].append((y[i],character_name))
		for i in z:
			language_ranks[i].append((z[i],character_name))
	print(emotion_ranks,language_ranks, social_ranks)
	for key in emotion_ranks.keys():
		emotion_ranks[key].sort(reverse=True)
	for key in language_ranks.keys():
		language_ranks[key].sort(reverse=True)
	for key in social_ranks.keys():
		social_ranks[key].sort(reverse=True)
		
	emotion_list={}
	for key in emotion_ranks:
		emotion_list[key]=[]
		for i in emotion_ranks[key][:3]:
			emotion_list[key].append(i[1])

	language_list={}
	for key in language_ranks:
		language_list[key]=[]
		for i in language_ranks[key][:3]:
			language_list[key].append(i[1])

	social_list={}
	for key in social_ranks:
		social_list[key]=[]
		for i in social_ranks[key][:3]:
			social_list[key].append(i[1])

	return render_template("analysis.html", title="LiteroAnalyzer - Analysis", emotion_list =emotion_list, emotion_keys=emotion_list.keys(), language_list =language_list, language_keys=language_list.keys(), social_list =social_list, social_keys=social_list.keys() )

@app.route("/watson", methods = ['POST'])
def watson():
	global uname
	#filename = "watson_fig"+str(time.time())+".png"
	'''for filename in os.listdir('static/'):
		os.remove('static/' + filename)'''
	character_name=request.form.get('character')
	traits = request.form.getlist('traits')
	if 'all' in traits:
		traits=['Anger', 'Sadness', 'Disgust', 'Fear', 'Joy', 'Openness', 'Conscientiousness', "Extraversion", "Agreeableness", "Emotional Range", "Analytical", "Confident", "Tentative"]
	path = "/static/"
	image = uname+str(time.time())+'_'+character_name
	if os.path.exists(path+image)==False:
		#print("####### ",image)
		global tone_analyzer
		global loc
		global mc
		global d
		global text
		character_personality_plot(character_name, tone_analyzer, image, loc, mc, d, text, traits)
		adj = adjectives(character_name, text, loc, mc, d)
		i2 = image+"_social.png"
		i1 = image+"_emotion.png"
		i3 = image+"_language.png"
		i4 = image+"_radar_emotion.png"
		i5 = image+"_radar_social.png"
		i6 = image+"_radar_language.png"
	return render_template("watson.html", title="LiteroAnalyzer - PersonalityProfiling", image1=i1, image2=i2, image3=i3, image4=i4, image5=i5, image6=i6, adj=adj)

@app.route("/network_graph", methods = ['POST'])
def network_graph():
	global fpath
	global loc
	global mc
	global uname
	with open(loc+"/chars.txt", "w") as f:
		f.write("\n".join(mc))

	iname = uname+str(time.time())+'_network.png'
	degree_centrality_ranks = network_graph_main(loc, iname, "ip.txt", "all")
	l = {}
	for i in range(len(degree_centrality_ranks)):
		l[i+1]= degree_centrality_ranks[i]
	print(l)
	l1=[]
	l1.append(l)
	return render_template("network_graph.html", title="LiteroAnalyzer - CharacterNetworks", ranks = l, i1=iname)

@app.route("/single_chapter_analysis", methods = ['POST'])
def single_chapter_analysis():
	global text
	global loc
	global tone_analyzer
	global mc
	global lit
	lit = Literature(text, loc)
	with open(loc+"/chars.txt", "w") as f:
		f.write("\n".join(mc))
	global uname
	fname=uname+str(time.time())+'_chapter_networks'
	os.mkdir('static/'+fname)
	nums=[]
	l1={}
	for chapter_num in lit.chapterNums:
		chapter_text = readText(loc+"/split_chapters/"+chapter_num+".txt")
		iname = fname+'/img'+chapter_num+'.png'
		l={}
		chapter_centrality_ranks = network_graph_main(loc, iname,"split_chapters/"+chapter_num+".txt", chapter_num)
		if chapter_centrality_ranks:
			for i in range(len(chapter_centrality_ranks)):
				#l1.append(chapter_centrality_ranks[i])
				l[i+1]=chapter_centrality_ranks[i]
			nums.append(chapter_num)
			l1[chapter_num]=l
	print(l1)
	return render_template("chapter_analysis1.html", title="LiteroAnalyzer - CharacterNetworks", num= nums, i1 = fname, ranks = l1, chapter = chapter_num)

@app.route("/custom_character_networks", methods = ['POST'])
def custom_char_nw():
	global mc
	mc.sort()
	return render_template("custom_char_nw.html", title="LiteroAnalyzer - CharacterNetworks", names = mc)
	
@app.route("/select_char_nw_analysis", methods = ['POST'])
def select_char_nw_analysis():
	global names
	names = request.form.getlist('entities')
	return render_template("select_char_nw_analysis.html", title="LiteroAnalyzer - CharacterNetworks")

@app.route("/char_nw_results", methods = ['POST'])
def char_nw_results():
	global fpath
	global loc
	global uname
	global names
	#names = request.form.getlist('entities')
	if "all" in names:
		global mc
		names = mc
	print("############################# ", names)
	with open(loc+"/chars.txt", "w") as f:
		f.write("\n".join(names))

	iname = uname+str(time.time())+'_network.png'
	degree_centrality_ranks = network_graph_main(loc, iname, "ip.txt", "all")
	l = {}
	for i in range(len(degree_centrality_ranks)):
		l[i+1]= degree_centrality_ranks[i]
	print(l)
	return render_template("network_graph.html", ranks = l, i1=iname, title="LiteroAnalyzer - CharacterNetworks")
	
@app.route("/chapter_char_nw_results", methods = ['POST'])
def chapter_char_nw_results():
	global text
	global loc
	global tone_analyzer
	global lit
	lit = Literature(text, loc)
	global names
	if "all" in names:
		global mc
		names = mc
	with open(loc+"/chars.txt", "w") as f:
		f.write("\n".join(names))

	global uname
	fname=uname+str(time.time())+'_chapter_networks'
	os.mkdir('static/'+fname)
	nums=[]
	l1={}
	for chapter_num in lit.chapterNums:
		chapter_text = readText(loc+"/split_chapters/"+chapter_num+".txt")
		iname = fname+'/img'+chapter_num+'.png'
		chapter_centrality_ranks = network_graph_main(loc, iname,"split_chapters/"+chapter_num+".txt", chapter_num)
		l = {}
		if chapter_centrality_ranks:
			for i in range(len(chapter_centrality_ranks)):
				#l1.append(chapter_centrality_ranks[i])
				l[i+1]=chapter_centrality_ranks[i]
			nums.append(chapter_num)
			l1[chapter_num]=l	
	return render_template("chapter_analysis1.html", title="LiteroAnalyzer - CharacterNetworks", num= nums, i1 = fname, ranks = l1, chapter = chapter_num)
	
@app.route("/logout", methods = ['POST', 'GET'])
def logout():
	path = "user_sessions/"
	global loc
	global uname
	loc1 = "static/"
	if os.path.exists(loc1):
	    for i in os.listdir(loc1):
	    	if i.startswith(uname):
	    		try:
	    			os.remove(loc1+'/'+i)
	    		except Exception:
	    			for j in os.listdir(loc1+'/'+i):
	    				os.remove(loc1+'/'+i+'/'+j)
	    			os.rmdir(loc1+'/'+i)
	loc=os.path.join(path, uname)
	if os.path.exists(loc):
		for i in os.listdir(loc):
			try:
				os.remove(loc+'/'+i)
			except Exception:
				for j in os.listdir(loc+'/'+i):
					try:
						os.remove(loc+'/'+i+'/'+j)
					except Exception:
						os.remove(loc+i+'/'+j)
				os.rmdir(loc+'/'+i)
		os.rmdir(loc)
	return render_template("login.html", title="LiteroAnalyzer - Login")

if __name__ == '__main__':  
	app.run(debug = True)  
