You are an expert Python developer.

Implement the Slack app for my bot named **“Engineer”**, which is part of a multi-agent system.

The app must:
- Receive events from Slack (via the Events API)
- Verify Slack signatures using the signing secret
- Normalize incoming messages into a clean JSON payload
- Forward those messages to my Agent Backend via HTTP POST
- Receive responses from the backend
- Post replies back to the correct Slack thread

---

## 🔧 Project Context

The code should live in:
`ai_system/slack_backend/app.py`

The Agent Backend runs separately and exposes:
`POST /agent/invoke`  
It expects an `AgentRequest` JSON and returns an `AgentResponse`.

The Slack App “Engineer” is already created in Slack and installed in the workspace.

Environment variables available in `.env`:
```bash
SLACK_BOT_TOKEN=xoxb-...
SLACK_SIGNING_SECRET=...
AGENT_BACKEND_URL=http://localhost:8000
```

---

## 🧱 Requirements

### Framework
- Use **FastAPI** for the HTTP server.
- Use **slack_sdk** for interacting with Slack’s Web API.
- Use **requests** to POST to the Agent Backend.

### Endpoints
- `POST /slack/events`:  
  - Verify the Slack signature using `X-Slack-Signature` and `X-Slack-Request-Timestamp`.
  - Handle the “url_verification” challenge (respond with the challenge text).
  - Parse “event_callback” events for:
    - `app_mention`
    - `message` (for threads where the bot is active)
  - Ignore subtype `bot_message` events (so it doesn’t reply to itself).
  - Normalize the Slack message into this payload format:
    ```json
    {
      "id": "<uuid4>",
      "timestamp": "<current UTC datetime>",
      "source": {
        "platform": "slack",
        "workspace": "<team_id>",
        "channel": "<channel_id>",
        "thread_ts": "<thread_ts>",
        "user_id": "<user_id>",
        "username": "<user_name>"
      },
      "agent": {
        "name": "engineer",
        "type": "developer"
      },
      "message": {
        "text": "<text_without_bot_mention>",
        "raw_text": "<original_text>"
      },
      "context": {
        "conversation_id": "<channel_id>:<thread_ts>"
      }
    }
    ```
  - Forward it to `POST {AGENT_BACKEND_URL}/agent/invoke`.
  - Expect a valid `AgentResponse` JSON like:
    ```json
    {
      "reply": {
        "text": "Hello world",
        "channel": "C12345",
        "thread_ts": "1733937292.123456"
      }
    }
    ```
  - Post that reply text to Slack with `chat_postMessage`.

- `GET /healthz`: return `{ "status": "ok" }`.

---

## 🧩 Functional Notes

- Initialize Slack WebClient with `SLACK_BOT_TOKEN`.
- Use `dotenv` to load environment variables.
- Log each received event type, channel, and user.
- Strip the bot mention from messages (regex: `<@U[A-Z0-9]+>`).
- Acknowledge Slack’s event requests within 3 seconds (return 200 fast).
- Send the Agent Backend call asynchronously if possible (but keep it simple — sync is fine for now).

---

## 🧱 Deliverables

Provide a single Python module:
`ai_system/slack_backend/app.py`
that defines a `FastAPI` app named `app`.

It must be ready to run with:
```bash
uvicorn ai_system.slack_backend.app:app --port 3000
```

---

## 🧪 Example Flow

1. User types in Slack:
   > `@Engineer summarize the last 5 commits`
2. Slack sends an `app_mention` event to `/slack/events`.
3. The app verifies, normalizes, and forwards it to the backend.
4. The Agent Backend responds with:
   ```json
   { "reply": { "text": "Summary complete.", "channel": "C123", "thread_ts": "1733..." } }
   ```
5. The app posts the reply in the same thread.
6. Responds `200 OK` to Slack.

---

Provide only the Python code, with clean docstrings and clear separation of logic.
