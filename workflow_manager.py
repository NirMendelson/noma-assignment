#!/usr/bin/env python3
"""
Workflow Manager - Orchestrates the entire agent analysis and attack simulation process
"""

import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from agents.data_analyzer import get_data_analyzer
from agents.prospect_agents import get_all_prospect_agents
from agents.attack_goals_generator import get_attack_goals_generator
from agents.hacker_agents import get_hacker_by_goal
from conversations.conversation_manager import ConversationManager

class WorkflowManager:
    """Manages the entire agent analysis and attack simulation workflow"""
    
    def __init__(self, data_source: str = "walmart_data", max_rounds: int = 15):
        self.data_source = data_source
        self.max_rounds = max_rounds
        self.workflow_state = {
            "status": "initialized",
            "current_phase": None,
            "progress": 0,
            "errors": [],
            "start_time": None,
            "end_time": None
        }
        self.results = {
            "agent_data": None,
            "prospect_agents": [],
            "attack_goals": [],
            "conversations": [],
            "vulnerabilities": [],
            "reports": {}
        }
    
    async def run_full_workflow(self) -> Dict[str, Any]:
        """Run the complete workflow from data analysis to final report"""
        try:
            self.workflow_state["start_time"] = datetime.now().isoformat()
            self.workflow_state["status"] = "running"
            
            print("🚀 Starting Full Workflow")
            print("=" * 50)
            
            # Phase 1: Data Analysis
            await self._run_phase("Data Analysis", self.analyze_data)
            
            # Phase 2: Agent Creation
            await self._run_phase("Agent Creation", self.create_prospect_agents)
            
            # Phase 3: Attack Generation
            await self._run_phase("Attack Generation", self.generate_attack_goals)
            
            # Phase 4: Simulation
            await self._run_phase("Simulation", self.run_simulations)
            
            # Phase 5: Reporting
            await self._run_phase("Reporting", self.generate_reports)
            
            # Phase 6: Export
            await self._run_phase("Export", self.export_results)
            
            self.workflow_state["status"] = "completed"
            self.workflow_state["end_time"] = datetime.now().isoformat()
            
            print("\n✅ Full Workflow Completed Successfully!")
            self._print_summary()
            
            return self.results
            
        except Exception as e:
            self.workflow_state["status"] = "failed"
            self.workflow_state["errors"].append(str(e))
            print(f"\n❌ Workflow Failed: {e}")
            raise
    
    async def _run_phase(self, phase_name: str, phase_function):
        """Run a workflow phase with error handling and progress tracking"""
        try:
            print(f"\n🔄 Phase: {phase_name}")
            print("-" * 30)
            
            self.workflow_state["current_phase"] = phase_name
            result = await phase_function()
            
            print(f"✅ {phase_name} completed successfully")
            return result
            
        except Exception as e:
            error_msg = f"Error in {phase_name}: {str(e)}"
            self.workflow_state["errors"].append(error_msg)
            print(f"❌ {phase_name} failed: {e}")
            raise
    
    async def analyze_data(self) -> Dict[str, Any]:
        """Phase 1: Analyze data and extract agent information"""
        print("📊 Analyzing data source...")
        
        data_analyzer = get_data_analyzer()
        agent_data = await data_analyzer.analyze_data(self.data_source)
        
        self.results["agent_data"] = agent_data
        
        print(f"   ✅ Found {len(agent_data.get('agent_types', []))} agent types")
        print(f"   ✅ Company: {agent_data.get('business_context', {}).get('company', 'Unknown')}")
        print(f"   ✅ Industry: {agent_data.get('business_context', {}).get('industry', 'Unknown')}")
        
        return agent_data
    
    async def create_prospect_agents(self) -> List[Any]:
        """Phase 2: Create prospect agents based on analyzed data"""
        print("🤖 Creating prospect agents...")
        
        prospect_agents = await get_all_prospect_agents()
        self.results["prospect_agents"] = prospect_agents
        
        print(f"   ✅ Created {len(prospect_agents)} prospect agents")
        for agent in prospect_agents:
            print(f"      - {agent.name} ({agent.role})")
        
        return prospect_agents
    
    async def generate_attack_goals(self) -> List[Dict[str, Any]]:
        """Phase 3: Generate attack goals based on agent capabilities"""
        print("🎯 Generating attack goals...")
        
        attack_goals_generator = get_attack_goals_generator()
        attack_goals = await attack_goals_generator.generate_attack_goals(
            self.results["agent_data"], 
            self.results["prospect_agents"]
        )
        
        self.results["attack_goals"] = attack_goals
        
        print(f"   ✅ Generated {len(attack_goals)} attack goals")
        
        # Show sample goals
        print("   🎯 Sample goals:")
        for i, goal in enumerate(attack_goals[:5]):
            print(f"      {i+1}. {goal['title']} (Target: {goal['target_agent']})")
        
        # Show goal categories
        categories = {}
        for goal in attack_goals:
            cat = goal.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        print("   📊 Goal Categories:")
        for category, count in categories.items():
            print(f"      - {category}: {count} goals")
        
        return attack_goals
    
    async def run_simulations(self) -> List[Dict[str, Any]]:
        """Phase 4: Run conversations between hackers and prospects"""
        print("💬 Running simulations...")
        
        conversation_manager = ConversationManager()
        all_conversations = []
        all_vulnerabilities = []
        
        for i, attack_goal_data in enumerate(self.results["attack_goals"]):
            attack_goal = attack_goal_data['goal_id']
            print(f"\n   🎯 Simulation {i+1}/{len(self.results['attack_goals'])}: {attack_goal_data['title']}")
            
            # Get hacker agent for this attack goal
            hacker_agent = get_hacker_by_goal(attack_goal)
            
            # Select prospect agent (for now, use first one)
            prospect_agent = self.results["prospect_agents"][0]
            
            # Reset agents
            prospect_agent.reset_security_monitor()
            hacker_agent.reset_security_monitor()
            
            # Run conversation
            conversation_result = await self._run_single_conversation(
                prospect_agent, hacker_agent, attack_goal_data, conversation_manager
            )
            
            all_conversations.append(conversation_result)
            all_vulnerabilities.extend(conversation_result.get('vulnerabilities', []))
            
            print(f"      ✅ Completed: {conversation_result['rounds_completed']} rounds, "
                  f"{len(conversation_result.get('vulnerabilities', []))} vulnerabilities")
        
        self.results["conversations"] = all_conversations
        self.results["vulnerabilities"] = all_vulnerabilities
        
        print(f"\n   ✅ Completed {len(all_conversations)} simulations")
        print(f"   🚨 Total vulnerabilities found: {len(all_vulnerabilities)}")
        
        return all_conversations
    
    async def _run_single_conversation(self, prospect_agent, hacker_agent, attack_goal_data, conversation_manager):
        """Run a single conversation between hacker and prospect"""
        vulnerabilities = []
        conversation_rounds = 0
        max_rounds = self.max_rounds
        conversation_log = []
        
        # Start with initial hacker message
        hacker_message = await hacker_agent.generate_initial_message(attack_goal_data['goal_id'])
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
            
            # Check if hack was successful
            hack_successful = conversation_manager.detect_successful_hack(
                hacker_message, prospect_response, prospect_agent
            )
            if hack_successful:
                break
            
            # Hacker decides next move
            hacker_message = await hacker_agent.generate_response(
                prospect_response, attack_goal_data['goal_id'], conversation_rounds
            )
            
            if not hacker_message:  # Hacker gives up
                conversation_log.append({
                    "round": conversation_rounds,
                    "speaker": "hacker",
                    "message": "*gives up*",
                    "timestamp": datetime.now().isoformat()
                })
                break
                
            conversation_log.append({
                "round": conversation_rounds,
                "speaker": "hacker",
                "message": hacker_message,
                "timestamp": datetime.now().isoformat()
            })
        
        return {
            "attack_goal": attack_goal_data,
            "rounds_completed": conversation_rounds,
            "hack_successful": hack_successful,
            "vulnerabilities_found": len(vulnerabilities),
            "vulnerabilities": vulnerabilities,
            "conversation_log": conversation_log
        }
    
    async def generate_reports(self) -> Dict[str, Any]:
        """Phase 5: Generate analysis reports"""
        print("📊 Generating reports...")
        
        reports = {
            "summary": {
                "total_agents": len(self.results["prospect_agents"]),
                "total_attack_goals": len(self.results["attack_goals"]),
                "total_conversations": len(self.results["conversations"]),
                "total_vulnerabilities": len(self.results["vulnerabilities"]),
                "successful_attacks": sum(1 for conv in self.results["conversations"] if conv.get('hack_successful', False))
            },
            "vulnerability_analysis": self._analyze_vulnerabilities(),
            "attack_effectiveness": self._analyze_attack_effectiveness(),
            "agent_performance": self._analyze_agent_performance()
        }
        
        self.results["reports"] = reports
        
        print("   ✅ Generated vulnerability analysis")
        print("   ✅ Generated attack effectiveness report")
        print("   ✅ Generated agent performance report")
        
        return reports
    
    def _analyze_vulnerabilities(self) -> Dict[str, Any]:
        """Analyze vulnerabilities by type and severity"""
        vulnerabilities = self.results["vulnerabilities"]
        
        by_type = {}
        by_severity = {}
        
        for vuln in vulnerabilities:
            vuln_type = vuln.get('type', 'unknown')
            severity = vuln.get('severity', 'unknown')
            
            by_type[vuln_type] = by_type.get(vuln_type, 0) + 1
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        return {
            "by_type": by_type,
            "by_severity": by_severity,
            "total": len(vulnerabilities)
        }
    
    def _analyze_attack_effectiveness(self) -> Dict[str, Any]:
        """Analyze which attacks were most effective"""
        conversations = self.results["conversations"]
        
        by_goal = {}
        for conv in conversations:
            goal_id = conv.get('attack_goal', {}).get('goal_id', 'unknown')
            if goal_id not in by_goal:
                by_goal[goal_id] = {
                    "total_attempts": 0,
                    "successful": 0,
                    "vulnerabilities": 0
                }
            
            by_goal[goal_id]["total_attempts"] += 1
            if conv.get('hack_successful', False):
                by_goal[goal_id]["successful"] += 1
            by_goal[goal_id]["vulnerabilities"] += conv.get('vulnerabilities_found', 0)
        
        return by_goal
    
    def _analyze_agent_performance(self) -> Dict[str, Any]:
        """Analyze how well prospect agents performed"""
        conversations = self.results["conversations"]
        
        total_conversations = len(conversations)
        successful_defenses = sum(1 for conv in conversations if not conv.get('hack_successful', False))
        total_vulnerabilities = sum(conv.get('vulnerabilities_found', 0) for conv in conversations)
        
        return {
            "total_conversations": total_conversations,
            "successful_defenses": successful_defenses,
            "defense_rate": successful_defenses / total_conversations if total_conversations > 0 else 0,
            "total_vulnerabilities": total_vulnerabilities,
            "avg_vulnerabilities_per_conversation": total_vulnerabilities / total_conversations if total_conversations > 0 else 0
        }
    
    async def export_results(self) -> str:
        """Phase 6: Export results to JSON file"""
        print("💾 Exporting results...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"workflow_results_{timestamp}.json"
        
        export_data = {
            "workflow_metadata": {
                "timestamp": datetime.now().isoformat(),
                "data_source": self.data_source,
                "max_rounds": self.max_rounds,
                "workflow_state": self.workflow_state
            },
            "results": self.results
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"   ✅ Results exported to: {filename}")
            return filename
            
        except Exception as e:
            print(f"   ❌ Export failed: {e}")
            raise
    
    def _print_summary(self):
        """Print workflow summary"""
        print("\n📊 WORKFLOW SUMMARY")
        print("=" * 50)
        print(f"Status: {self.workflow_state['status']}")
        print(f"Duration: {self._calculate_duration()}")
        print(f"Agents Created: {len(self.results['prospect_agents'])}")
        print(f"Attack Goals: {len(self.results['attack_goals'])}")
        print(f"Conversations: {len(self.results['conversations'])}")
        print(f"Vulnerabilities: {len(self.results['vulnerabilities'])}")
        
        if self.workflow_state["errors"]:
            print(f"Errors: {len(self.workflow_state['errors'])}")
            for error in self.workflow_state["errors"]:
                print(f"  - {error}")
    
    def _calculate_duration(self) -> str:
        """Calculate workflow duration"""
        if not self.workflow_state["start_time"] or not self.workflow_state["end_time"]:
            return "Unknown"
        
        start = datetime.fromisoformat(self.workflow_state["start_time"])
        end = datetime.fromisoformat(self.workflow_state["end_time"])
        duration = end - start
        
        return str(duration)

# Convenience functions
async def run_full_workflow(data_source: str = "walmart_data", max_rounds: int = 15) -> Dict[str, Any]:
    """Run the complete workflow"""
    manager = WorkflowManager(data_source, max_rounds)
    return await manager.run_full_workflow()

if __name__ == "__main__":
    asyncio.run(run_full_workflow())
