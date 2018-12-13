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

class TextBook(object):
    def __init__(self,book_name,outline_st_page,outline_end_page,document_st_page,
                 document_end_page,index_st_page,index_end_page):
        # book_name: 书名
        # outline_st_page: outline起始页码（指起始页在列表中的索引值，并非真实页码）,
        #                 为text_json中某一页的Page_num-1
        # outline_end_page: outline终止页码。
        # document_st_page: 正文起始页码。
        # document_end_page: 正文终止页码。
        # index_st_page: index起始页码。
        # index_end_page : ......
        self.name = book_name.replace('.pdf','')
        self.outline_st_page = outline_st_page
        self.outline_end_page = outline_end_page
        self.document_st_page = document_st_page
        self.document_end_page = document_end_page
        self.index_st_page = index_st_page
        self.index_end_page = index_end_page
        
    
    def determin_title_page(self,textbook_list):
        # function: 提取所有章节的页码,确定书里各个章节的范围
        # input: 课程文本的dict。
        # return: list,表示章节所在的页码。
    
        # contents outline 在书第七页至第九页
        outline_pages_idx = list(range(self.outline_st_page,self.outline_end_page+1))
        res = []
        for outline_page in outline_pages_idx:
            outline = textbook_list['Pages'][outline_page]['text']    
            # 用正则表达式提取页码
            tmp = re.findall('(\d+.*\d*)\n',outline)
            # 用正则筛选后，还包括一些噪声，比如：错乱的章节关系。所以去除结果中的噪声
            res.extend([i for i in tmp if '.' not in i and i.isdigit()])
        #真正的页码是从第五个元素开始
        
        ### !!!!!!!!!res[4]这里要按照书籍做修改，要把4改成书籍对应的位置。
        start_position = 4
        page = [int(res[start_position])]
        current_value = int(res[start_position])
        # 这里是因为page:[1,2,3,4,1,15,15……],真正的页码是从1,15,15开始的。
        res = res[start_position:]
        for i in range(len(res)-1):
            #print('compare {} with {}'.format(current_value,int(res[i+1])))
            if current_value<=int(res[i+1]):
                #print('yes!')
                page.append(int(res[i+1]))
                current_value = int(res[i+1])
        print(page)
        return page

    def load_json(self,file_path):
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

    def match_outline_page(self,outlines,pages_number):
        # function: 筛选出outlines中的一级标签与二级标签，并且开头为数字的标签
        # input: 
        #   outlines: 用extract_outline提取的大纲
        #   pages_number: list。大纲对应的页码
        # return:
        #   result: dict。 分开存储大纲与页码的字典。一二级章节用层级形式存储。
        outlines = [outline[1] for outline in outlines if outline[0] <=2 and outline[1][0].isdigit()]
        if len(outlines) != len(pages_number):
            print('==============================\n')
            print('Warning: The length of extracted outlines number is inconsistent with that of pages_number list')
            print('==============================\n')
        result = {}
        for i in ['chapters','subchapters']:
            result[i] = {'chapter':[],'page':[]}
        for chapter,page in zip(outlines,pages_number):
            if '.' not in chapter:
                result['chapters']['chapter'].append(chapter)
                result['chapters']['page'].append(page)
            else:
                result['subchapters']['chapter'].append(chapter)
                result['subchapters']['page'].append(page)
        self.outline = result
        return result

    def parse_key_concept_page(self,textbook_list):
        # function: 解析textbook文本，提取出index部分的关键词及所在页码
        # input: textbook_list: 教材文本dict。
        # return: key_concept字典
        key_concept_dict = {}
        key_concept_index_page =  list(range(self.index_st_page,self.index_end_page+1,1))
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

    def find_word_page_from_text(self,word,textbook,frequency=True):
        # function: 给定一个单词，返回它在教材中出现的页码。
        # input:
        #   word: str。待查询单词。
        #   textbook: dict。 教材dict。
        #   frequency: bool。 取值为True表示一张页码内的单词按出现次数计数，
        #                     取值为False表示一张页码内重复出现的单词只计数一次。
        # returns: list。概念对应出现的页码。如：[1,1,4,5,6]。
        # statistical一书的列表中，第一页对应textbook[12],textbook[11:11+695]
        # 这里要根据书籍来调整。
        document_nums = self.document_end_page - self.document_st_page +1
        documents = textbook['Pages'][self.document_st_page:(self.document_st_page+document_nums)]
        if not frequency:
            is_in_pages = [word in x['text'] for x in documents]
            word_pages = np.arange(1,document_nums+1)[is_in_pages] 
        else:
            # '(' ,')'是正则表达式中的元字符，所以要把查询pattern中的'('替换为'\('
            word = word.replace('(','\(').replace(')','\)')
            word_pages_fre = [len(re.findall(word,x['text'])) for x in documents]
            word_pages = []
            for i,num in enumerate(word_pages_fre):
                word_pages.extend([i+1]*num)

        if type(word_pages) != list:
            word_pages = word_pages.tolist()
        return word_pages


    def find_single_word(self,word,key_concept_dict,outlines,textbook,use_index=True):
        # function: 给定一个单词及它出现过的页码，返回这个单词所在章节。
        # input: 
        #   word: str。单词
        #   key_concept_dict: dict。关键词字典。
        #   outlines: match_outline_page函数返回的大纲dict。
        #   use_index: 是否使用index页中的概念页码信息。
        #   textbook:
        # return: a dict。
        
        # 如果这个词在key_concept_dict(index)中，就取key_concept_dict[word]，否则
        # 从文本中做遍历，寻找这个词对应的页码
        is_key_word = word in key_concept_dict
        if is_key_word and use_index:
            word_page_list = key_concept_dict[word]
        else:
            word_page_list = self.find_word_page_from_text(word,textbook)
        
        if not word_page_list:
            return {'concept':word,'info':{'chapter':None,
                                           'subchapter':None,
                                           'page':list(word_page_list)}}
        
        else:
            #print(word)
            result = {'concept':word,'info':{'page':list(word_page_list)}}
            for i in ['chapters','subchapters']:
                chapter_pages = np.array(outlines[i]['page'])
                concept_chapters = np.zeros((len(word_page_list),),dtype=np.int)
                for j,word_page in enumerate(word_page_list):
                    concept_chapters[j] = np.argmax(chapter_pages>word_page)-1
                    #print('word_page:{}. chapter_page:{}'.format(word_page,chapter_pages[np.argmax(chapter_pages>word_page)-1]))
                concept_chapters[concept_chapters == -1] = len(chapter_pages)-1
                chapter_idx = np.argmax(np.bincount(concept_chapters))
                chapter = outlines[i]['chapter'][chapter_idx]
                result['info'].setdefault(i,chapter)
                
        return result


if __name__ == '__main__':
    bookname = 'StatisticalModels'
    # 生成一个TextBook类的示例，各页码参数由具体的书籍给出。
    textbook = TextBook(bookname,outline_st_page=6,outline_end_page=8,
                        document_st_page=12,document_end_page=706,
                        index_st_page=729,index_end_page=737)
    # 载入教科书解析完成的json文件。
    text_json = textbook.load_json(bookname+'.json')
    pages_number = textbook.determin_title_page(text_json)
    outlines = extract_outline(bookname+'.pdf')
    # 生成层级大纲词典。
    outlines = textbook.match_outline_page(outlines,pages_number)
    # 获取关键词
    key_concept_dict = textbook.parse_key_concept_page(text_json)
    # 返回关键词所在章节及页码
    key_chapter = []
    for concept in key_concept_dict.keys():
        key_chapter.append(textbook.find_single_word(concept,key_concept_dict,outlines,text_json,use_index=False))
    print(key_chapter[:5])
    with open('word_info_'+bookname+'.json','w') as outputf:
        json.dump(key_chapter,outputf)
    # determin_title_page('StatisticalModels.pdf')