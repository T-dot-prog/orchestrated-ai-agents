"""
Redis-backed memory system for the AI Agent Orchestration System.
"""
import json
from typing import Any, Dict, Optional

import redis
from utils.config import settings
from utils.logger import setup_logging

logger = setup_logging()

class RedisMemory:
    """Redis-backed memory system for storing agent state and context."""
    
    def __init__(
        self,
        host: str = settings.REDIS_HOST,
        port: int = settings.REDIS_PORT,
        db: int = settings.REDIS_DB,
        password: Optional[str] = settings.REDIS_PASSWORD
    ):
        """
        Initialize Redis memory connection.
        
        Args:
            host (str): Redis host address
            port (int): Redis port number
            db (int): Redis database number
            password (Optional[str]): Redis password if required
        """
        try:
            self.redis = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=True
            )
            logger.info(f"Connected to Redis at {host}:{port}")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise

    def save_state(self, key: str, state: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        Save state to Redis.
        
        Args:
            key (str): Key to store the state under
            state (Dict[str, Any]): State data to store
            ttl (Optional[int]): Time-to-live in seconds
            
        Returns:
            bool: Success status
        """
        try:
            serialized_state = json.dumps(state)
            self.redis.set(key, serialized_state)
            
            if ttl:
                self.redis.expire(key, ttl)
                
            logger.debug(f"Saved state for key: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to save state for key {key}: {str(e)}")
            return False

    def load_state(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Load state from Redis.
        
        Args:
            key (str): Key to retrieve state for
            
        Returns:
            Optional[Dict[str, Any]]: Retrieved state or None if not found
        """
        try:
            state = self.redis.get(key)
            if state:
                return json.loads(state)
            logger.debug(f"No state found for key: {key}")
            return None
        except Exception as e:
            logger.error(f"Failed to load state for key {key}: {str(e)}")
            return None

    def clear_state(self, key: str) -> bool:
        """
        Clear state from Redis.
        
        Args:
            key (str): Key to clear state for
            
        Returns:
            bool: Success status
        """
        try:
            deleted = self.redis.delete(key)
            if deleted:
                logger.debug(f"Cleared state for key: {key}")
                return True
            logger.debug(f"No state found to clear for key: {key}")
            return False
        except Exception as e:
            logger.error(f"Failed to clear state for key {key}: {str(e)}")
            return False

    def list_keys(self, pattern: str = "*") -> list:
        """
        List all keys matching pattern.
        
        Args:
            pattern (str): Pattern to match keys against
            
        Returns:
            list: List of matching keys
        """
        try:
            return self.redis.keys(pattern)
        except Exception as e:
            logger.error(f"Failed to list keys with pattern {pattern}: {str(e)}")
            return []

    def save_workflow_state(self, workflow_id: str, state: Dict[str, Any]) -> bool:
        """
        Save workflow state with prefix.
        
        Args:
            workflow_id (str): Workflow identifier
            state (Dict[str, Any]): Workflow state to save
            
        Returns:
            bool: Success status
        """
        key = f"workflow:{workflow_id}"
        return self.save_state(key, state)

    def get_workflow_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get workflow state by ID.
        
        Args:
            workflow_id (str): Workflow identifier
            
        Returns:
            Optional[Dict[str, Any]]: Workflow state if found
        """
        key = f"workflow:{workflow_id}"
        return self.load_state(key)

    def close(self):
        """Close Redis connection."""
        try:
            self.redis.close()
            logger.info("Closed Redis connection")
        except Exception as e:
            logger.error(f"Error closing Redis connection: {str(e)}")