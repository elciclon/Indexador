import pdfplumber
import sys









# 

def select_pages(pages_ten_percent,pdf):
    numerated_pages = list(pdf.pages)
    half_pdf_pages = round(pages_ten_percent * 10 / 2)
    selected_pages = numerated_pages[half_pdf_pages:half_pdf_pages + 2]
    return selected_pages

 
        
    




    



    
    
