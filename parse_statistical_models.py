# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 20:53:55 2018

@author: Travis
"""

from miner_text_generator import extract_text, extract_outline
from json_exporter import export_as_json
import re
import json
import os
import sys
import numpy as np

#result = extract_text('StatisticalModels.pdf')

def determin_title_page(textbook_list):
    # 提取所有章节的页码,确定书里各个章节的范围
    # contents outline 在书第七页至第九页
    outline_pages_idx = [6,7,8]
    res = []
    for outline_page in outline_pages_idx:
        print(outline_page)
        outline = textbook_list['Pages'][outline_page]['Page_'+str(outline_page+1)]    
        # 用正则表达式提取页码
        tmp = re.findall('(\d+.*\d*)\n',outline)
        # 用正则筛选后，还包括一些噪声，比如：错乱的章节关系。所以去除结果中的噪声
        res.extend([i for i in tmp if '.' not in i and i.isdigit()])
    print(res)
    #真正的页码是从第五个元素开始
    page = [int(res[4])]
    current_value = int(res[4])
    for i in range(4,len(res)-1):
        #print('compare {} with {}'.format(current_value,int(res[i+1])))
        if current_value<=int(res[i+1]):
            #print('yes!')
            #print(current_value)
            page.append(int(res[i+1]))
            current_value = int(res[i+1])
    return page

def load_json(file_path):
    # 首先检查文件夹下有没有转化好的json文件，如果没有的话就用pdfminer来生成
    if not os.path.exists(file_path):
        print('Target pdf\'s json file does not exist. Generating one.')
        export_as_json(file_path.replace('.json','.pdf'),file_path)
    with open(file_path) as f:
        text_json = json.load(f)
    print('Reading target json file done.')
    return text_json    

def match_outline_page(outlines,pages_number):
    # 筛选出outlines中的一级标签与二级标签，并且开头为数字的
    outlines = [outline[1] for outline in outlines if outline[0] <=2 and outline[1][0].isdigit()]
    print(outlines)
    if len(outlines) != len(pages_number):
        print('The length of extracted outlines number is inconsistent with that of pages_number list')
    result = {'chapter_name':outlines,'chapter_page_number':pages_number}
    return result

def parse_key_concept_page(textbook_list):
    # 解析textbook文本，提取出index部分的关键词及所在页码
    # return: key_concept字典
    key_concept_dict = {}
    key_concept_index_page =  list(range(729,738,1))
    for key_concept_page in key_concept_index_page:
        text = textbook_list['Pages'][key_concept_page]['Page_'+str(key_concept_page+1)]
        unprocess_key_concepts = re.findall('.*,\n*\d*.* \d.*\n*\d.*',text)
        for unprocess_key_concept in unprocess_key_concepts:
            #print(unprocess_key_concept)
            tmp = unprocess_key_concept.replace('\n',',')
            tmp = tmp.split(',')
            # tmp是一个concept的list，
            # 如：['2 × 2 table', ' 135', ' 137', ' 492–496', ' 546', '', '', '557', ' 666', ' 697']
            # 去空格，去横杠，将其存入key_concept_dict中
            key_concept_dict.setdefault(tmp[0],[])
            for page in tmp[1:]:
                if not re.search('\d+',page):continue
                    # 把list中每个元素出现的第一个页码记录下来
                page_num = re.search('\d+',page)[0]
                key_concept_dict[tmp[0]].append(int(page_num))
            #print(tmp)
            #print(key_concept_dict[tmp[0]])
            #break
    # 概念页码去重
    for key,value in key_concept_dict.items():
        key_concept_dict[key] = list(set(value))
    return key_concept_dict 

def find_single_word(word,key_concept_dict,outlines):
    # 给定一个单词，返回这个单词所在章节。
    # input: word.
    # return: [word, most_frequent_chapter]
    chapter_pages = np.array(outlines['chapter_page_number'])
    word_page_list = key_concept_dict[word]
    concept_chapters = np.zeros((len(word_page_list),),dtype=np.int)
    for i,word_page in enumerate(word_page_list):
        concept_chapters[i] = np.argmax(chapter_pages>word_page)-1
        print('word_page:{}. chapter_page:{}'.format(word_page,chapter_pages[np.argmax(chapter_pages>word_page)-1]))
    concept_chapters[concept_chapters == -1] = len(chapter_pages)-1
    print(concept_chapters)
    most_frequent_chapter_idx = np.argmax(np.bincount(concept_chapters))
    most_frequent_chapter = outlines['chapter_name'][most_frequent_chapter_idx]
    return {word:most_frequent_chapter}

if __name__ == '__main__':
    text_json = load_json('StatisticalModels.json')
    pages_number = determin_title_page(text_json)
    outlines = extract_outline('StatisticalModels.pdf')
    outlines = match_outline_page(outlines,pages_number)
    key_concept_dict = parse_key_concept_page(text_json)
    key_chapter = []
    for concept in key_concept_dict.keys():
        key_chapter.append(find_single_word(concept,key_concept_dict,outlines))
    print(key_chapter[:5])
    # determin_title_page('StatisticalModels.pdf')