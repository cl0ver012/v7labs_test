"""
Knowledge Base Node - Simple LLM selection from available chart types
"""

import os
import glob
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
from chart_agent.models.agent_state import ChartAgentState, ProcessingStep

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


def get_available_chart_types(gallery_path: str = "/home/ilya/Desktop/v7labs_test/pyecharts-gallery") -> List[str]:
    """Get ALL chart types from ALL folder names in pyecharts-gallery."""
    chart_types = []
    
    if os.path.exists(gallery_path):
        for item in os.listdir(gallery_path):
            item_path = os.path.join(gallery_path, item)
            # Include ALL directories except hidden ones (starting with .)
            # Each folder contains example codes for that chart type
            if os.path.isdir(item_path) and not item.startswith('.'):
                chart_types.append(item)
    
    # Return all 44 chart types sorted
    return sorted(chart_types)


def select_chart_type_with_llm(chart_description: str, available_types: List[str]) -> str:
    """Use LLM to select the most relevant chart type."""
    try:
        llm = ChatAnthropic(
            model="claude-3-haiku-20240307",
            temperature=0.1
        )
        
        system_prompt = """Select the most relevant chart type from the list based on the user's description.
        Return ONLY the chart type name, nothing else."""
        
        user_prompt = f"""User wants to: {chart_description}
        
        Available chart types:
        {', '.join(available_types)}
        
        Select the single most appropriate chart type."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = llm.invoke(messages)
        selected = response.content.strip()
        
        # Validate the selection
        if selected in available_types:
            return selected
        else:
            # Fallback to Line if selection is invalid
            return "Line"
            
    except Exception as e:
        logger.warning(f"LLM selection failed: {e}, using keyword matching")
        
        # Simple keyword matching fallback
        description_lower = chart_description.lower()
        
        # Check for specific chart type keywords - covering ALL 44 chart types
        keyword_map = {
            # Basic charts
            'line': 'Line',
            'trend': 'Line',
            'time series': 'Line',
            'bar': 'Bar',
            'column': 'Bar',
            'compare': 'Bar',
            'comparison': 'Bar',
            'pie': 'Pie',
            'donut': 'Pie',
            'distribution': 'Pie',
            'percentage': 'Pie',
            'scatter': 'Scatter',
            'correlation': 'Scatter',
            'bubble': 'Scatter',
            
            # 3D charts
            'bar3d': 'Bar3D',
            '3d bar': 'Bar3D',
            'line3d': 'Line3D',
            '3d line': 'Line3D',
            'scatter3d': 'Scatter3D',
            '3d scatter': 'Scatter3D',
            'surface': 'Surface3D',
            'surface3d': 'Surface3D',
            
            # Map charts
            'map': 'Map',
            'geo': 'Geo',
            'geographic': 'Geo',
            'map3d': 'Map3D',
            '3d map': 'Map3D',
            'globe': 'MapGlobe',
            'amap': 'AMap',
            'bmap': 'BMap',
            'baidu': 'BMap',
            
            # Specialized charts
            'heat': 'Heatmap',
            'heatmap': 'Heatmap',
            'radar': 'Radar',
            'spider': 'Radar',
            'funnel': 'Funnel',
            'gauge': 'Gauge',
            'meter': 'Gauge',
            'sankey': 'Sankey',
            'flow': 'Sankey',
            'tree': 'Tree',
            'hierarchy': 'Tree',
            'treemap': 'Treemap',
            'sunburst': 'Sunburst',
            'calendar': 'Calendar',
            'boxplot': 'Boxplot',
            'box plot': 'Boxplot',
            'candlestick': 'Candlestick',
            'stock': 'Candlestick',
            'liquid': 'Liquid',
            'water': 'Liquid',
            'polar': 'Polar',
            'radial': 'Polar',
            'parallel': 'Parallel',
            'pictorial': 'PictorialBar',
            'icon': 'PictorialBar',
            'wordcloud': 'WordCloud',
            'word cloud': 'WordCloud',
            'themeriver': 'ThemeRiver',
            'river': 'ThemeRiver',
            'graph': 'Graph',
            'network': 'Graph',
            'graphgl': 'GraphGL',
            
            # Layout and composite
            'grid': 'Grid',
            'overlap': 'Overlap',
            'page': 'Page',
            'tab': 'Tab',
            'table': 'Table',
            'timeline': 'Timeline',
            'animation': 'Timeline',
            
            # Special
            'effect': 'EffectScatter',
            'ripple': 'EffectScatter',
            'dataset': 'Dataset',
            'graphic': 'Graphic',
            'image': 'Image',
            'theme': 'Theme'
        }
        
        for keyword, chart_type in keyword_map.items():
            if keyword in description_lower and chart_type in available_types:
                return chart_type
        
        # Default to Line if no match
        return "Line"


def get_example_from_folder(chart_type: str, gallery_path: str = "/home/ilya/Desktop/v7labs_test/pyecharts-gallery") -> str:
    """Get an example Python file from the selected chart type folder."""
    folder_path = os.path.join(gallery_path, chart_type)
    
    if not os.path.exists(folder_path):
        return None
    
    # Find Python files in the folder
    py_files = glob.glob(os.path.join(folder_path, "*.py"))
    
    if not py_files:
        return None
    
    # Prefer basic/simple examples
    for keyword in ['basic', 'simple', 'base']:
        for file in py_files:
            if keyword in os.path.basename(file).lower():
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        return f.read()
                except:
                    continue
    
    # Otherwise return the first file
    try:
        with open(py_files[0], 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return None


def search_knowledge_base_node(state: ChartAgentState) -> Dict[str, Any]:
    """
    Simple knowledge base search:
    1. Get available chart types from folders
    2. Use LLM to select the best one
    3. Return example code from that folder
    """
    logger.info("Searching knowledge base for chart examples...")
    
    request = state["request"]
    
    # Get available chart types
    available_types = get_available_chart_types()
    
    if not available_types:
        logger.warning("No chart types found in gallery")
        available_types = ["Line", "Bar", "Pie", "Scatter"]
    
    # Use LLM to select the best chart type
    selected_type = select_chart_type_with_llm(request.chart_description, available_types)
    logger.info(f"LLM selected chart type: {selected_type}")
    
    # Get example code from the selected folder
    example_code = get_example_from_folder(selected_type)
    
    if not example_code:
        # Simple fallback if no example found
        example_code = """from pyecharts import options as opts
from pyecharts.charts import Line

x_data = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
y_data = [820, 932, 901, 934, 1290, 1330, 1320]

(
    Line()
    .add_xaxis(x_data)
    .add_yaxis("", y_data)
    .set_global_opts(title_opts=opts.TitleOpts(title="Chart"))
    .render("chart.html")
)"""
    
    return {
        "messages": [
            HumanMessage(
                content=f"Selected {selected_type} chart from {len(available_types)} available types",
                name="search_knowledge_base"
            )
        ],
        "chart_examples": {"example": example_code},
        "selected_chart_type": selected_type,
        "current_step": ProcessingStep.SEARCH_KNOWLEDGE_BASE
    }