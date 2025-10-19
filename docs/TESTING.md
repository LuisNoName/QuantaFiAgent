# Testing Guide - Complete Slack → Agent Flow

This guide will help you test the complete message flow:
**Slack → Slack Backend → Agent Backend → Engineer Agent → Agent Backend → Slack Backend → Slack**

## Prerequisites

1. **Python virtual environment** activated:
   ```bash
   source venv/bin/activate
   ```

2. **Dependencies installed**:
   ```bash
   pip install -r ai_system/requirements.txt
   ```

3. **Environment variables configured** in `.env`:
   ```bash
   SLACK_BOT_TOKEN=xoxb-your-actual-token
   SLACK_SIGNING_SECRET=your-actual-secret
   AGENT_BACKEND_URL=http://localhost:8000
   ```

4. **Slack app configured** with Event Subscriptions (see `ENV_SETUP.md`)

---

## Step 1: Start the Agent Backend

Open a terminal and run:

```bash
./run_agent_backend.sh
```

You should see:
```
Starting Agent Backend on http://localhost:8000
Health check: http://localhost:8000/healthz
Agent invoke endpoint: http://localhost:8000/agent/invoke

INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Test it:**
```bash
curl http://localhost:8000/healthz
```

Expected response:
```json
{"status":"ok","service":"agent-backend"}
```

---

## Step 2: Start the Slack Backend

Open a **new terminal** and run:

```bash
./run_slack_backend.sh
```

You should see:
```
Starting Slack Backend on http://localhost:3000
Health check: http://localhost:3000/healthz
Slack events endpoint: http://localhost:3000/slack/events

INFO:     Uvicorn running on http://0.0.0.0:3000
```

**Test it:**
```bash
curl http://localhost:3000/healthz
```

Expected response:
```json
{"status":"ok","service":"slack-backend"}
```

---

## Step 3: Expose Slack Backend with ngrok

Open a **new terminal** and run:

```bash
ngrok http 3000
```

You'll see output like:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:3000
```

Copy the `https://` URL (e.g., `https://abc123.ngrok.io`)

---

## Step 4: Configure Slack Event Subscriptions

1. Go to https://api.slack.com/apps
2. Select your app
3. Navigate to **Event Subscriptions**
4. Enable Events
5. Set **Request URL** to: `https://abc123.ngrok.io/slack/events`
6. Wait for the green "Verified" checkmark
7. Under **Subscribe to bot events**, ensure you have:
   - `app_mention`
   - `message.channels`
   - `message.groups`
   - `message.im`
8. Click **Save Changes**
9. If prompted, reinstall your app to the workspace

---

## Step 5: Test in Slack

### Test 1: Health Check via Logs

You should already see connection logs in both backends showing they're running.

### Test 2: Send a Test Message

In any Slack channel where your bot is a member:

```
@Engineer hello there
```

### Expected Flow:

1. **Slack Backend logs** should show:
   ```
   INFO: Received event type: app_mention
   INFO: Normalized event - Type: app_mention, User: your_name, Channel: C12345...
   ```

2. **Agent Backend logs** should show:
   ```
   INFO: [INFO] Received message from your_name in C12345: "hello there"
   INFO: Routing to agent: engineer
   INFO: Received message from your_name in C12345: "hello there"
   INFO: Generated response for request req_...
   INFO: Agent engineer completed request req_... with status: completed
   ```

3. **Slack Backend logs** should show:
   ```
   INFO: Posted reply to Slack - Channel: C12345, Thread: 1234567890.123456
   ```

4. **In Slack**, you should see the bot reply in the same thread:
   ```
   Engineer APP  [bot reply]
   I received the message. This is my response.
   ```

---

## Test 3: Manual API Test

You can also test the Agent Backend directly without Slack:

```bash
curl -X POST http://localhost:8000/agent/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test_001",
    "timestamp": "2025-10-12T10:00:00Z",
    "source": {
      "platform": "slack",
      "workspace": "test",
      "channel": "C12345",
      "thread_ts": "1234567890.123456",
      "user_id": "U123",
      "username": "TestUser"
    },
    "agent": {
      "name": "engineer",
      "type": "developer"
    },
    "message": {
      "text": "test message",
      "raw_text": "@Engineer test message"
    },
    "context": {
      "conversation_id": "C12345:1234567890.123456"
    }
  }'
```

Expected response:
```json
{
  "id": "test_001",
  "agent": {
    "name": "engineer",
    "status": "completed"
  },
  "reply": {
    "text": "I received the message. This is my response.",
    "channel": "C12345",
    "thread_ts": "1234567890.123456"
  },
  "meta": {}
}
```

---

## Troubleshooting

### Bot doesn't respond in Slack

1. **Check both backend logs** for errors
2. **Verify ngrok URL** is correct in Slack Event Subscriptions
3. **Check your .env file** has correct tokens
4. **Ensure bot is invited** to the channel (`/invite @Engineer`)
5. **Try mentioning the bot** directly with `@Engineer`

### "Invalid signature" error

- Your `SLACK_SIGNING_SECRET` is incorrect
- Update it in `.env` from your Slack app settings

### "Agent backend unavailable" error

- Ensure Agent Backend is running on port 8000
- Check `AGENT_BACKEND_URL` in `.env` is `http://localhost:8000`

### ngrok session expired

- Free ngrok URLs expire after 2 hours
- Restart ngrok and update the Slack Event Subscriptions URL

---

## Success Criteria ✅

If you see all of the following, your setup is complete:

- [ ] Both backends start without errors
- [ ] Health checks return `200 OK`
- [ ] Slack Event Subscriptions shows "Verified"
- [ ] Bot responds in Slack with: "I received the message. This is my response."
- [ ] Logs show complete message flow from Slack → Agent Backend → Slack

---

## Next Steps

Once the flow is working:

1. Replace the dummy Engineer agent with a real agent using memory and LLM
2. Implement context awareness and conversation history
3. Add MCP tool support for external actions
4. Add persistent storage for conversations

See `ai_tasks/todo/` for upcoming implementation tasks.

