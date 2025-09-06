import os
from dotenv import load_dotenv

load_dotenv()

# Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# Data Paths
DATA_PATH = os.getenv("DATA_PATH", "./data")

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION", "2024-02-15-preview")
GPT_4O_MINI_DEPLOYMENT = os.getenv("GPT_4O_MINI_DEPLOYMENT", "gpt-4o-mini")

# Fallback to standard OpenAI if Azure not configured
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Security Rules Configuration
RISK_THRESHOLDS = {
    "high": 0.8,
    "medium": 0.5,
    "low": 0.2
}

# Red Agent Behaviors
RED_AGENT_BEHAVIORS = [
    "bigger_exports",
    "scope_escalation", 
    "approval_skipping",
    "tool_reordering",
    "concurrency_spikes",
    "environment_flips"
]
