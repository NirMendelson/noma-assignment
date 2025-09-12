#!/usr/bin/env python3
"""
Workflow Episodes - Handles attack episode execution and management
"""

from datetime import datetime
from typing import Dict, List, Any
from agents.prospect.prospect_agents import ProspectAgent

class WorkflowEpisodes:
    """Handles attack episode execution and management"""
    
    def __init__(self, workflow_manager):
        self.workflow = workflow_manager
    
    async def run_attack_episode(self, hacker_agent: Any, prospect_agent: ProspectAgent) -> Dict[str, Any]:
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
                "episode_id": f"episode_{len(self.workflow.results['attack_episodes']) + 1}",
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
