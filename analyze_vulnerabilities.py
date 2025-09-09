#!/usr/bin/env python3
"""
Vulnerability Analysis Runner - Analyzes hacker simulation results and generates policy draft
"""

import asyncio
import json
import os
from datetime import datetime
from agents.vulnerability_analyzer import get_vulnerability_analyzer

async def main():
    """Run vulnerability analysis on simulation results"""
    
    print("🔍 Vulnerability Analysis Starting...")
    print("=" * 50)
    
    # Find the most recent simulation results file
    json_files = [f for f in os.listdir('.') if f.startswith('hacker_simulation_results_') and f.endswith('.json')]
    if not json_files:
        print("❌ No simulation results found!")
        return
    
    # Get the most recent file
    latest_file = max(json_files, key=os.path.getctime)
    print(f"📄 Analyzing: {latest_file}")
    
    # Initialize vulnerability analyzer
    analyzer = get_vulnerability_analyzer()
    
    try:
        # Run analysis
        print("🔄 Analyzing vulnerabilities...")
        analysis_results = await analyzer.analyze_simulation_results(latest_file)
        
        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"vulnerability_analysis_{timestamp}.json"
        
        # Save results
        with open(output_file, 'w') as f:
            json.dump(analysis_results, f, indent=2)
        
        print(f"✅ Analysis complete! Results saved to: {output_file}")
        
        # Display summary
        print("\n📊 Analysis Summary:")
        print(f"   Episodes analyzed: {analysis_results['total_episodes_analyzed']}")
        print(f"   Total scenarios found: {analysis_results['total_scenarios_found']}")
        print(f"   Unique vulnerability scenarios: {analysis_results['unique_vulnerability_scenarios']}")
        
        # Display scenario breakdown by type
        scenario_types = {}
        for scenario in analysis_results['vulnerability_scenarios']:
            scenario_type = scenario.get('scenario_type', 'Unknown')
            scenario_types[scenario_type] = scenario_types.get(scenario_type, 0) + 1
        
        print(f"\n📋 Vulnerability Scenarios by Type:")
        for scenario_type, count in scenario_types.items():
            print(f"   {scenario_type}: {count} scenarios")
        
        print(f"\n🎯 Next Steps:")
        print(f"   1. Review the vulnerability scenarios in: {output_file}")
        print(f"   2. Use these scenarios as input for policy generation")
        print(f"   3. Create policy options for each scenario type")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
