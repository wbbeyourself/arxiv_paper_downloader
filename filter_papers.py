import json
import argparse

def json_to_markdown(json_data):
    markdown = ""
    
    for paper in json_data:
        markdown += f"## {paper['title']}\n"
        markdown += f"**Authors:** {', '.join(paper['authors'])}\n"
        markdown += f"**URL:** [{paper['url']}]({paper['url']})\n\n"
        markdown += f"**PDF:** [{paper['pdf']}]({paper['pdf']})\n\n"
    
    return markdown

parser = argparse.ArgumentParser(description='Export paper information to JSON and Markdown.')
parser.add_argument('--keywords', nargs='+', help='Keywords to filter papers')
parser.add_argument('--json_output', default='papers.json', help='Path to the JSON output file')
parser.add_argument('--markdown_output', default='papers.md', help='Path to the Markdown output file')
args = parser.parse_args()

path = args.json_output
papers = []
with open(path, encoding='utf-8') as fp:
    papers = json.load(fp)

target_papers = []
for js in papers:
    title = js['title'].lower()
    words = title.split()
    for w in args.keywords:
        if w in words:
            target_papers.append(js)
            break

# 将 JSON 数据转换为 Markdown
markdown_content = json_to_markdown(target_papers)

# 保存 Markdown 内容到文件
with open(args.markdown_output, 'w', encoding='utf-8') as f:
    f.write(markdown_content)

print("Markdown 文件保存成功！")


# python filter_papers.py --keywords code sql text-to-sql