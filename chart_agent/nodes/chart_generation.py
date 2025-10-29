"""
Chart Generation Node - Simplified version
"""

import os
import sys
import datetime
import subprocess
import logging
from typing import Dict, Any
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from chart_agent.models.agent_state import ChartAgentState, ProcessingStep

# Load environment variables
load_dotenv()

# Configuration
RESULTS_PATH = os.getenv('RESULTS_PATH', os.path.join(os.getcwd(), 'results'))

logger = logging.getLogger(__name__)


def save_outputs_node(state: ChartAgentState) -> Dict[str, Any]:
    """
    Save generated code and execute it to create the chart.
    """
    logger.info("Saving outputs and generating chart...")
    
    request = state["request"]
    generated_code = state.get("generated_code", "")
    
    if not generated_code:
        return {
            "messages": [
                HumanMessage(
                    content="No code was generated to save",
                    name="save_outputs"
                )
            ],
            "current_step": ProcessingStep.SAVE_OUTPUTS,
            "warnings": ["No code to save"]
        }
    
    # Generate filenames with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save code file - use absolute paths
    code_filename = f"chart_{timestamp}.py"
    code_path = os.path.abspath(os.path.join(RESULTS_PATH, code_filename))
    
    # Update code to use correct output path - use absolute path
    chart_filename = f"chart_{timestamp}.html"
    chart_path = os.path.abspath(os.path.join(RESULTS_PATH, chart_filename))
    
    # Replace the output file path in the code
    import re
    generated_code = re.sub(
        r'\.render\(["\'].*?["\']\)',
        f'.render("{chart_path}")',
        generated_code
    )
    
    # Save the code
    with open(code_path, 'w') as f:
        f.write(generated_code)
    
    logger.info(f"Saved generated code to {code_path}")
    
    # Try to execute the code
    try:
        # Use the venv python if available
        python_exe = sys.executable if hasattr(sys, 'executable') else 'python3'
        
        result = subprocess.run(
            [python_exe, code_path],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=os.path.dirname(code_path)  # Use the directory of the code file
        )
        
        if result.returncode == 0:
            logger.info(f"Chart created at {chart_path}")
            success_message = f"Successfully generated chart:\n- Code: {code_filename}\n- Chart: {chart_filename}"
        else:
            logger.warning(f"Code execution warning: {result.stderr}")
            success_message = f"Code saved but execution had issues:\n{result.stderr}"
            
    except Exception as e:
        logger.error(f"Error executing code: {e}")
        success_message = f"Code saved to {code_filename} but couldn't execute: {str(e)}"
    
    return {
        "messages": [
            HumanMessage(
                content=success_message,
                name="save_outputs"
            )
        ],
        "output_files": {
            "code": code_path,
            "chart": chart_path if os.path.exists(chart_path) else None,
            "data": state.get("data_source")
        },
        "current_step": ProcessingStep.SAVE_OUTPUTS
    }


def error_handler_node(state: ChartAgentState) -> Dict[str, Any]:
    """
    Handle errors and provide user-friendly messages.
    """
    messages = state.get("messages", [])
    
    # Collect all error messages
    errors = []
    for msg in messages:
        if "error" in msg.content.lower() or "failed" in msg.content.lower():
            errors.append(msg.content)
    
    summary = "Process encountered errors:\n" + "\n".join(errors) if errors else "Unknown error occurred"
    
    return {
        "messages": [
            HumanMessage(
                content=summary,
                name="error_handler"
            )
        ],
        "current_step": ProcessingStep.ERROR
    }