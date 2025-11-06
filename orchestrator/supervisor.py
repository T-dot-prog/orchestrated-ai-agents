"""
Supervisor for orchestrating agent workflows using LangGraph.
"""
import asyncio
from typing import Any, Dict, List, Optional, Set, Tuple

from langgraph.graph import StateGraph , END
from utils.config import settings
from utils.helpers import format_agent_response
from utils.logger import setup_logging

logger = setup_logging()

class Supervisor:
    """Orchestrator for agent workflows using LangGraph."""

    def __init__(self, agents: Dict[str, Any], memory_client: Any):
        """
        Initialize supervisor.
        
        Args:
            agents (Dict[str, Any]): Dictionary of available agents
            memory_client (Any): Memory client instance
        """
        self.agents = agents
        self.memory = memory_client
        self.graph = None
        self.current_workflow_id: Optional[str] = None

    async def create_workflow(self, task: Dict[str, Any]) -> str:
        """
        Create new workflow from task.
        
        Args:
            task (Dict[str, Any]): Task specification
            
        Returns:
            str: Workflow ID
        """
        try:
            # Get execution plan from planner
            plan = await self._get_execution_plan(task)
            
            # Create workflow graph
            self.graph = await  self._build_graph(plan)
            
            # Generate workflow ID
            self.current_workflow_id = self._generate_workflow_id()
            
            # Save initial state
            self.memory.save_workflow_state(
                self.current_workflow_id,
                {
                    "status": "initialized",
                    "plan": plan,
                    "task": task
                }
            )
            
            return self.current_workflow_id
            
        except Exception as e:
            logger.error(f"Failed to create workflow: {str(e)}")
            raise

    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Execute workflow by ID.
        
        Args:
            workflow_id (str): Workflow identifier
            
        Returns:
            Dict[str, Any]: Workflow results
        """
        try:
            # Load workflow state
            state = self.memory.get_workflow_state(workflow_id)
            if not state:
                raise ValueError(f"No workflow found with ID: {workflow_id}")
            
            # Set current workflow
            self.current_workflow_id = workflow_id
            
            # Execute graph
            results = await self._execute_graph(state)
            
            # Update workflow state
            state.update({
                "status": "completed",
                "results": results
            })
            self.memory.save_workflow_state(workflow_id, state)
            
            return format_agent_response(
                success=True,
                data=results
            )
            
        except Exception as e:
            error_msg = f"Workflow execution failed: {str(e)}"
            logger.error(error_msg)
            
            # Update workflow state with error
            if self.current_workflow_id:
                self.memory.save_workflow_state(
                    self.current_workflow_id,
                    {
                        "status": "failed",
                        "error": error_msg
                    }
                )
            
            return format_agent_response(
                success=False,
                error=error_msg
            )

    async def _get_execution_plan(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get execution plan from planner agent.
        
        Args:
            task (Dict[str, Any]): Task specification
            
        Returns:
            Dict[str, Any]: Execution plan
        """
        if "planner_agent" not in self.agents:
            raise ValueError("Planner agent not available")
            
        planner = self.agents["planner_agent"]
        response = await planner.execute(task)
        
        if not response["success"]:
            raise Exception(f"Planning failed: {response.get('error')}")
            
        return response["data"]

    async def _build_graph(self, plan: Dict[str, Any]) -> StateGraph:
        """
        Build StateGraph from execution plan.
        
        Args:
            plan (Dict[str, Any]): Execution plan
            
        Returns:
            StateGraph: Constructed workflow graph
        """
        graph = StateGraph()
        
        # Extract nodes and edges from plan
        nodes, edges = self._extract_graph_structure(plan)
        
        # Add nodes
        for node in nodes:
            graph.add_node(node, self._create_node_handler(node))
            
        # Add edges
        for start, end, condition in edges:
            if condition:
                graph.add_conditional_edges(
                    start,
                    condition,
                    {True: [end], False: [self._get_fallback_node(end)]}
                )
            else:
                graph.add_edge(start, end)
                
        # Add end state
        graph.add_node(END)
        graph.add_edge(nodes[-1], END)
        
        return graph

    async def _execute_graph(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute workflow graph.
        
        Args:
            state (Dict[str, Any]): Current workflow state
            
        Returns:
            Dict[str, Any]: Execution results
        """
        if not self.graph:
            raise ValueError("No workflow graph defined")
            
        # Initialize execution context
        context = {
            "workflow_id": self.current_workflow_id,
            "state": state,
            "results": {}
        }
        
        # Execute graph
        final_state = await self.graph.aexecute(context)
        
        return final_state["results"]

    def _extract_graph_structure(
        self,
        plan: Dict[str, Any]
    ) -> Tuple[List[str], List[Tuple[str, str, Optional[str]]]]:
        """
        Extract nodes and edges from plan.
        
        Args:
            plan (Dict[str, Any]): Execution plan
            
        Returns:
            Tuple[List[str], List[Tuple[str, str, Optional[str]]]]: 
            Nodes and edges with conditions
        """
        nodes = []
        edges = []
        
        # Extract steps and dependencies
        steps = self._extract_steps(plan)
        for i, step in enumerate(steps):
            nodes.append(f"step_{i}")
            if i > 0:
                edges.append((f"step_{i-1}", f"step_{i}", None))
                
        return nodes, edges

    def _create_node_handler(self, node: str) -> Any:
        """
        Create handler function for graph node.
        
        Args:
            node (str): Node identifier
            
        Returns:
            Any: Node handler function
        """
        async def handler(state: StateGraph) -> StateGraph:
            try:
                # Extract agent and task for this node
                agent_name = self._get_agent_for_node(node, StateGraph.get("plan", {}))
                if not agent_name or agent_name not in self.agents:
                    raise ValueError(f"No agent found for node {node}")
                    
                # Execute agent
                agent = self.agents[agent_name]
                result = await agent.execute(state)
                
                # Update state
                if result["success"]:
                    state["results"][node] = result["data"]
                else:
                    raise Exception(f"Agent execution failed: {result.get('error')}")
                    
                return state
                
            except Exception as e:
                logger.error(f"Node {node} execution failed: {str(e)}")
                if self._should_retry(node, state):
                    return await self._retry_node(node, state)
                raise
                
        return handler

    def _get_agent_for_node(self, node: str, plan: Dict[str, Any]) -> Optional[str]:
        """
        Determine which agent should handle a node.
        
        Args:
            node (str): Node identifier
            plan (Dict[str, Any]): Execution plan
            
        Returns:
            Optional[str]: Agent name if found
        """
        # This is a simplified version - in practice, would parse the plan
        # to match nodes to agents based on the plan structure
        for agent_name in self.agents:
            if agent_name in str(plan.get("agents_involved", [])):
                return agent_name
        return None

    def _get_fallback_node(self, node: str) -> str:
        """
        Get fallback node for error handling.
        
        Args:
            node (str): Failed node identifier
            
        Returns:
            str: Fallback node identifier
        """
        return f"{node}_fallback"

    def _should_retry(self, node: str, state: Dict[str, Any]) -> bool:
        """
        Determine if node should be retried.
        
        Args:
            node (str): Failed node identifier
            state (Dict[str, Any]): Current state
            
        Returns:
            bool: Whether to retry
        """
        retries = state.get("retries", {}).get(node, 0)
        return retries < settings.MAX_RETRIES

    async def _retry_node(self, node: str, state: Dict[str, Any]) -> StateGraph:
        """
        Retry failed node execution.
        
        Args:
            node (str): Failed node identifier
            state (Dict[str, Any]): Current state
            
        Returns:
            State: Updated state after retry
        """
        # Increment retry count
        state.setdefault("retries", {})
        state["retries"][node] = state["retries"].get(node, 0) + 1
        
        # Retry with exponential backoff
        await asyncio.sleep(2 ** state["retries"][node])
        
        # Retry handler
        handler = self._create_node_handler(node)
        return await handler(state)

    def _generate_workflow_id(self) -> str:
        """
        Generate unique workflow ID.
        
        Returns:
            str: Workflow ID
        """
        import uuid
        return str(uuid.uuid4())