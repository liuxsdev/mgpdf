from collections import Counter

from PyPDF2 import PdfReader


def get_pdf_pagenumber(pdfpath):
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
    """
    参考：https://stackoverflow.com/questions/37424416/how-to-get-pdf-orientation-using-pypdf2
    媒体框（media box）定义将用于印刷页面的物理介质的边界。
    旋转属性会覆盖mediaBox的设置，因此需要结合旋转属性进行判断：
    当 宽 > 高，并且不旋转或旋转180度的情况下，判断页面为横向Landscpae，否则为正常竖向
    当 宽 < 高，并且不旋转或旋转180度的情况下，页面为正常竖向，否则则是经过旋转，最终页面呈现效果是横向
    """
    deg = pdf_page.get("/Rotate")
    mediabox = pdf_page.mediabox
    width, height = mediabox.upper_right
    if width > height:
        if deg in [0, 180, None]:
            return True
        else:
            return False
    else:
        if deg in [0, 180, None]:
            return False
        else:
            return True


def get_pdf_info(pdfpath):
    filename = pdfpath.name
    reader = PdfReader(pdfpath)
    page_number = len(reader.pages)
    landscape = [page_is_landscape(page) for page in reader.pages]
    count_landscape = Counter(landscape)
    landscape_pages_num = count_landscape[True]
    page_break_list = page_break(landscape)
    page_landscape = {}
    for i in page_break_list:
        _num = int(i.split('-')[0]) - 1
        page_landscape[i] = landscape[_num]
    return {
        'filename': filename,
        'page_number': page_number,
        'landscape_pages_num': landscape_pages_num,
        'page_break_list': page_break_list,
        'page_landscape': page_landscape,
        'landscape': landscape
    }


def page_break(page_list):
    page_break_list = ['1']
    mark_all = []
    start = 1
    mark = [start]
    number_of_page_list = len(page_list)
    if number_of_page_list == 2:
        return ['1', '2']
    for i in range(1, number_of_page_list):
        if start == number_of_page_list - 2:
            # print("特殊处理{}".format(start))
            if page_list[start] == page_list[start + 1]:
                start += 1
                mark.append(start)
                mark_all.append(mark)
                break
            else:
                end = start + 1
                mark.append(end - 1)
                mark_all.append(mark)
                start = end
                mark = [start, end]
                mark_all.append(mark)
                break
        else:
            if page_list[start] == page_list[start + 1]:
                start += 1
            else:
                end = start + 1
                mark.append(end - 1)
                mark_all.append(mark)
                start = end
                mark = [start]
    # print(mark_all)
    for p in mark_all:
        if p[0] == p[1]:
            page_break_list.append('{}'.format(p[0] + 1))
        else:
            page_break_list.append('{}-{}'.format(p[0] + 1, p[1] + 1))
    return page_break_list
