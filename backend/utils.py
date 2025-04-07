from langchain_community.chat_models import ChatOllama
import re
import editdistance
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030') 
prompt = '''The following is an potential entry from the Reference section of a scholarly article:

{reference}

Please find the article's title and it's publication venue. If found, give your answer in the following format:

TITLE: [title of the article]
VENUE: [publication venue of the article]

However, if the title is not found, output NONE instead.
'''

def get_citenum(citations: dict,
                llm: ChatOllama,
                reference: str) -> int:
    """
    Returns the reference number for this reference entry if it already exists in citations.
    Otherwise insert it into citations and assign a reference number to it.
    If the input reference contains no title, return 0.

    CAVEAT: Matching algo seems to work but 7b comes short. Use better model if possible.
    """
    response = llm.invoke(prompt.format(reference=reference))
    llm_output = response['result'] if type(response)==dict else response.content
    title = None
    for line in llm_output.split('\n'):
        if re.search('TITLE:.*', line) != None: 
            title = re.search('TITLE:(.*)', line).group(1)
        if re.search('VENUE:.*', line) != None: 
            venue = re.search('VENUE:(.*)', line).group(1)
    if title == None or title.strip(' ').upper().startswith('NONE'):
        return 0
    #print('title:', title)
    if venue == None:
        venue = "Unknown"
    #print('venue:', venue)
    for key in citations.keys():
        _, _title, _venue = citations[key] 
        #print('DB title:', _title)
        #print('DB venue:', _venue)
        title_dist = editdistance.eval(title.lower(), _title.lower())
        #if title_dist > title_thres:
        #    print('different:', title_dist, '>', title_thres)
        #else:
        #    print('identical:', title_dist, '<=', title_thres)
        minlen = abs(len(title)-len(_title)) # allow all extra letters and allow 3 more
        venue_dist = editdistance.eval(venue[:minlen].lower(), _venue[:minlen].lower())
        #if venue_dist > venue_thres:
        #    print('different:', venue_dist, '>', venue_thres)
        #else:
        #    print('identical:', venue_dist, '<=', venue_thres)
        #print()
        if title_dist <= 2 and venue_dist <= 2: # Allow 2 errors
            #print('cite num:', key)
            return key
    citenum = len(citations) + 1
    #print('cite num:', citenum)
    citations[str(citenum)] = [reference, title, venue]
    return citenum

