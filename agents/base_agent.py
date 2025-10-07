"""
Base Agent Class for Multi-Agent Healthcare System
Location: agents/base_agent.py

Provides common functionality for all agents:
- Standardized logging
- Input/output validation
- Error handling
- Timestamp management
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Callable
from datetime import datetime
import json


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.
    
    All agents must implement:
    - process(): Main processing method
    - _validate_input(): Input validation
    """
    
    def __init__(self, agent_name: str, log_callback: Optional[Callable] = None):
        """
        Initialize base agent.
        
        Args:
            agent_name: Name identifier for this agent
            log_callback: Optional function(agent_name, level, message) for logging
        """
        self.agent_name = agent_name
        self.log_callback = log_callback
        self.start_time = None
    
    @abstractmethod
    def process(self, input_data: Dict) -> Dict:
        """
        Main processing method - must be implemented by subclass.
        
        Args:
            input_data: Input from previous agent or coordinator
            
        Returns:
            Dict: Standardized output for next agent
        """
        pass
    
    @abstractmethod
    def _validate_input(self, input_data: Dict) -> None:
        """
        Validate input data - must be implemented by subclass.
        
        Args:
            input_data: Data to validate
            
        Raises:
            ValueError: If validation fails
        """
        pass
    
    def _log(self, level: str, message: str, metadata: Optional[Dict] = None) -> None:
        """
        Log message with optional metadata.
        
        Args:
            level: Log level (INFO, WARNING, ERROR, SUCCESS)
            message: Log message
            metadata: Optional additional data to log
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.agent_name,
            "level": level,
            "message": message
        }
        
        if metadata:
            log_entry["metadata"] = metadata
        
        if self.log_callback:
            self.log_callback(self.agent_name, level, message, metadata)
        else:
            # Fallback to console logging
            prefix = {
                "INFO": "ℹ️",
                "SUCCESS": "✅",
                "WARNING": "⚠️",
                "ERROR": "❌",
                "DEBUG": "🔍"
            }.get(level, "•")
            
            print(f"{prefix} [{level}] {self.agent_name}: {message}")
            if metadata:
                print(f"   Metadata: {json.dumps(metadata, indent=2)}")
    
    def _start_processing(self) -> None:
        """Mark processing start time."""
        self.start_time = datetime.now()
        self._log("INFO", f"{self.agent_name} started processing")
    
    def _end_processing(self, success: bool = True) -> None:
        """
        Mark processing end and log duration.
        
        Args:
            success: Whether processing was successful
        """
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
            level = "SUCCESS" if success else "ERROR"
            self._log(level, f"{self.agent_name} completed in {duration:.2f}s")
    
    def _create_output(self, data: Dict, status: str = "success") -> Dict:
        """
        Create standardized output format.
        
        Args:
            data: Output data from agent processing
            status: Processing status (success/error/warning)
            
        Returns:
            Dict: Standardized output with metadata
        """
        output = {
            **data,
            "agent": self.agent_name,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add processing duration if available
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
            output["processing_time_seconds"] = round(duration, 3)
        
        return output
    
    def _error_response(self, error_msg: str, exception: Optional[Exception] = None) -> Dict:
        """
        Create standardized error response.
        
        Args:
            error_msg: Human-readable error message
            exception: Optional exception object
            
        Returns:
            Dict: Error response in standard format
        """
        self._log("ERROR", f"Error in {self.agent_name}: {error_msg}")
        
        error_data = {
            "error": error_msg,
            "error_type": type(exception).__name__ if exception else "UnknownError",
            "agent": self.agent_name,
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }
        
        return error_data
    
    def _validate_required_fields(self, data: Dict, required_fields: list) -> None:
        """
        Helper to validate required fields exist in input data.
        
        Args:
            data: Data dictionary to validate
            required_fields: List of required field names
            
        Raises:
            ValueError: If any required field is missing
        """
        missing = [field for field in required_fields if field not in data]
        
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
    
    def safe_process(self, input_data: Dict) -> Dict:
        """
        Wrapper around process() with error handling.
        
        Use this method for production to ensure errors don't crash the system.
        
        Args:
            input_data: Input from previous agent
            
        Returns:
            Dict: Either successful output or error response
        """
        try:
            self._start_processing()
            result = self.process(input_data)
            self._end_processing(success=True)
            return result
        except Exception as e:
            self._end_processing(success=False)
            return self._error_response(str(e), e)
    
    def get_agent_info(self) -> Dict:
        """
        Get agent metadata and capabilities.
        
        Returns:
            Dict: Agent information
        """
        return {
            "agent_name": self.agent_name,
            "agent_type": self.__class__.__name__,
            "capabilities": self._get_capabilities(),
            "status": "ready"
        }
    
    def _get_capabilities(self) -> list:
        """
        Override in subclasses to describe agent capabilities.
        
        Returns:
            List of capability strings
        """
        return ["process_data"]


# ============= UTILITY FUNCTIONS =============

def create_agent_chain(agents: list) -> Callable:
    """
    Create a processing chain from multiple agents.
    
    Args:
        agents: List of BaseAgent instances
        
    Returns:
        Function that processes data through all agents sequentially
    """
    def chain_process(initial_input: Dict) -> Dict:
        current_data = initial_input
        results = []
        
        for agent in agents:
            result = agent.safe_process(current_data)
            results.append(result)
            
            # Stop chain if error occurred
            if result.get("status") == "error":
                return {
                    "status": "chain_failed",
                    "failed_at": agent.agent_name,
                    "results": results
                }
            
            # Pass output to next agent
            current_data = result
        
        return {
            "status": "chain_completed",
            "final_output": current_data,
            "all_results": results
        }
    
    return chain_process


def validate_agent_output(output: Dict, required_keys: list) -> bool:
    """
    Validate agent output has required structure.
    
    Args:
        output: Agent output dictionary
        required_keys: List of required keys
        
    Returns:
        bool: True if valid, False otherwise
    """
    return all(key in output for key in required_keys)


# ============= EXAMPLE AGENT IMPLEMENTATION =============

class ExampleAgent(BaseAgent):
    """
    Example implementation of BaseAgent.
    Shows how to properly inherit and implement required methods.
    """
    
    def __init__(self, log_callback=None):
        super().__init__("ExampleAgent", log_callback)
        self.config = {}
    
    def process(self, input_data: Dict) -> Dict:
        """Process input data."""
        self._validate_input(input_data)
        
        # Your processing logic here
        result = {
            "processed": True,
            "input_received": input_data
        }
        
        return self._create_output(result)
    
    def _validate_input(self, input_data: Dict) -> None:
        """Validate input structure."""
        self._validate_required_fields(input_data, ["required_field"])
    
    def _get_capabilities(self) -> list:
        """List agent capabilities."""
        return ["example_processing", "data_validation"]


# ============= TESTING =============

if __name__ == "__main__":
    print("=" * 60)
    print("BASE AGENT - Testing & Demo")
    print("=" * 60)
    
    # Test ExampleAgent
    agent = ExampleAgent()
    
    print("\n1. Testing valid input:")
    valid_input = {"required_field": "test_value"}
    result = agent.safe_process(valid_input)
    print(f"   Status: {result.get('status')}")
    print(f"   Agent: {result.get('agent')}")
    
    print("\n2. Testing invalid input (missing field):")
    invalid_input = {"wrong_field": "value"}
    result = agent.safe_process(invalid_input)
    print(f"   Status: {result.get('status')}")
    print(f"   Error: {result.get('error')}")
    
    print("\n3. Agent info:")
    info = agent.get_agent_info()
    print(f"   Name: {info['agent_name']}")
    print(f"   Type: {info['agent_type']}")
    print(f"   Capabilities: {info['capabilities']}")
    
    print("\n4. Testing agent chain:")
    agent1 = ExampleAgent()
    agent2 = ExampleAgent()
    
    chain = create_agent_chain([agent1, agent2])
    chain_result = chain(valid_input)
    print(f"   Chain status: {chain_result['status']}")
    print(f"   Number of steps: {len(chain_result.get('all_results', []))}")
    
    print("\n" + "=" * 60)
    print("✅ Base Agent class ready for production use")
    print("=" * 60)