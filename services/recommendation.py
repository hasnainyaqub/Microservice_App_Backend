import math
import json
from typing import List, Dict, Any

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from db.database import fetch_menu, fetch_recent_orders
from cache.redis_cache import get_menu_from_cache, store_menu_in_cache
from utils.scoring import mood_match, spice_match
from core.config import settings

# === Configuration ===

# Meal-specific priority lists for recommendation
MEAL_PRIORITY = {
    "breakfast": [
        "Sandwich", "Omelette", "Paratha", "Tea", "Coffee", "Milkshake", "Smoothie", "Pudding", "Muffin", "Tart"
    ],
    "lunch": [
        "Rice", "Karahi", "BBQ", "Pasta", "Salad", "Wrap", "Burger", "Chicken Wings", "Chicken Tenders", "Lasagna", "Ravioli"
    ],
    "dinner": [
        "Pizza", "Burger", "BBQ", "Dessert", "Pasta", "Salad", "Sandwich", "Appetizer", "Fries", "Onion Rings", "Nachos"
    ],
}

# Default priority if meal time is unknown
DEFAULT_PRIORITY = [
    "Pizza", "Burger", "Rice", "BBQ", "Dessert", "Pasta", "Sandwich", "Salad", "Fries", "Wings"
]

# Bundle templates based on number of people
BUNDLE_TEMPLATES = {
    "solo": {"main": 1, "side": 1, "drink": 1},
    "couple": {"main": 1, "side": 2, "drink": 2},
    "family": {"main": 2, "side": 4, "drink": 4},
}

MOOD_EXCLUSION_RULES = {
    "healthy": {
        "exclude_categories": {
            "Pizza", "Burger", "BBQ", "Dessert", "Fries",
            "Onion Rings", "Nachos"
        }
    }
}

# === Internal Question Wrapper ===
class InternalQuestion:
    def __init__(self, preferences):
        self.peoples = preferences.number_of_people
        self.mood = preferences.craving_type
        self.spice_lvl = preferences.spice_level
        self.avoid_anything = preferences.dietary_restrictions or ""
        self.budget = preferences.budget_level
        self.meal_time = preferences.meal_type


# === Helper Functions ===

# === Infer Role from Menu Item Data ===
def infer_role_from_data(item: dict, avg_price: float) -> str:
    if item["serves"] >= 2 and item["price"] >= avg_price:
        return "main"

    if item["serves"] == 1 and item["price"] <= avg_price * 0.6:
        return "drink"

    return "side"

# === Calculate Quantity Needed ===
def calculate_quantity(peoples: int, serves: int) -> int:
    """
    Calculate quantity based on serving capacity.
    Example:
      peoples=6, serves=2 → qty=3
    """
    return max(1, math.ceil(peoples / serves))

# === Compute Budget Range ===
def get_budget_range(peoples: int, budget: str, mood: str):
    base_budget = peoples * 600
    multiplier = {
        "tight": 1.0,
        "medium": 1.4,
        "comfortable": 1.8,
    }.get(budget, 1.0)

    final = base_budget * multiplier
    return int(final * 0.7), int(final), int(final * 1.3)

# === Filter Items Based on Meal Time and Preferences ===
def filter_items_by_meal_time(
    menu: List[Dict],
    meal_time: str,
    mood: str,
    spice_lvl: str,
    avoid_anything: str,
    popularity: Dict[str, int]
) -> List[Dict]:
    """
    Manually filter items based on meal time and other preferences.
    Returns filtered and scored items.
    """
    # Get category priority for meal time
    if mood == "healthy":
        category_priority = [
            "Salad", "Grilled", "Wrap", "Sandwich", "Soup", "Smoothie"
        ]
    else:
        category_priority = MEAL_PRIORITY.get(meal_time, DEFAULT_PRIORITY)
    
    # Apply mood exclusion rules
    rules = MOOD_EXCLUSION_RULES.get(mood, {})
    excluded_categories = rules.get("exclude_categories", set())
    
    # Filter and score items
    filtered_items = []
    
    for item in menu:
        # Exclude based on mood rules
        if item["category"] in excluded_categories:
            continue
        
        # Exclude based on dietary restrictions
        if avoid_anything:
            avoid_lower = avoid_anything.lower()
            item_name_lower = item["name"].lower()
            item_category_lower = item.get("category", "").lower()
            if avoid_lower in item_name_lower or avoid_lower in item_category_lower:
                continue
        
        # Score items based on mood, spice, and popularity
        score = (
            mood_match(item["name"], mood) * 2
            + spice_match(item["name"], spice_lvl) * 3
            + popularity.get(item["name"], 0)
        )
        
        # Prioritize items from meal-specific categories
        if item["category"] in category_priority:
            score += 5
        
        filtered_items.append({**item, "score": score})
    
    # Sort by score descending
    filtered_items.sort(key=lambda x: x["score"], reverse=True)
    
    return filtered_items

# === Convert Items to JSON Format ===
def items_to_json(items: List[Dict]) -> str:
    """
    Convert filtered items to JSON format for ChatGroq.
    """
    # Prepare simplified item data for LLM
    json_items = []
    for item in items:
        json_items.append({
            "name": item["name"],
            "category": item["category"],
            "price": item["price"],
            "serves": item["serves"],
            "score": item.get("score", 0)
        })
    
    return json.dumps(json_items, indent=2)

# === Get ChatGroq Recommendations ===
async def get_groq_recommendations(
    filtered_items_json: str,
    preferences: InternalQuestion,
    ideal_budget: int,
    hard_budget: int
) -> str:
    """
    Send filtered items and preferences to ChatGroq and get recommendations.
    """
    # Initialize ChatGroq
    llm = ChatGroq(
        groq_api_key=settings.GROQ_API_KEY,
        model_name="moonshotai/kimi-k2-instruct",
        temperature=0.7
    )
    
    # Create prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a restaurant recommendation expert. Your task is to analyze menu items and user preferences to suggest meal deals.

Given filtered menu items and user preferences, recommend 3 different meal deals that:
1. Fit within the budget constraints
2. Match the user's preferences (mood, spice level, dietary restrictions)
3. Provide variety and good value
4. Cover the required number of people
5. Don't suggest items that are not in the filtered menu items.
6. Don't suggest items with the number of people like if 4 people balance the meal don't suggest 4 people items. like (large pizza will eat by 2/3 people so do like that don't suggest food for each person make balance.)

Return your recommendations in JSON format with this structure:
{{
    "recommendations": [
        {{
            "deal_number": 1,
            "items": [
                {{
                    "name": "item_name",
                    "quantity": 2,
                    "reason": "why this item fits"
                }}
            ],
            "total_estimated_cost": 1500,
            "explanation": "why this deal is good"
        }}
    ]
}}

Be practical and consider:
- Serving sizes (serves field)
- Price per item
- Category variety
- User preferences
- Budget constraints"""),
        ("human", """User Preferences:
- Number of people: {peoples}
- Meal time: {meal_time}
- Mood/Craving: {mood}
- Spice level: {spice_lvl}
- Dietary restrictions: {avoid_anything}
- Budget level: {budget}
- Ideal budget: {ideal_budget} PKR
- Maximum budget: {hard_budget} PKR

Filtered Menu Items (JSON):
{filtered_items}

Please recommend 3 different meal deals based on the above information. Return only valid JSON."""),
    ])
    
    # Format prompt
    formatted_prompt = prompt.format_messages(
        peoples=preferences.peoples,
        meal_time=preferences.meal_time,
        mood=preferences.mood,
        spice_lvl=preferences.spice_lvl,
        avoid_anything=preferences.avoid_anything or "None",
        budget=preferences.budget,
        ideal_budget=ideal_budget,
        hard_budget=hard_budget,
        filtered_items=filtered_items_json
    )
    
    # Get response from ChatGroq
    response = await llm.ainvoke(formatted_prompt)
    
    return response.content

# === Parse ChatGroq Response and Build Final Deals ===
def build_deals_from_groq_response(
    groq_response: str,
    filtered_items: List[Dict],
    peoples: int,
    ideal_budget: int,
    hard_budget: int
) -> List[Dict]:
    """
    Parse ChatGroq response and combine with filtered items to build final deals.
    """
    try:
        # Extract JSON from response (handle markdown code blocks if present)
        response_text = groq_response.strip()
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        groq_data = json.loads(response_text)
        
        # Create a lookup map for filtered items
        items_map = {item["name"]: item for item in filtered_items}
        
        final_deals = []
        
        if "recommendations" in groq_data:
            for rec in groq_data["recommendations"]:
                deal_items = []
                total_cost = 0
                
                if "items" in rec:
                    for item_rec in rec["items"]:
                        item_name = item_rec.get("name", "")
                        
                        if item_name in items_map:
                            item = items_map[item_name]
                            qty = item_rec.get("quantity", 1)
                            
                            # Ensure quantity is reasonable
                            qty = max(1, min(qty, math.ceil(peoples / item["serves"]) + 1))
                            
                            cost = qty * item["price"]
                            
                            if total_cost + cost <= hard_budget:
                                deal_items.append({
                                    "name": item["name"],
                                    "category": item["category"],
                                    "qty": qty,
                                    "serves_each": item["serves"],
                                    "unit_price": item["price"],
                                    "total_price": cost,
                                })
                                total_cost += cost
                
                # Only add deal if it has items and covers people
                if deal_items:
                    total_coverage = sum(item["qty"] * item["serves_each"] for item in deal_items)
                    if total_coverage >= peoples:
                        final_deals.append({
                            "deal_number": rec.get("deal_number", len(final_deals) + 1),
                            "items": deal_items,
                            "total_cost": total_cost,
                            "explanation": rec.get("explanation", "")
                        })
        
        # If we don't have 3 deals, fill with fallback deals
        if len(final_deals) < 3:
            final_deals.extend(build_fallback_deals(
                filtered_items, peoples, ideal_budget, hard_budget, len(final_deals)
            ))
        
        return final_deals[:3]
    
    except (json.JSONDecodeError, KeyError, Exception) as e:
        print(f"Error parsing Groq response: {e}")
        print(f"Response was: {groq_response}")
        # Fallback to manual deal building
        return build_fallback_deals(filtered_items, peoples, ideal_budget, hard_budget, 0)

# === Build Fallback Deals (Manual Method) ===
def build_fallback_deals(
    filtered_items: List[Dict],
    peoples: int,
    ideal_budget: int,
    hard_budget: int,
    start_deal_num: int = 0
) -> List[Dict]:
    """
    Build deals manually as fallback if ChatGroq fails.
    """
    deals = []
    
    # Group items by category
    grouped = {}
    for item in filtered_items:
        grouped.setdefault(item["category"], []).append(item)
    
    # Get category priority
    categories = list(grouped.keys())
    
    for shift in range(3):
        if start_deal_num + shift >= 3:
            break
            
        deal_items = []
        total_cost = 0
        total_coverage = 0
        
        rotated_categories = categories[shift:] + categories[:shift]
        
        for category in rotated_categories:
            if category not in grouped:
                continue
            
            items = grouped[category]
            if not items:
                continue
            
            item = items[0]  # Take top item from category
            
            remaining_people = max(peoples - total_coverage, 0)
            if remaining_people <= 0:
                break
            
            qty = math.ceil(remaining_people / item["serves"])
            qty = max(1, min(qty, 3))  # Limit quantity
            
            coverage = qty * item["serves"]
            cost = qty * item["price"]
            
            if total_cost + cost > hard_budget:
                continue
            
            deal_items.append({
                "name": item["name"],
                "category": item["category"],
                "qty": qty,
                "serves_each": item["serves"],
                "unit_price": item["price"],
                "total_price": cost,
            })
            
            total_cost += cost
            total_coverage += coverage
            
            if total_coverage >= peoples and len(deal_items) >= 2:
                break
        
        if deal_items and total_coverage >= peoples:
            deals.append({
                "deal_number": start_deal_num + shift + 1,
                "items": deal_items,
                "total_cost": total_cost,
            })
    
    return deals

# === Generate Recommendations ===
async def generate_recommendation(branch: int, q: InternalQuestion):
    """
    Main recommendation generation function.
    Uses ChatGroq for intelligent recommendations after manual filtering.
    """
    _, ideal_budget, hard_budget = get_budget_range(
        q.peoples, q.budget, q.mood
    )

    # Fetch menu from cache, fallback to DB
    menu = await get_menu_from_cache(branch)
    if not menu:
        menu = await fetch_menu(branch)
        await store_menu_in_cache(branch, menu)

    # Fetch popularity data for scoring
    popularity = await fetch_recent_orders(branch)

    # === STEP 1: Manual filtering based on meal time and preferences ===
    filtered_items = filter_items_by_meal_time(
        menu=menu,
        meal_time=q.meal_time,
        mood=q.mood,
        spice_lvl=q.spice_lvl,
        avoid_anything=q.avoid_anything,
        popularity=popularity
    )
    
    # Limit filtered items to top 50 for efficiency
    filtered_items = filtered_items[:50]
    
    # === STEP 2: Convert filtered items to JSON ===
    filtered_items_json = items_to_json(filtered_items)
    
    # === STEP 3: Get recommendations from ChatGroq ===
    try:
        groq_response = await get_groq_recommendations(
            filtered_items_json=filtered_items_json,
            preferences=q,
            ideal_budget=ideal_budget,
            hard_budget=hard_budget
        )
        
        # === STEP 4: Build final deals from ChatGroq response ===
        deals = build_deals_from_groq_response(
            groq_response=groq_response,
            filtered_items=filtered_items,
            peoples=q.peoples,
            ideal_budget=ideal_budget,
            hard_budget=hard_budget
        )
        
        return deals
    
    except Exception as e:
        print(f"Error with ChatGroq: {e}")
        # Fallback to manual deal building
        return build_fallback_deals(
            filtered_items, q.peoples, ideal_budget, hard_budget, 0
        )
