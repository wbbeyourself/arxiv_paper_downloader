# highlight authors, meetings, and keywords

# add your keywords here
STAR_KEYWORDS = ['Text-to-SQL']

# add your authors here
_AUTHOR_GROUP1 = ['Zhoujun Li']
_AUTHOR_GROUP2 = ['Qian Liu']
STAR_AUTHORS = _AUTHOR_GROUP1 + _AUTHOR_GROUP2

# add your meetings here
STAR_MEETINGS = ['ACL', 'COLING', 'NAACL', 'TACL', 'EMNLP']
# sort meetings according to string length desc
STAR_MEETINGS = sorted(STAR_MEETINGS, key=lambda x: len(x), reverse=True)