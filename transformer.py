# -*- coding: utf-8 -*-

import json
import os
import logging
from collections import Counter



class Transformer(object):
    def __init__(self,textbook_name):
        self.textbook_name = textbook_name

    def trans_single_word(self,word_dict):
        #logging.info(word_dict)
        if word_dict['info']['page']:
            word_name = word_dict['concept']
            frequency = Counter(word_dict['info']['page'])
            return [(word_name,page,fre) for page,fre in frequency.items()]

    def store_output(self,output):
        with open('data/result/result_'+self.textbook_name.replace('.json','') +'.csv','w+') as f:
            for record in output:
                f.write(record[0]+','+str(record[1])+','+str(record[2])+'\r')

    def run(self,out_type = 'line',output = True):
        logging.info('proccessing {}'.format(self.textbook_name))
        with open('data/'+self.textbook_name,'r') as json_file:
            text_book = json.load(json_file)
        res = []
        for word in text_book:
            #logging.info(word)
            if self.trans_single_word(word):
                res.extend(self.trans_single_word(word))
            if output == True:
                self.store_output(res)
        return res

def transform_all_json(textbooks):
    res = []
    for textbook in textbooks[0:1]:
        transformer = Transformer(textbook)
        res.append(transformer.run())
    return res


def run():
    textbooks = os.listdir('data')
    textbooks = [i for i in textbooks if '.json' in i]
    logging.info(textbooks)
    result = transform_all_json(textbooks)
    logging.info(result[0][0:5])




if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format=' %(asctime)s - %(levelname)s  %(filename)s,'
                           '[%(funcName)s] line:%(lineno)d output msg:  %(message)s')
    run()