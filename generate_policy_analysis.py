#!/usr/bin/env python3
"""
Policy Analysis Generator - Uses Policy Generator Agent to create comprehensive policy analysis
"""

import asyncio
import json
import os
from datetime import datetime
from agents.policy_generator import get_policy_generator

async def main():
    """Generate policy analysis using the Policy Generator Agent"""
    
    print("🔍 Policy Analysis Generation Starting...")
    print("=" * 50)
    
    # Find the most recent vulnerability analysis file
    analysis_files = [f for f in os.listdir('.') if f.startswith('vulnerability_analysis_') and f.endswith('.json')]
    if not analysis_files:
        print("❌ No vulnerability analysis files found!")
        print("Run 'python analyze_vulnerabilities.py' first.")
        return
    
    # Get the most recent file
    latest_file = max(analysis_files, key=os.path.getctime)
    print(f"📄 Analyzing: {latest_file}")
    
    # Load vulnerability analysis results
    with open(latest_file, 'r') as f:
        analysis_data = json.load(f)
    
    vulnerability_scenarios = analysis_data.get('vulnerability_scenarios', [])
    print(f"📊 Found {len(vulnerability_scenarios)} vulnerability scenarios")
    
    # Initialize policy generator
    policy_generator = get_policy_generator()
    
    try:
        # Generate policy analysis for all scenarios
        print("🔄 Generating policy analysis...")
        policy_analyses = await policy_generator.generate_policy_analysis(vulnerability_scenarios)
        
        # Create comprehensive policy report
        policy_report = {
            'analysis_timestamp': datetime.now().isoformat(),
            'source_analysis_file': latest_file,
            'total_scenarios_analyzed': len(policy_analyses),
            'policy_analyses': policy_analyses,
            'summary': {
                'total_scenarios': len(vulnerability_scenarios),
                'scenarios_by_agent': {},
                'scenarios_by_type': {},
                'recommended_policies': {
                    'block': 0,
                    'sanitize': 0,
                    'allow': 0
                }
            }
        }
        
        # Generate summary statistics
        for analysis in policy_analyses:
            scenario = analysis['original_scenario']
            policy = analysis['policy_analysis']
            
            # Count by agent
            agent = scenario.get('prospect_agent', 'Unknown')
            if agent not in policy_report['summary']['scenarios_by_agent']:
                policy_report['summary']['scenarios_by_agent'][agent] = 0
            policy_report['summary']['scenarios_by_agent'][agent] += 1
            
            # Count by type
            scenario_type = scenario.get('scenario_type', 'Unknown')
            if scenario_type not in policy_report['summary']['scenarios_by_type']:
                policy_report['summary']['scenarios_by_type'][scenario_type] = 0
            policy_report['summary']['scenarios_by_type'][scenario_type] += 1
            
            # Count recommended policies
            recommended = policy.get('recommended_option', 'Unknown').lower()
            if recommended in policy_report['summary']['recommended_policies']:
                policy_report['summary']['recommended_policies'][recommended] += 1
        
        # Save policy analysis results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"policy_analysis_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(policy_report, f, indent=2)
        
        print(f"✅ Policy analysis complete! Results saved to: {output_file}")
        
        # Display summary
        print("\n📊 Policy Analysis Summary:")
        print(f"   Scenarios analyzed: {policy_report['total_scenarios_analyzed']}")
        
        print(f"\n📋 Scenarios by Agent:")
        for agent, count in policy_report['summary']['scenarios_by_agent'].items():
            print(f"   {agent}: {count} scenarios")
        
        print(f"\n📋 Scenarios by Type:")
        for scenario_type, count in policy_report['summary']['scenarios_by_type'].items():
            print(f"   {scenario_type}: {count} scenarios")
        
        print(f"\n🎯 Recommended Policies:")
        for policy_type, count in policy_report['summary']['recommended_policies'].items():
            print(f"   {policy_type.title()}: {count} scenarios")
        
        print(f"\n🎯 Next Steps:")
        print(f"   1. Review the policy analysis in: {output_file}")
        print(f"   2. Generate PDF report using: python generate_policy_pdf_llm.py")
        print(f"   3. Implement recommended security policies")
        
    except Exception as e:
        print(f"❌ Policy analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
