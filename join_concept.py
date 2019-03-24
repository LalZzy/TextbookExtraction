# -*- coding: utf-8 -*-
import xlrd
import logging
logging.basicConfig(level=logging.INFO)
import sys
import os
from collections import defaultdict
import json

cpts_with_single_name = set()
cpts_with_multi_name = set()

class RawConceptDealer(object):
    def __init__(self):
        self.path = 'data/raw_concept/'

    def file_name_reader(self):
        import os
        filenames = [file for file in os.listdir(self.path) if '.xlsx' in file]
        logging.info('all files are: %s',','.join(filenames))
        return filenames

    def file_reader(self,file_name):
        data = xlrd.open_workbook(file_name)
        table = data.sheets()[0]
        data_list = []
        #import pdb;pdb.set_trace()
        for i in range(table.nrows):
            data_list.append(table.row_values(i))
        return data_list


    def deal_one_book(self,cpt_lists):
        # 把概念按照是否有多个名字分别存储。
        global cpts_with_single_name,cpts_with_multi_name
        one_name_output,multi_name_output = dict(),dict()
        textbooks = set()
        for cpt_list in cpt_lists:
            #import pdb;pdb.set_trace()
            concepts = [i for i in cpt_list if i]
            concepts = ','.join(concepts)
            concepts = concepts.lower().split(',')
            textbooks = textbooks.union(concepts)
            if len(concepts) == 1:
                cpts_with_single_name = cpts_with_single_name.union(concepts)
                one_name_output.setdefault(concepts[0], concepts)
            else:
                cpts_with_multi_name = cpts_with_multi_name.union(concepts)
                multi_name_output.setdefault(concepts[0],[])
                multi_name_output[concepts[0]].extend(concepts)
        return one_name_output,multi_name_output,list(textbooks)

    def drop_duplicates(self,output):
        global cpts_with_single_name,cpts_with_multi_name
        #import pdb;pdb.set_trace()

        for concept in list(output['concepts_one_name'].keys()):
            if concept in (cpts_with_multi_name & cpts_with_multi_name):
                output['concepts_one_name'].pop(concept)
        return output

    def write_json(self,output):
        concept_dict = output['concepts_one_name']
        concept_dict.update(output['concepts_multi_name'])
        with open(self.path+'all_concepts.json','w') as f:
            json.dump(concept_dict,f)
        with open(self.path+'concepts_in_textbooks.json', 'w') as g:
            json.dump(output['textbook'],g)
        logging.info('write concept to json file, total %d concepts'%len(concept_dict))
        return


    def run(self):
        file_names= self.file_name_reader()
        output = {'concepts_one_name':dict(),
                  'concepts_multi_name':dict(),
                  'textbook':dict()}
        for file_name in file_names:
            cpt_lists = self.file_reader(self.path+file_name)
            a,b,c = self.deal_one_book(cpt_lists)
            output['concepts_one_name'].update(a)
            output['concepts_multi_name'].update(b)
            output['textbook'].setdefault(file_name.replace('.xlsx',''),c)
            logging.info('concepts with one name: %d, with multi-name: %d'%(len(a.keys()),len(b.keys())))
            logging.info('deal %s done!'%file_name)
        logging.info('total %d concepts, before drop duplicate' % (
                    len(output['concepts_one_name']) + len(output['concepts_multi_name'])))
        logging.info('begin drop duplicated concept!')
        output = self.drop_duplicates(output)
        logging.info('total %d concepts, drop duplicate done!'%(len(output['concepts_one_name'])+len(output['concepts_multi_name'])))
        self.write_json(output)
        return output

def main():
    dealer = RawConceptDealer()
    concepts = dealer.run()
    #import pdb;pdb.set_trace()
    return concepts

if __name__ == '__main__':
    main()