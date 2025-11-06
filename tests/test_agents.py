"""
Tests for the AI Agent Orchestration System.
"""
import pytest
from fastapi.testclient import TestClient

from app.api import app

client = TestClient(app)

def test_system_status():
    """Test system status endpoint."""
    response = client.get("/api/v1/status/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert isinstance(data["agents"], list)

@pytest.mark.asyncio
async def test_research_agent():
    """Test research agent execution."""
    from agents.research_agent import ResearchAgent
    from memory.redis_memory import RedisMemory
    
    memory_client = RedisMemory()
    agent = ResearchAgent(memory_client=memory_client)
    
    response = await agent.execute({
        "query": "Latest developments in AI orchestration",
        "task_id": "test_task"
    })
    
    assert response["success"]
    assert "analysis" in response["data"]
    assert isinstance(response["data"]["source_count"], int)

@pytest.mark.asyncio
async def test_workflow_execution():
    """Test complete workflow execution."""
    request_data = {
        "task": "Research and summarize AI orchestration patterns",
        "constraints": {
            "max_sources": 5,
            "summary_length": "medium"
        }
    }
    
    response = client.post("/api/v1/run_agent/", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "workflow_id" in data
    assert "results" in data

def test_memory_operations():
    """Test memory operations."""
    from memory.redis_memory import RedisMemory
    
    memory_client = RedisMemory()
    test_key = "test_state"
    test_data = {"key": "value"}
    
    # Test save
    assert memory_client.save_state(test_key, test_data)
    
    # Test load
    loaded_data = memory_client.load_state(test_key)
    assert loaded_data == test_data
    
    # Test clear
    assert memory_client.clear_state(test_key)
    assert memory_client.load_state(test_key) is None

@pytest.mark.asyncio
async def test_planner_agent():
    """Test planner agent execution."""
    from agents.planner_agent import PlannerAgent
    from memory.redis_memory import RedisMemory
    
    memory_client = RedisMemory()
    agent = PlannerAgent(
        memory_client=memory_client,
        available_agents=["research_agent", "summarizer_agent"]
    )
    
    response = await agent.execute({
        "task": "Research and summarize a topic",
        "constraints": {"time_limit": "1h"},
        "task_id": "test_planning"
    })
    
    assert response["success"]
    assert "plan" in response["data"]
    assert isinstance(response["data"]["agents_involved"], list)

def test_feedback_submission():
    """Test feedback submission."""
    feedback_data = {
        "workflow_id": "test_workflow",
        "feedback": {
            "quality": "good",
            "suggestions": "faster execution"
        },
        "rating": 4
    }
    
    response = client.post("/api/v1/feedback/", json=feedback_data)
    assert response.status_code == 200


if __name__ == "__main__":
    test_system_status()