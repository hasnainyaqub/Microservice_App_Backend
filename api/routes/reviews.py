from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any, Literal
import json

from db.database import fetch_menu_with_reviews
from cache.redis_cache import get_reviews_menu_from_cache, store_reviews_menu_in_cache
from services.reviews import analyze_sentiment

# === Initialize API Router ===
router = APIRouter()

# === GET /reviews/menu endpoint ===
@router.get("/reviews/menu")
async def get_menu_with_reviews():
    """
    Fetch menu items with reviews.
    Uses cache first, falls back to DB, then stores in cache.
    """
    # Try cache first
    menu = await get_reviews_menu_from_cache()
    
    if menu is None:
        # Fallback to DB
        menu = await fetch_menu_with_reviews()
        
        # Store in cache
        if menu:
            await store_reviews_menu_in_cache(menu)
    
    return {
        "status": "success",
        "menu": menu or []
    }

# === WebSocket endpoint /reviews/ws/sentiment ===
@router.websocket("/reviews/ws/sentiment")
async def websocket_sentiment(websocket: WebSocket):
    """
    WebSocket endpoint for streaming reviews filtered by sentiment.
    
    Client sends:
    {
        "filter": "positive" | "negative"
    }
    
    Server streams back only matching sentiment reviews.
    """
    await websocket.accept()
    
    try:
        # Receive filter from client
        data = await websocket.receive_text()
        filter_data = json.loads(data)
        
        filter_type: Literal["positive", "negative"] = filter_data.get("filter")
        
        if filter_type not in ["positive", "negative"]:
            await websocket.send_json({
                "error": "Invalid filter. Must be 'positive' or 'negative'"
            })
            await websocket.close()
            return
        
        # Load menu data from cache or DB
        menu = await get_reviews_menu_from_cache()
        
        if menu is None:
            # Fallback to DB
            menu = await fetch_menu_with_reviews()
            
            # Store in cache
            if menu:
                await store_reviews_menu_in_cache(menu)
        
        if not menu:
            await websocket.send_json({
                "error": "No menu data available"
            })
            await websocket.close()
            return
        
        # Process each menu item and its reviews
        for item in menu:
            if "reviews" not in item or not item["reviews"]:
                continue
            
            # Analyze sentiment for each review
            for review in item["reviews"]:
                review_text = review.get("review", "")
                if not review_text:
                    continue
                
                # Analyze sentiment
                sentiment_result = analyze_sentiment(review_text)
                review_sentiment = sentiment_result.get("sentiment")
                
                # Only send reviews that match the filter
                if review_sentiment == filter_type:
                    # Send matching review with sentiment analysis
                    response = {
                        "item_id": item.get("id"),
                        "item_name": item.get("name"),
                        "item_category": item.get("category"),
                        "review": {
                            "id": review.get("id"),
                            "text": review_text,
                            "customer_name": review.get("customer_name"),
                            "date": review.get("date"),
                            "sentiment": review_sentiment,
                            "star_rating": sentiment_result.get("star_rating")
                        }
                    }
                    
                    await websocket.send_json(response)
        
        # Send completion message
        await websocket.send_json({
            "status": "complete",
            "message": f"Finished streaming {filter_type} reviews"
        })
        
    except json.JSONDecodeError:
        await websocket.send_json({
            "error": "Invalid JSON format"
        })
        await websocket.close()
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.send_json({
            "error": f"Server error: {str(e)}"
        })
        await websocket.close()

