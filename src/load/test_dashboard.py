#!/usr/bin/env python3
"""
Test script for Rick Steves Audio Guide Dashboard

This script tests the dashboard data loading and basic functionality.
"""

from dashboard import RickStevesDashboard
import json

def test_data_loading():
    """Test that all data files can be loaded correctly."""
    print("🎧 Testing Rick Steves Audio Guide Dashboard...")
    
    try:
        # Initialize dashboard
        dashboard = RickStevesDashboard(
            metrics_path="../transform/audio_guide_metrics.json",
            comparison_path="../transform/museum_comparison.json",
            enhanced_posts_path="../transform/enhanced_posts.json"
        )
        
        print("✅ Dashboard initialized successfully")
        
        # Test museum names
        museum_names = dashboard.get_museum_names()
        print(f"✅ Found {len(museum_names)} museums")
        print(f"   First 5 museums: {museum_names[:5]}")
        
        # Test getting museum data
        if museum_names:
            first_museum = museum_names[0]
            museum_data = dashboard.get_museum_data(first_museum)
            if museum_data:
                print(f"✅ Successfully loaded data for {first_museum}")
                print(f"   - Total posts: {museum_data.get('total_posts', 0)}")
                print(f"   - Total replies: {museum_data.get('total_replies', 0)}")
                print(f"   - Sentiment score: {museum_data.get('audio_guide_sentiment_score', 0):.3f}")
        
        # Test getting posts
        if museum_names:
            posts = dashboard.get_museum_posts(first_museum)
            print(f"✅ Found {len(posts)} posts for {first_museum}")
        
        # Test comparison data
        if dashboard.comparison_data:
            summary = dashboard.comparison_data.get('summary', {})
            print(f"✅ Comparison data loaded")
            print(f"   - Total museums: {summary.get('total_museums', 0)}")
            print(f"   - Total posts: {summary.get('total_posts', 0)}")
            print(f"   - Total replies: {summary.get('total_replies', 0)}")
        
        print("\n🎉 All tests passed! Dashboard is ready to run.")
        print("Run 'python run_dashboard.py' to start the dashboard.")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_data_loading() 