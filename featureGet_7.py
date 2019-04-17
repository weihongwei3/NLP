#!/usr/bin/env python
# -*- coding: utf-8 -*-
import psycopg2
import datetime

from django.shortcuts import render

from ddlib2 import dd
from ddlib2 import gen_feats
from ddlib2 import util
from getConn import get_conn
import progressbar as pb

data =[]

def featuree(request):
    start = datetime.datetime.now()
    data.append(start)
    selectfeatureMentionDB("belong")
    data.append(datetime.datetime.now())
    data.append("耗时" + str((datetime.datetime.now() - start).seconds) + "秒")
    return render(request, 'index.html')


# 检索关系对特征的入口
def selectfeatureMentionDB(tablename):
    conn = get_conn()
    cur = conn.cursor()
    # 从候选集里提取两词特征

    sql = """select A.id,A.p1_id,A.p2_id,B.begin_index,B.end_index,C.begin_index, C.end_index,D.tokens,D.lemmas,D.pos_tags,D.ner_tags,D.dep_types,D.dep_tokens 
        from candidate_"""+tablename+""" as A, mention1_"""+tablename+""" as B,mention2_"""+tablename+""" as C,sentences_"""+tablename+""" as D
        where A.p1_id=B.mention_id and A.p2_id=C.mention_id and B.doc_id=D.doc_id
        and B.sentence_index=D.sentence_index and A.id not in (select distinct cid from feature_"""+tablename+""")"""
    cur.execute(sql)
    data.append("实体关系选取中......")
    data.append(sql)
    datarows=cur.fetchall()
    taskNum = len(datarows)
    string = "%s:N=%d|" % ("featureGet", taskNum)
    pbar = pb.ProgressBar(widgets=[string, pb.Percentage(), pb.Bar(), pb.ETA()], maxval=taskNum)
    pbar.start()
    num_completed = 0
    #flash(string + "|" + "已完成" + str((num_completed / taskNum) * 100) + "%")
    for row in datarows:
        featureMention(row,tablename,conn,cur)
        num_completed += 1
        pbar.update(num_completed)
    pbar.finish()
    cur.close()
    conn.close()

# 特征提取函数
def featureMention(data,tablename,conn,cur):
    cid,p1_id, p2_id, p1_begin_index, p1_end_index, p2_begin_index, p2_end_index, tokens, lemmas, pos_tags, ner_tags, dep_types, dep_tokens = data
    sent = []
    for i, t in enumerate(tokens):
        #print("p1_id=====" + p1_id + "        p2_id======" + p2_id)
        sent.append(dd.Word(
            begin_char_offset=None,
            end_char_offset=None,
            word=t,
            lemma=lemmas[i],
            pos=pos_tags[i],
            ner=ner_tags[i],
            dep_par=dep_tokens[i] - 1,  # Note that as stored from CoreNLP 0 is ROOT, but for DDLIB -1 is ROOT
            dep_label=dep_types[i]))

    # Create DDLIB Spans for the two mentions
    p1_span = dd.Span(begin_word_id=p1_begin_index, length=(p1_end_index - p1_begin_index + 1))
    p2_span = dd.Span(begin_word_id=p2_begin_index, length=(p2_end_index - p2_begin_index + 1))

    # Gen'31LIB
    features = gen_feats.get_generic_features_relation(sent, p1_span, p2_span)
    # print (cid, features)
    data.append("特征提取中......")
    data.append("processing id ====" + str(cid) + "|features====" + features)
    buildFeatureDB(str(cid),features,tablename,conn,cur)
    conn.commit()

# 关系对特征结果插入数据库
def buildFeatureDB(cid,features,tablename,conn,cur):
    # 避免重复插入数据
    #cur.execute("select * from feature_"+tablename+" where p1_id='%s' and p2_id='%s' and feature='%s'" % (p1_id,p2_id,feature.replace("'","''")))
    #datarows = cur.rowcount
    #if datarows <= 0:
    values= ",".join(["("+cid+",\'"+f.replace("'","''")+"\')" for f in features])
    sql = "INSERT INTO feature_"+tablename+"(cid,feature )VALUES "+values
    data.append("插入特征结果......")
    data.append(sql)
    cur.execute(sql)

# 特征接口
def inferenceFeature(tablename):
    start = datetime.datetime.now()
    print(start)
    selectfeatureMentionDB(tablename)
    print((datetime.datetime.now() - start).seconds)


# if __name__ == '__main__':
#     import datetime
#     start = datetime.datetime.now()
#     print(start)
#     selectfeatureMentionDB("belong")
#     print(datetime.datetime.now())
#     print((datetime.datetime.now() - start).seconds)

