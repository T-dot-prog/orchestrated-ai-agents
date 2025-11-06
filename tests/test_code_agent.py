"""
Test for AI coding agent
"""
import pytest

@pytest.mark.asyncio
async def test_code_agent():
    "Test code for agent"
    from agents.code_agent import CodeAgent
    from memory.redis_memory import RedisMemory

    memory_client = RedisMemory()

    code_agent = CodeAgent(memory_client= memory_client)

    response = await code_agent.execute(input_data= {"type": "generate"})

    assert isinstance(response['success'], bool)
    assert response['success'] == False

    