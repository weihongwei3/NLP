#!/usr/bin/env python
# -*- coding: utf-8 -*-
import psycopg2
from django.shortcuts import render

from getConn import get_conn
import progressbar as pb
import numpy as np
import datetime

data =[]
def ment(request):
    # 输入识别NER，获得Mention集
    import datetime
    start = datetime.datetime.now()
    data.append(start)
    selectMentionDB("wholeOrganize.txt", "1", "belong", mode="dict")
    selectMentionDB("wholeKeyWord.txt", "2", "belong", mode="dict")
    data.append(datetime.datetime.now())
    data.append("耗时" + str((datetime.datetime.now() - start).seconds) + "秒")
    return render(request, 'index.html')


#无论如何都先建两个实体表


# 处理字典数据的函数
def reWrite(filename):
    file=open(filename,encoding="utf8")
    file2=open("wholeKeyWord.txt",'a',encoiiding="utf8")
    for line in file:
        word =line.split("\t")[1].replace("\n", "")
        file2.write("%s"%(word))
        file2.write("\n")
        word2=line.split("\t")[2].replace("\n", "")
        file2.write("%s"%(word2))
        file2.write("\n")
        # word3=line.split("\t")[3].replace("\n", "")
        # file2.write("%s"%(word3))
        # file2.write("\n")

    file.close()
    file2.close()

def loadNERFile(filePath,mode):
    if mode == "dict":
        with open(filePath, encoding="utf8") as file:
            affillist = []
            for line in file:
                word = line.replace("\n", "")
                affillist.append(word)
        return affillist
    elif mode == "type":
        with open(filePath, "r", encoding="utf8") as file:
            lines = file.readlines()
            keywordsDict = {}
            for line in lines:
                type, set1, set2 = line.split("|")
                type = type.strip()
                keys = set(set1.strip().split(" "))
                words = keys.copy() | set(set2.strip().split(" "))
                keywordsDict[type] = [keys, words]
        return keywordsDict

# 从句子集里提取目标实体入口
def selectMentionDB2(filePath,index,tablename, mode = "dict"):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("select doc_id,sentence_index,sentence_text,tokens from sentences_"+tablename)
    data.append("select doc_id,sentence_index,sentence_text,tokens from sentences_"+tablename)
    datarows=cur.fetchall()
    taskNum = len(datarows)
    string = "%s:N=%d|" % ("findNer", taskNum)
    pbar = pb.ProgressBar(widgets=[string, pb.Percentage(), pb.Bar(), pb.ETA()], maxval=taskNum)
    pbar.start()
    num_completed = 0
    nerData = loadNERFile(filePath, mode)
    for row in datarows:
        doc_id, sentence_index,sentence_text, tokens=row
        senLength = len(sentence_text)
        #筛选句子
        if senLength > 100 or senLength < 10: continue

        if mode == "dict":
            mentionDict(doc_id,sentence_index,sentence_text,tokens,nerData,index,tablename,conn,cur)
        #elif mode == "type":
        #    mentionType(doc_id, sentence_index, sentence_text, tokens, nerData, index, tablename, conn, cur)
        num_completed += 1
        pbar.update(num_completed)
    pbar.finish()
    cur.close()
    conn.close()

# 从句子集里提取目标实体入口
def selectMentionDB(filePath, index, tablename, mode = "dict"):
    conn = get_conn()
    cur = conn.cursor()
    sql = "select id,title,content from articles_" + tablename +" where id not in (select distinct doc_id from mention"+index+"_" + tablename+")"
    cur.execute(sql)
    datarows = cur.fetchall()
    taskNum = len(datarows)
    string = "%s:N=%d|" % ("findNer", taskNum)
    pbar = pb.ProgressBar(widgets=[string, pb.Percentage(), pb.Bar(), pb.ETA()], maxval=taskNum)
    pbar.start()
    num_completed = 0
    data.append(string + "|" + "已完成" + str((num_completed / taskNum) * 100) + "%")
    nerData = loadNERFile(filePath, mode)
    for row in datarows:
        docId,title,content = row
        keyList = getKeyListPerDoc(title,content,nerData,mode)
        # 按照文章遍历，每次获取一篇文章下所有句子，统一处理wordList
        cur.execute("select sentence_index,sentence_text,tokens from sentences_" + tablename+" where doc_id = '%s'"%docId)
        senrows = cur.fetchall()
        for sen in senrows:
            sentence_index, sentence_text, tokens = sen
            senLength = len(sentence_text)
            if senLength > 100 or senLength < 10: continue
            getMentionFromSen(docId,sentence_index,sentence_text,tokens,keyList,index,tablename,conn,cur)
        num_completed += 1
        pbar.update(num_completed)
    pbar.finish()
    cur.close()
    conn.close()

def getMentionFromSen(doc_id,sentence_index,sentence_text,tokens,keyList,index,tablename,conn,cur):
    senKeys = [key for key in keyList if key in sentence_text]
    tokens = [item if item is not None else "" for item in tokens]
    if len(senKeys) > 0:
        for i in range(len(tokens)):
            begin_index=i
            for word in senKeys:
                if word.find(tokens[i]) == 0:
                    entity = tokens[i]
                    indexes = i + 1
                    while (entity != word or len(entity) < len(word)) and indexes < len(tokens):
                        entity += tokens[indexes]
                        indexes += 1
                    if entity == word:
                        end_index=indexes-1
                        mention_id = "%s_%d_%d_%d" % (doc_id, sentence_index, begin_index, end_index)
                        mention_text = "".join(tokens[begin_index:end_index+1])
                        #print(mention_id,mention_text)
                        insertMentionDB(doc_id, sentence_index, begin_index, end_index, mention_id, mention_text, index,
                                        tablename,conn,cur)
        conn.commit()




filterList = ["实时","大众"]
def getKeyListPerDoc(title,content,nerData,mode="dict"):
    keyList = []
    if mode == "dict":
        affillist = list(set(nerData) - set(filterList))
        for word in affillist:
            if word in content:
                keyList.append(word)
    elif mode == "type":
        typeKeywords = nerData
        typesWeight = {}
        for item in typeKeywords.items():
            typesWeight[item[0]] = [0, 0]
            tags = item[1][1]
            for tag in tags:
                typesWeight[item[0]][0] += content.count(tag)
                typesWeight[item[0]][1] += title.count(tag)

        def softmax(x):
            return np.exp(x) / np.sum(np.exp(x), axis=0)

        typeList = sorted(typesWeight.items(), key=lambda x: x[1], reverse=True)
        contentList = softmax([item[1][0] for item in typeList])
        titleList = softmax([item[1][1] for item in typeList])
        newList = [(typeList[i][0], contentList[i] / 2 + titleList[i]) for i in range(len(typeList))]
        typeList = sorted(newList, key=lambda x: x[1], reverse=True)
        pridictTypes = [item[0] for item in typeList[:3] if item[1] > 0.3]
        if len(pridictTypes) == 0: pridictTypes = [typeList[0][0]]
        keySet = set()
        for type in pridictTypes:
            keySet.update(set(typeKeywords[type][0]))
        keyList = list(keySet)
    return keyList


# 实体判定函数,传入参数doc_id文章id，sentence_index句号，tokens分词情况，ner_type识别情况，index第几个实体，tablename表名后缀（可用于单提及的实体认知上，那样就无需生成候选集）
def mention(doc_id,sentence_index,tokens,ner_tags,ner_type,index,tablename):
    num_tokens = len(ner_tags)
    # mentionDict={}
    # find all first indexes of series of tokens tagged as ner_type
    first_indexes = (i for i in range(num_tokens) if ner_tags[i] ==ner_type and (i == 0 or ner_tags[i-1] != ner_type))
    for begin_index in first_indexes:
        # find the end of the ner_type phrase (consecutive tokens tagged as PERSON)
        end_index = begin_index + 1
        while end_index < num_tokens and ner_tags[end_index] == ner_type:
            end_index += 1
        end_index -= 1
        # generate a mention identifier
        mention_id = "%s_%d_%d_%d" % (doc_id, sentence_index, begin_index, end_index)
        # print(mention_id,len(tokens),tokens[begin_index])
        # print(len(ner_tags))
        mention_text = "".join(map(lambda i: tokens[i], range(begin_index, end_index+1)))
        # Output a tuple for each ner_type phrase
        # print(doc_id,sentence_index,begin_index,end_index,mention_id,mention_text)
        insertMentionDB(doc_id,sentence_index,begin_index,end_index,mention_id,mention_text,index,tablename)


def mentionDict(doc_id,sentence_index,sentence_text,tokens,nerData,index,tablename,conn,cur):
    tokens = [item if item is not None else "" for item in tokens]
    affillist = list(set(nerData)-set(filterList))
    num_tokens = len(tokens)
    wordList = []
    for word in affillist:
        if word in sentence_text:
            wordList.append(word)
    if len(wordList) > 0:
        # print(sentence, wordList)
        # print(doc_id,wordList,tokens)
        for i in range(num_tokens):
            begin_index=i
            for word in wordList:
                if word.find(tokens[i]) == 0:
                    entity = tokens[i]
                    indexes = i + 1
                    while (entity != word or len(entity) < len(word)) and indexes < len(tokens):
                        entity += tokens[indexes]
                        indexes += 1
                    if entity == word:
                        end_index=indexes-1
                        mention_id = "%s_%d_%d_%d" % (doc_id, sentence_index, begin_index, end_index)
                        mention_text = "".join(tokens[begin_index:end_index+1])
                        #print(mention_id,mention_text)
                        insertMentionDB(doc_id, sentence_index, begin_index, end_index, mention_id, mention_text, index,
                                        tablename,conn,cur)
        conn.commit()


# 插入提取实体到数据库
def insertMentionDB(doc_id,sentence_index,begin_index,end_index,mention_id,mention_text,index,tablename,conn,cur):
    # 避免重复插入数据
    cur.execute("select * from mention"+index+"_"+tablename+" where mention_id='%s'"%(mention_id))
    datarows=cur.rowcount
    if datarows<=0:
        sql = """INSERT INTO mention"""+index+"""_"""+tablename\
            +"""(doc_id,sentence_index,begin_index,end_index,mention_id,mention_text)
            VALUES('%s',%d,%d,%d,'%s','%s')""" % \
            (doc_id,sentence_index,begin_index,end_index,mention_id,mention_text.replace("'","''"))
        cur.execute(sql)
        data.append(sql)

# 实体模块输入接口
def inferenceMention(filepath1,fielpath2,tablename,mode1,mode2):
    start = datetime.datetime.now()
    print(start)
    selectMentionDB(filepath1, "1", tablename, mode=mode1)
    selectMentionDB(fielpath2, "2", tablename, mode=mode2)
    print((datetime.datetime.now() - start).seconds)


# if __name__ == '__main__':
#     # 输入识别NER，获得Mention集
#     import datetime
#     start = datetime.datetime.now()
#     print(start)
#     # selectMentionDB("PERSON","1","belong")
#     # selectMentionDB("ORGANIZATION", "2", "belong")
#     selectMentionDB("wholeOrganize.txt", "1", "belong", mode = "dict")
#     selectMentionDB("wholeKeyWord.txt", "2", "belong", mode = "dict")
#     # selectMentionDB("typeKeywords.txt", "1", "belong",
#     #
#     #
#     #  mode = "type")
#     # reWrite("../wholeKeyWord.txt")
#     print(datetime.datetime.now())
#     print((datetime.datetime.now() - start).seconds)

