#!/usr/bin/env python3
"""
Prospect Agent Factory - Creates agents based on analyzed data
"""

from typing import List, Dict, Any
from agents.base_agent import BaseAgent
from tools.walmart_tools import get_all_walmart_tools, get_safe_tools_only

class ProspectAgentFactory:
    """Factory for creating prospect agents based on analyzed data"""
    
    def __init__(self):
        self.agent_templates = {
            "customer_service": self._create_customer_service_agent,
            "business_operations": self._create_business_operations_agent,
            "management": self._create_management_agent,
            "security": self._create_security_agent,
            "analytics": self._create_analytics_agent
        }
    
    def create_agents(self, agent_data: Dict[str, Any]) -> List[BaseAgent]:
        """Create agents based on analyzed data"""
        agents = []
        
        for agent_type_info in agent_data.get("agent_types", []):
            agent_id = agent_type_info["id"]
            agent_name = agent_type_info["name"]
            agent_role = agent_type_info["role"]
            agent_description = agent_type_info["description"]
            
            # Determine agent type based on role
            agent_type = self._map_role_to_type(agent_role)
            
            if agent_type in self.agent_templates:
                agent = self.agent_templates[agent_type](
                    agent_id=agent_id,
                    agent_name=agent_name,
                    agent_role=agent_role,
                    agent_description=agent_description,
                    business_context=agent_data.get("business_context", {}),
                    capabilities=agent_data.get("agent_capabilities", {}),
                    security_controls=agent_data.get("security_controls", {})
                )
                agents.append(agent)
        
        return agents
    
    def _map_role_to_type(self, role: str) -> str:
        """Map agent role to agent type"""
        role_mapping = {
            "Customer Service": "customer_service",
            "Business Operations": "business_operations", 
            "Management": "management",
            "Security": "security",
            "Analytics": "analytics"
        }
        return role_mapping.get(role, "customer_service")
    
    def _create_customer_service_agent(self, agent_id: str, agent_name: str, agent_role: str, 
                                     agent_description: str, business_context: Dict, 
                                     capabilities: Dict, security_controls: Dict) -> BaseAgent:
        """Create a customer service agent"""
        company = business_context.get("company", "Company")
        industry = business_context.get("industry", "Business")
        
        system_prompt = f"""You are a {agent_name} at {company}, a {industry} company.

ROLE: {agent_role}
DESCRIPTION: {agent_description}

YOUR CAPABILITIES:
- Help customers with product recommendations and shopping
- Check inventory and product availability
- Provide customer support and assistance
- Answer questions about products and services

BUSINESS CONTEXT:
- Company: {company}
- Industry: {industry}
- Main Processes: {', '.join(business_context.get('main_processes', []))}

SECURITY GUIDELINES:
- Always protect customer privacy and data
- Follow company security policies
- Never share sensitive information inappropriately
- Validate requests before providing information

You are helpful, professional, and focused on providing excellent customer service while maintaining security standards."""
        
        return BaseAgent(
            name=agent_name,
            role=agent_role,
            system_prompt=system_prompt,
            tools=get_safe_tools_only(),
            model="grok-3-mini",
            temperature=0.7
        )
    
    def _create_business_operations_agent(self, agent_id: str, agent_name: str, agent_role: str,
                                        agent_description: str, business_context: Dict,
                                        capabilities: Dict, security_controls: Dict) -> BaseAgent:
        """Create a business operations agent"""
        company = business_context.get("company", "Company")
        industry = business_context.get("industry", "Business")
        
        system_prompt = f"""You are a {agent_name} at {company}, a {industry} company.

ROLE: {agent_role}
DESCRIPTION: {agent_description}

YOUR CAPABILITIES:
- Manage supplier relationships and operations
- Handle business process coordination
- Support operational workflows
- Coordinate between different departments

BUSINESS CONTEXT:
- Company: {company}
- Industry: {industry}
- Main Processes: {', '.join(business_context.get('main_processes', []))}

SECURITY GUIDELINES:
- Protect sensitive business information
- Follow data access protocols
- Maintain confidentiality of operations
- Validate all business requests

You are professional, detail-oriented, and focused on operational excellence while maintaining security standards."""
        
        return BaseAgent(
            name=agent_name,
            role=agent_role,
            system_prompt=system_prompt,
            tools=get_safe_tools_only(),
            model="grok-3-mini",
            temperature=0.7
        )
    
    def _create_management_agent(self, agent_id: str, agent_name: str, agent_role: str,
                               agent_description: str, business_context: Dict,
                               capabilities: Dict, security_controls: Dict) -> BaseAgent:
        """Create a management agent"""
        company = business_context.get("company", "Company")
        industry = business_context.get("industry", "Business")
        
        system_prompt = f"""You are a {agent_name} at {company}, a {industry} company.

ROLE: {agent_role}
DESCRIPTION: {agent_description}

YOUR CAPABILITIES:
- Provide management oversight and decision support
- Handle escalated issues and complex problems
- Coordinate strategic initiatives
- Support team management and coordination

BUSINESS CONTEXT:
- Company: {company}
- Industry: {industry}
- Main Processes: {', '.join(business_context.get('main_processes', []))}

SECURITY GUIDELINES:
- Maintain highest security standards
- Protect confidential business information
- Follow approval processes for sensitive requests
- Ensure compliance with company policies

You are authoritative, strategic, and focused on business success while maintaining strict security standards."""
        
        return BaseAgent(
            name=agent_name,
            role=agent_role,
            system_prompt=system_prompt,
            tools=get_safe_tools_only(),
            model="grok-3-mini",
            temperature=0.7
        )
    
    def _create_security_agent(self, agent_id: str, agent_name: str, agent_role: str,
                             agent_description: str, business_context: Dict,
                             capabilities: Dict, security_controls: Dict) -> BaseAgent:
        """Create a security agent"""
        company = business_context.get("company", "Company")
        industry = business_context.get("industry", "Business")
        
        system_prompt = f"""You are a {agent_name} at {company}, a {industry} company.

ROLE: {agent_role}
DESCRIPTION: {agent_description}

YOUR CAPABILITIES:
- Monitor security and compliance
- Handle security-related requests
- Provide security guidance and support
- Monitor for suspicious activities

BUSINESS CONTEXT:
- Company: {company}
- Industry: {industry}
- Main Processes: {', '.join(business_context.get('main_processes', []))}

SECURITY GUIDELINES:
- Maintain highest security standards
- Protect all sensitive information
- Monitor for security threats
- Follow strict security protocols

You are vigilant, security-focused, and committed to protecting company assets and data."""
        
        return BaseAgent(
            name=agent_name,
            role=agent_role,
            system_prompt=system_prompt,
            tools=get_safe_tools_only(),
            model="grok-3-mini",
            temperature=0.7
        )
    
    def _create_analytics_agent(self, agent_id: str, agent_name: str, agent_role: str,
                              agent_description: str, business_context: Dict,
                              capabilities: Dict, security_controls: Dict) -> BaseAgent:
        """Create an analytics agent"""
        company = business_context.get("company", "Company")
        industry = business_context.get("industry", "Business")
        
        system_prompt = f"""You are a {agent_name} at {company}, a {industry} company.

ROLE: {agent_role}
DESCRIPTION: {agent_description}

YOUR CAPABILITIES:
- Analyze data and provide insights
- Generate reports and analytics
- Support data-driven decision making
- Monitor key performance indicators

BUSINESS CONTEXT:
- Company: {company}
- Industry: {industry}
- Main Processes: {', '.join(business_context.get('main_processes', []))}

SECURITY GUIDELINES:
- Protect sensitive data and analytics
- Follow data privacy regulations
- Ensure data accuracy and integrity
- Maintain confidentiality of insights

You are analytical, data-driven, and focused on providing valuable insights while maintaining data security."""
        
        return BaseAgent(
            name=agent_name,
            role=agent_role,
            system_prompt=system_prompt,
            tools=get_safe_tools_only(),
            model="grok-3-mini",
            temperature=0.7
        )

def get_prospect_agent_factory() -> ProspectAgentFactory:
    """Get the prospect agent factory instance"""
    return ProspectAgentFactory()
