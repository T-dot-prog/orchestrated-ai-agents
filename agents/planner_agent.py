"""
Planner Agent for orchestrating workflows and agent collaboration.
"""
from typing import Any, Dict, List

from utils.helpers import format_agent_response

from .base_agent import BaseAgent

class PlannerAgent(BaseAgent):
    """Agent responsible for planning and orchestrating agent workflows."""

    def __init__(self, memory_client: Any, available_agents: List[str], **kwargs):
        """
        Initialize Planner Agent.
        
        Args:
            memory_client (Any): Memory client instance
            available_agents (List[str]): List of available agent names
            **kwargs: Additional arguments for BaseAgent
        """
        system_prompt = f"""You are a strategic planner specializing in orchestrating complex 
        workflows. Your task is to analyze requirements and create optimal execution plans 
        using these available agents: {', '.join(available_agents)}."""
        
        super().__init__(
            name="planner_agent",
            system_prompt=system_prompt,
            memory_client=memory_client,
            temperature=0.4,  # Moderate temperature for creative but focused planning
            **kwargs
        )
        
        self.available_agents = available_agents

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute planning task.
        
        Args:
            input_data (Dict[str, Any]): Input data containing task requirements
            
        Returns:
            Dict[str, Any]: Execution plan
        """
        try:
            task = input_data.get("task")
            if not task:
                return format_agent_response(
                    success=False,
                    error="No task provided for planning"
                )

            constraints = input_data.get("constraints", {})
            context = input_data.get("context", {})
            
            # Generate execution plan
            plan = await self._create_execution_plan(task, constraints, context)
            
            # Save plan
            self.save_state(
                state_id=input_data.get("task_id", "latest"),
                state={"task": task, "plan": plan}
            )
            
            return format_agent_response(
                success=True,
                data=plan
            )
            
        except Exception as e:
            return format_agent_response(
                success=False,
                error=f"Planning failed: {str(e)}"
            )

    async def _create_execution_plan(
        self,
        task: str,
        constraints: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create detailed execution plan.
        
        Args:
            task (str): Task description
            constraints (Dict[str, Any]): Task constraints
            context (Dict[str, Any]): Additional context
            
        Returns:
            Dict[str, Any]: Structured execution plan
        """
        prompt = self._create_planning_prompt(task, constraints, context)
        plan_response = await self._call_llm(self._create_messages(prompt))
        
        # Structure the plan
        return self._structure_plan(plan_response, task= task)

    def _create_planning_prompt(
        self,
        task: str,
        constraints: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """
        Create prompt for plan generation.
        
        Args:
            task (str): Task description
            constraints (Dict[str, Any]): Task constraints
            context (Dict[str, Any]): Additional context
            
        Returns:
            str: Formatted prompt
        """
        constraints_str = "\n".join(f"- {k}: {v}" for k, v in constraints.items())
        context_str = "\n".join(f"- {k}: {v}" for k, v in context.items())
        
        return f"""Create an execution plan for the following task using available agents 
        ({', '.join(self.available_agents)}):

        Task:
        {task}

        Constraints:
        {constraints_str}

        Context:
        {context_str}

        Provide:
        1. High-level strategy
        2. Step-by-step execution plan
        3. Agent assignments for each step
        4. Expected outputs and success criteria
        5. Fallback/recovery plans
        """

    def _structure_plan(self, plan_text: str, task: str) -> Dict[str, Any]:
        """
        Structure the planning response.
        
        Args:
            plan_text (str): Raw plan from LLM
            task (str): Original task
            
        Returns:
            Dict[str, Any]: Structured plan
        """
        return {
            "task": task,
            "plan": plan_text,
            "agents_involved": self._extract_agents(plan_text),
            "estimated_steps": len(self._extract_steps(plan_text)),
            "timestamp": self._get_timestamp()
        }

    def _extract_agents(self, plan_text: str) -> List[str]:
        """
        Extract agent names from plan text.
        
        Args:
            plan_text (str): Plan text to analyze
            
        Returns:
            List[str]: List of agent names found
        """
        agents = []
        for agent in self.available_agents:
            if agent.lower() in plan_text.lower():
                agents.append(agent)
        return agents

    def _extract_steps(self, plan_text: str) -> List[str]:
        """
        Extract execution steps from plan text.
        
        Args:
            plan_text (str): Plan text to analyze
            
        Returns:
            List[str]: List of execution steps
        """
        steps = []
        lines = plan_text.split("\n")
        
        for line in lines:
            # Look for numbered steps or bullet points
            line = line.strip()
            if (line.startswith(("1.", "2.", "3.", "4.", "5.", "-", "•")) and
                    len(line) > 2):
                steps.append(line)
                
        return steps

    def _get_timestamp(self) -> str:
        """
        Get current timestamp string.
        
        Returns:
            str: Formatted timestamp
        """
        from datetime import datetime
        return datetime.utcnow().isoformat()