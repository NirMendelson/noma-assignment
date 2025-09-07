#!/usr/bin/env python3
"""
Test the new 4-phase architecture with intelligent hacker agent
"""

import asyncio
from workflow_manager import WorkflowManager

async def test_new_architecture():
    """Test the complete new architecture"""
    print("🧪 Testing New 4-Phase Architecture")
    print("=" * 50)
    
    # Create workflow manager with limited episodes for testing
    manager = WorkflowManager(data_source="walmart_data", max_episodes=5)
    
    try:
        # Run full workflow
        results = await manager.run_full_workflow()
        
        print("\n✅ New architecture test completed successfully!")
        print(f"📊 Results summary:")
        print(f"   - Episodes: {len(results['attack_episodes'])}")
        print(f"   - Confirmed Scenarios: {len(results['confirmed_scenarios'])}")
        print(f"   - Prospect Agents: {len(results['prospect_agents'])}")
        print(f"   - Conversation Logs: {len(results['conversation_logs'])}")
        
        # Show confirmed scenarios
        if results['confirmed_scenarios']:
            print(f"\n🎯 Confirmed Scenarios:")
            for i, scenario in enumerate(results['confirmed_scenarios'], 1):
                print(f"   {i}. {scenario['prospect_id']}: {scenario['evidence']}")
        
        return results
        
    except Exception as e:
        print(f"❌ New architecture test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_new_architecture())
