from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import os
import psycopg2
import json

def search_articles(request):
	conn = psycopg2.connect(database="postgres", user="postgres", password="123456", host="localhost", port="5432")
	cur = conn.cursor()
	print("connect postgresql successful!!!!")
	cur.execute("SELECT id,url,title,SUBSTRING(content,0,50) FROM articles_belong LIMIT 1000;")
	rows = cur.fetchall()
	conn.commit()
	cur.close()
	conn.close()
	return render(request, 'save.html', {'data':rows})

def search_sentences(request):
	conn = psycopg2.connect(database="postgres", user="postgres", password="123456", host="localhost", port="5432")
	cur = conn.cursor()
	print("connect postgresql successful!!!!")
	cur.execute("SELECT id,doc_id,sentence_index,sentence_text,tokens FROM sentences_belong ORDER BY id ASC LIMIT 1000;")
	rows = cur.fetchall()
	conn.commit()
	cur.close()
	conn.close()
	return render(request, 'sentence.html', {'data':rows})

def search_entity(request):
	conn = psycopg2.connect(database="postgres", user="postgres", password="123456", host="localhost", port="5432")
	cur = conn.cursor()
	print("connect postgresql successful!!!!")
	cur.execute("SELECT id,p1_id,p1_name,p2_id,p2_name FROM candidate_belong ORDER BY id ASC LIMIT 1000;")
	rows = cur.fetchall()
	conn.commit()
	cur.close()
	conn.close()
	return render(request, 'entity.html', {'data':rows})

def search_feature(request):
	return render(request, 'feature.html')