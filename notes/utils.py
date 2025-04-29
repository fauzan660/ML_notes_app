from pypdf import PdfReader
from io import StringIO
from pdfminer.high_level import extract_text, extract_text_to_fp
from .preprocessing import preprocess_text

def read_pdf(pdf_file):
# creating a pdf reader object
    # reader = PdfReader(pdf_file)

    # # printing number of pages in pdf file
    # print(len(reader.pages))

    # # getting a specific page from the pdf file
    # page = reader.pages[0]

    # # extracting text from page
    # text = page.extract_text()
    # print(text)
    output_string = StringIO()
    extract_text_to_fp(pdf_file, output_string)
    return (preprocess_text(output_string.getvalue().strip()))