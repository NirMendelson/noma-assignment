#!/usr/bin/env python3
"""
Complete End-to-End Workflow Runner
Runs the entire process: simulation → vulnerability analysis → policy generation → PDF
"""

import asyncio
from workflow_manager import run_full_workflow

async def main():
    """Run the complete end-to-end workflow"""
    print("🚀 Starting Complete End-to-End Workflow")
    print("=" * 60)
    print("This will run:")
    print("1. Data Analysis")
    print("2. Agent Creation") 
    print("3. Hacker Initialization")
    print("4. Attack Simulation")
    print("5. Vulnerability Analysis")
    print("6. Policy Generation")
    print("7. PDF Report Generation")
    print("=" * 60)
    
    try:
        # Run the complete workflow
        results = await run_full_workflow(data_source="walmart_data", max_episodes=5)
        
        print("\n🎉 Complete Workflow Finished Successfully!")
        print("=" * 60)
        print("📄 Generated Files:")
        
        if results.get('pdf_report'):
            print(f"   ✅ Final PDF Report: {results['pdf_report']}")
        
        print("\n🎯 Ready for Review!")
        print("The complete tradeoff policy PDF is ready for security team review.")
        
    except Exception as e:
        print(f"\n❌ Workflow failed: {e}")
        print("Check the error details above and try again.")
        raise

if __name__ == "__main__":
    asyncio.run(main())
