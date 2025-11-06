"""
AI Agent Orchestration System
Main entry point for the application.
"""
import asyncio
import logging
import os

import uvicorn
from dotenv import load_dotenv, find_dotenv

from app.api import app
from utils.logger import setup_logging

# Load environment variables
load_dotenv(find_dotenv())

# Setup logging
logger = setup_logging()

def main():
    """Main function to start the FastAPI application."""
    try:
        logger.info("Starting AI Agent Orchestration System...")
        # Start the FastAPI application
        uvicorn.run(
            app,
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", 8000)),
            reload= True
        )
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise

if __name__ == "__main__":
    main()