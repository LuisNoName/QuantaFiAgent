# 🧠 TASK: Implement ChatHistory and LLM Integration for Engineer Agent

## 🎯 Objective
Upgrade the **Engineer Agent** to maintain per-thread chat history and use an actual LLM (OpenAI ChatGPT-5-Nano or GPT-4o-Mini) for message generation.

This will make the Engineer capable of coherent, context-aware replies using stored conversation history.

---

## 📂 Project Context

Existing repository structure:

```
ai_system/
├── agent_backend/
│   ├── main.py
│   ├── models.py
│   ├── chat_history.py        # TO IMPLEMENT (persistent message store)
│   └── registry.py
├── agents/
│   ├── components/
│   │   ├── llm.py             # TO IMPLEMENT (OpenAI client wrapper)
│   │   ├── chat_history.py    # optional future use
│   └── engineer.py           # Engineer agent (TO UPDATE)
└── slack_backend/
    └── app.py
```

---

## 🧩 Part 1: Implement `ChatHistory`

### File: `ai_system/agent_backend/chat_history.py`

#### Purpose
Maintain persistent conversation records **per Slack thread**.

Each conversation (thread) should be stored in a separate JSONL file named after the `conversation_id` (`channel:thread_ts`).

#### Interface

```python
class ChatHistory:
    def __init__(self, base_path="chat_history"):
        os.makedirs(base_path, exist_ok=True)
        self.base_path = base_path

    def _path(self, conversation_id: str) -> str:
        return os.path.join(self.base_path, f"{conversation_id}.jsonl")

    def append(self, conversation_id: str, role: str, content: str):
        with open(self._path(conversation_id), "a") as f:
            f.write(json.dumps({"role": role, "content": content}) + "\n")

    def load(self, conversation_id: str) -> List[dict]:
        path = self._path(conversation_id)
        if not os.path.exists(path):
            return []
        with open(path, "r") as f:
            return [json.loads(line) for line in f]
```

#### Behavior
- `append()` — Add new messages from either the user (`role="user"`) or the agent (`role="agent"`).
- `load()` — Retrieve the full message history for that thread in chronological order.

---

## 🧩 Part 2: Implement `LLM` Component

### File: `ai_system/agents/components/llm.py`

#### Purpose
Provide a lightweight interface to the OpenAI API (ChatGPT models).

#### Interface

```python
from openai import OpenAI
import os

class LLM:
    def __init__(self, model_name="gpt-4o-mini"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model_name = model_name

    def chat(self, messages: List[dict]) -> str:
        resp = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages
        )
        return resp.choices[0].message.content.strip()
```

#### Notes
- Default model: `"gpt-4o-mini"` (or `"gpt-5-nano"` if available).
- `messages` must follow the OpenAI Chat API format:
  ```python
  [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
  ```

---

## 🧩 Part 3: Update `Engineer` Agent

### File: `ai_system/agents/engineer.py`

#### Purpose
Integrate both `ChatHistory` and `LLM` to create a conversationally aware agent.

#### Implementation Outline

```python
import logging
from ai_system.agent_backend.models import AgentRequest, AgentResponse
from ai_system.agent_backend.chat_history import ChatHistory
from ai_system.agents.components.llm import LLM

logger = logging.getLogger(__name__)

class Engineer:
    def __init__(self, name: str = "engineer"):
        self.name = name
        self.chat_history = ChatHistory()
        self.llm = LLM(model_name="gpt-4o-mini")

    def handle(self, request: AgentRequest) -> AgentResponse:
        conversation_id = request.context["conversation_id"]
        user_text = request.message["text"]

        # 1. Append user message
        self.chat_history.append(conversation_id, "user", user_text)

        # 2. Load chat history
        messages = self.chat_history.load(conversation_id)

        # 3. Query LLM
        reply = self.llm.chat(messages)

        # 4. Append LLM reply
        self.chat_history.append(conversation_id, "assistant", reply)

        # 5. Return AgentResponse
        return AgentResponse(
            id=request.id,
            agent={"name": self.name, "status": "completed"},
            reply={
                "text": reply,
                "channel": request.source["channel"],
                "thread_ts": request.source["thread_ts"],
            },
            meta={},
        )
```

---

## ⚙️ Environment Setup

### 1. Add OpenAI credentials to `.env`:
```bash
OPENAI_API_KEY=sk-...
```

### 2. Install dependency:
```bash
pip install openai
```

### 3. Create the chat history folder:
```bash
mkdir chat_history
```

---

## 🧪 Testing

1. Run both backends:
   ```bash
   uvicorn ai_system.agent_backend.main:app --port 8000
   uvicorn ai_system.slack_backend.app:app --port 3000
   ngrok http 3000
   ```
2. Update your Slack app’s “Event Subscription URL” if needed.
3. Mention your bot in Slack:
   ```
   @Engineer Hello, how are you?
   ```
4. The Engineer should now:
   - Save the message in `chat_history/`
   - Call OpenAI’s model
   - Post a coherent response in Slack
   - Continue the conversation within the same thread

---

## ✅ Acceptance Criteria

- [ ] Each thread has its own JSONL file under `chat_history/`
- [ ] Messages persist between requests
- [ ] The LLM receives the entire conversation as context
- [ ] Responses appear in the correct Slack thread
- [ ] No serialization or auth errors occur

---

## 🚀 Next Steps (Future Enhancements)

- Add conversation summarization for long threads (ShortTermMemory).
- Replace ChatHistory JSONL with SQLite or vector DB.
- Add persistent agent state for multiple conversations.
- Implement MCP tools for code editing and recall.
