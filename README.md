# 🤖 AI Agent Orchestration System

A modular, production-grade AI Agent Orchestration System built with LangChain, LangGraph, FastAPI, and Redis.

## 🌟 Features

- Multiple specialized AI agents (Research, Summarizer, Code, Evaluator, Planner)
- Dynamic workflow orchestration using LangGraph
- Redis-backed persistent memory
- RESTful API endpoints with FastAPI
- Docker containerization
- Comprehensive testing suite
- Extensible architecture

## 🛠️ Technology Stack

- Python 3.10+
- LangChain & LangGraph for agent orchestration
- FastAPI for REST API
- Redis for memory persistence
- Docker & Docker Compose for containerization
- OpenAI GPT-4 (configurable)

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose installed
- OpenAI API key
- Python 3.10+ (for local development)

### Configuration

1. Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_api_key_here
MODEL_NAME=gpt-4
DEBUG=false
REDIS_HOST=redis
REDIS_PORT=6379
```

### Running with Docker

1. Build and start the services:
```bash
docker-compose up --build
```

2. The API will be available at `http://localhost:8000`

### Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\\Scripts\\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
uvicorn app.api:app --reload
```

## 📝 API Endpoints

### Start a Workflow
```bash
curl -X POST http://localhost:8000/api/v1/run_agent/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "task": "Research and summarize AI orchestration patterns",
    "constraints": {
      "max_sources": 5,
      "summary_length": "medium"
    }
  }'
```

### Get Memory State
```bash
curl http://localhost:8000/api/v1/memory/workflow_id
```

### Submit Feedback
```bash
curl -X POST http://localhost:8000/api/v1/feedback/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "workflow_id": "your_workflow_id",
    "feedback": {
      "quality": "good",
      "suggestions": "faster execution"
    },
    "rating": 4
  }'
```

### System Status
```bash
curl http://localhost:8000/api/v1/status/
```

## 🧪 Running Tests

```bash
pytest tests/
```

## 📚 Project Structure

```
ai_orchestrator/
├── agents/
│   ├── research_agent.py
│   ├── summarize_agent.py
│   ├── code_agent.py
│   ├── evaluator_agent.py
│   └── planner_agent.py
├── orchestrator/
│   └── supervisor.py
├── memory/
│   └── redis_memory.py
├── app/
│   └── api.py
├── utils/
│   ├── logger.py
│   ├── config.py
│   └── helpers.py
├── tests/
│   └── test_agents.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🔧 Extending the System

### Adding a New Agent

1. Create a new agent class inheriting from `BaseAgent`:

```python
from agents.base_agent import BaseAgent

class NewAgent(BaseAgent):
    def __init__(self, memory_client: Any, **kwargs):
        super().__init__(
            name="new_agent",
            system_prompt="Your system prompt here",
            memory_client=memory_client,
            **kwargs
        )

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Implement agent logic here
        pass
```

2. Register the agent in `app/api.py`:

```python
agents = {
    # ... existing agents ...
    "new_agent": NewAgent(memory_client=memory_client)
}
```

## 📄 License

MIT License

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to your branch
5. Create a Pull Request