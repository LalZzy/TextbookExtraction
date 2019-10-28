# TextbookExtraction
Using pdfminer, a python library, to extract key concept from 9 books.

run scripts to install required packages.

required python version: python3

```shell
pip install -r requirement.txt
```

make sure the following things:

(1) directories exist:`"./data/` & `"./data/concept_page/"` & `"./data/textbook_txt/"` 

(2) everybook's key concepts' file exists: `"./data/concept_[bookname].xlsx"`

(3) everybook's pdf_file exists: `"./data/textbook_txt/[bookname].pdf"`


Then run

```shell
sh main.sh 
```




