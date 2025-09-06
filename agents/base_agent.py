#!/usr/bin/env python3
"""
Base LangChain agent class for both Walmart and customer agents
"""

from typing import List, Dict, Any, Optional
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_core.tools import BaseTool
from langchain_xai import ChatXAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.agents import AgentAction, AgentFinish
import json

class SecurityCallbackHandler(BaseCallbackHandler):
    """Monitor agent actions for security violations"""
    
    def __init__(self):
        self.security_violations = []
        self.tool_usage = []
    
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs) -> None:
        """Called when a tool starts running"""
        tool_name = serialized.get("name", "unknown")
        self.tool_usage.append({
            "tool": tool_name,
            "input": input_str,
            "timestamp": kwargs.get("timestamp")
        })
        
        # Check for risky tools
        risky_tools = ["access_admin_panel", "export_data", "delete_data", "modify_permissions"]
        if tool_name in risky_tools:
            self.security_violations.append({
                "type": "risky_tool_usage",
                "tool": tool_name,
                "input": input_str,
                "severity": "HIGH"
            })
    
    def on_agent_action(self, action: AgentAction, **kwargs) -> None:
        """Called when agent takes an action"""
        if action.tool in ["access_admin_panel", "export_data"]:
            self.security_violations.append({
                "type": "admin_action_attempt",
                "tool": action.tool,
                "input": action.tool_input,
                "severity": "CRITICAL"
            })

class BaseAgent:
    """Base class for all agents in the Noma Security platform"""
    
    def __init__(
        self, 
        name: str, 
        role: str,
        system_prompt: str,
        tools: List[BaseTool],
        model: str = "grok-3-mini",
        temperature: float = 0.1
    ):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.tools = tools
        self.llm = ChatXAI(
            model=model,
            temperature=temperature
        )
        self.security_monitor = SecurityCallbackHandler()
        self.agent_executor = self._create_agent()
        self.conversation_history = []
    
    def _create_agent(self) -> AgentExecutor:
        """Create the LangChain agent executor"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("user", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])
        
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            callbacks=[self.security_monitor],
            verbose=False,
            return_intermediate_steps=True
        )
    
    def process_message(self, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process a message and return response with security analysis"""
        try:
            # Add context if provided
            full_input = message
            if context:
                full_input = f"Context: {json.dumps(context)}\n\nMessage: {message}"
            
            # Process with agent
            response = self.agent_executor.invoke({"input": full_input})
            
            # Record conversation
            self.conversation_history.append({
                "input": message,
                "output": response["output"],
                "intermediate_steps": response.get("intermediate_steps", []),
                "security_violations": self.security_monitor.security_violations.copy()
            })
            
            return {
                "agent_name": self.name,
                "response": response["output"],
                "tools_used": [step[0].tool for step in response.get("intermediate_steps", [])],
                "security_violations": self.security_monitor.security_violations.copy(),
                "success": True
            }
            
        except Exception as e:
            return {
                "agent_name": self.name,
                "response": f"Error: {str(e)}",
                "tools_used": [],
                "security_violations": [],
                "success": False,
                "error": str(e)
            }
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get summary of security violations for this agent"""
        return {
            "agent_name": self.name,
            "total_violations": len(self.security_monitor.security_violations),
            "violations": self.security_monitor.security_violations,
            "tools_used": [usage["tool"] for usage in self.security_monitor.tool_usage],
            "conversation_count": len(self.conversation_history)
        }
    
    def reset_security_monitor(self):
        """Reset security monitoring for new conversation"""
        self.security_monitor = SecurityCallbackHandler()
        self.conversation_history = []
    
    async def respond_to_message(self, message: str) -> str:
        """Respond to a message from a customer"""
        try:
            # Add customer message to history
            self.conversation_history.append({
                "role": "user",
                "content": message
            })
            
            # Get response from agent
            response = await self.agent_executor.ainvoke({
                "input": message
            })
            
            # Extract the response text
            if isinstance(response, dict) and 'output' in response:
                response_text = response['output']
            else:
                response_text = str(response)
            
            # Add agent response to history
            self.conversation_history.append({
                "role": "assistant", 
                "content": response_text
            })
            
            return response_text
            
        except Exception as e:
            error_msg = f"I apologize, but I encountered an error: {str(e)}"
            self.conversation_history.append({
                "role": "assistant",
                "content": error_msg
            })
            return error_msg
