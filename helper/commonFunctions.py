import re

def cleanNonASCII(text):

    text2= re.sub(r'[^\x00-\x7F]','', text)
    text2= re.sub(r'[\\]',' ', text)

    return text2
