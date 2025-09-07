#!/usr/bin/env python3
"""
Data Analyzer - Analyzes CSV data to build capability maps for prospect agents
"""

import csv
import json
from typing import Dict, List, Any
import os
from dotenv import load_dotenv
from agents.base_agent import BaseAgent
from langchain_xai import ChatXAI

# Load environment variables
load_dotenv()

class DataAnalyzer(BaseAgent):
    """Analyzes CSV data to build capability maps for prospect agents"""
    
    def __init__(self):
        system_prompt = """You are an EXPERT DATA ANALYST specializing in agent capability mapping and behavior analysis.

        YOUR EXPERTISE:
        1. CAPABILITY MAPPING: Building comprehensive maps of what agents can do
        2. BEHAVIOR ANALYSIS: Understanding agent usage patterns and frequencies
        3. DATA CLASSIFICATION: Identifying sensitive data types and destinations
        4. TOOL ANALYSIS: Mapping agent tools to their capabilities and usage

        ANALYSIS TASKS:
        1. Parse agents.csv to understand agent definitions and purposes
        2. Analyze runs.csv to understand agent usage patterns and frequencies
        3. Analyze actions.csv to map tools, destinations, and sensitive data
        4. Build capability maps showing what each agent can do

        You build high-level capability maps that show agent tools, destinations, sensitive data, and action frequencies."""
        
        super().__init__(
            name="Data Analyzer",
            role="Data Analyst",
            system_prompt=system_prompt,
            tools=[],
            model="grok-3-mini",
            temperature=0.3
        )
    
    async def analyze_data(self, data_source: str = "walmart_data") -> Dict[str, Any]:
        """Analyze CSV data and build capability maps for each agent"""
        try:
            print("📊 Analyzing CSV data to build capability maps...")
            
            # Load and analyze the CSV files
            agents_data = self._load_agents_csv()
            runs_data = self._load_runs_csv()
            actions_data = self._load_actions_csv()
            
            # Build capability maps for each agent
            capability_maps = self._build_capability_maps(agents_data, runs_data, actions_data)
            
            # Extract company and industry info
            company_info = self._extract_company_info(agents_data)
            
            result = {
                "company_info": company_info,
                "capability_maps": capability_maps,
                "total_agents": len(capability_maps),
                "analysis_timestamp": self._get_timestamp()
            }
            
            print(f"   ✅ Built capability maps for {len(capability_maps)} agents")
            print(f"   ✅ Company: {company_info.get('company', 'Unknown')}")
            print(f"   ✅ Industry: {company_info.get('industry', 'Unknown')}")
            
            return result
            
        except Exception as e:
            print(f"Error analyzing data: {e}")
            return self._get_fallback_analysis()
    
    def _load_agents_csv(self) -> List[Dict[str, Any]]:
        """Load and parse agents.csv"""
        agents = []
        try:
            with open('data/agents.csv', 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    agents.append({
                        'agent_id': row['agent_id'],
                        'agent_name': row['agent_name'],
                        'purpose_summary': row['purpose_summary'],
                        'created_at': row['created_at']
                    })
        except Exception as e:
            print(f"Error loading agents.csv: {e}")
        
        return agents
    
    def _load_runs_csv(self) -> List[Dict[str, Any]]:
        """Load and parse runs.csv"""
        runs = []
        try:
            with open('data/runs.csv', 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    runs.append({
                        'run_id': row['run_id'],
                        'agent_id': row['agent_id'],
                        'started_at': row['started_at'],
                        'ended_at': row['ended_at'],
                        'status': row['status'],
                        'user_input_summary': row['user_input_summary']
                    })
        except Exception as e:
            print(f"Error loading runs.csv: {e}")
        
        return runs
    
    def _load_actions_csv(self) -> List[Dict[str, Any]]:
        """Load and parse actions.csv"""
        actions = []
        try:
            with open('data/actions.csv', 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Parse data_classes_detected_json
                    data_classes = []
                    if row['data_classes_detected_json'] and row['data_classes_detected_json'] != '[]':
                        try:
                            data_classes = json.loads(row['data_classes_detected_json'])
                        except:
                            data_classes = []
                    
                    actions.append({
                        'action_id': row['action_id'],
                        'run_id': row['run_id'],
                        'action_type': row['action_type'],
                        'action_name': row['action_name'],
                        'started_at': row['started_at'],
                        'ended_at': row['ended_at'],
                        'success': row['success'] == 'true',
                        'destination_domain': row['destination_domain'],
                        'data_classes_detected': data_classes
                    })
        except Exception as e:
            print(f"Error loading actions.csv: {e}")
        
        return actions
    
    def _build_capability_maps(self, agents_data: List[Dict], runs_data: List[Dict], actions_data: List[Dict]) -> Dict[str, Dict[str, Any]]:
        """Build capability maps for each agent"""
        capability_maps = {}
        
        for agent in agents_data:
            agent_id = agent['agent_id']
            
            # Get runs for this agent
            agent_runs = [run for run in runs_data if run['agent_id'] == agent_id]
            
            # Get actions for this agent's runs
            agent_run_ids = [run['run_id'] for run in agent_runs]
            agent_actions = [action for action in actions_data if action['run_id'] in agent_run_ids]
            
            # Build capability map
            capability_map = {
                'agent_info': agent,
                'usage_stats': self._calculate_usage_stats(agent_runs),
                'tools_used': self._extract_tools_used(agent_actions),
                'destinations': self._extract_destinations(agent_actions),
                'sensitive_data': self._extract_sensitive_data(agent_actions),
                'action_frequencies': self._calculate_action_frequencies(agent_actions)
            }
            
            capability_maps[agent_id] = capability_map
        
        return capability_maps
    
    def _calculate_usage_stats(self, runs: List[Dict]) -> Dict[str, Any]:
        """Calculate usage statistics for an agent"""
        if not runs:
            return {'total_runs': 0, 'success_rate': 0, 'avg_duration': 0}
        
        total_runs = len(runs)
        successful_runs = len([run for run in runs if run['status'] == 'success'])
        success_rate = (successful_runs / total_runs) * 100 if total_runs > 0 else 0
        
        # Calculate average duration (simplified)
        durations = []
        for run in runs:
            try:
                # Simple duration calculation (in minutes)
                start = run['started_at']
                end = run['ended_at']
                # For now, just use a placeholder
                durations.append(2.5)  # Average 2.5 minutes
            except:
                durations.append(2.5)
        
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            'total_runs': total_runs,
            'success_rate': round(success_rate, 1),
            'avg_duration_minutes': round(avg_duration, 1)
        }
    
    def _extract_tools_used(self, actions: List[Dict]) -> List[str]:
        """Extract unique tools used by an agent"""
        tools = set()
        for action in actions:
            if action['action_type'] == 'tool':
                tools.add(action['action_name'])
        return sorted(list(tools))
    
    def _extract_destinations(self, actions: List[Dict]) -> List[str]:
        """Extract unique destinations accessed by an agent"""
        destinations = set()
        for action in actions:
            if action['destination_domain']:
                destinations.add(action['destination_domain'])
        return sorted(list(destinations))
    
    def _extract_sensitive_data(self, actions: List[Dict]) -> List[str]:
        """Extract sensitive data types handled by an agent"""
        sensitive_data = set()
        for action in actions:
            for data_class in action['data_classes_detected']:
                sensitive_data.add(data_class)
        return sorted(list(sensitive_data))
    
    def _calculate_action_frequencies(self, actions: List[Dict]) -> Dict[str, int]:
        """Calculate frequency of each action type"""
        frequencies = {}
        for action in actions:
            action_name = action['action_name']
            frequencies[action_name] = frequencies.get(action_name, 0) + 1
        return frequencies
    
    def _extract_company_info(self, agents_data: List[Dict]) -> Dict[str, str]:
        """Extract company and industry information"""
        # Analyze agent names and purposes to determine company and industry
        company = "Unknown"
        industry = "Unknown"
        
        # Simple heuristics based on agent names and purposes
        if any('wm_' in agent['agent_id'] for agent in agents_data):
            company = "Walmart"
            industry = "Retail and E-commerce"
        elif any('shop' in agent['purpose_summary'].lower() for agent in agents_data):
            industry = "E-commerce"
        elif any('supplier' in agent['purpose_summary'].lower() for agent in agents_data):
            industry = "Supply Chain"
        
        return {
            'company': company,
            'industry': industry
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _get_fallback_analysis(self) -> Dict[str, Any]:
        """Get fallback analysis if main analysis fails"""
        return {
            "company_info": {"company": "Unknown", "industry": "Unknown"},
            "capability_maps": {},
            "total_agents": 0,
            "analysis_timestamp": self._get_timestamp()
        }

def get_data_analyzer() -> DataAnalyzer:
    """Get the data analyzer instance"""
    return DataAnalyzer()