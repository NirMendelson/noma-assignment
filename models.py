from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class SeverityLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class ActionType(str, Enum):
    RETRIEVAL = "retrieval"
    TOOL = "tool"

class RunStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    RUNNING = "running"

class DataClass(str, Enum):
    PII = "PII"
    PHI = "PHI"
    CONFIDENTIAL = "Confidential"
    SECRETS = "Secrets"

class Agent(BaseModel):
    agent_id: str
    agent_name: str
    purpose_summary: str
    created_at: datetime

class Action(BaseModel):
    action_id: str
    run_id: str
    action_type: ActionType
    action_name: str
    started_at: datetime
    ended_at: datetime
    success: bool
    destination_domain: Optional[str] = None
    data_classes_detected_json: List[DataClass] = []

class Run(BaseModel):
    run_id: str
    agent_id: str
    started_at: datetime
    ended_at: datetime
    status: RunStatus
    user_input_summary: str

class MonitoringScenario(BaseModel):
    scenario_id: str
    action_id: str
    vuln_type: str
    severity: SeverityLevel
    recommended_option: str

class SimulationResult(BaseModel):
    simulation_id: str
    timestamp: datetime
    blue_agent_results: List[Dict[str, Any]]
    red_agent_results: List[Dict[str, Any]]
    findings: List[Dict[str, Any]]
    risk_score: float
    recommendations: List[str]

class RiskFinding(BaseModel):
    finding_id: str
    action_id: str
    risk_type: str
    severity: SeverityLevel
    description: str
    evidence: Dict[str, Any]
    recommendation: str
    confidence: float
