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

# Add the project to path
sys.path.append('/home/ilya/Desktop/v7labs_test')

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

# Title and description
st.title("📊 AI Chart Generator")
st.markdown("Generate beautiful charts from natural language descriptions")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # Display the actual chart visualization if available
        if "chart_path" in message and os.path.exists(message["chart_path"]):
            st.success(f"📈 Chart generated: {message['chart_path']}")
            
            # Display the actual chart from HTML file
            try:
                with open(message["chart_path"], 'r', encoding='utf-8') as f:
                    chart_html = f.read()
                # Display the chart in an iframe
                st.components.v1.html(chart_html, height=500, scrolling=True)
            except Exception as e:
                st.error(f"Could not display chart: {e}")
            
            # Show the generated code in an expander
            if "code_path" in message and os.path.exists(message["code_path"]):
                with st.expander("View Generated Code"):
                    with open(message["code_path"], 'r') as f:
                        code = f.read()
                    st.code(code, language="python")

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
            # Generate unique filenames in results folder
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            chart_path = f"results/chart_{timestamp}.html"
            code_path = f"results/chart_{timestamp}.py"
            
            # Ensure results folder exists
            os.makedirs("results", exist_ok=True)
            
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
                    
                    # Add assistant response with file paths
                    message_data = {
                        "role": "assistant", 
                        "content": response,
                        "chart_path": chart_path,
                        "code_path": code_path
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
                
                # Display the actual chart visualization
                # Check for the chart in both locations (old and new)
                actual_chart_path = None
                if result.get('output_files') and result['output_files'].get('chart'):
                    actual_chart_path = result['output_files']['chart']
                elif os.path.exists(chart_path):
                    actual_chart_path = chart_path
                elif os.path.exists(chart_path.replace('results/', '')):
                    actual_chart_path = chart_path.replace('results/', '')
                
                if result['success'] and actual_chart_path and os.path.exists(actual_chart_path):
                    st.success(f"📈 Chart generated: {os.path.basename(actual_chart_path)}")
                    try:
                        with open(actual_chart_path, 'r', encoding='utf-8') as f:
                            chart_html = f.read()
                        # Display the interactive chart
                        st.components.v1.html(chart_html, height=500, scrolling=True)
                    except Exception as e:
                        st.error(f"Could not display chart: {e}")
                
                # Show the code if generated
                actual_code_path = None
                if result.get('output_files') and result['output_files'].get('code'):
                    actual_code_path = result['output_files']['code']
                elif os.path.exists(code_path):
                    actual_code_path = code_path
                elif os.path.exists(code_path.replace('results/', '')):
                    actual_code_path = code_path.replace('results/', '')
                    
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
            # Clear the chat input and add the example
            st.session_state.messages.append({"role": "user", "content": example})
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
