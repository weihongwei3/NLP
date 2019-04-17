#!/usr/bin/env python
# -*- coding: utf-8 -*-
import psycopg2
import datetime

from django.shortcuts import render

from getConn import get_conn
import progressbar as pb

data =[]

def cand(request):
    start = datetime.datetime.now()
    ##flash(start)
    #combineMeniton("belong")  #逐个判断插入
    insertCandidationAll("belong") #全sql插入
    ##flash(datetime.datetime.now())
    ##flash((datetime.datetime.now() - start).seconds)
    return render(request, 'index.html')


# 目前仅针对两者之间的关系（待扩展）

# 查找句子与文章号，帮助mention两两组合,生成关系对入口
def combineMeniton(tablename):
    conn = get_conn()
    cur = conn.cursor()
    sql = "select * from mention1_"+tablename+" as A, mention2_"+tablename+" as B " +\
          "WHERE A.doc_id=B.doc_id and A.sentence_index=B.sentence_index"
    #print(sql)
    #return
    cur.execute(sql)
    datarows = cur.fetchall()
    taskNum = len(datarows)
    string = "%s:N=%d|" % ("candidate", taskNum)
    pbar = pb.ProgressBar(widgets=[string, pb.Percentage(), pb.Bar(), pb.ETA()], maxval=taskNum)
    pbar.start()
    num_completed = 0
    for data in datarows:
        mention_id, mention_text, doc_id, sentence_index, begin_index, end_index = data[:6]
        mention_id2, mention_text2, doc_id2, sentence_index2, begin_index2, end_index2 = data[6:]
        # 词距离过长
        if begin_index2 - end_index > 25 or end_index2 - begin_index > 25:
            continue
        insertCandidationDB(mention_id, mention_text, mention_id2, mention_text2, tablename, conn, cur)
        num_completed += 1
        pbar.update(num_completed)
    pbar.finish()
    cur.close()
    conn.close()


# 将数据集加入到数据库中
def insertCandidationDB(mention_id, mention_text,mention_id2, mention_text2,tablename, conn, cur):
    # 避免重复插入数据,允许同一种实体位置调换，便于后面推理
    cur.execute("select * from candidate_"+tablename+" where p1_id='%s' and p2_id='%s'" % (mention_id,mention_id2))
    datarows = cur.rowcount
    if datarows <= 0:
        # 数据库的名需要未来修改的
        sql = """INSERT INTO candidate_""" + tablename + """(p1_id,p1_name,p2_id,p2_name)
                   VALUES('%s','%s','%s','%s')""" % \
              (mention_id, mention_text.replace("'","''"),mention_id2, mention_text2.replace("'","''"))
        cur.execute(sql)
        conn.commit()
    return datarows

def insertCandidationAll(tablename):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE candidate_" + tablename)  # 清空原表
    cur.execute("select setval( 'candidate_" + tablename + "_id_seq',1,false);")  #重置自增id为1
    sql = "insert into candidate_" + tablename + " (p1_id, p1_name, p2_id, p2_name) " +\
    "select p1_id, p1_name, p2_id, p2_name from ("+\
    "select A.mention_id as p1_id, A.mention_text as p1_name, A.doc_id, A.sentence_index, A.begin_index,A.end_index,"+\
    "B.mention_id as p2_id, B.mention_text as p2_name, B.doc_id, B.sentence_index, B.begin_index,B.end_index "+\
    "from mention1_" + tablename + " as A, mention2_" + tablename + " as B "+\
    "WHERE A.doc_id=B.doc_id and A.sentence_index=B.sentence_index "+\
    "and (B.begin_index - A.end_index <= 25 or B.end_index - A.begin_index <= 25)" +\
    ") as C"
    data.append(sql)
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()
    ##flash("候选集创建完成")

# 候选关系对接口
def inferenceCandidate(tablename):
    start = datetime.datetime.now()
    print(start)
    # combineMeniton(tablename)  #逐个判断插入
    insertCandidationAll(tablename)  # 全sql插入
    print((datetime.datetime.now() - start).seconds)


# if __name__ == '__main__':
#     import datetime
#
#     start = datetime.datetime.now()
#     print(start)
#     #combineMeniton("belong")  #逐个判断插入
#     insertCandidationAll("belong") #全sql插入
#     print(datetime.datetime.now())
#     print((datetime.datetime.now() - start).seconds)
