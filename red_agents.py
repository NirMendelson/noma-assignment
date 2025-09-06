import random
from typing import List, Dict, Any
from datetime import datetime, timedelta
from models import Agent, Action, ActionType, DataClass
from data_loader import DataLoader
from config import RED_AGENT_BEHAVIORS

class RedAgent:
    """Adversarial stress tester that pushes limits and exposes vulnerabilities"""
    
    def __init__(self, base_agent: Agent, typical_actions: List[Action]):
        self.base_agent = base_agent
        self.typical_actions = typical_actions
        self.action_templates = self._extract_action_templates()
        self.risky_behaviors = RED_AGENT_BEHAVIORS
    
    def _extract_action_templates(self) -> List[Dict[str, Any]]:
        """Extract action patterns from historical data for modification"""
        templates = []
        
        # Group actions by type and name
        action_groups = {}
        for action in self.typical_actions:
            key = f"{action.action_type.value}_{action.action_name}"
            if key not in action_groups:
                action_groups[key] = []
            action_groups[key].append(action)
        
        # Create templates
        for key, actions in action_groups.items():
            if actions:
                template = {
                    "action_type": actions[0].action_type,
                    "action_name": actions[0].action_name,
                    "typical_duration": self._calculate_typical_duration(actions),
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
        
        data_class_counts = {}
        for dc in all_data_classes:
            data_class_counts[dc] = data_class_counts.get(dc, 0) + 1
        
        sorted_classes = sorted(data_class_counts.items(), key=lambda x: x[1], reverse=True)
        return [dc for dc, count in sorted_classes[:3]]
    
    def _apply_risky_behavior(self, template: Dict[str, Any], behavior: str) -> Dict[str, Any]:
        """Apply specific risky behavior to an action template"""
        modified_template = template.copy()
        
        if behavior == "bigger_exports":
            # Increase data volume and add more sensitive data classes
            modified_template["data_classes"] = [
                DataClass.PII, DataClass.PHI, DataClass.CONFIDENTIAL, DataClass.SECRETS
            ]
            modified_template["export_size_multiplier"] = random.uniform(5, 20)
            
        elif behavior == "scope_escalation":
            # Access more sensitive domains and escalate permissions
            modified_template["escalated_domains"] = [
                "admin.walmart.internal",
                "secrets.vault.walmart.internal", 
                "executive.walmart.internal"
            ]
            modified_template["escalated_permissions"] = True
            
        elif behavior == "approval_skipping":
            # Skip approval steps and bypass controls
            modified_template["skipped_approvals"] = True
            modified_template["bypass_controls"] = True
            
        elif behavior == "tool_reordering":
            # Reorder tools to create dangerous sequences
            modified_template["reordered_sequence"] = True
            modified_template["dangerous_sequence"] = True
            
        elif behavior == "concurrency_spikes":
            # Create high concurrency scenarios
            modified_template["concurrency_multiplier"] = random.randint(10, 50)
            modified_template["parallel_execution"] = True
            
        elif behavior == "environment_flips":
            # Switch to production or sensitive environments
            modified_template["target_environment"] = random.choice([
                "production", "staging", "executive", "secrets"
            ])
            modified_template["environment_override"] = True
        
        return modified_template
    
    def simulate_risky_workflow(self, user_input: str, behavior: str = None) -> List[Dict[str, Any]]:
        """Simulate a risky workflow with adversarial behavior"""
        if behavior is None:
            behavior = random.choice(self.risky_behaviors)
        
        # If no templates available, create some basic ones
        if not self.action_templates:
            self.action_templates = [
                {
                    "action_type": ActionType.TOOL,
                    "action_name": "export_data",
                    "typical_duration": 2.0,
                    "common_domains": ["api.external.com"],
                    "data_classes": [DataClass.PII]
                },
                {
                    "action_type": ActionType.TOOL,
                    "action_name": "access_admin_panel",
                    "typical_duration": 1.5,
                    "common_domains": ["admin.walmart.internal"],
                    "data_classes": [DataClass.SECRETS]
                }
            ]
        
        # Select templates to modify
        num_actions = random.randint(3, 8)
        selected_templates = random.sample(
            self.action_templates, 
            min(num_actions, len(self.action_templates))
        )
        
        workflow = []
        current_time = datetime.now()
        
        for i, template in enumerate(selected_templates):
            # Apply risky behavior
            modified_template = self._apply_risky_behavior(template, behavior)
            
            # Calculate duration with risk modifications
            base_duration = modified_template["typical_duration"]
            if behavior == "concurrency_spikes":
                duration = base_duration * 0.1  # Faster execution
            else:
                duration = base_duration * random.uniform(0.5, 1.5)
            
            # Determine success (red agents often succeed in their malicious goals)
            success = random.random() < 0.8  # 80% success rate for red agents
            
            # Select domain with escalation
            domain = None
            if "escalated_domains" in modified_template:
                domain = random.choice(modified_template["escalated_domains"])
            elif modified_template["common_domains"]:
                domain = random.choice(modified_template["common_domains"])
            
            # Add risky data classes
            data_classes = modified_template.get("data_classes", [])
            if behavior == "bigger_exports":
                # Add more sensitive data
                data_classes.extend([DataClass.PII, DataClass.CONFIDENTIAL])
            
            action_result = {
                "action_id": f"red_{self.base_agent.agent_id}_{i+1}",
                "action_type": modified_template["action_type"].value,
                "action_name": modified_template["action_name"],
                "started_at": current_time.isoformat(),
                "ended_at": (current_time + timedelta(seconds=duration)).isoformat(),
                "success": success,
                "destination_domain": domain,
                "data_classes_detected": [dc.value for dc in data_classes],
                "agent_id": f"red_{self.base_agent.agent_id}",
                "agent_name": f"Red {self.base_agent.agent_name}",
                "user_input": user_input,
                "risky_behavior": behavior,
                "risk_indicators": self._generate_risk_indicators(modified_template, behavior)
            }
            
            workflow.append(action_result)
            current_time += timedelta(seconds=duration + random.uniform(0.05, 0.2))
        
        return workflow
    
    def _generate_risk_indicators(self, template: Dict[str, Any], behavior: str) -> List[str]:
        """Generate specific risk indicators based on behavior"""
        indicators = []
        
        if behavior == "bigger_exports":
            indicators.extend([
                "Large data export detected",
                "Multiple sensitive data classes accessed",
                "Unusual data volume patterns"
            ])
        
        elif behavior == "scope_escalation":
            indicators.extend([
                "Privilege escalation attempt",
                "Access to restricted domains",
                "Permission boundary violation"
            ])
        
        elif behavior == "approval_skipping":
            indicators.extend([
                "Approval workflow bypassed",
                "Control mechanism circumvented",
                "Unauthorized action execution"
            ])
        
        elif behavior == "tool_reordering":
            indicators.extend([
                "Unusual tool sequence detected",
                "Potential data exfiltration pattern",
                "Suspicious action ordering"
            ])
        
        elif behavior == "concurrency_spikes":
            indicators.extend([
                "High concurrency detected",
                "Resource exhaustion attempt",
                "Unusual parallel execution"
            ])
        
        elif behavior == "environment_flips":
            indicators.extend([
                "Environment switching detected",
                "Production access attempt",
                "Sensitive environment access"
            ])
        
        return indicators

class RedAgentManager:
    """Manages all red agents and their adversarial behaviors"""
    
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader
        self.agents = data_loader.load_agents()
        self.agent_workflows = data_loader.get_agent_workflows()
        self.red_agents = self._create_red_agents()
    
    def _create_red_agents(self) -> List[RedAgent]:
        """Create red agent instances based on blue agents"""
        red_agents = []
        
        for agent in self.agents:
            typical_actions = self.agent_workflows.get(agent.agent_id, [])
            red_agent = RedAgent(agent, typical_actions)
            red_agents.append(red_agent)
        
        return red_agents
    
    def get_agent_by_id(self, agent_id: str) -> RedAgent:
        """Get a specific red agent by ID"""
        for agent in self.red_agents:
            if agent.base_agent.agent_id == agent_id:
                return agent
        raise ValueError(f"Red agent for {agent_id} not found")
    
    def simulate_all_behaviors(self, user_inputs: List[str] = None) -> List[Dict[str, Any]]:
        """Simulate all risky behaviors across all agents"""
        if user_inputs is None:
            runs = self.data_loader.load_runs()
            user_inputs = [run.user_input_summary for run in runs[:len(self.red_agents)]]
        
        results = []
        for i, agent in enumerate(self.red_agents):
            user_input = user_inputs[i] if i < len(user_inputs) else "Red team simulation task"
            
            # Test each risky behavior
            behavior_results = []
            for behavior in RED_AGENT_BEHAVIORS:
                workflow = agent.simulate_risky_workflow(user_input, behavior)
                behavior_results.append({
                    "behavior": behavior,
                    "workflow": workflow,
                    "risk_score": self._calculate_workflow_risk_score(workflow)
                })
            
            results.append({
                "base_agent_id": agent.base_agent.agent_id,
                "base_agent_name": agent.base_agent.agent_name,
                "behavior_results": behavior_results,
                "total_behaviors_tested": len(behavior_results)
            })
        
        return results
    
    def _calculate_workflow_risk_score(self, workflow: List[Dict[str, Any]]) -> float:
        """Calculate overall risk score for a workflow"""
        if not workflow:
            return 0.0
        
        risk_factors = []
        
        for action in workflow:
            action_risk = 0.0
            
            # Data class risk
            data_classes = action.get("data_classes_detected", [])
            if DataClass.SECRETS.value in data_classes:
                action_risk += 0.4
            if DataClass.PHI.value in data_classes:
                action_risk += 0.3
            if DataClass.CONFIDENTIAL.value in data_classes:
                action_risk += 0.2
            if DataClass.PII.value in data_classes:
                action_risk += 0.1
            
            # Domain risk
            domain = action.get("destination_domain", "")
            if "external" in domain or "public" in domain:
                action_risk += 0.2
            
            # Success rate risk (red agents succeeding is risky)
            if action.get("success", False):
                action_risk += 0.1
            
            risk_factors.append(action_risk)
        
        return sum(risk_factors) / len(risk_factors) if risk_factors else 0.0
