import re
import os
import time
from os.path import join
import sys
import argparse
import requests
from bs4 import BeautifulSoup
import json
from pdf2image import convert_from_bytes
from PyPDF2 import PdfReader
from PIL import Image, ImageDraw, ImageFont
import logging
import platform
import arxiv
from datetime import datetime, timedelta
from tqdm import tqdm
from typing import List
logging.basicConfig(level=logging.DEBUG)
client = arxiv.Client()

ROOT_DIR = ''
OVERWRITE_MARKDOWN = False
ARXIV_LATEST_PAPER_URL = 'https://arxiv.org/list/cs.CL/pastweek?show=500'  # 替换为你要爬取的url

def datetime_to_date_str(d: datetime):
    return d.strftime('%Y-%m-%d')


# 保留字母和数字
def remove_symbols(title):
    new_title = re.sub('[^a-zA-Z0-9 ]', ' ', title)
    return new_title


# 添加前导0
def add_leading_zeros(num):
    return str(num).zfill(3)


def convert_date_format(s):
    # 定义输入字符串的日期格式
    input_format = "%a, %d %b %Y"
    # 定义输出字符串的日期格式
    output_format = "%Y-%m-%d"
    
    # 将输入字符串转换为datetime对象
    date_obj = datetime.strptime(s, input_format)
    # 将datetime对象转换为指定格式的字符串
    converted_date = date_obj.strftime(output_format)
    
    return converted_date


# 判断 pdf 文件是否损坏
def is_pdf_file_corrupted(file_path):
    base_name = os.path.basename(file_path)
    try:
        with open(file_path, "rb") as file:
            reader = PdfReader(file)
            if len(reader.pages) > 0:  # 如果能读取到页数，说明文件没有损坏
                return False
    except Exception as e:
        print(f"file: {base_name[:80]} ... corrupted!\nException: {e}")
        return True  # 如果在尝试读取文件时抛出异常，说明文件可能已经损坏


def get_latest_n_date_strings(n=1):
    date_strings = []
    today = datetime.now().date()
    for i in range(n, -1, -1):
        date = today - timedelta(days=i)
        date_string = date.strftime('%Y-%m-%d')
        date_strings.append(date_string)
    return date_strings


def add_watermark(pdf_path, watermark_text):
    base_name: str = os.path.basename(pdf_path)
    root_dir = os.path.dirname(os.path.dirname(pdf_path))
    img_dir = join(root_dir, 'imgs')
    os.makedirs(img_dir, exist_ok=True)
    img_filename = base_name.replace('.pdf', '.jpg')

    image_abs_path = join(img_dir, img_filename)
    image_relative_path = f"./imgs/{img_filename}"

    if os.path.exists(image_abs_path):
        print(f"\nskip {image_abs_path} ...\n")
        return image_relative_path

    # 打开并读取PDF文件
    with open(pdf_path, "rb") as file:
        pdf_bytes = file.read()

    # 将PDF文件转换为图像
    images = convert_from_bytes(pdf_bytes)

    image = images[0]
    if not watermark_text:
        image.save(image_abs_path, 'JPEG')
        return image_relative_path
    
    width, height = image.size

    # 创建一个新的图片对象，大小与原图一致
    new_image = Image.new('RGB', (width, height + 50), (255, 255, 255))
    new_image.paste(image, (0, 0))

    # 在新图片上添加水印
    draw = ImageDraw.Draw(new_image)

    # 判断当前系统类型，选择字体
    if platform.system() == 'Windows':
        font = ImageFont.truetype('arial.ttf', 60)  # 使用Arial字体，字号为60
    elif platform.system() == 'Darwin':  # Mac
        font = ImageFont.truetype('/System/Library/Fonts/PingFang.ttc', 60)  # 使用Mac自带字体PingFang，字号为60
    else:
        raise Exception('Unsupported system type')

    text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_position = ((width - text_width) // 2, height - 60)
    draw.text(text_position, watermark_text, font=font, fill=(255, 0, 0))
    # 保存新图片
    new_image.save(image_abs_path, 'JPEG')
    
    return image_relative_path


def get_reponse(url):
    try:
        # print(f"url: {url}")
        response = requests.get(url)
        if response.status_code == 200:
            return response
        elif response.status_code == 500:
            return None
        else:
            raise Exception(f'Network is down, status code: {response.status_code}')
    except Exception as e:
        print(f"e: {e}, try proxy !")
        proxy = "http://127.0.0.1:7890"
        proxies = {
            'http': proxy,
            'https': proxy
        }
        try:
            response = requests.get(url, proxies=proxies)
            if response.status_code == 200:
                return response
            else:
                raise Exception(f"Network is down! Proxy {proxy} is unavaliable!")
        except:
            raise Exception(f"Network is down! Proxy {proxy} is unavaliable!")


def get_valid_title(title):
    title = remove_symbols(title)[:150]
    title = title[:150]
    title = ' '.join(title.split())
    title = title.replace(' ', '_')
    return title


# 将 content_list 追加到filename中
def append_file(filename, content_list, new_line=False):
    if not content_list:
        return
    if new_line:
        content_list = [text if text.endswith('\n') else text+'\n' for text in content_list]
    with open(filename, 'a+', encoding='utf-8') as f:
        f.writelines(content_list)
    return 0


def get_day_to_paper_list(latest_n=3):
    global ARXIV_LATEST_PAPER_URL
    day2papers = {}

    response = get_reponse(ARXIV_LATEST_PAPER_URL)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    dl_tags = soup.find_all('dl')[:latest_n]
    h3_date_tags = soup.find_all('h3')[:latest_n]

    for day_tag, day_paper_lst_tag in zip(h3_date_tags, dl_tags):
        day_date = day_tag.text.strip()
        day_date_str = convert_date_format(day_date)

        dt_tags = day_paper_lst_tag.find_all('dt')
        dd_tags = day_paper_lst_tag.find_all('dd')
        result = []
        for dt_tag, dd_tag in zip(dt_tags, dd_tags):
            a_tag = dt_tag.find('a', {'title': 'Abstract'})
            try:
                if a_tag:
                    arxiv_id = a_tag['href'].split('/')[-1]
                    
                    title_element = dd_tag.find('div', class_='list-title mathjax')
                    title = title_element.text.strip().replace('Title:', ' ').strip()

                    item = {'arxiv_id': arxiv_id, 'title': title}
                    result.append(item)
            except Exception as e:
                print('\n\n++++++++++++++++\n')
                print(e)
                print('\n\n')
                pass
        day2papers[day_date_str] = result
    return day2papers


def check_markdown_file(md_path):
    global OVERWRITE_MARKDOWN
    skip = False
    # 已存在并跳过
    if os.path.exists(md_path) and (not OVERWRITE_MARKDOWN):
        print(f'{date_str}.md already exists! Add --overwrite to rewrite! Skip this day!')
        skip = True
        return skip
    
    with open(md_path, 'w', encoding='utf-8') as fp: pass
    return skip


def do_paper_download(paper: arxiv.Result, pdf_dir, pdf_filename):
    status = 0
    max_try = 3
    pdf_abs_path = join(pdf_dir, pdf_filename)
    is_existed = os.path.exists(pdf_abs_path)
    is_file_corrupted = False
    if is_existed:
        is_file_corrupted = is_pdf_file_corrupted(pdf_abs_path)

    if (not is_existed) or (is_existed and is_file_corrupted):
        j = 0
        if is_file_corrupted:
            print(f"\n\nDownloading {pdf_filename} Again ...!\n\n")
        while j < max_try+1:
            try:
                paper.download_pdf(pdf_dir, pdf_filename)
                print(f"Download Done!\n\n")
                break
            except Exception as e:
                print(f"Download pdf exception: \n{e}\n")
            j += 1
            print(f"try {j} times ...")
            time.sleep(2)
            if j == max_try:
                status = -1
                return status
    else:
        print(f"Skip {pdf_filename} ...")
    return status


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--root_dir", type=str, required=True, help="root dir to place pdfs.")
    parser.add_argument("--days", type=int, default=3, help="get latest n days paper, deefault 3 days.")
    parser.add_argument("--overwrite", action='store_true', help='overwrite markdowns')
    args = parser.parse_args()

    ROOT_DIR = args.root_dir
    days = args.days
    OVERWRITE_MARKDOWN = True if args.overwrite else False

    cur_root_dir = join(ROOT_DIR, 'arxiv_papers')
    os.makedirs(cur_root_dir, exist_ok=True)
    # cur_dir = f"{CUR_ROOT_DIR}/{date_str}"

    day2papers = get_day_to_paper_list(latest_n=days)

    for date_str, papers in day2papers.items():
        print()
        print(f"day: {date_str}")
        print()
        cur_dir = join(cur_root_dir, date_str)
        os.makedirs(cur_dir, exist_ok=True)

        md_path = join(cur_dir, f'arxiv_{date_str}.md')
        skip = check_markdown_file(md_path)
        if skip: continue

        total = len(papers)
        arxiv_id_lst = [p['arxiv_id'] for p in papers]

        result_lst = client.results(arxiv.Search(id_list=arxiv_id_lst))

        for j, (d, paper) in enumerate(zip(papers, result_lst)):
            index = j + 1
            
            print(f"index: {index}/{total}  {date_str}")
            arxiv_id = d['arxiv_id']
            title = d['title']
            # print(d)

            print(f"\n\nDownloading {date_str} {index}/{total} {arxiv_id}   {title}\n\n")
            
            truncated_title = get_valid_title(title)
            authors= [a.name for a in paper.authors]
            authors_str = ', '.join(authors)
            pdf_url = paper.pdf_url[:-2]
            comment = paper.comment
            # updated_date = datetime_to_date_str(paper.updated)
            # published_date = datetime_to_date_str(paper.published)
            # paper.download_pdf(dirpath="./mydir")
            pdf_dir = join(cur_dir, 'pdfs')
            os.makedirs(pdf_dir, exist_ok=True)
            index = add_leading_zeros(index)
            pdf_filename = f'{date_str}_{index}__{arxiv_id}__{truncated_title}.pdf'
            pdf_relative_path = f'./pdfs/{pdf_filename}'
            pdf_abs_path = join(pdf_dir, pdf_filename)

            status = do_paper_download(paper, pdf_dir, pdf_filename)

            md_block = []
            md_block.append(f"## 【{j+1}】{title}\n")
            md_block.append(f"- arXiv id: {arxiv_id}\n")
            md_block.append(f"- PDF LINK: {pdf_url}\n")
            md_block.append(f"- authors: {authors_str}\n")
            md_block.append(f"- comments: {comment}\n")
            # 下载正常
            if status == 0:
                img_relative_path = add_watermark(pdf_abs_path, watermark_text=comment)
                md_block.append(f"- [PDF FILE]({pdf_relative_path})\n\n")
                md_block.append(f"![fisrt page]({img_relative_path})\n\n\n")
            
            append_file(md_path, md_block)
        print(f"\n\nDay: {date_str} done!\n\n")