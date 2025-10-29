"""
Simple Chart Generator - Generate PyEcharts code from JSON data
Following exact PyEcharts gallery structure
"""

import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage

# Load environment variables
load_dotenv()


def generate_chart_code(
    data: Dict[str, Any],
    chart_description: str,
    example_code: Optional[str] = None,
    output_file: str = "chart.html",
    model: str = "claude-3-haiku-20240307",
    temperature: float = 0.3
) -> str:
    """
    Generate PyEcharts code from data using LLM.
    Code will follow exact PyEcharts gallery structure.
    
    Args:
        data: JSON data to visualize
        chart_description: What kind of chart to create
        example_code: Optional example code to follow
        output_file: Output HTML file name
        model: LLM model to use
        temperature: Creativity level
    
    Returns:
        Python code string
    """
    
    try:
        # Initialize LLM
        llm = ChatAnthropic(model=model, temperature=temperature)
        
        # Build prompt emphasizing exact structure
        system_prompt = """You are a PyEcharts code generator.

CRITICAL RULES:
1. Use ONLY these imports:
   - from pyecharts import options as opts
   - from pyecharts.charts import [ChartType]  # Line, Bar, Pie, etc.

2. Follow EXACT PyEcharts gallery structure:
   - Data as simple lists (x_data = [...], y_data = [...])
   - Chart creation with parentheses and method chaining
   - NO other imports (no pandas, no csv, etc.)
   - NO complex logic or functions

3. Structure must be:
```python
from pyecharts import options as opts
from pyecharts.charts import Line  # or Bar, Pie, etc.

x_data = [...]
y_data = [...]

(
    Line()  # or Bar(), Pie(), etc.
    .add_xaxis(x_data)
    .add_yaxis("series_name", y_data)
    .set_global_opts(
        title_opts=opts.TitleOpts(title="Title")
    )
    .render("output.html")
)
```

Output ONLY the Python code, no explanations."""
        
        # Format data for prompt
        data_str = json.dumps(data, indent=2)
        
        user_prompt = f"""Generate PyEcharts code for: {chart_description}

Data to visualize:
{data_str}

Requirements:
1. Convert the JSON data to simple Python lists (x_data, y_data, etc.)
2. Use appropriate chart type (Line, Bar, Pie, Scatter, etc.)
3. Follow EXACT PyEcharts gallery structure
4. Set output to: {output_file}
5. Add title based on description
6. NO pandas, NO csv reading, NO complex imports"""
        
        # Add example if provided
        if example_code:
            user_prompt += f"""

Follow this EXACT structure (but with your data):
{example_code}"""
        else:
            # Provide a default example structure
            user_prompt += """

Follow this EXACT structure:
from pyecharts import options as opts
from pyecharts.charts import Line

x_data = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
y_data = [820, 932, 901, 934, 1290, 1330, 1320]

(
    Line()
    .add_xaxis(x_data)
    .add_yaxis("", y_data)
    .set_global_opts(
        title_opts=opts.TitleOpts(title="Chart Title")
    )
    .render("output.html")
)"""
        
        # Make LLM call
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = llm.invoke(messages)
        code = response.content
        
        # Clean up code if wrapped in markdown
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0]
        elif "```" in code:
            code = code.split("```")[1].split("```")[0]
        
        return code.strip()
        
    except Exception as e:
        print(f"Code generation failed: {e}, using fallback")
        
        # Generate simple fallback code following exact structure
        return generate_fallback_code(data, chart_description, output_file)


def generate_fallback_code(data: Dict, description: str, output_file: str, chart_type: str = None) -> str:
    """Generate simple fallback PyEcharts code following exact gallery structure."""
    
    # Get first two data arrays from the dict
    keys = list(data.keys())
    x_key = keys[0] if keys else "x"
    y_key = keys[1] if len(keys) > 1 else keys[0] if keys else "y"
    
    x_data = data.get(x_key, ["A", "B", "C"])
    y_data = data.get(y_key, [1, 2, 3])
    
    # Ensure lists
    if not isinstance(x_data, list):
        x_data = [x_data]
    if not isinstance(y_data, list):
        y_data = [y_data]
    
    # Determine chart type from description if not provided
    if not chart_type:
        desc_lower = description.lower()
        if 'bar' in desc_lower:
            chart_type = 'Bar'
        elif 'pie' in desc_lower:
            chart_type = 'Pie'
        elif 'scatter' in desc_lower:
            chart_type = 'Scatter'
        else:
            chart_type = 'Line'
    
    # Generate code following EXACT PyEcharts structure
    code = f'''from pyecharts import options as opts
from pyecharts.charts import {chart_type}

x_data = {x_data!r}
y_data = {y_data!r}

(
    {chart_type}()
    .add_xaxis(x_data)
    .add_yaxis("", y_data)
    .set_global_opts(
        title_opts=opts.TitleOpts(title="{description[:50]}")
    )
    .render("{output_file}")
)'''
    
    return code


# Example usage
if __name__ == "__main__":
    # Test data
    test_data = {
        "months": ["Jan", "Feb", "Mar", "Apr", "May"],
        "sales": [100, 120, 115, 140, 135]
    }
    
    # Generate code
    code = generate_chart_code(
        data=test_data,
        chart_description="Monthly sales line chart",
        output_file="test_chart.html"
    )
    
    print("Generated code:")
    print(code)