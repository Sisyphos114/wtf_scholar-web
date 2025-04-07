from langchain_community.chat_models import ChatPerplexity
import re
import os
from utils import get_citenum
import editdistance
from pathlib import Path
import sys
import io
from langchain_openai import ChatOpenAI
# Store the current stdout (in case you need to revert back)
original_stdout = sys.stdout

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='gb18030')

# 确保文件路径总是相对于脚本所在目录
# 构造文件的完整路径
script_dir = Path(__file__).parent
outline_path = script_dir / 'outline.txt'
file_path = script_dir / "prompt02pplx-area2fact.txt"
prompt_path = script_dir / "prompt01.out"


# Get the reference number of url from citations, append to the end of citations if not found
def get_citenum_by_url(citations, title, url, proof):
    for key in citations.keys():
        _, _url, _ = citations[key]
        url_dist = editdistance.eval(url.lower(), _url.lower())
        if url_dist <= 2:  # Allow 2 errors
            return key  # citation exists
    citenum = len(citations) + 1
    citations[str(citenum)] = [title, url, proof]
    return citenum  # citation does not exist


# retrieve facts and their supports, resolving citation number from citations
def get_facts_and_supports(llm_output, citations):
    references_reached = False
    facts = []
    supports = []
    citenum_map = dict()
    lines = llm_output.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        if re.match('FACT*', line) is not None:
            facts.append(line)
            i += 1
            line = lines[i]
            if re.search('SUPPORT', line) is None:
                return None, None  # bad llm_output
            ref_entry = re.match(r'SUPPORT: (.*) ::: (.*) ::: (.*)', line)
            title = ref_entry.group(1)
            url = ref_entry.group(2)
            proof = ref_entry.group(3)
            citenum = get_citenum_by_url(citations, title, url, proof)
            supports.append([title, url, proof, citenum])
        i += 1
    return facts, supports


if __name__ == "__main__":
    llm = ChatOpenAI( base_url='https://tbnx.plus7.plus/v1',
                          api_key=os.environ["R1_API_KEY"],
                          model='deepseek-chat' )

    # 使用outline_path来读取文件，打开outline.txt文件并读取内容
    with open(outline_path, 'r') as f:
        outline = f.read()
        outlines = outline.split('\n')
        article_title = outlines[0]

    # 打开prompt02pplx-area2fact.txt文件并读取内容
    with open(file_path, 'r') as f:
        prompt = f.read()

    # 打开prompt01.out文件并读取内容
    collected = []
    section_title = None
    with open(prompt_path) as f:
        line = f.readline()
        while line is not None and line != "":
            # pplx likes to prefix ### to section titles
            if re.match('.*ection [\\d\\.]*', line) is not None:
                if section_title is not None:
                    collected.append((section_title, section_areas))
                section_title = line
                section_areas = []
            if re.match(r'^\s*\d+\. .*', line) is not None:
                section_areas.append(line)
            line = f.readline()
        collected.append((section_title, section_areas))

    citations = dict()

    # 打开文件以写入模式
    output_path = script_dir / "prompt02.out"  # 确保输出文件在Backend目录中
    # Modify the part where you use print() to use output_file.write() instead
    with open(output_path, 'w', encoding='utf-8') as output_file:
        prev_section_title = None  # 新增变量用于记录上一个章节标题
        for section_title, section_areas in collected:
            if section_title != prev_section_title:  # 检查是否为重复标题
                print()
                output_file.write('\n')
                print(section_title, end='')
                output_file.write(section_title)
                prev_section_title = section_title  # 更新上一个章节标题
            for i, area in enumerate(section_areas):
                print(area, end='')
                output_file.write(area)
                tries = 0
                while True:
                    response = llm.invoke(prompt.format(article_title=article_title,
                                                        section_title=section_title,
                                                        area=area))
                    llm_output = response['result'] if isinstance(response, dict) else response.content
                    facts, supports = get_facts_and_supports(llm_output, citations)
                    if facts is not None:
                        for fact, support in zip(facts, supports):
                            fact_with_citation = f"{fact} [{str(support[3])}]"
                            print(fact_with_citation)
                            output_file.write(fact_with_citation + '\n')
                            source_info = f'SOURCE: {support[2]}'
                            print(source_info)
                            output_file.write(source_info + '\n')
                            url_info = f'URL: {support[1]}\n'
                            print(url_info)
                            output_file.write(url_info)
                        break
                    tries += 1
                    if tries > 5:
                        print('Unable to generate facts')
                        output_file.write('Unable to generate facts\n')
                        break
                print('\n\n')
                output_file.write('\n\n')

        if len(citations) != 0:
            print("References:")
            output_file.write("References:\n")
        for i in citations.keys():
            reference, url, _ = citations[i]
            reference_info = f"{i}. {reference}. {url}\n"
            print(reference_info)
            output_file.write(reference_info)

    # 检测并删除连续包含**的行
    with open(output_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    while i < len(lines):
        current_line = lines[i]
        if '**' in current_line and i + 1 < len(lines) and '**' in lines[i + 1]:
            new_lines.append(current_line)
            i += 2  # 跳过下一行
        else:
            new_lines.append(current_line)
            i += 1

    # 将处理后的内容写回文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
