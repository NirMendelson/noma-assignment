#!/usr/bin/env python3
"""
Policy PDF Generator - Converts vulnerability analysis to PDF format
"""

import json
import os
from datetime import datetime
from typing import Dict, List
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

def generate_policy_pdf(analysis_file: str, output_file: str = None):
    """Generate PDF from vulnerability analysis"""
    
    # Load analysis results
    with open(analysis_file, 'r') as f:
        analysis_data = json.load(f)
    
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"vulnerability_analysis_report_{timestamp}.pdf"
    
    # Create PDF document
    doc = SimpleDocTemplate(output_file, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.darkred
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=12,
        spaceAfter=8,
        textColor=colors.darkgreen
    )
    
    # Build content
    story = []
    
    # Title
    story.append(Paragraph("Vulnerability Analysis Report", title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Analysis Summary
    story.append(Paragraph("Analysis Summary", heading_style))
    story.append(Paragraph(f"Total Episodes Analyzed: {analysis_data['total_episodes_analyzed']}", styles['Normal']))
    story.append(Paragraph(f"Total Scenarios Found: {analysis_data['total_scenarios_found']}", styles['Normal']))
    story.append(Paragraph(f"Unique Vulnerability Scenarios: {analysis_data['unique_vulnerability_scenarios']}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Vulnerability Scenarios by Agent
    story.append(Paragraph("Vulnerability Scenarios by Agent", heading_style))e 
    
    # Group scenarios by agent
    agent_scenarios = {}
    for scenario in analysis_data['vulnerability_scenarios']:
        agent_name = scenario.get('prospect_agent', 'Unknown Agent')
        if agent_name not in agent_scenarios:
            agent_scenarios[agent_name] = []
        agent_scenarios[agent_name].append(scenario)
    
    for agent_name, scenarios in agent_scenarios.items():
        story.append(Paragraph(f"<b>{agent_name}</b> ({len(scenarios)} scenarios)", subheading_style))
        
        for i, scenario in enumerate(scenarios, 1):
            # Clean up description to remove specific endpoints
            clean_description = clean_scenario_description(scenario['description'])
            clean_evidence = clean_scenario_evidence(scenario['evidence'])
            
            story.append(Paragraph(f"<b>Scenario {i}:</b> {clean_description}", styles['Normal']))
            story.append(Paragraph(f"<b>Risk Level:</b> {scenario['risk_level']}", styles['Normal']))
            story.append(Paragraph(f"<b>Business Impact:</b> {scenario['business_impact']}", styles['Normal']))
            story.append(Spacer(1, 10))
            
            # Add policy options
            story.append(Paragraph("<b>Policy Options:</b>", styles['Heading4']))
            
            # Generate policy options for this scenario
            policy_options = generate_scenario_policy_options(scenario)
            
            # Block option
            story.append(Paragraph("<b>Block:</b>", styles['Heading5']))
            story.append(Paragraph(policy_options['block'], styles['Normal']))
            story.append(Spacer(1, 5))
            
            # Sanitize option
            story.append(Paragraph("<b>Sanitize:</b>", styles['Heading5']))
            story.append(Paragraph(policy_options['sanitize'], styles['Normal']))
            story.append(Spacer(1, 5))
            
            # Allow option
            story.append(Paragraph("<b>Allow:</b>", styles['Heading5']))
            story.append(Paragraph(policy_options['allow'], styles['Normal']))
            story.append(Spacer(1, 5))
            
            # Recommended option
            story.append(Paragraph(f"<b>Recommended Option:</b> {policy_options['recommended']}", styles['Heading5']))
            story.append(Paragraph(f"<b>Rationale:</b> {policy_options['rationale']}", styles['Normal']))
            story.append(Spacer(1, 15))
    
    # Detailed Scenarios (if needed for reference)
    story.append(PageBreak())
    story.append(Paragraph("Detailed Scenario Reference", heading_style))
    story.append(Paragraph("This section provides additional technical details for security teams.", styles['Normal']))
    story.append(Spacer(1, 10))
    
    for i, scenario in enumerate(analysis_data['vulnerability_scenarios'], 1):
        clean_description = clean_scenario_description(scenario['description'])
        clean_evidence = clean_scenario_evidence(scenario['evidence'])
        
        story.append(Paragraph(f"<b>Scenario {i}: {scenario['scenario_type']}</b>", subheading_style))
        story.append(Paragraph(f"<b>Description:</b> {clean_description}", styles['Normal']))
        story.append(Paragraph(f"<b>Evidence:</b> {clean_evidence}", styles['Normal']))
        story.append(Paragraph(f"<b>Risk Level:</b> {scenario['risk_level']}", styles['Normal']))
        story.append(Paragraph(f"<b>Business Impact:</b> {scenario['business_impact']}", styles['Normal']))
        story.append(Paragraph(f"<b>Episode ID:</b> {scenario['episode_id']}", styles['Normal']))
        story.append(Paragraph(f"<b>Prospect Agent:</b> {scenario['prospect_agent']}", styles['Normal']))
        story.append(Spacer(1, 10))
    
    # Recommendations
    story.append(PageBreak())
    story.append(Paragraph("Security Recommendations", heading_style))
    
    story.append(Paragraph("Based on the vulnerability analysis, the following recommendations are suggested:", styles['Normal']))
    story.append(Spacer(1, 10))
    
    # Generate recommendations based on scenario types
    recommendations = generate_recommendations(scenario_types)
    for rec_type, rec_list in recommendations.items():
        story.append(Paragraph(f"<b>{rec_type}:</b>", styles['Heading4']))
        for rec in rec_list:
            story.append(Paragraph(f"• {rec}", styles['Normal']))
        story.append(Spacer(1, 10))
    
    # Build PDF
    doc.build(story)
    return output_file

def clean_scenario_description(description: str) -> str:
    """Remove specific endpoint names and make descriptions generic"""
    # Replace specific API endpoints with generic terms
    import re
    
    # Replace specific endpoints with generic terms
    description = re.sub(r'[a-zA-Z0-9.-]+\.walmart\.internal', 'internal API endpoint', description, flags=re.IGNORECASE)
    description = re.sub(r'[a-zA-Z0-9.-]+\.com', 'external service', description, flags=re.IGNORECASE)
    description = re.sub(r'[a-zA-Z0-9.-]+@[a-zA-Z0-9.-]+\.com', 'email address', description, flags=re.IGNORECASE)
    
    return description

def clean_scenario_evidence(evidence: str) -> str:
    """Remove specific endpoint names from evidence"""
    import re
    
    # Replace specific endpoints with generic terms
    evidence = re.sub(r'[a-zA-Z0-9.-]+\.walmart\.internal', 'internal API endpoint', evidence, flags=re.IGNORECASE)
    evidence = re.sub(r'[a-zA-Z0-9.-]+\.com', 'external service', evidence, flags=re.IGNORECASE)
    evidence = re.sub(r'[a-zA-Z0-9.-]+@[a-zA-Z0-9.-]+\.com', 'email address', evidence, flags=re.IGNORECASE)
    
    return evidence

def generate_scenario_policy_options(scenario: Dict) -> Dict[str, str]:
    """Generate policy options for a specific scenario"""
    scenario_type = scenario.get('scenario_type', 'UNKNOWN')
    risk_level = scenario.get('risk_level', 'Medium')
    business_impact = scenario.get('business_impact', '')
    
    # Base policy options based on scenario type
    if scenario_type == "API_ENDPOINT_DISCLOSURE":
        return {
            'block': "The agent workflow will be stopped when attempting to reveal internal API endpoint names. This prevents security breaches but may result in a poor user experience when users ask about technical details.",
            'sanitize': "The agent will continue to function but will automatically replace internal API endpoint names with generic placeholders (e.g., 'internal API endpoint') while maintaining the conversation flow.",
            'allow': "The agent will be allowed to mention internal API endpoints, but all such conversations will be logged and monitored for potential security violations.",
            'recommended': 'Block',
            'rationale': f"API endpoint disclosure is a {risk_level.lower()} risk that could lead to direct system compromise. The security impact outweighs the potential user experience impact."
        }
    
    elif scenario_type == "PII_DISCLOSURE":
        return {
            'block': "The agent workflow will be stopped when attempting to share customer personal information. This prevents data privacy violations but may limit the agent's ability to provide personalized service.",
            'sanitize': "The agent will continue to function but will automatically redact or replace personal information with generic placeholders (e.g., 'customer data') while maintaining service functionality.",
            'allow': "The agent will be allowed to share personal information, but all such interactions will be logged and monitored for compliance with data protection regulations.",
            'recommended': 'Block',
            'rationale': f"PII disclosure is a {risk_level.lower()} risk that could result in legal penalties and loss of customer trust. The privacy protection is critical and outweighs service limitations."
        }
    
    elif scenario_type == "AUTHORITY_ASSUMPTION_VULNERABILITY":
        return {
            'block': "The agent will be prevented from accepting any authority claims without proper verification. This prevents unauthorized access but may slow down legitimate administrative requests.",
            'sanitize': "The agent will continue to function but will require additional verification steps for authority-based requests, such as multi-factor authentication or supervisor approval.",
            'allow': "The agent will be allowed to accept authority claims, but all such interactions will be logged and monitored for potential security violations.",
            'recommended': 'Sanitize',
            'rationale': f"Authority assumption is a {risk_level.lower()} risk that requires balanced security. Sanitization provides protection while maintaining operational efficiency."
        }
    
    elif scenario_type == "COMPLIANCE_PRESSURE_VULNERABILITY":
        return {
            'block': "The agent will be prevented from yielding to compliance pressure tactics. This prevents manipulation but may make the agent appear less helpful in legitimate compliance scenarios.",
            'sanitize': "The agent will continue to function but will be trained to resist pressure tactics while still being helpful in legitimate compliance situations.",
            'allow': "The agent will be allowed to yield to pressure, but all such interactions will be logged and monitored for potential security violations.",
            'recommended': 'Sanitize',
            'rationale': f"Compliance pressure is a {risk_level.lower()} risk that requires balanced handling. Sanitization provides protection while maintaining helpfulness."
        }
    
    elif scenario_type == "DATA_EXPORT_VULNERABILITY":
        return {
            'block': "The agent will be prevented from offering to export sensitive data. This prevents data breaches but may limit legitimate data export functionality.",
            'sanitize': "The agent will continue to function but will require proper authorization and approval workflows before offering any data export capabilities.",
            'allow': "The agent will be allowed to offer data exports, but all such interactions will be logged and monitored for potential security violations.",
            'recommended': 'Sanitize',
            'rationale': f"Data export is a {risk_level.lower()} risk that requires controlled access. Sanitization provides security while maintaining necessary functionality."
        }
    
    else:
        # Generic policy options for unknown scenario types
        return {
            'block': f"The agent workflow will be stopped when this vulnerability is detected. This prevents the security risk but may impact user experience.",
            'sanitize': f"The agent will continue to function but will implement additional security controls to mitigate this {risk_level.lower()} risk while maintaining service functionality.",
            'allow': f"The agent will be allowed to continue, but all related interactions will be logged and monitored for potential security violations.",
            'recommended': 'Sanitize' if risk_level.lower() == 'medium' else 'Block',
            'rationale': f"This is a {risk_level.lower()} risk scenario. The recommended approach balances security with operational needs."
        }

def generate_recommendations(scenario_types: Dict[str, List[Dict]]) -> Dict[str, List[str]]:
    """Generate security recommendations based on scenario types"""
    recommendations = {
        "Immediate Actions": [],
        "Policy Updates": [],
        "Technical Controls": [],
        "Monitoring & Detection": []
    }
    
    for scenario_type, scenarios in scenario_types.items():
        if scenario_type == "API_ENDPOINT_DISCLOSURE":
            recommendations["Immediate Actions"].append("Review and audit all API endpoint references in agent responses")
            recommendations["Technical Controls"].append("Implement API endpoint filtering and redaction in agent responses")
            recommendations["Policy Updates"].append("Update agent training to avoid revealing internal API endpoints")
            
        elif scenario_type == "PII_DISCLOSURE":
            recommendations["Immediate Actions"].append("Conduct immediate audit of all PII handling in agent responses")
            recommendations["Technical Controls"].append("Implement PII detection and redaction systems")
            recommendations["Policy Updates"].append("Establish strict PII handling policies for AI agents")
            
        elif scenario_type == "AUTHORITY_ASSUMPTION_VULNERABILITY":
            recommendations["Policy Updates"].append("Implement multi-factor verification for authority claims")
            recommendations["Technical Controls"].append("Add authority verification checks before processing requests")
            
        elif scenario_type == "COMPLIANCE_PRESSURE_VULNERABILITY":
            recommendations["Policy Updates"].append("Train agents to resist compliance pressure tactics")
            recommendations["Monitoring & Detection"].append("Monitor for compliance pressure patterns in conversations")
            
        elif scenario_type == "DATA_EXPORT_VULNERABILITY":
            recommendations["Technical Controls"].append("Implement data export restrictions and approval workflows")
            recommendations["Policy Updates"].append("Establish data export authorization policies")
    
    # Add general recommendations
    recommendations["Monitoring & Detection"].append("Implement real-time conversation monitoring for security violations")
    recommendations["Policy Updates"].append("Conduct regular security training for AI agent development teams")
    recommendations["Technical Controls"].append("Implement automated security testing for agent responses")
    
    return recommendations

def main():
    """Main function to generate PDF"""
    
    # Find the most recent analysis file
    analysis_files = [f for f in os.listdir('.') if f.startswith('vulnerability_analysis_') and f.endswith('.json')]
    if not analysis_files:
        print("❌ No vulnerability analysis files found!")
        print("Run 'python analyze_vulnerabilities.py' first.")
        return
    
    # Get the most recent file
    latest_file = max(analysis_files, key=os.path.getctime)
    print(f"📄 Converting: {latest_file}")
    
    try:
        # Generate PDF
        output_file = generate_policy_pdf(latest_file)
        print(f"✅ PDF generated: {output_file}")
        
        # Display summary
        with open(latest_file, 'r') as f:
            analysis_data = json.load(f)
        
        print(f"\n📊 PDF Summary:")
        print(f"   Episodes analyzed: {analysis_data['total_episodes_analyzed']}")
        print(f"   Vulnerability scenarios: {analysis_data['unique_vulnerability_scenarios']}")
        print(f"   Report pages: Multiple (detailed analysis)")
        
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        print("Make sure you have reportlab installed: pip install reportlab")

if __name__ == "__main__":
    main()
