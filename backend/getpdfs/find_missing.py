# Find the files that has not been successfully processed
import re

def find_missing(lst):
    return sorted(set(range(lst[0], lst[-1])) - set(lst))

with open('processed', 'r') as file:
    content = file.read()
content = content.split('\n')
content = [int(c) for c in content[:-1]]
missing = find_missing(content)

with open('biblio.uniq.txt', 'rb') as file:
    biblio = file.read()
biblio = biblio.decode('ascii', errors='ignore').split('\n')[:-1]
biblio = [re.findall('^([0-9]+) (.*)$', c)[0] for c in biblio]
for num, c in biblio:
    if int(num) in missing:
        print(num, c)
