from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from models import SimulationResult, RiskFinding
from data_loader import DataLoader
from blue_agents import BlueAgentManager
from red_agents import RedAgentManager
from tool_router import ToolRouter
from evaluator import SecurityEvaluator
from config import HOST, PORT, DEBUG

app = FastAPI(
    title="Noma Security Agent Risk Simulator",
    description="Simulates customer agents to identify risky behaviors and generate security findings",
    version="1.0.0"
)

# Initialize components
data_loader = DataLoader()
blue_agent_manager = BlueAgentManager(data_loader)
red_agent_manager = RedAgentManager(data_loader)
tool_router = ToolRouter()
evaluator = SecurityEvaluator()

# Store simulation results
simulation_results = {}

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Noma Security Agent Risk Simulator",
        "version": "1.0.0",
        "endpoints": {
            "simulate": "/simulate",
            "results": "/results/{simulation_id}",
            "agents": "/agents",
            "findings": "/findings",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/agents")
async def get_agents():
    """Get all available agents"""
    agents = data_loader.load_agents()
    return {
        "total_agents": len(agents),
        "agents": [
            {
                "agent_id": agent.agent_id,
                "agent_name": agent.agent_name,
                "purpose_summary": agent.purpose_summary,
                "created_at": agent.created_at.isoformat()
            }
            for agent in agents
        ]
    }

@app.post("/simulate")
async def run_simulation(
    background_tasks: BackgroundTasks,
    agent_ids: Optional[List[str]] = None,
    user_inputs: Optional[List[str]] = None,
    include_red_team: bool = True,
    max_actions_per_agent: int = 5
):
    """Run a complete simulation with blue and red agents"""
    simulation_id = f"sim_{uuid.uuid4().hex[:8]}"
    
    try:
        # Run simulation in background
        background_tasks.add_task(
            _run_simulation_task,
            simulation_id,
            agent_ids,
            user_inputs,
            include_red_team,
            max_actions_per_agent
        )
        
        return {
            "simulation_id": simulation_id,
            "status": "started",
            "message": "Simulation started in background. Use /results/{simulation_id} to check progress."
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start simulation: {str(e)}")

async def _run_simulation_task(
    simulation_id: str,
    agent_ids: Optional[List[str]],
    user_inputs: Optional[List[str]],
    include_red_team: bool,
    max_actions_per_agent: int
):
    """Background task to run the simulation"""
    try:
        # Initialize simulation result
        simulation_results[simulation_id] = {
            "status": "running",
            "started_at": datetime.now().isoformat(),
            "blue_agent_results": [],
            "red_agent_results": [],
            "findings": [],
            "error": None
        }
        
        # Run blue agent simulations
        blue_results = []
        if agent_ids:
            for agent_id in agent_ids:
                try:
                    agent = blue_agent_manager.get_agent_by_id(agent_id)
                    user_input = user_inputs[agent_ids.index(agent_id)] if user_inputs and len(user_inputs) > agent_ids.index(agent_id) else "Simulation task"
                    workflow = agent.simulate_workflow(user_input, max_actions_per_agent)
                    blue_results.append({
                        "agent_id": agent_id,
                        "workflow": workflow,
                        "total_actions": len(workflow)
                    })
                except ValueError:
                    continue
        else:
            # Run all blue agents
            blue_results = blue_agent_manager.simulate_all_agents(user_inputs)
        
        # Route blue agent actions through tool router
        blue_actions = []
        for result in blue_results:
            for action in result["workflow"]:
                routed_action = tool_router.route_action(
                    action_type=action["action_type"],
                    action_name=action["action_name"],
                    agent_id=action["agent_id"],
                    agent_name=action["agent_name"],
                    user_input=action["user_input"],
                    destination_domain=action.get("destination_domain"),
                    data_classes=action.get("data_classes_detected", [])
                )
                blue_actions.append(routed_action)
        
        # Run red agent simulations if requested
        red_results = []
        red_actions = []
        if include_red_team:
            if agent_ids:
                for agent_id in agent_ids:
                    try:
                        red_agent = red_agent_manager.get_agent_by_id(agent_id)
                        user_input = user_inputs[agent_ids.index(agent_id)] if user_inputs and len(user_inputs) > agent_ids.index(agent_id) else "Red team simulation"
                        
                        # Test each risky behavior
                        behavior_results = []
                        for behavior in ["bigger_exports", "scope_escalation", "approval_skipping"]:
                            workflow = red_agent.simulate_risky_workflow(user_input, behavior)
                            behavior_results.append({
                                "behavior": behavior,
                                "workflow": workflow
                            })
                            
                            # Route red agent actions
                            for action in workflow:
                                routed_action = tool_router.route_action(
                                    action_type=action["action_type"],
                                    action_name=action["action_name"],
                                    agent_id=action["agent_id"],
                                    agent_name=action["agent_name"],
                                    user_input=action["user_input"],
                                    destination_domain=action.get("destination_domain"),
                                    data_classes=action.get("data_classes_detected", []),
                                    metadata={"risky_behavior": behavior, "risk_indicators": action.get("risk_indicators", [])}
                                )
                                red_actions.append(routed_action)
                        
                        red_results.append({
                            "agent_id": agent_id,
                            "behavior_results": behavior_results
                        })
                    except ValueError:
                        continue
        
        # Evaluate all actions
        all_actions = blue_actions + red_actions
        findings = evaluator.evaluate_actions(all_actions)
        
        # Calculate overall risk score
        risk_score = _calculate_overall_risk_score(findings)
        
        # Generate recommendations
        recommendations = _generate_recommendations(findings)
        
        # Update simulation results
        simulation_results[simulation_id].update({
            "status": "completed",
            "completed_at": datetime.now().isoformat(),
            "blue_agent_results": blue_results,
            "red_agent_results": red_results,
            "findings": [evaluator._finding_to_dict(f) for f in findings],
            "risk_score": risk_score,
            "recommendations": recommendations,
            "total_actions": len(all_actions),
            "total_findings": len(findings)
        })
    
    except Exception as e:
        simulation_results[simulation_id].update({
            "status": "error",
            "error": str(e),
            "completed_at": datetime.now().isoformat()
        })

def _calculate_overall_risk_score(findings: List[RiskFinding]) -> float:
    """Calculate overall risk score from findings"""
    if not findings:
        return 0.0
    
    # Weight by severity and confidence
    weighted_scores = []
    for finding in findings:
        severity_weights = {"high": 1.0, "medium": 0.6, "low": 0.3}
        weight = severity_weights.get(finding.severity.value, 0.5)
        weighted_scores.append(weight * finding.confidence)
    
    return sum(weighted_scores) / len(weighted_scores) if weighted_scores else 0.0

def _generate_recommendations(findings: List[RiskFinding]) -> List[str]:
    """Generate high-level recommendations from findings"""
    recommendations = []
    
    # Group findings by type
    finding_types = {}
    for finding in findings:
        risk_type = finding.risk_type
        if risk_type not in finding_types:
            finding_types[risk_type] = []
        finding_types[risk_type].append(finding)
    
    # Generate recommendations for each type
    for risk_type, type_findings in finding_types.items():
        high_confidence = [f for f in type_findings if f.confidence > 0.8]
        if high_confidence:
            recommendations.append(f"High priority: Address {len(high_confidence)} instances of {risk_type}")
    
    # Add general recommendations
    if len(findings) > 10:
        recommendations.append("Consider implementing automated monitoring for high-volume risk patterns")
    
    high_severity = [f for f in findings if f.severity.value == "high"]
    if high_severity:
        recommendations.append(f"Immediate action required: {len(high_severity)} high-severity findings detected")
    
    return recommendations

@app.get("/results/{simulation_id}")
async def get_simulation_results(simulation_id: str):
    """Get results for a specific simulation"""
    if simulation_id not in simulation_results:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    return simulation_results[simulation_id]

@app.get("/findings")
async def get_findings(
    simulation_id: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 100
):
    """Get security findings, optionally filtered"""
    if simulation_id and simulation_id in simulation_results:
        findings = simulation_results[simulation_id].get("findings", [])
    else:
        findings = evaluator.get_findings_summary().get("findings", [])
    
    # Filter by severity
    if severity:
        findings = [f for f in findings if f.get("severity") == severity]
    
    # Limit results
    findings = findings[:limit]
    
    return {
        "total_findings": len(findings),
        "findings": findings
    }

@app.get("/action-log")
async def get_action_log(
    agent_id: Optional[str] = None,
    action_type: Optional[str] = None,
    limit: int = 100
):
    """Get action log from tool router"""
    log = tool_router.get_action_log(agent_id, action_type)
    return {
        "total_actions": len(log),
        "actions": log[-limit:] if log else []
    }

@app.get("/agent-stats/{agent_id}")
async def get_agent_statistics(agent_id: str):
    """Get statistics for a specific agent"""
    try:
        stats = tool_router.get_agent_statistics(agent_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Agent statistics not found: {str(e)}")

@app.delete("/simulations/{simulation_id}")
async def delete_simulation(simulation_id: str):
    """Delete a simulation and its results"""
    if simulation_id not in simulation_results:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    del simulation_results[simulation_id]
    return {"message": f"Simulation {simulation_id} deleted"}

@app.get("/simulations")
async def list_simulations():
    """List all simulations"""
    return {
        "total_simulations": len(simulation_results),
        "simulations": [
            {
                "simulation_id": sim_id,
                "status": data["status"],
                "started_at": data.get("started_at"),
                "completed_at": data.get("completed_at"),
                "total_findings": data.get("total_findings", 0)
            }
            for sim_id, data in simulation_results.items()
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT, debug=DEBUG)
