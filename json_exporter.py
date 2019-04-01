# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 16:10:08 2018

@author: Travis
"""

# json_exporter.py
 
import json
import os
import re 

from miner_text_generator import extract_text_by_page
 
 
def export_as_json(pdf_path, json_path):
    filename = os.path.splitext(os.path.basename(pdf_path))[0]
    data = {'Filename': filename}
    data['Pages'] = []
 
    counter = 1
    for page in extract_text_by_page(pdf_path):
        text = re.sub("\x0c",' ',page)
        page = {'Page_number':counter ,'text': text.lower()}
        data['Pages'].append(page)
        counter += 1
 
    with open(json_path, 'w') as fh:
        json.dump(data, fh)


 
if __name__ == '__main__':
    pdf_path = 'StatisticalModels.pdf'
    json_path = 'StatisticalModels.json'
    export_as_json(pdf_path, json_path)