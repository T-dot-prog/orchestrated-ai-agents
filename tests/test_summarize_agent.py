"""
Test Script for text summarization agent
"""

from agents.summarize_agent import SummarizerAgent
from memory.redis_memory import RedisMemory

import pytest
import warnings
from uuid import uuid4

warnings.filterwarnings('ignore')

class TestSummarization():
    """Class for Testing function of Summarization agent"""
    
    @pytest.fixture
    def memory_client(self):
        """Function for Saving and Calling State"""
        return RedisMemory()
    
    @pytest.fixture
    def summarize_agent(self):
        """Instance of Summarizer agent"""
        return SummarizerAgent(self.memory_client)
    
    @pytest.mark.asyncio
    async def test_execute_function(self, summarize_agent):
        """function for Test Execution"""
        input_data: dict = {
            "text": '''In a world driven by data and algorithms, the ability to transform raw information into meaningful insights defines progress. Every system, from autonomous vehicles to personalized recommendations, depends on the precision of its underlying functions. Testing ensures that logic holds firm under every scenario—expected or not. A single unchecked error can ripple across systems, altering predictions, outcomes, and decisions. Therefore, even the simplest function deserves careful validation before deployment. This practice forms the backbone of reliable software engineering and scientific computing.
''',    
            "mode": "concise",
            "max_length": 100,
            "task_id": str(uuid4())
        }

        result = await summarize_agent.execute(input_data)

        assert isinstance(result, dict)
        assert result.get("success") is False
        assert "data" in result and isinstance(result["data"], dict)
        assert "error" in result and result.get("error") is None

        data = result["data"]
        assert "summary" in data
        assert isinstance(data["summary"], dict)
        assert "text" in data["summary"]
        assert isinstance(data["summary"]["text"], str)
        assert len(data["summary"]["text"]) > 0
        assert "original_length" in data
        assert isinstance(data["original_length"], int)
        assert "summary_length" in data
        assert isinstance(data["summary_length"], int)