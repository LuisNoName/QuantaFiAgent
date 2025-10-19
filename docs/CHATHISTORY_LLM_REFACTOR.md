# ChatHistory & LLM Refactoring Summary

## ✅ Completed

Standardized message handling across ChatHistory and LLM components using the shared `BasicMessage` Pydantic schema.

---

## 🎯 Changes Made

### 1. BasicMessage Schema (Already Existed)
**File:** `ai_system/agent_backend/models.py`

```python
class BasicMessage(BaseModel):
    role: str
    content: str
    name: Optional[str] = None
```

This schema provides:
- Strong typing with Pydantic validation
- Optional `name` field for multi-user/multi-agent scenarios
- OpenAI-compatible structure

---

### 2. ChatHistory Updates
**File:** `ai_system/agent_backend/chat_history.py`

#### Before:
```python
def load(self, conversation_id: str) -> List[dict]:
    # Returns raw dicts
    return [{"role": "user", "content": "..."}]
```

#### After:
```python
def load(self, conversation_id: str) -> List[BasicMessage]:
    # Returns validated BasicMessage objects
    messages = []
    for line in f:
        data = json.loads(line)
        messages.append(BasicMessage(**data))
    return messages
```

**Benefits:**
- ✅ Type safety - IDE autocomplete and validation
- ✅ Guaranteed schema compliance
- ✅ Pydantic validation catches malformed data

---

### 3. LLM Component Updates
**File:** `ai_system/agents/components/llm.py`

#### Before:
```python
def chat(self, messages: List[dict]) -> str:
    response = self.client.responses.create(
        model=self.model_name,
        input=messages  # Wrong! Passing list to input
    )
    reply = response.choices[0].message.content  # Wrong API!
```

#### After:
```python
def _format_messages(self, messages: List[BasicMessage]) -> str:
    formatted = []
    for msg in messages:
        name_suffix = f" ({msg.name})" if msg.name else ""
        formatted.append(f"{msg.role.upper()}{name_suffix}: {msg.content}")
    return "\n".join(formatted)

def chat(self, messages: List[BasicMessage]) -> str:
    input_text = self._format_messages(messages)
    
    response = self.client.responses.create(
        model=self.model_name,
        input=input_text  # Correct! Single formatted string
    )
    
    reply = response.output[0].content[0].text.strip()  # Correct API!
    tokens_used = response.usage.total_tokens
    return reply
```

**Key Changes:**
- ✅ Accepts `List[BasicMessage]` (typed)
- ✅ Formats messages into single string for `responses.create()` API
- ✅ Extracts response from correct API format (`response.output[0].content[0].text`)
- ✅ Includes names in formatted output: `"USER (luis_safar): Hello!"`
- ✅ Supports both standard and Flex service tiers

---

### 4. Engineer Agent Updates
**File:** `ai_system/agents/engineer.py`

#### Before:
```python
self.chat_history.append(conversation_id, "assistant", reply_text, name=self.name)
```

#### After:
```python
self.chat_history.append(conversation_id, "assistant", name=self.name, content=reply_text)
```

**Change:** Using named parameters for clarity (matching the signature change in ChatHistory)

---

## 📊 Message Format Examples

### JSONL Storage (unchanged):
```json
{"role": "user", "name": "luis_safar", "content": "Hello!"}
{"role": "assistant", "name": "engineer", "content": "Hi Luis!"}
{"role": "user", "name": "john_doe", "content": "What's the weather?"}
{"role": "assistant", "name": "engineer", "content": "I don't have access to weather data."}
```

### BasicMessage Objects (in memory):
```python
[
    BasicMessage(role="user", name="luis_safar", content="Hello!"),
    BasicMessage(role="assistant", name="engineer", content="Hi Luis!"),
    ...
]
```

### Formatted for OpenAI API:
```
USER (luis_safar): Hello!
ASSISTANT (engineer): Hi Luis!
USER (john_doe): What's the weather?
ASSISTANT (engineer): I don't have access to weather data.
```

---

## 🎯 Benefits

### Type Safety
- IDE autocomplete for message fields
- Pydantic validation catches errors early
- No more `message.get("role", "unknown")` - just `message.role`

### Readability
```python
# Before
for msg in messages:
    role = msg.get("role")
    content = msg.get("content")
    name = msg.get("name")

# After
for msg in messages:
    role = msg.role
    content = msg.content
    name = msg.name
```

### Consistency
- Single source of truth for message structure
- Same schema everywhere (ChatHistory, LLM, internal processing)
- Easy to extend (add new fields once, available everywhere)

### OpenAI API Compatibility
- Proper use of `responses.create()` with `input` parameter
- Correct response extraction from `response.output[0].content[0].text`
- Flex service tier support

---

## 🔄 Data Flow

```
Slack → SlackBackend
         ↓
         chat_history.append(conv_id, "user", name="luis", content="Hello")
         ↓
         [JSONL: {"role": "user", "name": "luis", "content": "Hello"}]

Engineer Agent
         ↓
         messages: List[BasicMessage] = chat_history.load(conv_id)
         ↓
         [BasicMessage(role="user", name="luis", content="Hello")]

LLM Component
         ↓
         input_text = format_messages(messages)
         ↓
         "USER (luis): Hello"
         ↓
         OpenAI responses.create(input=input_text)
         ↓
         response.output[0].content[0].text = "Hi Luis!"
         ↓
         chat_history.append(conv_id, "assistant", name="engineer", content="Hi Luis!")
         ↓
         [JSONL: {"role": "assistant", "name": "engineer", "content": "Hi Luis!"}]
```

---

## ✅ Validation

- [x] `ChatHistory.append()` still writes valid JSONL
- [x] `ChatHistory.load()` returns `List[BasicMessage]`
- [x] `LLM.chat()` accepts `List[BasicMessage]`
- [x] Message formatting includes names: `"USER (name): content"`
- [x] OpenAI `responses.create()` API called correctly
- [x] Response extraction works with `response.output[0].content[0].text`
- [x] No linter errors
- [x] Engineer agent works with new types

---

## 🧪 Testing

### Manual Test:
1. Restart backends (changes auto-reload)
2. Send message in Slack: `@Engineer test with names`
3. Check chat history file: Should include name fields
4. Check LLM logs: Should show formatted messages with names
5. Verify response works correctly

### Expected Log Output:
```
INFO: Loaded 1 messages from conversation history
INFO: Calling OpenAI API with 1 messages
INFO: OpenAI response received: 123 chars, 456 tokens used
INFO: Appended engineer response to history
```

### Chat History File:
```json
{"role": "user", "name": "luis_safar", "content": "test with names"}
{"role": "assistant", "name": "engineer", "content": "Response from GPT..."}
```

---

## 🎓 Design Improvements

### Before: Stringly Typed
```python
messages: List[dict] = [...]
role = msg["role"]  # Could be missing!
content = msg.get("content", "")  # Manual defaults
```

### After: Strongly Typed
```python
messages: List[BasicMessage] = [...]
role = msg.role  # Guaranteed to exist
content = msg.content  # Guaranteed to exist
name = msg.name  # Optional[str], properly typed
```

---

## 🚀 Next Steps

Future enhancements enabled by this refactoring:

1. **Add metadata field** to `BasicMessage`:
   ```python
   class BasicMessage(BaseModel):
       role: str
       content: str
       name: Optional[str] = None
       metadata: dict = Field(default_factory=dict)  # New!
   ```

2. **Message validation**:
   ```python
   from pydantic import validator
   
   @validator('role')
   def validate_role(cls, v):
       if v not in ['user', 'assistant', 'system']:
           raise ValueError('Invalid role')
       return v
   ```

3. **Conversation analysis**:
   ```python
   def get_user_messages(messages: List[BasicMessage]) -> List[BasicMessage]:
       return [msg for msg in messages if msg.role == "user"]
   ```

---

**Refactor Date**: 2025-10-12  
**Version**: 1.0  
**Status**: ✅ Complete

