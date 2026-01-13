"""
LLM Utilities
Shared LLM helper functions used across the travel planner.
This replaces the previous BaseAgent abstract class with simpler utility functions.
"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# Load environment variables
load_dotenv()


def get_llm(
    model_name: str = "sonar",
    temperature: float = 0.7
) -> ChatOpenAI:
    """
    Get a configured LLM instance using Perplexity API.
    
    Args:
        model_name: Perplexity model to use (default: sonar)
        temperature: Creativity level (0=deterministic, 1=creative)
        
    Returns:
        Configured ChatOpenAI instance
    """
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise ValueError("PERPLEXITY_API_KEY not found in .env file!")
    
    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        openai_api_key=api_key,
        openai_api_base="https://api.perplexity.ai"
    )


async def think(system_prompt: str, user_message: str) -> str:
    """
    Send a message to the LLM and get a response.
    This is the "thinking" capability used by graph nodes.
    
    Args:
        system_prompt: The system instructions for the LLM
        user_message: The question or task for the LLM
        
    Returns:
        The LLM's response as a string
    """
    llm = get_llm()
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ]
    response = await llm.ainvoke(messages)
    return response.content


# ============================================
# TESTING
# ============================================

if __name__ == "__main__":
    import asyncio
    
    async def test_llm():
        print("=" * 60)
        print("TESTING LLM UTILITIES")
        print("=" * 60)
        
        try:
            # Test simple question
            print("\nTest 1: Simple Question")
            print("-" * 60)
            
            response = await think(
                system_prompt="You are a helpful travel assistant. Answer concisely.",
                user_message="What's the capital of Japan?"
            )
            print(f"Response: {response}")
            
            # Test travel question
            print("\nTest 2: Travel Question")
            print("-" * 60)
            
            response = await think(
                system_prompt="You are a travel expert. Give brief recommendations.",
                user_message="What are the top 3 things to do in Tokyo?"
            )
            print(f"Response: {response}")
            
            print("\n" + "=" * 60)
            print("ALL TESTS PASSED!")
            print("=" * 60)
            
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("\nTroubleshooting:")
            print("1. Check your .env file exists")
            print("2. Verify PERPLEXITY_API_KEY is set correctly")
    
    asyncio.run(test_llm())
