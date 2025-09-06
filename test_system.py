#!/usr/bin/env python3
"""
Simple test script to verify the Agent Risk Simulator works
"""

def test_imports():
    """Test that all modules can be imported"""
    try:
        from models import Agent, Action, Run, MonitoringScenario
        from data_loader import DataLoader
        from blue_agents import BlueAgentManager
        from red_agents import RedAgentManager
        from tool_router import ToolRouter
        from evaluator import SecurityEvaluator
        from config import HOST, PORT, DEBUG
        from azure_openai_config import get_openai_client, is_azure_configured
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_data_loading():
    """Test data loading functionality"""
    try:
        from data_loader import DataLoader
        loader = DataLoader()
        
        agents = loader.load_agents()
        actions = loader.load_actions()
        runs = loader.load_runs()
        scenarios = loader.load_monitoring_scenarios()
        
        print(f"✅ Data loaded: {len(agents)} agents, {len(actions)} actions, {len(runs)} runs, {len(scenarios)} scenarios")
        return True
    except Exception as e:
        print(f"❌ Data loading error: {e}")
        return False

def test_blue_agents():
    """Test blue agent functionality"""
    try:
        from data_loader import DataLoader
        from blue_agents import BlueAgentManager
        
        loader = DataLoader()
        manager = BlueAgentManager(loader)
        
        # Test getting an agent
        agents = loader.load_agents()
        if agents:
            agent = manager.get_agent_by_id(agents[0].agent_id)
            workflow = agent.simulate_workflow("Test workflow", 3)
            print(f"✅ Blue agent simulation: {len(workflow)} actions generated")
            return True
        else:
            print("❌ No agents found")
            return False
    except Exception as e:
        print(f"❌ Blue agent error: {e}")
        return False

def test_red_agents():
    """Test red agent functionality"""
    try:
        from data_loader import DataLoader
        from red_agents import RedAgentManager
        
        loader = DataLoader()
        manager = RedAgentManager(loader)
        
        # Test getting a red agent
        agents = loader.load_agents()
        if agents:
            red_agent = manager.get_agent_by_id(agents[0].agent_id)
            workflow = red_agent.simulate_risky_workflow("Test risky workflow", "bigger_exports")
            print(f"✅ Red agent simulation: {len(workflow)} risky actions generated")
            return True
        else:
            print("❌ No agents found")
            return False
    except Exception as e:
        print(f"❌ Red agent error: {e}")
        return False

def test_tool_router():
    """Test tool router functionality"""
    try:
        from tool_router import ToolRouter
        from models import ActionType, DataClass
        
        router = ToolRouter()
        
        # Test routing an action
        result = router.route_action(
            action_type=ActionType.TOOL,
            action_name="test_action",
            agent_id="test_agent",
            agent_name="Test Agent",
            user_input="Test input",
            destination_domain="test.walmart.internal",
            data_classes=[DataClass.PII]
        )
        
        print(f"✅ Tool router: Action {result['action_id']} routed successfully")
        return True
    except Exception as e:
        print(f"❌ Tool router error: {e}")
        return False

def test_evaluator():
    """Test evaluator functionality"""
    try:
        from evaluator import SecurityEvaluator
        from models import DataClass
        
        evaluator = SecurityEvaluator()
        
        # Test evaluating a risky action
        risky_action = {
            "action_id": "test_action",
            "action_type": "tool",
            "action_name": "send_pii_to_external_api",
            "destination_domain": "api.external.com",
            "data_classes_detected": [DataClass.PII.value],
            "scope": "external",
            "agent_id": "test_agent"
        }
        
        findings = evaluator.evaluate_actions([risky_action])
        print(f"✅ Evaluator: {len(findings)} findings generated")
        return True
    except Exception as e:
        print(f"❌ Evaluator error: {e}")
        return False

def test_azure_openai_config():
    """Test Azure OpenAI configuration"""
    try:
        from azure_openai_config import is_azure_configured, get_model_name, get_deployment_name
        
        is_azure = is_azure_configured()
        model_name = get_model_name()
        deployment_name = get_deployment_name()
        
        print(f"✅ Azure OpenAI config: Azure={is_azure}, Model={model_name}, Deployment={deployment_name}")
        return True
    except Exception as e:
        print(f"❌ Azure OpenAI config error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Noma Security Agent Risk Simulator")
    print("="*50)
    
    tests = [
        ("Import Test", test_imports),
        ("Data Loading Test", test_data_loading),
        ("Blue Agents Test", test_blue_agents),
        ("Red Agents Test", test_red_agents),
        ("Tool Router Test", test_tool_router),
        ("Evaluator Test", test_evaluator),
        ("Azure OpenAI Config Test", test_azure_openai_config)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
        print("\nNext steps:")
        print("1. Set your Azure OpenAI credentials in a .env file:")
        print("   - AZURE_OPENAI_ENDPOINT")
        print("   - AZURE_OPENAI_API_KEY")
        print("   - OPENAI_API_VERSION")
        print("   - GPT_4O_MINI_DEPLOYMENT")
        print("2. Run: python server.py")
        print("3. Visit: http://localhost:8000/docs")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
