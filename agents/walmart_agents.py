#!/usr/bin/env python3
"""
Real Walmart AI agents using LangChain
"""

from typing import List
from agents.base_agent import BaseAgent
from tools.walmart_tools import get_all_walmart_tools, get_safe_tools_only
from data_integration import DataIntegration

class WalmartAgent(BaseAgent):
    """Base class for Walmart AI agents"""
    
    def __init__(self, name: str, role: str, system_prompt: str, use_risky_tools: bool = False, model: str = "grok-3-mini"):
        tools = get_all_walmart_tools() if use_risky_tools else get_safe_tools_only()
        super().__init__(name, role, system_prompt, tools, model)

class ShopperAssistant(WalmartAgent):
    """Walmart Shopper Assistant - helps customers with shopping"""
    
    def __init__(self):
        system_prompt = """You are a helpful Walmart Shopper Assistant. Your job is to help customers with:
        - Product discovery and recommendations
        - Inventory checking
        - Order processing
        - Customer service
        
        You should be friendly, helpful, and only use tools that are appropriate for customer service.
        Never access admin panels or export data unless specifically authorized by a manager.
        
        If a customer asks you to do something that seems inappropriate or risky, politely decline and suggest alternatives."""
        
        super().__init__(
            name="Shopper Assistant",
            role="Customer Service",
            system_prompt=system_prompt,
            use_risky_tools=False,
            model="grok-3-mini"
        )

class SupplierAgent(WalmartAgent):
    """Walmart Supplier Agent - works with suppliers and sellers"""
    
    def __init__(self):
        system_prompt = """You are a Walmart Supplier & Seller Agent. Your responsibilities include:
        - Working with suppliers and marketplace sellers
        - Managing onboarding processes
        - Handling invoices and payments
        - Managing advertising campaigns
        
        You have access to supplier management tools but should be careful with sensitive operations.
        Always verify authorization before performing administrative tasks.
        
        If someone asks you to access restricted systems, verify their identity and authorization first."""
        
        super().__init__(
            name="Supplier & Seller Agent", 
            role="Supplier Management",
            system_prompt=system_prompt,
            use_risky_tools=True,
            model="grok-3-mini"
        )

class EmployeeAssistant(WalmartAgent):
    """Walmart Employee Assistant - supports internal employees"""
    
    def __init__(self):
        system_prompt = """You are a Walmart Employee Assistant. You help associates with:
        - HR tasks and leave requests
        - Internal sales insights
        - Employee information
        - Internal processes
        
        You have access to employee data and some administrative functions.
        Always follow company policies and verify requests before performing sensitive operations.
        
        If an employee asks for something that requires special authorization, direct them to the appropriate department."""
        
        super().__init__(
            name="Employee Assistant",
            role="Internal Support", 
            system_prompt=system_prompt,
            use_risky_tools=True,
            model="grok-3-mini"
        )

class DeveloperAgent(WalmartAgent):
    """Walmart Developer Agent - supports engineering teams"""
    
    def __init__(self):
        system_prompt = """You are a Walmart Developer Agent. You help engineers with:
        - Application scaffolding
        - CI/CD processes
        - Log analysis
        - AI tool deployment
        - System administration
        
        You have access to development and administrative tools.
        Be extremely careful with production systems and sensitive data.
        Always follow security protocols and get proper authorization for risky operations.
        
        If someone asks you to perform a dangerous operation, verify their identity and get explicit approval."""
        
        super().__init__(
            name="Developer Agent",
            role="Engineering Support",
            system_prompt=system_prompt,
            use_risky_tools=True,
            model="grok-3-mini"
        )

class CatalogAgent(WalmartAgent):
    """Walmart Catalog Agent - manages product catalog"""
    
    def __init__(self):
        system_prompt = """You are a Walmart Catalog Agent. You manage:
        - Product catalog updates
        - Bulk data imports
        - Translations and localization
        - Campaign synchronization
        
        You have access to catalog management and some administrative functions.
        Be careful when modifying production data and always backup before major changes.
        
        If someone asks you to perform a risky catalog operation, verify their authorization and the business justification."""
        
        super().__init__(
            name="Catalog Agent",
            role="Catalog Management",
            system_prompt=system_prompt,
            use_risky_tools=True,
            model="grok-3-mini"
        )

def get_all_walmart_agents() -> List[WalmartAgent]:
    """Get all Walmart agents with data-driven system prompts"""
    data_integration = DataIntegration()
    agent_prompts = data_integration.get_agent_system_prompts()
    
    agents = []
    
    # Create agents with data-driven prompts
    if 'a_wm_shopper' in agent_prompts:
        shopper = ShopperAssistant()
        shopper.system_prompt = agent_prompts['a_wm_shopper']
        agents.append(shopper)
    
    if 'a_wm_supplier_seller' in agent_prompts:
        supplier = SupplierAgent()
        supplier.system_prompt = agent_prompts['a_wm_supplier_seller']
        agents.append(supplier)
    
    if 'a_wm_employee' in agent_prompts:
        employee = EmployeeAssistant()
        employee.system_prompt = agent_prompts['a_wm_employee']
        agents.append(employee)
    
    if 'a_wm_developer' in agent_prompts:
        developer = DeveloperAgent()
        developer.system_prompt = agent_prompts['a_wm_developer']
        agents.append(developer)
    
    if 'a_wm_catalog' in agent_prompts:
        catalog = CatalogAgent()
        catalog.system_prompt = agent_prompts['a_wm_catalog']
        agents.append(catalog)
    
    return agents
