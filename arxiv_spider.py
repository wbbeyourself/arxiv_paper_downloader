import re
import os
import requests
from bs4 import BeautifulSoup
import json
from pdf2image import convert_from_bytes
from PIL import Image
from datetime import datetime
from tqdm import tqdm

url = 'https://arxiv.org/list/cs.CL/pastweek?show=500'  # 替换为你要爬取的url

def remove_symbols(title):
    new_title = re.sub('[^a-zA-Z ]', ' ', title)
    return new_title


# def get_formatted_date():
#     # 获取当前日期
#     current_date = datetime.now()

#     # 将日期格式化成 YYYY-MM-DD 格式的字符串
#     formatted_date = current_date.strftime("%Y-%m-%d")

#     return formatted_date


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


def get_latest_date(url):
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    
    # 找到第一个 h3 标签并提取文本
    first_h3 = soup.find('h3')
    latest_date = first_h3.text.strip()
    final_date = convert_date_format(latest_date)
    # print(f'latest_date: {latest_date}\n\nfinal_date: {final_date}')
    print(final_date)
    return final_date

date_str = get_latest_date(url)
cur_dir = f"./arxiv_papers/{date_str}/"
os.makedirs(cur_dir, exist_ok=True)

def download_pdf_image(url, title):
    global cur_dir
    global date_str
    # 保存前2页图片
    title = remove_symbols(title)
    path = f'{cur_dir}{date_str}_{title}_1.jpg'

    if os.path.exists(path):
        return

    # 下载PDF文件
    response = requests.get(url)

    # 将PDF文件转换为图片
    images = convert_from_bytes(response.content)

    # 获取第一页图片
    first_page = images[0]
    first_page.save(path, 'JPEG')

    path = f'{cur_dir}{date_str}_{title}_2.jpg'
    second_page = images[1]
    second_page.save(path, 'JPEG')


def crawl_html(url):
    global date_str
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
                result.append({'arxiv_id': arxiv_id, 'title': title, 'pdf_link': pdf_link, 'date': date_str})
        return result
    else:
        return None


result = crawl_html(url)

# 保存结果到文件
json_path = f'{cur_dir}arxiv_{date_str}.json'
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
print(date_str)