# -*- coding: utf-8 -*-
import re
import os
from langchain_community.chat_models import ChatPerplexity, ChatOllama
import sys
import io
from langchain_openai import ChatOpenAI
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030') 
def generate_paragraph(prompt, title, topic, facts, output_file):
    response = llm.invoke(prompt.format(section_title=title, topic=topic, facts=facts))
    payload = re.search(r'BEGIN\n([\s\S]+)\nEND', response.content)
    if payload is not None:
        print(payload.group(1))
        output_file.write(payload.group(1) + '\n')
    else:  # Retry
        response = llm.invoke(prompt.format(section_title=title, topic=topic, facts=facts))
        payload = re.search(r'BEGIN\n([\s\S]+)\nEND', response.content)
        if payload is not None:
            print(payload.group(1))
        else:  # Give up
            print('---THERE MAY BE ERRORS WITH THE FOLLOWING TEXT---')
            output_file.write('---THERE MAY BE ERRORS WITH THE FOLLOWING TEXT---\n')
            print(response.content)
            output_file.write(response.content + '\n')
            print('-------------------------------------------------')
            output_file.write('-------------------------------------------------\n')
    print()
    output_file.write('\n')


if __name__ == "__main__":
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    i_am_rich = True  # 此处较原代码修改为True
    if i_am_rich:
        llm = ChatOpenAI( base_url='https://tbnx.plus7.plus/v1',
                            api_key=os.environ["R1_API_KEY"],
                            model='deepseek-chat' )
    else:
        model = "llama3.1"
        llm = ChatOllama(model=model)
    
    # 读取prompt模板
    with open(os.path.join(script_dir, "prompt04-fact2article.txt"), 'r', encoding='utf-8') as f:
        prompt = f.read()
    
    # 读取outline文件
    with open(os.path.join(script_dir, "outline.txt"), 'r', encoding='utf-8') as f:
        outline = f.read()
        outlines = outline.split('\n')
        article_title = outlines[0]

    facts = []
    # 打开输出文件，路径为脚本所在目录
    output_path = os.path.join(script_dir, "prompt04.out")
    with open(output_path, 'w', encoding='utf-8') as output_file:
        # 读取事实文件
        with open(os.path.join(script_dir, "prompt02.out"), 'r', encoding='utf-8') as f:
            line = f.readline()
            while line is not None and line != "":
                if "References:" in line:
                    break
                title_line = re.match('.*Subsection (.*)', line)
                if title_line is not None:
                    _title = title_line.group(1)
                    if len(facts) != 0:
                        generate_paragraph(prompt=prompt, title=title, topic=topic,
                                         facts="- " + "\n\n- ".join(facts), output_file=output_file)
                        facts = []
                    title = _title
                    line = f.readline()
                    print(title)
                    output_file.write(title + '\n')
                    continue
                topic_line = re.match(r'^\d+\. (.*)', line)
                if topic_line is not None:
                    _topic = topic_line.group(1)
                    if len(facts) != 0:
                        generate_paragraph(prompt=prompt, title=title, topic=topic,
                                         facts="- " + "\n\n- ".join(facts), output_file=output_file)
                        facts = []
                    topic = _topic
                    line = f.readline()
                    print(topic)
                    output_file.write(topic + '\n')
                    continue
                fact_line = re.match('^FACT: (.*)', line)
                if fact_line is not None:
                    facts.append(fact_line.group(1))
                line = f.readline()
            if len(facts) != 0:
                generate_paragraph(prompt=prompt, title=title, topic=topic,
                                   facts="- " + "\n\n- ".join(facts), output_file=output_file)
