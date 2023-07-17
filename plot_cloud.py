# -*- coding: utf-8 -*-
# @Time    : 2021/5/12 11:00 
# @Author  : Yong Cao
# @Email   : yongcao@fuzhi.ai
import json
import argparse
import matplotlib.pyplot as plt
from wordcloud import WordCloud
# import random, requests, re
import nltk
from nltk.corpus import stopwords
import numpy as np
from PIL import Image


def cloud_generate(words, mask):
    wordcloud = WordCloud(background_color="white",
                          min_font_size=1,
                          max_words=70,
                          collocations=False,
                          mask=mask,
                          width=1600, height=800)
    wordcloud.generate(words)
    plt.figure(figsize=(20,10))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig("img.png", dpi=100)
    plt.show()


def replace(x, old) -> str:
    '''批量替换字符串内容
    :param x: 原始字符串
    :param old: 要替换的内容，`list`
    '''
    for item in old:
        x = x.replace(item, "")
    x = x.strip()
    return x

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Export paper information to JSON and Markdown.')
    parser.add_argument('--json_output', default='papers.json', help='Path to the JSON output file')
    args = parser.parse_args()

    path = args.json_output
    papers = []
    with open(path, encoding='utf-8') as fp:
        papers = json.load(fp)

    paper_title_lst = []
    for js in papers:
        url = js['url']
        if 'acl-long' in url:
            paper_title_lst.append(js['title'])
    
    paper_title = ' '.join(paper_title_lst)
    data_cut = nltk.word_tokenize(paper_title)

    words = stopwords.words('english')
    filtered_words = [word for word in data_cut if word not in stopwords.words('english') and len(word) > 1]
    print(filtered_words)
    filtered_words = ' '.join(filtered_words)
    filtered_words = replace(filtered_words, ['dataset', 'Model', "Language", "Neural", "Learning"])
    mask = np.array(Image.open("./circle.jpg"))
    cloud_generate(filtered_words, mask)