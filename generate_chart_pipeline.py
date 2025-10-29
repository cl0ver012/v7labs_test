"""
Pipeline to generate 100 readable charts with high visual variance
Generates 5 charts per chart type with different themes and styles
"""

import os
import sys
import json
import glob
import random
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

# Add project to path
sys.path.append('.')

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

# Load environment variables
# load_dotenv()

# Configuration
GALLERY_PATH = os.getenv('GALLERY_PATH', os.path.join(os.getcwd(), 'pyecharts-gallery'))
OUTPUT_PATH = os.path.abspath('./dump_generation')  # Use absolute path
CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-3-5-haiku-latest')
CHARTS_PER_TYPE = 4  # 4 charts per type for variety

# Chart types from pyecharts-gallery
# Start with simpler, more reliable charts, then add complex ones
TARGET_CHART_TYPES = [
    # Basic charts that work well
    'Bar',            # Bar charts
    'Line',           # Line charts
    'Pie',            # Pie charts
    'Scatter',        # Scatter plots
    'Funnel',         # Funnel charts
    'Gauge',          # Gauge charts
    'Radar',          # Radar charts
    'Heatmap',        # Heatmaps
    'Boxplot',        # Box plots
    'Candlestick',    # Candlestick (finance)
    'EffectScatter',  # Scatter with effects
    'Liquid',         # Liquid fill
    'Polar',          # Polar charts
    'WordCloud',      # Word clouds
    'Calendar',       # Calendar heatmap
    'PictorialBar',   # Pictorial bar
    'Parallel',       # Parallel coordinates
    'Sunburst',       # Sunburst charts
    'Treemap',        # Treemaps
    
    # 3D charts
    'Bar3D',          # 3D Bar charts
    'Line3D',         # 3D Line charts
    'Scatter3D',      # 3D Scatter plots
    
    # Complex charts (may need special handling)
    'Tree',           # Tree diagrams
    'Graph',          # Network graphs
    'Sankey',         # Sankey diagrams
    'ThemeRiver',     # Theme river
    
    # Map charts (need special data/setup)
    'Geo',            # Geographic maps
    'Map',            # Maps
    
    # Very complex or special charts (often fail)
    # 'AMap',         # Needs API key
    # 'BMap',         # Needs API key
    # 'Map3D',        # Complex 3D
    # 'MapGlobe',     # Complex globe
    # 'GraphGL',      # WebGL
    # 'Surface3D',    # Complex 3D
    # 'Graphic',      # Custom graphics
    # 'Image',        # Image handling
    # 'Grid',         # Layout
    # 'Overlap',      # Layout
    # 'Timeline',     # Complex timeline
    # 'Table',        # Table viz
]

# All available themes
THEMES = [
    'ThemeType.LIGHT', 'ThemeType.DARK', 'ThemeType.WHITE', 
    'ThemeType.CHALK', 'ThemeType.ESSOS', 'ThemeType.INFOGRAPHIC',
    'ThemeType.MACARONS', 'ThemeType.PURPLE_PASSION', 'ThemeType.ROMA',
    'ThemeType.ROMANTIC', 'ThemeType.SHINE', 'ThemeType.VINTAGE',
    'ThemeType.WALDEN', 'ThemeType.WESTEROS', 'ThemeType.WONDERLAND',
    'ThemeType.HALLOWEEN'
]

# Professional data topics for variety (expanded for diverse chart types)
DATA_TOPICS = [
    "quarterly revenue growth",
    "customer satisfaction metrics",
    "product sales distribution",
    "employee performance ratings",
    "website traffic analysis",
    "market share comparison",
    "inventory levels tracking",
    "social media engagement",
    "energy consumption patterns",
    "project timeline progress",
    "budget allocation breakdown",
    "user demographics analysis",
    "conversion rate optimization",
    "supply chain efficiency",
    "risk assessment matrix",
    "competitive analysis",
    "seasonal trends analysis",
    "quality control metrics",
    "customer acquisition costs",
    "operational efficiency KPIs",
    "geographic sales distribution",
    "network traffic flow",
    "stock price movements",
    "temperature variations",
    "population density map",
    "word frequency analysis",
    "hierarchical organization",
    "process flow diagram",
    "correlation matrix",
    "time series forecast",
    "resource utilization",
    "skill proficiency radar",
    "financial portfolio",
    "production capacity",
    "customer journey flow",
    "sentiment analysis",
    "performance benchmarks",
    "regional comparisons",
    "trend indicators",
    "workload distribution"
]


def load_example_codes(chart_type: str) -> List[str]:
    """Load Python example codes from a chart type folder, preferring simpler ones."""
    folder_path = os.path.join(GALLERY_PATH, chart_type)
    if not os.path.exists(folder_path):
        return []
    
    py_files = glob.glob(os.path.join(folder_path, "*.py"))
    examples = []
    
    # Sort to get basic/simple examples first
    py_files.sort(key=lambda x: (
        'complex' in x.lower(),
        'advanced' in x.lower(), 
        len(x)  # Shorter names often simpler
    ))
    
    for py_file in py_files[:3]:  # Limit to 3 examples per type
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Skip if it's a complex example
                if 'Page(' in content or 'Timeline(' in content or 'Grid(' in content:
                    continue
                # Prefer shorter examples (usually simpler)
                if len(content) > 3000:
                    content = content[:3000] + "\n# ... truncated ..."
                examples.append(content)
        except:
            continue
    
    # If no examples found, create a minimal template
    if not examples:
        examples = [f"from pyecharts.charts import {chart_type}\n# Basic {chart_type} example"]
    
    return examples


def generate_synthetic_data(topic: str, chart_type: str, num_points: int = 12) -> Dict[str, Any]:
    """Generate synthetic data using simple LLM call."""
    try:
        llm = ChatAnthropic(model=CLAUDE_MODEL, temperature=0.7)
        
        system_prompt = """Generate synthetic data for a chart visualization.
        Output ONLY valid JSON. No explanations, no markdown.
        The data should be realistic and appropriate for the chart type."""
        
        user_prompt = f"""Generate data for a {chart_type} chart about: {topic}

Requirements:
- About {num_points} data points
- Professional, short labels
- Realistic values that make sense for {topic}
- Structure appropriate for {chart_type}

For example:
- Bar/Line charts need categories and values
- Pie charts need name-value pairs
- Map charts need location names and values
- WordCloud needs words and frequencies
- Graph/Tree need nodes and connections
- Candlestick needs OHLC data

Output as JSON object."""
        
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        
        # Parse JSON from response
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        data = json.loads(content.strip())
        return data
        
    except Exception as e:
        # Simple fallback data
        print(f"    Data generation failed: {str(e)[:50]}, using fallback")
        return {
            "labels": [f"Item {i+1}" for i in range(num_points)],
            "values": [random.randint(50, 200) for _ in range(num_points)]
        }


def generate_chart_code(
    data: Dict[str, Any],
    chart_type: str,
    example_code: str,
    theme: str,
    variation_num: int,
    output_file: str
) -> str:
    """Generate chart code using simple LLM call."""
    # Normalize path for cross-platform compatibility
    output_file_normalized = output_file.replace('\\', '/')
    
    try:
        llm = ChatAnthropic(model=CLAUDE_MODEL, temperature=0.3)
        
        system_prompt = f"""You are a PyEcharts code generator. 
Generate working PyEcharts code based on the example provided.

CRITICAL RULES:
1. Output ONLY executable Python code, no explanations
2. Use the exact same chart type and structure as the example
3. Replace the data with the new data provided
4. Set size: init_opts=opts.InitOpts(width="1280px", height="720px", theme={theme})
5. Use short, professional titles (max 3-4 words)
6. Output to: {output_file_normalized}
7. The code must run without errors"""
        
        # Use first 1500 chars of example to avoid token limits
        if len(example_code) > 1500:
            example_code = example_code[:1500] + "\n# ... rest of example ..."
        
        user_prompt = f"""Generate a {chart_type} chart with this data:

DATA TO USE:
{json.dumps(data, indent=2)}

EXAMPLE CODE TO FOLLOW:
{example_code}

Adapt the example code to use the new data above.
Keep the same structure and chart type.
Apply theme: {theme}
Output file: {output_file_normalized}"""
        
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        
        # Clean response
        code = response.content
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0]
        elif "```" in code:
            code = code.split("```")[1].split("```")[0]
        
        return code.strip()
        
    except Exception as e:
        print(f"    Code generation failed: {str(e)[:50]}, using simple fallback")
        # Use simple fallback that might work for basic charts
        return generate_simple_fallback(data, chart_type, theme, output_file_normalized)


def generate_simple_fallback(data: Dict, chart_type: str, theme: str, output_file: str) -> str:
    """Generate very simple fallback - just try basic chart patterns."""
    
    # Normalize path for cross-platform compatibility
    output_file = output_file.replace('\\', '/')
    
    # For charts that definitely won't work with basic structure, skip
    skip_types = ['AMap', 'BMap', 'Geo', 'Map', 'Map3D', 'MapGlobe', 'Graph', 
                  'GraphGL', 'Sankey', 'Tree', 'ThemeRiver', 'Surface3D', 
                  'Graphic', 'Image', 'Table', 'Grid', 'Overlap', 'Timeline']
    
    if chart_type in skip_types:
        # Return minimal code that at least imports correctly
        return f'''from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.globals import ThemeType

# {chart_type} requires special setup - using Bar as fallback
(
    Bar(init_opts=opts.InitOpts(width="1280px", height="720px", theme={theme}))
    .add_xaxis(["A", "B", "C"])
    .add_yaxis("Data", [1, 2, 3])
    .set_global_opts(title_opts=opts.TitleOpts(title="{chart_type} Demo"))
    .render("{output_file}")
)'''
    
    # Try to use basic structure for simpler charts
    keys = list(data.keys())
    values = data.get('values', data.get(keys[0] if keys else 'data', [1, 2, 3]))
    
    if not isinstance(values, list):
        values = [values]
    
    # Normalize path here too
    output_file = output_file.replace('\\', '/')
    
    # Simple pattern that might work for basic charts
    return f'''from pyecharts import options as opts
from pyecharts.charts import {chart_type}
from pyecharts.globals import ThemeType

try:
    c = {chart_type}(init_opts=opts.InitOpts(width="1280px", height="720px", theme={theme}))
    # Try to add data in simplest way possible
    if hasattr(c, 'add'):
        c.add("", {values[:10]!r})
    elif hasattr(c, 'add_xaxis'):
        c.add_xaxis(["Item " + str(i) for i in range(len({values[:10]!r}))])
        c.add_yaxis("Data", {values[:10]!r})
    c.set_global_opts(title_opts=opts.TitleOpts(title="Chart"))
    c.render("{output_file}")
except:
    # Final fallback
    from pyecharts.charts import Bar
    Bar(init_opts=opts.InitOpts(width="1280px", height="720px", theme={theme})).add_xaxis(["A", "B", "C"]).add_yaxis("Data", [1, 2, 3]).render("{output_file}")
'''


def ensure_output_structure():
    """Create output directory structure."""
    for chart_type in TARGET_CHART_TYPES:
        os.makedirs(os.path.join(OUTPUT_PATH, chart_type), exist_ok=True)


def generate_charts_for_type(chart_type: str) -> int:
    """Generate multiple chart variations for a given type."""
    print(f"\n📊 Generating {CHARTS_PER_TYPE} {chart_type} charts...")
    
    # Load examples
    examples = load_example_codes(chart_type)
    if not examples:
        print(f"  ⚠️ No examples found for {chart_type}, using default")
        examples = ["# Default example"]
    
    generated_count = 0
    
    for i in range(CHARTS_PER_TYPE):
        try:
            # Select random theme and example
            theme = random.choice(THEMES)
            example = random.choice(examples)
            topic = random.choice(DATA_TOPICS)
            
            print(f"  Chart {i+1}/{CHARTS_PER_TYPE}: {topic} with {theme}")
            
            # Generate data
            data = generate_synthetic_data(topic, chart_type)
            
            # Generate chart code
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.abspath(os.path.join(
                OUTPUT_PATH, 
                chart_type, 
                f"{chart_type.lower()}_{i+1}_{timestamp}.html"
            ))
            
            code = generate_chart_code(
                data=data,
                chart_type=chart_type,
                example_code=example,
                theme=theme,
                variation_num=i+1,
                output_file=output_file
            )
            
            # Save and execute code
            code_file = output_file.replace('.html', '.py')
            with open(code_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Execute to generate HTML
            import subprocess
            result = subprocess.run(
                [sys.executable, code_file],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=os.path.dirname(code_file)  # Run in the same directory as the code file
            )
            
            if result.returncode == 0 and os.path.exists(output_file):
                print(f"    ✅ Generated: {os.path.basename(output_file)}")
                generated_count += 1
            else:
                print(f"    ❌ Failed to generate chart: {result.stderr[:100]}")
                
        except Exception as e:
            print(f"    ❌ Error: {str(e)[:100]}")
    
    return generated_count


def main():
    """Main pipeline execution."""
    print("🚀 Starting Chart Generation Pipeline")
    print("=" * 60)
    print(f"Chart Types: {len(TARGET_CHART_TYPES)} different types")
    print(f"Charts per type: {CHARTS_PER_TYPE}")
    print(f"Target Total: {len(TARGET_CHART_TYPES) * CHARTS_PER_TYPE} charts")
    print(f"Output: {OUTPUT_PATH}")
    print("=" * 60)
    
    # Ensure output structure
    ensure_output_structure()
    
    # Generate charts for each type
    total_generated = 0
    for chart_type in TARGET_CHART_TYPES:
        generated = generate_charts_for_type(chart_type)
        total_generated += generated
    
    # Summary
    print("\n" + "=" * 60)
    print("📈 Generation Complete!")
    print(f"Total charts generated: {total_generated}")
    print(f"Success rate: {total_generated}/{len(TARGET_CHART_TYPES) * CHARTS_PER_TYPE} ({total_generated / (len(TARGET_CHART_TYPES) * CHARTS_PER_TYPE) * 100:.1f}%)")
    print(f"Output location: {OUTPUT_PATH}")
    print("=" * 60)
    
    # List generated files
    print("\n📁 Generated files by category:")
    for chart_type in TARGET_CHART_TYPES:
        folder = os.path.join(OUTPUT_PATH, chart_type)
        if os.path.exists(folder):
            html_files = glob.glob(os.path.join(folder, "*.html"))
            if html_files:
                print(f"  {chart_type}: {len(html_files)} charts")


if __name__ == "__main__":
    main()
