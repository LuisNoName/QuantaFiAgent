You are an expert Python architect.  
Implement the module **`ai_system/slack_backend/app.py`** for my project based on the following design requirements.

---

## 🎯 Goal

Create the **Slack Backend** — a minimal, stateless gateway that:

1. Receives Slack Events via the Events API (using FastAPI).  
2. Verifies Slack requests (using Slack signing secret).  
3. Normalizes each incoming event into an `AgentRequest` (imported from `ai_system.agent_backend.models`).  
4. Forwards that request to the Agent Backend via HTTP POST (`/agent/invoke`).  
5. Receives an `AgentResponse` and posts it back to Slack using `chat.postMessage`.  
6. Does **not** contain any agent logic or state.

Keep it lightweight, testable, and idiomatic.

---

## 🧩 Constraints and Guidelines

- Use **FastAPI** for the server.
- Use the official **Slack SDK for Python** (`slack_sdk`).
- Load environment variables:  
  - `SLACK_BOT_TOKEN`  
  - `SLACK_SIGNING_SECRET`  
  - `AGENT_BACKEND_URL`
- Keep **no persistent state** — everything must be stateless between requests.
- Always **acknowledge Slack within 3 seconds**.
- Logging and error handling should be clear but minimal.
- Add the environment variables to the workspace yourself.

---

## 📦 Responsibilities

### 1️⃣ Event Handling
- Expose a `POST /slack/events` endpoint.
- Verify Slack signature and timestamp.
- Handle at least these Slack event types:
  - `app_mention`
  - `message` (for threads where the bot participates)
- For unsupported events → return 200 OK (no error).
- Normalize incoming Slack event into an `AgentRequest` according to this shape:

```python
AgentRequest(
    id=<uuid4>,
    timestamp=<datetime.utcnow()>,
    source={
        "platform": "slack",
        "workspace": event["team"],
        "channel": event["channel"],
        "thread_ts": event.get("thread_ts", event["ts"]),
        "user_id": event["user"],
        "username": slack_client.users_info(user=event["user"])["user"]["name"]
    },
    agent={"name": "dev", "type": "developer"},  # hardcoded for now
    message={
        "text": clean_text_without_bot_mention,
        "raw_text": event["text"],
        "attachments": []
    },
    context={"conversation_id": f"{event['channel']}:{event.get('thread_ts', event['ts'])}"}
)
```

### 2️⃣ Forwarding to Agent Backend
- POST JSON to `f"{AGENT_BACKEND_URL}/agent/invoke"`.
- Use standard `requests` library (synchronous is fine).
- Expect a valid `AgentResponse` JSON.

### 3️⃣ Posting Back to Slack
- Use Slack WebClient (`from slack_sdk import WebClient`).
- Call `chat_postMessage` with:
  - `channel=response.reply["channel"]`
  - `thread_ts=response.reply["thread_ts"]`
  - `text=response.reply["text"]`

---

## ⚙️ Implementation Details

- File: `ai_system/slack_backend/app.py`
- Expose a `FastAPI` app object named `app`.
- Include simple healthcheck endpoint (`GET /healthz`).
- Validate requests using Slack’s signature header (`X-Slack-Signature`, `X-Slack-Request-Timestamp`).
- Add logging for each event: type, user, channel, text.
- Clean the text by stripping bot mentions (regex on `<@UXXXX>`).
- Ignore events that are echoes of the bot’s own messages (`if event.get("subtype") == "bot_message"`).

---

## 🧱 Example Flow

1. Slack sends a POST to `/slack/events` when someone mentions the bot.
2. Server verifies request → normalizes → sends to Agent Backend.
3. Receives `AgentResponse`.
4. Posts the reply back to the same channel/thread via Slack API.
5. Returns `{"ok": True}` to Slack.

---

## 🧰 Deliverables

Implement in **one Python file**:
- FastAPI app setup
- Slack signature verification helper
- Event parsing + normalization
- HTTP forwarder to Agent Backend
- Slack message sender
- Simple logging

---

## ✅ Output Format

Provide **only the full Python source code** for `ai_system/slack_backend/app.py` — no explanations or comments outside the code.  
Use clear docstrings and inline comments instead.

---

This Slack backend must be **minimal, stateless, and ready to run behind ngrok**.
