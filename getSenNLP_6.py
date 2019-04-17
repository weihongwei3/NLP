# -*- coding: utf-8 -*-
from django.shortcuts import render
from stanfordcorenlp import StanfordCoreNLP
import psycopg2
import datetime
from getConn import get_conn
import progressbar as pb

data =[]

def getnlpp(request):
    start = datetime.datetime.now()
    data.append(start)
    nlp = StanfordCoreNLP(r'./stanford-corenlp-full-2017-06-09', lang='zh')
    data.append("server start")
    getSensNLP("belong",nlp)
    data.append(datetime.datetime.now())
    data.append("耗时" + str((datetime.datetime.now() - start).seconds) + "秒")
    # nlp.close()
    return render(request, 'index.html')

def parsertext(sentence, tokens, docid,sentence_index,nlp):
    # print (text)
    sentence = sentence.replace(",", "").replace("{", "").replace("}", "").replace("'","")
    #print("sentence=" + sentence)
    #tokenizedatas = nlp.word_tokenize(sentence)
    #tokens = ",".join(tokenizedatas).replace(",", "")
    lemmas = "{" + ",".join(tokens) + "}"
    print("lemmas=" + lemmas)
    # pos_tag
    posrows = nlp.pos_tag(sentence)
    pos_tag = "{" + ",".join([v for k,v in posrows]) + "}"
    # stanford get ner_tags
    nerrows = nlp.ner(sentence)
    ner_tag = "{" + ",".join([v for k,v in nerrows]) + "}"

    tempdeprows = nlp.dependency_parse(sentence)
    #print(tempdeprows)
    #print("tempdeprows------------------------------------------------------")
    deprows = sorted(tempdeprows, key=lambda tempdeprows: tempdeprows[2])
    #print(deprows)
    #print("deprows---------------------------------------------------------")
    dep_types = "{" + ",".join([a.replace("ROOT","\'\'") for a,b,c in deprows]) + "}"
    #print(dep_types)
    #print("dep_types------------------------------------------------------")
    dep_tokens = "{" + ",".join([str(b) for a,b,c in deprows]) + "}"
    #print(dep_tokens)
    #print("dep_tokens--------------------------------------------------------")

    #print("docid=======" + docid)
    dict = {}
    dict["docid"]=docid
    dict["sentence_index"]= sentence_index
    dict["lemmas"] = lemmas
    dict["pos_tags"] = pos_tag
    dict["ner_tags"] = ner_tag
    dict["dep_types"] = dep_types
    dict["dep_tokens"] = dep_tokens
    return dict

def buildSentenceDB(dict,tablename,conn,cur):
        #print(dict["docid"])
        sql="""update sentences_"""+tablename+"""
        set lemmas = '%s',pos_tags= '%s',ner_tags= '%s',dep_types= '%s',dep_tokens= '%s',flag=1 
        where doc_id = '%s' and sentence_index = '%s'"""%\
        (dict["lemmas"],dict["pos_tags"],dict["ner_tags"],dict["dep_types"],dict["dep_tokens"],dict["docid"], dict["sentence_index"])
        data.append("更新词性标注......")
        data.append(sql)
        cur.execute(sql)
        conn.commit()

def getSensNLP(tablename,nlp):
    conn = get_conn()
    cur = conn.cursor()
    sql = "select doc_id, sen_id,max(txt),max(tokens) from ( "+\
    "select D.doc_id as doc_id, D.sentence_index as sen_id, D.sentence_text as txt, D.tokens as tokens "+\
    "from candidate_"+tablename+" as A, mention1_"+tablename+" as B,mention2_"+tablename+" as C,sentences_"+tablename+" as D "+\
    " where A.p1_id=B.mention_id and A.p2_id=C.mention_id and B.doc_id=D.doc_id "+\
    "and B.sentence_index=D.sentence_index and D.flag = 0 "+\
    ") as E group by doc_id,sen_id"
    data.append("实体关系选取中......")
    data.append(sql)
    cur.execute(sql)
    rows = cur.fetchall()
    taskNum = len(rows)
    string = "%s:N=%d|" % ("senNLP", taskNum)
    pbar = pb.ProgressBar(widgets=[string, pb.Percentage(), pb.Bar(), pb.ETA()], maxval=taskNum)
    pbar.start()
    num_completed = 0
    #flash(string + "|" + "已完成" + str((num_completed / taskNum) * 100) + "%")
    for row in rows:
        docid,sen_id,sen_txt,tokens = row
        try:
            print("processing doc id:" + docid)
            buildSentenceDB(parsertext(sen_txt, tokens, docid, sen_id, nlp), tablename, conn, cur)
            #buildSentenceDB(parsertext(tokens, docid, sen_id, nlp), tablename, conn, cur)
        except Exception as e:
            print("1", e)
            continue

        num_completed += 1
        pbar.update(num_completed)
    pbar.finish()
    cur.close()
    conn.close()

# 句子后期处理接口
def inferenceSenSec(tablename):
    start = datetime.datetime.now()
    print(start)
    nlp = StanfordCoreNLP(r'./stanford-corenlp-full-2017-06-09', lang='zh')
    # text = '我是普通的人，大海啊大海，是清华大学的地方。海风吹过铜锣湾，阳光照沙滩。'
    # parsertext(text, None,"1","1")
    # print("server start")
    getSensNLP(tablename,nlp)
    print((datetime.datetime.now() - start).seconds)
    # nlp.close()


# if __name__ == '__main__':
#     import datetime
#     start = datetime.datetime.now()
#     print(start)
#     nlp = StanfordCoreNLP(r'./stanford-corenlp-full-2017-06-09', lang='zh')
#     #text = '我是普通的人，大海啊大海，是清华大学的地方。海风吹过铜锣湾，阳光照沙滩。'
#     #parsertext(text, None,"1","1")
#     print("server start")
#     getSensNLP("belong",nlp)
#     print(datetime.datetime.now())
#     print((datetime.datetime.now() - start).seconds)
#     # nlp.close()