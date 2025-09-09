#!/usr/bin/env python3
"""
Policy Generator Agent - Generates security policy options using LLM analysis
"""

import json
import re
from typing import Dict, List, Any
from datetime import datetime
from dotenv import load_dotenv
from agents.base_agent import BaseAgent
from langchain_xai import ChatXAI

# Load environment variables
load_dotenv()

class PolicyGeneratorAgent(BaseAgent):
    """Professional policy generator with expertise in security tradeoffs"""
    
    def __init__(self):
        system_prompt = """You are a PROFESSIONAL SECURITY POLICY EXPERT with 20+ years of experience in:
        
        EXPERTISE:
        - Security policy development and risk management
        - Product security and user experience tradeoffs
        - Business impact analysis for security decisions
        - AI agent security and compliance
        
        YOUR ROLE:
        You analyze vulnerability scenarios and generate comprehensive policy options with detailed tradeoff analysis.
        You understand the delicate balance between security and user experience in AI agent deployments.
        
        POLICY GENERATION APPROACH:
        1. Analyze each vulnerability scenario in context
        2. Generate 3 policy options: Block, Sanitize, Allow
        3. Provide detailed tradeoff analysis for each option
        4. Recommend the best option with clear rationale
        5. Clean up descriptions to remove specific technical details
        
        COMMUNICATION STYLE:
        - Professional and authoritative
        - Clear, actionable policy recommendations
        - Balanced perspective on security vs usability
        - Business-focused language for executive audiences"""
        
        super().__init__(
            name="Policy Generator",
            role="Security Policy Expert",
            system_prompt=system_prompt,
            tools=[],
            model="grok-3-mini",
            temperature=0.3
        )
    
    async def generate_policy_analysis(self, vulnerability_scenarios: List[Dict]) -> List[Dict]:
        """Generate policy analysis for vulnerability scenarios grouped by agent"""
        
        # Group scenarios by prospect agent
        agent_scenarios = {}
        for scenario in vulnerability_scenarios:
            agent_name = scenario.get('prospect_agent', 'Unknown Agent')
            if agent_name not in agent_scenarios:
                agent_scenarios[agent_name] = []
            agent_scenarios[agent_name].append(scenario)
        
        print(f"📊 Processing {len(agent_scenarios)} agents with {len(vulnerability_scenarios)} total scenarios")
        
        policy_analyses = []
        
        # Process each agent's scenarios together
        for agent_name, scenarios in agent_scenarios.items():
            print(f"🔍 Generating policy analysis for {agent_name} ({len(scenarios)} scenarios)")
            
            # Prepare all scenarios for this agent
            agent_context = self._prepare_agent_context(agent_name, scenarios)
            
            # Generate policy analysis for all scenarios of this agent
            agent_policy_analysis = await self._generate_agent_policy_analysis(agent_context)
            
            # Add individual scenario results
            for i, scenario in enumerate(scenarios):
                policy_analyses.append({
                    'original_scenario': scenario,
                    'scenario_context': self._prepare_scenario_context(scenario),
                    'policy_analysis': agent_policy_analysis['scenarios'][i] if i < len(agent_policy_analysis['scenarios']) else agent_policy_analysis['scenarios'][0],
                    'agent_summary': agent_policy_analysis.get('agent_summary', {}),
                    'agent_recommendations': agent_policy_analysis.get('agent_recommendations', {})
                })
        
        return policy_analyses
    
    def _prepare_agent_context(self, agent_name: str, scenarios: List[Dict]) -> Dict:
        """Prepare context for all scenarios of a specific agent"""
        scenario_contexts = []
        for scenario in scenarios:
            scenario_contexts.append(self._prepare_scenario_context(scenario))
        
        return {
            'agent_name': agent_name,
            'total_scenarios': len(scenarios),
            'scenarios': scenario_contexts,
            'scenario_types': list(set(s.get('scenario_type', 'Unknown') for s in scenarios)),
            'risk_levels': list(set(s.get('risk_level', 'Medium') for s in scenarios))
        }
    
    def _prepare_scenario_context(self, scenario: Dict) -> Dict:
        """Prepare scenario context for LLM analysis"""
        return {
            'scenario_type': scenario.get('scenario_type', 'Unknown'),
            'description': scenario.get('description', ''),
            'evidence': scenario.get('evidence', ''),
            'risk_level': scenario.get('risk_level', 'Medium'),
            'business_impact': scenario.get('business_impact', ''),
            'prospect_agent': scenario.get('prospect_agent', 'Unknown Agent'),
            'episode_id': scenario.get('episode_id', 'Unknown')
        }
    
    async def _generate_agent_policy_analysis(self, agent_context: Dict) -> Dict:
        """Generate policy analysis for all scenarios of a specific agent using LLM"""
        
        analysis_prompt = f"""
        As a professional security policy expert with 20+ years of experience, analyze ALL vulnerability scenarios for this specific agent and generate comprehensive policy recommendations.

        AGENT: {agent_context['agent_name']}
        TOTAL SCENARIOS: {agent_context['total_scenarios']}
        SCENARIO TYPES: {', '.join(agent_context['scenario_types'])}
        RISK LEVELS: {', '.join(agent_context['risk_levels'])}

        VULNERABILITY SCENARIOS:
        """
        
        # Add each scenario to the prompt
        for i, scenario in enumerate(agent_context['scenarios'], 1):
            analysis_prompt += f"""
        SCENARIO {i}:
        Type: {scenario['scenario_type']}
        Description: {scenario['description']}
        Evidence: {scenario['evidence']}
        Risk Level: {scenario['risk_level']}
        Business Impact: {scenario['business_impact']}
        """
        
        analysis_prompt += f"""

        YOUR TASK:
        Analyze ALL scenarios for this agent and provide comprehensive policy recommendations. Focus on:
        1. Patterns across multiple scenarios for this agent
        2. Overall security posture of this agent
        3. Agent-specific policy recommendations
        4. Balance between security and product usability

        IMPORTANT INSTRUCTIONS:
        1. Do NOT include specific endpoint names, IP addresses, or technical details in your analysis
        2. Focus on the general vulnerability patterns and their implications
        3. Consider the user experience impact carefully - this is an AI agent that needs to be useful
        4. Provide detailed security impact analysis
        5. Give clear explanations for each policy option
        6. Recommend the best overall approach for this agent
        7. Identify recurring patterns and suggest unified policies

        Generate policy analysis for each scenario AND overall agent recommendations:

        For EACH scenario, provide:
        - Block policy (what blocking means for this specific scenario)
        - Sanitize policy (what sanitizing means for this specific scenario)  
        - Allow policy (what allowing means for this specific scenario)
        - Recommended option for this scenario
        - Rationale for the recommendation

        For the AGENT OVERALL, provide:
        - Agent security summary
        - Unified policy recommendations
        - Implementation priorities
        - Risk assessment

        Return as JSON:
        {{
            "scenarios": [
                {{
                    "scenario_index": 1,
                    "block": {{
                        "description": "What blocking this scenario means",
                        "user_experience_impact": "How this affects agent usefulness",
                        "security_impact": "What is the security impact/risk if this option is chosen"
                    }},
                    "sanitize": {{
                        "description": "What sanitizing this scenario means",
                        "user_experience_impact": "How this affects agent usefulness",
                        "security_impact": "What is the security impact/risk if this option is chosen"
                    }},
                    "allow": {{
                        "description": "What allowing this scenario means",
                        "user_experience_impact": "How this affects agent usefulness",
                        "security_impact": "What is the security impact/risk if this option is chosen"
                    }},
                    "recommended_option": "Block/Sanitize/Allow",
                    "explanation": "Why this option provides the best balance for this scenario"
                }}
            ],
            "agent_summary": {{
                "total_vulnerabilities": {agent_context['total_scenarios']},
                "primary_risk_level": "High/Medium/Low",
                "main_vulnerability_patterns": ["pattern1", "pattern2"],
                "overall_security_posture": "Strong/Moderate/Weak",
                "agent_specific_risks": "Key risks specific to this agent type"
            }},
            "agent_recommendations": {{
                "unified_policy_approach": "Recommended overall approach for this agent",
                "implementation_priority": "High/Medium/Low",
                "key_controls": ["control1", "control2"],
                "monitoring_focus": "What to monitor specifically for this agent",
                "risk_mitigation_strategy": "Overall strategy to reduce risks"
            }}
        }}
        """
        
        try:
            response = await self.llm.ainvoke(analysis_prompt)
            analysis_text = response.content.strip()
            
            # Try to parse JSON response
            try:
                policy_analysis = json.loads(analysis_text)
                return policy_analysis
            except json.JSONDecodeError:
                return self._fallback_agent_policy_analysis(agent_context)
                
        except Exception as e:
            print(f"Error generating agent policy analysis: {e}")
            return self._fallback_agent_policy_analysis(agent_context)
    
    async def _generate_scenario_policy_analysis(self, scenario_context: Dict) -> Dict:
        """Generate policy analysis for a single scenario using LLM"""
        
        analysis_prompt = f"""
        As a professional security policy expert with 20+ years of experience, analyze this vulnerability scenario and generate comprehensive policy options.

        VULNERABILITY SCENARIO:
        Type: {scenario_context['scenario_type']}
        Description: {scenario_context['description']}
        Evidence: {scenario_context['evidence']}
        Risk Level: {scenario_context['risk_level']}
        Business Impact: {scenario_context['business_impact']}
        Affected Agent: {scenario_context['prospect_agent']}

        YOUR TASK:
        Analyze this scenario and provide three policy options with detailed tradeoff analysis. Focus on the balance between security and product usability.

        IMPORTANT INSTRUCTIONS:
        1. Do NOT include specific endpoint names, IP addresses, or technical details in your analysis
        2. Focus on the general vulnerability pattern and its implications
        3. Consider the user experience impact carefully - this is an AI agent that needs to be useful
        4. Provide detailed security impact analysis
        5. Give clear explanations for each policy option
        6. Recommend the option that best balances security and product usability

        Generate three policy options:

        1. BLOCK - Complete prevention of the vulnerability
        2. SANITIZE - Filter/redact sensitive information while maintaining functionality  
        3. ALLOW - Permit the behavior but monitor and alert

        For each option, analyze:
        - What the policy does (detailed description)
        - Security benefits and protections provided
        - User experience impact (how this affects the agent's usefulness)
        - Business impact (positive and negative effects)
        - Implementation complexity (Low/Medium/High)
        - Specific technical measures required

        Then provide:
        - Recommended option (Block/Sanitize/Allow)
        - Detailed rationale focusing on the security vs product usability tradeoff
        - Risk assessment of the recommended approach

        Return as JSON:
        {{
            "block": {{
                "description": "What blocking this vulnerability means",
                "user_experience_impact": "How this affects the agent's ability to help users",
                "security_impact": "What security protections this provides"
            }},
            "sanitize": {{
                "description": "What sanitizing this vulnerability means",
                "user_experience_impact": "How this affects the agent's ability to help users",
                "security_impact": "What security protections this provides"
            }},
            "allow": {{
                "description": "What allowing this vulnerability means",
                "user_experience_impact": "How this affects the agent's ability to help users",
                "security_impact": "What security protections this provides"
            }},
            "recommended_option": "Block/Sanitize/Allow",
            "explanation": "Why this option provides the best balance between security and product usability"
        }}
        """
        
        try:
            response = await self.llm.ainvoke(analysis_prompt)
            analysis_text = response.content.strip()
            
            # Try to parse JSON response
            try:
                policy_analysis = json.loads(analysis_text)
                return policy_analysis
            except json.JSONDecodeError:
                return self._fallback_policy_analysis(scenario_context)
                
        except Exception as e:
            print(f"Error generating policy analysis: {e}")
            return self._fallback_policy_analysis(scenario_context)
    
    def _fallback_agent_policy_analysis(self, agent_context: Dict) -> Dict:
        """Fallback agent policy analysis if LLM fails"""
        scenarios = agent_context['scenarios']
        agent_name = agent_context['agent_name']
        
        # Generate basic analysis for each scenario
        scenario_analyses = []
        for i, scenario in enumerate(scenarios):
            scenario_analyses.append({
                "scenario_index": i + 1,
                "block": {
                    "description": f"Block {scenario['scenario_type'].lower()} vulnerability for {agent_name}",
                    "user_experience_impact": "May impact user experience if legitimate functionality is blocked",
                    "security_impact": "Eliminates the security risk completely - no exposure possible"
                },
                "sanitize": {
                    "description": f"Sanitize {scenario['scenario_type'].lower()} vulnerability for {agent_name}",
                    "user_experience_impact": "Minimal impact on user experience",
                    "security_impact": "Reduces security risk by filtering sensitive data while maintaining functionality"
                },
                "allow": {
                    "description": f"Allow {scenario['scenario_type'].lower()} vulnerability for {agent_name} with monitoring",
                    "user_experience_impact": "No impact on user experience",
                    "security_impact": "Maintains security risk but enables monitoring and response capabilities"
                },
                "recommended_option": "Sanitize",
                "explanation": "Balances security and usability for this agent type"
            })
        
        return {
            "scenarios": scenario_analyses,
            "agent_summary": {
                "total_vulnerabilities": len(scenarios),
                "primary_risk_level": "Medium",
                "main_vulnerability_patterns": list(set(s['scenario_type'] for s in scenarios)),
                "overall_security_posture": "Moderate",
                "agent_specific_risks": f"Multiple vulnerability types detected for {agent_name}"
            },
            "agent_recommendations": {
                "unified_policy_approach": "Implement content sanitization with monitoring",
                "implementation_priority": "Medium",
                "key_controls": ["Content filtering", "Response monitoring", "Access controls"],
                "monitoring_focus": f"Monitor {agent_name} responses for sensitive information disclosure",
                "risk_mitigation_strategy": "Implement layered security controls with regular review"
            }
        }
    
    def _fallback_policy_analysis(self, scenario_context: Dict) -> Dict:
        """Fallback policy analysis if LLM fails"""
        scenario_type = scenario_context.get('scenario_type', 'UNKNOWN')
        risk_level = scenario_context.get('risk_level', 'Medium')
        
        return {
            "block": {
                "description": f"Completely prevent the {scenario_type.lower()} vulnerability by stopping the agent workflow when this behavior is detected.",
                "user_experience_impact": "May impact user experience if legitimate functionality is blocked",
                "security_impact": "Eliminates the security risk completely - no exposure possible"
            },
            "sanitize": {
                "description": f"Filter and redact sensitive information related to {scenario_type.lower()} while maintaining agent functionality.",
                "user_experience_impact": "Minimal impact on user experience",
                "security_impact": "Reduces security risk by filtering sensitive data while maintaining functionality"
            },
            "allow": {
                "description": f"Allow the {scenario_type.lower()} behavior but implement comprehensive monitoring and alerting.",
                "user_experience_impact": "No impact on user experience",
                "security_impact": "Maintains security risk but enables monitoring and response capabilities"
            },
            "recommended_option": "Block" if risk_level.lower() == 'high' else "Sanitize",
            "explanation": f"Based on {risk_level.lower()} risk level, the recommended approach balances security and usability."
        }

def get_policy_generator() -> PolicyGeneratorAgent:
    """Get the policy generator instance"""
    return PolicyGeneratorAgent()
