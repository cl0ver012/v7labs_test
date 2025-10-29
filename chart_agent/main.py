"""
Main entry point for the Chart Generation Agent
"""

import os
import logging
import asyncio
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from chart_agent.models.agent_state import ChartAgentState, ChartRequest, ProcessingStep
from chart_agent.core.graph import setup_chart_generation_graph

# Load environment variables
load_dotenv()

# Configuration
RESULTS_PATH = os.getenv('RESULTS_PATH', os.path.join(os.getcwd(), 'results'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ChartGenerationAgent:
    """
    Main agent class for chart generation workflow.
    """
    
    def __init__(self, anthropic_api_key: Optional[str] = None):
        """
        Initialize the Chart Generation Agent.
        
        Args:
            anthropic_api_key: Optional API key for Anthropic. If not provided,
                             will look for ANTHROPIC_API_KEY environment variable.
        """
        # Set API key
        if anthropic_api_key:
            os.environ["ANTHROPIC_API_KEY"] = anthropic_api_key
        elif not os.getenv("ANTHROPIC_API_KEY"):
            logger.warning("No Anthropic API key provided. Some features may be limited.")
        
        # Setup the graph
        self.graph = setup_chart_generation_graph()
        logger.info("Chart Generation Agent initialized")
    
    async def generate_chart_async(
        self,
        chart_description: str,
        data_topic: Optional[str] = None,
        data_details: Optional[str] = None,
        data_rows: Optional[int] = 30,
        input_data_path: Optional[str] = None,
        output_chart_path: str = None,
        output_code_path: str = None,
        chart_type_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a chart asynchronously based on the provided description.
        
        Args:
            chart_description: Description of the chart to create
            data_topic: Topic for synthetic data generation
            data_details: Additional details for data generation
            data_rows: Number of rows to generate
            input_data_path: Path to existing data file (if available)
            output_chart_path: Where to save the generated chart
            output_code_path: Where to save the generated code
            chart_type_hint: Optional hint for chart type
            
        Returns:
            Dictionary containing the results of the chart generation
        """
        # Create the request
        # Use default paths if not specified
        if not output_chart_path:
            output_chart_path = os.path.join(RESULTS_PATH, "output_chart.html")
        if not output_code_path:
            output_code_path = os.path.join(RESULTS_PATH, "generated_chart.py")
        
        request = ChartRequest(
            chart_description=chart_description,
            data_topic=data_topic,
            data_details=data_details,
            data_rows=data_rows,
            input_data_path=input_data_path,
            output_chart_path=output_chart_path,
            output_code_path=output_code_path,
            chart_type_hint=chart_type_hint
        )
        
        # Create initial state
        initial_state: ChartAgentState = {
            "messages": [HumanMessage(content=chart_description)],
            "request": request,
            "current_step": ProcessingStep.ANALYZE_REQUEST,
            "data_source": None,
            "generated_data": None,
            "data_analysis": None,
            "selected_chart_type": None,
            "chart_examples": None,
            "kb_reasoning": None,
            "generated_code": None,
            "imports_required": None,
            "customizations_applied": None,
            "output_files": None,
            "errors": None,
            "warnings": None,
            "next": None
        }
        
        logger.info(f"Starting chart generation for: {chart_description}")
        
        # Run the graph
        try:
            final_state = await self.graph.ainvoke(initial_state)
            
            # Extract results
            results = {
                "success": final_state.get("current_step") != ProcessingStep.ERROR,
                "chart_type": final_state.get("selected_chart_type"),
                "data_source": final_state.get("data_source"),
                "generated_code": final_state.get("generated_code"),
                "output_files": final_state.get("output_files"),
                "errors": final_state.get("errors"),
                "warnings": final_state.get("warnings"),
                "messages": [msg.content for msg in final_state.get("messages", [])]
            }
            
            if results["success"]:
                logger.info("Chart generation completed successfully")
            else:
                logger.error(f"Chart generation failed: {results['errors']}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error during chart generation: {e}")
            return {
                "success": False,
                "errors": [str(e)],
                "messages": [f"Fatal error: {str(e)}"]
            }
    
    def generate_chart(
        self,
        chart_description: str,
        data_topic: Optional[str] = None,
        data_details: Optional[str] = None,
        data_rows: Optional[int] = 30,
        input_data_path: Optional[str] = None,
        output_chart_path: str = None,
        output_code_path: str = None,
        chart_type_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a chart synchronously (wrapper for async method).
        """
        return asyncio.run(self.generate_chart_async(
            chart_description=chart_description,
            data_topic=data_topic,
            data_details=data_details,
            data_rows=data_rows,
            input_data_path=input_data_path,
            output_chart_path=output_chart_path,
            output_code_path=output_code_path,
            chart_type_hint=chart_type_hint
        ))


# Convenience function for simple usage
def generate_chart(
    description: str,
    data_path: Optional[str] = None,
    data_topic: Optional[str] = None,
    output_path: str = None
) -> Dict[str, Any]:
    """
    Simple interface to generate a chart.
    
    Args:
        description: What chart to create
        data_path: Path to data file (optional - always generates new data)
        data_topic: Topic for synthetic data
        output_path: Where to save the chart (in results folder)
        
    Returns:
        Results dictionary
    """
    import os
    # Ensure results folder exists
    os.makedirs(RESULTS_PATH, exist_ok=True)
    
    # Use default path if not specified
    if not output_path:
        output_path = os.path.join(RESULTS_PATH, "chart.html")
    
    agent = ChartGenerationAgent()
    
    return agent.generate_chart(
        chart_description=description,
        input_data_path=None,  # Always generate new data
        data_topic=data_topic or description,
        output_chart_path=output_path,
        output_code_path=output_path.replace('.html', '.py')
    )


if __name__ == "__main__":
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate charts using AI")
    parser.add_argument("description", help="Description of the chart to create")
    parser.add_argument("--data", help="Path to data file")
    parser.add_argument("--topic", help="Topic for synthetic data generation")
    parser.add_argument("--rows", type=int, default=50, help="Number of rows to generate")
    parser.add_argument("--output", default="chart.html", help="Output file path")
    parser.add_argument("--chart-type", help="Hint for chart type (e.g., Line, Bar, Pie)")
    
    args = parser.parse_args()
    
    # Create agent
    agent = ChartGenerationAgent()
    
    # Generate chart
    results = agent.generate_chart(
        chart_description=args.description,
        data_topic=args.topic,
        data_rows=args.rows,
        input_data_path=args.data,
        output_chart_path=args.output,
        output_code_path=args.output.replace('.html', '.py'),
        chart_type_hint=args.chart_type
    )
    
    # Print results
    if results["success"]:
        print(f"✅ Chart generated successfully!")
        print(f"📊 Chart type: {results['chart_type']}")
        if results["output_files"]:
            print(f"📁 Files created:")
            for key, path in results["output_files"].items():
                if path:
                    print(f"  - {key}: {path}")
    else:
        print(f"❌ Chart generation failed:")
        for error in results.get("errors", []):
            print(f"  - {error}")
    
    if results.get("warnings"):
        print(f"⚠️  Warnings:")
        for warning in results["warnings"]:
            print(f"  - {warning}")
