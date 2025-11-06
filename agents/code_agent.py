"""
Code Agent for generating and reviewing code.
"""
from typing import Any, Dict, List, Optional
import warnings

from langchain_experimental.utilities import PythonREPL
from utils.helpers import format_agent_response

from base_agent import BaseAgent

from utils.logger import logger

warnings.filterwarnings('ignore')

class CodeAgent(BaseAgent):
    """Agent responsible for code generation and review."""

    def __init__(self, memory_client: Any, **kwargs):
        """
        Initialize Code Agent.
        
        Args:
            memory_client (Any): Memory client instance
            **kwargs: Additional arguments for BaseAgent
        """
        system_prompt = """You are an expert software engineer specializing in code generation, 
        review, and optimization. Write clean, efficient, and well-documented code following 
        best practices and design patterns."""
        
        super().__init__(
            name="code_agent",
            system_prompt=system_prompt,
            memory_client=memory_client,
            temperature=0.2,  # Lower temperature for more precise code generation
            **kwargs
        )
        
        # Initialize Python REPL tool for code execution
        self.repl_tool = PythonREPL()

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute code-related task.
        
        Args:
            input_data (Dict[str, Any]): Input data containing task details
            
        Returns:
            Dict[str, Any]: Code generation or review results
        """
        try:
            task_type = input_data.get("type", "generate")
            if task_type not in ["generate", "review", "optimize"]:
                return format_agent_response(
                    success=False,
                    error="Invalid task type"
                )

            if task_type == "generate":
                return await self._generate_code(input_data)
            elif task_type == "review":
                return await self._review_code(input_data)
            else:  # optimize
                return await self._optimize_code(input_data)
            
        except Exception as e:
            return format_agent_response(
                success=False,
                error=f"Code agent task failed: {str(e)}"
            )

    async def _generate_code(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate code based on requirements.
        
        Args:
            input_data (Dict[str, Any]): Input containing requirements
            
        Returns:
            Dict[str, Any]: Generated code and documentation
        """
        requirements = input_data.get("requirements")
        language = input_data.get("language", "python")
        include_tests = input_data.get("include_tests", True)
        
        if not requirements:
            return format_agent_response(
                success=False,
                error="No requirements provided"
            )

        prompt = f"""Generate {language} code based on these requirements:

        Requirements:
        {requirements}

        Provide:
        1. Well-structured, documented code
        2. Brief explanation of implementation
        3. Usage examples
        {"4. Unit tests" if include_tests else ""}
        """

        response = await self._call_llm(self._create_messages(prompt))
        
        # Save generated code
        self.save_state(
            state_id=input_data.get("task_id", "latest_generate"),
            state={
                "code": response,
                "language": language,
                "requirements": requirements
            }
        )
        
        return format_agent_response(
            success=True,
            data={
                "code": response,
                "language": language,
                "includes_tests": include_tests
            }
        )

    async def _review_code(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review code for quality and issues.
        
        Args:
            input_data (Dict[str, Any]): Input containing code to review
            
        Returns:
            Dict[str, Any]: Review results and recommendations
        """
        code = input_data.get("code")
        language = input_data.get("language", "python")
        
        if not code:
            return format_agent_response(
                success=False,
                error="No code provided for review"
            )

        prompt = f"""Review the following {language} code:

        {code}

        Provide:
        1. Code quality assessment
        2. Potential issues or bugs
        3. Style and best practices review
        4. Specific improvement recommendations
        """

        review = await self._call_llm(self._create_messages(prompt))
        

        # Save the state
        self.save_state(
            state_id= input_data.get("task_id", "latest_review_code"),
            state= {
                "review": review,
                "language": language
            }
        )

        return format_agent_response(
            success=True,
            data={
                "review": review,
                "language": language
            }
        )

    async def _optimize_code(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize code for better performance.
        
        Args:
            input_data (Dict[str, Any]): Input containing code to optimize
            
        Returns:
            Dict[str, Any]: Optimized code and improvements
        """
        code = input_data.get("code")
        language = input_data.get("language", "python")
        optimization_goals = input_data.get("optimization_goals", ["performance", "readability"])
        
        if not code:
            return format_agent_response(
                success=False,
                error="No code provided for optimization"
            )

        prompt = f"""Optimize the following {language} code for {', '.join(optimization_goals)}:

        {code}

        Provide:
        1. Optimized code version
        2. Explanation of optimizations
        3. Expected improvements
        4. Any trade-offs made
        """

        optimization = await self._call_llm(self._create_messages(prompt))
        
        
        # Save the state
        self.save_state(
            state_id= input_data.get("task_id", "latest_optimize"),
            state= {
                "optimized_code": optimization,
                "goals": optimization_goals,
                "language": language
            }
        )

        return format_agent_response(
            success=True,
            data={
                "optimized_code": optimization,
                "goals": optimization_goals,
                "language": language
            }
        )

    async def test_code(self, code: str) -> Optional[str]:
        """
        Test code execution using Python REPL.
        
        Args:
            code (str): Code to test
            
        Returns:
            Optional[str]: Execution output or None if failed
        """
        try:
            result = self.repl_tool.run(code)
            
            return result
        except Exception as e:
            logger.error(f"Code execution failed: {str(e)}")
            return None
        
    async def load_state(self, state_id):
        return super().load_state(state_id)
        
async def main():
    from memory.redis_memory import RedisMemory

    code_agent = CodeAgent(memory_client= RedisMemory())

    

    state = await code_agent.load_state(state_id= "latest")

    print(state)
    

if __name__ == "__main__":
    import asyncio

    asyncio.run(main= main())

