# Environment Setup

## Required Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_SIGNING_SECRET=your-signing-secret-here

# Agent Backend Configuration
AGENT_BACKEND_URL=http://localhost:8000

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
```

## How to Get Slack Credentials

### 1. SLACK_BOT_TOKEN
1. Go to https://api.slack.com/apps
2. Create a new app or select your existing app
3. Navigate to "OAuth & Permissions"
4. Under "Bot Token Scopes", add the following scopes:
   - `chat:write` - Post messages
   - `users:read` - Get user information
   - `app_mentions:read` - Receive app mentions
   - `channels:history` - View messages in public channels
   - `groups:history` - View messages in private channels
   - `im:history` - View messages in direct messages
5. Install the app to your workspace
6. Copy the "Bot User OAuth Token" (starts with `xoxb-`)

### 2. SLACK_SIGNING_SECRET
1. In the same Slack app settings
2. Navigate to "Basic Information"
3. Under "App Credentials", find "Signing Secret"
4. Click "Show" and copy the value

## How to Get OpenAI API Key

### 3. OPENAI_API_KEY
1. Go to https://platform.openai.com/api-keys
2. Sign in or create an OpenAI account
3. Click **"Create new secret key"**
4. Give it a name (e.g., "QuantaFiAgent")
5. Copy the key (starts with `sk-`)
6. **Important**: Save it immediately - you won't be able to see it again!
7. Paste it into your `.env` file

**Note**: You'll need to add credits to your OpenAI account to use the API. The default model (`gpt-4o-mini`) is very cost-effective (~$0.15 per 1M input tokens).

---

## Running the Slack Backend

1. Install dependencies:
```bash
source venv/bin/activate
pip install -r ai_system/requirements.txt
```

2. Run the FastAPI server:
```bash
./run_slack_backend.sh
```

Or manually:
```bash
uvicorn ai_system.slack_backend.app:app --reload --port 3000
```

3. Expose your local server to the internet using ngrok:
```bash
ngrok http 3000
```

4. Configure Slack Event Subscriptions:
   - Go to your Slack app settings
   - Navigate to "Event Subscriptions"
   - Enable events
   - Set Request URL to: `https://your-ngrok-url.ngrok.io/slack/events`
   - Subscribe to bot events:
     - `app_mention`
     - `message.channels`
     - `message.groups`
     - `message.im`
   - Save changes

## Testing

1. Health check:
```bash
curl http://localhost:3000/healthz
```

2. Invite your bot to a channel and mention it:
```
@Engineer hello!
```

The bot should receive the event, forward it to the agent backend, and post the response back to Slack.

