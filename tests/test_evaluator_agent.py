"""
Pure Pytest for evaluator agent environment
"""
import pytest
from typing import Dict, Any
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

from agents.evaluator_agent import EvaluatorAgent
from memory.redis_memory import RedisMemory

class TestEvaluator:
    """Test Suite for Evaluator Agent"""


    @pytest.fixture
    def memory_client(self):
        """Instance for memory client"""
        return RedisMemory()

    @pytest.fixture
    def evaluator_agent(self, memory_client):
        "Function for init the evaluator agent"
        return EvaluatorAgent(memory_client= memory_client)
    
    @pytest.mark.asyncio
    async def test_execute_returns_dict(self, evaluator_agent):
        input_data = {"content": "Test content"}

        result = await evaluator_agent.execute(input_data)

        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_execute_with_general_type(self, evaluator_agent):
        "Test execution with general evaluation type"
        input_data = {
            "content": "Ai is taking over content creation",
            "type": "general"
        }

        result = await evaluator_agent.execute(input_data)

        assert isinstance(result, dict)

    def test_get_timstamp(self, evaluator_agent):
        """Test for timestamp check"""
        ts = evaluator_agent._get_timestamp()
        assert isinstance(ts, str)
        assert "T" in ts
        datetime.fromisoformat(ts)

    @pytest.mark.asyncio
    async def test_execute_with_research_type(self, evaluator_agent):
        """Test for Evaluator Agent"""
        input_data = {
            "content": "Ai is gonna take your job in future",
            "type": "research",
            "criteria": None
        }

        result = await evaluator_agent.execute(input_data)
        assert isinstance(result, dict)

        assert result['success'] == True

    @pytest.mark.asyncio 
    async def test_execute_all_parameters(self, evaluator_agent):
        """Test function for all combined parameters"""
        input_data = {
            "content": "def test(): pass",
            "type": "code",
            "criteria": ["functionality", "readability"],
            "task_id": "full_test_001"
        }

        result = await evaluator_agent.execute(input_data)

        assert isinstance(result, dict)
        assert "success" in result
        assert result['success'] == True
