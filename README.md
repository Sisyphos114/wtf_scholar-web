# wtf_scholar-web
Web application for Manuscript GEN

docker 部署
下载release中的镜像zip,
解压为前后端的tar
dockerfile

构建 Docker 镜像：
backend
```sh
docker build -t wtf-api-backend -f Backend/Dockerfile .
```
```sh
docker run -d -p 5001:5001 flask-api-app
```
————————————————————

frontend
```sh
docker build -t wtf-frontend-dev -f frontend/Dockerfile .
```
```sh
docker run -d -p 5173:5173 vue-frontend-dev
```



# frontend
# academic-writing-assistant

This template should help get you started developing with Vue 3 in Vite.

## Recommended IDE Setup

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur).

## Customize configuration

See [Vite Configuration Reference](https://vite.dev/config/).

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Compile and Minify for Production

```sh
npm run build
```
--------------------
一、运行逻辑分析
1. 流程架构
这是一个基于LLM的文档生成流水线，系统按以下顺序执行：
大纲 → 扩展要点 → 获取事实 → 匹配参考文献 → 生成段落 → 优化表达 → 过滤冗余引用
2. 核心模块说明  
  ○ prompt01.py: 大纲转结构化要点（生成树形结构的话题分支）
  ○ prompt02.py: 每个要点下注入3-5个实证数据点
  ○ prompt03.py: 通过向量数据库检索文献证据（使用md2biblio.txt做元数据映射）
  ○ prompt04.py: 将事实数据转换为连贯段落
  ○ prompt05.py: 语言润色优化
  ○ prompt06.py: 自动去重引用（基于引用计数算法）
  ○ ps: 没有vectorstore时靠pplx给reference：prompt01.py -> prompt02pplx.py -> prompt03pplx.py -> prompt04.py -> prompt05.py -> prompt06.py
3. 数据流动
每个模块的输入输出均以文本文件传递，形成链式处理结构。中间产物包括：
  ○ area结构（含层级的话题树）
  ○ fact结构（带文献标记的原子事实）
  ○ draft版本（含临时引用标记的原始稿件）
二、API设计建议
1. 服务端点规划  
# 基础接口
POST /api/v1/pipeline/init          # 创建新写作任务
POST /api/v1/upload/outline         # 大纲上传

# 分阶段处理
#(后续需要整合在一起，理想情况就是整合成一个POST/api/v1/process/generate命令，输入为用户outline，输出为manuscript.py)
POST /api/v1/process/expand_outline # 执行prompt01（生成树形结构的话题分支）
POST /api/v1/process/collect_facts # 执行prompt02/pplx（注入3-5个实证数据点）
POST /api/v1/process/link_refs      # 执行prompt03/pplx（通过向量数据库检索文献证据）
POST /api/v1/process/generate_draft # 执行prompt04(数据转换)
POST /api/v1/process/polish         # 执行prompt05(语言润色优化)
POST /api/v1/process/filter_refs    # 执行prompt06(自动去重引用)

# 辅助接口
GET  /api/v1/references/{doc_id}    # 获取文献列表
POST /api/v1/validate/citation      # 引文校验
2. 请求响应示例  
// 扩展大纲请求
{
  "task_id": "UUID",
  "outline": "# Main Topic\n## Subtopic",
  "parameters": {
    "depth": 3,
    "max_branches": 5
  }
}

// 文献匹配响应
{
  "status": "processing",
  "current_step": "reference_linking",
  "progress": 65,
  "citations": [
    {
      "fact_id": "FACT_001",
      "source_hash": "md5:a1b2c3",
      "confidence": 0.92
    }
  ]
}
三、前端设计方案
1. 核心功能模块

2. 界面组件规划  
  ○ 工作区面板  
| 组件                | 功能描述                     |
|---------------------|----------------------------|
| Outline Editor      | 大纲可视化编辑（树形结构+Markdown）|
| Fact Inspector      | 事实点溯源查看（显示文献支撑证据）  |
| Draft Preview       | 实时稿件预览（带引用高亮）       |
| Reference Dashboard | 文献管理面板（按影响力排序）     |
| Pipeline Monitor    | 流水线进度监控（各阶段状态灯）    |
3. 交互流程  

4. 关键技术需求  
  ○ 实时协同编辑：使用Operational Transformation实现大纲多人协作
  ○ 溯源可视化：D3.js绘制事实-文献关系图谱
  ○ 差异对比：Monaco Editor集成Diff功能
  ○ 进度追踪：WebSocket推送流水线状态更新
四、扩展建议
1. 性能优化  
  ○ 实现增量处理：当用户修改部分内容时，仅重新执行受影响流水线阶段
  ○ 引入缓存机制：对已验证通过的文献匹配结果建立缓存库
2. 安全设计  
  ○ 文献校验：增加DOI/PMID真实性验证接口
  ○ 水印机制：在最终输出嵌入不可见的数字水印
3. AI增强功能  
  ○ 可信度评分：对每个事实点进行证据充分性评级
  ○ 争议检测：通过立场分析识别可能存疑的表述
这个设计保持了学术写作工具的专业性，同时通过模块化接口支持灵活扩展。建议采用React+FastAPI技术栈实现，用Celery管理后台流水线任务。


**npm run serve**

# backend

pip install -r requirements.txt
