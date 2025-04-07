import os
import re
import sys

# 设置标准输出和标准错误的编码为 UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# 获取脚本所在目录的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    # 文件路径
    manuscript_path = os.path.join(script_dir, "manuscript.md")
    prompt04_path = os.path.join(script_dir, "prompt04.out")
    prompt02_path = os.path.join(script_dir, "prompt02.out")
    outline_path = os.path.join(script_dir, "outline.txt")

    with open(manuscript_path, 'w', encoding='utf-8') as output_file:
        # 读取 outline.txt 的第一行作为标题
        with open(outline_path, 'r', encoding='utf-8') as outline_file:
            title = outline_file.readline().strip()
            # 以 Markdown 一级标题格式写入
            output_file.write(f'# {title}\n\n')

        # 读取 prompt04.out 文件
        with open(prompt04_path, 'r', encoding='utf-8') as f:
            article = f.read()
            citenums = set([int(x) for x in re.findall(r'\[(\d+)\]', article)])
            missing = set(range(max(citenums))) - citenums

        indexmap = dict(list(zip(citenums, [i + 1 for i in list(range(len(citenums)))])))
        for i in indexmap.keys():
            source = '[' + str(i) + ']'
            target = '[' + str(indexmap[i]) + ']'
            article = article.replace(source, target)
        print(article)  # 现在可以安全打印
        output_file.write(article + '\n')

        # 读取 prompt02.out 文件
        f = open(prompt02_path, 'r', encoding='utf-8')
        line = f.readline()
        while line is not None and line != "" and re.match("References:.*", line) is None:
            line = f.readline()
        refnum = 1
        print('References:\n')
        output_file.write('References:\n\n')
        while line is not None and line != "":
            matches = re.match(r'^(\d+)\. (.*)', line)
            if matches is None:
                line = f.readline()
                continue
            linenum, reference = matches.group(1), matches.group(2)
            if int(linenum) not in missing:
                # Add a check to ensure linenum exists in indexmap
                if int(linenum) in indexmap:
                    reference_line = f'{indexmap[int(linenum)]}. {reference}\n'
                    print(reference_line)
                    output_file.write(reference_line)
            line = f.readline()
        f.close()  # Good practice to close the file
