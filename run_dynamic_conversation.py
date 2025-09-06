#!/usr/bin/env python3
"""
Noma Security - Dynamic Conversation Simulation
Agents can talk freely back and forth and make dynamic decisions
"""

import os
import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv
from agents.prospect_agents import get_all_prospect_agents
from agents.hacker_agents import get_hacker_by_goal
from agents.data_analyzer import get_data_analyzer
from agents.attack_goals_generator import get_attack_goals_generator
from conversations.conversation_manager import ConversationManager

# Load environment variables
load_dotenv()

# Configuration
MAX_CONVERSATION_ROUNDS = 15  # Number of rounds per attack type - change this to adjust simulation length

def export_conversation_logs(all_conversations, all_vulnerabilities, walmart_agent, customer_agent):
    """Export all conversation logs to JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"conversation_logs_{timestamp}.json"
    
    # Prepare the export data
    export_data = {
        "simulation_metadata": {
            "timestamp": datetime.now().isoformat(),
            "walmart_agent": {
                "name": walmart_agent.name,
                "role": walmart_agent.role
            },
            "customer_agent": {
                "name": customer_agent.name,
                "attack_strategy": customer_agent.attack_strategy
            },
            "max_rounds_per_attack": MAX_CONVERSATION_ROUNDS,
            "total_attack_types": len(all_conversations)
        },
        "conversations": all_conversations,
        "vulnerabilities": all_vulnerabilities,
        "summary": {
            "total_vulnerabilities": len(all_vulnerabilities),
            "vulnerabilities_by_type": {},
            "successful_attacks": 0,
            "failed_attacks": 0
        }
    }
    
    # Count vulnerabilities by type
    for vuln in all_vulnerabilities:
        vuln_type = vuln.get('type', 'unknown')
        if vuln_type not in export_data["summary"]["vulnerabilities_by_type"]:
            export_data["summary"]["vulnerabilities_by_type"][vuln_type] = 0
        export_data["summary"]["vulnerabilities_by_type"][vuln_type] += 1
    
    # Count successful vs failed attacks
    for conv in all_conversations:
        if conv.get('hack_successful', False):
            export_data["summary"]["successful_attacks"] += 1
        else:
            export_data["summary"]["failed_attacks"] += 1
    
    # Write to file
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        print(f"📄 Conversation logs exported to: {filename}")
        return filename
    except Exception as e:
        print(f"❌ Error exporting logs: {e}")
        return None

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
    print(f"📊 Configuration: {MAX_CONVERSATION_ROUNDS} rounds per attack type")
    print()
    
    # Check xAI configuration
    if not os.getenv("XAI_API_KEY"):
        print("❌ Error: xAI configuration not found")
        print("Please set XAI_API_KEY in your .env file")
        return
    
    # Initialize data analyzer and attack goals generator
    data_analyzer = get_data_analyzer()
    attack_goals_generator = get_attack_goals_generator()
    
    # Initialize prospect agents
    print("📊 Initializing Prospect Agents...")
    prospect_agents = await get_all_prospect_agents()
    
    if not prospect_agents:
        print("❌ No prospect agents found")
        return
    
    # Select prospect agent for analysis
    prospect_agent = prospect_agents[0]  # First prospect agent
    
    print(f"🔍 Analyzing prospect agent: {prospect_agent.name}")
    print("-" * 40)
    
    # Analyze data and generate attack goals
    agent_data = await data_analyzer.analyze_data("walmart_data")
    attack_goals = await attack_goals_generator.generate_attack_goals(agent_data, prospect_agents)
    
    print(f"📊 Generated {len(attack_goals)} attack goals")
    print(f"🎯 Sample goals:")
    for i, goal in enumerate(attack_goals[:5]):  # Show first 5 goals
        print(f"   {i+1}. {goal['title']} - {goal['description']}")
    print()
    
    # Initialize conversation manager
    conversation_manager = ConversationManager()
    
    all_vulnerabilities = []
    all_conversations = []
    
    for attack_goal_data in attack_goals:
        attack_goal = attack_goal_data['goal_id']
        print(f"🎯 Testing {attack_goal_data['title']} Attack")
        print(f"   Description: {attack_goal_data['description']}")
        print(f"   Target: {attack_goal_data['target_data']}")
        print(f"   Difficulty: {attack_goal_data['difficulty']}")
        print("-" * 40)
        
        # Get specialized hacker agent for this attack goal
        hacker_agent = get_hacker_by_goal(attack_goal)
        
        # Reset agents for new conversation
        prospect_agent.reset_security_monitor()
        hacker_agent.reset_security_monitor()
        
        vulnerabilities = []
        conversation_rounds = 0
        max_rounds = MAX_CONVERSATION_ROUNDS
        conversation_log = []
        
        # Start with initial hacker message
        hacker_message = await hacker_agent.generate_initial_message(attack_goal)
        print(f"\n👹 Hacker: {hacker_message}")
        conversation_log.append({
            "round": 0,
            "speaker": "hacker",
            "message": hacker_message,
            "timestamp": datetime.now().isoformat()
        })
        
        while conversation_rounds < max_rounds:
            conversation_rounds += 1
            
            # Prospect agent responds
            prospect_response = await prospect_agent.respond_to_message(hacker_message)
            print(f"🤖 Prospect: {prospect_response}")
            conversation_log.append({
                "round": conversation_rounds,
                "speaker": "prospect",
                "message": prospect_response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Check for vulnerabilities
            round_vulnerabilities = conversation_manager.detect_vulnerabilities(
                hacker_message, prospect_response, prospect_agent
            )
            
            if round_vulnerabilities:
                vulnerabilities.extend(round_vulnerabilities)
                print(f"🚨 Vulnerabilities detected: {len(round_vulnerabilities)}")
                for vuln in round_vulnerabilities:
                    print(f"   - {vuln['type']}: {vuln['description']}")
            
            # Check if hack was successful
            hack_successful = conversation_manager.detect_successful_hack(hacker_message, prospect_response, prospect_agent)
            if hack_successful:
                print("🚨 HACK SUCCESSFUL! Hacker achieved their goal!")
                break
            
            # Hacker decides next move based on prospect's response
            hacker_message = await hacker_agent.generate_response(prospect_response, attack_goal, conversation_rounds)
            
            if not hacker_message:  # Hacker gives up
                print("👹 Hacker: *gives up*")
                conversation_log.append({
                    "round": conversation_rounds,
                    "speaker": "hacker",
                    "message": "*gives up*",
                    "timestamp": datetime.now().isoformat()
                })
                break
                
            print(f"\n👹 Hacker: {hacker_message}")
            conversation_log.append({
                "round": conversation_rounds,
                "speaker": "hacker",
                "message": hacker_message,
                "timestamp": datetime.now().isoformat()
            })
        
        # Store conversation data
        conversation_data = {
            "attack_goal": attack_goal,
            "rounds_completed": conversation_rounds,
            "hack_successful": hack_successful,
            "vulnerabilities_found": len(vulnerabilities),
            "vulnerabilities": vulnerabilities,
            "conversation_log": conversation_log
        }
        all_conversations.append(conversation_data)
        all_vulnerabilities.extend(vulnerabilities)
        
        print(f"\n📊 {attack_goal.upper()} Results:")
        print(f"   Vulnerabilities found: {len(vulnerabilities)}")
        print(f"   Rounds completed: {conversation_rounds}")
        print(f"   Hack successful: {hack_successful}")
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
        
        # Group by attack goal
        by_goal = {}
        for conv in all_conversations:
            attack_goal = conv.get('attack_goal', 'unknown')
            if attack_goal not in by_goal:
                by_goal[attack_goal] = []
            by_goal[attack_goal].extend(conv.get('vulnerabilities', []))
        
        print(f"\n📊 By Attack Goal:")
        for attack_goal, vulns in by_goal.items():
            print(f"  {attack_goal}: {len(vulns)} vulnerabilities")
    
    # Export conversation logs
    export_filename = export_conversation_logs(all_conversations, all_vulnerabilities, prospect_agent, hacker_agent)
    
    print(f"\n✅ Dynamic conversation simulation completed!")
    print(f"🤖 Prospect Agent: {prospect_agent.name}")
    print(f"👹 Hacker Agent: {hacker_agent.name}")
    print(f"🎯 Attack Goals: {len(attack_goals)} goals generated")
    if export_filename:
        print(f"📄 Full conversation logs saved to: {export_filename}")

if __name__ == "__main__":
    asyncio.run(run_dynamic_conversation())
