"""
Code Generation Node - Simplified version
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

# Configuration
PROJECT_ROOT = os.getenv('PROJECT_ROOT', os.getcwd())
RESULTS_PATH = os.getenv('RESULTS_PATH', os.path.join(os.getcwd(), 'results'))

logger = logging.getLogger(__name__)


def generate_code_node(state: ChartAgentState) -> Dict[str, Any]:
    """
    Generate chart visualization code using simplified approach.
    """
    logger.info("Generating chart visualization code...")
    
    request = state["request"]
    data = state.get("generated_data", {})
    examples = state.get("chart_examples", {})
    
    try:
        # Import the simple chart generator
        import sys
        if PROJECT_ROOT not in sys.path:
            sys.path.append(PROJECT_ROOT)
        from simple_chart_generator import generate_chart_code
        
        # Get first example if available
        example_code = None
        if examples:
            example_code = list(examples.values())[0] if isinstance(examples, dict) else str(examples)
        
        # Generate the code
        code = generate_chart_code(
            data=data,
            chart_description=request.chart_description,
            example_code=example_code,
            output_file=request.output_chart_path,
            temperature=0.3
        )
        
        logger.info(f"Generated {len(code)} characters of code")
        
        return {
            "messages": [
                HumanMessage(
                    content=f"Generated visualization code ({len(code)} chars)",
                    name="generate_code"
                )
            ],
            "generated_code": code,
            "current_step": ProcessingStep.GENERATE_CODE
        }
        
    except Exception as e:
        logger.error(f"Error generating code: {e}")
        
        # Fallback code following EXACT PyEcharts gallery structure
        keys = list(data.keys()) if data else ["x", "y"]
        x_key = keys[0]
        y_key = keys[1] if len(keys) > 1 else keys[0]
        
        x_data = data.get(x_key, ["A", "B", "C"])
        y_data = data.get(y_key, [1, 2, 3])
        
        # Use the selected chart type from knowledge base
        chart_type = state.get("selected_chart_type", "Line")
        
        # Generate appropriate fallback based on chart type
        if chart_type == "Bar":
            chart_class = "Bar"
        elif chart_type == "Pie":
            chart_class = "Pie"
        elif chart_type == "Scatter":
            chart_class = "Scatter"
        else:
            chart_class = "Line"
        
        fallback_code = f"""from pyecharts import options as opts
from pyecharts.charts import {chart_class}

x_data = {x_data!r}
y_data = {y_data!r}

(
    {chart_class}()
    .add_xaxis(x_data)
    .add_yaxis("", y_data)
    .set_global_opts(
        title_opts=opts.TitleOpts(title="Chart")
    )
    .render("output.html")
)"""
        
        return {
            "messages": [
                HumanMessage(
                    content=f"Using fallback code due to error: {str(e)}",
                    name="generate_code"
                )
            ],
            "generated_code": fallback_code,
            "current_step": ProcessingStep.GENERATE_CODE,
            "warnings": [f"Code generation error: {str(e)}"]
        }