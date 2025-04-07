import os
import re
from unidecode import unidecode
from langchain_community.chat_models import ChatPerplexity
import time

llm = ChatPerplexity(model="llama-3-sonar-large-32k-chat", temperature=0)

with open('missing2', 'rb') as file:
    content = file.read()
content = content.decode('ascii', errors='ignore').split('\n')[:-1]
content = [re.findall('^([0-9]+) (.*)$', c)[0] for c in content]

ftitle  = open( "otitle.txt", "w")

for num, line in content:
    if line == '':
        break
    print("processing", num)
    output = llm.invoke('what is the title of the paper in this bibliography'
                      f'entry: \"{line}\". State only the title without any extra text.')
    ftitle.write(f'{num} {output.content}\n')
    time.sleep(3)
