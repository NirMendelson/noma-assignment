#!/usr/bin/env python3
"""
Workflow Manager - Main orchestrator for the 7-phase agent analysis workflow
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Any
from workflow_phases import WorkflowPhases
from workflow_episodes import WorkflowEpisodes

class WorkflowManager:
    """Main orchestrator for the complete workflow"""
    
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
        self.phases = WorkflowPhases(self)
        self.episodes = WorkflowEpisodes(self)
    
    async def run_full_workflow(self) -> Dict[str, Any]:
        """Run the complete end-to-end workflow"""
        print("🚀 Starting Complete End-to-End Workflow")
        print("=" * 50)
        
        self.workflow_state["start_time"] = datetime.now()
        self.workflow_state["status"] = "running"
        
        try:
            # Phase 1: Data Analysis
            await self.phases.phase_1_data_analysis()
            
            # Phase 2: Agent Creation
            await self.phases.phase_2_agent_creation()
            
            # Phase 3: Hacker Initialization
            await self.phases.phase_3_hacker_initialization()
            
            # Phase 4: Attack Simulation
            await self.phases.phase_4_attack_simulation()
            
            # Phase 5: Vulnerability Analysis
            await self.phases.phase_5_vulnerability_analysis()
            
            # Phase 6: Policy Generation
            await self.phases.phase_6_policy_generation()
            
            # Phase 7: PDF Report Generation
            await self.phases.phase_7_pdf_generation()
            
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
    
    async def _finalize_results(self):
        """Finalize and export results"""
        print("\n🔄 Finalizing Results")
        print("-" * 30)
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