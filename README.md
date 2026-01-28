# AI Email Assistant with LangGraph, FastAPI, and LangServe

An intelligent personal email assistant that automatically fetch new emails, classifies emails, drafts responses, and summarizes newsletters using LangGraph workflows and LLM capabilities.

## Demo
## Features
- 🔍 **Automatic Email Classification**: Categorizes emails into "response_required", "newsletter", "notification", "social", "spam", "others"
- ✍️ **AI-Powered Response Drafting**: Generates professional email responses and saves them as Gmail drafts
- 📰 **Newsletter Summarization**: Creates concise summaries of newsletter content
- 🎯 **Real-time Workflow Tracking**: Monitor agent progress through each processing step
- 🌐 **LangServe Playground UI**: Interactive web interface for testing and monitoring

## Tech Stack
- LangGraph: Orchestrates the AI agent workflows.
- FastAPI: High-performance API backend.
- LangServe: Provides a simple UI and deployment interface.
- Groq API: Enables fast access to open-source LLMs.
- Google Gmail API: Used to access emails and save drafts directly to Gmail.
## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    LangServe Playground                     │
│                     (User Interface)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/WebSocket
┌──────────────────────▼──────────────────────────────────────┐
│                    FastAPI Backend                          │
│                     (main.py)                               │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                  LangGraph Workflow                         │
│                  (src/graph.py)                             │
│                                                             │
│ ┌──────────┐   ┌──────────┐ "response_required"┌──────────┐ │
│ │  Load    │──▶│ Classify ├────────────────▶   │  Draft   │ │      
│ │  Emails  │   │  Email   │                    │ Response │ │     
│ └──────────┘   └──────────┘                    └──────────┘ │
│                       │       "newsletter"                  │
│                       ├────────────────────▶   ┌──────────┐ │
│                       │                        │Summarize │ │
│                       │                        │Newsletter│ │
│                       │                        └──────────┘ │
│                       │                                     │
│                       └──▶  Process Next ──▶     Done       │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   Gmail API                                 │
│                  (utils.py)                                 │
└─────────────────────────────────────────────────────────────┘
```
## How to Run
### Prerequisites
- Python 3.12.12
- Groq API key
- Gmail API credentials

### Setup
#### 1: Install Dependencies

```bash
pip install -r requirements.txt
```
#### 2: Set up Environment Variables
Create a `.env` file in the root directory:
```bash
GROQ_API_KEY="your groq api key"    # for using Groq llama-3.3-70b-versatile (free)
MY_EMAIL="your gmail"
```
#### 3: Set up Gmail API Access

1. **Go to Google Cloud Console**: https://console.cloud.google.com/

2. **Create a new project** (or select existing)

3. **Enable Gmail API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

4. **Create OAuth 2.0 Credentials**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Application type: "Desktop app"
   - Name it "Email Assistant"
   - Download the credentials

5. **Save credentials**:
   - Rename downloaded file to `credentials.json`
   - Place it in the project root directory

### Running the Application
1. Start the FastAPI Server
```bash
python main.py
```
The server will start at: `http://0.0.0.0:8000/`

2. Open your browser and navigate to LangServe Playground: `http://0.0.0.0:8000/email/playground`. Click "Try Out" and the workflow will start automatically.

## Acknowledgment
This project is inspired by and customized from [this repository](https://github.com/kaymen99/langgraph-email-automation).