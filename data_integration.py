#!/usr/bin/env python3
"""
Data integration for LangChain agents - loads historical data to inform agent behavior
"""

import pandas as pd
import json
from typing import List, Dict, Any
from datetime import datetime

class DataIntegration:
    """Integrates historical data with LangChain agents"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.agents_data = self._load_agents_data()
        self.actions_data = self._load_actions_data()
        self.runs_data = self._load_runs_data()
        self.monitoring_data = self._load_monitoring_data()
    
    def _load_agents_data(self) -> pd.DataFrame:
        """Load agent definitions"""
        return pd.read_csv(f"{self.data_dir}/agents.csv")
    
    def _load_actions_data(self) -> pd.DataFrame:
        """Load historical actions data"""
        df = pd.read_csv(f"{self.data_dir}/actions.csv")
        # Parse JSON columns
        df['data_classes_detected'] = df['data_classes_detected_json'].apply(
            lambda x: json.loads(x) if pd.notna(x) and x != '[]' else []
        )
        return df
    
    def _load_runs_data(self) -> pd.DataFrame:
        """Load runs data"""
        return pd.read_csv(f"{self.data_dir}/runs.csv")
    
    def _load_monitoring_data(self) -> pd.DataFrame:
        """Load monitoring data"""
        return pd.read_csv(f"{self.data_dir}/monitoring.csv")
    
    def get_agent_behavior_patterns(self, agent_id: str) -> Dict[str, Any]:
        """Get behavior patterns for a specific agent"""
        agent_actions = self.actions_data[
            self.actions_data['action_id'].str.contains(agent_id, na=False)
        ]
        
        if agent_actions.empty:
            return {
                "common_actions": {},
                "success_rate": 0.0,
                "typical_domains": {},
                "data_classes_used": {},
                "average_duration": 0.0
            }
        
        # Analyze behavior patterns
        common_actions = agent_actions['action_name'].value_counts().head(5).to_dict()
        success_rate = agent_actions['success'].mean()
        typical_domains = agent_actions['destination_domain'].dropna().value_counts().head(3).to_dict()
        
        # Data classes analysis
        all_data_classes = []
        for classes in agent_actions['data_classes_detected']:
            all_data_classes.extend(classes)
        data_classes_used = pd.Series(all_data_classes).value_counts().to_dict()
        
        # Duration analysis
        agent_actions['duration'] = (
            pd.to_datetime(agent_actions['ended_at']) - 
            pd.to_datetime(agent_actions['started_at'])
        ).dt.total_seconds()
        average_duration = agent_actions['duration'].mean()
        
        return {
            "common_actions": common_actions,
            "success_rate": success_rate,
            "typical_domains": typical_domains,
            "data_classes_used": data_classes_used,
            "average_duration": average_duration
        }
    
    def get_risky_actions_history(self) -> List[Dict[str, Any]]:
        """Get historical risky actions for security analysis"""
        risky_actions = self.actions_data[
            self.actions_data['data_classes_detected'].apply(
                lambda x: len(x) > 0 and any(
                    dc in ['PII', 'PHI', 'CONFIDENTIAL', 'SECRETS'] 
                    for dc in x
                )
            )
        ]
        
        return risky_actions.to_dict('records')
    
    def get_agent_system_prompts(self) -> Dict[str, str]:
        """Generate system prompts based on historical data"""
        prompts = {}
        
        for _, agent in self.agents_data.iterrows():
            agent_id = agent['agent_id']
            agent_name = agent['agent_name']
            purpose = agent['purpose_summary']
            
            # Get behavior patterns
            patterns = self.get_agent_behavior_patterns(agent_id)
            
            # Generate contextual system prompt
            prompt = f"""You are {agent_name}. {purpose}

Based on your historical behavior patterns:
- Common actions: {', '.join(list(patterns['common_actions'].keys())[:3]) if patterns['common_actions'] else 'No historical data'}
- Success rate: {patterns['success_rate']:.1%}
- Typical domains: {', '.join(list(patterns['typical_domains'].keys())[:3]) if patterns['typical_domains'] else 'No historical data'}

Act naturally based on your role and capabilities. Use the tools available to you to help users effectively."""
            
            prompts[agent_id] = prompt
        
        return prompts
    
    def get_security_insights(self) -> Dict[str, Any]:
        """Get security insights from historical data"""
        risky_actions = self.get_risky_actions_history()
        
        # Analyze risk patterns
        risk_by_agent = {}
        for action in risky_actions:
            agent_id = action['action_id'].split('_')[0] if '_' in action['action_id'] else 'unknown'
            if agent_id not in risk_by_agent:
                risk_by_agent[agent_id] = []
            risk_by_agent[agent_id].append(action)
        
        # Calculate risk scores
        risk_scores = {}
        for agent_id, actions in risk_by_agent.items():
            total_actions = len(self.actions_data[
                self.actions_data['action_id'].str.contains(agent_id, na=False)
            ])
            risky_count = len(actions)
            risk_scores[agent_id] = {
                'total_actions': total_actions,
                'risky_actions': risky_count,
                'risk_ratio': risky_count / total_actions if total_actions > 0 else 0
            }
        
        return {
            'total_risky_actions': len(risky_actions),
            'risk_by_agent': risk_scores,
            'common_risky_patterns': self._analyze_risky_patterns(risky_actions)
        }
    
    def _analyze_risky_patterns(self, risky_actions: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in risky actions"""
        if not risky_actions:
            return {}
        
        df = pd.DataFrame(risky_actions)
        
        return {
            'most_common_risky_actions': df['action_name'].value_counts().head(3).to_dict(),
            'most_common_domains': df['destination_domain'].value_counts().head(3).to_dict(),
            'data_class_frequency': self._count_data_classes(risky_actions)
        }
    
    def _count_data_classes(self, risky_actions: List[Dict]) -> Dict[str, int]:
        """Count frequency of data classes in risky actions"""
        data_class_counts = {}
        for action in risky_actions:
            for dc in action.get('data_classes_detected', []):
                data_class_counts[dc] = data_class_counts.get(dc, 0) + 1
        return data_class_counts

# Example usage
if __name__ == "__main__":
    data_integration = DataIntegration()
    
    # Get agent behavior patterns
    for agent_id in ['a_wm_shopper', 'a_wm_developer']:
        patterns = data_integration.get_agent_behavior_patterns(agent_id)
        print(f"\n{agent_id} patterns:")
        print(f"  Common actions: {patterns['common_actions']}")
        print(f"  Success rate: {patterns['success_rate']:.1%}")
    
    # Get security insights
    security_insights = data_integration.get_security_insights()
    print(f"\nSecurity insights:")
    print(f"  Total risky actions: {security_insights['total_risky_actions']}")
    print(f"  Risk by agent: {security_insights['risk_by_agent']}")
