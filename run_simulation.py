#!/usr/bin/env python3
"""
Quick simulation runner for testing the Agent Risk Simulator
"""

import asyncio
import json
from datetime import datetime
from data_loader import DataLoader
from blue_agents import BlueAgentManager
from red_agents import RedAgentManager
from tool_router import ToolRouter
from evaluator import SecurityEvaluator

async def run_quick_simulation():
    """Run a quick simulation to test the system"""
    print("🔒 Noma Security Agent Risk Simulator - Quick Test")
    print("="*60)
    
    # Initialize components
    print("📊 Loading data...")
    data_loader = DataLoader()
    blue_manager = BlueAgentManager(data_loader)
    red_manager = RedAgentManager(data_loader)
    tool_router = ToolRouter()
    evaluator = SecurityEvaluator()
    
    # Get available agents
    agents = data_loader.load_agents()
    print(f"✅ Loaded {len(agents)} agents")
    
    # Run blue agent simulation
    print("\n🔵 Running Blue Agent Simulation...")
    blue_results = blue_manager.simulate_all_agents()
    
    # Route blue actions through tool router
    blue_actions = []
    for result in blue_results:
        for action in result["workflow"]:
            from models import ActionType, DataClass
            # Convert string to enum
            action_type = ActionType(action["action_type"]) if isinstance(action["action_type"], str) else action["action_type"]
            data_classes = [DataClass(dc) for dc in action.get("data_classes_detected", []) if isinstance(dc, str)] or action.get("data_classes_detected", [])
            
            routed_action = tool_router.route_action(
                action_type=action_type,
                action_name=action["action_name"],
                agent_id=action["agent_id"],
                agent_name=action["agent_name"],
                user_input=action["user_input"],
                destination_domain=action.get("destination_domain"),
                data_classes=data_classes
            )
            blue_actions.append(routed_action)
    
    print(f"✅ Blue agents completed {len(blue_actions)} actions")
    
    # Run red agent simulation
    print("\n🔴 Running Red Agent Simulation...")
    red_results = red_manager.simulate_all_behaviors()
    
    # Route red actions through tool router
    red_actions = []
    for result in red_results:
        for behavior_result in result["behavior_results"]:
            for action in behavior_result["workflow"]:
                from models import ActionType, DataClass
                # Convert string to enum
                action_type = ActionType(action["action_type"]) if isinstance(action["action_type"], str) else action["action_type"]
                data_classes = [DataClass(dc) for dc in action.get("data_classes_detected", []) if isinstance(dc, str)] or action.get("data_classes_detected", [])
                
                routed_action = tool_router.route_action(
                    action_type=action_type,
                    action_name=action["action_name"],
                    agent_id=action["agent_id"],
                    agent_name=action["agent_name"],
                    user_input=action["user_input"],
                    destination_domain=action.get("destination_domain"),
                    data_classes=data_classes,
                    metadata={
                        "risky_behavior": action.get("risky_behavior"),
                        "risk_indicators": action.get("risk_indicators", [])
                    }
                )
                red_actions.append(routed_action)
    
    print(f"✅ Red agents completed {len(red_actions)} actions")
    
    # Evaluate all actions
    print("\n🔍 Evaluating Security Findings...")
    all_actions = blue_actions + red_actions
    findings = evaluator.evaluate_actions(all_actions)
    
    # Generate summary
    print("\n📋 SIMULATION RESULTS")
    print("="*60)
    print(f"Total Actions: {len(all_actions)}")
    print(f"  - Blue Agent Actions: {len(blue_actions)}")
    print(f"  - Red Agent Actions: {len(red_actions)}")
    print(f"Total Findings: {len(findings)}")
    
    # Findings by severity
    severity_counts = {}
    for finding in findings:
        severity = finding.severity.value
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    print(f"\nFindings by Severity:")
    for severity, count in severity_counts.items():
        print(f"  - {severity.upper()}: {count}")
    
    # Top findings
    print(f"\n🔝 Top 5 Findings:")
    for i, finding in enumerate(findings[:5], 1):
        print(f"{i}. {finding.risk_type} ({finding.severity.value.upper()})")
        print(f"   Confidence: {finding.confidence:.2f}")
        print(f"   Action: {finding.action_id}")
        print(f"   Recommendation: {finding.recommendation}")
        print()
    
    # Export results
    results = {
        "simulation_timestamp": datetime.now().isoformat(),
        "total_actions": len(all_actions),
        "blue_actions": len(blue_actions),
        "red_actions": len(red_actions),
        "total_findings": len(findings),
        "findings_by_severity": severity_counts,
        "findings": [evaluator._finding_to_dict(f) for f in findings],
        "agent_statistics": {
            agent.agent_id: tool_router.get_agent_statistics(agent.agent_id)
            for agent in agents
        }
    }
    
    # Save results
    with open("simulation_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"💾 Results saved to simulation_results.json")
    print("\n✅ Simulation completed successfully!")

if __name__ == "__main__":
    asyncio.run(run_quick_simulation())
