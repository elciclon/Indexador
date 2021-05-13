import pdfplumber

with pdfplumber.open("test.pdf") as pdf:
    print(len(pdf.pages))    
