# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 15:37:35 2018

@author: Travis
"""

# miner_text_generator.py
 
import io
 
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams
import re
def extract_text_by_page(pdf_path):
    with open(pdf_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh, 
                                      caching=True,
                                      check_extractable=True):
            resource_manager = PDFResourceManager()
            fake_file_handle = io.StringIO()
            #保留原文件中的空格
            laparams = LAParams()
            converter = TextConverter(resource_manager, fake_file_handle, laparams = laparams)
            page_interpreter = PDFPageInterpreter(resource_manager, converter)
            page_interpreter.process_page(page)
 
            text = fake_file_handle.getvalue()
            yield text
 
            # close open handles
            converter.close()
            fake_file_handle.close()
 
def extract_text(pdf_path):
    result = []
    for page in extract_text_by_page(pdf_path):
        result.append(re.sub("\x0c",' ',page))
    return result

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
# Open a PDF document.
def extract_outline(pdf_path):
    fp = open(pdf_path, 'rb')
    parser = PDFParser(fp)
    document = PDFDocument(parser)
    # Get the outlines of the document.
    outlines = document.get_outlines()
    #print(list(outlines))
    result = [(level,title) for (level,title,dest,a,se) in outlines]
    return result
        
if __name__ == '__main__':
    result = extract_text('StatisticalModels.pdf')
    outline = extract_outline('StatisticalModels.pdf')
    # 有内容丢失现象，举例：
    print(result[6])
    #print(outline)   
    #print(result)