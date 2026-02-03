try:
    from duckduckgo_search import DDGS
    HAS_INTERNET = True
except ImportError:
    HAS_INTERNET = False

from typing import List, Dict, Any

class ToolBelt:
    def __init__(self):
        self.ddgs = DDGS() if HAS_INTERNET else None

    def search_web(self, query: str, max_results: int = 3) -> str:
        """
        Searches the internet and returns a summarized string of results.
        """
        if not self.ddgs:
            return "Internet access unavailable."
        
        try:
            results = list(self.ddgs.text(query, max_results=max_results))
            if not results:
                return "No results found."
            
            summary = f"Search Results for '{query}':\n"
            for i, r in enumerate(results):
                summary += f"{i+1}. {r['title']}: {r['body']}\n"
            return summary
        except Exception as e:
            return f"Search failed: {e}"

    def get_tool_descriptions(self) -> str:
        return """
        - search_web(query): access real-time information from the internet.
        """

global_tools = ToolBelt()
