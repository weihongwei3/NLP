#!/usr/bin/env python
# -*- coding: utf-8 -*-
from createAllDB_1 import inferenceDB
from getArticles_2 import inferenceArticle
from textProcess_3 import inferenceSenfst
from findNerMention_4 import  inferenceMention
from buildCandidateMention_5 import inferenceCandidate
from getSenNLP_6 import inferenceSenSec
from featureGet_7 import inferenceFeature
from superviseLab_8 import  inferenceQFS
from toSumVote_9 import inferenceTongji
from createFactorGraph_10 import  inferenceInfer
from fankui_11 import inferenceFK


#  整体运行入口（待实现）
def main(tablename,filepathAricle,filepath1,filepath2,mode1,mode2,labeltype,resultpath,exception):
    # inferenceDB(tablename)
    # inferenceArticle(filepathAricle,tablename)
    # inferenceSenfst(tablename)
    # inferenceMention(filepath1,filepath2,tablename,mode1,mode2)
    # inferenceCandidate(tablename)
    # inferenceSenSec(tablename)
    # inferenceFeature(tablename)
    # inferenceQFS(tablename,labeltype)
    # inferenceTongji(tablename)
    # inferenceInfer(tablename,resultpath)
    inferenceFK(tablename,exception)



if __name__ == '__main__':
    # main("belong","news.tsv","wholeOrganize.txt","wholeKeyWord.txt","dict","dict","启发式","./result/biased_coin-performance/inference_result.out.text","0.995")
    main("apply", "news.tsv", "typeKeywords.txt", "wholeOrganize.txt", "type", "dict", "启发式",
         "./result/biased_coin-performance/inference_result.out.text", "0.995")
