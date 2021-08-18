from neo4j import GraphDatabase
import pandas as pd
import numpy as np
import networkx as nx
import spacy
from collections import Counter
import json

class Neo4j:
    def __init__(self,uri,user,password):
        self.driver = GraphDatabase.driver(uri,auth=(user,password))
        
    def query(self,query):
        result=None
        with self.driver.session() as session:
            result = list(session.run(query))
            session.close()
        return result
    
    def close(self):
        self.driver.close()


def Recommendation(movie):
    nlp = spacy.load("en_core_web_sm")
    neo = Neo4j("bolt://localhost:7687","neo4j","password")

    movieliked = neo.query(f'''
        match (p:Person) -[r1:WATCHED] -> (m:Movie)
        where r1.rating>3 and m.title = "{movie}"
        return distinct p.user_id as id
    ''')

    movieliked = list(map(lambda x:x['id'],movieliked))

    movies = {}
    for i in movieliked:
        ilikes = neo.query(f'''
            match (p:Person)-[r1:WATCHED]->(m:Movie)
            where p.user_id={i} and r1.rating>2.5
            return m.IMDB_id as imdb,r1.rating as rating
        ''')
        for j in ilikes:
            movies[j['imdb']] = movies.get(j['imdb'],[])
            movies[j['imdb']].append(j['rating'])

    n = 0.25*len(movieliked)
    movies = dict(filter(lambda x: len(x[1]) > n,movies.items()))

    for i in movies:
        movies[i] = np.mean(movies[i])

    plots = movies.copy()

    for i in plots:
        plot = neo.query(f'''
            match (m:Movie)
            where m.IMDB_id = "{i}"
            return m.plot as plot,m.genres as genres
        ''')
        plots[i] = plot[0]['genres']+" "+plot[0]['plot']

    movieplot = neo.query(f'''match (m:Movie) where m.title="{movie}" return m.plot as plot, m.genres as genres''')
    movieplot = movieplot[0]['genres']+" "+movieplot[0]['plot']

    movieplot = nlp(movieplot)
    movieplot = list(filter(lambda x: x.pos_ not in "PUNCT" and x.is_stop == False,movieplot))
    movieplot = list(map(lambda x:x.text.lower(),movieplot))

    for i in plots:
        plots[i] = nlp(plots[i])
        plots[i] = list(filter(lambda x: x.pos_ not in "PUNCT" and x.is_stop == False,plots[i]))
        plots[i] = list(map(lambda x:x.text.lower(),plots[i]))

    allwords = set(movieplot)

    for i in plots:
        allwords = allwords|set(plots[i])

    idf = {}
    allwords = tuple(allwords)
    n = len(plots)

    for i in allwords:
        count = 0
        for j in plots:
            if i in plots[j]:
                count+=1
        idf[i]=np.log10(n/count)

    for i in plots:
        plots[i] = Counter(plots[i])
        n = sum(plots[i].values())
        for j in plots[i]:
            plots[i][j]*=idf[j]/n

    movieplot = Counter(movieplot)
    mn = sum(movieplot.values())
    for i in movieplot:
        movieplot[i]*=idf[i]/mn

    cosinesim = {}
    for i in plots:
        common = list(set(movieplot.keys())&set(plots[i].keys()))
        idotj = sum(map(lambda x:movieplot[x]*plots[i][x],common))
        deti = sum(map(lambda x:movieplot[x]**2,list(movieplot)))**0.5
        detj = sum(map(lambda x:plots[i][x]**2,list(plots[i])))**0.5
        cosinesim[i] = idotj/(deti*detj)

    simmovies = sorted(cosinesim.items(),key=lambda x:x[1],reverse=True)
    simmovies = list(filter(lambda x:x[1]>0,simmovies))   
    result = []
    
    # import poster data
    file = open("moviePosters.json","r")
    posters = json.load(file)
    file.close()

    for i in simmovies[:12]:
        movieTemp = neo.query(f'match (m:Movie) where m.IMDB_id ="{i[0]}" return m.title as title')[0]['title']
        posterLink = posters.get(movieTemp,"static/images/NoPoster.jpg")
        result.append([movieTemp,posterLink])
    neo.close()
    return result

# Recommendation("Thor")