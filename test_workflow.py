#!/usr/bin/env python3
"""
Test the WorkflowManager
"""

import asyncio
from workflow_manager import WorkflowManager

async def test_workflow():
    """Test the workflow manager"""
    print("🧪 Testing WorkflowManager")
    print("=" * 40)
    
    # Create workflow manager
    manager = WorkflowManager(data_source="walmart_data", max_rounds=10)  # 10 rounds for testing
    
    try:
        # Run full workflow
        results = await manager.run_full_workflow()
        
        print("\n✅ Workflow test completed successfully!")
        print(f"📊 Results summary:")
        print(f"   - Agents: {len(results['prospect_agents'])}")
        print(f"   - Attack Goals: {len(results['attack_goals'])}")
        print(f"   - Conversations: {len(results['conversations'])}")
        print(f"   - Vulnerabilities: {len(results['vulnerabilities'])}")
        
        return results
        
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_workflow())
