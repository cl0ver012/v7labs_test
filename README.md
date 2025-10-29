# AI Chart Generation System

An intelligent chart generation system powered by LangGraph and PyEcharts that creates beautiful, interactive visualizations from natural language descriptions.

## Features

- 🤖 **Natural Language to Charts**: Describe what you want in plain English
- 📊 **50+ Chart Types**: Line, Bar, Pie, Scatter, Heatmap, 3D charts, and more
- 🎨 **Automatic Theming**: Beautiful pre-configured chart themes
- 📸 **PNG Export**: Convert HTML charts to PNG images (1280x720)
- 🚀 **Streamlit Interface**: Interactive web app for easy chart generation
- 🔄 **Batch Processing**: Generate multiple chart variations automatically

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Chrome/Chromium browser (for PNG conversion)

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd v7labs_test
```

2. **Create a virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:

**Option A: Using pyproject.toml (Recommended)**
```bash
pip install -e .  # Basic installation
pip install -e ".[png]"  # With PNG conversion support
pip install -e ".[all]"  # All features including dev tools
```

**Option B: Using requirements files**
```bash
pip install -r requirements.txt  # Basic installation
# OR
pip install -r requirements-full.txt  # With PNG conversion support
```

4. **Set up environment variables**:
```bash
# Copy the example file and edit it
cp env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Usage

### 1. Streamlit App (Interactive Interface)

The easiest way to generate charts:

```bash
streamlit run app.py
```

Open your browser to `http://localhost:8501` and:
- Type chart descriptions in natural language
- Click example queries from the sidebar
- View generated charts instantly
- Export code for further customization

### 2. Generate Charts from PyEcharts Gallery

Generate multiple chart variations based on PyEcharts gallery examples:

```bash
# Generate charts for all types (HTML files)
python generate_chart_pipeline.py

# Generate specific chart types
python generate_chart_pipeline.py --chart-types Bar Line Pie

# Generate with specific themes
python generate_chart_pipeline.py --themes wonderland walden vintage

# Full options
python generate_chart_pipeline.py \
    --chart-types Bar Line Scatter \
    --themes romantic macarons \
    --variations 3 \
    --output-dir custom_output
```

**Available Chart Types**: 
Bar, Line, Pie, Scatter, Heatmap, Radar, Funnel, Gauge, Map, Tree, Treemap, Sunburst, Parallel, Sankey, WordCloud, and many more.

**Available Themes**: 
chalk, dark, essos, infographic, macarons, purple-passion, roma, romantic, shine, vintage, walden, westeros, white, wonderland, halloween

### 3. Convert HTML Charts to PNG Images

Convert generated HTML charts to PNG images (1280x720):

```bash
# Convert all HTML files in dump_generation folder
python convert_html_to_png.py

# Convert specific folder
python convert_html_to_png.py path/to/html/folder

# Convert single file
python convert_html_to_png.py path/to/chart.html
```

PNG files are saved to the `chart_pngs/` directory.

### 4. Simple Chart Generation (Direct API)

Generate a single chart programmatically:

```python
from chart_agent.main import ChartGenerationAgent

agent = ChartGenerationAgent()
result = agent.generate_chart(
    chart_description="Create a bar chart showing monthly sales",
    data_topic="retail sales",
    data_rows=12,
    output_chart_path="sales_chart.html"
)
```

Or use the simple generator:

```python
python simple_chart_generator.py
```

## Project Structure

```
v7labs_test/
├── app.py                      # Streamlit web interface
├── chart_agent/                # Core chart generation agent
│   ├── main.py                 # Main agent orchestrator
│   └── nodes/                  # LangGraph nodes
│       ├── chart_generation.py # Chart rendering
│       ├── code_generation.py  # Code synthesis
│       ├── data_generation.py  # Data creation
│       └── knowledge_base.py   # Chart type selection
├── generate_chart_pipeline.py  # Batch chart generation
├── convert_html_to_png.py      # HTML to PNG converter
├── simple_chart_generator.py   # Simple generation interface
├── simple_data_generator.py    # Data generation utilities
├── pyecharts-gallery/         # PyEcharts examples library
├── dump_generation/            # Generated chart outputs
├── chart_pngs/                # PNG exports
└── results/                   # Streamlit app outputs
```

## Configuration

### Environment Variables

Create a `.env` file:

```env
# Required for AI features
ANTHROPIC_API_KEY=your-anthropic-api-key

# Optional
PROJECT_ROOT=/path/to/project
RESULTS_PATH=/path/to/results
```

### Chart Dimensions

Default chart size: 1280x720 pixels

To modify, edit the configuration in:
- `generate_chart_pipeline.py`: `CHART_WIDTH`, `CHART_HEIGHT`
- `convert_html_to_png.py`: `CHART_WIDTH`, `CHART_HEIGHT`

## Tips & Best Practices

### For Best Results

1. **Be specific in descriptions**:
   - ✅ "Create a bar chart showing monthly revenue by region with gradient colors"
   - ❌ "Make a chart"

2. **Mention chart type when known**:
   - "Line chart with trend analysis"
   - "Stacked bar chart comparing categories"

3. **Include data context**:
   - "Sales data over 12 months"
   - "Customer demographics by age group"

### Troubleshooting

**Charts not displaying in Streamlit?**
- Ensure generated HTML files exist in the results folder
- Check browser console for JavaScript errors
- Verify PyEcharts is properly installed

**PNG conversion failing?**
- Install Chrome/Chromium browser
- Install selenium: `pip install selenium webdriver-manager`
- Check Chrome driver compatibility

**AI features not working?**
- Verify ANTHROPIC_API_KEY is set correctly
- Check API key has sufficient credits
- Fallback mode will use template-based generation

## Requirements

See `pyproject.toml` for complete dependency list. Key packages:
- streamlit >= 1.29.0
- pyecharts >= 2.0.0
- langchain >= 0.1.0
- langgraph >= 0.0.20
- anthropic >= 0.18.0
- selenium (for PNG conversion)
- pillow (for image processing)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or suggestions, please open an issue on the GitHub repository.