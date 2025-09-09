#!/usr/bin/env python3
"""
LLM-Powered Policy PDF Generator - Uses Policy Generator Agent output to create PDF
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

def generate_policy_pdf_llm(analysis_file: str, output_file: str = None):
    """Generate PDF from LLM-powered policy analysis"""
    
    # Load policy analysis results
    with open(analysis_file, 'r') as f:
        policy_data = json.load(f)
    
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"security_policy_report_{timestamp}.pdf"
    
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
    story.append(Paragraph("Security Policy Analysis Report", title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", heading_style))
    story.append(Paragraph(f"Total Scenarios Analyzed: {policy_data['total_scenarios_analyzed']}", styles['Normal']))
    story.append(Paragraph(f"Source Analysis: {policy_data['source_analysis_file']}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Policy Recommendations Summary
    story.append(Paragraph("Policy Recommendations Summary", heading_style))
    recommendations = policy_data['summary']['recommended_policies']
    story.append(Paragraph(f"Block: {recommendations['block']} scenarios", styles['Normal']))
    story.append(Paragraph(f"Sanitize: {recommendations['sanitize']} scenarios", styles['Normal']))
    story.append(Paragraph(f"Allow: {recommendations['allow']} scenarios", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Group scenarios by agent
    agent_scenarios = {}
    for analysis in policy_data['policy_analyses']:
        agent_name = analysis['original_scenario'].get('prospect_agent', 'Unknown Agent')
        if agent_name not in agent_scenarios:
            agent_scenarios[agent_name] = []
        agent_scenarios[agent_name].append(analysis)
    
    # Vulnerability Scenarios by Agent
    story.append(Paragraph("Vulnerability Scenarios by Agent", heading_style))
    
    for agent_name, analyses in agent_scenarios.items():
        story.append(Paragraph(f"<b>{agent_name}</b> ({len(analyses)} scenarios)", subheading_style))
        
        for i, analysis in enumerate(analyses, 1):
            scenario = analysis['scenario_context']
            policy = analysis['policy_analysis']
            
            story.append(Paragraph(f"<b>Scenario {i}:</b> {scenario['description']}", styles['Normal']))
            story.append(Paragraph(f"<b>Risk Level:</b> {scenario['risk_level']}", styles['Normal']))
            story.append(Paragraph(f"<b>Business Impact:</b> {scenario['business_impact']}", styles['Normal']))
            story.append(Spacer(1, 10))
            
            # Policy Options
            story.append(Paragraph("<b>Policy Options:</b>", styles['Heading4']))
            
            # Block option
            story.append(Paragraph("<b>Block:</b>", styles['Heading5']))
            story.append(Paragraph(policy['block']['description'], styles['Normal']))
            story.append(Paragraph(f"<b>User Experience Impact:</b> {policy['block']['user_experience_impact']}", styles['Normal']))
            story.append(Paragraph(f"<b>Security Impact:</b> {policy['block']['security_impact']}", styles['Normal']))
            story.append(Spacer(1, 8))
            
            # Sanitize option
            story.append(Paragraph("<b>Sanitize:</b>", styles['Heading5']))
            story.append(Paragraph(policy['sanitize']['description'], styles['Normal']))
            story.append(Paragraph(f"<b>User Experience Impact:</b> {policy['sanitize']['user_experience_impact']}", styles['Normal']))
            story.append(Paragraph(f"<b>Security Impact:</b> {policy['sanitize']['security_impact']}", styles['Normal']))
            story.append(Spacer(1, 8))
            
            # Allow option
            story.append(Paragraph("<b>Allow:</b>", styles['Heading5']))
            story.append(Paragraph(policy['allow']['description'], styles['Normal']))
            story.append(Paragraph(f"<b>User Experience Impact:</b> {policy['allow']['user_experience_impact']}", styles['Normal']))
            story.append(Paragraph(f"<b>Security Impact:</b> {policy['allow']['security_impact']}", styles['Normal']))
            story.append(Spacer(1, 8))
            
            # Recommendation
            story.append(Paragraph(f"<b>Recommended Option:</b> {policy['recommended_option']}", styles['Heading5']))
            story.append(Paragraph(f"<b>Explanation:</b> {policy['explanation']}", styles['Normal']))
            story.append(Spacer(1, 15))
    
    # Implementation Guidelines
    story.append(PageBreak())
    story.append(Paragraph("Implementation Guidelines", heading_style))
    
    story.append(Paragraph("Based on the policy analysis, the following implementation guidelines are recommended:", styles['Normal']))
    story.append(Spacer(1, 10))
    
    # Generate implementation guidelines based on recommendations
    guidelines = generate_implementation_guidelines(policy_data['summary'])
    
    for guideline_type, guideline_list in guidelines.items():
        story.append(Paragraph(f"<b>{guideline_type}:</b>", styles['Heading4']))
        for guideline in guideline_list:
            story.append(Paragraph(f"• {guideline}", styles['Normal']))
        story.append(Spacer(1, 10))
    
    # Build PDF
    doc.build(story)
    return output_file

def generate_implementation_guidelines(summary: Dict) -> Dict[str, List[str]]:
    """Generate implementation guidelines based on policy analysis summary"""
    guidelines = {
        "Immediate Actions": [],
        "Policy Updates": [],
        "Technical Controls": [],
        "Monitoring & Detection": []
    }
    
    # Add guidelines based on recommended policies
    block_count = summary['recommended_policies']['block']
    sanitize_count = summary['recommended_policies']['sanitize']
    allow_count = summary['recommended_policies']['allow']
    
    if block_count > 0:
        guidelines["Immediate Actions"].append(f"Implement blocking controls for {block_count} high-risk scenarios")
        guidelines["Technical Controls"].append("Deploy workflow interruption mechanisms for blocked scenarios")
    
    if sanitize_count > 0:
        guidelines["Technical Controls"].append(f"Implement content filtering and redaction for {sanitize_count} scenarios")
        guidelines["Policy Updates"].append("Establish content sanitization policies and procedures")
    
    if allow_count > 0:
        guidelines["Monitoring & Detection"].append(f"Deploy comprehensive monitoring for {allow_count} allowed scenarios")
        guidelines["Technical Controls"].append("Implement real-time alerting and logging systems")
    
    # Add general guidelines
    guidelines["Policy Updates"].append("Conduct regular security training for AI agent development teams")
    guidelines["Monitoring & Detection"].append("Implement automated security testing for agent responses")
    guidelines["Technical Controls"].append("Establish regular security review and update procedures")
    
    return guidelines

def main():
    """Main function to generate PDF"""
    
    # Find the most recent policy analysis file
    analysis_files = [f for f in os.listdir('.') if f.startswith('policy_analysis_') and f.endswith('.json')]
    if not analysis_files:
        print("❌ No policy analysis files found!")
        print("Run 'python generate_policy_analysis.py' first.")
        return
    
    # Get the most recent file
    latest_file = max(analysis_files, key=os.path.getctime)
    print(f"📄 Converting: {latest_file}")
    
    try:
        # Generate PDF
        output_file = generate_policy_pdf_llm(latest_file)
        print(f"✅ PDF generated: {output_file}")
        
        # Display summary
        with open(latest_file, 'r') as f:
            policy_data = json.load(f)
        
        print(f"\n📊 PDF Summary:")
        print(f"   Scenarios analyzed: {policy_data['total_scenarios_analyzed']}")
        print(f"   Agents covered: {len(policy_data['summary']['scenarios_by_agent'])}")
        print(f"   Report pages: Multiple (detailed policy analysis)")
        
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        print("Make sure you have reportlab installed: pip install reportlab")

if __name__ == "__main__":
    main()
