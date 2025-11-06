#!/usr/bin/env python3
from setuptools import find_packages, setup

# Read the contents of README.md file
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

# Core requirements
CORE_REQUIREMENTS = [
    "langchain>=0.0.325",
    "langgraph>=0.0.10",
    "fastapi>=0.104.0",
    "uvicorn>=0.23.2",
    "redis>=5.0.1",
    "python-dotenv>=1.0.0",
    "openai>=1.2.3",
    "requests>=2.31.0",
    "python-multipart>=0.0.6",
    "langsmith>=0.0.52",
    "streamlit>=1.28.0",
    "celery>=5.3.4",
    "aiohttp>=3.8.6",
    "pydantic>=2.4.2",
    "pydantic-settings>=2.0.3",
]

# Development requirements
DEV_REQUIREMENTS = [
    "pytest>=7.4.3",
    "pytest-asyncio>=0.21.1",
    "black>=23.10.1",
    "isort>=5.12.0",
    "flake8>=6.1.0",
    "mypy>=1.6.1",
]

# Testing requirements
TEST_REQUIREMENTS = [
    "pytest>=7.4.3",
    "pytest-asyncio>=0.21.1",
    "pytest-cov>=4.1.0",
]

# Documentation requirements
DOCS_REQUIREMENTS = [
    "sphinx>=7.2.6",
    "sphinx-rtd-theme>=1.3.0",
]

setup(
    name="ai_orchestrator",
    version="0.1.0",
    description="A modular AI Agent Orchestration System using LangChain, LangGraph, FastAPI, and Redis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AI Orchestrator Team",
    author_email="team@ai-orchestrator.com",
    url="https://github.com/username/ai-orchestrator",
    packages=find_packages(exclude=["tests*"]),
    python_requires=">=3.10",
    install_requires=CORE_REQUIREMENTS,
    extras_require={
        "dev": DEV_REQUIREMENTS,
        "test": TEST_REQUIREMENTS,
        "docs": DOCS_REQUIREMENTS,
        "all": DEV_REQUIREMENTS + TEST_REQUIREMENTS + DOCS_REQUIREMENTS,
    },
    entry_points={
        "console_scripts": [
            "ai-orchestrator=ai_orchestrator.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords=["ai", "agents", "langchain", "langgraph", "fastapi", "redis"],
    project_urls={
        "Homepage": "https://github.com/username/ai-orchestrator",
        "Documentation": "https://ai-orchestrator.readthedocs.io/",
        "Source": "https://github.com/username/ai-orchestrator",
        "Tracker": "https://github.com/username/ai-orchestrator/issues",
    },
    include_package_data=True,
    zip_safe=False,
    license="MIT",
    package_dir= {'': '.'}
)