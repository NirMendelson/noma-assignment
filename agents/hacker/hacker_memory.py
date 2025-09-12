#!/usr/bin/env python3
"""
Hacker Memory System - Handles all memory-related functionality for the hacker agent
"""

import json
from typing import Dict, List, Any, Optional
from collections import deque
from datetime import datetime

class HackerMemory:
    """Hybrid memory system for hacker learning"""
    
    def __init__(self):
        self.session_memories = {}  # Current workflow memories
        self.persistent_memories = {}  # Cross-session learning
        self.confirmed_scenarios = []  # Successful attacks with evidence
    
    def remember_interaction(self, prospect_id: str, attack_type: str, success: bool, 
                           evidence: str, conversation_log: List[str]):
        """Remember an interaction with a prospect agent"""
        memory_entry = {
            'timestamp': datetime.now().isoformat(),
            'prospect_id': prospect_id,
            'attack_type': attack_type,
            'success': success,
            'evidence': evidence,
            'conversation_log': conversation_log
        }
        
        # Store in session memory
        if prospect_id not in self.session_memories:
            self.session_memories[prospect_id] = []
        self.session_memories[prospect_id].append(memory_entry)
        
        # If successful, add to confirmed scenarios
        if success:
            self.confirmed_scenarios.append(memory_entry)
    
    def get_prospect_memories(self, prospect_id: str) -> List[Dict]:
        """Get memories for a specific prospect"""
        return self.session_memories.get(prospect_id, [])
    
    def get_successful_attacks(self) -> List[Dict]:
        """Get all successful attacks"""
        return self.confirmed_scenarios
    
    def get_all_memories(self) -> List[Dict]:
        """Get all memories from all prospects"""
        all_memories = []
        for prospect_memories in self.session_memories.values():
            all_memories.extend(prospect_memories)
        return all_memories
    
    def export_memories(self) -> Dict[str, Any]:
        """Export memories for persistence"""
        return {
            'session_memories': self.session_memories,
            'persistent_memories': self.persistent_memories,
            'confirmed_scenarios': self.confirmed_scenarios,
            'export_timestamp': datetime.now().isoformat()
        }

class WorkingContext:
    """Rolling window of recent conversation exchanges"""
    
    def __init__(self, max_size: int = 7):
        self.contexts = {}  # prospect_id -> deque
        self.max_size = max_size
    
    def add_exchange(self, prospect_id: str, hacker_message: str, prospect_response: str):
        """Add a conversation exchange to working context"""
        if prospect_id not in self.contexts:
            self.contexts[prospect_id] = deque(maxlen=self.max_size)
        
        self.contexts[prospect_id].append({
            'hacker': hacker_message,
            'prospect': prospect_response,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_context(self, prospect_id: str) -> List[Dict]:
        """Get working context for a prospect"""
        if prospect_id not in self.contexts:
            return []
        return list(self.contexts[prospect_id])
    
    def get_latest_exchange(self, prospect_id: str) -> Optional[Dict]:
        """Get the most recent exchange for a prospect"""
        if prospect_id not in self.contexts or not self.contexts[prospect_id]:
            return None
        return self.contexts[prospect_id][-1]

class SemanticMemory:
    """Long-term semantic memory for discovered information"""
    
    def __init__(self):
        self.memories = {}  # prospect_id -> semantic data
    
    def initialize_prospect(self, prospect_id: str):
        """Initialize semantic memory for a new prospect"""
        if prospect_id not in self.memories:
            self.memories[prospect_id] = {
                'discovered_tools': [],
                'discovered_endpoints': [],
                'security_measures': [],
                'sensitive_data_types': [],
                'prospect_vulnerabilities': [],
                'successful_attack_vectors': [],
                'failed_attack_vectors': []
            }
    
    def update_discoveries(self, prospect_id: str, extracted_info: dict):
        """Update semantic memory with discovered information"""
        if prospect_id not in self.memories:
            self.initialize_prospect(prospect_id)
        
        # Update discovered tools
        if extracted_info.get('tools_mentioned'):
            for tool in extracted_info['tools_mentioned']:
                if tool not in self.memories[prospect_id]['discovered_tools']:
                    self.memories[prospect_id]['discovered_tools'].append(tool)
        
        # Update discovered endpoints
        if extracted_info.get('endpoints_mentioned'):
            for endpoint in extracted_info['endpoints_mentioned']:
                if endpoint not in self.memories[prospect_id]['discovered_endpoints']:
                    self.memories[prospect_id]['discovered_endpoints'].append(endpoint)
        
        # Update security measures
        if extracted_info.get('security_measures'):
            for measure in extracted_info['security_measures']:
                if measure not in self.memories[prospect_id]['security_measures']:
                    self.memories[prospect_id]['security_measures'].append(measure)
        
        # Update sensitive data types
        if extracted_info.get('sensitive_data_mentioned'):
            for data_type in extracted_info['sensitive_data_mentioned']:
                if data_type not in self.memories[prospect_id]['sensitive_data_types']:
                    self.memories[prospect_id]['sensitive_data_types'].append(data_type)
        
        # Update vulnerabilities
        if extracted_info.get('vulnerabilities_hinted'):
            for vuln in extracted_info['vulnerabilities_hinted']:
                if vuln not in self.memories[prospect_id]['prospect_vulnerabilities']:
                    self.memories[prospect_id]['prospect_vulnerabilities'].append(vuln)
    
    def add_attack_result(self, prospect_id: str, attack_type: str, success: bool, info_gained: str = ""):
        """Add attack result to semantic memory"""
        if prospect_id not in self.memories:
            self.initialize_prospect(prospect_id)
        
        attack_record = {
            'type': attack_type,
            'success': success,
            'info_gained': info_gained,
            'timestamp': datetime.now().isoformat()
        }
        
        if success:
            self.memories[prospect_id]['successful_attack_vectors'].append(attack_record)
        else:
            self.memories[prospect_id]['failed_attack_vectors'].append(attack_record)
    
    def get_memory(self, prospect_id: str) -> Dict[str, Any]:
        """Get semantic memory for a prospect"""
        return self.memories.get(prospect_id, {})
    
    def get_all_memories(self) -> Dict[str, Dict[str, Any]]:
        """Get all semantic memories"""
        return self.memories

class ProfileMemory:
    """Memory for prospect characteristics and behavior patterns"""
    
    def __init__(self):
        self.profiles = {}  # prospect_id -> profile data
    
    def initialize_prospect(self, prospect_id: str):
        """Initialize profile memory for a new prospect"""
        if prospect_id not in self.profiles:
            self.profiles[prospect_id] = {
                'willingness_level': 'unknown',
                'security_awareness': 'unknown',
                'helpful_tendencies': True,
                'defensive_triggers': [],
                'communication_style': 'unknown',
                'response_patterns': []
            }
    
    def update_profile(self, prospect_id: str, extracted_info: dict, prospect_response: str):
        """Update profile memory with prospect characteristics"""
        if prospect_id not in self.profiles:
            self.initialize_prospect(prospect_id)
        
        # Update willingness level
        if extracted_info.get('willingness_level'):
            self.profiles[prospect_id]['willingness_level'] = extracted_info['willingness_level']
        
        # Analyze response patterns
        response_length = len(prospect_response)
        helpful_indicators = ['happy to help', 'sure', 'absolutely', 'of course', 'definitely']
        defensive_indicators = ['sorry', 'can\'t', 'unable', 'restricted', 'policy', 'security']
        
        helpful_count = sum(1 for indicator in helpful_indicators if indicator in prospect_response.lower())
        defensive_count = sum(1 for indicator in defensive_indicators if indicator in prospect_response.lower())
        
        # Update communication style
        if response_length > 500:
            self.profiles[prospect_id]['communication_style'] = 'verbose'
        elif response_length < 100:
            self.profiles[prospect_id]['communication_style'] = 'concise'
        else:
            self.profiles[prospect_id]['communication_style'] = 'moderate'
        
        # Update helpful tendencies
        if helpful_count > defensive_count:
            self.profiles[prospect_id]['helpful_tendencies'] = True
        elif defensive_count > helpful_count:
            self.profiles[prospect_id]['helpful_tendencies'] = False
        
        # Track response patterns
        self.profiles[prospect_id]['response_patterns'].append({
            'length': response_length,
            'helpful_indicators': helpful_count,
            'defensive_indicators': defensive_count,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_profile(self, prospect_id: str) -> Dict[str, Any]:
        """Get profile memory for a prospect"""
        return self.profiles.get(prospect_id, {})
    
    def get_all_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Get all profile memories"""
        return self.profiles

class AttackTracking:
    """Track attack attempts and strategies per prospect"""
    
    def __init__(self):
        self.attempts = {}  # prospect_id -> strategy -> attempts/successes
    
    def track_attempt(self, prospect_id: str, strategy: str, success: bool):
        """Track an attack attempt"""
        if prospect_id not in self.attempts:
            self.attempts[prospect_id] = {}
        
        if strategy not in self.attempts[prospect_id]:
            self.attempts[prospect_id][strategy] = {"attempts": 0, "successes": 0}
        
        self.attempts[prospect_id][strategy]["attempts"] += 1
        if success:
            self.attempts[prospect_id][strategy]["successes"] += 1
    
    def should_switch_strategy(self, prospect_id: str, current_strategy: str) -> bool:
        """Check if we should switch strategies after failed attempts"""
        if prospect_id not in self.attempts:
            return False
        
        attempts = self.attempts[prospect_id].get(current_strategy, {})
        if attempts.get("attempts", 0) >= 3 and attempts.get("successes", 0) == 0:
            return True
        return False
    
    def get_attempts(self, prospect_id: str) -> Dict[str, Dict[str, int]]:
        """Get attack attempts for a prospect"""
        return self.attempts.get(prospect_id, {})
    
    def get_all_attempts(self) -> Dict[str, Dict[str, Dict[str, int]]]:
        """Get all attack attempts"""
        return self.attempts
