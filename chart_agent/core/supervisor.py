"""
Supervisor for orchestrating the chart generation workflow
"""

from typing import Literal
from langgraph.types import Command
from langgraph.graph import END
from chart_agent.models.agent_state import ChartAgentState, ProcessingStep
import logging

logger = logging.getLogger(__name__)


def make_supervisor_node(members: list[str], execution_flow: dict):
    """
    Create a supervisor node that routes to the next appropriate node
    based on the execution flow and current state.
    """
    
    def supervisor_node(state: ChartAgentState) -> Command[Literal[*members, "__end__"]]:
        """Route to the next node based on state and execution flow"""
        
        # Check for errors
        if state.get("errors") and len(state["errors"]) > 0:
            logger.error(f"Errors detected: {state['errors']}")
            return Command(goto=END, update={"current_step": ProcessingStep.ERROR})
        
        # Get the last message to determine where we are
        if state["messages"] and len(state["messages"]) > 1:
            # Look for the last message with a name attribute
            previous_node = None
            for msg in reversed(state["messages"]):
                if hasattr(msg, 'name') and msg.name:
                    previous_node = msg.name
                    break
            if not previous_node:
                previous_node = "__start__"
        else:
            previous_node = "__start__"
        
        # Determine next step from execution flow
        goto = execution_flow.get(previous_node, END)
        
        if goto == "FINISH":
            goto = END
            update = {"current_step": ProcessingStep.COMPLETE}
        else:
            update = {"next": goto}
        
        logger.info(f"Routing from {previous_node} to {goto}")
        return Command(goto=goto, update=update)
    
    return supervisor_node


def routing_function(state: ChartAgentState) -> str:
    """
    Determine the next node based on the current state.
    This is used for conditional routing in the main graph.
    """
    step = state.get("current_step", ProcessingStep.ANALYZE_REQUEST)
    
    # Route based on the current processing step
    if step == ProcessingStep.ANALYZE_REQUEST:
        # Check if we need to generate data or use existing
        if state.get("input_data_path"):
            return "search_knowledge_base"
        else:
            return "generate_data"
    
    elif step == ProcessingStep.GENERATE_DATA:
        return "search_knowledge_base"
    
    elif step == ProcessingStep.SEARCH_KNOWLEDGE_BASE:
        return "generate_code"
    
    elif step == ProcessingStep.GENERATE_CODE:
        return "save_outputs"
    
    elif step == ProcessingStep.ERROR:
        return "error_handler"
    
    else:
        return END
