from typing import Dict, Literal, Any
import re

# === Sentiment Analysis Service ===

def analyze_sentiment(review: str) -> Dict[str, Any]:
    """
    Analyze sentiment of a review text.
    Returns sentiment (positive, negative, neutral) and star_rating (1-5).
    
    Args:
        review: Review text to analyze
        
    Returns:
        Dictionary with 'sentiment' and 'star_rating' keys
    """
    if not review or not review.strip():
        return {"sentiment": "neutral", "star_rating": 3}
    
    review_lower = review.lower().strip()
    
    # Positive keywords and phrases
    positive_patterns = [
        r'\b(excellent|amazing|great|wonderful|fantastic|delicious|love|perfect|best|awesome|outstanding|superb|tasty|yummy|satisfied|happy|pleased|recommend|highly|very good|really good)\b',
        r'\b(5|five)\s*(star|stars)\b',
        r'\b(10/10|9/10|8/10)\b',
    ]
    
    # Negative keywords and phrases
    negative_patterns = [
        r'\b(terrible|awful|horrible|bad|worst|disgusting|hate|disappointed|poor|unacceptable|inedible|waste|regret|never again|avoid|disgusting|nasty|sick)\b',
        r'\b(1|one)\s*(star|stars)\b',
        r'\b(0/10|1/10|2/10)\b',
    ]
    
    # Count positive and negative matches
    positive_count = sum(len(re.findall(pattern, review_lower)) for pattern in positive_patterns)
    negative_count = sum(len(re.findall(pattern, review_lower)) for pattern in negative_patterns)
    
    # Determine sentiment
    if positive_count > negative_count:
        sentiment = "positive"
        # Map to star rating: more positive matches = higher rating
        if positive_count >= 3:
            star_rating = 5
        elif positive_count >= 2:
            star_rating = 4
        else:
            star_rating = 4
    elif negative_count > positive_count:
        sentiment = "negative"
        # Map to star rating: more negative matches = lower rating
        if negative_count >= 3:
            star_rating = 1
        elif negative_count >= 2:
            star_rating = 2
        else:
            star_rating = 2
    else:
        # Neutral or balanced
        sentiment = "neutral"
        star_rating = 3
    
    return {
        "sentiment": sentiment,
        "star_rating": star_rating
    }

