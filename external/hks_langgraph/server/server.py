import os

from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from langchain.chat_models import init_chat_model
from .document_tools import insert_docs, retrieve_docs, delete_docs
from .web_search_tools import web_search
from dotenv import load_dotenv
load_dotenv()

# ======================
# LLM配置
# ======================
master_llm = init_chat_model(
    model_provider="openai",
    model=os.getenv("DASHSCOPE_MODEL"),
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    temperature=0.7,
)

expert_llm = init_chat_model(
    model_provider="openai",
    model=os.getenv("DASHSCOPE_MODEL"),
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    temperature=0.7,
)


# ======================
# 专家 Agent 定义
# ======================

document_expert = create_react_agent(
    model=expert_llm,
    tools=[insert_docs, retrieve_docs, delete_docs],
    name="文档处理专家智能体",
    debug=True,
    prompt="你是一个文档处理专家，你擅长调用各种工具插入、删除和检索知识库中的文档。用户的请求通常是插入/删除/检索文档，请你务必调用工具来完成。"
)

search_expert = create_react_agent(
    model=expert_llm,
    tools=[web_search],
    name="搜索专家智能体",
    debug=True,
    prompt="你是一个联网搜索专家，请你务必调用联网搜索工具搜索获取相关信息。"
)

answer_expert = create_react_agent(
    model=expert_llm,
    tools=[],
    name="回答专家智能体",
    debug=True,
    prompt="""
你是一个回答专家，用户会输入一个问题，并且带有文档处理专家检索到的相关知识或者联网搜索专家搜索到的相关背景知识。
请你对用户原始问题+相关知识进行整理、总结，生成最终回答，请务必保证最终回答准确、全面、专业。
"""
)

# ======================
# 主编排 (Supervisor)
# ======================

supervisor = create_supervisor(
    agents=[document_expert, search_expert, answer_expert],
    output_mode="full_history",
    model=master_llm,
    supervisor_name="主决策者",
    add_handoff_messages=True,
    handoff_tool_prefix="主决策者调用-",
    add_handoff_back_messages=False,
    prompt="""
你是一位管理着一个由专业人工智能专家组成的团队的编排大师，负责接收用户请求并决定路由。

你的团队由以下专家组成：
1. 文档处理专家(document_expert)
   - 功能：用于插入、删除、检索知识库中的文档。
   - 调用方式：操作+用户的原始文档内容，无需加工文档内容。格式示例：
     {"action: "插入/删除/检索", "content": "文档内容"}

2. 搜索专家(search_expert)
   - 功能：当文档处理专家未检索到相关内容或结果相关性不足时，从互联网上检索信息并返回相关片段。
   - 调用方式：操作+需要联网搜索的内容。格式示例：
     {"action": "联网搜索", "content": "需要联网搜索的内容"}

3. 回答专家(answer_expert)
   - 功能：根据文档处理专家或联网搜索专家返回的内容整理、总结，生成最终回答。
   - 调用方式：输入问题和相关背景知识。格式示例：
     {"question": "用户提出的问题", "background": "文档处理专家或搜索专家返回的内容"}

请务必严格按照以下规则进行调度：
- 如果用户请求是“插入文档/删除文档”，将请求交给 document_expert 来执行。
- 如果用户请求是“提出问题”，先调用 document_expert 进行检索这个问题的相关背景知识。
  - 如果文档处理专家返回的背景知识不足或不相关，再调用 search_expert 进行联网搜索。
- 将最终检索或联网搜索结果交给 answer_expert 整理并回答，你无需整理answer_expert返回的内容，直接将内容返回给用户即可。
"""
).compile()