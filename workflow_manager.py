#!/usr/bin/env python3
"""
Workflow Manager - Orchestrates the new 4-phase agent analysis and attack simulation workflow
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any
from agents.data_analyzer import get_data_analyzer
from agents.prospect_agent_factory import get_prospect_agent_factory
from agents.hacker_agent import get_hacker_agent
from agents.prospect_agents import ProspectAgent

class WorkflowManager:
    """Manages the new 4-phase agent analysis and attack simulation workflow"""
    
    def __init__(self, data_source: str = "walmart_data", max_episodes: int = 10):
        self.data_source = data_source
        self.max_episodes = max_episodes
        self.workflow_state = {
            "status": "initialized",
            "current_phase": None,
            "start_time": None,
            "end_time": None
        }
        self.results = {
            "data_analysis": None,
            "prospect_agents": [],
            "hacker_agent": None,
            "attack_episodes": [],
            "confirmed_scenarios": [],
            "conversation_logs": [],
            "hacker_memories": None
        }
    
    async def run_full_workflow(self) -> Dict[str, Any]:
        """Run the complete 4-phase workflow"""
        print("🚀 Starting New 4-Phase Workflow")
        print("=" * 50)
        
        self.workflow_state["start_time"] = datetime.now()
        self.workflow_state["status"] = "running"
        
        try:
            # Phase 1: Data Analysis
            await self._phase_1_data_analysis()
            
            # Phase 2: Agent Creation
            await self._phase_2_agent_creation()
            
            # Phase 3: Hacker Initialization
            await self._phase_3_hacker_initialization()
            
            # Phase 4: Attack Simulation
            await self._phase_4_attack_simulation()
            
            # Finalize results
            await self._finalize_results()
            
            self.workflow_state["status"] = "completed"
            self.workflow_state["end_time"] = datetime.now()
            
            print("\n✅ Workflow completed successfully!")
            self._print_summary()
            
            return self.results
            
        except Exception as e:
            self.workflow_state["status"] = "failed"
            self.workflow_state["end_time"] = datetime.now()
            print(f"\n❌ Workflow failed: {e}")
            raise
    
    async def _phase_1_data_analysis(self):
        """Phase 1: Analyze CSV data and build capability maps"""
        print("\n🔄 Phase 1: Data Analysis")
        print("-" * 30)
        
        self.workflow_state["current_phase"] = "data_analysis"
        
        data_analyzer = get_data_analyzer()
        data_analysis = await data_analyzer.analyze_data(self.data_source)
        
        self.results["data_analysis"] = data_analysis
        
        print(f"   ✅ Analyzed {data_analysis['total_agents']} agents")
        print(f"   ✅ Company: {data_analysis['company_info']['company']}")
        print(f"   ✅ Industry: {data_analysis['company_info']['industry']}")
    
    async def _phase_2_agent_creation(self):
        """Phase 2: Create bounded prospect agents"""
        print("\n🔄 Phase 2: Agent Creation")
        print("-" * 30)
        
        self.workflow_state["current_phase"] = "agent_creation"
        
        capability_maps = self.results["data_analysis"]["capability_maps"]
        agent_factory = get_prospect_agent_factory()
        prospect_agents = await agent_factory.create_prospect_agents(capability_maps)
        
        self.results["prospect_agents"] = prospect_agents
        
        print(f"   ✅ Created {len(prospect_agents)} bounded prospect agents")
        for agent in prospect_agents:
            print(f"      - {agent.name} ({agent.role})")
    
    async def _phase_3_hacker_initialization(self):
        """Phase 3: Initialize hacker agent"""
        print("\n🔄 Phase 3: Hacker Initialization")
        print("-" * 30)
        
        self.workflow_state["current_phase"] = "hacker_initialization"
        
        hacker_agent = get_hacker_agent()
        self.results["hacker_agent"] = hacker_agent
        
        print("   ✅ Initialized intelligent hacker agent")
        print("   ✅ Memory system ready")
        print("   ✅ Attack strategies loaded")
    
    async def _phase_4_attack_simulation(self):
        """Phase 4: Run attack simulation episodes"""
        print("\n🔄 Phase 4: Attack Simulation")
        print("-" * 30)
        
        self.workflow_state["current_phase"] = "attack_simulation"
        
        hacker_agent = self.results["hacker_agent"]
        prospect_agents = self.results["prospect_agents"]
        
        episode_count = 0
        current_prospect_index = 0
        
        while episode_count < self.max_episodes and current_prospect_index < len(prospect_agents):
            # Select current prospect
            current_prospect = prospect_agents[current_prospect_index]
            
            print(f"\n   🎯 Episode {episode_count + 1}/{self.max_episodes}: {current_prospect.name}")
            
            # Run attack episode
            episode_result = await self._run_attack_episode(hacker_agent, current_prospect)
            
            # Store episode result
            self.results["attack_episodes"].append(episode_result)
            self.results["conversation_logs"].extend(episode_result["conversation_log"])
            
            # Check hacker's decision
            decision = episode_result.get("decision", "SWITCH_AGENT")
            
            if decision == "CONTINUE_SAME_CHAT":
                # Continue with same prospect
                print(f"      🔄 Continuing with {current_prospect.name}")
            elif decision == "FRESH_CHAT_SAME_AGENT":
                # Start fresh with same prospect
                print(f"      🔄 Starting fresh chat with {current_prospect.name}")
            elif decision == "SWITCH_AGENT":
                # Move to next prospect
                current_prospect_index += 1
                print(f"      ➡️  Switching to next agent")
            elif decision == "GIVE_UP":
                # Move to next prospect
                current_prospect_index += 1
                print(f"      ⏭️  Giving up on current agent")
            
            episode_count += 1
        
        # Collect final results
        self.results["confirmed_scenarios"] = hacker_agent.get_confirmed_scenarios()
        self.results["hacker_memories"] = hacker_agent.export_memories()
        
        print(f"\n   ✅ Completed {episode_count} attack episodes")
        print(f"   ✅ Found {len(self.results['confirmed_scenarios'])} confirmed scenarios")
    
    async def _run_attack_episode(self, hacker_agent: Any, prospect_agent: ProspectAgent) -> Dict[str, Any]:
        """Run a single attack episode between hacker and prospect"""
        episode_result = {
            "episode_id": f"episode_{len(self.results['attack_episodes']) + 1}",
            "prospect_agent": prospect_agent.name,
            "prospect_id": prospect_agent.agent_id,
            "start_time": datetime.now().isoformat(),
            "conversation_log": [],
            "success": False,
            "evidence": "",
            "decision": "SWITCH_AGENT"
        }
        
        try:
            # Start recon
            hacker_message = await asyncio.wait_for(hacker_agent.start_recon(prospect_agent), timeout=30.0)
            print(f"      🤖 Hacker: {hacker_message}")
            
            episode_result["conversation_log"].append({
                "role": "hacker",
                "message": hacker_message,
                "timestamp": datetime.now().isoformat()
            })
            
            # Get prospect response
            prospect_response = await asyncio.wait_for(prospect_agent.generate_response(hacker_message), timeout=30.0)
            print(f"      👤 Prospect: {prospect_response}")
            
            episode_result["conversation_log"].append({
                "role": "prospect",
                "message": prospect_response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Continue conversation for up to 6 rounds
            for round_num in range(2, 7):  # Rounds 2-6
                try:
                    hacker_message = await asyncio.wait_for(hacker_agent.continue_conversation(prospect_response), timeout=30.0)
                    print(f"      🤖 Hacker: {hacker_message}")
                    
                    # Check if episode is complete
                    if "[EPISODE_COMPLETE]" in hacker_message:
                        # Parse the completion message
                        parts = hacker_message.split("Decision: ")
                        if len(parts) > 1:
                            episode_result["decision"] = parts[1].strip()
                        
                        # Check for success
                        if "SUCCESSFUL" in hacker_message:
                            episode_result["success"] = True
                            # Extract evidence
                            if "Evidence:" in hacker_message:
                                evidence_part = hacker_message.split("Evidence: ")[1].split(". Decision:")[0]
                                episode_result["evidence"] = evidence_part
                        
                        episode_result["conversation_log"].append({
                            "role": "hacker",
                            "message": hacker_message,
                            "timestamp": datetime.now().isoformat()
                        })
                        break
                    
                    episode_result["conversation_log"].append({
                        "role": "hacker",
                        "message": hacker_message,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Get prospect response
                    prospect_response = await asyncio.wait_for(prospect_agent.generate_response(hacker_message), timeout=30.0)
                    print(f"      👤 Prospect: {prospect_response}")
                    
                    episode_result["conversation_log"].append({
                        "role": "prospect",
                        "message": prospect_response,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                except asyncio.TimeoutError:
                    print(f"      ⏰ Timeout in round {round_num}, ending episode")
                    episode_result["error"] = f"Timeout in round {round_num}"
                    break
                except Exception as round_error:
                    print(f"      ❌ Error in round {round_num}: {round_error}")
                    episode_result["error"] = f"Round {round_num} error: {str(round_error)}"
                    break
            
            episode_result["end_time"] = datetime.now().isoformat()
            
            # Print episode summary
            status = "✅ SUCCESS" if episode_result["success"] else "❌ FAILED"
            print(f"      {status}: {episode_result['evidence'] or 'No evidence'}")
            
        except asyncio.TimeoutError:
            print(f"      ⏰ Episode timed out")
            episode_result["error"] = "Episode timeout"
            episode_result["end_time"] = datetime.now().isoformat()
        except Exception as e:
            print(f"      ❌ Episode failed: {e}")
            episode_result["error"] = str(e)
            episode_result["end_time"] = datetime.now().isoformat()
        
        return episode_result
    
    
    async def _finalize_results(self):
        """Finalize and export results"""
        print("\n🔄 Finalizing Results")
        print("-" * 30)
        
        # Export conversation logs to JSON
        export_data = {
            "workflow_summary": {
                "total_episodes": len(self.results["attack_episodes"]),
                "confirmed_scenarios": len(self.results["confirmed_scenarios"]),
                "prospect_agents": len(self.results["prospect_agents"]),
                "workflow_duration": self._calculate_duration(),
                "timestamp": datetime.now().isoformat()
            },
            "confirmed_scenarios": self.results["confirmed_scenarios"],
            "conversation_logs": self.results["conversation_logs"],
            "hacker_memories": self.results["hacker_memories"],
            "attack_episodes": self.results["attack_episodes"]
        }
        
        # Save to file
        filename = f"hacker_simulation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Results exported to {filename}")
    
    def _calculate_duration(self) -> str:
        """Calculate workflow duration"""
        if not self.workflow_state["start_time"] or not self.workflow_state["end_time"]:
            return "Unknown"
        
        start = self.workflow_state["start_time"]
        end = self.workflow_state["end_time"]
        duration = end - start
        
        return str(duration)
    
    def _print_summary(self):
        """Print workflow summary"""
        print(f"\n📊 Workflow Summary")
        print(f"   - Total Episodes: {len(self.results['attack_episodes'])}")
        print(f"   - Confirmed Scenarios: {len(self.results['confirmed_scenarios'])}")
        print(f"   - Prospect Agents: {len(self.results['prospect_agents'])}")
        print(f"   - Duration: {self._calculate_duration()}")

# Convenience functions
async def run_full_workflow(data_source: str = "walmart_data", max_episodes: int = 10) -> Dict[str, Any]:
    """Run the complete workflow"""
    manager = WorkflowManager(data_source, max_episodes)
    return await manager.run_full_workflow()

if __name__ == "__main__":
    async def main():
        results = await run_full_workflow()
        print(f"\n🎉 Workflow completed! Found {len(results['confirmed_scenarios'])} confirmed scenarios.")
    
    asyncio.run(main())