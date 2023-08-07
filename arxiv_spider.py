import re
import os
import requests
from bs4 import BeautifulSoup
import json
from pdf2image import convert_from_bytes
from PIL import Image
from datetime import datetime
from tqdm import tqdm

def remove_symbols(title):
    new_title = re.sub('[^a-zA-Z ]', ' ', title)
    return new_title

def get_formatted_date():
    # 获取当前日期
    current_date = datetime.now()

    # 将日期格式化成 YYYY-MM-DD 格式的字符串
    formatted_date = current_date.strftime("%Y-%m-%d")

    return formatted_date


def download_pdf_image(url, title):
    # 保存第一页图片
    date_str = get_formatted_date()
    title = remove_symbols(title)
    os.makedirs(f'./{date_str}/', exist_ok=True)
    path = f'{date_str}/{date_str}_{title}.png'

    if os.path.exists(path):
        return

    # 下载PDF文件
    response = requests.get(url)

    # 将PDF文件转换为图片
    images = convert_from_bytes(response.content)

    # 获取第一页图片
    first_page = images[0]
    first_page.save(path, 'PNG')


def crawl_html(url):
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    dl_tags = soup.find_all('dl')
    if len(dl_tags) > 0:
        dl_tag = dl_tags[0]
        dt_tags = dl_tag.find_all('dt')
        dd_tags = dl_tag.find_all('dd')
        result = []
        for dt_tag, dd_tag in zip(dt_tags, dd_tags):
            a_tag = dt_tag.find('a', {'title': 'Abstract'})
            if a_tag:
                arxiv_id = a_tag['href'].split('/')[-1]
                title_element = dd_tag.find('div', class_='list-title mathjax')
                title = title_element.text.strip().replace('Title:', ' ').strip()
                # https://arxiv.org /pdf/2308.02482  .pdf
                # /pdf/2308.02482
                pdf_link = dt_tag.find('a', {'title': 'Download PDF'})['href']
                pdf_link = f"https://arxiv.org{pdf_link}.pdf"
                result.append({'arxiv_id': arxiv_id, 'title': title, 'pdf_link': pdf_link})
        return result
    else:
        return None

url = 'https://arxiv.org/list/cs.CL/pastweek?show=500'  # 替换为你要爬取的url
result = crawl_html(url)

date_str = get_formatted_date()
os.makedirs(f'./{date_str}/', exist_ok=True)


# 保存结果到文件
json_path = f'./{date_str}/arxiv_{date_str}.json'
with open(json_path, 'w', encoding='utf-8') as file:
    json.dump(result, file, ensure_ascii=False, indent=2)


total = len(result)
for i, js in tqdm(enumerate(result)):
    title = js['title']
    arxiv_id = js['arxiv_id']
    pdf_link = js['pdf_link']
    print(f"processing {i+1}/{total} {title} ...")
    download_pdf_image(pdf_link, title)

print('\n\ndone!!!')