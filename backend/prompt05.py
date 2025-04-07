# -*- coding: utf-8 -*-
import re
import os
from langchain_community.chat_models import ChatPerplexity, ChatOllama
import sys
import io
from langchain_openai import ChatOpenAI
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030') 
def count_references(text):
    """统计文本中的引用数量"""
    type1 = set(re.findall(r'\[\d{1,3}\]', text))
    type2 = set(re.findall(r'\(\d{1,3}\)', text))
    return len(type1) + len(type2)

def polish(prompt, article_title, topic, texts, output_file):
    """处理文本并写入输出文件"""
    fulltext = "\n\n".join(texts)
    num_references = count_references(fulltext)
    citation_preserved = 0
    failed_outputs = []
    failed_reason = []
    retries = 0
    llm_model = "deepseek-chat" if os.environ.get("R1_API_KEY") else "llama3.1"

    while retries < 4:
        try:
            if retries < 2:
                llm = ChatOpenAI( base_url='https://tbnx.plus7.plus/v1',
                        api_key=os.environ["R1_API_KEY"],
                        model='deepseek-chat' )
            else:
                llm = ChatOllama(model=llm_model)
            
            response = llm.invoke(
                prompt.format(article_title=article_title, topic=topic, texts=fulltext)
            )
            
            payload = re.search(r'BEGIN\n([\s\S]+)\nEND', response.content)
            if payload is None:
                failed_reason.append("BAD FORM")
                retries += 1
                continue
            
            polished = payload.group(1)
            num_references_in_new_text = count_references(polished)
            
            if num_references == 0:
                citation_preserved = 1  # 避免除以零错误
            else:
                citation_preserved = num_references_in_new_text / num_references
            
            if citation_preserved > 0.3 or num_references_in_new_text > 2:
                print(polished)
                output_file.write(polished + '\n')
                return
            
            failed_outputs.append(polished)
            failed_reason.append("INSUFFICIENT CITATION")
            
        except Exception as e:
            print(f"Error during LLM invoke: {e}")
            retries += 1
            continue
        
        retries += 1
    
    if failed_outputs:
        failed_outputs_eval = [count_references(output) for output in failed_outputs]
        max_index = failed_outputs_eval.index(max(failed_outputs_eval))
        print(failed_outputs_eval, num_references)
        output_file.write(f"{failed_outputs_eval} {num_references}\n")
        print(f'------------------------{failed_reason[max_index]}--------------------------')
        output_file.write(f'------------------------{failed_reason[max_index]}--------------------------\n')
        print(failed_outputs[max_index])
        output_file.write(failed_outputs[max_index] + '\n')
        print('-----------------------------------------------------------------------------')
        output_file.write('-----------------------------------------------------------------------------\n')

if __name__ == "__main__":
    # 确保输出文件生成在与脚本相同的目录下
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(current_dir, "prompt05.out")
    
    # 加载prompt和outline
    with open(os.path.join(current_dir, "prompt05-tighten.txt"), 'r', encoding='utf-8') as f:
        prompt = f.read()
    
    with open(os.path.join(current_dir, "outline.txt"), 'r', encoding='utf-8') as f:
        outline = f.read()
    
    article_title = outline.split('\n')[0]

    texts = []
    topic = None
    
    # 读取输入文件
    input_path = os.path.join(current_dir, "prompt04.out")
    with open(input_path, 'r', encoding='utf-8') as input_file:
        with open(output_path, 'w', encoding='utf-8') as output_file:
            for line in input_file:
                line = line.strip()
                if not line:
                    continue
                topic_line = re.search(r'section (\d+\.\d+\: .*)', line)
                if topic_line:
                    _topic = topic_line.group(1)
                    if texts:
                        polish(prompt=prompt, article_title=article_title, topic=topic, texts=texts, output_file=output_file)
                    topic = _topic
                    texts = []
                    print(topic)
                    output_file.write(topic + '\n')
                else:
                    texts.append(line)
            if texts:
                polish(prompt=prompt, article_title=article_title, topic=topic, texts=texts, output_file=output_file)
