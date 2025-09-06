import pandas as pd
from typing import List, Dict, Any
from models import Agent, Action, Run, MonitoringScenario, DataClass, ActionType, RunStatus, SeverityLevel
from datetime import datetime
import json

class DataLoader:
    def __init__(self, data_path: str = "./data"):
        self.data_path = data_path
    
    def load_agents(self) -> List[Agent]:
        """Load agents from CSV file"""
        df = pd.read_csv(f"{self.data_path}/agents.csv")
        agents = []
        
        for _, row in df.iterrows():
            agent = Agent(
                agent_id=row['agent_id'],
                agent_name=row['agent_name'],
                purpose_summary=row['purpose_summary'],
                created_at=datetime.fromisoformat(row['created_at'].replace('Z', '+00:00'))
            )
            agents.append(agent)
        
        return agents
    
    def load_actions(self) -> List[Action]:
        """Load actions from CSV file"""
        df = pd.read_csv(f"{self.data_path}/actions.csv")
        actions = []
        
        for _, row in df.iterrows():
            # Parse data classes from JSON string
            data_classes = []
            if pd.notna(row['data_classes_detected_json']) and row['data_classes_detected_json'] != '[]':
                try:
                    data_classes_list = json.loads(row['data_classes_detected_json'])
                    data_classes = [DataClass(dc) for dc in data_classes_list if dc in [e.value for e in DataClass]]
                except (json.JSONDecodeError, ValueError):
                    data_classes = []
            
            action = Action(
                action_id=row['action_id'],
                run_id=row['run_id'],
                action_type=ActionType(row['action_type']),
                action_name=row['action_name'],
                started_at=datetime.fromisoformat(row['started_at'].replace('Z', '+00:00')),
                ended_at=datetime.fromisoformat(row['ended_at'].replace('Z', '+00:00')),
                success=row['success'],
                destination_domain=row['destination_domain'] if pd.notna(row['destination_domain']) else None,
                data_classes_detected_json=data_classes
            )
            actions.append(action)
        
        return actions
    
    def load_runs(self) -> List[Run]:
        """Load runs from CSV file"""
        df = pd.read_csv(f"{self.data_path}/runs.csv")
        runs = []
        
        for _, row in df.iterrows():
            run = Run(
                run_id=row['run_id'],
                agent_id=row['agent_id'],
                started_at=datetime.fromisoformat(row['started_at'].replace('Z', '+00:00')),
                ended_at=datetime.fromisoformat(row['ended_at'].replace('Z', '+00:00')),
                status=RunStatus(row['status']),
                user_input_summary=row['user_input_summary']
            )
            runs.append(run)
        
        return runs
    
    def load_monitoring_scenarios(self) -> List[MonitoringScenario]:
        """Load monitoring scenarios from CSV file"""
        df = pd.read_csv(f"{self.data_path}/monitoring.csv")
        scenarios = []
        
        for _, row in df.iterrows():
            scenario = MonitoringScenario(
                scenario_id=row['scenario_id'],
                action_id=row['action_id'],
                vuln_type=row['vuln_type'],
                severity=SeverityLevel(row['severity']),
                recommended_option=row['recommended_option']
            )
            scenarios.append(scenario)
        
        return scenarios
    
    def get_agent_workflows(self) -> Dict[str, List[Action]]:
        """Group actions by agent to understand typical workflows"""
        agents = self.load_agents()
        actions = self.load_actions()
        runs = self.load_runs()
        
        # Create agent_id to run_id mapping
        agent_runs = {run.agent_id: run.run_id for run in runs}
        
        # Group actions by agent
        agent_workflows = {}
        for agent in agents:
            agent_workflows[agent.agent_id] = []
            for action in actions:
                if action.run_id in [run_id for run_id, agent_id in agent_runs.items() if agent_id == agent.agent_id]:
                    agent_workflows[agent.agent_id].append(action)
        
        return agent_workflows
