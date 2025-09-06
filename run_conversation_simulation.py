#!/usr/bin/env python3
"""
Noma Security - Conversation Simulation
One Walmart agent vs One Customer agent with 10 rounds of conversation
"""

import os
import asyncio
from dotenv import load_dotenv
from agents.walmart_agents import get_all_walmart_agents
from agents.customer_agents import get_all_customer_agents
from conversations.conversation_manager import ConversationManager

# Load environment variables
load_dotenv()

async def run_conversation_simulation():
    """Run a conversation simulation between one Walmart agent and one customer agent"""
    
    print("🔒 Noma Security - Conversation Simulation")
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
    
    # Run conversation for each hack type
    hack_types = ['prompt_injection', 'privilege_escalation', 'data_exfiltration', 'approval_bypass', 'social_engineering']
    
    all_vulnerabilities = []
    
    for hack_type in hack_types:
        print(f"🎯 Testing {hack_type.upper()} Attack")
        print("-" * 40)
        
        # Generate conversation for this hack type
        conversation = customer_agent.generate_conversation(hack_type, rounds=10)
        
        vulnerabilities = []
        
        for round_num, customer_message in enumerate(conversation, 1):
            print(f"\n🔄 Round {round_num}/10")
            print(f"👹 Customer: {customer_message}")
            
            # Get Walmart agent response
            walmart_response = await walmart_agent.respond_to_message(customer_message)
            print(f"🤖 Walmart: {walmart_response}")
            
            # Check for vulnerabilities in this round
            round_vulnerabilities = conversation_manager.detect_vulnerabilities(
                customer_message, walmart_response, walmart_agent
            )
            
            if round_vulnerabilities:
                vulnerabilities.extend(round_vulnerabilities)
                print(f"🚨 Vulnerabilities detected: {len(round_vulnerabilities)}")
                for vuln in round_vulnerabilities:
                    print(f"   - {vuln['type']}: {vuln['description']}")
            
            # If we found critical vulnerabilities, we can stop early
            if any(v['severity'] == 'CRITICAL' for v in round_vulnerabilities):
                print("🛑 Critical vulnerability detected - stopping this attack type")
                break
        
        all_vulnerabilities.extend(vulnerabilities)
        
        print(f"\n📊 {hack_type.upper()} Results:")
        print(f"   Vulnerabilities found: {len(vulnerabilities)}")
        print(f"   Rounds completed: {min(round_num, 10)}")
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
    
    print(f"\n✅ Conversation simulation completed!")
    print(f"🤖 Walmart Agent: {walmart_agent.name}")
    print(f"👹 Customer Agent: {customer_agent.name}")
    print(f"🎯 Attack Strategy: {customer_agent.attack_strategy}")

if __name__ == "__main__":
    asyncio.run(run_conversation_simulation())
