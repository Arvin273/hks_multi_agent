from typing import Dict, Any, List
from tavily import TavilyClient
from pydantic import BaseModel, Field
from aiq.builder.builder import Builder
from aiq.builder.function_info import FunctionInfo
from aiq.cli.register_workflow import register_function
from aiq.data_models.function import FunctionBaseConfig

# 初始化Tavily客户端
tavily_client = TavilyClient(
    api_key="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"
)


def _generate_summary(results: List[Dict[str, Any]], query: str) -> str:
    """从搜索结果生成摘要"""
    if not results:
        return f"No relevant information found for '{query}'."

    # 取前3个结果的内容片段
    summary_parts = []
    for i, result in enumerate(results[:3]):
        content = result.get("content", "").strip()
        if content:
            # 截取前200个字符
            snippet = content[:200] + "..." if len(content) > 200 else content
            summary_parts.append(f"{i + 1}. {snippet}")

    if summary_parts:
        return f"Based on search results for '{query}':\n\n" + "\n\n".join(summary_parts)
    else:
        return f"Found search results for '{query}', but content summary is not available."


def _format_search_result(response: Dict[str, Any], query: str) -> Dict[str, Any]:
    """格式化搜索结果"""
    try:
        results = response.get("results", [])
        answer = response.get("answer", "")

        # 格式化结果列表
        formatted_results = []
        for result in results:
            formatted_results.append({
                "title": result.get("title", ""),
                "content": result.get("content", ""),
            })

        # 生成摘要答案
        if answer:
            summary = answer
        elif formatted_results:
            # 如果没有直接答案，从结果中生成摘要
            summary = _generate_summary(formatted_results, query)
        else:
            summary = f"No relevant information found for '{query}'."

        return {
            "query": query,
            "answer": summary,
            "results": formatted_results,
            "total_results": len(formatted_results)
        }

    except Exception as e:
        return {
            "query": query,
            "answer": f"Result processing failed: {str(e)}",
            "results": [],
            "error": str(e)
        }


# 联网搜索工具输入模型
class WebSearchInput(BaseModel):
    docs: str = Field(..., description="这是一个字符串，请直接输入需要联网搜索的内容")


class WebSearchConfig(FunctionBaseConfig, name="web_search"):
    """联网搜索工具配置"""
    pass


@register_function(config_type=WebSearchConfig)
async def web_search(config: WebSearchConfig, builder: Builder):
    """执行联网搜索工具"""

    async def _web_search(input_data: WebSearchInput) -> str:
        """内部联网搜索工具，执行实际的搜索并返回结果"""
        try:
            # 获取用户输入的搜索查询
            query = input_data.docs.strip()

            if not query:
                return "搜索内容不能为空，请提供有效的搜索关键词或问题"

            # 使用Tavily客户端进行搜索
            search_response = tavily_client.search(
                query=query,
                max_results=3,
                search_depth="basic",
                include_answer=True,
                include_raw_content=False
            )

            # 格式化搜索结果
            formatted_result = _format_search_result(search_response, query)
            return str(formatted_result)

        except Exception as e:
            return f"搜索过程中发生错误: {str(e)}"

    yield FunctionInfo.from_fn(
        _web_search,
        description="此工具用于联网搜索，可以获取最新的信息和数据",
        input_schema=WebSearchInput
    )
