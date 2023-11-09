# acl & arxiv paper downloader


## env
```bash
pip install -r requirements.txt
```

Windows system meets `pdf2image` related errors, see [issue_markdown](./issue_bugs.md) for solution.

## usage


### 1. Download ACL papers
Step 1: download all papers, default is ACL 2023 papers, you can specify your acl url.
```bash
python acl_spider.py
```

Step 2: filter papers according to your keywords, and get the abstract of every paper.
```bash
python filter_papers.py --keywords keyword1 keyword2 keyword3
```


### 2. Download Arxiv papers

Download the latest n day research paper PDF, generate corresponding markdown and preview images.

```bash
python arxiv_spider.py  --root_dir  /your/papers/dir/path  --days n
```

If you want to overwrite previous markdowns, use
```bash
python arxiv_spider.py  --root_dir  /your/papers/dir/path  --days n  --overwrite
```

## todo
- [ ] Highlight target conferences and authors.
- [ ] Highlight custom keyword list.
- [ ] Customize the specific areas of interest, such as CS.CL and CS.CV.
- [ ] Demo videos.
- [x] Use VPN Arg Parse. 

## Useful Arxiv Related Repos
- https://github.com/lukasschwab/arxiv.py
- https://github.com/braun-steven/arxiv-downloader
