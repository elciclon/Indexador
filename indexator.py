#!/home/adrian/anaconda3/bin/python3

import sys
import pdfplumber
import unidecode
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from helpers import *
from operator import itemgetter
from PyPDF2 import PdfFileReader, PdfFileWriter

def main():
    # Verify the two arguments in the command line if not print some error message
    if not len(sys.argv) == 2:
        print("Usage: python3 indexator.py some_file.pdf")
        sys.exit()

    pdf_name = sys.argv[1]
    try:
        with pdfplumber.open(pdf_name) as pdf:
            pdf_lenght = len(pdf.pages)
            pages_ten_percent = round(pdf_lenght * .1)
            selected_pages = select_pages(pages_ten_percent,pdf)
            
            index = ['indice'] 
            index_pages_word_wordindex = conform_index(pdf, pages_ten_percent, index)
            
            stats = conform_stats(selected_pages)
            index_pages = index_pages_word_wordindex[0]
            word = index_pages_word_wordindex[1][1]
            wordindex = index_pages_word_wordindex[1][2]
            total_lines = []
            for page in index_pages:
                lines = list_conform(pdf.pages[page])
                lines = remove_spaces(lines)
                lines = remove_empty_items(lines, word)
                del lines[0]
                total_lines += lines

            pdf_indexed = copy_pdf(pdf_name)
            pdf_indexed = insert_index_outline(pdf_indexed, index[wordindex], index_pages[0])
            
            page_being_ckecked_number = index_pages[-1] + 1
            
            for line in total_lines:

                while page_being_ckecked_number <= pdf_lenght:
                    cursor = 0
                
                    page_with_line = check_if_line_in_page(line, pdf, page_being_ckecked_number)
                    
                    if page_with_line:    

                        page_being_ckecked_number = page_with_line
                        page_cursor_sorted_stats = [page_with_line, cursor, stats]
                        if compare_at_char_level(pdf, line, page_cursor_sorted_stats):
                            add_outlines(line,pdf_indexed,page_with_line)
                            break
                        else:
                            page_being_ckecked_number += 1   
                    else:
                        print("WARNING: " + line.capitalize() + " --not found--")                    
                        break         
                
                    
                
            write_indexed(pdf_name, pdf_indexed)                        

    except EnvironmentError: # parent of IOError, OSError *and* WindowsError where available
        print("The file doesn't exists")        

def conform_stats(selected_pages):  
    stats =[[selected_pages[0].chars[0], 1]]
    for page in selected_pages:
        for char in page.chars:
            found = False
            font_type = char['fontname'] + str(char['size'])
            for font in stats:
                if font_type == font[0]:
                    font[1] += 1
                    found = True
                    break

            if not found:                    
                stats.append([font_type, 1])
    
    number_of_fonts_to_check = round(len(stats) * .1)
    sorted_stats = sorted(stats, key=itemgetter(1), reverse=True)
    sorted_stats = sorted_stats[:number_of_fonts_to_check]

    return sorted_stats       

def insert_index_outline(pdf_indexed, index, index_result):
    parent = pdf_indexed.addBookmark('Index', 0) # add parent bookmark
    pdf_indexed.addBookmark(str(index).capitalize(), index_result, parent)
    return pdf_indexed

def remove_spaces(lines):
    no_space_lines =[]
    for line in lines:
        line = line.rstrip().lower()
        no_space_lines.append(line)
    proc_lines = []    
    for item in no_space_lines:
        res = "".join(filter(lambda x: not x.isdigit() and not x == '.', item)) 
        res = res.lstrip().rstrip()
        res = res.replace("nota  – ", "")
        proc_lines.append(res)
        
    return proc_lines

def list_conform(page):
    lines = page.extract_text(x_tolerance=3, y_tolerance=3).splitlines()
    return lines
    
def is_word_in_text(index, text):
    for i, word in enumerate(index):
        if word in text:
            word_packed = [True, word, i]
            return word_packed
    return False

def remove_empty_items(lines, index):
    i = 0
    flag = False
    while not flag: 
        if not index in unidecode.unidecode(lines[i].lower()):
            i += 1
        else:
            flag = True    
    del lines[:i]
    lines = list(filter(None, lines)) 
    return lines

def conform_index(pdf,pages_ten_percent, index):
    blank_pages = 0
    for page_number, page in enumerate(pdf.pages):
        text = page.extract_text(x_tolerance=3, y_tolerance=3)
        if text == None:
            page_number += 1
            blank_pages += 1
            if blank_pages > 2:
                sys.exit("Sorry, cannot process images")
        else:
            text = unidecode.unidecode(text).lower()
            word_packed = is_word_in_text(index, text)
            if not word_packed:
                page_number += 1  
                if page_number > pages_ten_percent:
                    sys.exit("Sorry, index not found")
            else:
                print("Index found on page " + str(page_number + 1))
                page_with_index = [page_number]
                flag = True
                while flag:
                    page_number += 1 
                    text = unidecode.unidecode(pdf.pages[page_number].extract_text(x_tolerance=3, y_tolerance=3).lower())
                    index_continuation = ["cont."]
                    if is_word_in_text(index_continuation, text):
                        page_with_index.append(page_number)
                    else:
                        flag = False    

                index_pages_word_wordindex = [page_with_index, word_packed] 
                
                return index_pages_word_wordindex

def write_indexed(pdf_name, pdf_indexed):
    indexed_pdf_name = pdf_name[:-4] + '_indexed.pdf'
    resultPdf = open(indexed_pdf_name, 'wb')
    pdf_indexed.write(resultPdf)
    resultPdf.close()
    sys.exit("Done!")

def check_if_line_in_page(line, pdf, page_being_checked_number):
    line_found = False
    max_pages_to_check = len(pdf.pages)
    while not line_found:
        text = unidecode.unidecode(pdf.pages[page_being_checked_number].extract_text(x_tolerance=3, y_tolerance=3).lower())
        if unidecode.unidecode(line) in text:
            line_found = True
        else:
            page_being_checked_number += 1
            if page_being_checked_number == max_pages_to_check:
                return False
            
    return page_being_checked_number
            
def add_outlines(line,pdf_indexed,page_with_line):
    line = line.capitalize()
    print("Adding outline: " + line)
    pdf_indexed.addBookmark(line, page_with_line)

def compare_at_char_level(pdf, line, page_and_cursor):
    page_with_line = page_and_cursor[0]
    cursor = page_and_cursor[1]
    sorted_stats = page_and_cursor[2]
    chars_in_page = len(pdf.pages[page_with_line].chars)
    line_lenght = len(line)
    page_info = [pdf.pages[page_with_line], chars_in_page]
    line_info = [line, line_lenght]
    while cursor + line_lenght < chars_in_page:
        cursor = get_matching(page_info, line_info, cursor)
        if not cursor:
            return False
        if is_end_of_page_reached(line_lenght, chars_in_page, cursor):
            return False
        line_comparable = conform_line_comparable(pdf.pages[page_with_line], cursor, line_lenght)
        if line_comparable == unidecode.unidecode(line) and compare_fonts(sorted_stats, pdf.pages[page_with_line], cursor):
                return True
        else:
            cursor += 1

    return False        

def get_matching(page_info, line_info, cursor):
    while True:
        if unidecode.unidecode((page_info[0].chars[cursor]['text']).lower()) != line_info[0][0]:
            cursor += 1
            if is_end_of_page_reached(line_info[1], page_info[1], cursor):
                return False
        elif unidecode.unidecode((page_info[0].chars[cursor + 1]['text']).lower()) == line_info[0][1]:
            return cursor    
        else:
            cursor += 1    

def is_end_of_page_reached(line_lenght, chars_in_page, cursor):
    if cursor + line_lenght > chars_in_page:
        return True
    else:
        return False


def conform_line_comparable(page, cursor, line_lenght):
    line_comparable = ''
    for i in range(line_lenght):
        line_comparable += unidecode.unidecode(page.chars[cursor + i]['text'].lower())
    return line_comparable

def compare_fonts(stats, page, cursor):
    if page.chars[cursor]['fontname'] + str(page.chars[cursor]['size']) in stats[0]:
        return False
    else:
        return True
        
def copy_pdf(pdf_name):
    pdf_to_index = PdfFileReader(pdf_name)
    pdf_indexed = PdfFileWriter()
    pdf_indexed.cloneDocumentFromReader(pdf_to_index)
    return pdf_indexed


if __name__ == '__main__':
    main()
