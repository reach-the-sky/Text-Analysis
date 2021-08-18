from neo4j import GraphDatabase
import spacy
import re
from spacy import displacy
import networkx as nx

# def NER(text,link):
#     nlp = spacy.load("en_core_web_sm")
#     doc = nlp(text)

#     driver = GraphDatabase.driver(link,auth=("neo4j","password"))

#     def addEntity(tx,entity1,entity2):
#         tx.run("MERGE (a1:Entity {name: $entity1}) "
#         "MERGE (a2:Entity {name: $entity2}) "
#         "MERGE (a1)-[:Related]-(a2)"
#         ,entity1 = entity1,entity2 = entity2)

#     with driver.session() as session:
#         for sent in doc.sents:
#             temp = nlp(str(sent)).ents
#             if(len(temp) > 2):
#                 for i,entity1 in enumerate(temp[:-1]):
#                     for entity2 in temp[i+1:]:
#                         session.write_transaction(addEntity,str(entity1),str(entity2))
#             elif(len(temp) == 2):
#                 session.write_transaction(addEntity,str(temp[0]),str(temp[1]))

#     driver.close()


def NER(text):
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)
    sent = [i.text for i in doc.sents]
    def get_entities(a): 
        dep_type=[]
        doc = nlp(a)

        d={}
        for i in doc:
            d[i.text] = i.dep_

        a = list(filter(lambda x:'det' not in x and 'punct' not in x and 'dep' not in x and 'prep' not in x,d.items()))

        pron = ['he', 'she', 'it', 'they','his', 'her','their','i', 'me', 'you','this', 'that', 'which']
        for pos,i in enumerate(a):
            for j in pron:
                if j in i[0].lower().split(' '):
                    a.pop(pos)
                    break
        mod=''
        prev=''
        prev_text=''

        comp=''
        entities = []
        for i in range(0,len(a)):
            global added
            if 'nsubj' == a[i][1] or 'obj' in a[i][1]:
                added=0
            else:
                added=float('inf')
            
            flag=''
            if spacy.explain(prev):
                flag = spacy.explain(prev)
            if 'mod' in prev or 'mod' in flag:
                mod = mod+' '+prev_text

            if 'mod' in a[i-1][1] and 'attr' in a[i][1]:
                entities.append((a[i-1][0]+' '+a[i][0]).strip())
                dep_type.append(a[i-1][1])

            if 'comp' in prev:
                comp = comp+' '+prev_text
            
            if 'mod' not in prev:
                mod=''
            if 'comp' not in prev:
                comp=''
                    
            if 'subj' in a[i][1] or 'obj' in a[i][1]:
                entities.append((' '.join([mod.strip(),comp.strip(),a[i][0].strip()])).strip())
                dep_type.append(a[i][1])
                added=1
                mod=''
                
            if added==0:
                entities.append(a[i][0])
                dep_type.append(a[i][1])
            
            prev=a[i][1]
            prev_text=a[i][0]

        return(entities,dep_type)
    l=[]
    d=[]
    for i in sent:
        temp=get_entities(i)
        l.append(temp[0])
        d.append(temp[1])
    
    sent = [i for i in doc.sents]
    edges=[]
    for pos,i in enumerate(sent):
        lst=[]
        lst.append(i.root)
        for j in i.root.children:
            if 'subj' in j.dep_ or 'obj' in j.dep_:
                asdf=l[pos]
                flag=0
                for k in asdf:
                    if str(j.text).lower() in list(map(lambda x:x.strip(), k.lower().split())):
                        lst.append(k)
                        flag=1
                        break
                if not flag:
                    lst.append(j.text)
        if len(lst)<3:
            for j in i.root.children:
                if j.dep_ == 'prep':
                    for k in j.children:
                        if "obj" in k.dep_:
                            if len(lst)<=3:
                                lst.append(str(j)+' '+str(k))
        if len(lst)>=3:
            edges.append(lst[:3])

    graph = {
        "nodes":[],
        "links":[]
    }
    uniqueNodes = set()
    for triplet in edges:
        if(triplet[1] not in uniqueNodes):
            uniqueNodes.add(triplet[1])
            graph["nodes"].append({"id": triplet[1]})
        if(triplet[2] not in uniqueNodes):
            uniqueNodes.add(triplet[2])
            graph["nodes"].append({"id": triplet[2]})
        graph["links"].append({"source": triplet[1], "target": triplet[2],"value":str(triplet[0])})
    print(graph)
    return graph


# text='''Neo-Nazism consists of post-World War II militant social or political movements seeking to revive and implement the ideology of Nazism. Neo-Nazis seek to employ their ideology to promote hatred and attack minorities, or in some cases to create a fascist political state. It is a global phenomenon, with organized representation in many countries and international networks. It borrows elements from Nazi doctrine, including ultranationalism, racism, xenophobia, ableism, homophobia, anti-Romanyism, antisemitism, anti-communism and initiating the Fourth Reich. Holocaust denial is a common feature, as is the incorporation of Nazi symbols and admiration of Adolf Hitler.

# In some European and Latin American countries, laws prohibit the expression of pro-Nazi, racist, anti-Semitic, or homophobic views. Many Nazi-related symbols are banned in European countries (especially Germany) in an effort to curtail neo-Nazism.

# The term neo-Nazism describes any post-World War II militant, social or political movements seeking to revive the ideology of Nazism in whole or in part.

# The term neo-Nazism can also refer to the ideology of these movements, which may borrow elements from Nazi doctrine, including ultranationalism, anti-communism, racism, ableism, xenophobia, homophobia, anti-Romanyism, antisemitism, up to initiating the Fourth Reich. Holocaust denial is a common feature, as is the incorporation of Nazi symbols and admiration of Adolf Hitler.

# Neo-Nazism is considered a particular form of far-right politics and right-wing extremism.'''

# NER(text,"bolt://localhost:7687")
