#!/usr/bin/env python
# -*- coding: utf-8 -*-
import psycopg2
import datetime

from django.shortcuts import render

from getConn import get_conn
data =[]
def article(request):
    import datetime
    start = datetime.datetime.now()
    print(start)
    readTSV("../news.tsv","belong")
    print(datetime.datetime.now())
    print("耗时"+str((datetime.datetime.now() - start).seconds)+"秒")

    data.append("开始时间：" + str(start))
    data.append("结束时间：" + str(datetime.datetime.now()))
    data.append("耗时"+str((datetime.datetime.now() - start).seconds)+"秒")
    return render(request, 'index.html', {'data':data})



# 读取tsv格式源文件55
def readTSV(filename,name):
    dict={}
    file=open(filename,"r",encoding="utf8")
    # conn=get_conn()
    # cur=conn.cursor()
    # cur.execute("select *  from articles_"+name+" ")
    # datarows=cur.fetchall()
    # count=len(datarows)
    conn = get_conn()
    cur = conn.cursor()
    # 按行读文件
    alllines=file.readlines()
    for line in alllines:
        list=line.split("\t")
        dict["id"]=list[0]
        # print (dict["id"])
        dict["url"]=list[1]
        # print (dict["url"])
        dict["title"]=list[2]
        dict["content"]=list[3]
        # dict["count"]=count
        insertArticleInDB(dict,name,conn,cur)
        # count+=1
    cur.close()
    conn.close()

# 插入文章信息到数据库,name反映传进去的表后缀
def insertArticleInDB(dict,name,conn,cur):

    cur.execute("select * from articles_"+name+" where content='%s'" % (dict["content"].replace("'","''")))
    datarows = cur.rowcount
    # 重复数据项不添加数据
    if datarows <= 0:
        sql = """INSERT INTO articles_"""+name+"""(id,url,title,content)
                        VALUES('%s','%s','%s','%s')""" % \
              (dict["id"],dict["url"],dict["title"].replace("'","''"),dict["content"].replace("'","''"))
        # sql = """INSERT INTO articles_"""+name+"""(id,content)
        #                 VALUES('%s','%s')""" % \
        #       (dict["count"],dict["content"].replace("'","''"))
        cur.execute(sql)
        #print("id==" + dict["id"])
        #flash(sql)
        #flash("=============================")
        conn.commit()

#  文章输入接口
def inferenceArticle(filepath,tablename):
    start = datetime.datetime.now()
    print(start)
    readTSV(filepath, tablename)
    print((datetime.datetime.now() - start).seconds)

