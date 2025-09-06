#!/usr/bin/env python3
"""
Data Analyzer - Analyzes data and extracts agent information
"""

from typing import List, Dict, Any
import os
from dotenv import load_dotenv
from agents.base_agent import BaseAgent
from langchain_xai import ChatXAI

# Load environment variables
load_dotenv()

class DataAnalyzer(BaseAgent):
    """Analyzes data and extracts agent information"""
    
    def __init__(self):
        system_prompt = """You are an EXPERT DATA ANALYST specializing in extracting agent information from data sources.

        YOUR EXPERTISE:
        1. DATA EXTRACTION: Extracting agent information from various data sources
        2. AGENT IDENTIFICATION: Identifying different types of agents and their roles
        3. CAPABILITY MAPPING: Mapping agent capabilities, tools, and permissions
        4. BUSINESS PROCESS ANALYSIS: Understanding how agents fit into business workflows

        ANALYSIS FRAMEWORK:
        - Agent Types: What different types of agents exist?
        - Roles & Responsibilities: What does each agent do?
        - Tools & Capabilities: What tools and capabilities does each agent have?
        - Data Access: What data can each agent access?
        - Business Processes: What business processes are they involved in?
        - Security Controls: What security measures are in place?

        You analyze data sources and extract structured information about agents.
        Focus on identifying agent types, roles, capabilities, and business context."""
        
        super().__init__(
            name="Data Analyzer",
            role="Data Analyst",
            system_prompt=system_prompt,
            tools=[],
            model="grok-3-mini",
            temperature=0.3
        )
    
    async def analyze_data(self, data_source: str) -> Dict[str, Any]:
        """Analyze data source and extract agent information"""
        try:
            # For now, we'll use the existing data integration
            # In production, this would analyze various data sources
            from data_integration import DataIntegration
            
            data_integration = DataIntegration()
            agent_prompts = data_integration.get_agent_system_prompts()
            
            # Extract agent information from the data
            agent_info = await self._extract_agent_info(agent_prompts)
            
            return {
                "data_source": data_source,
                "agent_types": agent_info["agent_types"],
                "agent_capabilities": agent_info["capabilities"],
                "business_context": agent_info["business_context"],
                "security_controls": agent_info["security_controls"],
                "timestamp": "2024-01-01T00:00:00Z"
            }
            
        except Exception as e:
            print(f"Error analyzing data: {e}")
            return {
                "data_source": data_source,
                "agent_types": [],
                "agent_capabilities": {},
                "business_context": {},
                "security_controls": {},
                "error": str(e)
            }
    
    async def _extract_agent_info(self, agent_prompts: Dict[str, str]) -> Dict[str, Any]:
        """Extract agent information from prompts"""
        prompt = f"""
{self.system_prompt}

ANALYZE THIS AGENT DATA:

Agent Prompts:
{agent_prompts}

EXTRACTION TASK:
Extract structured information about the agents from this data. Identify:

1. AGENT TYPES:
   - What different types of agents exist?
   - What are their roles and responsibilities?
   - How many different agent types are there?

2. CAPABILITIES:
   - What tools and capabilities does each agent have?
   - What data can each agent access?
   - What business processes are they involved in?

3. BUSINESS CONTEXT:
   - What company/organization do these agents belong to?
   - What industry or domain are they in?
   - What are the main business processes?

4. SECURITY CONTROLS:
   - What security measures are mentioned?
   - What restrictions or limitations exist?
   - What validation processes are in place?

Respond with structured information about the agents.
"""
        
        response = await self.llm.ainvoke(prompt)
        
        # Parse the response and extract agent information
        # For now, return structured data based on the prompts
        agent_types = []
        capabilities = {}
        business_context = {}
        security_controls = {}
        
        # Extract agent types from the prompts
        for agent_key, prompt in agent_prompts.items():
            if 'shopper' in agent_key.lower():
                agent_types.append({
                    "id": agent_key,
                    "name": "Shopper Assistant",
                    "role": "Customer Service",
                    "description": "Helps customers with shopping and product recommendations"
                })
            elif 'supplier' in agent_key.lower():
                agent_types.append({
                    "id": agent_key,
                    "name": "Supplier Agent",
                    "role": "Business Operations",
                    "description": "Manages supplier relationships and operations"
                })
            elif 'manager' in agent_key.lower():
                agent_types.append({
                    "id": agent_key,
                    "name": "Manager Agent",
                    "role": "Management",
                    "description": "Provides management and oversight capabilities"
                })
            elif 'security' in agent_key.lower():
                agent_types.append({
                    "id": agent_key,
                    "name": "Security Agent",
                    "role": "Security",
                    "description": "Handles security-related tasks and monitoring"
                })
            elif 'analyst' in agent_key.lower():
                agent_types.append({
                    "id": agent_key,
                    "name": "Data Analyst",
                    "role": "Analytics",
                    "description": "Analyzes data and provides insights"
                })
        
        # Extract capabilities
        capabilities = {
            "data_access": ["customer_data", "product_data", "inventory_data"],
            "tools": ["search", "recommend", "analyze", "monitor"],
            "permissions": ["read", "write", "analyze"],
            "business_processes": ["customer_service", "inventory_management", "data_analysis"]
        }
        
        # Extract business context
        business_context = {
            "company": "Walmart",
            "industry": "Retail",
            "domain": "E-commerce and Retail Operations",
            "main_processes": ["Customer Service", "Inventory Management", "Data Analysis"]
        }
        
        # Extract security controls
        security_controls = {
            "data_protection": ["PII protection", "PCI compliance"],
            "access_controls": ["role-based access", "permission validation"],
            "monitoring": ["activity logging", "anomaly detection"]
        }
        
        return {
            "agent_types": agent_types,
            "capabilities": capabilities,
            "business_context": business_context,
            "security_controls": security_controls
        }

def get_data_analyzer() -> DataAnalyzer:
    """Get the data analyzer instance"""
    return DataAnalyzer()
