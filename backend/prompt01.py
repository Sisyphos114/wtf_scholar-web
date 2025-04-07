# -*- coding: utf-8 -*-
import os
import sys
import re
from langchain_community.chat_models import ChatPerplexity, ChatOllama
from langchain_openai import ChatOpenAI
import sys
import io
# 获取当前脚本的目录
script_dir = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    # 判断是否提供了outline文件路径作为命令行参数
    use_remote = True
    if len(sys.argv) > 1:
        outline_path = sys.argv[1]
    else:
        outline_path = os.path.join(script_dir, "outline.txt")

    # 使用绝对路径来获取prompt文件
    prompt_path = os.path.join(script_dir, "prompt01-outline2area.txt")
    pplx_models = ["sonar-pro", "sonar-reasoning", "sonar-reasoning-pro", "sonar-deep-research"]
    if use_remote:
        #llm = ChatPerplexity(api_key=os.environ["PPLX_API_KEY"], temperature=0, model=pplx_models[0])
        llm = ChatOpenAI( base_url='https://tbnx.plus7.plus/v1',
                          api_key=os.environ["R1_API_KEY"],
                          model='deepseek-chat' )
    else:
        model = "llama3.1"
        llm = ChatOllama(model=model)
    try:
        # 读取prompt文件内容
        with open(prompt_path, 'r', encoding='utf-8', errors='ignore') as f:
            prompt = f.read()

        # 读取outline文件内容
        with open(outline_path, 'r', encoding='utf-8', errors='ignore') as f:
            outline_content = f.read()

        # 解析outline内容
        outlines = outline_content.split('\n')
        article_title = outlines[0]
        outlines = outlines[1:]  # 移除标题行

        processed_outline = []
        section_count = 1
        subsection_count = 1  # 初始化subsection_count

        for line in outlines:
            # 匹配子部分（"--"）
            subsection_match = re.match(r'^--\s*(.*)', line)
            if subsection_match:
                title = subsection_match.group(1)
                processed_outline.append(f"  Subsection {section_count - 1}.{subsection_count}. {title}")
                subsection_count += 1
            # 匹配部分（"-"）
            section_match = re.match(r'^-\s*(.*)', line)
            if section_match:
                title = section_match.group(1)
                processed_outline.append(f"Section {section_count}. {title}")
                section_count += 1
                subsection_count = 1  # 重置subsection_count


        # 生成内容
        response = llm.invoke(prompt.format(article_title=article_title, outline='\n'.join(processed_outline)))

        # 确定输出文件路径
        output_path = os.path.join(script_dir, 'prompt01.out')

        # 将结果保存到指定文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(response.content)

        print(f"结果已保存到 {output_path} 文件中。")
        print(f"处理了 {section_count - 1} 个部分和 {subsection_count - 1} 个子部分。")

    except Exception as e:
        print(f"错误：{str(e)}")
        sys.exit(1)
