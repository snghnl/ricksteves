# Rick Steves Audio Guide Analysis Dashboard

This Streamlit dashboard provides interactive visualization of Rick Steves forum audio guide analysis data, including sentiment analysis, theme distribution, and forum metrics.

## Features

-   **📊 Overview**: Key metrics and insights for each museum
-   **🎯 Analysis**: Sentiment distribution, user engagement, and common themes
-   **📋 Posts**: Detailed view of individual forum posts with filtering options
-   **🏛️ Comparison**: Cross-museum comparison charts and statistics
-   **📈 Global Insights**: Overall summary and top museums by various metrics

## Data Sources

The dashboard uses three main data files:

1. `audio_guide_metrics.json` - Individual museum metrics and analysis
2. `museum_comparison.json` - Cross-museum comparison data
3. `enhanced_posts.json` - Detailed forum posts with sentiment analysis

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Ensure the data files are present in the `transform/` directory:
    - `transform/audio_guide_metrics.json`
    - `transform/museum_comparison.json`
    - `transform/enhanced_posts.json`

## Usage

### Option 1: Run with launcher script

```bash
python run_dashboard.py
```

### Option 2: Run directly with Streamlit

```bash
streamlit run dashboard.py --server.port 8502
```

The dashboard will open in your browser at `http://localhost:8502`

## Dashboard Sections

### Overview Tab

-   Key metrics for the selected museum
-   Total posts, replies, and reactions
-   Sentiment score and overall assessment

### Analysis Tab

-   Sentiment distribution pie chart
-   User engagement bar chart
-   Common themes visualization

### Posts Tab

-   Individual forum posts with expandable details
-   Filtering options by sentiment, audio guide mentions, and text search
-   Quick reference table

### Comparison Tab

-   Cross-museum comparison charts
-   Summary statistics table

### Global Insights Tab

-   Overall summary metrics
-   Top museums by engagement and sentiment
-   Theme distribution across all museums

## Data Structure

### Museum Metrics

Each museum entry contains:

-   `museum`: Museum name
-   `forum`: Forum source (usually "Unknown" for Rick Steves)
-   `total_posts`: Number of forum posts
-   `total_replies`: Number of replies
-   `positive_reactions`, `negative_reactions`, `neutral_reactions`: Sentiment counts
-   `audio_guide_sentiment_score`: Calculated sentiment score
-   `common_themes`: List of identified themes
-   `user_engagement`: Dictionary of user engagement counts

### Enhanced Posts

Each post contains:

-   `url`: Forum post URL
-   `title`: Post title
-   `content`: Post content
-   `audio_guide_mention`: Boolean indicating audio guide mention
-   `sentiment`: Sentiment classification
-   `sentiment_score`: Numeric sentiment score
-   `replies`: List of reply objects

## Customization

You can modify the dashboard by:

1. **Adding new visualizations**: Create new methods in the `RickStevesDashboard` class
2. **Changing data sources**: Update the file paths in the constructor
3. **Adding new filters**: Modify the filtering logic in the Posts tab
4. **Customizing styling**: Update the Plotly chart configurations

## Troubleshooting

-   **Data files not found**: Ensure all JSON files are in the same directory as the dashboard
-   **Streamlit not found**: Install with `pip install streamlit`
-   **Port already in use**: Change the port number in `run_dashboard.py`
-   **Large data files**: The dashboard handles large files but may take time to load initially

## Dependencies

-   `streamlit`: Web application framework
-   `pandas`: Data manipulation
-   `plotly`: Interactive visualizations
-   `numpy`: Numerical operations
