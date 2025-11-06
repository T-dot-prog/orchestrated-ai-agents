"""
Test for Research Agent
"""
import pytest

from agents.research_agent import ResearchAgent
from memory.redis_memory import RedisMemory

import warnings
warnings.filterwarnings('ignore')

class TestResearch:
    """
    Initalize Reseach agent
    """

    @pytest.fixture
    def memory_client(self):
        """Memory instance for agent"""
        return RedisMemory()
    
    @pytest.fixture
    def evalautor_agent(self, memory_client):
        """Research agent initialization"""
        return ResearchAgent(memory_client= memory_client)
    
    
    def test_perform_search(self, evalautor_agent): 
        """Function for performing search"""
        results = evalautor_agent._perform_search("Latest advancement in explainable AI for deep learning models")

        assert isinstance(results, str) 


    @pytest.mark.asyncio
    async def test_execute(self, evalautor_agent):
        """test function to check the execution"""

        from uuid import uuid4
        query = "Latest advancement in explainable AI for deep learning models"
        input_data = {
            "query": query,
            "task_id": str(uuid4())
        }
        analysis = await evalautor_agent.execute(input_data)

        data = analysis['data']
        assert isinstance(analysis, dict)
        assert "success" in analysis
        assert analysis['success'] == True
        assert "query" in data
        assert "analysis" in data
        assert isinstance(data['analysis'], dict)
        assert isinstance(data['analysis']['summary'], str)
        assert "sources" in data['analysis']
        assert isinstance(data['analysis']['sources'], list)
