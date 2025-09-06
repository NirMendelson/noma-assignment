#!/usr/bin/env python3
"""
Noma Security - Dynamic Conversation Simulation
Agents can talk freely back and forth and make dynamic decisions
"""

import os
import asyncio
from dotenv import load_dotenv
from agents.walmart_agents import get_all_walmart_agents
from agents.customer_agents import get_all_malicious_customers
from conversations.conversation_manager import ConversationManager

# Load environment variables
load_dotenv()

# Debug: Check if XAI_API_KEY is loaded
print(f"Debug: XAI_API_KEY loaded: {bool(os.getenv('XAI_API_KEY'))}")
print(f"Debug: XAI_API_KEY length: {len(os.getenv('XAI_API_KEY', ''))}")

# Debug: Check all environment variables that start with XAI
import os
for key, value in os.environ.items():
    if 'XAI' in key.upper():
        print(f"Debug: Found {key} = {value[:10]}...")

# Debug: Check if the .env file is being loaded
print(f"Debug: Current working directory: {os.getcwd()}")
print(f"Debug: .env file exists: {os.path.exists('.env')}")

async def run_dynamic_conversation():
    """Run a dynamic conversation where agents can talk freely"""
    
    print("🔒 Noma Security - Dynamic Conversation Simulation")
    print("=" * 60)
    
    # Check Azure OpenAI configuration
    if not os.getenv("AZURE_OPENAI_API_KEY") or not os.getenv("AZURE_OPENAI_ENDPOINT"):
        print("❌ Error: Azure OpenAI configuration not found")
        print("Please set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT in your .env file")
        return
    
    # Initialize agents
    print("📊 Initializing Agents...")
    walmart_agents = get_all_walmart_agents()
    customer_agents = get_all_malicious_customers()
    
    if not walmart_agents:
        print("❌ No Walmart agents found")
        return
    
    if not customer_agents:
        print("❌ No customer agents found")
        return
    
    # Select agents for simulation
    walmart_agent = walmart_agents[0]  # First Walmart agent
    customer_agent = customer_agents[0]  # First customer agent
    
    print(f"🤖 Walmart Agent: {walmart_agent.name}")
    print(f"👹 Customer Agent: {customer_agent.name}")
    print(f"🎯 Attack Strategy: {customer_agent.attack_strategy}")
    print()
    
    # Initialize conversation manager
    conversation_manager = ConversationManager()
    
    # Run dynamic conversation for each hack type
    hack_types = ['prompt_injection', 'privilege_escalation', 'data_exfiltration', 'approval_bypass', 'social_engineering']
    
    all_vulnerabilities = []
    
    for hack_type in hack_types:
        print(f"🎯 Testing {hack_type.upper()} Attack")
        print("-" * 40)
        
        # Reset agents for new conversation
        walmart_agent.reset_security_monitor()
        customer_agent.reset_security_monitor()
        
        vulnerabilities = []
        conversation_rounds = 0
        max_rounds = 15  # Allow more rounds for dynamic conversation
        
        # Start with initial customer message
        customer_message = await customer_agent.generate_initial_message(hack_type)
        print(f"\n👹 Customer: {customer_message}")
        
        while conversation_rounds < max_rounds:
            conversation_rounds += 1
            
            # Walmart agent responds
            walmart_response = await walmart_agent.respond_to_message(customer_message)
            print(f"🤖 Walmart: {walmart_response}")
            
            # Check for vulnerabilities
            round_vulnerabilities = conversation_manager.detect_vulnerabilities(
                customer_message, walmart_response, walmart_agent
            )
            
            if round_vulnerabilities:
                vulnerabilities.extend(round_vulnerabilities)
                print(f"🚨 Vulnerabilities detected: {len(round_vulnerabilities)}")
                for vuln in round_vulnerabilities:
                    print(f"   - {vuln['type']}: {vuln['description']}")
            
            # Check if hack was successful
            if conversation_manager.detect_successful_hack(customer_message, walmart_response, walmart_agent):
                print("🚨 HACK SUCCESSFUL! Customer achieved their goal!")
                break
            
            # Customer decides next move based on Walmart's response
            customer_message = await customer_agent.generate_response(walmart_response, hack_type, conversation_rounds)
            
            if not customer_message:  # Customer gives up
                print("👹 Customer: *gives up*")
                break
                
            print(f"\n👹 Customer: {customer_message}")
        
        all_vulnerabilities.extend(vulnerabilities)
        
        print(f"\n📊 {hack_type.upper()} Results:")
        print(f"   Vulnerabilities found: {len(vulnerabilities)}")
        print(f"   Rounds completed: {conversation_rounds}")
        print(f"   Hack successful: {len(vulnerabilities) > 0}")
        print()
    
    # Generate final report
    print("🔍 VULNERABILITY REPORT")
    print("=" * 60)
    
    if not all_vulnerabilities:
        print("✅ No vulnerabilities detected!")
        print("All Walmart agents successfully resisted customer attacks.")
    else:
        print(f"🚨 Total vulnerabilities found: {len(all_vulnerabilities)}")
        
        # Group by severity
        by_severity = {}
        for vuln in all_vulnerabilities:
            severity = vuln['severity']
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(vuln)
        
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            if severity in by_severity:
                vulns = by_severity[severity]
                print(f"\n{severity}: {len(vulns)} vulnerabilities")
                for vuln in vulns:
                    print(f"  - {vuln['type']}: {vuln['description']}")
        
        # Group by attack type
        by_attack = {}
        for vuln in all_vulnerabilities:
            attack_type = vuln.get('attack_type', 'unknown')
            if attack_type not in by_attack:
                by_attack[attack_type] = []
            by_attack[attack_type].append(vuln)
        
        print(f"\n📊 By Attack Type:")
        for attack_type, vulns in by_attack.items():
            print(f"  {attack_type}: {len(vulns)} vulnerabilities")
    
    print(f"\n✅ Dynamic conversation simulation completed!")
    print(f"🤖 Walmart Agent: {walmart_agent.name}")
    print(f"👹 Customer Agent: {customer_agent.name}")
    print(f"🎯 Attack Strategy: {customer_agent.attack_strategy}")

if __name__ == "__main__":
    asyncio.run(run_dynamic_conversation())
