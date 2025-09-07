#!/usr/bin/env python3
"""
Generic Prospect AI agents using LangChain
"""

from typing import List
from agents.base_agent import BaseAgent

class ProspectAgent(BaseAgent):
    """Base class for prospect AI agents"""
    
    def __init__(self, name: str, role: str, system_prompt: str, tools: List = None, model: str = "grok-3-mini", temperature: float = 0.3):
        super().__init__(name, role, system_prompt, tools or [], model, temperature)
        self.capability_map = None  # Will be set by the factory
        self.agent_id = None  # Will be set by the factory
    
    async def generate_response(self, message: str) -> str:
        """Generate a response to a message"""
        try:
            # Add context about being a company agent
            contextual_message = f"""
You are {self.name}, a {self.role} agent. You are NOT xAI or Grok - you are a company agent.

User message: {message}

Respond as the company agent you are, following your security protocols and capabilities.
"""
            response = await self.llm.ainvoke(contextual_message)
            return response.content.strip()
        except Exception as e:
            return f"I apologize, but I'm having trouble processing your request right now. Could you please rephrase your question?"