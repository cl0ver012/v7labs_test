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
# load_dotenv()

# Configuration
DEFAULT_MODEL = os.getenv('CLAUDE_MODEL', 'claude-3-5-haiku-latest')


def generate_chart_code(
    data: Dict[str, Any],
    chart_description: str,
    example_code: Optional[str] = None,
    output_file: str = "chart.html",
    model: Optional[str] = None,
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
        llm = ChatAnthropic(model=model or DEFAULT_MODEL, temperature=temperature)
        
        # Build prompt emphasizing exact structure
        system_prompt = """You are a PyEcharts code generator.

CRITICAL RULES:
1. Use ONLY these imports:
   - from pyecharts import options as opts
   - from pyecharts.charts import [ChartType]  # Line, Bar, Pie, etc.
   - from pyecharts.globals import ThemeType  # Only if using a theme

2. Follow EXACT PyEcharts gallery structure:
   - Data as simple lists (x_data = [...], y_data = [...])
   - Chart creation with parentheses and method chaining
   - NO other imports (no pandas, no csv, etc.)
   - NO complex logic or functions

3. THEMES - Choose an appropriate theme for visual appeal:
   Available themes (use EXACTLY as shown):
   - ThemeType.LIGHT (clean, minimal light theme)
   - ThemeType.DARK (modern dark mode)
   - ThemeType.WHITE (pure white background)
   - ThemeType.CHALK (chalkboard style)
   - ThemeType.ESSOS (Game of Thrones inspired)
   - ThemeType.INFOGRAPHIC (bold infographic colors)
   - ThemeType.MACARONS (soft pastel colors)
   - ThemeType.PURPLE_PASSION (purple-dominated elegant)
   - ThemeType.ROMA (classic professional)
   - ThemeType.ROMANTIC (warm and inviting)
   - ThemeType.SHINE (bright and vibrant)
   - ThemeType.VINTAGE (retro-inspired)
   - ThemeType.WALDEN (natural earth tones)
   - ThemeType.WESTEROS (Game of Thrones inspired)
   - ThemeType.WONDERLAND (whimsical and colorful)
   - ThemeType.HALLOWEEN (spooky Halloween theme)
   
   Use themes like this:
   ```python
   Bar(init_opts=opts.InitOpts(theme=ThemeType.MACARONS))
   ```

4. Structure must be:
```python
from pyecharts import options as opts
from pyecharts.charts import Line  # or Bar, Pie, etc.
from pyecharts.globals import ThemeType  # If using theme

# Chart implementation here

```

Output ONLY the Python code, no explanations."""
        
        # Format data for prompt
        data_str = json.dumps(data, indent=2)
        
        # Normalize output file path for cross-platform compatibility
        output_file_normalized = output_file.replace('\\', '/')
        
        user_prompt = f"""Generate PyEcharts code for: {chart_description}

Data to visualize:
{data_str}

Requirements:
1. Convert the JSON data to simple Python lists (x_data, y_data, etc.)
2. Use appropriate chart type (Line, Bar, Pie, Scatter, etc.)
3. Follow EXACT PyEcharts gallery structure
4. Set output to: {output_file_normalized}
5. Add title based on description
6. Apply an appropriate theme using ThemeType (pick from: LIGHT, DARK, WHITE, CHALK, ESSOS, INFOGRAPHIC, MACARONS, PURPLE_PASSION, ROMA, ROMANTIC, SHINE, VINTAGE, WALDEN, WESTEROS, WONDERLAND, HALLOWEEN)
7. NO pandas, NO csv reading, NO complex imports"""
        
        # Add example if provided
        if example_code:
            user_prompt += f"""

Follow this EXACT structure (but with your data):
{example_code}


If Multiple examples are provided, just pick random one and generate the code based on that.
Because when you are generating code combining multiple examples, generated chart often get confussed and didn't looks good.
So just pick one, not the most relevant one it can be just random one and generate the code based on that.
You can generate the code by updating the code with your data and use the random theme.

And while you are generating code, use simple, short and professional title and labels for the chart.
When it gets longer, it looks not good and professional.
Do not not generate chart title. I mean just keep title of the chart empty string.
"""
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
    
    # Normalize output file path for cross-platform compatibility
    output_file = output_file.replace('\\', '/')
    
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
    
    # Select a nice theme for the chart
    import random
    # All available themes in PyEcharts
    themes = ['LIGHT', 'DARK', 'WHITE', 'CHALK', 'ESSOS', 'INFOGRAPHIC', 
              'MACARONS', 'PURPLE_PASSION', 'ROMA', 'ROMANTIC', 'SHINE', 
              'VINTAGE', 'WALDEN', 'WESTEROS', 'WONDERLAND', 'HALLOWEEN']
    # Prefer colorful themes over plain ones
    colorful_themes = ['MACARONS', 'ROMANTIC', 'INFOGRAPHIC', 'SHINE', 'ROMA', 
                      'WALDEN', 'VINTAGE', 'PURPLE_PASSION', 'WONDERLAND', 'HALLOWEEN']
    selected_theme = random.choice(colorful_themes)
    
    # Generate code following EXACT PyEcharts structure with theme
    code = f'''from pyecharts import options as opts
from pyecharts.charts import {chart_type}
from pyecharts.globals import ThemeType

x_data = {x_data!r}
y_data = {y_data!r}

(
    {chart_type}(init_opts=opts.InitOpts(theme=ThemeType.{selected_theme}))
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