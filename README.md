# QuantaFiAgent

AI Agent System with Slack Integration

## Project Structure

```
QuantaFiAgent/
├── ai_system/
│   ├── slack_backend/       # Slack Events API handler
│   │   └── app.py
│   ├── agent_backend/       # Agent orchestration layer
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── registry.py
│   │   └── chat_history.py
│   ├── agents/              # Agent implementations
│   │   ├── base_agent.py
│   │   ├── components/
│   │   │   ├── chat_history.py
│   │   │   ├── short_term_memory.py
│   │   │   ├── long_term_memory.py
│   │   │   ├── llm.py
│   │   │   └── mcp.py
│   │   └── engineer.py      # Engineer agent (dummy implementation)
│   └── requirements.txt
├── venv/                    # Python virtual environment
├── run_agent_backend.sh     # Start Agent Backend on port 8000
├── run_slack_backend.sh     # Start Slack Backend on port 3000
└── TESTING.md              # Comprehensive testing guide
```

## Quick Start

### 1. Setup Virtual Environment

```bash
# Already created - activate it
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r ai_system/requirements.txt
```

### 3. Configure Environment

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

See `ENV_SETUP.md` for detailed instructions on obtaining Slack credentials.

### 4. Run Agent Backend

In terminal 1:
```bash
./run_agent_backend.sh
```

### 5. Run Slack Backend

In terminal 2:
```bash
./run_slack_backend.sh
```

### 6. Expose to Internet (for Slack Events)

In terminal 3:
```bash
ngrok http 3000
```

Configure your Slack app's Event Subscriptions URL to: `https://your-ngrok-url.ngrok.io/slack/events`

### 7. Test in Slack

Mention your bot in any channel:
```
@Engineer hello!
```

See `TESTING.md` for comprehensive testing instructions.

## Components

### Slack Backend
- **Purpose**: Stateless gateway for Slack Events API
- **Port**: 3000
- **Endpoints**:
  - `GET /healthz` - Health check
  - `POST /slack/events` - Slack events handler

### Agent Backend
- **Purpose**: Hosts and manages agent instances
- **Port**: 8000 (default)
- **Endpoints**:
  - `POST /agent/invoke` - Process agent requests

## Development

### Running Tests

```bash
pytest
```

### Code Style

```bash
black ai_system/
flake8 ai_system/
```

## Architecture

1. **Slack** sends events → **Slack Backend** (`POST /slack/events`)
2. **Slack Backend** normalizes to `AgentRequest` → **Agent Backend** (`POST /agent/invoke`)
3. **Agent Backend** routes to appropriate **Agent**
4. **Agent** processes using components (LLM, Memory, MCP tools)
5. **Agent** returns `AgentResponse` → **Slack Backend**
6. **Slack Backend** posts reply back to **Slack**

## Documentation

- `ENV_SETUP.md` - Detailed environment setup guide
- `ai_tasks/todo/` - Task specifications and requirements

## License

Proprietary

