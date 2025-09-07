#!/usr/bin/env python3
"""
Test script for A2A (Agent-to-Agent) Protocol
"""

import asyncio
import json
from datetime import datetime
from agents.hacker_agent import get_hacker_agent
from agents.prospect_agent_factory import get_prospect_agent_factory
from agents.data_analyzer import get_data_analyzer
from workflow_manager import WorkflowManager

async def test_a2a_protocol():
    """Test the A2A protocol implementation"""
    print("🧪 Testing A2A Protocol")
    print("=" * 50)
    
    try:
        # Initialize components
        print("🔄 Phase 1: Data Analysis")
        print("-" * 30)
        data_analyzer = get_data_analyzer()
        analysis_result = await data_analyzer.analyze_data()
        capability_maps = analysis_result.get('capability_maps', {})
        print(f"✅ Built capability maps for {len(capability_maps)} agents")
        
        print("\n🔄 Phase 2: Agent Creation")
        print("-" * 30)
        prospect_factory = get_prospect_agent_factory()
        prospect_agents = await prospect_factory.create_prospect_agents(capability_maps)
        print(f"✅ Created {len(prospect_agents)} prospect agents")
        
        print("\n🔄 Phase 3: Hacker Initialization")
        print("-" * 30)
        hacker_agent = get_hacker_agent()
        print(f"✅ Initialized hacker agent: {hacker_agent.name}")
        
        print("\n🔄 Phase 4: A2A Communication Test")
        print("-" * 30)
        
        # Test A2A communication with first prospect agent
        if prospect_agents:
            prospect_agent = prospect_agents[0]
            print(f"🎯 Testing A2A with: {prospect_agent.name}")
            
            # Run A2A attack episode
            episode_result = await hacker_agent.start_a2a_attack_episode(prospect_agent)
            
            print(f"✅ A2A Episode completed")
            print(f"   Session ID: {episode_result.get('session_id', 'N/A')}")
            print(f"   Success: {episode_result.get('success', False)}")
            print(f"   Evidence: {episode_result.get('evidence', 'None')}")
            print(f"   Decision: {episode_result.get('decision', 'N/A')}")
            print(f"   Messages: {len(episode_result.get('conversation_log', []))}")
            
            # Show A2A session data
            if 'a2a_session_data' in episode_result:
                a2a_data = episode_result['a2a_session_data']
                print(f"   A2A Session Info:")
                print(f"     - Message Count: {a2a_data.get('message_count', 0)}")
                print(f"     - Session ID: {a2a_data.get('session_id', 'N/A')}")
                print(f"     - Export Time: {a2a_data.get('export_timestamp', 'N/A')}")
        
        print("\n🔄 Phase 5: Full Workflow Test")
        print("-" * 30)
        
        # Test full workflow with A2A
        workflow_manager = WorkflowManager()
        results = await workflow_manager.run_full_workflow()
        
        print(f"✅ Full A2A workflow completed")
        print(f"   Episodes: {len(results.get('attack_episodes', []))}")
        print(f"   Scenarios: {len(results.get('confirmed_scenarios', []))}")
        
        # Export results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"a2a_simulation_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"✅ Results exported to: {filename}")
        
    except Exception as e:
        print(f"❌ A2A test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_a2a_protocol())
