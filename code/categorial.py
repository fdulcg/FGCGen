# coding=utf-8
import codecs
import lcg
import math
import re
import numpy as np

def calc_ent(x):
    x_value_list = set([x[i] for i in range(x.shape[0])])
    ent = 0.0
    # sum_value = sum(x_value_list)
    for x_value in x_value_list:
        # p = x_value/sum_value
        p = float(x[x == x_value].shape[0]) / x.shape[0]
        logp = np.log(p)
        ent -= p * logp
    return ent

def calc_schent(x):
    x_value_list = set([x[i] for i in range(x.shape[0])])
    ent = 0.0
    for x_value in x_value_list:
        # p = x_value/sum_value
        p = float(x[x == x_value].shape[0]) / x.shape[0]
        logp = np.log(p)
        ent -= p * logp / np.log(len(x_value_list))
    return ent

def cal_fc(x):
    # x_value_list = set([x[i] for i in range(x.shape[0])])
    fc = np.var(x)
    return fc


def RemoveHerf(text):
    pattern = re.compile('<a(.*?)>')
    for noise in pattern.findall(text):
        text = text.replace('<a'+noise+'>','')
    text = text.replace('</a>','')
    text = text.strip()
    return text

def RemoveSymbol(text):
    pattern2 = re.compile('\((.*?)\)|（(.*?)）')
    for noise2 in pattern2.findall(text):
        for en in noise2:
            text = text.replace('(' + en + ')', '').replace('（' + en + '）', '')
    text = text.strip()
    rule = re.compile("[^a-zA-Z0-9\u4e00-\u9fa5&]")
    text = rule.sub('', text)
    text = text.strip()
    return text

def quoteFile(path,line):
    with codecs.open(path,'a','utf-8') as fd:
        fd.write(line)

def getMostFreqLength(d):
    len2freq = {}
    for val in d:
        if len(val) not in len2freq:
            len2freq[len(val)] = int(d[val])
        else:
            len2freq[len(val)] += int(d[val])
    len2freq = lcg.sortdict(len2freq)
    retlen = 0
    for each in len2freq:
        retlen = each
        break
    return retlen

def Writep2v2f(path ,p2vdict):
    with codecs.open(path,'a','utf-8') as fd:
        for p in p2vdict:
            # fd.write(p + '\t' + str(len(p2vdict[p])) + '\n')
            for v in p2vdict[p]:
                fd.write(p+'\t'+v+'\t'+str(p2vdict[p][v])+'\n')


def CompuateCharWeight(dict1):
    char2f = {}
    sum = 0
    for item in dict1:
        for char in item:
            sum += dict1[item]
            if char not in char2f:
                char2f[char] = dict1[item]
            else:
                char2f[char] += dict1[item]
    char2score = {}
    for each in char2f:
        char2score[each] = float(char2f[each] / sum)
    word2score = {}
    for it in dict1:
        s = 0
        for c in it:
            s+=char2score[c]
        word2score[it] = s
    return word2score


def ValueDistribution(spo_file, outfile):
    '''
    统计过程，输出属性  属性值  频率
    :return:
    '''
    p2vdict = {}

    for lin in lcg.LoadCSV(spo_file'):
        if len(lin)<3:
            continue
        value = RemoveHerf(lin[2])
        if '\\' in lin[2] : value = [v.strip() for v in value.split('\\')]
        elif '/' in lin[2] : value = [v.strip() for v in value.split('/')]
        elif ',' in lin[2]: value = [v.strip() for v in value.split(',')]
        elif '；' in lin[2] : value =[v.strip() for v in value.split('；')]
        else: value = [value]
        for v in value:
            v = RemoveSymbol(v)
            if v.strip() == '' or v.strip('\t') == '':
                continue
            if lin[1] not in p2vdict:
                p2vdict[lin[1]] = {v:1}
            else:
                if v in p2vdict[lin[1]]:
                    p2vdict[lin[1]][v] += 1
                else:
                    p2vdict[lin[1]][v] = 1
    Writep2v2f(outfile, p2vdict)


def FuseValue(p2v_file, outfile):
    '''
    归一化属性值，基于假设：如果v0属于v1，则保留v0还是
    :return:
    '''
    p2v2f = {}
    for line in lcg.LoadCSV(p2v_file):
        if len(line) == 3:
            if line[0] not in p2v2f:
                p2v2f[line[0]] = {line[1]: int(line[2])}
            else:
                p2v2f[line[0]][line[1]] = int(line[2])
    writedict = {}
    for p in p2v2f:
        templatelen = getMostFreqLength( p2v2f[p])
        valuelist = [v for v in p2v2f[p]]
        word2score = CompuateCharWeight(p2v2f[p])
        word2weight = {}
        for word in word2score:
            word2weight[word] = word2score[word]*p2v2f[p][word]
        writedict[p] = lcg.sortdict(word2weight)
        # newp2f = {}
        # removelist = []

        for value in valuelist:
            print(removelist)
            if value in removelist:
                continue
            for item in valuelist:
                if item == value:continue
                fusionlist = []
                if str(item).startswith(value):
                    if len(item) == templatelen:
                        newp2f[item] = p2v2f[p][item]+p2v2f[p][value]
                        removelist+=[item,value]
                    elif len(value) == templatelen:
                        newp2f[value] = p2v2f[p][item]+p2v2f[p][value]
                        removelist+=[item,value]
                    else:
                        newp2f[value] = p2v2f[p][value]
        # writedict[p] = newp2f
    Writep2v2f(outfile, writedict)

# FuseValue()

def writed(path,lin):
    with codecs.open(path,'a','utf-8') as f:
        f.write(lin)

def testpro(true_properties, falseproperties, allp2v):
    truelist = [it[0] for it in true_properties]
    falselist = [it[0] for it in falseproperties)]
    item2pro = {}
    for each in allp2v:
        if len(each) == 3:
            # if float(each[2])>1:
            #     print(each[0],each[1],each[2])
            if each[0] not in item2pro:
                item2pro[each[0]] = [int(float(each[2]))]
            else:
                item2pro[each[0]].append(int(float(each[2])))

    p2e = {}
    for ited in item2pro:
        entropy = calc_ent(np.array(item2pro[ited]))
        entropy = float(entropy)
        p2e[ited] = entropy
    p2e = lcg.sortdict(p2e)
    score,sum = 0,0
    for it in truelist:
        if it in item2pro:
            sum+=1
            ent = calc_ent(np.array(item2pro[it]))
            print(it,ent)
            if ent>1:
                score+=1
            # writed('trueresult.txt',it+'\t'+ str(ent)+'\n')
    print('true pre',float(score)/sum)
    print('##################################')
    score1 = 0
    sum1 = 0
    for it1 in falselist:
        if it1 in item2pro:
            sum1+=1
            ent1 = calc_ent(np.array(item2pro[it1]))
            print(it1, ent1)
            if ent1<1:
                score1 += 1
            # writed('falseresult.txt',it1 + '\t' + str(ent1) + '\n')
    print('false pre',float(score1)/sum1)

testpro()

