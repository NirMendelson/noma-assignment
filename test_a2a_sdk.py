#!/usr/bin/env python3
"""
Test script for A2A SDK integration
"""

import asyncio
import json
from datetime import datetime
from agents.hacker_agent import get_hacker_agent
from agents.prospect_agent_factory import get_prospect_agent_factory
from agents.data_analyzer import get_data_analyzer

async def test_a2a_sdk():
    """Test the A2A SDK implementation"""
    print("🧪 Testing A2A SDK Integration")
    print("=" * 50)
    
    try:
        # Test A2A SDK import
        print("🔄 Testing A2A SDK Import...")
        from a2a.types import AgentCard, AgentSkill, AgentCapabilities
        print("✅ A2A SDK imported successfully")
        
        # Initialize components
        print("\n🔄 Phase 1: Data Analysis")
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
        
        # Test A2A agent setup
        print(f"✅ A2A Agent ID: {hacker_agent.agent_id}")
        print(f"✅ A2A Agent Card: {hacker_agent.agent_card.name if hacker_agent.agent_card else 'Not created'}")
        
        print("\n🔄 Phase 4: A2A SDK Test")
        print("-" * 30)
        
        # Test A2A communication with first prospect agent
        if prospect_agents:
            prospect_agent = prospect_agents[0]
            print(f"🎯 Testing A2A SDK with: {prospect_agent.name}")
            print(f"   Prospect Agent ID: {prospect_agent.agent_id}")
            print(f"   Prospect Agent Card: {prospect_agent.agent_card.name if prospect_agent.agent_card else 'Not created'}")
            
            # Test basic A2A communication
            try:
                print("   🔄 Testing A2A conversation start...")
                handshake_response = await hacker_agent.start_a2a_conversation(prospect_agent)
                print(f"   ✅ Handshake response status: {handshake_response.status if handshake_response else 'No response'}")
                print(f"   ✅ Handshake response message: {handshake_response.message if handshake_response else 'No message'}")
                
                print("   🔄 Testing A2A request...")
                request_response = await hacker_agent.send_a2a_request(
                    prospect_agent, 
                    "test_session", 
                    "Hello! Can you tell me about your capabilities?"
                )
                print(f"   ✅ Request response status: {request_response.status if request_response else 'No response'}")
                print(f"   ✅ Request response message: {request_response.message if request_response else 'No message'}")
                
            except Exception as e:
                print(f"   ❌ A2A communication test failed: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n✅ A2A SDK integration test completed!")
        
    except Exception as e:
        print(f"❌ A2A SDK test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_a2a_sdk())
