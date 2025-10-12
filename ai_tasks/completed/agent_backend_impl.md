# 🧠 TASK: Implement Minimal AgentBackend and Dummy "Engineer" Agent

## 🎯 Objective
Create a working **Agent Backend** and a simple **Engineer Agent** to complete the first functional loop:
Slack → Slack Backend → Agent Backend → Agent → Agent Backend → Slack Backend → Slack.

The goal: verify message flow, token passing, and data contract correctness — not to implement real reasoning yet.

---

## 📂 Project Context

Repository structure (rename the dev_agent.py to engineer.py):

```
ai_system/
├── agent_backend/
│   ├── main.py                # TO IMPLEMENT
│   ├── models.py              # Contains Pydantic models (AgentRequest, AgentResponse, etc.)
│   ├── chat_history.py
│   └── registry.py
├── agents/
│   ├── base_agent.py
│   └── engineer.py           # "Engineer" agent will be implemented here
└── slack_backend/
    └── app.py                 # Already implemented
```

---

## 🧩 Part 1: Implement `ai_system/agent_backend/main.py`

### Requirements

1. Use **FastAPI** for the backend service.
2. Define a single endpoint:
   - `POST /agent/invoke`
   - Receives an `AgentRequest` object (Pydantic model from `models.py`)
   - Returns an `AgentResponse` object
3. Instantiate a single agent instance (Engineer).
   - Keep it simple — in-memory, no persistence.
4. The backend should:
   - Log incoming requests (channel, text, user)
   - Forward them to the `Engineer` agent’s `handle()` method
   - Return the agent’s `AgentResponse`
5. Add a healthcheck route:
   - `GET /healthz` → returns `{ "status": "ok" }`
6. Make it runnable via:
   ```bash
   uvicorn ai_system.agent_backend.main:app --port 8000
   ```

### Example Flow
**Request** (`POST /agent/invoke`):
```json
{
  "id": "req_001",
  "timestamp": "2025-10-11T22:45:00Z",
  "source": {
    "platform": "slack",
    "workspace": "acme-dev",
    "channel": "C12345",
    "thread_ts": "1733937292.123456",
    "user_id": "U789",
    "username": "Luis"
  },
  "agent": { "name": "engineer", "type": "developer" },
  "message": {
    "text": "please fix the utils module",
    "raw_text": "@Engineer please fix the utils module"
  },
  "context": { "conversation_id": "C12345:1733937292.123456" }
}
```

**Response**:
```json
{
  "id": "req_001",
  "agent": { "name": "engineer", "status": "completed" },
  "reply": {
    "text": "I received the message. This is my response.",
    "channel": "C12345",
    "thread_ts": "1733937292.123456"
  },
  "meta": {}
}
```

---

## 🧩 Part 2: Implement Dummy "Engineer" Agent

### File: `ai_system/agents/dev_agent.py`

1. Import `AgentRequest` and `AgentResponse` from `ai_system.agent_backend.models`.
2. Implement a simple class `Engineer` with a single method:

```python
class Engineer:
    def __init__(self, name: str = "engineer"):
        self.name = name

    def handle(self, request: AgentRequest) -> AgentResponse:
        """
        Receives an AgentRequest and returns a fixed AgentResponse.
        For initial testing, no reasoning or memory involved.
        """
```

3. The method should:
   - Extract `channel` and `thread_ts` from `request.source`.
   - Return an `AgentResponse` with:
     ```text
     "I received the message. This is my response."
     ```
   - Status: `"completed"`

4. This is only a placeholder — later it will be replaced by a full Agent class with memory, context, LLM, etc.

---

## ⚙️ Expected Behavior

- When Slack sends an event (via Slack Backend),
  the Agent Backend should log:
  ```
  [INFO] Received message from Luis in C12345: "please fix the utils module"
  ```
- The Engineer agent should respond with the static message.
- The Slack Backend should receive that response, post it to the same Slack thread, and the bot reply should appear correctly.

---

## ✅ Acceptance Criteria

- [ ] `POST /agent/invoke` returns valid `AgentResponse` JSON
- [ ] Logs show incoming message and outgoing response
- [ ] Slack receives and displays the response in the correct thread
- [ ] `GET /healthz` returns `{ "status": "ok" }`
- [ ] No external API calls fail (only internal logic)

---

## 🧪 Testing

Once implemented:
1. Run Agent Backend:
   ```bash
   uvicorn ai_system.agent_backend.main:app --port 8000
   ```
2. Run Slack Backend:
   ```bash
   uvicorn ai_system.slack_backend.app:app --port 3000
   ngrok http 3000
   ```
3. In Slack, mention your bot:
   ```
   @Engineer hello there
   ```
4. The bot should respond in the same thread with:
   > "I received the message. This is my response."

If you see that, everything is correctly wired up.

---

## 🧾 Deliverables

- `ai_system/agent_backend/main.py` (FastAPI app)
- `ai_system/agents/dev_agent.py` (Engineer class)
- Code must import existing Pydantic models and return proper JSON.
- No dependencies beyond FastAPI, pydantic, and standard library logging.

---

## 🚀 Next Steps (after this works)

- Replace `Engineer` with a real `Agent` using ChatHistory, ShortTermMemory, etc.
- Add context-based message handling and memory persistence.
- Add MCP tool support (e.g., recall past conversations).

---
