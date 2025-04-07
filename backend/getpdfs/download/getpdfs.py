# Download from URLs in odois.txt, otitle.txt, and opmid.txt
import re
from scidownl import scihub_download
import os.path

paper_type = ["doi", "title", "pmid"][1]
paper_src = ["odois.txt", "otitle.txt", "opmid.txt"][1]

with open(paper_src, 'r') as file:
    content = file.read()
X = [re.findall('^([0-9]*) (.*)$', x, re.IGNORECASE)[0] for x in content.split('\n')[:-1]]
D = dict()
for (x, key) in X:
    val = int(x)
    if key not in D.keys():
        D[key] = [val]
    else:
        D[key].extend([val])
for item in D.keys():
    if int(D[item][0]) <= 712:
        print(f'skipping {D[item][0]}')
        continue
    paper = item
    doiout = f'./pdfs/doi/{D[item][0]}.pdf'
    titleout = f'./pdfs/title/{D[item][0]}.pdf'
    pmidout = f'./pdfs/pmid/{D[item][0]}.pdf'
    out = f'./pdfs/{paper_type}/{D[item][0]}.pdf'
    if os.path.isfile(doiout) or os.path.isfile(titleout) or os.path.isfile(pmidout):
        print(f'{D[item][0]}.pdf exists')
    else:
        scihub_download(paper, paper_type=paper_type, out=out)
    #else:
    #    print(f'mv {item}.pdf {D[item][0]}.pdf')
