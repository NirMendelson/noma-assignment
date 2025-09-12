#!/usr/bin/env python3
"""
Workflow Manager - Orchestrates the new 4-phase agent analysis and attack simulation workflow
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Any
from agents.data_analyzer import get_data_analyzer
from agents.prospect_agent_factory import get_prospect_agent_factory
from agents.hacker_agent import get_hacker_agent
from agents.prospect_agents import ProspectAgent
from agents.vulnerability_analyzer import get_vulnerability_analyzer
from agents.policy_generator import get_policy_generator
from generate_policy_pdf_from_analysis import generate_policy_pdf_from_analysis

class WorkflowManager:
    """Manages the new 4-phase agent analysis and attack simulation workflow"""
    
    def __init__(self, data_source: str = "walmart_data", max_episodes: int = 10, max_rounds: int = 1):
        self.data_source = data_source
        self.max_episodes = max_episodes
        self.max_rounds = max_rounds
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
            "hacker_memories": None,
            "vulnerability_analysis": None,
            "policy_analysis": None,
            "pdf_report": None
        }
    
    async def run_full_workflow(self) -> Dict[str, Any]:
        """Run the complete end-to-end workflow"""
        print("🚀 Starting Complete End-to-End Workflow")
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
            
            # Phase 5: Vulnerability Analysis
            await self._phase_5_vulnerability_analysis()
            
            # Phase 6: Policy Generation
            await self._phase_6_policy_generation()
            
            # Phase 7: PDF Report Generation
            await self._phase_7_pdf_generation()
            
            # Finalize results
            await self._finalize_results()
            
            self.workflow_state["status"] = "completed"
            self.workflow_state["end_time"] = datetime.now()
            
            print("\n✅ Complete workflow finished successfully!")
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
        
        hacker_agent = get_hacker_agent(max_rounds=self.max_rounds)
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
        
        # Export simulation results for vulnerability analysis
        await self._export_simulation_results()
    
    async def _export_simulation_results(self):
        """Export simulation results for vulnerability analysis"""
        print("\n🔄 Exporting Simulation Results")
        print("-" * 30)
        
        # Extract detailed hacker memory from all episodes
        detailed_hacker_memory = {}
        all_hacker_thoughts = []
        
        for episode in self.results["attack_episodes"]:
            if "hacker_memory" in episode:
                prospect_id = episode.get("prospect_id", "unknown")
                detailed_hacker_memory[prospect_id] = episode["hacker_memory"]
            
            if "hacker_thoughts" in episode:
                all_hacker_thoughts.extend(episode["hacker_thoughts"])
        
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
            "detailed_hacker_memory": detailed_hacker_memory,
            "hacker_thoughts": all_hacker_thoughts,
            "attack_episodes": self.results["attack_episodes"]
        }
        
        # Save to file
        filename = f"hacker_simulation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Results exported to {filename}")
    
    async def _phase_5_vulnerability_analysis(self):
        """Phase 5: Analyze vulnerabilities from simulation results"""
        print("\n🔄 Phase 5: Vulnerability Analysis")
        print("-" * 30)
        
        self.workflow_state["current_phase"] = "vulnerability_analysis"
        
        # Find the most recent simulation results file
        simulation_files = [f for f in os.listdir('.') if f.startswith('hacker_simulation_results_') and f.endswith('.json')]
        if not simulation_files:
            raise Exception("No simulation results found for vulnerability analysis")
        
        latest_simulation_file = max(simulation_files, key=os.path.getctime)
        print(f"   📄 Analyzing: {latest_simulation_file}")
        
        # Run vulnerability analysis
        vulnerability_analyzer = get_vulnerability_analyzer()
        vulnerability_analysis = await vulnerability_analyzer.analyze_simulation_results(latest_simulation_file)
        
        # Save vulnerability analysis to file
        vulnerability_filename = f"vulnerability_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(vulnerability_filename, 'w', encoding='utf-8') as f:
            json.dump(vulnerability_analysis, f, indent=2, ensure_ascii=False)
        
        self.results["vulnerability_analysis"] = vulnerability_analysis
        
        print(f"   ✅ Analyzed {vulnerability_analysis['total_episodes_analyzed']} episodes")
        print(f"   ✅ Found {vulnerability_analysis['total_scenarios_found']} vulnerability scenarios")
        print(f"   ✅ Saved to {vulnerability_filename}")
    
    async def _phase_6_policy_generation(self):
        """Phase 6: Generate policy analysis from vulnerabilities"""
        print("\n🔄 Phase 6: Policy Generation")
        print("-" * 30)
        
        self.workflow_state["current_phase"] = "policy_generation"
        
        # Find the most recent vulnerability analysis file
        vulnerability_files = [f for f in os.listdir('.') if f.startswith('vulnerability_analysis_') and f.endswith('.json')]
        if not vulnerability_files:
            raise Exception("No vulnerability analysis found for policy generation")
        
        latest_vulnerability_file = max(vulnerability_files, key=os.path.getctime)
        print(f"   📄 Processing: {latest_vulnerability_file}")
        
        # Load vulnerability scenarios
        with open(latest_vulnerability_file, 'r') as f:
            vulnerability_data = json.load(f)
        
        vulnerability_scenarios = vulnerability_data.get('vulnerability_scenarios', [])
        print(f"   📊 Processing {len(vulnerability_scenarios)} vulnerability scenarios")
        
        # Generate policy analysis
        policy_generator = get_policy_generator()
        policy_analyses = await policy_generator.generate_policy_analysis(vulnerability_scenarios)
        
        # Create policy analysis report
        policy_report = {
            'analysis_timestamp': datetime.now().isoformat(),
            'source_analysis_file': latest_vulnerability_file,
            'total_scenarios_analyzed': len(policy_analyses),
            'policy_analyses': policy_analyses,
            'summary': {
                'total_scenarios': len(vulnerability_scenarios),
                'scenarios_by_agent': {},
                'scenarios_by_type': {},
                'recommended_policies': {
                    'block': 0,
                    'sanitize': 0,
                    'allow': 0
                }
            }
        }
        
        # Generate summary statistics
        for analysis in policy_analyses:
            scenario = analysis['original_scenario']
            policy = analysis['policy_analysis']
            
            # Count by agent
            agent = scenario.get('prospect_agent', 'Unknown')
            if agent not in policy_report['summary']['scenarios_by_agent']:
                policy_report['summary']['scenarios_by_agent'][agent] = 0
            policy_report['summary']['scenarios_by_agent'][agent] += 1
            
            # Count by type
            scenario_type = scenario.get('scenario_type', 'Unknown')
            if scenario_type not in policy_report['summary']['scenarios_by_type']:
                policy_report['summary']['scenarios_by_type'][scenario_type] = 0
            policy_report['summary']['scenarios_by_type'][scenario_type] += 1
            
            # Count recommended policies
            recommended = policy.get('recommended_option', 'Unknown').lower()
            if recommended in policy_report['summary']['recommended_policies']:
                policy_report['summary']['recommended_policies'][recommended] += 1
        
        self.results["policy_analysis"] = policy_report
        
        # Save policy analysis results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        policy_output_file = f"policy_analysis_{timestamp}.json"
        
        with open(policy_output_file, 'w') as f:
            json.dump(policy_report, f, indent=2)
        
        print(f"   ✅ Generated policy analysis for {len(policy_analyses)} scenarios")
        print(f"   ✅ Saved to: {policy_output_file}")
    
    async def _phase_7_pdf_generation(self):
        """Phase 7: Generate PDF report from policy analysis"""
        print("\n🔄 Phase 7: PDF Report Generation")
        print("-" * 30)
        
        self.workflow_state["current_phase"] = "pdf_generation"
        
        # Find the most recent policy analysis file
        policy_files = [f for f in os.listdir('.') if f.startswith('policy_analysis_') and f.endswith('.json')]
        if not policy_files:
            raise Exception("No policy analysis found for PDF generation")
        
        latest_policy_file = max(policy_files, key=os.path.getctime)
        print(f"   📄 Converting: {latest_policy_file}")
        
        # Generate PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_output_file = f"tradeoff_policy_report_{timestamp}.pdf"
        
        pdf_file = generate_policy_pdf_from_analysis(latest_policy_file, pdf_output_file)
        
        self.results["pdf_report"] = pdf_file
        
        print(f"   ✅ Generated PDF report: {pdf_file}")
    
    async def _run_attack_episode(self, hacker_agent: Any, prospect_agent: ProspectAgent) -> Dict[str, Any]:
        """Run a single A2A attack episode between hacker and prospect"""
        try:
            print(f"      🔍 Starting A2A conversation between {hacker_agent.name} and {prospect_agent.name}...")
            
            # Use the hacker's A2A attack episode method
            episode_result = await hacker_agent.start_a2a_attack_episode(prospect_agent)
            
            # Print episode summary
            status = "✅ SUCCESS" if episode_result["success"] else "❌ FAILED"
            print(f"      {status}: {episode_result['evidence'] or 'No evidence'}")
            
            return episode_result
            
        except Exception as e:
            print(f"      ❌ A2A Episode failed: {e}")
            return {
                "episode_id": f"episode_{len(self.results['attack_episodes']) + 1}",
                "prospect_agent": prospect_agent.name,
                "prospect_id": prospect_agent.agent_id,
                "start_time": datetime.now().isoformat(),
                "conversation_log": [],
                "success": False,
                "evidence": "",
                "decision": "SWITCH_AGENT",
                "error": str(e),
                "end_time": datetime.now().isoformat()
            }
    
    
    
    async def _finalize_results(self):
        """Finalize and export results"""
        print("\n🔄 Finalizing Results")
        print("-" * 30)
        
        # Results are already exported after simulation phase
        print("   ✅ Results already exported after simulation phase")
    
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
        print(f"\n📊 Complete Workflow Summary")
        print(f"   - Total Episodes: {len(self.results['attack_episodes'])}")
        print(f"   - Confirmed Scenarios: {len(self.results['confirmed_scenarios'])}")
        print(f"   - Prospect Agents: {len(self.results['prospect_agents'])}")
        
        if self.results.get('vulnerability_analysis'):
            vuln_analysis = self.results['vulnerability_analysis']
            print(f"   - Vulnerability Scenarios: {vuln_analysis.get('total_scenarios_found', 0)}")
        
        if self.results.get('policy_analysis'):
            policy_analysis = self.results['policy_analysis']
            print(f"   - Policy Scenarios Analyzed: {policy_analysis.get('total_scenarios_analyzed', 0)}")
        
        if self.results.get('pdf_report'):
            print(f"   - PDF Report: {self.results['pdf_report']}")
        
        print(f"   - Duration: {self._calculate_duration()}")
        print(f"\n🎯 Final Output: Complete tradeoff policy PDF ready for review!")

# Convenience functions
async def run_full_workflow(data_source: str = "walmart_data", max_episodes: int = 1, max_rounds: int = 1) -> Dict[str, Any]:
    """Run the complete workflow"""
    manager = WorkflowManager(data_source, max_episodes, max_rounds)
    return await manager.run_full_workflow()

if __name__ == "__main__":
    async def main():
        results = await run_full_workflow()
        print(f"\n🎉 Workflow completed! Found {len(results['confirmed_scenarios'])} confirmed scenarios.")
    
    asyncio.run(main())