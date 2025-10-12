# 🧠 Task: Refactor LLM and ChatHistory Components for Message Schema Integration

## Overview
We’re standardizing our message format across the LLM and ChatHistory components to use a shared Pydantic schema (`BasicMessage`) instead of plain dictionaries.

The goal is to:
- Unify message handling (`List[dict]` → `List[BasicMessage]`).
- Ensure compatibility with OpenAI’s `responses.create()` API (which expects a valid `input` format, not `messages`).
- Improve type safety and readability across the codebase.

---

## 1. Find the BasicMessage schema
The basic BasicMessage schema is located in ai_syste/agent_backend/models.py

```python
from pydantic import BaseModel
from typing import Optional

class BasicMessage(BaseModel):
    role: str
    content: str
    name: Optional[str] = None
```

---

## 2. Update `ChatHistory` class
**File:** `ai_system/agents/components/chat_history.py`

### Changes:
- Change method signatures and internal storage to use `List[BasicMessage]` instead of `List[dict]`.
- When appending messages, continue storing them in JSONL, but when loading, **deserialize into `BasicMessage` objects**.

### Updated methods:

```python
from schemas.messages import BasicMessage

def append(self, conversation_id: str, role: str, content: str, name: str = None) -> None:
    # (no major change except optional sanitization of `name`)
    ...

def load(self, conversation_id: str) -> List[BasicMessage]:
    path = self._path(conversation_id)
    if not os.path.exists(path):
        return []
    messages = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                messages.append(BasicMessage(**data))
    return messages
```

---

## 3. Update `LLM` class
**File:** `ai_system/agents/components/llm.py`

### Changes:
- Update the `chat()` method signature to accept `List[BasicMessage]`.
- Convert `BasicMessage` list into a single formatted string for the `responses.create()` API.
- Keep Flex handling intact.

### Implementation example:

```python
def _format_messages(messages: List[BasicMessage]) -> str:
    formatted = []
    for msg in messages:
        name = f" ({msg.name})" if msg.name else ""
        formatted.append(f"{msg.role.upper()}{name}: {msg.content}")
    return "\n".join(formatted)

def chat(self, messages: List[BasicMessage]) -> str:
    input_text = self._format_messages(messages)

    if not self.use_flex:
        response = self.client.responses.create(
            model=self.model_name,
            input=input_text
        )
    else:
        response = self.client.with_options(timeout=900.0).responses.create(
            model=self.model_name,
            input=input_text,
            service_tier="flex",
        )

    reply = response.output[0].content[0].text.strip()
    tokens_used = response.usage.total_tokens

    logger.info(
        f"OpenAI response received: {len(reply)} chars, {tokens_used} tokens used"
    )

    return reply
```

---

## 4. Validation
- Verify both `ChatHistory.append()` and `ChatHistory.load()` maintain data consistency (JSONL format unchanged).
- Ensure `LLM.chat()` correctly formats messages and produces valid API responses.
- Run a few integration tests with sample chat histories to confirm round-trip serialization.

---

## Expected Outcome
After completion:
- Both `LLM` and `ChatHistory` will operate with `BasicMessage` objects end-to-end.
- The OpenAI API calls will be fully compatible with the new `responses.create()` schema.
- Codebase gains stronger typing and better clarity for agent–LLM communication.
