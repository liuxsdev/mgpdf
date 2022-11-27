import json
import subprocess
from pathlib import Path

import click

from pdfinfo import get_pdffile_pagenumber

cwd = Path.cwd()
packagejson_path = Path.joinpath(cwd, 'package.json')
pyfile_dict = Path(__file__).parent
template_file_path = Path.joinpath(pyfile_dict, 'template.tex')


def get_pdf_files():
    p = Path(cwd)
    return list(p.glob('[1234567890]*.pdf'))


def clean_file():
    aux_file = list(cwd.glob('*.aux'))
    log_file = list(cwd.glob('*.log'))
    out_file = list(cwd.glob('*.out'))
    toc_file = list(cwd.glob('*.toc'))
    clean_list = aux_file + log_file + out_file + toc_file
    for p in clean_list:
        p.unlink()


def runcmd(command):
    ret = subprocess.run(command, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, encoding="utf-8")
    if ret.returncode == 0:
        resa = ret.stdout
    else:
        resa = ret.stderr
    return resa


#  #1:file name 2:section name 3:landscape 4:scale 5:frame
def addpdf_tex_cmd(filepath, landscape: bool = False, scale: float = 0.75, frame: bool = True):
    filename = filepath.name
    a_ = filename.split(' ')
    b_ = ' '.join(a_[1:])
    section_name = b_.replace(' ', r' \ ')[:-4]
    page_number = get_pdffile_pagenumber(filepath)
    if page_number >= 2:
        c_ = fr'\addpdf{{{filename}}}{{{section_name}}}{{{landscape}}}{{{scale}}}{{{frame}}}'
    else:
        c_ = fr'\addonepdf{{{filename}}}{{{section_name}}}{{{landscape}}}{{{scale}}}{{{frame}}}'
    return c_


def total_tex_cmd():
    pdfs = get_pdf_files()
    latexcmd = ''
    for pdf in pdfs:
        latexcmd += addpdf_tex_cmd(pdf) + '\n'
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


def init_project():
    project_info = {
        'papername': ''
    }
    # outputdir,pdffiles(name,pages,landscape)
    with open(packagejson_path, 'w', encoding='utf-8') as f:
        json.dump(project_info, f, indent=4, ensure_ascii=False)
    print(project_info)


def get_project_info():
    if packagejson_path.exists():
        with open(packagejson_path, 'r', encoding='utf-8') as f:
            j = json.load(f)
            return j
    else:
        print("package.json not exist,creating an empty")
        init_project()
        return {'papername': ''}


def save_project_info(project_info):
    with open(packagejson_path, 'w', encoding='utf-8') as f:
        json.dump(project_info, f, indent=4, ensure_ascii=False)


def show_info():
    click.echo(click.style('Project Info:', fg='yellow'))
    click.echo(f"当前目录: {cwd}")
    click.echo(f"tex文件目录: {template_file_path}")
    project_info = get_project_info()
    click.echo(f"项目信息: ")
    click.echo("  papername: {}".format(project_info['papername']))


def buildpdf(papername):
    print(f"项目名称: {papername}")
    file_name = f"{papername}-附件.tex"
    replace_template(papername)
    print(f">>> 生成tex文件: run xelatex {file_name}")
    cmd = ['xelatex', file_name]
    runcmd(cmd)  # 需要执行两次，生成目录 尝试用latexmk生成
    res = runcmd(cmd)
    print(res.split("\n")[-3])
    print(">>> 清理生成文件")
    clean_file()
    print(">>> 完成")


@click.group()
def cli():
    pass


@cli.command()
def init():
    """Init Project"""
    click.echo(click.style(f"Init Project", fg='yellow'))
    init_project()


@cli.command()
def info():
    """Show project info"""
    show_info()


@cli.command()
def build():
    """Build pdf file"""
    project_info = get_project_info()
    if project_info['papername'] == '':
        print("empty name")
        project_info['papername'] = input("input papername:")
    save_project_info(project_info)
    print(project_info['papername'])
    buildpdf(project_info['papername'])


if __name__ == '__main__':
    cli()
