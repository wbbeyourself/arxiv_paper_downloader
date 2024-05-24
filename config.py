# highlight authors, meetings, and keywords

# add your keywords here
STAR_KEYWORDS = ['Text-to-SQL']

# add your authors here
_AUTHOR_GROUP1 = ['Zhoujun Li', 'Wanxiang Che', 'Zhiyuan Liu', 'Dawn Song', 'Kaiming He', 'Min-Yen Kan', 'Jian-Guang Lou', 'Yan Gao', 'Jiajun Zhang']
_AUTHOR_GROUP2 = ['Qian Liu', 'Libo Qin', 'Li Dong', 'Xinyun Chen', 'Tao Yu', 'Danqi Chen', 'Diyi Yang', 'Jason Wei']
_AUTHOR_GROUP3 = ['Jiuxiang Gu']
STAR_AUTHORS = _AUTHOR_GROUP1 + _AUTHOR_GROUP2 + _AUTHOR_GROUP3

# add your meetings here
_AI_MEETINGS = ['AAAI', 'IJCAI']
_ML_MEETINGS = ['ICLR', 'ICML', 'NeurIPS', 'ECML']
_IR_MEETINGS = ['SIGIR']
_NLP_MEETINGS = ['ACL', 'EMNLP', 'COLING', 'NAACL', 'TACL', 'EACL']
STAR_MEETINGS = _AI_MEETINGS + _ML_MEETINGS + _IR_MEETINGS + _NLP_MEETINGS

# sort meetings according to string length desc
STAR_MEETINGS = sorted(STAR_MEETINGS, key=lambda x: len(x), reverse=True)