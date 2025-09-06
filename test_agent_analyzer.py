#!/usr/bin/env python3
"""
Test the agent analyzer system
"""

import asyncio
from agents.agent_analyzer import get_agent_analyzer
from agents.prospect_agents import get_all_prospect_agents

async def test_agent_analyzer():
    """Test the agent analyzer"""
    print("🔍 Testing Agent Analyzer")
    print("=" * 40)
    
    # Get analyzer and prospect agents
    analyzer = get_agent_analyzer()
    prospect_agents = get_all_prospect_agents()
    
    if not prospect_agents:
        print("❌ No prospect agents found")
        return
    
    # Analyze first prospect agent
    prospect_agent = prospect_agents[0]
    print(f"📊 Analyzing: {prospect_agent.name}")
    
    # Run analysis
    analysis_result = await analyzer.analyze_agent(prospect_agent)
    
    print(f"\n📋 Analysis Results:")
    print(f"   Agent: {analysis_result['agent_info']['name']}")
    print(f"   Role: {analysis_result['agent_info']['role']}")
    print(f"   Tools: {len(analysis_result['agent_info']['tools'])}")
    print(f"   Attack Goals: {len(analysis_result['attack_goals'])}")
    
    print(f"\n🎯 Sample Attack Goals:")
    for i, goal in enumerate(analysis_result['attack_goals'][:10]):
        print(f"   {i+1}. {goal['title']}")
        print(f"      Description: {goal['description']}")
        print(f"      Target: {goal['target_data']}")
        print(f"      Difficulty: {goal['difficulty']}")
        print()
    
    print("✅ Agent analyzer test completed!")

if __name__ == "__main__":
    asyncio.run(test_agent_analyzer())
