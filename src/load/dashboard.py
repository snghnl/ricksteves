"""
Rick Steves Audio Guide Analysis Dashboard

This Streamlit application provides interactive visualization of Rick Steves forum
audio guide analysis data, including sentiment analysis, theme distribution, and forum metrics.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import numpy as np

# Add this helper function
def is_running_in_streamlit():
    try:
        import streamlit.runtime.scriptrunner.script_run_context as stc
        return stc.get_script_run_ctx() is not None
    except Exception:
        return False

class RickStevesDashboard:
    """Main dashboard class for Rick Steves audio guide analysis."""
    
    def __init__(self, metrics_path: str, comparison_path: str, enhanced_posts_path: str):
        """Initialize dashboard with data paths."""
        self.metrics_path = Path(metrics_path)
        self.comparison_path = Path(comparison_path)
        self.enhanced_posts_path = Path(enhanced_posts_path)
        self.load_data()
        self.setup_museum_categories()
    
    def setup_museum_categories(self):
        """Setup museum categories for sidebar navigation."""
        self.major_museums = {
            "국립중앙박물관": "National Museum of Korea",
            "대영박물관": "British Museum",
            "테이트 모던": "Tate Modern", 
            "루브르 박물관": "Louvre Museum",
            "우피치 미술관": "Uffizi Gallery",
            "메트로폴리탄 미술관": "Metropolitan Museum of Art",
            "프라도 미술관": "Prado Museum"
        }
        
        # Get all available museum names
        all_museums = self.get_museum_names()
        
        # Separate major museums and others
        self.available_major_museums = {}
        self.other_museums = []
        
        for korean_name, english_name in self.major_museums.items():
            # Check if this museum exists in our data
            for museum in all_museums:
                if english_name.lower() in museum.lower() or korean_name.lower() in museum.lower():
                    self.available_major_museums[korean_name] = museum
                    break
        
        # Get other museums (not in major list)
        major_english_names = [name.lower() for name in self.major_museums.values()]
        for museum in all_museums:
            is_major = False
            for major_name in major_english_names:
                if major_name in museum.lower():
                    is_major = True
                    break
            if not is_major:
                self.other_museums.append(museum)
    
    def load_data(self) -> None:
        """Load metrics, comparison, and enhanced posts data from JSON files."""
        try:
            with open(self.metrics_path, 'r', encoding='utf-8') as f:
                self.metrics_data = json.load(f)
            
            with open(self.comparison_path, 'r', encoding='utf-8') as f:
                self.comparison_data = json.load(f)
            
            with open(self.enhanced_posts_path, 'r', encoding='utf-8') as f:
                self.enhanced_posts_data = json.load(f)
        except FileNotFoundError as e:
            if is_running_in_streamlit():
                st.error(f"Data file not found: {e}")
                st.stop()
            else:
                raise
        except json.JSONDecodeError as e:
            if is_running_in_streamlit():
                st.error(f"Invalid JSON data: {e}")
                st.stop()
            else:
                raise
    
    def get_museum_names(self) -> List[str]:
        """Get list of available museum names."""
        if not self.metrics_data:
            return []
        return [museum['museum'] for museum in self.metrics_data]
    
    def get_museum_data(self, museum_name: str) -> Optional[Dict[str, Any]]:
        """Get data for a specific museum."""
        if not self.metrics_data:
            return None
        
        for museum in self.metrics_data:
            if museum['museum'] == museum_name:
                return museum
        return None
    
    def get_museum_posts(self, museum_name: str) -> List[Dict[str, Any]]:
        """Get posts for a specific museum."""
        if not self.enhanced_posts_data:
            return []
        
        # Filter posts by museum name (case-insensitive)
        museum_posts = []
        for post in self.enhanced_posts_data:
            title = post.get('title', '') or ''
            content = post.get('content', '') or ''
            if museum_name.lower() in title.lower() or \
               museum_name.lower() in content.lower():
                museum_posts.append(post)
        return museum_posts
    
    def create_overview_metrics(self, museum_data: Dict[str, Any]) -> None:
        """Display overview metrics for selected museum."""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Posts",
                value=museum_data['total_posts']
            )
        
        with col2:
            st.metric(
                label="Total Replies",
                value=museum_data['total_replies']
            )
        
        with col3:
            total_reactions = museum_data['positive_reactions'] + museum_data['negative_reactions'] + museum_data['neutral_reactions']
            st.metric(
                label="Total Reactions",
                value=total_reactions
            )
        
        with col4:
            st.metric(
                label="Sentiment Score",
                value=f"{museum_data['audio_guide_sentiment_score']:.3f}"
            )
    
    def create_sentiment_chart(self, museum_data: Dict[str, Any]) -> None:
        """Create sentiment distribution chart."""
        sentiment_data = {
            'Sentiment': ['Positive', 'Negative', 'Neutral'],
            'Count': [
                museum_data['positive_reactions'],
                museum_data['negative_reactions'],
                museum_data['neutral_reactions']
            ]
        }
        
        df = pd.DataFrame(sentiment_data)
        
        fig = px.pie(
            df,
            values='Count',
            names='Sentiment',
            title=f"Audio Guide Sentiment Distribution - {museum_data['museum']}",
            color_discrete_map={
                'Positive': '#2E8B57',
                'Negative': '#DC143C',
                'Neutral': '#FFD700'
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def create_engagement_chart(self, museum_data: Dict[str, Any]) -> None:
        """Create user engagement chart."""
        user_engagement = museum_data.get('user_engagement', {})
        
        if not user_engagement:
            st.info("No user engagement data available for this museum.")
            return
        
        # Get top 10 users by engagement
        top_users = sorted(user_engagement.items(), key=lambda x: x[1], reverse=True)[:10]
        
        df = pd.DataFrame(top_users, columns=['User', 'Posts'])
        
        fig = px.bar(
            df,
            x='User',
            y='Posts',
            title=f"Top Users by Engagement - {museum_data['museum']}",
            color='Posts',
            color_continuous_scale='viridis'
        )
        
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    def create_themes_chart(self, museum_data: Dict[str, Any]) -> None:
        """Create common themes chart."""
        themes = museum_data.get('common_themes', [])
        
        if not themes:
            st.info("No common themes data available for this museum.")
            return
        
        # Count theme occurrences
        theme_counts = {}
        for theme in themes:
            theme_counts[theme] = theme_counts.get(theme, 0) + 1
        
        df = pd.DataFrame([
            {'Theme': k, 'Count': v} 
            for k, v in theme_counts.items()
        ])
        
        fig = px.bar(
            df,
            x='Theme',
            y='Count',
            title=f"Common Themes - {museum_data['museum']}",
            color='Count',
            color_continuous_scale='plasma'
        )
        
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    def create_museum_comparison(self) -> None:
        """Create comparison chart across all museums."""
        if not self.metrics_data:
            return
        
        df = pd.DataFrame(self.metrics_data)
        
        # Create subplots for different metrics
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Total Posts', 'Sentiment Score', 'Total Replies', 'Total Reactions'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Total Posts
        fig.add_trace(
            go.Bar(x=df['museum'], y=df['total_posts'], name='Total Posts'),
            row=1, col=1
        )
        
        # Sentiment Score
        fig.add_trace(
            go.Bar(x=df['museum'], y=df['audio_guide_sentiment_score'], name='Sentiment Score'),
            row=1, col=2
        )
        
        # Total Replies
        fig.add_trace(
            go.Bar(x=df['museum'], y=df['total_replies'], name='Total Replies'),
            row=2, col=1
        )
        
        # Total Reactions
        total_reactions = df['positive_reactions'] + df['negative_reactions'] + df['neutral_reactions']
        fig.add_trace(
            go.Bar(x=df['museum'], y=total_reactions, name='Total Reactions'),
            row=2, col=2
        )
        
        fig.update_layout(
            height=600,
            title_text="Museum Comparison Metrics",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def create_posts_table(self, posts: List[Dict[str, Any]], text_search: str = "") -> None:
        """Display posts in a table format."""
        if not posts:
            st.info("No posts available for this museum.")
            return
        
        # Prepare data for table
        table_data = []
        for post in posts:
            table_data.append({
                'Title': post.get('title', 'No Title'),
                'Sentiment': post.get('sentiment', 'neutral'),
                'Sentiment Score': f"{post.get('sentiment_score', 0):.3f}",
                'Audio Guide Mention': 'Yes' if post.get('audio_guide_mention') else 'No',
                'URL': post.get('url', 'No URL'),
                'Content': post.get('content', 'No content available')
            })
        
        df = pd.DataFrame(table_data)
        
        # Display the table with post content in a more user-friendly way
        st.markdown("### 📝 Individual Posts")
        st.markdown("Click on any post to view the full details.")
        
        # Create an interactive table with expandable post content
        for idx, row in df.iterrows():
            with st.expander(f"📝 {row['Title']} - Sentiment: {row['Sentiment']}"):
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown(f"**Title:** {row['Title']}")
                    st.markdown(f"**Sentiment:** {row['Sentiment']}")
                    st.markdown(f"**Sentiment Score:** {row['Sentiment Score']}")
                
                with col2:
                    st.markdown(f"**Audio Guide Mention:** {row['Audio Guide Mention']}")
                    st.markdown(f"**URL:** [{row['URL']}]({row['URL']})")
                
                st.markdown("---")
                st.markdown("**Content:**")
                
                # Highlight search terms if text search is active
                content = row['Content']
                if text_search and text_search.strip():
                    search_term = text_search.lower().strip()
                    if search_term in content.lower():
                        # Simple highlighting by making the text bold where it matches
                        highlighted_text = content.replace(
                            search_term, f"**{search_term}**"
                        )
                        st.markdown(f"*{highlighted_text}*")
                    else:
                        st.markdown(f"*{content}*")
                else:
                    st.markdown(f"*{content}*")
                
                # Show replies if available
                replies = posts[idx].get('replies', [])
                if replies:
                    st.markdown("**Replies:**")
                    for reply in replies[:3]:  # Show first 3 replies
                        st.markdown(f"- **{reply.get('author', 'Unknown')}**: {reply.get('content', 'No content')}")
                    if len(replies) > 3:
                        st.markdown(f"... and {len(replies) - 3} more replies")
        
        # Also show a compact table for quick reference
        st.markdown("### 📊 Quick Reference Table")
        st.markdown("Compact view for quick scanning.")
        # Remove the content column for the compact view
        compact_df = df.drop('Content', axis=1)
        st.dataframe(compact_df, use_container_width=True)
    
    def get_comparison_summary(self) -> None:
        """Display the comparison summary from the comparison data."""
        if not self.comparison_data:
            return
        
        summary = self.comparison_data.get('summary', {})
        
        st.markdown("### 📊 Overall Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Museums", summary.get('total_museums', 0))
        
        with col2:
            st.metric("Total Posts", summary.get('total_posts', 0))
        
        with col3:
            st.metric("Total Replies", summary.get('total_replies', 0))
        
        with col4:
            st.metric("Audio Guide Mentions", summary.get('total_audio_guide_mentions', 0))
    
    def get_top_museums_by_engagement(self) -> None:
        """Display top museums by engagement."""
        if not self.comparison_data:
            return
        
        top_museums = self.comparison_data.get('top_museums_by_engagement', [])
        
        if not top_museums:
            return
        
        st.markdown("### 🏆 Top Museums by Engagement")
        
        df = pd.DataFrame(top_museums)
        
        fig = px.bar(
            df,
            x='museum',
            y='total_engagement',
            title="Top Museums by Total Engagement",
            color='total_engagement',
            color_continuous_scale='viridis'
        )
        
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    def get_top_museums_by_sentiment(self) -> None:
        """Display top museums by sentiment."""
        if not self.comparison_data:
            return
        
        top_museums = self.comparison_data.get('top_museums_by_sentiment', [])
        
        if not top_museums:
            return
        
        st.markdown("### 😊 Top Museums by Sentiment Score")
        
        df = pd.DataFrame(top_museums)
        
        fig = px.bar(
            df,
            x='museum',
            y='sentiment_score',
            title="Top Museums by Sentiment Score",
            color='sentiment_score',
            color_continuous_scale='plasma'
        )
        
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    def get_theme_distribution(self) -> None:
        """Display theme distribution."""
        if not self.comparison_data:
            return
        
        theme_dist = self.comparison_data.get('theme_distribution', {})
        
        if not theme_dist:
            return
        
        st.markdown("### 🏷️ Theme Distribution")
        
        df = pd.DataFrame([
            {'Theme': k, 'Count': v} 
            for k, v in theme_dist.items()
        ])
        
        fig = px.bar(
            df,
            x='Theme',
            y='Count',
            title="Theme Distribution Across All Museums",
            color='Count',
            color_continuous_scale='viridis'
        )
        
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    def run(self) -> None:
        """Run the main dashboard application."""
        st.set_page_config(
            page_title="Rick Steves Audio Guide Analysis",
            page_icon="🎧",
            layout="wide"
        )
        
        st.title("🎧 Rick Steves Audio Guide Analysis Dashboard")
        st.markdown("---")
        
        # Sidebar for navigation
        st.sidebar.title("🎧 Museum Selection")
        
        # Museum selection with categories
        if self.available_major_museums:
            st.sidebar.markdown("### 🏛️ Major Museums")
            major_museum_options = list(self.available_major_museums.keys())
            selected_major = st.sidebar.selectbox(
                "Select Major Museum",
                ["-- Select Major Museum --"] + major_museum_options,
                index=0
            )
            
            if selected_major != "-- Select Major Museum --":
                selected_museum = self.available_major_museums[selected_major]
            else:
                selected_museum = None
        else:
            selected_museum = None
        
        # Other museums section
        if self.other_museums:
            st.sidebar.markdown("### 📚 Other Museums")
            other_museum_options = ["-- Select Other Museum --"] + self.other_museums
            selected_other = st.sidebar.selectbox(
                "Select Other Museum",
                other_museum_options,
                index=0
            )
            
            if selected_other != "-- Select Other Museum --":
                selected_museum = selected_other
            elif selected_museum is None:
                selected_museum = None
        
        # Add statistics to sidebar
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📊 Statistics")
        st.sidebar.markdown(f"**Total Museums:** {len(self.get_museum_names())}")
        st.sidebar.markdown(f"**Major Museums:** {len(self.available_major_museums)}")
        st.sidebar.markdown(f"**Other Museums:** {len(self.other_museums)}")
        
        if selected_museum:
            museum_data = self.get_museum_data(selected_museum)
            if museum_data:
                st.sidebar.markdown("---")
                st.sidebar.markdown("### 🎯 Selected Museum")
                st.sidebar.markdown(f"**Name:** {selected_museum}")
                st.sidebar.markdown(f"**Posts:** {museum_data.get('total_posts', 0)}")
                st.sidebar.markdown(f"**Replies:** {museum_data.get('total_replies', 0)}")
                st.sidebar.markdown(f"**Sentiment:** {museum_data.get('audio_guide_sentiment_score', 0):.3f}")
        
        if not selected_museum:
            st.warning("Please select a museum from the sidebar.")
            return
        
        # Main content area
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Overview", 
            "🎯 Analysis", 
            "📋 Posts", 
            "🏛️ Comparison",
            "📈 Global Insights"
        ])
        
        museum_data = self.get_museum_data(selected_museum)
        if not museum_data:
            st.error(f"Data not found for {selected_museum}")
            return
        
        with tab1:
            st.header(f"Overview - {selected_museum}")
            
            self.create_overview_metrics(museum_data)
            
            st.markdown("### Key Insights")
            total_reactions = museum_data['positive_reactions'] + museum_data['negative_reactions'] + museum_data['neutral_reactions']
            st.markdown(f"""
            - **Total Posts Analyzed:** {museum_data['total_posts']}
            - **Total Replies:** {museum_data['total_replies']}
            - **Total Reactions:** {total_reactions}
            - **Overall Sentiment:** {'Positive' if museum_data['audio_guide_sentiment_score'] > 0.1 else 'Neutral' if museum_data['audio_guide_sentiment_score'] > -0.1 else 'Negative'}
            - **Sentiment Score:** {museum_data['audio_guide_sentiment_score']:.3f}
            """)
        
        with tab2:
            st.header(f"Analysis - {selected_museum}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                self.create_sentiment_chart(museum_data)
            
            with col2:
                self.create_engagement_chart(museum_data)
            
            st.markdown("### Common Themes")
            self.create_themes_chart(museum_data)
        
        with tab3:
            st.header(f"Posts - {selected_museum}")
            
            posts = self.get_museum_posts(selected_museum)
            
            # Summary at the top
            st.markdown("### 📊 Posts Summary")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_posts = len(posts)
                st.metric("Total Posts", total_posts)
            
            with col2:
                audio_mentions = len([p for p in posts if p.get('audio_guide_mention')])
                st.metric("Audio Guide Mentions", audio_mentions)
            
            with col3:
                positive_posts = len([p for p in posts if p.get('sentiment') == 'positive'])
                st.metric("Positive Posts", positive_posts)
            
            with col4:
                avg_sentiment = sum(p.get('sentiment_score', 0) for p in posts) / max(1, len(posts))
                st.metric("Average Sentiment", f"{avg_sentiment:.3f}")
            
            st.markdown("---")
            
            # Filter options
            st.markdown("### 🔍 Filter Options")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                show_audio_mentions = st.checkbox("Show only audio guide mentions", value=False)
            
            with col2:
                sentiment_filter = st.selectbox(
                    "Sentiment filter",
                    ["All", "Positive", "Negative", "Neutral"]
                )
            
            with col3:
                min_sentiment = st.slider("Minimum sentiment score", -1.0, 1.0, -1.0, 0.1)
            
            with col4:
                text_search = st.text_input("Search in post content", placeholder="Enter keywords...")
            
            # Apply filters
            filtered_posts = posts
            if show_audio_mentions:
                filtered_posts = [p for p in filtered_posts if p.get('audio_guide_mention')]
            
            filtered_posts = [p for p in filtered_posts if p.get('sentiment_score', 0) >= min_sentiment]
            
            if sentiment_filter != "All":
                filtered_posts = [p for p in filtered_posts if p.get('sentiment') == sentiment_filter.lower()]
            
            # Apply text search filter
            if text_search and text_search.strip():
                search_term = text_search.lower().strip()
                filtered_posts = [
                    p for p in filtered_posts 
                    if search_term in (p.get('content', '') or '').lower() or search_term in (p.get('title', '') or '').lower()
                ]
            
            st.markdown(f"**📋 Showing {len(filtered_posts)} of {len(posts)} posts**")
            self.create_posts_table(filtered_posts, text_search)
        
        with tab4:
            st.header("Museum Comparison")
            self.create_museum_comparison()
            
            st.markdown("### Summary Statistics")
            if self.metrics_data:
                summary_df = pd.DataFrame(self.metrics_data)
                st.dataframe(summary_df, use_container_width=True)
        
        with tab5:
            st.header("Global Insights")
            
            self.get_comparison_summary()
            
            col1, col2 = st.columns(2)
            
            with col1:
                self.get_top_museums_by_engagement()
            
            with col2:
                self.get_top_museums_by_sentiment()
            
            self.get_theme_distribution()


def main():
    """Main function to run the dashboard."""
    # Initialize dashboard
    dashboard = RickStevesDashboard(
        metrics_path="../transform/audio_guide_metrics.json",
        comparison_path="../transform/museum_comparison.json",
        enhanced_posts_path="../transform/enhanced_posts.json"
    )
    
    # Run dashboard
    dashboard.run()


if __name__ == "__main__":
    main() 