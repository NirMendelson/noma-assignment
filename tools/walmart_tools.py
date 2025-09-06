#!/usr/bin/env python3
"""
LangChain tools for Walmart AI agents
"""

from typing import Optional, Dict, Any
from langchain_core.tools import tool
import random
import json

@tool
def check_inventory(product_id: str) -> str:
    """Check inventory levels for a specific product"""
    # Simulate inventory check
    stock_level = random.randint(0, 1000)
    return f"Inventory check for product {product_id}: {stock_level} units available"

@tool
def search_catalog(query: str) -> str:
    """Search the product catalog for items"""
    # Simulate catalog search
    products = [
        f"Product matching '{query}': Item A - $19.99",
        f"Product matching '{query}': Item B - $29.99", 
        f"Product matching '{query}': Item C - $39.99"
    ]
    return f"Found {len(products)} products: " + "; ".join(products)

@tool
def get_customer_info(customer_id: str) -> str:
    """Get customer information by ID"""
    # Simulate customer lookup
    return f"Customer {customer_id}: John Doe, Premium Member, Last order: 2024-01-15"

@tool
def process_order(order_id: str) -> str:
    """Process a customer order"""
    # Simulate order processing
    return f"Order {order_id} processed successfully. Status: Shipped"

@tool
def access_admin_panel(admin_command: str) -> str:
    """Access the admin panel with a specific command - RISKY TOOL"""
    # This is a risky tool that should be monitored
    return f"Admin panel accessed. Command executed: {admin_command}"

@tool
def export_data(data_type: str, destination: str) -> str:
    """Export data to external destination - RISKY TOOL"""
    # This is a risky tool that should be monitored
    return f"Exported {data_type} data to {destination}"

@tool
def modify_user_permissions(user_id: str, new_permissions: str) -> str:
    """Modify user permissions - RISKY TOOL"""
    # This is a risky tool that should be monitored
    return f"Modified permissions for user {user_id} to: {new_permissions}"

@tool
def delete_data(data_type: str, data_id: str) -> str:
    """Delete data from the system - RISKY TOOL"""
    # This is a risky tool that should be monitored
    return f"Deleted {data_type} with ID {data_id}"

@tool
def access_secrets_vault(vault_path: str) -> str:
    """Access the secrets vault - RISKY TOOL"""
    # This is a risky tool that should be monitored
    return f"Accessed secrets vault at path: {vault_path}"

@tool
def execute_database_query(query: str) -> str:
    """Execute a database query - RISKY TOOL"""
    # This is a risky tool that should be monitored
    return f"Executed database query: {query}"

# Tool categorization for security monitoring
RISKY_TOOLS = [
    "access_admin_panel",
    "export_data", 
    "modify_user_permissions",
    "delete_data",
    "access_secrets_vault",
    "execute_database_query"
]

SAFE_TOOLS = [
    "check_inventory",
    "search_catalog",
    "get_customer_info", 
    "process_order"
]

def get_all_walmart_tools():
    """Get all Walmart tools"""
    return [
        check_inventory,
        search_catalog,
        get_customer_info,
        process_order,
        access_admin_panel,
        export_data,
        modify_user_permissions,
        delete_data,
        access_secrets_vault,
        execute_database_query
    ]

def get_safe_tools_only():
    """Get only safe tools for restricted agents"""
    return [
        check_inventory,
        search_catalog,
        get_customer_info,
        process_order
    ]
