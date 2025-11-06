"""
FastAPI application for the AI Agent Orchestration System.
"""
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils.config import settings
from utils.logger import setup_logging

logger = setup_logging()

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json"
)

# Request/Response Models
class TaskRequest(BaseModel):
    """Task request model."""
    task: str
    constraints: Optional[Dict] = None
    context: Optional[Dict] = None

class MemoryRequest(BaseModel):
    """Memory request model."""
    key: str

class FeedbackRequest(BaseModel):
    """Feedback request model."""
    workflow_id: str
    feedback: Dict
    rating: Optional[int] = None

# Initialize agents and supervisor
try:
    from agents.code_agent import CodeAgent
    from agents.evaluator_agent import EvaluatorAgent
    from agents.planner_agent import PlannerAgent
    from agents.research_agent import ResearchAgent
    from agents.summarize_agent import SummarizerAgent
    from memory.redis_memory import RedisMemory
    from orchestrator.supervisor import Supervisor

    # Initialize memory client
    memory_client = RedisMemory()

    # Initialize agents
    agents = {
        "research_agent": ResearchAgent(memory_client=memory_client),
        "summarizer_agent": SummarizerAgent(memory_client=memory_client),
        "code_agent": CodeAgent(memory_client=memory_client),
        "evaluator_agent": EvaluatorAgent(memory_client=memory_client),
        "planner_agent": PlannerAgent(
            memory_client=memory_client,
            available_agents=["research_agent", "summarizer_agent", "code_agent", "evaluator_agent"]
        )
    }

    # Initialize supervisor
    supervisor = Supervisor(agents=agents, memory_client=memory_client)
    logger.info("Initialized AI Agent Orchestration System")

except Exception as e:
    logger.error(f"Failed to initialize system: {str(e)}")
    raise

@app.post("/api/v1/run_agent/")
async def run_agent(request: TaskRequest):
    """
    Run agent orchestration workflow.
    
    Args:
        request (TaskRequest): Task specification
        
    Returns:
        dict: Workflow results
    """
    try:
        # Create workflow
        workflow_id = await supervisor.create_workflow({
            "task": request.task,
            "constraints": request.constraints or {},
            "context": request.context or {}
        })
        
        # Execute workflow
        results = await supervisor.execute_workflow(workflow_id)
        
        return {
            "workflow_id": workflow_id,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/api/v1/memory/{key}")
async def get_memory(key: str):
    """
    Get stored memory state.
    
    Args:
        key (str): Memory key
        
    Returns:
        dict: Stored state
    """
    try:
        state = memory_client.load_state(key)
        if not state:
            raise HTTPException(
                status_code=404,
                detail=f"No state found for key: {key}"
            )
        return state
        
    except Exception as e:
        logger.error(f"Failed to retrieve memory: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.post("/api/v1/feedback/")
async def submit_feedback(request: FeedbackRequest):
    """
    Submit feedback for a workflow.
    
    Args:
        request (FeedbackRequest): Feedback data
        
    Returns:
        dict: Confirmation
    """
    try:
        # Load workflow state
        state = memory_client.get_workflow_state(request.workflow_id)
        if not state:
            raise HTTPException(
                status_code=404,
                detail=f"No workflow found with ID: {request.workflow_id}"
            )
            
        # Add feedback to state
        state["feedback"] = request.feedback
        state["rating"] = request.rating
        
        # Save updated state
        memory_client.save_workflow_state(request.workflow_id, state)
        
        return {"message": "Feedback recorded successfully"}
        
    except Exception as e:
        logger.error(f"Failed to record feedback: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/api/v1/status/")
async def get_system_status():
    """
    Get system status.
    
    Returns:
        dict: System status information
    """
    try:
        return {
            "status": "healthy",
            "agents": list(agents.keys()),
            "memory_connected": memory_client.redis.ping()
        }
        
    except Exception as e:
        logger.error(f"Failed to get system status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )