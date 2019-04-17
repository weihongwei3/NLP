#!/usr/bin/env python
# -*- coding: utf-8 -*-
import psycopg2
from django.shortcuts import render

from getConn import get_conn

data = []

def create(request):
    createAllDB("belong")
    print('建表成功')
    data.append("建表成功")
    return render(request, 'index.html',{'data':data})


def createAllDB(name):
    #连接数据库
    conn = get_conn()
    # 建立cursor对象
    cur = conn.cursor()
    # id 文章id惟一，url文章链接，title文章标题，content文章内容，source文章来源，主键id
    sql = """CREATE TABLE if not exists articles_"""+name+""" (
                id text COLLATE "default",
                url text COLLATE "default",
                title text COLLATE "default",
                content text COLLATE "default"
            )
            WITH (OIDS=FALSE);
            ALTER TABLE articles_"""+name+""" OWNER TO postgres"""
    #执行sql命令，创建一个新表
    cur.execute(sql)
    #print(sql)

    #提交数据改变
    conn.commit()
    data.append(sql)
    data.append("表articles_" + name + "创建完成")
    data.append("=========================================")
    # doc_id文章id，sentence_index句号，sentence_text句子内容，tokens分词，lemmas原词，pos_tags词性标记，ner_tags实体识别标记，doc_offsets所在文章第几个词，dep_types文法依赖，dep_tokens文法依赖树
    sql = """CREATE TABLE if not exists sentences_"""+name+""" (
                id SERIAL primary key,
                doc_id text COLLATE "default",
                sentence_index int4,
                sentence_text text COLLATE "default",
                tokens text[] COLLATE "default",
                lemmas text[] COLLATE "default",
                pos_tags text[] COLLATE "default",
                ner_tags text[] COLLATE "default",
                doc_offsets int4[],
                dep_types text[] COLLATE "default",
                dep_tokens int4[],
                flag int4
            )
            WITH (OIDS=FALSE);
            ALTER TABLE sentences_"""+name+""" OWNER TO postgres"""
    cur.execute(sql)
    data.append(sql)
    data.append("表sentences_" + name + "创建完成")
    data.append("=========================================")
    conn.commit()
    # mention_id实体1id，mention_text实体内容，doc_id文章id，sentence_index句号，begin_index实体1句中起始位置，end_index实体1句中结束位置
    sql = """CREATE TABLE if not exists mention1_"""+name+""" (
                   mention_id text COLLATE "default",
                   mention_text text COLLATE "default",
                   doc_id text COLLATE "default",
                   sentence_index int4,
                   begin_index int4,
                   end_index int4
               )
               WITH (OIDS=FALSE);
               ALTER TABLE mention1_"""+name+""" OWNER TO postgres"""
    cur.execute(sql)
    data.append(sql)
    data.append("表mention1_" + name + "创建完成")
    data.append("=========================================")
    conn.commit()
    # mention_id实体2id，mention_text实体内容，doc_id文章id，sentence_index句号，begin_index实体2句中起始位置，end_index实体2句中结束位置
    sql = """CREATE TABLE if not exists mention2_"""+name+""" (
                   mention_id text COLLATE "default",
                   mention_text text COLLATE "default",
                   doc_id text COLLATE "default",
                   sentence_index int4,
                   begin_index int4,
                   end_index int4
               )
               WITH (OIDS=FALSE);
               ALTER TABLE mention2_"""+name+""" OWNER TO postgres"""
    cur.execute(sql)
    data.append(sql)
    data.append("表mention2_" + name + "创建完成")
    data.append("=========================================")
    conn.commit()
    # p1_id实体1id，p1_name实体1内容，p2_id实体2id，p2_name实体2内容，关系对候选表
    sql = """CREATE TABLE if not exists candidate_"""+name+""" (
                    id SERIAL primary key,
                    p1_id text COLLATE "default",
                    p1_name text COLLATE "default",
                    p2_id text COLLATE "default",
                    p2_name text COLLATE "default"
                )
                WITH (OIDS=FALSE);
                ALTER TABLE candidate_"""+name+""" OWNER TO postgres"""
    cur.execute(sql)
    data.append(sql)
    data.append("表candidate_" + name + "创建完成")
    data.append("=========================================")
    conn.commit()
    # p1_id实体1id，p2_id实体2id，feature关系对特征
    sql = """CREATE TABLE if not exists feature_"""+name+""" (
                    cid int NOT NULL,
                    feature text COLLATE "default"
                )
                WITH (OIDS=FALSE);
                ALTER TABLE feature_"""+name+""" OWNER TO postgres"""
    cur.execute(sql)
    data.append(sql)
    data.append("表feature_" + name + "创建完成")
    data.append("=========================================")
    conn.commit()
    conn.close()



# from getArticles_2 import artic
# app.register_blueprint(artic, url_prefix='/artic')
# from textProcess_3 import sentence
# app.register_blueprint(sentence, url_prefix='/sentence')
# from findNerMention_4 import mentionn
# app.register_blueprint(mentionn, url_prefix='/mentionn')
# from buildCandidateMention_5 import candidatee
# app.register_blueprint(candidatee, url_prefix='/candidatee')
# from getSenNLP_6 import getnlp
# app.register_blueprint(getnlp, url_prefix='/getnlpp')
# from featureGet_7 import feature
# app.register_blueprint(feature, url_prefix='/feature')



# 数据库创建接口
def inferenceDB(tablename):
    # 需要提供一个数据库接口
    createAllDB(tablename)
    print("建表成功")


# if __name__ == '__main__':
    # 需要提供一个数据库接口
    #createAllDB("belong")
    #print ("建表成功")
