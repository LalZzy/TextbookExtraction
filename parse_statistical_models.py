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
import numpy as np

#result = extract_text('StatisticalModels.pdf')

def determin_title_page(textbook_list):
    # function: 提取所有章节的页码,确定书里各个章节的范围
    # input: 课程文本的dict。
    # return: list,表示章节所在的页码。

    # contents outline 在书第七页至第九页
    outline_pages_idx = [6,7,8]
    res = []
    for outline_page in outline_pages_idx:
        outline = textbook_list['Pages'][outline_page]['text']    
        # 用正则表达式提取页码
        tmp = re.findall('(\d+.*\d*)\n',outline)
        # 用正则筛选后，还包括一些噪声，比如：错乱的章节关系。所以去除结果中的噪声
        res.extend([i for i in tmp if '.' not in i and i.isdigit()])
    #真正的页码是从第五个元素开始
    page = [int(res[4])]
    current_value = int(res[4])
    for i in range(4,len(res)-1):
        #print('compare {} with {}'.format(current_value,int(res[i+1])))
        if current_value<=int(res[i+1]):
            #print('yes!')
            page.append(int(res[i+1]))
            current_value = int(res[i+1])
    return page

def load_json(file_path):
    # function: 检查文件夹下有没有解析好的json文件，如果没有的话就调用pdfminer来生成
    # input: str。文件路径名
    # return：
    #   dict。 存储教材的字典。
    #   {'Filename':,
    #    'Pages':{
    #      'Page_number': 1,
    #      'text': 'blablabla……'
    #    }
    #   }
    if not os.path.exists(file_path):
        print('Target pdf\'s json file does not exist. Generating one.')
        export_as_json(file_path.replace('.json','.pdf'),file_path)
    with open(file_path) as f:
        text_json = json.load(f)
    print('Reading target json file done.')
    return text_json    

def match_outline_page(outlines,pages_number):
    # function: 筛选出outlines中的一级标签与二级标签，并且开头为数字的标签
    # input: 
    #   outlines: 用extract_outline提取的大纲
    #   pages_number: list。大纲对应的页码
    # return:
    #   result: dict。 分开存储大纲与页码的字典。
    outlines = [outline[1] for outline in outlines if outline[0] <=2 and outline[1][0].isdigit()]
    if len(outlines) != len(pages_number):
        print('The length of extracted outlines number is inconsistent with that of pages_number list')
    result = {'chapter_name':outlines,'chapter_page_number':pages_number}
    return result

def parse_key_concept_page(textbook_list):
    # function: 解析textbook文本，提取出index部分的关键词及所在页码
    # input: textbook_list: 教材文本dict。
    # return: key_concept字典
    key_concept_dict = {}
    key_concept_index_page =  list(range(729,738,1))
    for key_concept_page in key_concept_index_page:
        text = textbook_list['Pages'][key_concept_page]['text']
        unprocess_key_concepts = re.findall('.*,\n*\d*.* \d.*\n*\d.*',text)
        for unprocess_key_concept in unprocess_key_concepts:
            #print(unprocess_key_concept)
            tmp = unprocess_key_concept.replace('\n',',')
            tmp = tmp.split(',')
            # 全部统一为小写
            tmp[0] = tmp[0].lower()
            # tmp是一个concept的list，
            # 如：['2 × 2 table', ' 135', ' 137', ' 492–496', ' 546', '', '', '557', ' 666', ' 697']
            # 去空格，去横杠，将其存入key_concept_dict中
            key_concept_dict.setdefault(tmp[0],[])
            for page in tmp[1:]:
                if not re.search('\d+',page):continue
                    # 把list中每个元素出现的第一个页码记录下来，比如'492–496'就提取出'492'
                page_num = re.search('\d+',page)[0]
                key_concept_dict[tmp[0]].append(int(page_num))
    # 概念页码去重
    for key,value in key_concept_dict.items():
        key_concept_dict[key] = list(set(value))
    return key_concept_dict 

def find_word_page_from_text(word,textbook):
    # function: 给定一个单词，返回它在教材中出现的页码。
    # input:
    #   word: str。待查询单词。
    #   textbook: dict。 教材dict。
    
    # statistical一书的列表中，第一页对应textbook[12],textbook[11:11+695]
    is_in_pages = [word in x['text'] for x in textbook['Pages'][12:(12+695)]]  
    word_pages = np.arange(1,695+1)[is_in_pages] 
    # 检查单词是否在书中出现过，没有则报错。
    if len(word_pages) == 0:
        raise IOError('Words to be inquired for does not exist in the textbook')
    return word_pages.tolist()


def find_single_word(word,key_concept_dict,outlines,textbook):
    # function: 给定一个单词及它出现过的页码，返回这个单词所在章节。
    # input: 
    #   word: str。单词
    #   key_concept_dict: dict。关键词字典。
    #   outlines: match_outline_page函数返回的大纲dict。
    #   textbook:
    # return: [word, most_frequent_chapter]
    # 如果这个词在key_concept_dict(index)中，就取key_concept_dict[word]，否则
    # 从文本中做遍历，寻找这个词对应的页码
    is_key_word = word in key_concept_dict
    chapter_pages = np.array(outlines['chapter_page_number'])
    if is_key_word:
        word_page_list = key_concept_dict[word]
    else:
        word_page_list = find_word_page_from_text(word,textbook)
        
    concept_chapters = np.zeros((len(word_page_list),),dtype=np.int)
    for i,word_page in enumerate(word_page_list):
        concept_chapters[i] = np.argmax(chapter_pages>word_page)-1
        #print('word_page:{}. chapter_page:{}'.format(word_page,chapter_pages[np.argmax(chapter_pages>word_page)-1]))
    concept_chapters[concept_chapters == -1] = len(chapter_pages)-1
    #print(concept_chapters)
    most_frequent_chapter_idx = np.argmax(np.bincount(concept_chapters))
    most_frequent_chapter = outlines['chapter_name'][most_frequent_chapter_idx]
    return {word:{'most_frequent_chapter':most_frequent_chapter,'page':list(word_page_list)}}

if __name__ == '__main__':
    text_json = load_json('StatisticalModels.json')
    pages_number = determin_title_page(text_json)
    outlines = extract_outline('StatisticalModels.pdf')
    outlines = match_outline_page(outlines,pages_number)
    key_concept_dict = parse_key_concept_page(text_json)
    key_chapter = []
    for concept in key_concept_dict.keys():
        key_chapter.append(find_single_word(concept,key_concept_dict,outlines,text_json))
    print(key_chapter[:5])
    # determin_title_page('StatisticalModels.pdf')