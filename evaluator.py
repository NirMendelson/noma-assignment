import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from models import RiskFinding, SeverityLevel, DataClass
from config import RISK_THRESHOLDS

class SecurityEvaluator:
    """Applies Noma's security rules and data lineage checks"""
    
    def __init__(self):
        self.security_rules = self._initialize_security_rules()
        self.findings = []
    
    def _initialize_security_rules(self) -> List[Dict[str, Any]]:
        """Initialize security rules for evaluation"""
        return [
            {
                "rule_id": "rule_001",
                "name": "PII to External API",
                "description": "PII data sent to external APIs without proper controls",
                "severity": SeverityLevel.HIGH,
                "pattern": {
                    "data_classes": [DataClass.PII],
                    "scope": "external",
                    "action_types": ["tool"]
                },
                "weight": 0.9
            },
            {
                "rule_id": "rule_002", 
                "name": "PHI to Third Party",
                "description": "Health information sent to third-party services",
                "severity": SeverityLevel.HIGH,
                "pattern": {
                    "data_classes": [DataClass.PHI],
                    "scope": "external",
                    "action_types": ["tool"]
                },
                "weight": 0.95
            },
            {
                "rule_id": "rule_003",
                "name": "Secrets to Public Repository",
                "description": "Secrets or credentials exposed to public repositories",
                "severity": SeverityLevel.HIGH,
                "pattern": {
                    "data_classes": [DataClass.SECRETS],
                    "destination_contains": ["github.com", "gitlab.com"],
                    "action_types": ["tool"]
                },
                "weight": 1.0
            },
            {
                "rule_id": "rule_004",
                "name": "Confidential Data to Ads Partner",
                "description": "Confidential business data sent to advertising partners",
                "severity": SeverityLevel.MEDIUM,
                "pattern": {
                    "data_classes": [DataClass.CONFIDENTIAL],
                    "destination_contains": ["ads.", "partner"],
                    "action_types": ["tool"]
                },
                "weight": 0.7
            },
            {
                "rule_id": "rule_005",
                "name": "Vendor Financials to Unapproved Domain",
                "description": "Financial data sent to unapproved external domains",
                "severity": SeverityLevel.HIGH,
                "pattern": {
                    "action_contains": ["invoice", "billing", "financial"],
                    "destination_contains": ["vendor", "billing"],
                    "scope": "external",
                    "approved_domains": ["billing.vendorx.com"]
                },
                "weight": 0.85
            },
            {
                "rule_id": "rule_006",
                "name": "High Volume Data Export",
                "description": "Unusually large data exports detected",
                "severity": SeverityLevel.MEDIUM,
                "pattern": {
                    "action_contains": ["export", "bulk", "download"],
                    "volume_threshold": 1000
                },
                "weight": 0.6
            },
            {
                "rule_id": "rule_007",
                "name": "Privilege Escalation Attempt",
                "description": "Attempts to access restricted domains or escalate permissions",
                "severity": SeverityLevel.HIGH,
                "pattern": {
                    "destination_contains": ["admin", "executive", "secrets"],
                    "action_types": ["tool"]
                },
                "weight": 0.9
            },
            {
                "rule_id": "rule_008",
                "name": "Approval Workflow Bypass",
                "description": "Actions that skip required approval workflows",
                "severity": SeverityLevel.MEDIUM,
                "pattern": {
                    "skipped_approvals": True,
                    "bypass_controls": True
                },
                "weight": 0.7
            }
        ]
    
    def evaluate_actions(self, actions: List[Dict[str, Any]]) -> List[RiskFinding]:
        """Evaluate a list of actions against security rules"""
        findings = []
        
        for action in actions:
            action_findings = self._evaluate_single_action(action)
            findings.extend(action_findings)
        
        # Sort findings by severity and confidence
        findings.sort(key=lambda x: (x.severity.value, -x.confidence), reverse=True)
        
        self.findings.extend(findings)
        return findings
    
    def _evaluate_single_action(self, action: Dict[str, Any]) -> List[RiskFinding]:
        """Evaluate a single action against all security rules"""
        findings = []
        
        for rule in self.security_rules:
            if self._matches_rule(action, rule):
                finding = self._create_finding(action, rule)
                findings.append(finding)
        
        return findings
    
    def _matches_rule(self, action: Dict[str, Any], rule: Dict[str, Any]) -> bool:
        """Check if an action matches a security rule pattern"""
        pattern = rule["pattern"]
        
        # Check data classes
        if "data_classes" in pattern:
            action_data_classes = set(action.get("data_classes_detected", []))
            rule_data_classes = set([dc.value for dc in pattern["data_classes"]])
            if not action_data_classes.intersection(rule_data_classes):
                return False
        
        # Check scope
        if "scope" in pattern:
            if action.get("scope") != pattern["scope"]:
                return False
        
        # Check action types
        if "action_types" in pattern:
            if action.get("action_type") not in pattern["action_types"]:
                return False
        
        # Check destination domain patterns
        if "destination_contains" in pattern:
            destination = action.get("destination_domain", "")
            if not any(term in destination for term in pattern["destination_contains"]):
                return False
        
        # Check action name patterns
        if "action_contains" in pattern:
            action_name = action.get("action_name", "")
            if not any(term in action_name.lower() for term in pattern["action_contains"]):
                return False
        
        # Check approved domains (for negative rules)
        if "approved_domains" in pattern:
            destination = action.get("destination_domain", "")
            if destination in pattern["approved_domains"]:
                return False
        
        # Check volume thresholds
        if "volume_threshold" in pattern:
            # This would need to be calculated from actual data volume
            # For now, we'll use a simple heuristic
            if "bulk" in action.get("action_name", "").lower():
                # Simulate high volume
                pass
            else:
                return False
        
        # Check risk indicators
        if "skipped_approvals" in pattern:
            risk_indicators = action.get("risk_indicators", [])
            if not any("approval" in indicator.lower() for indicator in risk_indicators):
                return False
        
        if "bypass_controls" in pattern:
            risk_indicators = action.get("risk_indicators", [])
            if not any("bypass" in indicator.lower() or "circumvent" in indicator.lower() 
                      for indicator in risk_indicators):
                return False
        
        return True
    
    def _create_finding(self, action: Dict[str, Any], rule: Dict[str, Any]) -> RiskFinding:
        """Create a risk finding from an action and matched rule"""
        finding_id = f"finding_{uuid.uuid4().hex[:8]}"
        
        # Calculate confidence based on rule weight and action characteristics
        confidence = rule["weight"]
        
        # Adjust confidence based on data classes present
        data_classes = action.get("data_classes_detected", [])
        if DataClass.SECRETS.value in data_classes:
            confidence += 0.1
        if DataClass.PHI.value in data_classes:
            confidence += 0.05
        
        # Cap confidence at 1.0
        confidence = min(confidence, 1.0)
        
        # Generate evidence
        evidence = {
            "action_id": action.get("action_id"),
            "action_name": action.get("action_name"),
            "destination_domain": action.get("destination_domain"),
            "data_classes": data_classes,
            "scope": action.get("scope"),
            "timestamp": action.get("started_at"),
            "agent_id": action.get("agent_id"),
            "risk_indicators": action.get("risk_indicators", [])
        }
        
        # Generate recommendation
        recommendation = self._generate_recommendation(rule, action)
        
        return RiskFinding(
            finding_id=finding_id,
            action_id=action.get("action_id", ""),
            risk_type=rule["name"],
            severity=rule["severity"],
            description=rule["description"],
            evidence=evidence,
            recommendation=recommendation,
            confidence=confidence
        )
    
    def _generate_recommendation(self, rule: Dict[str, Any], action: Dict[str, Any]) -> str:
        """Generate a specific recommendation based on the rule and action"""
        rule_name = rule["name"]
        action_name = action.get("action_name", "")
        destination = action.get("destination_domain", "")
        
        if "PII to External API" in rule_name:
            return f"Block PII data from being sent to external API {destination}. Implement data sanitization or use approved internal APIs."
        
        elif "PHI to Third Party" in rule_name:
            return f"Immediately block health information from being sent to {destination}. This violates HIPAA compliance requirements."
        
        elif "Secrets to Public Repository" in rule_name:
            return f"Block action {action_name} from accessing public repositories. Use secure secret management instead."
        
        elif "Confidential Data to Ads Partner" in rule_name:
            return f"Sanitize confidential data before sending to {destination}. Remove sensitive business information."
        
        elif "Vendor Financials to Unapproved Domain" in rule_name:
            return f"Block financial data to unapproved domain {destination}. Use only approved vendor billing systems."
        
        elif "High Volume Data Export" in rule_name:
            return f"Implement data export limits and approval workflows for {action_name}. Monitor for unusual export patterns."
        
        elif "Privilege Escalation Attempt" in rule_name:
            return f"Block access to restricted domain {destination}. Implement proper access controls and monitoring."
        
        elif "Approval Workflow Bypass" in rule_name:
            return f"Enforce approval workflows for {action_name}. Implement mandatory approval gates."
        
        else:
            return f"Review and implement appropriate controls for {rule_name}."
    
    def get_findings_summary(self) -> Dict[str, Any]:
        """Get a summary of all findings"""
        if not self.findings:
            return {"total_findings": 0}
        
        # Count by severity
        severity_counts = {}
        for finding in self.findings:
            severity = finding.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Count by risk type
        risk_type_counts = {}
        for finding in self.findings:
            risk_type = finding.risk_type
            risk_type_counts[risk_type] = risk_type_counts.get(risk_type, 0) + 1
        
        # Calculate average confidence
        avg_confidence = sum(finding.confidence for finding in self.findings) / len(self.findings)
        
        # Get high-priority findings
        high_priority = [f for f in self.findings if f.severity == SeverityLevel.HIGH and f.confidence > 0.8]
        
        return {
            "total_findings": len(self.findings),
            "severity_breakdown": severity_counts,
            "risk_type_breakdown": risk_type_counts,
            "average_confidence": avg_confidence,
            "high_priority_findings": len(high_priority),
            "findings": [self._finding_to_dict(f) for f in self.findings]
        }
    
    def _finding_to_dict(self, finding: RiskFinding) -> Dict[str, Any]:
        """Convert a RiskFinding to dictionary"""
        return {
            "finding_id": finding.finding_id,
            "action_id": finding.action_id,
            "risk_type": finding.risk_type,
            "severity": finding.severity.value,
            "description": finding.description,
            "evidence": finding.evidence,
            "recommendation": finding.recommendation,
            "confidence": finding.confidence
        }
    
    def clear_findings(self):
        """Clear all findings"""
        self.findings = []
    
    def export_findings(self, format: str = "json") -> str:
        """Export findings in specified format"""
        import json
        
        if format.lower() == "json":
            return json.dumps(self.get_findings_summary(), indent=2, default=str)
        else:
            raise ValueError(f"Unsupported format: {format}")
