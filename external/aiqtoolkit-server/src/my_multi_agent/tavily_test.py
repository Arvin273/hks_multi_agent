from typing import Dict, Any, List

from tavily import TavilyClient

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
                "url": result.get("url", ""),
                "content": result.get("content", ""),
                "score": result.get("score", 0)
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

tavily_client = TavilyClient(
    api_key="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"
)

response = tavily_client.search(
    query="蔡建国是谁",
    max_results=3,
    search_depth="basic",
    include_answer=True,
    include_raw_content=False
)

print(str(_format_search_result(response, "蔡建国是谁")))