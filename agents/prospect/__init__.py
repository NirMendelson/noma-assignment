#!/usr/bin/env python3
"""
Prospect Agent Package - Contains all prospect-related functionality
"""

from .prospect_agents import ProspectAgent
from .prospect_agent_factory import ProspectAgentFactory, get_prospect_agent_factory

__all__ = [
    'ProspectAgent',
    'ProspectAgentFactory',
    'get_prospect_agent_factory'
]
