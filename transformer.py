# -*- coding: utf-8 -*-

import json
import os
import logging
from collections import Counter
from datetime import datetime


class Transformer(object):
    def __init__(self,textbook_name, path):
        self.textbook_name = textbook_name
        self.path = path

    def trans_single_word(self,word_dict):
        #logging.info(word_dict)
        if word_dict['info']['page']:
            word_name = word_dict['concept']
            frequency = Counter(word_dict['info']['page'])
            return [(word_name,page,fre) for page,fre in frequency.items()]

    def store_output(self,output):
        with open(self.path + 'result_'+self.textbook_name.replace('.json','') +'.csv','w+', encoding = "utf-8") as f:
            for record in output:
                f.write(record[0]+','+str(record[1])+','+str(record[2])+'\r')

    def run(self,out_type = 'line',output = True):
        logging.info('start proccessing {}'.format(self.textbook_name))
        st = datetime.now()
        with open(self.path+self.textbook_name,'r') as json_file:
            text_book = json.load(json_file)
        res = []
        for word in text_book:
            #logging.info(word)
            if self.trans_single_word(word):
                res.extend(self.trans_single_word(word))
            if output == True:
                self.store_output(res)
        ed = datetime.now()
        logging.info('finish processing book {} in total {} seconds.'.format(self.textbook_name,(ed-st).total_seconds()))
        return res

def transform_all_json(textbooks,path):
    res = []
    for textbook in textbooks:
        transformer = Transformer(textbook,path)
        res.append(transformer.run(output=True))
    return res


def run():
    st = datetime.now()
    textbooks = os.listdir('data/concept_page/')
    textbooks = [i for i in textbooks if '.json' in i]
    logging.info(textbooks)
    result = transform_all_json(textbooks,'data/concept_page/')
    logging.info(result[0][0:5])
    ed = datetime.now()
    logging.info('cost total {} seconds'.format((ed-st).total_seconds()))




if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format=' %(asctime)s - %(levelname)s  %(filename)s,'
                           '[%(funcName)s] line:%(lineno)d output msg:  %(message)s')
    run()