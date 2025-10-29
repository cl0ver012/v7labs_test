"""
Simple Data Generator - Just one LLM call to generate JSON data
"""

import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage

# Load environment variables
load_dotenv()

def generate_data(
    description: str,
    num_rows: int = 20,
    model: str = "claude-3-haiku-20240307",
    temperature: float = 0.7
) -> Dict[str, Any]:
    """
    Generate data with a single LLM call.
    
    Args:
        description: What kind of data to generate
        num_rows: Approximate number of data points
        model: LLM model to use
        temperature: Creativity level
    
    Returns:
        Dictionary containing the generated data
    """
    
    try:
        # Initialize LLM
        llm = ChatAnthropic(model=model, temperature=temperature)
        
        # Simple, clear prompt
        system_prompt = """Generate data in JSON format. 
        Create realistic, varied data that would work well for visualization.
        Include appropriate column names and values.
        Output ONLY valid JSON, no explanations."""
        
        user_prompt = f"""Generate data for: {description}
        
        Requirements:
        - About {num_rows} data points
        - Include time/category dimension for x-axis
        - Include numeric values for y-axis
        - Add any other relevant fields
        - Make the data interesting with trends and variations
        
        Output format: JSON object with arrays for each field
        Example structure: {{"months": ["Jan", "Feb", ...], "sales": [100, 120, ...], "category": [...]}}"""
        
        # Make the LLM call
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = llm.invoke(messages)
        
        # Parse JSON from response
        content = response.content
        
        # Clean up if needed
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        data = json.loads(content.strip())
        return data
        
    except Exception as e:
        print(f"Data generation failed: {e}, using fallback")
        
        # Simple fallback data
        return {
            "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                      "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            "values": [100, 120, 115, 140, 135, 160, 
                      155, 180, 175, 190, 185, 200],
            "category": ["A"] * 6 + ["B"] * 6
        }


def generate_data_as_text(
    description: str,
    num_rows: int = 20,
    model: str = "claude-3-haiku-20240307",
    temperature: float = 0.7
) -> str:
    """
    Generate data and return as formatted text for prompts.
    
    Returns:
        String representation of the data
    """
    data = generate_data(description, num_rows, model, temperature)
    return json.dumps(data, indent=2)


# Example usage
if __name__ == "__main__":
    # Test the generator
    data = generate_data("monthly sales data for a retail store", num_rows=12)
    print("Generated data:")
    print(json.dumps(data, indent=2))
