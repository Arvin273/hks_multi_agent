from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma
import dashscope
from langchain_dashscope import DashScopeEmbeddings
from langchain.tools import tool
from pydantic import BaseModel, Field

# 设置全局API密钥
dashscope.api_key = "sk-84adb09076ae4093add2d94cc2bfb61c"

# 定义嵌入模型
my_embedding = DashScopeEmbeddings(
    model="text-embedding-v4",
)

# 创建Chroma操作客户端
chroma_client = Chroma(
    collection_name="collection-0827",
    embedding_function=my_embedding,
    persist_directory="./chroma_db",
)

# 插入文档工具输入模型
class InsertDocsInput(BaseModel):
    docs: str = Field(..., description="这是一个字符串，请直接输入用户的原始文档内容，无需加工，如果有多条，请使用换行符进行分割")

@tool("insert_docs", args_schema=InsertDocsInput)
def insert_docs(docs: str) -> str:
    """将一条或多条文档插入到知识库中。输入应为原始文档内容字符串，多条文档用换行符分割。"""
    try:
        # 定义字符分割器
        splitter = CharacterTextSplitter(
            separator="\n",
        )
        documents = splitter.create_documents([docs])
        chroma_client.add_documents(documents)
        return "插入成功"
    except Exception as e:
        print("Error: ", e)
        return f"插入失败: {str(e)}"

# 检索文档工具输入模型
class RetrieveDocsInput(BaseModel):
    query: str = Field(..., description="这是一个字符串，请直接输入用户的原始查询内容，无需加工")

@tool("retrieve_docs", args_schema=RetrieveDocsInput)
def retrieve_docs(query: str) -> str:
    """根据用户的原始问题从知识库中检索相关文档。输入应为查询字符串。"""
    try:
        docs = chroma_client.similarity_search_with_relevance_scores(
            query,
            k=3,
            score_threshold=0.5
        )
        context = "\n".join(list(map(lambda x: x[0].page_content, docs)))
        return context if context else "未找到相关文档"
    except Exception as e:
        print("Error: ", e)
        return f"检索失败: {str(e)}"

# 删除文档工具输入模型
class DeleteDocsInput(BaseModel):
    docs: str = Field(..., description="这是一个字符串，请直接输入用户要删除的原始文档内容，无需加工")

@tool("delete_docs", args_schema=DeleteDocsInput)
def delete_docs(docs: str) -> str:
    """根据文档内容从知识库中删除相关文档。输入应为要删除的文档内容字符串。"""
    try:
        docs = chroma_client.similarity_search_with_relevance_scores(
            docs,
            k=1,
            score_threshold=0.8
        )
        # 获取id
        ids = list(map(lambda x: x[0].id, docs))
        if len(ids) > 0 and ids[0] is not None:
            chroma_client.delete(ids)
            return "删除成功"
        else:
            return "未找到匹配的文档"
    except Exception as e:
        print("Error: ", e)
        return f"删除失败: {str(e)}"
