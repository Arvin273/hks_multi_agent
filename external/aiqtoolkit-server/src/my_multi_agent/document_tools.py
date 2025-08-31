"""
多智能体系统的自定义工具实现
"""
import logging
from pydantic import BaseModel, Field

from aiq.builder.builder import Builder
from aiq.builder.function_info import FunctionInfo
from aiq.cli.register_workflow import register_function
from aiq.data_models.function import FunctionBaseConfig

logger = logging.getLogger(__name__)

# -------------------------------------向量知识库工具--------------------------------
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma
import dashscope
from langchain_dashscope import DashScopeEmbeddings

# 先设置全局API密钥
dashscope.api_key = "sk-84adb09076ae4093add2d94cc2bfb61c"

# 定义嵌入模型
my_embedding = DashScopeEmbeddings(
    model="text-embedding-v4",
)

# 创建Chroma操作客户端
chroma_client = Chroma(
    collection_name="collection-0825",
    embedding_function=my_embedding,
    persist_directory="./chroma_db",
)

# 插入文档工具输入模型
class InsertDocsInput(BaseModel):
    docs: str = Field(..., description="这是一个字符串，请直接输入用户的原始文档内容，无需加工，如果有多条，请使用换行符进行分割")

class InsertDocsConfig(FunctionBaseConfig, name="insert_docs"):
    """插入文档工具配置"""
    pass

@register_function(config_type=InsertDocsConfig)
async def insert_docs(config: InsertDocsConfig, builder: Builder):
    """执行插入文档工具"""

    async def _insert_docs(input_data: InsertDocsInput) -> str:
        """内部插入文档工具"""
        # 定义字符分割器
        try:
            splitter = CharacterTextSplitter(
                separator="\n",
            )
            documents = splitter.create_documents([input_data.docs])
            chroma_client.add_documents(documents)
            return "插入成功"
        except Exception as e:
            print("Error: ", e)
            return f"插入失败{e}"

    yield FunctionInfo.from_fn(
        _insert_docs,
        description="将一条或多条文档插入到知识库中",
        input_schema=InsertDocsInput
    )

# 检索文档工具输入模型
class RetrieveDocsInput(BaseModel):
    query: str = Field(..., description="这是一个字符串，请直接输入用户的原始文档内容，无需加工")

class RetrieveDocsConfig(FunctionBaseConfig, name="retrieve_docs"):
    """检索文档工具配置"""
    pass

@register_function(config_type=RetrieveDocsConfig)
async def retrieve_docs(config: RetrieveDocsConfig, builder: Builder):
    """执行检索文档工具"""

    async def _retrieve_docs(input_data: RetrieveDocsInput) -> str:
        """内部检索文档工具"""
        try:
            docs = chroma_client.similarity_search_with_relevance_scores(
                input_data.query, 
                k=3, 
                score_threshold=0.5
            )
            context = "\n".join(list(map(lambda x: x[0].page_content, docs)))
            return context if context else "未找到相关文档"
        except Exception as e:
            print("Error: ", e)
            return f"检索失败{e}"

    yield FunctionInfo.from_fn(
        _retrieve_docs,
        description="根据用户的原始问题从知识库中检索相关文档",
        input_schema=RetrieveDocsInput
    )

# 删除文档工具输入模型
class DeleteDocsInput(BaseModel):
    docs: str = Field(..., description="这是一个字符串，请直接输入用户的原始文档内容，无需加工")

class DeleteDocsConfig(FunctionBaseConfig, name="delete_docs"):
    """删除文档工具配置"""
    pass

@register_function(config_type=DeleteDocsConfig)
async def delete_docs(config: DeleteDocsConfig, builder: Builder):
    """执行删除文档工具"""

    async def _delete_docs(input_data: DeleteDocsInput) -> str:
        """内部删除文档工具"""
        try:
            docs = chroma_client.similarity_search_with_relevance_scores(
                input_data.docs, 
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
            return f"删除失败{e}"

    yield FunctionInfo.from_fn(
        _delete_docs,
        description="根据文档内容从知识库中删除相关文档",
        input_schema=DeleteDocsInput
    )

# -------------------------------------空工具--------------------------------
class NoOpToolInput(BaseModel):
    pass

class NoOpToolConfig(FunctionBaseConfig, name="no_op_tool"):
    pass

@register_function(config_type=NoOpToolConfig)
async def no_op_tool(config: NoOpToolConfig, builder: Builder):
    async def _no_op_tool(input_data: NoOpToolInput) -> str:
        """
        空操作工具 - 不执行任何实际操作
        """
        return "This tool does nothing."

    yield FunctionInfo.from_fn(
        _no_op_tool,
        description="此为空工具，仅做占位使用，任何时候无需调用此工具。",
        input_schema=NoOpToolInput
    )