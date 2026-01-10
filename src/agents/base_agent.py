"""
Base Agent Class
This is the foundation for all AI agents in the travel planner.
Every specialized agent (Flight, Hotel, Activity, etc.) inherits from this.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class BaseAgent(ABC):
    """
    Base class for all agents in the travel planner.
    
    Each agent has:
    - A specific role/purpose
    - Access to an LLM for reasoning (Perplexity API)
    - Tools it can use
    - A method to execute its task
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        model_name: str = "sonar",
        temperature: float = 0.7
    ):
        """
        Initialize a new agent.
        
        Args:
            name: Agent's name (e.g., "Flight Agent")
            description: What this agent does
            model_name: Perplexity model to use
            temperature: Creativity level (0=deterministic, 1=creative)
        """
        self.name = name
        self.description = description
        
        # Initialize LLM with Perplexity API
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            raise ValueError("PERPLEXITY_API_KEY not found in .env file!")
        
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            openai_api_key=api_key,
            openai_api_base="https://api.perplexity.ai"
        )
        
        self.tools = []
    
    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """
        Define the agent's personality and instructions.
        Each child agent must implement this.
        """
        pass
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's main task.
        Each child agent must implement this.
        """
        pass
    
    async def think(self, user_message: str) -> str:
        """
        Send a message to the LLM and get a response.
        This is the agent's "thinking" capability.
        
        Args:
            user_message: The question or task for the LLM
            
        Returns:
            The LLM's response as a string
        """
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_message)
        ]
        
        response = await self.llm.ainvoke(messages)
        
        return response.content
    
    def add_tool(self, tool):
        """Add a tool that this agent can use"""
        self.tools.append(tool)
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}')>"


# ============================================
# TEST AGENT - For testing the base agent
# ============================================

class TestAgent(BaseAgent):
    """Simple test agent to verify the base agent works"""
    
    @property
    def system_prompt(self) -> str:
        return """You are a helpful travel assistant. 
        Answer questions about travel in a friendly and concise way.
        Keep responses short and informative."""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test execution - just asks a question"""
        question = input_data.get("question", "What is travel planning?")
        response = await self.think(question)
        return {"question": question, "answer": response}


# Test the base agent if run directly
if __name__ == "__main__":
    import asyncio
    
    async def test_base_agent():
        print("=" * 60)
        print("TESTING BASE AGENT WITH PERPLEXITY API")
        print("=" * 60)
        
        try:
            # Create a test agent
            agent = TestAgent(
                name="Test Travel Agent",
                description="A test agent to verify Perplexity API connection"
            )
            
            print("\n" + "=" * 60)
            print("TEST 1: Simple Question")
            print("=" * 60)
            
            result1 = await agent.execute({
                "question": "What's the capital of Japan?"
            })
            print(f"\nQuestion: {result1['question']}")
            print(f"Answer: {result1['answer']}")
            
            print("\n" + "=" * 60)
            print("TEST 2: Travel Question")
            print("=" * 60)
            
            result2 = await agent.execute({
                "question": "What are the top 3 things to do in Tokyo?"
            })
            print(f"\nQuestion: {result2['question']}")
            print(f"Answer: {result2['answer']}")
            
            print("\n" + "=" * 60)
            print("ALL TESTS PASSED!")
            print("=" * 60)
            print("\nPerplexity API is working!")
            print("Base Agent is ready to use.")
            
        except Exception as e:
            print("\n" + "=" * 60)
            print("ERROR OCCURRED")
            print("=" * 60)
            print(f"Error: {str(e)}")
            print("\nTroubleshooting:")
            print("1. Check your .env file exists")
            print("2. Verify PERPLEXITY_API_KEY is set correctly")
            print("3. Make sure you activated your virtual environment")
    
    # Run the test
    asyncio.run(test_base_agent())
