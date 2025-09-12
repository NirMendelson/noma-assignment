#!/usr/bin/env python3
"""
Policy PDF Generator - Creates PDF from policy analysis JSON
"""

import json
import os
from datetime import datetime
from typing import Dict, List
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

def generate_policy_pdf_from_analysis(analysis_file: str, output_file: str = None):
    """Generate PDF from policy analysis JSON"""
    
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
        spaceAfter=10,
        textColor=colors.darkblue
    )
    
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceBefore=0,
        spaceAfter=15,
        textColor=colors.black
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=10,
        spaceAfter=8,
        textColor=colors.darkred
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=12,
        spaceBefore=5,
        spaceAfter=5,
        textColor=colors.darkgreen
    )
    
    policy_option_style = ParagraphStyle(
        'PolicyOption',
        parent=styles['Heading6'],
        fontSize=11,
        spaceBefore=5,
        spaceAfter=3,
        textColor=colors.darkblue
    )
    
    # Build content
    story = []
    
    # Title
    story.append(Paragraph("Tradeoff Policy - Noma Security", title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", date_style))
    
    # Group scenarios by agent
    agent_scenarios = {}
    for analysis in policy_data['policy_analyses']:
        prospect_agent = analysis['original_scenario'].get('prospect_agent', 'Unknown Agent')
        
        # Handle both string and dict formats for prospect_agent
        if isinstance(prospect_agent, dict):
            agent_name = prospect_agent.get('name', prospect_agent.get('agent_id', 'Unknown Agent'))
        else:
            agent_name = str(prospect_agent)
        
        if agent_name not in agent_scenarios:
            agent_scenarios[agent_name] = []
        agent_scenarios[agent_name].append(analysis)
    
    # Vulnerability Scenarios by Agent
    story.append(Paragraph("Vulnerability Scenarios by Agent", heading_style))
    
    for agent_name, analyses in agent_scenarios.items():
        story.append(Paragraph(f"<b>{agent_name}</b>", subheading_style))
        
        # Individual Scenarios
        for i, analysis in enumerate(analyses, 1):
            scenario = analysis['scenario_context']
            policy = analysis['policy_analysis']
            
            story.append(Paragraph(f"<b>Scenario {i}: {scenario['scenario_type']}</b>", styles['Heading4']))
            story.append(Paragraph(f"<b>Description:</b> {scenario['description']}", styles['Normal']))
            story.append(Paragraph(f"<b>Risk Level:</b> {scenario['risk_level']}", styles['Normal']))
            story.append(Paragraph(f"<b>Business Impact:</b> {scenario['business_impact']}", styles['Normal']))
            story.append(Spacer(1, 10))
            
            # Policy Options
            story.append(Paragraph("<b>Policy Options:</b>", styles['Heading5']))
            
            # Block option
            story.append(Paragraph("<b>Block:</b>", policy_option_style))
            story.append(Paragraph(f"<b>Description:</b> {policy['block']['description']}", styles['Normal']))
            story.append(Paragraph(f"<b>User Experience Impact:</b> {policy['block']['user_experience_impact']}", styles['Normal']))
            story.append(Paragraph(f"<b>Security Impact:</b> {policy['block']['security_impact']}", styles['Normal']))
            story.append(Spacer(1, 6))
            
            # Sanitize option
            story.append(Paragraph("<b>Sanitize:</b>", policy_option_style))
            story.append(Paragraph(f"<b>Description:</b> {policy['sanitize']['description']}", styles['Normal']))
            story.append(Paragraph(f"<b>User Experience Impact:</b> {policy['sanitize']['user_experience_impact']}", styles['Normal']))
            story.append(Paragraph(f"<b>Security Impact:</b> {policy['sanitize']['security_impact']}", styles['Normal']))
            story.append(Spacer(1, 6))
            
            # Allow option
            story.append(Paragraph("<b>Allow:</b>", policy_option_style))
            story.append(Paragraph(f"<b>Description:</b> {policy['allow']['description']}", styles['Normal']))
            story.append(Paragraph(f"<b>User Experience Impact:</b> {policy['allow']['user_experience_impact']}", styles['Normal']))
            story.append(Paragraph(f"<b>Security Impact:</b> {policy['allow']['security_impact']}", styles['Normal']))
            story.append(Spacer(1, 6))
            
            # Recommendation
            story.append(Paragraph(f"<b>Recommended Option:</b> {policy['recommended_option']}", policy_option_style))
            story.append(Paragraph(f"<b>Explanation:</b> {policy['explanation']}", styles['Normal']))
            story.append(Spacer(1, 12))
    
    
    
    
    # Build PDF
    doc.build(story)
    return output_file

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
        output_file = generate_policy_pdf_from_analysis(latest_file)
        print(f"✅ PDF generated: {output_file}")
        
        # Display summary
        with open(latest_file, 'r') as f:
            policy_data = json.load(f)
        
        print(f"\n📊 PDF Summary:")
        print(f"   Scenarios analyzed: {policy_data['total_scenarios_analyzed']}")
        print(f"   Agents covered: {len(set(a['original_scenario']['prospect_agent'] for a in policy_data['policy_analyses']))}")
        print(f"   Report pages: Multiple (detailed policy analysis)")
        
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        print("Make sure you have reportlab installed: pip install reportlab")

if __name__ == "__main__":
    main()
