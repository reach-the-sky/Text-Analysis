from networkx.algorithms.link_analysis.pagerank_alg import pagerank
import spacy as sp 
import networkx as nx
import re
import numpy as np
import matplotlib.pyplot as plt
# import nltk
# from nltk.corpus import stopwords
# stopWords = stopwords.words("english")

def textRank(text,n):
    def cosineSimilarity(a,b):
        return (a.T.dot(b)/(np.linalg.norm(a)*np.linalg.norm(b)))[0,0]

    def pageRank(nxGraph,nodes,alpha,limit):
        dampingFactor = alpha
        pi = np.array([1/nodes]*nodes,dtype=np.float64)
        graph = np.zeros((nodes,nodes),dtype=np.float64)
        inCount = [0]*nodes
        for _ in nxGraph.edges:
            inCount[_[0]] += 1
        for _ in nxGraph.edges:
            graph[_[1]][_[0]] = 1/inCount[_[0]]
        for i,_ in enumerate(inCount):
            if(_ == 0):
                graph[:,i] = [1/nodes]*nodes

        graph = dampingFactor * graph + (1-dampingFactor) * ((1/nodes) * np.ones((nodes,nodes)))

        present = pi
        prev = pi
        count = 0
        while(count < limit and sum(inCount) != 0):
            prev = np.matmul(graph,present)
            present = np.matmul(graph,prev)
            if(prev == present).all():
                break
            count += 1
        return prev


    stopWords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]

    nlp = sp.load("en_core_web_sm")
    doc = nlp(text)

    sentences = [re.sub(r"[^ A-Za-z]","",i.text).lower() for i in doc.sents]
    words = [list(i.split()) for i in sentences]

    removeCommonWords = lambda x : [i for i in x if i not in stopWords]
    cleanWords = [removeCommonWords(i) for i in words]

    wordEmbeddings = {}
    file = open("data/glove.6B/glove.6B.100d.txt")
    for _ in file:
        values = _.split()
        word = values[0]
        wordEmbeddings[word] = np.asarray(values[1:],dtype="float64")
    file.close()

    sVectors = []
    for _ in cleanWords:
        if len(_) != 0:
            temp = sum([wordEmbeddings.get(i,np.zeros((100,))) for i in _])/len(_)
        else:
            temp = np.zeros((100,))
        sVectors.append(temp)

    similarity = np.zeros((len(cleanWords),len(cleanWords)))

    for _ in range(len(cleanWords)):
        for __ in range(len(cleanWords)):
            if _!=__:
                similarity[_][__] = cosineSimilarity(sVectors[_].reshape(100,1),sVectors[__].reshape(100,1))

    nxGraph = nx.from_numpy_array(similarity)
    ranking = pageRank(nxGraph,len(cleanWords),0.85,10)

    RankedSentences = sorted(zip(zip(list(doc.sents),list(range(len(list(doc.sents))))),ranking),key = lambda x:x[1],reverse=True)
    
    RankedSentences = RankedSentences[:n if(n < len(RankedSentences)) else len(RankedSentences)]
    RankedSentences = sorted(RankedSentences,key = lambda x:x[0][1])
    i = 0
    result = ""
    while(i<len(RankedSentences) and i < n):
        result += RankedSentences[i][0][0].text.strip() + " "
        i += 1
    return result


# text = '''Neo-Nazism consists of post-World War II militant social or political movements seeking to revive and implement the ideology of Nazism. Neo-Nazis seek to employ their ideology to promote hatred and attack minorities, or in some cases to create a fascist political state. It is a global phenomenon, with organized representation in many countries and international networks. It borrows elements from Nazi doctrine, including ultranationalism, racism, xenophobia, ableism, homophobia, anti-Romanyism, antisemitism, anti-communism and initiating the Fourth Reich. Holocaust denial is a common feature, as is the incorporation of Nazi symbols and admiration of Adolf Hitler.

# In some European and Latin American countries, laws prohibit the expression of pro-Nazi, racist, anti-Semitic, or homophobic views. Many Nazi-related symbols are banned in European countries (especially Germany) in an effort to curtail neo-Nazism.

# The term neo-Nazism describes any post-World War II militant, social or political movements seeking to revive the ideology of Nazism in whole or in part.

# The term neo-Nazism can also refer to the ideology of these movements, which may borrow elements from Nazi doctrine, including ultranationalism, anti-communism, racism, ableism, xenophobia, homophobia, anti-Romanyism, antisemitism, up to initiating the Fourth Reich. Holocaust denial is a common feature, as is the incorporation of Nazi symbols and admiration of Adolf Hitler.

# Neo-Nazism is considered a particular form of far-right politics and right-wing extremism.'''

# print(textRank(text,5))