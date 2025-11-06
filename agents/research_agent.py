"""
Research Agent for gathering information and context.
"""
from typing import Any, Dict, List

from langchain_community.tools import DuckDuckGoSearchResults
from utils.helpers import chunk_text, format_agent_response, convert_str_to_list

from base_agent import BaseAgent

class ResearchAgent(BaseAgent):
    """Agent responsible for web research and information gathering."""

    def __init__(self, memory_client: Any, **kwargs):
        """
        Initialize Research Agent.
        
        Args:
            memory_client (Any): Memory client instance
            **kwargs: Additional arguments for BaseAgent
        """
        system_prompt = """You are a research agent specializing in gathering and analyzing information 
        from various sources. Your task is to search for relevant information and provide 
        comprehensive, well-structured summaries."""
        
        super().__init__(
            name="research_agent",
            system_prompt=system_prompt,
            memory_client=memory_client,
            temperature=0.5,
            **kwargs
        )
        
        # Initialize search tool
        self.search_tool = DuckDuckGoSearchResults()

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute research task.
        
        Args:
            input_data (Dict[str, Any]): Input data containing query and parameters
            
        Returns:
            Dict[str, Any]: Research results and analysis
        """
        try:
            query = input_data.get("query")
            if not query:
                return format_agent_response(
                    success=False,
                    error="No query provided"
                )

            # Perform search
            search_results =  self._perform_search(query)

            #Conversion
            search_results = convert_str_to_list(search_results)
            
            # Analyze results
            analysis = await self._analyze_results(query, search_results)
            
            # Save research results
            self.save_state(
                state_id=input_data.get("task_id", "latest"),
                state={"query": query, "results": analysis}
            )
            
            return format_agent_response(
                success= True,
                data={
                    "query": query,
                    "analysis": analysis,
                    "source_count": len(search_results)
                }
            )
            
        except Exception as e:
            return format_agent_response(
                success=False,
                error=f"Research failed: {str(e)}"
            )

    def _perform_search(self, query: str) -> str:
        """
        Perform web search using DuckDuckGo.
        
        Args:
            query (str): Search query
            
        Returns:
            List[Dict[str, Any]]: Search results
        """
        try:
            result = self.search_tool.run(query)
            return result

        except Exception as e:
            print(f"Search Tool failed: {e}")
        

        

    async def _analyze_results(self, query: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze search results.
        
        Args:
            query (str): Original search query
            results (List[Dict[str, Any]]): Search results to analyze
            
        Returns:
            Dict[str, Any]: Analyzed and structured information
        """
        if not results:
            return {"summary": "No results found", "key_points": []}

        # Combine all results into a single context
        combined_text = "\n\n".join(
            [f"Source {i+1}: {result['link']}\n{result['snippet']}"
             for i, result in enumerate(results)]
        )

        # Split into chunks if too long
        chunks = chunk_text(combined_text)
        
        # Analyze each chunk
        analysis_prompt = f"""
        Analyze the following information related to the query: "{query}"
        
        {chunks[0]}
        
        Provide:
        1. A concise summary
        2. Key points and findings
        3. Reliability assessment of sources
        """
        
        analysis_response = await self._call_llm(
            self._create_messages(analysis_prompt)
        )
        
        # Structure the response
        return {
            "summary": analysis_response,
            "sources": [result["link"] for result in results],
            "query": query
        }