from bs4 import BeautifulSoup
import json
import argparse
from tqdm import tqdm
from utils import get_html_from_url


def extract_paper_info(url, output_filename):
    # 发送 GET 请求获取 HTML 内容
    html = get_html_from_url(url)
    
    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(html, 'html.parser')
    
    # 创建空列表存储论文信息
    papers = []
    
    # 找到所有论文的 HTML block
    paper_blocks = soup.find_all('span', class_='d-block')

    # 遍历每个论文 block 提取信息
    for block in tqdm(paper_blocks):
        try:
            # 提取论文标题和 URL
            title_element = block.find('strong').find('a')
            title = title_element.text
            paper_url = title_element['href']
            
            # 提取作者列表
            authors = block.find_all('a')[1:]
            author_list = [author.text for author in authors]
            
            # 构建论文信息字典
            paper_info = {
                'title': title,
                'url': 'https://aclanthology.org' + paper_url,
                'pdf': 'https://aclanthology.org' + paper_url[:-1] + '.pdf',
                'authors': author_list
            }
            
            # 将论文信息添加到列表中
            papers.append(paper_info)
            
        except Exception as e:
            # print(e)
            continue
    
    # 将论文信息列表导出为 JSON 文件
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(papers, f, ensure_ascii=False, indent=4)
        print("papers.json 文件保存成功！")
    return papers


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Export paper information to JSON given ACL url.')
    parser.add_argument('--url', default='https://aclanthology.org/events/acl-2023/', help='ACL url')
    parser.add_argument('--output', default='papers.json', help='Path to the json output file')
    args = parser.parse_args()


    url = args.url
    output_filename = args.output
    papers = extract_paper_info(url, output_filename)

