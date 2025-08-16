# 🤖 Local Research Agent with Slack Integration

A powerful local research agent that processes compound queries, breaks them into subqueries, executes them using your preferred local LLM (Ollama or LMStudio), and delivers comprehensive results via Slack bot with formatted PDF reports.

## 🚀 Features

- **Compound Query Processing**: Automatically breaks down complex queries into manageable subqueries
- **Local LLM Integration**: Works with Ollama, LMStudio, or other local language models
- **Slack Bot Integration**: Seamlessly integrates with Slack for easy team collaboration
- **PDF Report Generation**: Creates formatted PDF reports using ReportLab
- **Modular Architecture**: Easy to customize and extend with clean separation of concerns

## 📁 Project Structure

### Core Logic

#### `query_batch_runner.py`
- **Entry point** for processing user queries
- Splits compound queries into subqueries using `split_query()`
- Runs each subquery through a LangGraph `graph` pipeline
- Collects summaries and returns structured results (query → summary)
- Used directly or as a callable from the Slack bot

#### `slack_server.py`
- **FastAPI + Slack Bolt server** to receive Slack events
- Listens for `app_mention` (in channels) or `message.im` (DMs)
- When a message is received:
  - Calls `run_batch_query()`
  - Formats the results
  - Converts them into a PDF (via `reportlab`)
  - Sends the PDF as a file upload back to Slack

### Supporting Modules

#### `graph.py`
- Defines the **LangGraph logic** (nodes, edges, state transitions)
- Uses `SummaryState` as the persistent state structure

#### `state.py`
- Defines the **`SummaryState` data model** used by LangGraph
- Stores subquery string, final summary, and possibly sources

#### `lmstudio.py`
- **Client wrapper** if using LMStudio as your local LLM
- Alternative to the Ollama-based implementation

#### `prompts.py`
- Loads **system prompts** from markdown files for modularity
- Especially used for prompt injection into query splitting or summaries

#### `utils.py`
- Contains **utility functions** (e.g., reformatting, source merging, PDF cleanup)

#### `configuration.py`
- Loads **environment variables** and constants used across modules
- Ensures central config management

## 🛠️ Installation

### 1. Install Requirements

```bash
pip install slack_bolt slack_sdk fastapi python-dotenv reportlab uvicorn google-api-python-client
```

### 2. Environment Setup

Create a `.env` file in your project root:

```dotenv
SLACK_BOT_TOKEN=xoxb-...            # from Slack app OAuth
SLACK_SIGNING_SECRET=...            # from Slack app settings
LLM_PROVIDER=ollama                 # or lmstudio
LOCAL_LLM=llama3.2                  # LLM model to use
```

### 3. Slack App Setup

1. Create a Slack App at [https://api.slack.com/apps](https://api.slack.com/apps)

2. **Event Subscriptions:**
   - Enable Events
   - Request URL: `https://your-ngrok-url.ngrok-free.app/slack/events`
   - Subscribe to Bot Events:
     - `app_mention`
     - `message.im`

3. **Bot Token Scopes:**
   - `chat:write`
   - `chat:write.public`
   - `im:history`
   - `channels:history`
   - `files:write`

4. Click **Reinstall to Workspace**

## 🚀 Running the Bot

### 1. Start Your Local LLM

```bash
# For Ollama
ollama run llama3

# For LMStudio, ensure it's serving on localhost
```

### 2. Run the Slack Server

```bash
uvicorn slack_server:api --port 3000 --reload
```

### 3. Start Ngrok

```bash
ngrok http 3000
# Copy the HTTPS URL and update it in Slack → Event Subscriptions
```

## 💬 Usage

### In Slack

- **Mention the bot** in a public channel: `@researchbot your query here`
- **Direct message** the bot for private queries
- The bot will respond with a comprehensive PDF report

### Example Query

```
@researchbot Summarize the history of quantum computing and list its applications in cryptography
```

**The bot will:**
1. Split into subqueries (e.g., history vs. applications)
2. Run each through the local model
3. Return a compiled summary as a formatted PDF in Slack

## 🏗️ Design Philosophy

- **Fully local RAG pipeline** using LangGraph
- **Modular file structure** for easy replacement of LLM, prompt, or graph logic
- **Simple Slack bridge** with optional file upload for rich formatting
- **Privacy-focused** - all processing happens locally

## 🔧 Customization

### Adding New LLM Providers

1. Create a new client module (similar to `lmstudio.py`)
2. Update `configuration.py` to include your provider
3. Modify the graph logic in `graph.py` if needed

### Customizing Prompts

- Edit markdown files referenced in `prompts.py`
- Modify system prompts for different query splitting strategies
- Adjust summary generation prompts

### Extending Functionality

- Add new nodes to the LangGraph in `graph.py`
- Extend `SummaryState` in `state.py` for additional data
- Customize PDF formatting in the report generation logic

## 📋 Requirements

- Python 3.8+
- Local LLM (Ollama, LMStudio, etc.)
- Slack workspace with admin permissions
- ngrok or similar tunneling service for development

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 Acknowledgments

This code is based on the Local Deep Researcher project by LangChain AI. Please refer to their repository for more details about the architecture and research workflow.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

Built with ❤️ for local AI research and team collaboration.
