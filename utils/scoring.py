# === Mood-Based Dish Matching ===
def mood_match(name: str, mood: str) -> int:
    # === Define mood keywords ===
    keywords = {
        "spicy_craving": ["spicy", "hot"],
        "cheesy_mood": ["cheese"],
        "sweet_craving": ["sweet", "dessert"],
        "healthy_choice": ["salad", "grill"],
        "heavy_meal": ["karahi", "biryani"],
        "light_meal": ["soup", "salad"]
    }

    # === Convert dish name to lowercase for case-insensitive matching ===
    name_lower = name.lower()

    # === Check if any keyword for the given mood exists in the dish name ===
    for word in keywords.get(mood, []):
        if word in name_lower:
            return 1
    return 0

# === Spice Level Matching ===
def spice_match(name: str, spice: str) -> int:
    # === Define spice level keywords ===
    levels = {
        "low": ["mild"],
        "medium": ["regular"],
        "high": ["hot", "spicy"]
    }

    # === Convert dish name to lowercase for case-insensitive matching ===
    name_lower = name.lower()

    # === Check if any keyword for the given spice level exists in the dish name ===
    for word in levels.get(spice, []):
        if word in name_lower:
            return 1
    return 0 