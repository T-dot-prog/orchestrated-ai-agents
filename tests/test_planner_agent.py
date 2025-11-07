"""
Test function for Planner agent
"""
import pytest
from agents.planner_agent import PlannerAgent
from memory.redis_memory import RedisMemory
from utils.config import settings

@pytest.fixture
def memory_client():
    """Instance for memory client"""
    return RedisMemory()

@pytest.fixture
def planner_agent(memory_client):
    """Fixture for initializing the PlannerAgent."""
    available_agents = settings.AVAILABLE_AGENTS
    return PlannerAgent(memory_client=memory_client, available_agents=available_agents)

@pytest.mark.asyncio
async def test_execute_returns_dict(planner_agent):
    """Test that execute returns a dictionary."""
    input_data = {"task": "Test task"}
    result = await planner_agent.execute(input_data)
    assert isinstance(result, dict)

@pytest.mark.asyncio
async def test_execute_no_task(planner_agent):
    """Test that execute handles no task provided."""
    input_data = {}
    result = await planner_agent.execute(input_data)
    assert result["success"] is False
    assert "No task provided" in result["error"]

def test_create_planning_prompt(planner_agent):
    """Test the creation of a planning prompt."""
    task = "Develop a new feature."
    constraints = {"language": "Python"}
    context = {"framework": "FastAPI"}
    prompt = planner_agent._create_planning_prompt(task, constraints, context)
    assert task in prompt
    assert "Python" in prompt
    assert "FastAPI" in prompt

def test_extract_agents(planner_agent):
    """Test the extraction of agent names from plan text."""
    plan_text = "The code_agent will write the code, and the research_agent will gather information."
    agents = planner_agent._extract_agents(plan_text)
    assert "code_agent" in agents
    assert "research_agent" in agents

def test_extract_steps(planner_agent):
    """Test the extraction of execution steps from plan text."""
    plan_text = """
    1. Step one
    2. Step two
    - Step three
    • Step four
    """
    steps = planner_agent._extract_steps(plan_text)
    assert len(steps) == 4