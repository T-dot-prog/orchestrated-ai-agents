"""
Base agent class for the AI Agent Orchestration System.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from langchain.callbacks import LangChainTracer
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from utils.config import settings
from utils.logger import setup_logging
from dotenv import load_dotenv, find_dotenv

logger = setup_logging()

load_dotenv(find_dotenv())

class BaseAgent(ABC):
    """Abstract base class for all agents in the system."""
    
    def __init__(
        self,
        name: str,
        system_prompt: str,
        memory_client: Any,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_retries: int = settings.MAX_RETRIES
    ):
        """
        Initialize base agent.
        
        Args:
            name (str): Agent name
            system_prompt (str): System prompt for the agent
            memory_client (Any): Memory client instance
            model_name (Optional[str]): Name of the LLM model to use
            temperature (float): Temperature for LLM sampling
            max_retries (int): Maximum number of retries on failure
        """
        self.name = name
        self.system_prompt = system_prompt
        self.memory = memory_client
        self.model_name = model_name or settings.MODEL_NAME
        self.temperature = temperature
        self.max_retries = max_retries
        
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model= self.model_name,
            temperature=self.temperature
        )
        
        # Initialize LangSmith tracer if API key is available
        if settings.LANGCHAIN_API_KEY:
            self.tracer = LangChainTracer(
                project_name=settings.LANGCHAIN_PROJECT
            )
        else:
            self.tracer = None
            
        logger.info(f"Initialized {name} agent with model {self.model_name}")

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent's main task.
        
        Args:
            input_data (Dict[str, Any]): Input data for the agent
            
        Returns:
            Dict[str, Any]: Agent's output
        """
        pass

    async def _call_llm(self, messages: list) -> str:
        """
        Call LLM with retry logic.
        
        Args:
            messages (list): List of messages for the LLM
            
        Returns:
            str: LLM response
            
        Raises:
            Exception: If all retries fail
        """
        for attempt in range(self.max_retries):
            try:
                response = await self.llm.agenerate([messages])
                return response.generations[0][0].text
            except Exception as e:
                logger.error(f"LLM call failed (attempt {attempt + 1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
        
        raise Exception("All LLM call attempts failed")

    def _create_messages(self, user_input: str) -> list:
        """
        Create message list for LLM.
        
        Args:
            user_input (str): User input to process
            
        Returns:
            list: List of messages for LLM
        """
        return [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_input)
        ]
    def save_state(self, state_id: str, state: Dict[str, Any]) -> bool:
        """
        Save agent state to memory.
        
        Args:
            state_id (str): Identifier for the state
            state (Dict[str, Any]): State to save
            
        Returns:
            bool: Success status
        """
        key = f"{self.name}:{state_id}"
        return self.memory.save_state(key, state)

    def load_state(self, state_id: str) -> Optional[Dict[str, Any]]:
        """
        Load agent state from memory.
        
        Args:
            state_id (str): Identifier for the state
            
        Returns:
            Optional[Dict[str, Any]]: Loaded state if found
        """
        key = f"{self.name}:{state_id}"
        return self.memory.load_state(key)