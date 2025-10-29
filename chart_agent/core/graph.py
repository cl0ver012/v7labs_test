"""
Main graph for the Chart Generation Agent
"""

from langgraph.graph import START, END, StateGraph
from langgraph.graph import MessagesState
import logging

from chart_agent.models.agent_state import ChartAgentState, ProcessingStep
from chart_agent.core.supervisor import make_supervisor_node
from chart_agent.nodes.data_generation import analyze_request_node, generate_data_node
from chart_agent.nodes.knowledge_base import search_knowledge_base_node
from chart_agent.nodes.code_generation import generate_code_node
from chart_agent.nodes.chart_generation import save_outputs_node, error_handler_node

logger = logging.getLogger(__name__)


def setup_chart_generation_graph():
    """
    Set up the main chart generation workflow graph with simplified flow.
    """
    try:
        # Create the state graph
        graph = StateGraph(ChartAgentState)
        
        # Add all workflow nodes (simplified flow with examples)
        graph.add_node("analyze_request", analyze_request_node)
        graph.add_node("generate_data", generate_data_node)
        graph.add_node("search_knowledge_base", search_knowledge_base_node)
        graph.add_node("generate_code", generate_code_node)
        graph.add_node("save_outputs", save_outputs_node)
        graph.add_node("error_handler", error_handler_node)
        
        # Add edges for the simplified workflow
        graph.add_edge(START, "analyze_request")
        
        # Always generate data
        graph.add_edge("analyze_request", "generate_data")
        
        # Get example code before generating
        graph.add_edge("generate_data", "search_knowledge_base")
        graph.add_edge("search_knowledge_base", "generate_code")
        
        # Save and finish
        graph.add_edge("generate_code", "save_outputs")
        graph.add_edge("save_outputs", END)
        graph.add_edge("error_handler", END)
        
        # Compile the graph
        compiled_graph = graph.compile()
        
        logger.info("Chart generation graph successfully compiled")
        return compiled_graph
        
    except Exception as e:
        logger.error(f"Error setting up chart generation graph: {e}")
        raise Exception(f"Failed to setup graph: {e}")
