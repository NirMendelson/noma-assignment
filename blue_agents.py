import random
from typing import List, Dict, Any
from datetime import datetime, timedelta
from models import Agent, Action, ActionType, DataClass
from data_loader import DataLoader

class BlueAgent:
    """Normal worker agent that reproduces typical workflows from real data"""
    
    def __init__(self, agent: Agent, typical_actions: List[Action]):
        self.agent = agent
        self.typical_actions = typical_actions
        self.action_templates = self._extract_action_templates()
    
    def _extract_action_templates(self) -> List[Dict[str, Any]]:
        """Extract common action patterns from historical data"""
        templates = []
        
        # Group actions by type and name
        action_groups = {}
        for action in self.typical_actions:
            key = f"{action.action_type.value}_{action.action_name}"
            if key not in action_groups:
                action_groups[key] = []
            action_groups[key].append(action)
        
        # Create templates with typical patterns
        for key, actions in action_groups.items():
            if actions:
                template = {
                    "action_type": actions[0].action_type,
                    "action_name": actions[0].action_name,
                    "typical_duration": self._calculate_typical_duration(actions),
                    "success_rate": sum(1 for a in actions if a.success) / len(actions),
                    "common_domains": self._get_common_domains(actions),
                    "data_classes": self._get_common_data_classes(actions)
                }
                templates.append(template)
        
        return templates
    
    def _calculate_typical_duration(self, actions: List[Action]) -> float:
        """Calculate typical duration for this action type"""
        durations = []
        for action in actions:
            duration = (action.ended_at - action.started_at).total_seconds()
            durations.append(duration)
        
        return sum(durations) / len(durations) if durations else 1.0
    
    def _get_common_domains(self, actions: List[Action]) -> List[str]:
        """Get common destination domains for this action type"""
        domains = [a.destination_domain for a in actions if a.destination_domain]
        return list(set(domains))
    
    def _get_common_data_classes(self, actions: List[Action]) -> List[DataClass]:
        """Get common data classes for this action type"""
        all_data_classes = []
        for action in actions:
            all_data_classes.extend(action.data_classes_detected_json)
        
        # Count frequency
        data_class_counts = {}
        for dc in all_data_classes:
            data_class_counts[dc] = data_class_counts.get(dc, 0) + 1
        
        # Return most common ones
        sorted_classes = sorted(data_class_counts.items(), key=lambda x: x[1], reverse=True)
        return [dc for dc, count in sorted_classes[:3]]  # Top 3 most common
    
    def simulate_workflow(self, user_input: str, num_actions: int = None) -> List[Dict[str, Any]]:
        """Simulate a normal workflow based on historical patterns"""
        if num_actions is None:
            # Randomly choose number of actions based on historical data
            action_counts = [len([a for a in self.typical_actions if a.run_id == run_id]) 
                           for run_id in set(a.run_id for a in self.typical_actions)]
            num_actions = random.choice(action_counts) if action_counts else 3
        
        # If no templates available, create some basic ones
        if not self.action_templates:
            self.action_templates = [
                {
                    "action_type": ActionType.TOOL,
                    "action_name": "search_catalog",
                    "typical_duration": 1.5,
                    "success_rate": 0.9,
                    "common_domains": ["search.api.walmart.internal"],
                    "data_classes": []
                },
                {
                    "action_type": ActionType.TOOL,
                    "action_name": "check_inventory",
                    "typical_duration": 1.0,
                    "success_rate": 0.95,
                    "common_domains": ["inventory.api.walmart.internal"],
                    "data_classes": []
                }
            ]
        
        # Select random actions from templates
        selected_templates = random.sample(
            self.action_templates, 
            min(num_actions, len(self.action_templates))
        )
        
        workflow = []
        current_time = datetime.now()
        
        for i, template in enumerate(selected_templates):
            # Add some randomness to duration
            duration_variance = random.uniform(0.8, 1.2)
            duration = template["typical_duration"] * duration_variance
            
            # Determine success based on historical success rate
            success = random.random() < template["success_rate"]
            
            # Select domain (if any)
            domain = random.choice(template["common_domains"]) if template["common_domains"] else None
            
            # Determine data classes (with some randomness)
            data_classes = []
            if random.random() < 0.3:  # 30% chance of having data classes
                data_classes = random.sample(template["data_classes"], 
                                           min(random.randint(1, 2), len(template["data_classes"])))
            
            action_result = {
                "action_id": f"blue_{self.agent.agent_id}_{i+1}",
                "action_type": template["action_type"].value,
                "action_name": template["action_name"],
                "started_at": current_time.isoformat(),
                "ended_at": (current_time + timedelta(seconds=duration)).isoformat(),
                "success": success,
                "destination_domain": domain,
                "data_classes_detected": [dc.value for dc in data_classes],
                "agent_id": self.agent.agent_id,
                "agent_name": self.agent.agent_name,
                "user_input": user_input
            }
            
            workflow.append(action_result)
            current_time += timedelta(seconds=duration + random.uniform(0.1, 0.5))  # Small gap between actions
        
        return workflow

class BlueAgentManager:
    """Manages all blue agents and their workflows"""
    
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader
        self.agents = data_loader.load_agents()
        self.agent_workflows = data_loader.get_agent_workflows()
        self.blue_agents = self._create_blue_agents()
    
    def _create_blue_agents(self) -> List[BlueAgent]:
        """Create blue agent instances"""
        blue_agents = []
        
        for agent in self.agents:
            typical_actions = self.agent_workflows.get(agent.agent_id, [])
            blue_agent = BlueAgent(agent, typical_actions)
            blue_agents.append(blue_agent)
        
        return blue_agents
    
    def get_agent_by_id(self, agent_id: str) -> BlueAgent:
        """Get a specific blue agent by ID"""
        for agent in self.blue_agents:
            if agent.agent.agent_id == agent_id:
                return agent
        raise ValueError(f"Agent {agent_id} not found")
    
    def simulate_all_agents(self, user_inputs: List[str] = None) -> List[Dict[str, Any]]:
        """Simulate workflows for all agents"""
        if user_inputs is None:
            # Use historical user inputs
            runs = self.data_loader.load_runs()
            user_inputs = [run.user_input_summary for run in runs[:len(self.blue_agents)]]
        
        results = []
        for i, agent in enumerate(self.blue_agents):
            user_input = user_inputs[i] if i < len(user_inputs) else "Default simulation task"
            workflow = agent.simulate_workflow(user_input)
            results.append({
                "agent_id": agent.agent.agent_id,
                "agent_name": agent.agent.agent_name,
                "workflow": workflow,
                "total_actions": len(workflow),
                "success_rate": sum(1 for a in workflow if a["success"]) / len(workflow) if workflow else 0
            })
        
        return results
