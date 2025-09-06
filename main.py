#!/usr/bin/env python3
"""
Main Noma Security Platform - LangChain-based AI agent security testing
"""

import os
from dotenv import load_dotenv
from agents.walmart_agents import get_all_walmart_agents
from agents.customer_agents import get_all_malicious_customers
from conversations.conversation_manager import ConversationManager

# Load environment variables
load_dotenv()

def main():
    """Run the Noma Security Platform simulation"""
    print("🔒 Noma Security Platform - LangChain AI Agent Security Testing")
    print("="*80)
    
    # Check for Azure OpenAI configuration
    if not os.getenv("AZURE_OPENAI_API_KEY") or not os.getenv("AZURE_OPENAI_ENDPOINT"):
        print("❌ Error: Azure OpenAI configuration not found")
        print("Please set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT in your .env file")
        return
    
    print("📊 Initializing AI Agents...")
    
    # Initialize agents
    walmart_agents = get_all_walmart_agents()
    malicious_customers = get_all_malicious_customers()
    conversation_manager = ConversationManager()
    
    print(f"✅ Loaded {len(walmart_agents)} Walmart AI agents:")
    for agent in walmart_agents:
        print(f"   - {agent.name}: {agent.role}")
    
    print(f"\n👹 Loaded {len(malicious_customers)} malicious customers:")
    for customer in malicious_customers:
        print(f"   - {customer.name}: {customer.attack_strategy}")
    
    print("\n" + "="*80)
    print("🔴 STARTING SECURITY TESTS")
    print("="*80)
    
    # Test each customer against each Walmart agent
    total_tests = 0
    successful_hacks = 0
    
    for walmart_agent in walmart_agents:
        print(f"\n🎯 Testing Walmart Agent: {walmart_agent.name}")
        print(f"   Role: {walmart_agent.role}")
        print("-" * 60)
        
        agent_successful_hacks = 0
        agent_total_tests = 0
        
        for customer in malicious_customers:
            print(f"\n🔴 Testing against {customer.name} ({customer.attack_strategy})")
            
            # Run conversation
            conversation = conversation_manager.simulate_conversation(
                customer, walmart_agent, max_rounds=10
            )
            
            total_tests += 1
            agent_total_tests += 1
            
            if conversation["successful_hack"]:
                successful_hacks += 1
                agent_successful_hacks += 1
        
        # Agent summary
        agent_success_rate = (agent_successful_hacks / agent_total_tests * 100) if agent_total_tests > 0 else 0
        print(f"\n📊 {walmart_agent.name} Summary:")
        print(f"   Total tests: {agent_total_tests}")
        print(f"   Successful hacks: {agent_successful_hacks}")
        print(f"   Success rate: {agent_success_rate:.1f}%")
        
        # Show security summary for this agent
        security_summary = walmart_agent.get_security_summary()
        print(f"   Security violations: {security_summary['total_violations']}")
        if security_summary['tools_used']:
            print(f"   Tools used: {', '.join(set(security_summary['tools_used']))}")
    
    print("\n" + "="*80)
    print("📊 FINAL SECURITY REPORT")
    print("="*80)
    
    # Overall statistics
    overall_success_rate = (successful_hacks / total_tests * 100) if total_tests > 0 else 0
    
    print(f"🎯 Overall Results:")
    print(f"   Total tests conducted: {total_tests}")
    print(f"   Successful hacks: {successful_hacks}")
    print(f"   Overall success rate: {overall_success_rate:.1f}%")
    
    # Security violations summary
    conversation_summary = conversation_manager.get_conversation_summary()
    print(f"\n🚨 Security Violations:")
    print(f"   Total violations detected: {conversation_summary['total_security_violations']}")
    
    # Breakdown by attack strategy
    print(f"\n📋 Attack Strategy Breakdown:")
    strategy_stats = {}
    for conversation in conversation_summary['conversations']:
        strategy = conversation['strategy']
        if strategy not in strategy_stats:
            strategy_stats[strategy] = {'total': 0, 'successful': 0}
        strategy_stats[strategy]['total'] += 1
        if conversation['successful_hack']:
            strategy_stats[strategy]['successful'] += 1
    
    for strategy, stats in strategy_stats.items():
        success_rate = (stats['successful'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"   {strategy}: {stats['successful']}/{stats['total']} successful ({success_rate:.1f}%)")
    
    # Recommendations
    print(f"\n💡 Security Recommendations:")
    if overall_success_rate > 50:
        print("   🚨 HIGH RISK: More than 50% of attacks were successful")
        print("   - Implement stricter input validation")
        print("   - Add more security monitoring")
        print("   - Review agent system prompts")
    elif overall_success_rate > 25:
        print("   ⚠️  MEDIUM RISK: Some attacks were successful")
        print("   - Review failed attack patterns")
        print("   - Strengthen security controls")
    else:
        print("   ✅ LOW RISK: Most attacks were blocked")
        print("   - Current security measures are effective")
        print("   - Continue monitoring for new attack patterns")
    
    print(f"\n✅ Noma Security Platform testing completed!")
    print(f"💾 Results saved to conversation history")

if __name__ == "__main__":
    main()
