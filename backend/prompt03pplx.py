# -*- coding: utf-8 -*-
from langchain_community.chat_models import ChatPerplexity
import re
import os
import sys
import io
from langchain_openai import ChatOpenAI
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030') 
if __name__ == "__main__":
    # 获取脚本所在目录
    script_dir = os.path.dirname(__file__)
    
    llm = ChatOpenAI( base_url='https://tbnx.plus7.plus/v1',
                          api_key=os.environ["R1_API_KEY"],
                          model='deepseek-chat' )
    
    # 构造输出文件路径
    output_file_path = os.path.join(script_dir, 'prompt03.out')
    explain_file_path = os.path.join(script_dir, 'prompt03explain.out')
    
    # 打开输出文件
    explain_f = open(explain_file_path, 'w', encoding='utf-8')
    output_file = open(output_file_path, 'w', encoding='utf-8')

    # 读取输入文件
    input_file_path = os.path.join(script_dir, "prompt03-fact2ref.txt")
    with open(input_file_path, 'r', encoding='utf-8') as f:
        prompt = f.read()

    citations = dict()
    input_file_path = os.path.join(script_dir, "prompt02.out")
    with open(input_file_path, 'r', encoding='utf-8') as f:
        line = f.readline()
        while line is not None and line != "":
            if re.search('Subsection', line) is not None:
                print()
                output_file.write('\n')
                print(line)
                output_file.write(line)
                print()
                output_file.write('\n')
                explain_f.write(f'{line}\n')

            elif re.match(r'\d+\.', line) is not None:
                print()
                output_file.write('\n')
                print(line)
                output_file.write(line)
                print()
                output_file.write('\n')
                explain_f.write(f'{line}\n')

            elif re.match('FACT:', line) is not None:
                fact = re.match('FACT: (.*)', line).group(1)
                print('FACT:', fact)
                output_file.write(f'FACT: {fact}\n')
                line = f.readline()
                if re.match(r'SOURCE:', line) is None:
                    print('Bad input file: No SUPPORT line for fact')
                    output_file.write('Bad input file: No SUPPORT line for fact\n')
                    exit()
                support = re.match('SOURCE: (.*)', line).group(1)
                evaluation = llm.invoke(prompt.format(fact=fact, text=support))
                lines = evaluation.content.split('\n')
                lines = [s for s in lines if s]
                rated = False
                i = 0
                while i < len(lines):
                    l = lines[i]
                    if re.match('RATING:', l) is not None:
                        rated = True
                        rating = re.search(r'RATING: (\d+)', l).group(1)
                        if rating.endswith('**'):
                            rating = rating[:-2]
                        i += 1
                        l = lines[i]
                        if re.match('REASON:', l) is None:
                            print('Bad LLM output: No REASON line in LLM output')
                            output_file.write('Bad LLM output: No REASON line in LLM output\n')
                            print('LLM output:', evaluation.content)
                            output_file.write(f'LLM output: {evaluation.content}\n')
                            exit()
                        reason = re.search('REASON:(.*)', l).group(1)
                        explain_f.write(f'FACT: {fact}\n')
                        explain_f.write(f'SUPPORT: {support}\n')
                        explain_f.write(f'SCORE: {rating}\n')
                        explain_f.write(f'REASON: {reason}\n\n')
                    i += 1
                if not rated:
                    print('Bad LLM output: No RATING line in LLM output')
                    output_file.write('Bad LLM output: No RATING line in LLM output\n')
                    print('LLM output:', evaluation.content)
                    output_file.write(f'LLM output: {evaluation.content}\n')
                    exit()

                print()
                output_file.write('\n')

            elif re.match('^References', line) is not None:
                break

            line = f.readline()

    # 关闭文件
    explain_f.close()
    output_file.close()
