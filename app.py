"""
Simple Streamlit App for Chart Generation Agent
Clean chat interface for generating charts
"""

import streamlit as st
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
PROJECT_ROOT = os.getenv('PROJECT_ROOT', os.getcwd())
RESULTS_PATH = os.getenv('RESULTS_PATH', os.path.join(os.getcwd(), 'results'))

# Add the project to path
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from chart_agent.main import ChartGenerationAgent

# Page config
st.set_page_config(
    page_title="Chart Generator",
    page_icon="📊",
    layout="centered"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'agent' not in st.session_state:
    if not os.getenv("ANTHROPIC_API_KEY"):
        os.environ["ANTHROPIC_API_KEY"] = "test-key"
    st.session_state.agent = ChartGenerationAgent()
if 'auto_execute_query' not in st.session_state:
    st.session_state.auto_execute_query = None

# Title and description
st.title("📊 AI Chart Generator")
st.markdown("Generate beautiful charts from natural language descriptions")

# Check if there's an auto-execute query from example button
if st.session_state.auto_execute_query:
    prompt = st.session_state.auto_execute_query
    st.session_state.auto_execute_query = None  # Clear the flag
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Generate the chart automatically
    with st.spinner("Generating chart..."):
        # Generate unique filenames in results folder (use absolute paths)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_abs = os.path.abspath(RESULTS_PATH)
        chart_path = os.path.join(results_abs, f"chart_{timestamp}.html")
        code_path = os.path.join(results_abs, f"chart_{timestamp}.py")
        
        # Ensure results folder exists
        os.makedirs(results_abs, exist_ok=True)
        
        try:
            # Call the agent
            result = st.session_state.agent.generate_chart(
                chart_description=prompt,
                data_topic=prompt[:50],  # Use description as topic
                data_rows=20,
                output_chart_path=chart_path,
                output_code_path=code_path
            )
            
            # Process result
            if result['success']:
                # Get actual output file paths
                actual_chart_path = None
                actual_code_path = None
                
                if result.get('output_files') and result['output_files'].get('chart'):
                    actual_chart_path = result['output_files']['chart']
                elif os.path.exists(chart_path):
                    actual_chart_path = chart_path
                elif os.path.exists(chart_path.replace('results/', '')):
                    actual_chart_path = chart_path.replace('results/', '')
                
                if result.get('output_files') and result['output_files'].get('code'):
                    actual_code_path = result['output_files']['code']
                elif os.path.exists(code_path):
                    actual_code_path = code_path
                elif os.path.exists(code_path.replace('results/', '')):
                    actual_code_path = code_path.replace('results/', '')
                
                # Use actual paths in response
                display_chart_path = actual_chart_path if actual_chart_path else chart_path
                display_code_path = actual_code_path if actual_code_path else code_path
                
                response = f"""✅ **Chart generated successfully!**

**Chart Type:** {result.get('chart_type', 'Auto-detected')}  
**Data Source:** {result.get('data_source', 'Synthetic data')}  
**Files Created:**
- Chart: `{os.path.basename(display_chart_path)}`
- Code: `{os.path.basename(display_code_path)}`

You can find the generated files in the project directory."""
                
                # Add assistant response with actual file paths
                message_data = {
                    "role": "assistant", 
                    "content": response,
                    "chart_path": display_chart_path,
                    "code_path": display_code_path
                }
                
                # If warnings exist, add them
                if result.get('warnings'):
                    response += "\n\n⚠️ **Warnings:**\n"
                    for warning in result['warnings']:
                        response += f"- {warning[:100]}...\n"
                    message_data["content"] = response
                
            else:
                response = "❌ **Failed to generate chart**\n\n"
                if result.get('errors'):
                    response += "**Errors:**\n"
                    for error in result['errors']:
                        response += f"- {error}\n"
                message_data = {"role": "assistant", "content": response}
            
            st.session_state.messages.append(message_data)
            
        except Exception as e:
            error_msg = f"❌ **Error:** {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Rerun to show the new messages
    st.rerun()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # Display the actual chart visualization if available
        if "chart_path" in message and message["chart_path"] and os.path.exists(message["chart_path"]):
            st.success(f"📈 Chart generated: {os.path.basename(message['chart_path'])}")
            
            # Display the actual chart from HTML file
            try:
                with open(message["chart_path"], 'r', encoding='utf-8') as f:
                    chart_html = f.read()
                
                # Modify HTML to make the chart responsive
                # Replace fixed dimensions with responsive ones
                modified_html = chart_html.replace(
                    'style="width:1280px; height:720px; "',
                    'style="width:100%; height:100%; min-height:720px; "'
                )
                # Also handle variations in spacing
                modified_html = modified_html.replace(
                    'style="width:1280px; height:720px;"',
                    'style="width:100%; height:100%; min-height:720px;"'
                )
                
                # Add viewport meta tag and responsive CSS if not present
                if '<style>' not in modified_html:
                    modified_html = modified_html.replace(
                        '</head>',
                        '''<style>
                        body { margin: 0; padding: 0; overflow: hidden; }
                        .chart-container { width: 100% !important; height: 100% !important; }
                        </style>
                        </head>'''
                    )
                
                # Display the chart with proper height
                st.components.v1.html(
                    modified_html, 
                    height=750,  # Slightly more than 720px to ensure full visibility
                    scrolling=False,
                    width=None  # Use full container width
                )
            except Exception as e:
                st.error(f"Could not display chart: {e}")
            
            # Show the generated code in an expander
            if "code_path" in message and message["code_path"] and os.path.exists(message["code_path"]):
                with st.expander("View Generated Code"):
                    with open(message["code_path"], 'r') as f:
                        code = f.read()
                    st.code(code, language="python")
        elif "chart_path" in message and message["chart_path"]:
            # Debug: Show why chart is not displaying
            st.warning(f"⚠️ Chart file not found: {message['chart_path']}")

# Chat input
if prompt := st.chat_input("Describe the chart you want (e.g., 'Create a bar chart showing monthly sales')"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Generating chart..."):
            # Generate unique filenames in results folder (use absolute paths)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_abs = os.path.abspath(RESULTS_PATH)
            chart_path = os.path.join(results_abs, f"chart_{timestamp}.html")
            code_path = os.path.join(results_abs, f"chart_{timestamp}.py")
            
            # Ensure results folder exists
            os.makedirs(results_abs, exist_ok=True)
            
            try:
                # Call the agent
                result = st.session_state.agent.generate_chart(
                    chart_description=prompt,
                    data_topic=prompt[:50],  # Use description as topic
                    data_rows=20,
                    output_chart_path=chart_path,
                    output_code_path=code_path
                )
                
                # Process result
                if result['success']:
                    response = f"""✅ **Chart generated successfully!**

**Chart Type:** {result.get('chart_type', 'Auto-detected')}  
**Data Source:** {result.get('data_source', 'Synthetic data')}  
**Files Created:**
- Chart: `{chart_path}`
- Code: `{code_path}`

You can find the generated files in the project directory."""
                    
                    # Check for the actual output files
                    actual_chart_path = None
                    actual_code_path = None
                    
                    if result.get('output_files') and result['output_files'].get('chart'):
                        actual_chart_path = result['output_files']['chart']
                    elif os.path.exists(chart_path):
                        actual_chart_path = chart_path
                    elif os.path.exists(chart_path.replace('results/', '')):
                        actual_chart_path = chart_path.replace('results/', '')
                    
                    if result.get('output_files') and result['output_files'].get('code'):
                        actual_code_path = result['output_files']['code']
                    elif os.path.exists(code_path):
                        actual_code_path = code_path
                    elif os.path.exists(code_path.replace('results/', '')):
                        actual_code_path = code_path.replace('results/', '')
                    
                    # Add assistant response with actual file paths
                    message_data = {
                        "role": "assistant", 
                        "content": response,
                        "chart_path": actual_chart_path if actual_chart_path else chart_path,
                        "code_path": actual_code_path if actual_code_path else code_path
                    }
                    
                    # If warnings exist, add them
                    if result.get('warnings'):
                        response += "\n\n⚠️ **Warnings:**\n"
                        for warning in result['warnings']:
                            response += f"- {warning[:100]}...\n"
                        message_data["content"] = response
                    
                else:
                    response = "❌ **Failed to generate chart**\n\n"
                    if result.get('errors'):
                        response += "**Errors:**\n"
                        for error in result['errors']:
                            response += f"- {error}\n"
                    message_data = {"role": "assistant", "content": response}
                
                st.session_state.messages.append(message_data)
                st.markdown(response)
                
                if result['success'] and actual_chart_path and os.path.exists(actual_chart_path):
                    st.success(f"📈 Chart generated: {os.path.basename(actual_chart_path)}")
                    try:
                        with open(actual_chart_path, 'r', encoding='utf-8') as f:
                            chart_html = f.read()
                        
                        # Modify HTML to make the chart responsive
                        # Replace fixed dimensions with responsive ones
                        modified_html = chart_html.replace(
                            'style="width:1280px; height:720px; "',
                            'style="width:100%; height:100%; min-height:720px; "'
                        )
                        # Also handle variations in spacing
                        modified_html = modified_html.replace(
                            'style="width:1280px; height:720px;"',
                            'style="width:100%; height:100%; min-height:720px;"'
                        )
                        
                        # Add viewport meta tag and responsive CSS if not present
                        if '<style>' not in modified_html:
                            modified_html = modified_html.replace(
                                '</head>',
                                '''<style>
                                body { margin: 0; padding: 0; overflow: hidden; }
                                .chart-container { width: 100% !important; height: 100% !important; }
                                </style>
                                </head>'''
                            )
                        
                        # Display the interactive chart with proper height
                        st.components.v1.html(
                            modified_html, 
                            height=750,  # Slightly more than 720px to ensure full visibility
                            scrolling=False,
                            width=None  # Use full container width
                        )
                    except Exception as e:
                        st.error(f"Could not display chart: {e}")
                
                # Show the code if generated (actual_code_path already found above)
                if result['success'] and actual_code_path and os.path.exists(actual_code_path):
                    with st.expander("View Generated Code"):
                        with open(actual_code_path, 'r') as f:
                            code = f.read()
                        st.code(code, language="python")
                
            except Exception as e:
                error_msg = f"❌ **Error:** {str(e)}"
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                st.error(error_msg)

# Sidebar with information
with st.sidebar:
    st.header("ℹ️ Information")
    
    # API Key status
    if os.getenv("ANTHROPIC_API_KEY") and os.getenv("ANTHROPIC_API_KEY") != "test-key":
        st.success("✅ API Key Configured")
    else:
        st.warning("⚠️ Running in fallback mode")
        st.caption("Set ANTHROPIC_API_KEY environment variable for full features")
    
    st.markdown("---")
    
    # Examples
    st.header("💡 Example Requests")
    examples = [
        "Create a line chart showing monthly sales trends",
        "Bar chart comparing revenue by region", 
        "Pie chart of market share distribution",
        "Show temperature changes over the last 30 days",
        "Scatter plot of price vs demand correlation"
    ]
    
    for example in examples:
        if st.button(f"📝 {example}", key=example):
            # Set the example to be auto-executed
            st.session_state.auto_execute_query = example
            st.rerun()
    
    st.markdown("---")
    
    # Clear conversation
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    
    # Instructions
    st.markdown("""
    ### 📖 How to Use
    
    1. **Type your request** in the chat input
    2. **Be specific** about:
       - Chart type (line, bar, pie, etc.)
       - Data to visualize
       - Any special requirements
    3. **Press Enter** to generate
    
    The agent will:
    - Generate synthetic data if needed
    - Select the best chart type
    - Create visualization code
    - Save the chart as HTML
    
    ### 🎯 Tips
    - Mention specific chart types
    - Include data context
    - Request styling preferences
    """)

# Footer
st.markdown("---")
st.caption("Powered by LangGraph, PyEcharts, and Anthropic Claude")
