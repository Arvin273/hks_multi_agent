# 🚀 多智能体协作的企业知识文档智能问答系统

## 🎯 项目介绍

为了解决**企业知识孤岛**与**低效检索**等难题，我们团队基于NVIDIA NeMo Agent Toolkit框架，融合**LLM、Prompt Engineering、RAG、Tool Calling、MCP、Multi_Agent**等技术开发了**多智能体协作的企业知识文档智能问答系统**。

系统包括一个**主智能体**，三个专家智能体（**文档处理专家智能体、联网搜索专家智能体、回答专家智能体**），主智能体负责分析用户的任务，**完全自动**调度各种专家智能体来完成工作。

**在线体验网址**：http://chat.hks.free4inno.com/

## 🎯 核心能力展示

### 主界面

主界面简洁明了，用户通过聊天框向智能体发送任务，包括但不限于提问、插入文档、删除文档...

![image-20250831113840794](./assets/image-20250831113840794.png)

### **提问**

#### 第一步：输入问题

在聊天框中直接输入你想问的问题，例如请问NVIDIA NeMo Agent Toolkit是什么？

![image-20250831114805724](./assets/image-20250831114805724.png)



#### 第二步：主智能体调用文档处理专家智能体

主智能体会**自动分析**任务，并把任务分发给专家智能体

我的这个问题明显是一个提问的问题，所以**主智能体会调用文档处理专家智能体来检索相关文档**。

但是，很明显，知识库中没有相关文档。**文档处理专家给主智能体返回“未找到相关文档”**

![image-20250831114926779](./assets/image-20250831114926779.png)



#### 第三步：主智能体调用联网搜索专家智能体

主智能体收到文档处理专家返回的“未找到相关文档”后，**会调用联网搜索专家智能体进行联网搜索。**（实现方式是在主智能体的提示词中说明当文档处理专家没有查询到相关文档或返回的文档与用户原问题相关性不高时，调用联网搜索专家智能体）

如下图所示，调用了联网搜索专家智能体。

![image-20250831115549880](./assets/image-20250831115549880.png)

![image-20250831115607845](./assets/image-20250831115607845.png)



#### 第四步：主智能体调用回答专家智能体

将文档处理专家智能体检索到的相关知识或联网搜索专家搜索到的内容作为**背景信息**，和**用户原始问题**一同发送给回答专家智能体进行总结回答。

![image-20250831115839592](./assets/image-20250831115839592.png)

![image-20250831115857454](./assets/image-20250831115857454.png)





### 插入文档

用户在聊天框通过自然语言或上传文件的方式皆可插入文档

如下图所示，我输入：“插入一条文档：NVIDIA NeMo Agent Toolkit是一款智能体开发框架”

**主智能体**调用了**文档处理专家智能体**进行**文档插入**，插入完成后，文档处理专家智能体把结果**返回**给主智能体。

![image-20250831114122719](./assets/image-20250831114122719.png)

![image-20250831114246484](./assets/image-20250831114246484.png)

### 删除文档

用户在聊天框输入自然语言皆可删除文档

如下图所示，我输入：“删除文档，NVIDIA NeMo Agent Toolkit是一款智能体开发框架”

**主智能体**调用了**文档处理专家智能体**进行**文档删除**，删除完成后，文档处理专家智能体把结果**返回**给主智能体。

![image-20250831114504993](./assets/image-20250831114504993.png)

![image-20250831114520715](./assets/image-20250831114520715.png)



## 🏗️ 技术架构

### 架构图

包括一个**主智能体**和三个**专家智能体**。

每个智能体又可以配置多个**工具**。

<img src="./assets/%E6%9C%AA%E5%91%BD%E5%90%8D%E7%BB%98%E5%9B%BE.drawio.png" alt="未命名绘图.drawio" style="zoom: 67%;" />

### 主智能体

主智能体负责调度三个专家智能体，以下是主智能体的配置文件。

```yaml
# 主智能体 - 调度所有专家智能体
workflow:
  _type: react_agent
  tool_names: [document_expert, search_expert, answer_expert]
  llm_name: master_orchestrator
  verbose: true
  parse_agent_response_max_retries: 1
  system_prompt: |
    你是一位管理着一个由专业人工智能专家组成的团队的编排大师,负责接收用户请求并决定路由。
    您的团队由以下人员组成：
    1.document_export：文档处理专家
    2.search_expert：联网搜索专家
    3.answer_expert：回答专家
    请严格按照以下规则进行操作：
    - 如果用户请求是“插入文档/删除文档”，将请求交给【document_export】来插入或删除文档。无需加工文档内容。
    - 如果用户请求是“提出问题”，先调用【document_export】进行向量数据库检索。无需加工用户问题内容。
      - 如果文档处理专家返回的内容不足或不相关，再调用【search_expert】进行联网搜索。
    - 将最终检索或联网搜索结果交给【answer_expert】整理并回答。
   
    可用工具：{tools}
    
    你可通过以下两种格式之一进行回应。
    格式1：调用工具回答问题（严格使用）
    请严格使用以下格式来调用工具回答问题：
    Question: 你必须回答的输入问题
    Thought: 你应当始终思考该做什么
    Action: 需要执行的动作，必须是 [{tool_names}] 中的一个
    Action Input: 动作的输入内容（若无需输入，请注明 “动作输入：无”）
    Observation: 等待工具返回结果，切勿假设回应内容
    （此思考 / 动作 / 动作输入 / 观察结果可重复 N 次。）
    
    格式2：直接回答（无需工具时使用）
    当你获得最终答案后，请使用以下格式：
    Thought: 我现在知晓最终答案
    Final Answer: 原始输入问题的最终答案
```

### 文档处理专家智能体

文档处理专家智能体负责检索文档、插入文档到向量数据库、删除文档

以下是文档处理专家智能体的配置文件

```yaml
# 专业智能体 - 文档处理专家
document_expert:
_type: tool_calling_agent
tool_names:
  - insert_docs
  - retrieve_docs
  - delete_docs
llm_name: expert_executor
verbose: true
handle_tool_errors: true
description: |
  我是一个文档处理专家，用于插入、删除、检索知识库中的文档。
  调用我时，输入格式如下：
  【插入/删除/检索】：具体文档内容，请输入用户的原始文档内容，无需加工
```

### 联网搜索专家智能体

联网搜索专家智能体的作用是：当文档处理专家未检索到相关内容，或检索到的相关内容与用户原始问题相关性不高时，进行联网搜索。

以下是联网搜索专家智能体的配置文件

```yaml
  # 专业智能体 - 联网搜索专家
  search_expert:
    _type: tool_calling_agent
    tool_names:
      - web_search
    llm_name: expert_executor
    verbose: true
    handle_tool_errors: true
    description: |
      我是一个联网搜索专家，当文档处理专家未检索到相关内容或结果相关性不足时，负责从互联网上检索信息并返回相关片段。
      调用我时，输入格式如下：
      【联网搜索】：需要联网搜索的内容
```

### 回答专家智能体

回答专家智能体负责根据文档处理专家检索到的内容或联网搜索到的内容，以及用户原始问题，进行总结回答。

以下是回答专家智能体的配置文件

```yaml
# 专业智能体 - 回答专家
answer_expert:
_type: react_agent
tool_names:
  - no_op_tool
llm_name: expert_executor
verbose: true
handle_tool_errors: true
system_prompt: |
  你是一个回答专家，用户会输入一个问题，并且带有文档处理专家检索到的相关知识或者联网搜索专家搜索到的相关背景知识。
  请你对用户原始问题+相关知识进行整理、总结，生成最终回答，请务必保证最终回答准确、全面、专业。
  工具：{tools}
  工具名称：{tool_names}
  此工具仅作占位，你无需调用工具。
  请严格使用以下格式回复：
  Thought: 我现在知晓最终答案
  Final Answer: 你最终生成的回答
description: |
  我是一个回答专家，负责根据文档处理专家或联网搜索专家返回的内容进行整理、总结，生成最终回答。
  调用我时，输入格式如下：
  【问题】：用户原始的问题
  【相关背景知识】：文档处理专家或联网搜索专家返回的相关知识
```



## 🚀 快速部署

### 🏃‍♂️ 一键启动 (30秒部署)

```bash
# 1. 克隆项目
git clone https://github.com/HeKun-NVIDIA/hackathon_aiqtoolkit.git
cd hackathon_aiqtoolkit

# 2. 环境配置
cp .env.example .env
# 编辑.env文件，填入API密钥

# 3. 智能启动
./start.sh --mode production --config multi_agent
```
