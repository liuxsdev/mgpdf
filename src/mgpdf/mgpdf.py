import subprocess
from pathlib import Path

cwd = Path.cwd()
pyfile_dict = Path(__file__).parent
template_file_path = Path.joinpath(pyfile_dict, 'template.tex')


def get_pdf_files():
    p = Path(cwd)
    return list(p.glob('[1234567890]*.pdf'))


def clean_file():
    p = Path(cwd)
    aux_file = list(p.glob('*.aux'))
    log_file = list(p.glob('*.log'))
    out_file = list(p.glob('*.out'))
    toc_file = list(p.glob('*.toc'))
    clean_list = aux_file + log_file + out_file + toc_file
    for p in clean_list:
        p.unlink()


def runcmd(command):
    ret = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
    if ret.returncode == 0:
        resa = ret.stdout
    else:
        resa = ret.stderr
    return resa


#  #1:file name 2:section name 3:landscape 4:scale 5:frame
def add_pdf_tex_cmd(filename: str, landscape: bool = False, scale: float = 0.75, frame: bool = True):
    a_ = filename.split(' ')
    b_ = ' '.join(a_[1:])
    section_name = b_.replace(' ', r' \ ')[:-4]
    c_ = fr'\addpdf{{{filename}}}{{{section_name}}}{{{landscape}}}{{{scale}}}{{{frame}}}'
    return c_


def total_tex_cmd():
    pdfs = get_pdf_files()
    latexcmd = ''
    for pdf in pdfs:
        latexcmd += add_pdf_tex_cmd(pdf.name) + '\n'
    return latexcmd


def replace_template(papername):
    with open(template_file_path, 'r', encoding='utf-8') as f:
        tpl = f.read()
        a = tpl.replace('AAANAMEAAA', papername)
        content = total_tex_cmd()
        b = a.replace('AAACONTENTAAA', content)
        new_file_name = Path.joinpath(cwd, "{}-附件.tex".format(papername))
        with open(new_file_name, 'w', encoding='utf-8') as newfile:
            newfile.write(b)


if __name__ == '__main__':
    name = 'example'
    print(f"项目名称{name}")
    file_name = "{}-附件.tex".format(name)
    replace_template(name)
    print(f">>> 生成tex文件 : run xelatex {file_name}")
    cmd = ['xelatex', file_name]
    res = runcmd(cmd)
    print(res.split("\n")[-3])
    print(">>> 清理生成文件")
    clean_file()
