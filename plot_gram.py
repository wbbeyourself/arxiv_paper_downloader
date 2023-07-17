import json
import argparse
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from collections import Counter

one_gram_stop_words = ['a', 'an', 'language', 'via', 'model', 'models', 'dataset', 'neural', 'learning', 'text', 'towards', 'large']
two_gram_stop_words = ['of', 'for']



def is_good_text(text):
    filter_suffix = [' for', ' of', ' via', ' with', ' in', ' to', ' and']
    filter_prefix = ['a ', 'on ', 'in ', 'for ', 'of ', 'with ', 'and ']
    for w in filter_prefix:
        if text.startswith(w):
            return False
    
    for w in filter_suffix:
        if text.endswith(w):
            return False
    
    return True


def get_ngram_frequency(title_list, n):
    ngram_list = []
    for title in title_list:
        words = title.split()
        if len(words) >= n:
            for i in range(len(words) - n + 1):
                ngram = ' '.join(words[i:i+n]).lower()
                if ngram not in stopwords.words('english'):
                    if n == 1 and ngram in one_gram_stop_words:
                        continue
                    elif not is_good_text(ngram):
                        continue
                    ngram_list.append(ngram)
    ngram_counts = Counter(ngram_list)
    return ngram_counts

def plot_bar_chart(data, title, n='n'):
    labels, values = zip(*data)
    fig, ax = plt.subplots(figsize=(8, 6))  # 创建一个8x6大小的图形
    ax.barh(labels, values)  # 使用plt.barh绘制横向条形图
    ax.set_yticks(labels)  # 设置y轴刻度标签
    ax.set_xlabel('Frequency')  # 调整x轴标签
    ax.set_ylabel(f'{n}-gram')  # 调整y轴标签
    ax.set_title(title)
    ax.invert_yaxis()  # 翻转y轴，使频率高的在上面
    plt.tight_layout()  # 调整子图布局
    plt.show()




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Export paper information to JSON and Markdown.')
    parser.add_argument('--json_output', default='papers.json', help='Path to the JSON output file')
    args = parser.parse_args()

    path = args.json_output
    papers = []
    with open(path, encoding='utf-8') as fp:
        papers = json.load(fp)

    paper_title_list = []
    for js in papers:
        url = js['url']
        if 'acl-long' in url:
            paper_title_list.append(js['title'])


    # 计算1-gram和2-gram的词频
    one_gram_counts = get_ngram_frequency(paper_title_list, 1)
    two_gram_counts = get_ngram_frequency(paper_title_list, 2)
    three_gram_counts = get_ngram_frequency(paper_title_list, 3)

    # 获取top 10的1-gram和2-gram词频
    topk = 20
    topk_one_gram = one_gram_counts.most_common(topk)
    topk_two_gram = two_gram_counts.most_common(topk)
    topk_three_gram = three_gram_counts.most_common(topk)

    # 打印结果
    print(f"Top {topk} 1-gram:")
    for ngram, count in topk_one_gram:
        print(f"{ngram}: {count}")

    print(f"\nTop {topk} 2-gram:")
    for ngram, count in topk_two_gram:
        print(f"{ngram}: {count}")
    
    print(f"\nTop {topk} 3-gram:")
    for ngram, count in topk_three_gram:
        print(f"{ngram}: {count}")

    # # 绘制柱状图
    plot_bar_chart(topk_one_gram, f"Top {topk} 1-gram", n=1)
    plot_bar_chart(topk_two_gram, f"Top {topk} 2-gram", n=2)
    plot_bar_chart(topk_three_gram, f"Top {topk} 3-gram", n=3)
