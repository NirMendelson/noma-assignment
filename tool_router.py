import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from models import Action, ActionType, DataClass
import json

class ToolRouter:
    """Central gateway for all actions - routes calls and logs everything"""
    
    def __init__(self):
        self.action_log = []
        self.metadata_cache = {}
    
    def route_action(self, 
                    action_type: ActionType,
                    action_name: str,
                    agent_id: str,
                    agent_name: str,
                    user_input: str,
                    destination_domain: Optional[str] = None,
                    data_classes: List[DataClass] = None,
                    metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Route an action through the tool router with logging"""
        
        action_id = f"act_{uuid.uuid4().hex[:8]}"
        started_at = datetime.now()
        
        # Attach metadata
        action_metadata = {
            "action_id": action_id,
            "agent_id": agent_id,
            "agent_name": agent_name,
            "user_input": user_input,
            "action_type": action_type.value,
            "action_name": action_name,
            "destination_domain": destination_domain,
            "data_classes": [dc.value for dc in (data_classes or [])],
            "started_at": started_at.isoformat(),
            "scope": self._determine_scope(action_name, destination_domain),
            "pii_tags": self._extract_pii_tags(data_classes or []),
            "environment": self._determine_environment(destination_domain),
            "additional_metadata": metadata or {}
        }
        
        # Simulate action execution
        execution_result = self._simulate_action_execution(action_metadata)
        
        # Complete the action
        ended_at = datetime.now()
        action_metadata.update({
            "ended_at": ended_at.isoformat(),
            "success": execution_result["success"],
            "duration_seconds": (ended_at - started_at).total_seconds(),
            "execution_result": execution_result
        })
        
        # Log the action
        self.action_log.append(action_metadata)
        
        return action_metadata
    
    def _determine_scope(self, action_name: str, destination_domain: Optional[str]) -> str:
        """Determine the scope of the action"""
        if not destination_domain:
            return "internal"
        
        if "walmart.internal" in destination_domain:
            return "internal"
        elif "external" in destination_domain or "public" in destination_domain:
            return "external"
        elif "api." in destination_domain:
            return "api"
        else:
            return "unknown"
    
    def _extract_pii_tags(self, data_classes: List[DataClass]) -> List[str]:
        """Extract PII tags from data classes"""
        pii_tags = []
        for dc in data_classes:
            if dc == DataClass.PII:
                pii_tags.append("personal_identifiers")
            elif dc == DataClass.PHI:
                pii_tags.append("health_information")
            elif dc == DataClass.CONFIDENTIAL:
                pii_tags.append("confidential_data")
            elif dc == DataClass.SECRETS:
                pii_tags.append("secrets")
        
        return pii_tags
    
    def _determine_environment(self, destination_domain: Optional[str]) -> str:
        """Determine the environment based on domain"""
        if not destination_domain:
            return "unknown"
        
        if "staging" in destination_domain or "test" in destination_domain:
            return "staging"
        elif "prod" in destination_domain or "production" in destination_domain:
            return "production"
        elif "dev" in destination_domain or "development" in destination_domain:
            return "development"
        else:
            return "unknown"
    
    def _simulate_action_execution(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate the actual execution of an action"""
        action_name = metadata["action_name"]
        action_type = metadata["action_type"]
        
        # Simulate different success rates based on action type
        if action_type == "retrieval":
            success_rate = 0.95
        elif action_type == "tool":
            success_rate = 0.85
        else:
            success_rate = 0.90
        
        # Add some randomness
        success = hash(action_name) % 100 < (success_rate * 100)
        
        # Simulate different response times
        if "bulk" in action_name or "import" in action_name:
            response_time = 2.5
        elif "search" in action_name or "query" in action_name:
            response_time = 1.2
        else:
            response_time = 0.8
        
        return {
            "success": success,
            "response_time": response_time,
            "status_code": 200 if success else 500,
            "error_message": None if success else f"Action {action_name} failed",
            "data_processed": metadata.get("data_classes", []),
            "scope_accessed": metadata["scope"]
        }
    
    def get_action_log(self, agent_id: Optional[str] = None, 
                      action_type: Optional[ActionType] = None) -> List[Dict[str, Any]]:
        """Get filtered action log"""
        filtered_log = self.action_log
        
        if agent_id:
            filtered_log = [action for action in filtered_log if action["agent_id"] == agent_id]
        
        if action_type:
            filtered_log = [action for action in filtered_log if action["action_type"] == action_type.value]
        
        return filtered_log
    
    def get_agent_statistics(self, agent_id: str) -> Dict[str, Any]:
        """Get statistics for a specific agent"""
        agent_actions = [action for action in self.action_log if action["agent_id"] == agent_id]
        
        if not agent_actions:
            return {"error": "No actions found for agent"}
        
        total_actions = len(agent_actions)
        successful_actions = sum(1 for action in agent_actions if action["success"])
        success_rate = successful_actions / total_actions
        
        # Data class analysis
        all_data_classes = []
        for action in agent_actions:
            all_data_classes.extend(action.get("data_classes", []))
        
        data_class_counts = {}
        for dc in all_data_classes:
            data_class_counts[dc] = data_class_counts.get(dc, 0) + 1
        
        # Domain analysis
        domains = [action["destination_domain"] for action in agent_actions if action["destination_domain"]]
        domain_counts = {}
        for domain in domains:
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        return {
            "agent_id": agent_id,
            "total_actions": total_actions,
            "successful_actions": successful_actions,
            "success_rate": success_rate,
            "data_class_usage": data_class_counts,
            "domain_usage": domain_counts,
            "average_duration": sum(action["duration_seconds"] for action in agent_actions) / total_actions,
            "scope_breakdown": self._get_scope_breakdown(agent_actions)
        }
    
    def _get_scope_breakdown(self, actions: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get breakdown of actions by scope"""
        scope_counts = {}
        for action in actions:
            scope = action.get("scope", "unknown")
            scope_counts[scope] = scope_counts.get(scope, 0) + 1
        return scope_counts
    
    def export_log(self, format: str = "json") -> str:
        """Export the action log in specified format"""
        if format.lower() == "json":
            return json.dumps(self.action_log, indent=2, default=str)
        elif format.lower() == "csv":
            # Convert to CSV format
            if not self.action_log:
                return ""
            
            headers = list(self.action_log[0].keys())
            csv_lines = [",".join(headers)]
            
            for action in self.action_log:
                row = []
                for header in headers:
                    value = action.get(header, "")
                    if isinstance(value, (list, dict)):
                        value = json.dumps(value)
                    row.append(str(value))
                csv_lines.append(",".join(row))
            
            return "\n".join(csv_lines)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def clear_log(self):
        """Clear the action log"""
        self.action_log = []
    
    def get_recent_actions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent actions from the log"""
        return self.action_log[-limit:] if self.action_log else []
