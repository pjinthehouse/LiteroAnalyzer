
import re
import nltk
from nltk.stem.snowball import SnowballStemmer
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt


def wordTokens(text, stop_words):
    """
    Tokenization of a string in word tokens
    
    :param text: A string
    :param stop_words: A list of stop words to not be considered in the final tokens

    :return: A list of word tokens
    """
    
    wtokens = nltk.word_tokenize(text.lower())
    
    # Remove stop words
    wtokens = [w for w in wtokens if w not in stop_words]

    return wtokens



def char_tuple_f(chars_list):
    """
    This function creates a list of tuples from the names of the characters.
    
    :param chars_list: A list of character names. The names should be in lowercase.
    :return: A list of tuples for each name in the initial list
    """
    
    char_tuples_list = []
    for char in chars_list:
        tup = tuple(char.split(" "))
        char_tuples_list.append(tup)
    return char_tuples_list


def indices_dic(char_tuples, words, bigr, trigr):
    """
    This function finds every occurrence of a character name in a list of tokens.
    It returns the indices of each occurrence for each character in a numpy array.  
    
    :param char_tuples: A list of character names as tuples
    :param words: A list of single word tokens
    :param bigr: A list of bigram tuples 
    :param trigr: A list of trigram tuples
    :return: A dictionary with the characters' names as keys and a array of indices as values.
    """
    
    dic = {}
    for tup in char_tuples:
        char_name = " ".join(tup)
        n = len(tup)
        
        if n == 1:
            indices = [i for i, x in enumerate(words) if x == tup[0]]
            
        elif n == 2:
            indices = [i for i, x in enumerate(bigr) if x == tup]
            
            if tup[0] not in ['mr.', 'mrs.', 'mr', 'mrs', 'master', 'mistress']:
                indices += [i for i, x in enumerate(words) if x == tup[0]]
            
        elif n == 3:
            indices = [i for i, x in enumerate(trigr) if x == tup]
            if tup[0] in ['mr.', 'mrs.', 'mr', 'mrs']:
                indices+= [i for i, x in enumerate(bigr) if x == (tup[0], tup[1])]
                indices+= [i for i, x in enumerate(bigr) if x == (tup[0], tup[2])]
                indices+= [i for i, x in enumerate(bigr) if x == (tup[1], tup[2])]
                indices += [i for i, x in enumerate(words) if x == tup[1]]
                indices += [i for i, x in enumerate(words) if x == tup[2]]
                
            else:
                indices+= [i for i, x in enumerate(bigr) if x == (tup[0], tup[2])]
                indices += [i for i, x in enumerate(words) if x == tup[0]]
                indices += [i for i, x in enumerate(words) if x == tup[2]]
            
        dic[char_name] = np.array(indices)
    
    return dic


def links_dic_f(indices_dic, threshold):
    """
    This function creates the dictionary of the links of each character. The function compares 
    the distance of two indices where character names appear. If this distance is lower than a 
    threshold it counts as an interaction between the two characters.
    
    :param indices_dic: The dictionary with the indices for each character 
    :param threshold: The distance threshold. If the difference of two indices of two characters is 
                       lower than the threshold, this counts as an interaction
    :return: A nested dictionary. Each key is a character name. The values are dictionaries with 
              keys the characters the initial key character has interacted with, and with values the 
              number of interactions. 
    """
    
    link_dic = {}
    for first_char, ind_arr1 in indices_dic.items():
        dic = {}
        for second_char, ind_arr2 in indices_dic.items():
            
            # Don't count interactions with self
            if first_char == second_char:
                continue
            
            matr = np.abs(ind_arr1[np.newaxis].T - ind_arr2) <= threshold
            s = np.sum(matr)
            
            # Only include character pairs with more than 3 interactions
            if s > 3:
                dic[second_char] = s
        link_dic[first_char] = dic
    
    return link_dic

def merge_nickname(dic, mainname, nickname):
    """
    This function updates a link dictionary by merging the interaction values of one character 
    name with another. The second character is considered as a nickname of first, so we wish to 
    have all character's interactions under one name.
    
    :param dic: A link dictionary produced by the links_dic_f function
    :param mainname: The main name of the character that will remain after the merge
    :param nickname: The nickname of the character that will be merge into the main name
    :return: A link dictionary like the one produced by links_dic_f but with the nickname 
              values merged into the main name
    """
    
    for key in dic[nickname]:
        if key in dic[mainname]:
            dic[mainname][key] += dic[nickname][key]
        elif key==mainname:
            continue
        else:
            dic[mainname][key] = dic[nickname][key]

    for key in dic:
        if key==mainname:
            dic[key].pop(nickname, None)
            continue

        if nickname in dic[key]:
            if mainname in dic[key]:
                dic[key][mainname] += dic[key][nickname]
            else:
                dic[key][mainname] = dic[key][nickname]

        dic[key].pop(nickname, None)

    dic.pop(nickname, None)
    
    return dic


def merge_all_nicknames(dic, nickname_list):
    """
    This function updates a link dictionary by merging the interactions of some characters with
    other characters. This is done by applying the merge_nickname function for a provided
    list of main names and nick names.

    :param dic: A link dictionary produced by the links_dic_f function
    :param nickname_list: A list of tuples. The first item of the tuple is the main name of
                           a character and the second in the nickname
    :return: An updated link dictionary with all the nicknames merged into the main names
    """
    
    for tup in nickname_list:
        (mainname, nickname) = tup
        dic = merge_nickname(dic, mainname, nickname)
    return dic


# Uncomment this part and provide a nickname list if your text contains characters with more than one name

#nick_list = []
#grand_dic = merge_all_nicknames(grand_dic, nick_list)


# # Remove characters with no interactions

# In[11]:


def remove_zero_link_chars(link_dic, chars_list):
    """
    This function removes all characters with no links from a characters list.
    
    :param link_dic: A link dictionary produced by the links_dic_f function
    :param chars_list: A list of characters
    :return: A list of characters. All of the characters in the final list have links with 
             other characters in the link dictionary
    """
    
    rem_set = set()
    for key in link_dic:
        if link_dic[key] == {}:
            rem_set.add(key)
    
    fin_list = [char for char in chars_list if char not in rem_set]
    
    return fin_list




# # Create the nodes and edges of the graph

# In[12]:


def edge_tuples_f(link_dic):
    """
    It produces the edges of a graph, along with their weight, based on the dictionary
    with the interactions of the characters.
    
    :param link_dic: A link dictionary produced by the links_dic_f function
    :return: A list of tuples to be used as the edges of a graph. The first two items are 
              the nodes of the edge. The third item is the weight of the edge 
    """
    
    edges_tuples = []
    for key in link_dic:
        for item, value in link_dic[key].items():
            tup = (key.title(), item.title(), value/1000)
            edges_tuples.append(tup)

    return edges_tuples



# In[13]:


def convert_to_capitals(char_list):
    """
    Capitalizes characters' names.
    
    :param char_list: A list of characters names
    :return: A list of capitalized characters names
    """
    
    conv_list = []
    for char in char_list:
        conv_list.append(char.title())
    
    return conv_list




# In[ ]:

def network_graph_main(loc, iname, switch, chapter):

    
        infile = loc+"/"+switch
        outfile = 'out.gexf'

        with open(infile, 'r', errors='ignore') as file:
            data = file.read().replace('\n', ' ')

        text = re.sub('[^A-Za-z0-9.]+', ' ', data)

        chars = []

        with open(loc+"/chars.txt", 'r') as file:
            for line in file:
                name = line.strip().lower()
                chars.append(name)

        # Get a list of stop words
        stopWords = nltk.corpus.stopwords.words('english')

        tokens = wordTokens(text, stopWords)
        bigrm = nltk.bigrams(tokens)
        bigrms = list(bigrm)
        trigrm = nltk.trigrams(tokens)
        trigrms = list(trigrm)

        #print(tokens,"\n\n\n\n", bigrms,"\n\n\n\n", trigrms)

        char_tuples = char_tuple_f(chars)
        #print(char_tuples)
        ind_dic = indices_dic(char_tuples, tokens, bigrms, trigrms)
        grand_dic = links_dic_f(ind_dic, 20)
        #print(grand_dic)
        new_chars = remove_zero_link_chars(grand_dic, chars)
        edges_tuples = edge_tuples_f(grand_dic)
        node_chars = convert_to_capitals(new_chars)
        centrality_ranks=[]
        if node_chars:	
        	G = nx.Graph()
        	G.add_nodes_from(node_chars)
        	G.add_weighted_edges_from(edges_tuples)
        	
        	edges = G.edges()
        	weights = [G[u][v]['weight'] * 50 for u,v in edges]
        	
        	#plt.figure(figsize=(12,12)) 
        	plt.clf()
        	nx.draw_shell(G, with_labels=True,  width = weights, node_size=100, font_size=10)
        
        	import community
        	partition = community.best_partition(G)
        	nx.set_node_attributes(G, partition, 'group')
        	
        	#plt.savefig('static/network_graph.png', dpi=300, bbox_inches='tight')
        	try:
        	    os.remove('static/'+iname)
        	except:
        	    pass
        	#plt.title('Chapter: ', chapter)
        	plt.savefig('static/'+iname, dpi=600,  bbox_inches='tight')
        	d=nx.degree_centrality(G)
        	centrality_ranks=list(dict(sorted(d.items(), key = lambda x : x[-1], reverse=True)))
        return centrality_ranks[:10]
        
