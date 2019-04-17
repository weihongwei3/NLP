from stanfordcorenlp import StanfordCoreNLP

nlp = StanfordCoreNLP(r'./stanford-corenlp-full-2017-06-09', lang='zh')
text = "国务院总理李克强调研上海外高桥时提出，支持上海积极探索新机制。"
print(nlp.word_tokenize(text))