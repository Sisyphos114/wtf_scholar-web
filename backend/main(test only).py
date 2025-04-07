import os
from dotenv import load_dotenv
import subprocess
from pathlib import Path

# 加载 .env 文件中的环境变量
load_dotenv()
SCRIPT_DIR = Path(__file__).parent
# 获取 R1_API_KEY 环境变量
api_key = os.getenv('R1_API_KEY')
if api_key is None:
    print("未找到 R1_API_KEY 环境变量，请检查 .env 文件。")
else:
    print(f"成功获取 R1_API_KEY: {api_key}")

# 定义要执行的脚本列表
scripts = [    
    "prompt06.py"
    ]

# 依次执行脚本
for script in scripts:
    try:
        # 使用 SCRIPT_DIR 构造脚本的完整路径
        script_path = SCRIPT_DIR / script
        print(f"正在执行脚本: {script_path}")
        # 在 subprocess.run 中使用完整路径
        result = subprocess.run(['python', str(script_path)], check=True, text=True, capture_output=True, encoding='utf-8', errors='replace')
        print(f"脚本 {script} 执行成功。")
        print("脚本输出:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"脚本 {script} 执行失败，错误信息:")
        print(e.stderr)
        break
