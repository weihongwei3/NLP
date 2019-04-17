# -*- coding: utf-8 -*-
from django.shortcuts import render
from stanfordcorenlp import StanfordCoreNLP
import psycopg2
import datetime
from getConn import get_conn
import progressbar as pb

import datetime

data =[]

def sen(request):
    start = datetime.datetime.now()
    data.append(start)
    nlp = StanfordCoreNLP(r'./stanford-corenlp-full-2017-06-09', lang='zh')
    data.append("server start")
    getNewsDB("belong", nlp)
    # nlp.close()
    data.append(datetime.datetime.now())
    data.append("耗时"+str((datetime.datetime.now() - start).seconds)+"秒")
    return render(request, 'index.html')


def segLine(text):
    seglist = []
    # 分得句子内容列表，分句数
    dictseg={}
    singleline = ""
    # 字符串结构存储（去除干扰部分，英文逗号，tab，{},(),"）
    text = text.replace("”","").replace("\"","").replace("“","").replace("\n","").replace(",","，").replace("    "," ").replace("{"," ").replace("}"," ").replace("("," ").replace(")"," ").replace("'","")
    for i in range(0,len(text)):
        char = text[i]
        if char in "。？！":
            if len(singleline.strip()) == 0:continue
            seglist.append(singleline + char)
            singleline = ""
        else:
            singleline += char
        # print(singleline)
    dictseg["segcontentlist"]=seglist
    dictseg["segnum"]=len(seglist)
    dictseg["text"]=text

    # for item in dictseg["segcontentlist"]:
    #     print(item)
    # print(len(dictseg["segcontentlist"]))
    return dictseg

def parsertext(content,text,docid,sentence_index,nlp):
    sentences=text[sentence_index:]
    listtokens =[]
    listsen = []
    listsentence = []
    listdoc_offset = []
    dict={}
    counter = 0
    for sentence in sentences:
        # 分词
        sentence = sentence.replace(",","").replace("{","").replace("}","")
        tokenizedatas=nlp.word_tokenize(sentence)
        tokens = "{"+",".join(tokenizedatas)+"}"
        #doc_offset
        doc_offsets = []
        for data in tokenizedatas:
            i = content[counter:].find(data)
            doc_offsets.append(str(i + counter))
            counter += i
        offsetStr =  "{"+",".join(doc_offsets)+"}"

        # print(tokens)
        listtokens.append(tokens)
        listdoc_offset.append(offsetStr)
        sentence_index+=1
        listsentence.append(sentence_index)
        listsen.append(sentence)

    dict["docid"]=docid
    dict["sentence_index"]=listsentence
    dict["tokens"] = listtokens
    dict["sentence"]=listsen
    dict["offset"] = listdoc_offset

    return dict

def buildSentenceDB(dict,tablename,conn,cur):
    for i in range(len(dict["sentence_index"])):
        # print(dict["docid"])
        sql="""INSERT INTO sentences_"""+tablename+"""
        (doc_id, sentence_index,sentence_text,tokens,doc_offsets,flag)VALUES('%s','%s','%s','%s','%s',0)"""%\
        (dict["docid"], dict["sentence_index"][i],
        dict["sentence"][i].replace("'","''"),dict["tokens"][i].replace("'","''"),dict["offset"][i])
        # print(sql)
        cur.execute(sql)
        data.append(sql)
        #print(sql)
        conn.commit()

def getNewsDB(tablename,nlp):
    idlist=[]
    conn = get_conn()
    cur = conn.cursor()
    sql = "select id,content from articles_"+tablename+" where id not in (select distinct doc_id from sentences_"+tablename+")"
    #cur.execute("select id,content from articles_"+tablename+" where id not in (select distinct doc_id from sentences_"+tablename+")")   #limit 50 offset 100
    data.append(sql)
    #print(sql)
    cur.execute(sql)
    rows = cur.fetchall()
    taskNum = len(rows)
    string = "%s:N=%d|" % ("textProcess", taskNum)
    pbar = pb.ProgressBar(widgets=[string, pb.Percentage(), pb.Bar(), pb.ETA()], maxval=taskNum)
    pbar.start()
    num_completed = 0
    data.append(string + "|" + "已完成" + str((num_completed/taskNum)*100)+"%")
    for row in rows:
        docid,content=row
        segdict=segLine(content)
        # 按文章解析
        try:
            #print("processing doc id:" + docid)
            buildSentenceDB(parsertext(content,segdict["segcontentlist"],docid,0,nlp),tablename,conn,cur)
        except Exception as err:
            print("1",err)
            conn.commit()
            cur1 = conn.cursor()
            cur1.execute("delete from sentences_" + tablename + " where doc_id='" + docid + "'")
            conn.commit()
            cur1.close()
            continue
        num_completed += 1
        pbar.update(num_completed)
    pbar.finish()
    cur.close()
    conn.close()

#  句子前期处理模块输入接口
def inferenceSenfst(tablename):
    start = datetime.datetime.now()
    print(start)
    print("server start")
    nlp = StanfordCoreNLP(r'./stanford-corenlp-full-2017-06-09', lang='zh')
    getNewsDB(tablename,nlp)
    # nlp.close()
    print((datetime.datetime.now() - start).seconds)

# if __name__ == '__main__':
#     start = datetime.datetime.now()
#     print(start)
#     nlp = StanfordCoreNLP(r'./stanford-corenlp-full-2017-06-09', lang='zh')
#     print("server start")
#     # text = ['我是普通的人，大海啊大海，是清华大学的地方。','海风吹过铜锣湾，阳光照沙滩。']
#     # parsertext(" ".join(text),text, "1", 0)
#     getNewsDB("belong", nlp)
#     # nlp.close()
#     print(datetime.datetime.now())
#     print("耗时"+str((datetime.datetime.now() - start).seconds)+"秒")