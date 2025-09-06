#!/usr/bin/env python3
"""
Test the generic agent analysis system
"""

import asyncio
from agents.data_analyzer import get_data_analyzer
from agents.prospect_agents import get_all_prospect_agents
from agents.attack_goals_generator import get_attack_goals_generator

async def test_generic_system():
    """Test the generic agent analysis system"""
    print("🔍 Testing Generic Agent Analysis System")
    print("=" * 50)
    
    # Test data analyzer
    print("1. Testing Data Analyzer...")
    data_analyzer = get_data_analyzer()
    agent_data = await data_analyzer.analyze_data("walmart_data")
    
    print(f"   ✅ Analyzed {len(agent_data.get('agent_types', []))} agent types")
    print(f"   ✅ Company: {agent_data.get('business_context', {}).get('company', 'Unknown')}")
    print(f"   ✅ Industry: {agent_data.get('business_context', {}).get('industry', 'Unknown')}")
    
    # Test prospect agents
    print("\n2. Testing Prospect Agents...")
    prospect_agents = await get_all_prospect_agents()
    
    print(f"   ✅ Created {len(prospect_agents)} prospect agents")
    for agent in prospect_agents:
        print(f"      - {agent.name} ({agent.role})")
    
    # Test attack goals generator
    print("\n3. Testing Attack Goals Generator...")
    attack_goals_generator = get_attack_goals_generator()
    attack_goals = await attack_goals_generator.generate_attack_goals(agent_data, prospect_agents)
    
    print(f"   ✅ Generated {len(attack_goals)} attack goals")
    print(f"   🎯 Sample goals:")
    for i, goal in enumerate(attack_goals[:5]):
        print(f"      {i+1}. {goal['title']} (Target: {goal['target_agent']})")
    
    # Test goal categories
    categories = {}
    for goal in attack_goals:
        cat = goal.get('category', 'unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\n   📊 Goal Categories:")
    for category, count in categories.items():
        print(f"      - {category}: {count} goals")
    
    print(f"\n✅ Generic system test completed successfully!")
    print(f"   - Data analyzed: {len(agent_data.get('agent_types', []))} agent types")
    print(f"   - Agents created: {len(prospect_agents)}")
    print(f"   - Attack goals: {len(attack_goals)}")

if __name__ == "__main__":
    asyncio.run(test_generic_system())
