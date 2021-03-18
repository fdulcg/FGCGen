# coding=utf-8
import codecs
import lcg
from pymongo import MongoClient


# CN-Probase
isa_db = None

# fatherconcept = {}
# for c in concept:
#     for each in [item[0] for item in lcg.getConcept(c)]:
#         if each in concept:
#             if c not in fatherconcept:
#                 fatherconcept[c] = [each]
#             else:
#                 fatherconcept[c].append(each)


numberlist = [0]

import time,re

def RemoveHerf(text):
    pattern = re.compile('<a(.*?)>')
    for noise in pattern.findall(text):
        text = text.replace('<a'+noise+'>','')
    text = text.replace('</a>','')
    text = text.strip()
    return text

def getTriples(ent):
    ret = []
    for item in triplesdb.find({'s':ent}):
        p = item.get('p')
        if p=='CATEGORY_ZH' or p=='DESC':
            continue
        if item.get('o') is not None:
            o = RemoveHerf(item.get('o'))
            ret.append([p,o])
    return ret



def getConcept(ent):
    ret = []
    for item in isadb.find({'ent':ent}):
        ret.append([item.get('con')])
    return ret


def writed(num,thedict):
    if num not in numberlist:
        with codecs.open('data/proresult'+str(num)+'.txt','a','utf-8') as fda:
            for each in thedict:
                for values in thedict[each]:
                    fda.write(each + '\t' + str(values) + '\n')

def conceptGetPropertyList(property2entropy_file):
    child2properties = {}
    for line in lcg.LoadCSV('data/proresult13649.txt'):
        if line[0] not in child2properties:
            child2properties[line[0]] = [line[1]]
        else:
            child2properties[line[0]].append(line[1])
    print(len(child2properties))
    pro2entropy = {line[0]:float(line[1]) for line in lcg.LoadCSV(property2entropy_file)}
    counter = 0
    flag = False
    for entity in entitylist:
        counter+=1
        if counter%100 == 0:
            print(counter)
        rettriples = getTriples(entity)
        # concept = [item[1] for item in rettriples if item[0] =='CATEGORY_ZH']
        triples = [item for item in rettriples if item[0] !='CATEGORY_ZH']
        templateproperty = {}
        for p2o in triples:
            if pro2entropy.get(p2o[0],-999)>1.0:
                templateproperty[p2o[0]] = pro2entropy.get(p2o[0],-999)
        # print(templateproperty)
        entConcepts = [item[0] for item in getConcept(entity)]
        for child in entConcepts:
            manyentities = [ent[0] for ent in lcg.getEntityByConcept(child) if ent[0]!=entity]
            if len(manyentities)>25:
                manyentities = manyentities[:25]
            haslist = []
            for ent in manyentities:
                if child not in [item for item in entConcepts if item!=child]:
                    plist = [item[0] for item in getTriples(ent) if item[0] != 'CATEGORY_ZH']
                    for tempp in templateproperty:
                        if tempp in plist and tempp not in haslist:
                            haslist.append(tempp)
            if len(haslist)<1:
                continue
            if child not in child2properties:
                child2properties[child] = haslist
            else:
                child2properties[child] += [it for it in haslist if it not in child2properties[child]]
        print(entity,'concept len',len(child2properties))
        if len(child2properties)>numberlist[-1]:
            writed(len(child2properties),child2properties)
            numberlist.append(len(child2properties)+100)
    with codecs.open('data/finalproresult.txt','a','utf-8') as fd:
        for thekey in child2properties:
            for values in child2properties[thekey]:
                fd.write(thekey+'\t'+str(values)+'\n')


