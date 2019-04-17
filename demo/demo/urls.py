from django.conf.urls import url 
from . import index_view

from . import _404_view
from . import relation_view
import sys
sys.path.append("../..")
import createAllDB_1
import getArticles_2
import textProcess_3
import findNerMention_4
import buildCandidateMention_5
import getSenNLP_6
import featureGet_7


urlpatterns = [
    url(r'^$', index_view.index),
    url(r'^404',_404_view._404_),
    url(r'^search_articles',relation_view.search_articles),
    url(r'^search_sentences', relation_view.search_sentences),
    url(r'^search_entity', relation_view.search_entity),
    url(r'^search_feature', relation_view.search_feature),

    url(r'^create', createAllDB_1.create),
    url(r'^article', getArticles_2.article),
    url(r'^sen', textProcess_3.sen),
    url(r'^ment', findNerMention_4.ment),
    url(r'^cand', buildCandidateMention_5.cand),
    url(r'^getnlpp', getSenNLP_6.getnlpp),
    url(r'^featuree', featureGet_7.featuree)
]
