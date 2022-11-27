from PyPDF2 import PdfReader


def get_pdffile_pagenumber(pdfpath):
    reader = PdfReader(pdfpath)
    return len(reader.pages)


def get_page_size(pdf_page):
    """get pdf pages size in millimeters"""
    """https://stackoverflow.com/questions/46232984/how-to-get-pdf-file-metadata-page-size-using-python"""
    width = float(pdf_page.mediabox.width) * 25.4 / 72
    height = float(pdf_page.mediabox.height) * 25.4 / 72
    return width, height


def page_is_landscape(pdf_page):
    """return if the pdf page is landscape"""
    width, height = get_page_size(pdf_page)
    return width > height
