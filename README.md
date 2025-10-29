# Chart Generation App

A Streamlit app that generates charts using AI.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file with your configuration:
```bash
# Required
ANTHROPIC_API_KEY=your-api-key-here

# Optional (defaults shown)
CLAUDE_MODEL=claude-3-5-haiku-latest
RESULTS_PATH=./results
GALLERY_PATH=./pyecharts-gallery
PROJECT_ROOT=.
```

3. Run the app:
```bash
streamlit run app.py
```

## How it works

- Type what chart you want in the chat
- The app generates data and creates a chart
- Charts are saved in the `results/` folder

## Features

- 44 chart types available (Line, Bar, Pie, Scatter, etc.)
- Automatic data generation
- PyEcharts visualizations with beautiful themes
- Multiple color themes (Macarons, Romantic, Dark, Vintage, etc.)
