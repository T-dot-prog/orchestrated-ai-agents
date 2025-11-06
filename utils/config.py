"""
Configuration management for the AI Agent Orchestration System.
"""
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "AI Agent Orchestration System"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Gemini Configuration
    GOOGLE_API_KEY: str
    MODEL_NAME: str = "gemini-2.0-flash"
    MAX_TOKENS: int = 2000
    TEMPERATURE: float = 0.7
    
    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_TTL: int = 3600  # 1 hour default TTL
    
    # LangSmith Configuration (Optional)
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: str = "ai-orchestrator"
    LANGCHAIN_TRACING_V2: bool = True
    
    # Agent Configuration
    MAX_RETRIES: int = 3
    TIMEOUT: int = 300  # 5 minutes
    CONCURRENT_TASKS: int = 5
    
    # Memory Configuration
    MEMORY_BACKEND: str = "redis"
    MEMORY_TTL: int = 86400  # 24 hours
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: str = "logs/ai_orchestrator.log"
    
    # Security Configuration
    API_KEY_HEADER: str = "X-API-Key"
    API_KEY: Optional[str] = None
    CORS_ORIGINS: list = ["*"]
    
    # Task Queue Configuration
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # Agent-specific Configuration
    RESEARCH_AGENT_CONFIG: dict = {
        "max_sources": 5,
        "search_timeout": 60,
        "relevance_threshold": 0.7
    }
    
    SUMMARIZER_AGENT_CONFIG: dict = {
        "max_length": 1000,
        "min_length": 100,
        "style": "concise"
    }
    
    CODE_AGENT_CONFIG: dict = {
        "supported_languages": ["python", "javascript", "typescript"],
        "max_code_length": 5000,
        "include_tests": True
    }
    
    EVALUATOR_AGENT_CONFIG: dict = {
        "min_score": 1,
        "max_score": 10,
        "evaluation_criteria": [
            "accuracy",
            "completeness",
            "efficiency",
            "readability"
        ]
    }
    
    PLANNER_AGENT_CONFIG: dict = {
        "max_steps": 10,
        "planning_timeout": 120,
        "include_fallbacks": True
    }
    
    # Model Configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
    )
    
    def get_agent_config(self, agent_name: str) -> dict:
        """
        Get configuration for a specific agent.
        
        Args:
            agent_name (str): Name of the agent
            
        Returns:
            dict: Agent configuration
        """
        config_map = {
            "research_agent": self.RESEARCH_AGENT_CONFIG,
            "summarizer_agent": self.SUMMARIZER_AGENT_CONFIG,
            "code_agent": self.CODE_AGENT_CONFIG,
            "evaluator_agent": self.EVALUATOR_AGENT_CONFIG,
            "planner_agent": self.PLANNER_AGENT_CONFIG
        }
        return config_map.get(agent_name, {})
    
    def get_redis_url(self) -> str:
        """
        Get Redis URL from configuration.
        
        Returns:
            str: Redis URL
        """
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    def get_logging_config(self) -> dict:
        """
        Get logging configuration.
        
        Returns:
            dict: Logging configuration
        """
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": self.LOG_FORMAT
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "stream": "ext://sys.stdout"
                },
                "file": {
                    "class": "logging.FileHandler",
                    "formatter": "default",
                    "filename": self.LOG_FILE
                }
            },
            "root": {
                "level": self.LOG_LEVEL,
                "handlers": ["console", "file"]
            }
        }


# creating settings instance 
settings = Settings()
