"""
Azure OpenAI configuration utilities
"""

import os
from typing import Optional
from config import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    OPENAI_API_VERSION,
    GPT_4O_MINI_DEPLOYMENT,
    OPENAI_API_KEY
)

def get_openai_client():
    """Get configured OpenAI client (Azure or standard)"""
    try:
        from openai import AzureOpenAI, OpenAI
        
        # Check if Azure OpenAI is configured
        if AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY:
            return AzureOpenAI(
                azure_endpoint=AZURE_OPENAI_ENDPOINT,
                api_key=AZURE_OPENAI_API_KEY,
                api_version=OPENAI_API_VERSION
            )
        
        # Fallback to standard OpenAI
        elif OPENAI_API_KEY:
            return OpenAI(api_key=OPENAI_API_KEY)
        
        else:
            raise ValueError("No OpenAI configuration found. Please set Azure OpenAI or standard OpenAI credentials.")
    
    except ImportError:
        raise ImportError("OpenAI package not installed. Run: pip install openai")

def get_deployment_name() -> Optional[str]:
    """Get the deployment name for Azure OpenAI"""
    return GPT_4O_MINI_DEPLOYMENT if AZURE_OPENAI_ENDPOINT else None

def is_azure_configured() -> bool:
    """Check if Azure OpenAI is properly configured"""
    return bool(AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY)

def get_model_name() -> str:
    """Get the model name to use"""
    if is_azure_configured():
        return GPT_4O_MINI_DEPLOYMENT
    else:
        return "gpt-4o-mini"  # Default model for standard OpenAI
