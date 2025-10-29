"""
State models for the Chart Generation Agent
"""

from typing import TypedDict, List, Annotated, Dict, Optional, Any
from langchain_core.messages import BaseMessage
import operator
from pydantic import BaseModel, Field
from enum import Enum


class ChartRequest(BaseModel):
    """User request for chart generation"""
    chart_description: str = Field(..., description="Description of what chart to create")
    data_topic: Optional[str] = Field(None, description="Topic for synthetic data generation")
    data_details: Optional[str] = Field(None, description="Details for data generation")
    data_rows: Optional[int] = Field(50, description="Number of rows for synthetic data")
    input_data_path: Optional[str] = Field(None, description="Path to existing data file")
    output_chart_path: str = Field("output_chart.html", description="Where to save the chart")
    output_code_path: str = Field("generated_chart.py", description="Where to save the code")
    chart_type_hint: Optional[str] = Field(None, description="Optional chart type preference")


class ProcessingStep(str, Enum):
    """Steps in the chart generation process"""
    ANALYZE_REQUEST = "analyze_request"
    GENERATE_DATA = "generate_data"
    SEARCH_KNOWLEDGE_BASE = "search_knowledge_base"
    GENERATE_CODE = "generate_code"
    SAVE_OUTPUTS = "save_outputs"
    ERROR = "error"
    COMPLETE = "complete"


class ChartAgentState(TypedDict):
    """Main state for the chart generation agent"""
    # Core state
    messages: Annotated[List[BaseMessage], operator.add]
    request: ChartRequest
    current_step: ProcessingStep
    
    # Data related
    data_source: Optional[str]  # Path to data or 'generated'
    generated_data: Optional[Dict[str, Any]]  # Generated data if applicable
    data_analysis: Optional[Dict[str, Any]]  # Analysis of the data
    
    # Knowledge base related
    selected_chart_type: Optional[str]
    chart_examples: Optional[Dict[str, str]]  # Example codes from knowledge base
    kb_reasoning: Optional[str]  # Why this chart type was selected
    
    # Code generation related
    generated_code: Optional[str]  # The generated Python code
    imports_required: Optional[List[str]]
    customizations_applied: Optional[List[str]]
    
    # Results
    output_files: Optional[Dict[str, str]]  # Paths to generated files
    errors: Optional[List[str]]  # Any errors encountered
    warnings: Optional[List[str]]  # Any warnings
    
    # Routing
    next: Optional[str]  # Next node to execute
