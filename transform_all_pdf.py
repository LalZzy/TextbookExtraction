# -*- coding: utf-8 -*-
import sys
import os
import logging
logging.basicConfig(level=logging.WARNING)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(sys.path)
from TextbookExtraction.miner_text_generator import extract_text_by_page

if __name__ == '__main__':
    pdf_path = 'data/textbook_txt'
    out_txt_path = 'data/textbook_txt/result'
    all_pdfs = [file for file in os.listdir(pdf_path) if '.pdf' in file]
    logging.warning('total {} files.'.format(len(all_pdfs)))
    for pdf in all_pdfs:
        logging.warning('{} begin!'.format(pdf))
        try:
            text_list = extract_text_by_page('{}/{}'.format(pdf_path,pdf))
            #import pdb;pdb.set_trace()
            #text_list = ['1','2','3']
            output = '\n'.join(text_list)
            with open('{}/{}'.format(out_txt_path,pdf.replace('pdf','txt')),'w+') as fp:
                fp.write(output)
            logging.warning('{} finished'.format(pdf))
        except Exception as e:
            logging.error('{} failed.{}'.format(pdf,e))
