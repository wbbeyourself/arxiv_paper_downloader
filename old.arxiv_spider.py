import re
import os
import sys
import requests
from bs4 import BeautifulSoup
import json
from pdf2image import convert_from_bytes
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from tqdm import tqdm

url = 'https://arxiv.org/list/cs.CL/pastweek?show=500'  # 替换为你要爬取的url


# 保留字母和数字
def remove_symbols(title):
    new_title = re.sub('[^a-zA-Z0-9 ]', ' ', title)
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



def get_latest_date(url):
    response = get_reponse(url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    
    # 找到第一个 h3 标签并提取文本
    first_h3 = soup.find('h3')
    latest_date = first_h3.text.strip()
    final_date = convert_date_format(latest_date)
    # print(f'latest_date: {latest_date}\n\nfinal_date: {final_date}')
    print(final_date)
    return final_date

ROOT_DIR = sys.argv[1]
overwrite = False
if len(sys.argv) >= 3:
    flag_overwrite = sys.argv[2]
    if flag_overwrite == '--overwrite':
        overwrite = True
    else:
        print(f"Error: invalid args: {sys.argv[1:]}\n")
        print(f"Usage: python {__file__} /paper/target/path [--overwrite]\n")
        sys.exit(-1)

date_str = get_latest_date(url)
cur_dir = f"{ROOT_DIR}/arxiv_papers/{date_str}"
os.makedirs(cur_dir, exist_ok=True)


import platform

def add_watermark(image_path, watermark_text):
    image = Image.open(image_path)
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
    new_image.save(image_path)


# 添加前导0
def add_leading_zeros(num):
    return str(num).zfill(3)


def download_pdf_image(url, title, arxiv_id, watermark_text, index):
    global cur_dir
    global date_str
    
    index = add_leading_zeros(index)

    pdf_root = f'{cur_dir}/pdfs'
    img_root = f'{cur_dir}/imgs'
    os.makedirs(pdf_root, exist_ok=True)
    os.makedirs(img_root, exist_ok=True)

    pdf_path = f'{cur_dir}/pdfs/{date_str}_{index}__{arxiv_id}__{title}.pdf'
    pdf_relative_path = f'./pdfs/{date_str}_{index}__{arxiv_id}__{title}.pdf'
    img_path = f'{cur_dir}/imgs/{date_str}_{index}__{arxiv_id}__{title}.jpg'
    img_relative_path = f'./imgs/{date_str}_{index}__{arxiv_id}__{title}.jpg'

    if os.path.exists(pdf_path) and os.path.exists(img_path):
        print(f"Skip PDF {pdf_path} ...")
        return pdf_relative_path, img_relative_path


    # 下载PDF文件
    response = get_reponse(url)
    if not response:
        print(f"no pdf file for : {title}")
        return None, None
    with open(pdf_path, 'wb') as f:
        f.write(response.content)

    # 将PDF文件转换为图片
    images = convert_from_bytes(response.content)

    # 获取第一页图片
    first_page = images[0]
    first_page.save(img_path, 'JPEG')
    if watermark_text:
        add_watermark(img_path, watermark_text)
    return pdf_relative_path, img_relative_path



def crawl_html(url):
    global date_str
    response = get_reponse(url)
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
            try:
                if a_tag:
                    arxiv_id = a_tag['href'].split('/')[-1]
                    pdf_link = dt_tag.find('a', {'title': 'Download PDF'})['href']
                    pdf_link = f"https://arxiv.org{pdf_link}.pdf"
                    
                    title_element = dd_tag.find('div', class_='list-title mathjax')
                    title = title_element.text.strip().replace('Title:', ' ').strip()

                    authors_tag = dd_tag.find('div', class_='list-authors')
                    authors = ''
                    if authors_tag:
                        authors = authors_tag.get_text(strip=True).replace('Authors:', '').replace(',', ', ')
                    
                    comments_tag = dd_tag.find('div', class_='list-comments')
                    comments = ''
                    if comments_tag:
                        comments = comments_tag.get_text(strip=True).replace('Comments:', '')

                    item = {'arxiv_id': arxiv_id, 'title': title, 'pdf_link': pdf_link, 'authors': authors, 'comments': comments, 'date': date_str}
                    result.append(item)
            except Exception as e:
                print('\n\n++++++++++++++++\n')
                print(e)
                print('\n\n')
                pass
        return result
    else:
        return None

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

result = crawl_html(url)

# 保存结果到文件
json_path = f'{cur_dir}/arxiv_{date_str}.json'
with open(json_path, 'w', encoding='utf-8') as file:
    json.dump(result, file, ensure_ascii=False, indent=2)


md_path = f'{cur_dir}/arxiv_{date_str}.md'
if os.path.exists(md_path):
    if not overwrite:
        print(f'{date_str}.md already exists! Add --overwrite to rewrite!')
        sys.exit(-1)
    else:
        with open(md_path, 'w', encoding='utf-8') as fp:
            # create empty md file
            pass


total = len(result)
for i, js in tqdm(enumerate(result)):
    title = js['title']
    truncated_title = get_valid_title(title)
    arxiv_id = js['arxiv_id']
    pdf_link = js['pdf_link']
    comments = js['comments']
    authors = js['authors']
    comments = js['comments']
    print(f"processing {i+1}/{total} {title} ...")
    max_try = 5
    kk = 0
    failed = False
    while True:
        kk += 1
        try:
            pdf_relative_path, img_relative_path = \
                download_pdf_image(pdf_link, truncated_title, arxiv_id, comments, i+1)
            break
        except Exception as e:
            print(f"Exception: {e}, try {kk} times ...\n")
            if kk > max_try:
                failed = True
                break
    
    if failed:
        print(f"download {title} failed! skip ...")
        continue
    
    md_block = []
    md_block.append(f"## 【{i+1}】{title}\n")
    md_block.append(f"- arXiv id: {arxiv_id}\n")
    md_block.append(f"- PDF LINK: {pdf_link}\n")
    md_block.append(f"- authors: {authors}\n")
    md_block.append(f"- comments: {comments}\n")
    if pdf_relative_path:
        md_block.append(f"- [PDF FILE]({pdf_relative_path})\n\n")
        md_block.append(f"![fisrt page]({img_relative_path})\n\n\n")
    append_file(md_path, md_block)


print('\n\ndone!!!')
print(date_str)