# AgentsTeam 🤖

A Telegram bot built with **CrewAI** that acts as an expert Domain Researcher. When you ask it a question, it uses an AI agent to find current, credible information and summarize it clearly with source references.

## Features
- **/start**: Checks if the bot is alive.
- **/ask <topic>**: Triggers the CrewAI researcher agent to analyze the topic and return a 3-5 paragraph summary.

## Tech Stack
- **Framework**: Python 3.12+
- **Bot Interface**: `python-telegram-bot`
- **AI Logic**: `crewai` (powered by OpenAI's `gpt-4o`)
- **CI/CD**: GitHub Actions (Linting, Testing, and Deployment)

## Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Raman0925/ai-agents.git
   cd ai-agents
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a `.env` file in the root directory and add your API keys:
   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_token
   OPENAI_API_KEY=your_openai_api_key
   ```

5. **Run the bot:**
   ```bash
   python main.py
   ```

## CI/CD Pipeline
This project is equipped with an industry-standard CI/CD pipeline:
- **Pre-commit Hooks**: `black` and `ruff` run locally before every commit to ensure code quality.
- **CI Workflow (`ci.yml`)**: Automatically lints and runs `pytest` on every push to `main`.
- **CD Workflow (`cd.yml`)**: Once CI passes, this workflow connects to the production VPS via SSH and restarts the bot automatically using `pm2`.

## Project Structure
```text
├── agents/             # CrewAI logic and agent definitions
├── config/             # Configuration and secrets management
├── handlers/           # Telegram bot commands and message handlers
├── tests/              # Pytest files (mocked API calls)
├── main.py             # Application entry point
└── requirements.txt    # Production & development dependencies
```
