import json
import subprocess
from pathlib import Path

import click

from .pdfinfo import get_pdf_info

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


def tex_add_pages(filename, pages: str, frame: bool = True, scale: float = 0.75, landscape: bool = False):
    return fr'\includepdf[pages={{{pages}}}, frame={frame}, scale={scale},landscape={landscape}]{{{filename}}}'


def tex_add_firstpage(filename, pages: str, frame: bool = True, scale: float = 0.75, landscape: bool = False):
    _a = filename.split(' ')
    _b = ' '.join(_a[1:])
    section_name = _b.replace(' ', r' \ ')[:-4]
    return fr'\includepdf[pages={{{pages}}}, frame={frame}, scale={scale},landscape={landscape},pagecommand=\section{{{section_name}}}]{{{filename}}} '


def tex_add_pdf(filepath):
    pdfinfo = get_pdf_info(filepath)
    filename = pdfinfo['filename']
    latex_cmd = f'% add {filename}\n'
    latex_cmd += r'\includepdfset{pagecommand={\thispagestyle{fancy}}}'
    page_break_list = pdfinfo['page_break_list']
    page_landscape = pdfinfo['page_landscape']
    for i in page_break_list:
        if i == '1':
            latex_cmd += '\n' + tex_add_firstpage(filename, '1', landscape=page_landscape[i])
        else:
            latex_cmd += '\n' + tex_add_pages(filename, pages=i, landscape=page_landscape[i])
    return latex_cmd


def total_tex_cmd():
    pdfs = get_pdf_files()
    if len(pdfs) == 0:
        raise Exception("当前目录下无PDF文件")
    latexcmd = ''
    for pdf in pdfs:
        latexcmd += tex_add_pdf(pdf) + '\n\n'
    return latexcmd


def generate_tex_file(papername):
    with open(template_file_path, 'r', encoding='utf-8') as f:
        tpl = f.read()
        a = tpl.replace('AAANAMEAAA', papername)
        content = total_tex_cmd()
        b = a.replace('AAACONTENTAAA', content)
        new_file_name = Path.joinpath(cwd, "{}.tex".format(papername))
        with open(new_file_name, 'w', encoding='utf-8') as newfile:
            newfile.write(b)


def init_project():
    project_info = {
        'papername': '',
        'files': [x.name for x in get_pdf_files()]
    }
    with open(packagejson_path, 'w', encoding='utf-8') as f:
        json.dump(project_info, f, indent=4, ensure_ascii=False)
    print(project_info)
    print("需要修改package.json中报告名称papername")


def get_project_info():
    if packagejson_path.exists():
        with open(packagejson_path, 'r', encoding='utf-8') as f:
            j = json.load(f)
            return j
    else:
        print("package.json not exist,creating an empty")
        init_project()
        return {'papername': '', 'files': []}


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
    click.echo("  files: {}".format(project_info['files']))


def buildpdf(papername):
    print(f"项目名称: {papername}")
    file_name = f"{papername}.tex"
    print(f">>> 生成tex文件: {file_name}", end=' ')
    generate_tex_file(papername)
    print("✓")
    print(">>> 使用xelatex编译", end=' ')
    cmd = ['xelatex', file_name]
    runcmd(cmd)  # 需要执行两次，生成目录 尝试用latexmk生成
    res = runcmd(cmd)
    print("✓")
    print(res.split("\n")[-3])
    print(">>> 清理文件")
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
@click.option('-y', 'y', is_flag=True)
def build(y):
    """Build pdf file"""
    project_info = get_project_info()
    show_info()
    if project_info['papername'] == '':
        print("报告名称为空")
        project_info['papername'] = input("请输入报告名称:")
    save_project_info(project_info)
    if not y:
        _y = input("是否现在编译PDF? (y/N) ")
        if _y == 'y':
            buildpdf(project_info['papername'])
        else:
            print("取消")
    else:
        buildpdf(project_info['papername'])


if __name__ == '__main__':
    cli()
