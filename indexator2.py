from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
import sys

from helpers import conform_index, extractable 

# Verify the two arguments in the command line if not print some error message
if not len(sys.argv) == 2:
    print("Usage: python3 indexator.py some_file.pdf")
    sys.exit()

pdf_name = sys.argv[1]
try:
    with open(pdf_name, 'rb') as f:
        
        parser = PDFParser(f)
        pdf = PDFDocument(parser)
        extractable(pdf)
        
        
        # Search the index word
        index_result = conform_index(f, pdf, pdf_name)
        
except EnvironmentError: # parent of IOError, OSError *and* WindowsError where available
    print("The file doesn't exists")        
        
        

