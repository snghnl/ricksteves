"""
Main transform script for Rick Steves audio guide forum data

This script loads the Rick Steves forum data and performs audio guide analysis,
generating metrics and insights about audio guide reactions across different museums.
"""

import json
import sys
from pathlib import Path
from audio_guide_analyzer import RickStevesAudioGuideAnalyzer


def main():
    """Main function to run the transform process"""
    
    # Input and output file paths
    input_file = Path("../../data/posts_audio_guide_detail.json")
    output_file = Path("audio_guide_metrics.json")
    comparison_file = Path("museum_comparison.json")
    enhanced_posts_file = Path("enhanced_posts.json")
    
    # Check if input file exists
    if not input_file.exists():
        print(f"Error: Input file {input_file} not found")
        sys.exit(1)
    
    # Initialize analyzer
    analyzer = RickStevesAudioGuideAnalyzer()
    
    try:
        # Load data
        print("Loading Rick Steves forum data...")
        analyzer.load_data(input_file)
        print(f"Loaded data for {len(analyzer.data)} posts")
        
        # Analyze all museums
        print("Analyzing audio guide reactions...")
        metrics = analyzer.analyze_all_museums()
        
        # Save metrics
        print("Saving analysis metrics...")
        analyzer.save_metrics(output_file)
        
        # Save enhanced posts with sentiment analysis
        print("Creating enhanced posts with sentiment analysis...")
        analyzer.save_enhanced_posts(enhanced_posts_file)
        
        # Generate and save comparison
        print("Generating museum comparison...")
        comparison = analyzer.get_museum_comparison()
        
        with open(comparison_file, 'w', encoding='utf-8') as f:
            json.dump(comparison, f, indent=2, ensure_ascii=False, default=str)
        
        # Print summary
        print("\n=== Analysis Summary ===")
        print(f"Total museums analyzed: {len(metrics)}")
        print(f"Total posts processed: {sum(m.total_posts for m in metrics)}")
        print(f"Total replies processed: {sum(m.total_replies for m in metrics)}")
        print(f"Total audio guide reactions: {sum(m.positive_reactions + m.negative_reactions + m.neutral_reactions for m in metrics)}")
        
        print("\n=== Sentiment Distribution ===")
        total_positive = sum(m.positive_reactions for m in metrics)
        total_negative = sum(m.negative_reactions for m in metrics)
        total_neutral = sum(m.neutral_reactions for m in metrics)
        total_reactions = total_positive + total_negative + total_neutral
        
        if total_reactions > 0:
            print(f"Positive: {total_positive} ({total_positive/total_reactions*100:.1f}%)")
            print(f"Negative: {total_negative} ({total_negative/total_reactions*100:.1f}%)")
            print(f"Neutral: {total_neutral} ({total_neutral/total_reactions*100:.1f}%)")
        
        print("\n=== Top Museums by Audio Guide Sentiment Score ===")
        sorted_metrics = sorted(metrics, key=lambda x: x.audio_guide_sentiment_score, reverse=True)
        for i, metric in enumerate(sorted_metrics[:5], 1):
            print(f"{i}. {metric.museum} ({metric.forum}): {metric.audio_guide_sentiment_score:.3f}")
        
        print("\n=== Museums with Most Audio Guide Reactions ===")
        sorted_by_reactions = sorted(
            metrics, 
            key=lambda x: x.positive_reactions + x.negative_reactions + x.neutral_reactions, 
            reverse=True
        )
        for i, metric in enumerate(sorted_by_reactions[:5], 1):
            total_reactions = metric.positive_reactions + metric.negative_reactions + metric.neutral_reactions
            print(f"{i}. {metric.museum} ({metric.forum}): {total_reactions} reactions")
        
        print("\n=== Forum Distribution ===")
        forum_counts = {}
        for metric in metrics:
            forum = metric.forum
            if forum not in forum_counts:
                forum_counts[forum] = 0
            forum_counts[forum] += 1
        
        for forum, count in sorted(forum_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"{forum}: {count} museums")
        
        print("\n=== Common Themes ===")
        all_themes = []
        for metric in metrics:
            all_themes.extend(metric.common_themes)
        
        theme_counts = {}
        for theme in all_themes:
            if theme not in theme_counts:
                theme_counts[theme] = 0
            theme_counts[theme] += 1
        
        for theme, count in sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"{theme}: {count} mentions")
        
        print(f"\nResults saved to:")
        print(f"- Metrics: {output_file}")
        print(f"- Comparison: {comparison_file}")
        print(f"- Enhanced Posts: {enhanced_posts_file}")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 