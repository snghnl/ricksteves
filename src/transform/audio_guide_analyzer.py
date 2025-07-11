"""
Audio Guide Analyzer for Rick Steves Forum Data

This module processes Rick Steves forum data to analyze audio guide reactions
and calculate various metrics for audio guide quality assessment across different museums.
"""

import json
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import Counter
from datetime import datetime


@dataclass
class AudioGuideMetrics:
    """Metrics for audio guide analysis"""
    museum: str
    forum: str
    total_posts: int
    total_replies: int
    positive_reactions: int
    negative_reactions: int
    neutral_reactions: int
    audio_guide_sentiment_score: float
    common_themes: List[str]
    user_engagement: Dict[str, int]
    time_distribution: Dict[str, int]


class RickStevesAudioGuideAnalyzer:
    """Analyzes audio guide reactions from Rick Steves forum data"""
    
    # Positive keywords related to audio guides
    POSITIVE_KEYWORDS = [
        'excellent', 'great', 'good', 'helpful', 'useful', 'essential', 
        'recommended', 'worth', 'amazing', 'fantastic', 'perfect', 'love',
        'enjoy', 'informative', 'educational', 'clear', 'easy', 'convenient',
        'well-made', 'professional', 'comprehensive', 'detailed', 'insightful',
        'wonderful', 'outstanding', 'superb', 'brilliant', 'impressive',
        'thank', 'thanks', 'helpful', 'good', 'nice', 'better', 'best'
    ]
    
    # Negative keywords related to audio guides
    NEGATIVE_KEYWORDS = [
        'bad', 'terrible', 'awful', 'horrible', 'useless', 'waste', 
        'disappointing', 'confusing', 'complicated', 'difficult', 'hard',
        'annoying', 'frustrating', 'broken', 'not working', 'missing',
        'outdated', 'poor', 'weak', 'limited', 'inadequate', 'overpriced',
        'expensive', 'rip-off', 'scam', 'trash', 'garbage', 'rubbish',
        'disaster', 'nightmare', 'awful', 'dreadful', 'miserable', 'no',
        'problem', 'issue', 'trouble', 'difficult', 'confusing'
    ]
    
    # Audio guide related terms
    AUDIO_GUIDE_TERMS = [
        'audio guide', 'audioguide', 'audio tour', 'audio commentary',
        'guided tour', 'audio device', 'headphones', 'audio app',
        'audio recording', 'audio explanation', 'audio description',
        'audio', 'guide', 'tour'
    ]
    
    # Museum name mappings for better categorization
    MUSEUM_MAPPINGS = {
        'prado': 'Museo del Prado',
        'vatican': 'Vatican Museums',
        'louvre': 'Louvre Museum',
        'british museum': 'British Museum',
        'metropolitan': 'Metropolitan Museum of Art',
        'uffizi': 'Uffizi Gallery',
        'tate': 'Tate Modern',
        'alhambra': 'Alhambra',
        'colosseum': 'Colosseum',
        'pompeii': 'Pompeii',
        'herculaneum': 'Herculaneum',
        'borghese': 'Borghese Gallery',
        'medici': 'Medici Riccardi Palace',
        'tower of london': 'Tower of London',
        'edinburgh castle': 'Edinburgh Castle',
        'ostia': 'Ostia Antica',
        'accademia': 'Accademia Gallery',
        'bargello': 'Bargello Museum',
        'duomo': 'Duomo Museum',
        'milan duomo': 'Milan Duomo',
        'florence': 'Florence Museums',
        'olympia': 'Olympia',
        'budapest': 'Budapest Museums'
    }
    
    def __init__(self):
        self.data = []
        self.metrics = []
    
    def load_data(self, file_path: str) -> None:
        """Load Rick Steves forum data from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
    
    def extract_museum_name(self, title: str, content: str = "") -> str:
        """Extract museum name from post title and content"""
        # Handle None values
        title = title or ""
        content = content or ""
        
        text = f"{title} {content}".lower()
        
        # Check for specific museum names
        for key, museum_name in self.MUSEUM_MAPPINGS.items():
            if key in text:
                return museum_name
        
        # Extract from title if it contains museum-related terms
        title_lower = title.lower()
        if 'museum' in title_lower:
            # Extract the part before 'museum'
            parts = title_lower.split('museum')
            if parts[0].strip():
                return parts[0].strip().title() + ' Museum'
        
        # Check for other cultural sites
        if 'gallery' in title_lower:
            parts = title_lower.split('gallery')
            if parts[0].strip():
                return parts[0].strip().title() + ' Gallery'
        
        if 'palace' in title_lower:
            parts = title_lower.split('palace')
            if parts[0].strip():
                return parts[0].strip().title() + ' Palace'
        
        if 'castle' in title_lower:
            parts = title_lower.split('castle')
            if parts[0].strip():
                return parts[0].strip().title() + ' Castle'
        
        return "Unknown Museum"
    
    def extract_audio_guide_mentions(self, text: str) -> bool:
        """Check if text mentions audio guide"""
        # Handle None values
        text = text or ""
        text_lower = text.lower()
        return any(term in text_lower for term in self.AUDIO_GUIDE_TERMS)
    
    def analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of audio guide mentions"""
        # Handle None values
        text = text or ""
        text_lower = text.lower()
        
        positive_count = sum(1 for word in self.POSITIVE_KEYWORDS if word in text_lower)
        negative_count = sum(1 for word in self.NEGATIVE_KEYWORDS if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def calculate_sentiment_score(self, text: str) -> float:
        """Calculate detailed sentiment score for a single post/reply"""
        # Handle None values
        text = text or ""
        text_lower = text.lower()
        
        # Count positive and negative keywords
        positive_count = sum(1 for word in self.POSITIVE_KEYWORDS if word in text_lower)
        negative_count = sum(1 for word in self.NEGATIVE_KEYWORDS if word in text_lower)
        
        # Calculate base score
        if positive_count > negative_count:
            base_score = 1.0
        elif negative_count > positive_count:
            base_score = -1.0
        else:
            base_score = 0.0
        
        # Normalize by text length to avoid bias towards longer texts
        text_length = len(text.split())
        if text_length > 0:
            normalized_score = base_score / (text_length ** 0.5)
        else:
            normalized_score = base_score
        
        return normalized_score
    
    def extract_common_themes(self, posts: List[Dict]) -> List[str]:
        """Extract common themes from audio guide mentions"""
        themes = []
        
        for post in posts:
            title = post.get('title', '')
            content = post.get('content', '')
            replies = post.get('replies', [])
            
            # Check main post title and content
            if self.extract_audio_guide_mentions(title) or self.extract_audio_guide_mentions(content):
                text = f"{title} {content}".lower()
                self._extract_themes_from_text(text, themes)
            
            # Check reply content
            for reply in replies:
                reply_content = reply.get('content', '')
                if self.extract_audio_guide_mentions(reply_content):
                    text = reply_content.lower()
                    self._extract_themes_from_text(text, themes)
        
        # Return most common themes
        theme_counts = Counter(themes)
        return [theme for theme, count in theme_counts.most_common(10)]
    
    def _extract_themes_from_text(self, text: str, themes: List[str]) -> None:
        """Helper method to extract themes from text"""
        if 'app' in text or 'application' in text or 'smartphone' in text:
            themes.append('mobile app')
        if 'device' in text or 'headphones' in text or 'rent' in text:
            themes.append('physical device')
        if 'free' in text or 'no cost' in text or 'included' in text:
            themes.append('free service')
        if 'paid' in text or 'cost' in text or 'expensive' in text or 'rent' in text:
            themes.append('paid service')
        if 'language' in text or 'translation' in text or 'english' in text:
            themes.append('multilingual')
        if 'complicated' in text or 'difficult' in text or 'confusing' in text:
            themes.append('complexity issues')
        if 'missing' in text or 'not available' in text or 'no longer' in text:
            themes.append('availability issues')
        if 'rick steves' in text or 'rs' in text:
            themes.append('rick steves guide')
        if 'download' in text or 'online' in text:
            themes.append('digital download')
        if 'reservation' in text or 'advance' in text or 'book' in text:
            themes.append('advance booking')
        if 'quality' in text or 'sound' in text or 'audio' in text:
            themes.append('audio quality')
        if 'time' in text or 'duration' in text or 'length' in text:
            themes.append('time management')
        if 'guided tour' in text or 'tour guide' in text:
            themes.append('guided tours')
        if 'skip the line' in text or 'skip line' in text:
            themes.append('skip the line')
    
    def extract_user_engagement(self, posts: List[Dict]) -> Dict[str, int]:
        """Extract user engagement metrics"""
        user_posts = Counter()
        user_replies = Counter()
        
        for post in posts:
            # Count main posts (assuming they have an author field)
            if 'author' in post:
                user_posts[post['author']] += 1
            
            # Count replies
            replies = post.get('replies', [])
            for reply in replies:
                author = reply.get('author', 'Unknown')
                user_replies[author] += 1
        
        # Combine post and reply counts
        total_engagement = {}
        for user in set(user_posts.keys()) | set(user_replies.keys()):
            total_engagement[user] = user_posts[user] + user_replies[user]
        
        return dict(total_engagement)
    
    def extract_time_distribution(self, posts: List[Dict]) -> Dict[str, int]:
        """Extract time distribution of posts"""
        time_distribution = Counter()
        
        for post in posts:
            time_str = post.get('time', '')
            if time_str:
                # Extract year from time string
                year_match = re.search(r'(\d{4})', time_str)
                if year_match:
                    year = year_match.group(1)
                    time_distribution[year] += 1
                else:
                    # Handle relative time strings
                    if 'years ago' in time_str:
                        # Extract number of years
                        years_match = re.search(r'(\d+)\s+years? ago', time_str)
                        if years_match:
                            years_ago = int(years_match.group(1))
                            # Estimate year (assuming current year is 2024)
                            estimated_year = 2024 - years_ago
                            time_distribution[str(estimated_year)] += 1
        
        return dict(time_distribution)
    
    def process_museum_data(self, museum_posts: List[Dict]) -> AudioGuideMetrics:
        """Process individual museum data and return metrics"""
        if not museum_posts:
            return AudioGuideMetrics(
                museum="Unknown",
                forum="Unknown",
                total_posts=0,
                total_replies=0,
                positive_reactions=0,
                negative_reactions=0,
                neutral_reactions=0,
                audio_guide_sentiment_score=0.0,
                common_themes=[],
                user_engagement={},
                time_distribution={}
            )
        
        # Calculate basic metrics
        total_posts = len(museum_posts)
        total_replies = sum(len(post.get('replies', [])) for post in museum_posts)
        
        # Analyze sentiment based on titles and content
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        total_sentiment_score = 0.0
        sentiment_count = 0
        
        for post in museum_posts:
            title = post.get('title', '')
            content = post.get('content', '')
            replies = post.get('replies', [])
            
            # Analyze main post title and content
            if self.extract_audio_guide_mentions(title) or self.extract_audio_guide_mentions(content):
                combined_text = f"{title} {content}"
                sentiment = self.analyze_sentiment(combined_text)
                if sentiment == 'positive':
                    positive_count += 1
                elif sentiment == 'negative':
                    negative_count += 1
                else:
                    neutral_count += 1
                
                score = self.calculate_sentiment_score(combined_text)
                total_sentiment_score += score
                sentiment_count += 1
            
            # Analyze replies
            for reply in replies:
                reply_content = reply.get('content', '')
                if self.extract_audio_guide_mentions(reply_content):
                    sentiment = self.analyze_sentiment(reply_content)
                    if sentiment == 'positive':
                        positive_count += 1
                    elif sentiment == 'negative':
                        negative_count += 1
                    else:
                        neutral_count += 1
                    
                    score = self.calculate_sentiment_score(reply_content)
                    total_sentiment_score += score
                    sentiment_count += 1
        
        # Calculate average sentiment score
        avg_sentiment_score = total_sentiment_score / sentiment_count if sentiment_count > 0 else 0.0
        
        # Extract additional metrics
        common_themes = self.extract_common_themes(museum_posts)
        user_engagement = self.extract_user_engagement(museum_posts)
        time_distribution = self.extract_time_distribution(museum_posts)
        
        # Get forum from first post
        forum = museum_posts[0].get('forum', 'Unknown') if museum_posts else 'Unknown'
        
        # Get museum name from first post
        museum_name = self.extract_museum_name(
            museum_posts[0].get('title', ''),
            museum_posts[0].get('content', '')
        ) if museum_posts else 'Unknown'
        
        return AudioGuideMetrics(
            museum=museum_name,
            forum=forum,
            total_posts=total_posts,
            total_replies=total_replies,
            positive_reactions=positive_count,
            negative_reactions=negative_count,
            neutral_reactions=neutral_count,
            audio_guide_sentiment_score=avg_sentiment_score,
            common_themes=common_themes,
            user_engagement=user_engagement,
            time_distribution=time_distribution
        )
    
    def group_posts_by_museum(self) -> Dict[str, List[Dict]]:
        """Group posts by museum name"""
        museum_groups = {}
        
        for post in self.data:
            museum_name = self.extract_museum_name(
                post.get('title', ''),
                post.get('content', '')
            )
            
            if museum_name not in museum_groups:
                museum_groups[museum_name] = []
            
            museum_groups[museum_name].append(post)
        
        return museum_groups
    
    def analyze_all_museums(self) -> List[AudioGuideMetrics]:
        """Analyze all museums in the dataset"""
        museum_groups = self.group_posts_by_museum()
        self.metrics = []
        
        for museum_name, posts in museum_groups.items():
            if posts:  # Only process if there are posts
                metrics = self.process_museum_data(posts)
                self.metrics.append(metrics)
        
        return self.metrics
    
    def save_metrics(self, output_file: str) -> None:
        """Save metrics to JSON file"""
        if not self.metrics:
            self.analyze_all_museums()
        
        metrics_data = []
        for metric in self.metrics:
            metrics_data.append({
                'museum': metric.museum,
                'forum': metric.forum,
                'total_posts': metric.total_posts,
                'total_replies': metric.total_replies,
                'positive_reactions': metric.positive_reactions,
                'negative_reactions': metric.negative_reactions,
                'neutral_reactions': metric.neutral_reactions,
                'audio_guide_sentiment_score': metric.audio_guide_sentiment_score,
                'common_themes': metric.common_themes,
                'user_engagement': metric.user_engagement,
                'time_distribution': metric.time_distribution
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(metrics_data, f, indent=2, ensure_ascii=False, default=str)
    
    def create_enhanced_posts_data(self) -> List[Dict]:
        """Create enhanced posts data with sentiment analysis"""
        enhanced_data = []
        
        for post in self.data:
            enhanced_post = post.copy()
            
            # Add sentiment analysis to main post
            title = post.get('title', '')
            content = post.get('content', '')
            combined_text = f"{title} {content}"
            
            if self.extract_audio_guide_mentions(combined_text):
                enhanced_post['audio_guide_mention'] = True
                enhanced_post['sentiment'] = self.analyze_sentiment(combined_text)
                enhanced_post['sentiment_score'] = self.calculate_sentiment_score(combined_text)
            else:
                enhanced_post['audio_guide_mention'] = False
                enhanced_post['sentiment'] = 'neutral'
                enhanced_post['sentiment_score'] = 0.0
            
            # Add sentiment analysis to replies
            enhanced_replies = []
            for reply in post.get('replies', []):
                enhanced_reply = reply.copy()
                reply_content = reply.get('content', '')
                
                if self.extract_audio_guide_mentions(reply_content):
                    enhanced_reply['audio_guide_mention'] = True
                    enhanced_reply['sentiment'] = self.analyze_sentiment(reply_content)
                    enhanced_reply['sentiment_score'] = self.calculate_sentiment_score(reply_content)
                else:
                    enhanced_reply['audio_guide_mention'] = False
                    enhanced_reply['sentiment'] = 'neutral'
                    enhanced_reply['sentiment_score'] = 0.0
                
                enhanced_replies.append(enhanced_reply)
            
            enhanced_post['replies'] = enhanced_replies
            enhanced_data.append(enhanced_post)
        
        return enhanced_data
    
    def save_enhanced_posts(self, output_file: str) -> None:
        """Save enhanced posts data with sentiment analysis"""
        enhanced_data = self.create_enhanced_posts_data()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, indent=2, ensure_ascii=False, default=str)
    
    def get_museum_comparison(self) -> Dict:
        """Generate museum comparison data"""
        if not self.metrics:
            self.analyze_all_museums()
        
        comparison = {
            'summary': {
                'total_museums': len(self.metrics),
                'total_posts': sum(m.total_posts for m in self.metrics),
                'total_replies': sum(m.total_replies for m in self.metrics),
                'total_audio_guide_mentions': sum(
                    m.positive_reactions + m.negative_reactions + m.neutral_reactions 
                    for m in self.metrics
                )
            },
            'top_museums_by_engagement': [],
            'top_museums_by_sentiment': [],
            'forum_distribution': {},
            'theme_distribution': {},
            'time_trends': {}
        }
        
        # Top museums by engagement
        sorted_by_engagement = sorted(
            self.metrics, 
            key=lambda x: x.total_posts + x.total_replies, 
            reverse=True
        )
        comparison['top_museums_by_engagement'] = [
            {
                'museum': m.museum,
                'forum': m.forum,
                'total_posts': m.total_posts,
                'total_replies': m.total_replies,
                'total_engagement': m.total_posts + m.total_replies
            }
            for m in sorted_by_engagement[:10]
        ]
        
        # Top museums by sentiment
        sorted_by_sentiment = sorted(
            self.metrics, 
            key=lambda x: x.audio_guide_sentiment_score, 
            reverse=True
        )
        comparison['top_museums_by_sentiment'] = [
            {
                'museum': m.museum,
                'forum': m.forum,
                'sentiment_score': m.audio_guide_sentiment_score,
                'positive_reactions': m.positive_reactions,
                'negative_reactions': m.negative_reactions
            }
            for m in sorted_by_sentiment[:10]
        ]
        
        # Forum distribution
        forum_counts = Counter(m.forum for m in self.metrics)
        comparison['forum_distribution'] = dict(forum_counts)
        
        # Theme distribution
        all_themes = []
        for m in self.metrics:
            all_themes.extend(m.common_themes)
        theme_counts = Counter(all_themes)
        comparison['theme_distribution'] = dict(theme_counts)
        
        # Time trends
        all_time_distributions = {}
        for m in self.metrics:
            for year, count in m.time_distribution.items():
                if year not in all_time_distributions:
                    all_time_distributions[year] = 0
                all_time_distributions[year] += count
        comparison['time_trends'] = all_time_distributions
        
        return comparison 