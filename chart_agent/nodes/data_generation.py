"""
Data Generation Node - Simplified version using JSON
"""

import os
import json
import logging
from typing import Dict, Any
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from chart_agent.models.agent_state import ChartAgentState, ProcessingStep

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


def analyze_request_node(state: ChartAgentState) -> Dict[str, Any]:
    """
    Analyze the user's chart request and prepare for data generation.
    """
    logger.info("Analyzing user request...")
    
    request = state["request"]
    
    # Ensure results directory exists
    os.makedirs("/home/ilya/Desktop/v7labs_test/results", exist_ok=True)
    
    # Build message about the analysis
    message_content = f"""Request Analysis Complete:
    - Chart Description: {request.chart_description}
    - Data Topic: {request.data_topic or 'Derived from description'}
    - Rows Requested: {request.data_rows or 20}
    - Output will be saved in results/ folder
    
    Proceeding to generate data..."""
    
    return {
        "messages": [
            HumanMessage(
                content=message_content,
                name="analyze_request"
            )
        ],
        "current_step": ProcessingStep.ANALYZE_REQUEST,
        "request": request
    }


def generate_data_node(state: ChartAgentState) -> Dict[str, Any]:
    """
    Generate synthetic data using simplified approach with JSON.
    """
    logger.info("Generating synthetic data...")
    
    request = state["request"]
    
    try:
        # Import the simple data generator
        import sys
        sys.path.append('/home/ilya/Desktop/v7labs_test')
        from simple_data_generator import generate_data
        
        # Create description for data generation
        description = f"{request.data_topic or request.chart_description}"
        rows = request.data_rows or 20
        
        # Generate data with single LLM call
        data = generate_data(
            description=description,
            num_rows=rows,
            temperature=0.7
        )
        
        logger.info(f"Generated data with {len(data)} fields")
        
        # Save as JSON for reference (optional)
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        json_filename = f"data_{timestamp}.json"
        json_path = f"/home/ilya/Desktop/v7labs_test/results/{json_filename}"
        
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return {
            "messages": [
                HumanMessage(
                    content=f"Generated data with {len(data)} fields and approximately {rows} data points. Saved to {json_filename}",
                    name="generate_data"
                )
            ],
            "generated_data": data,
            "data_source": json_path,
            "current_step": ProcessingStep.GENERATE_DATA
        }
        
    except Exception as e:
        logger.error(f"Error generating data: {e}")
        
        # Simple fallback data
        fallback_data = {
            "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "values": [100, 120, 115, 140, 135, 160]
        }
        
        return {
            "messages": [
                HumanMessage(
                    content=f"Using fallback data due to error: {str(e)}",
                    name="generate_data"
                )
            ],
            "generated_data": fallback_data,
            "data_source": None,
            "current_step": ProcessingStep.GENERATE_DATA,
            "warnings": [f"Data generation error: {str(e)}"]
        }