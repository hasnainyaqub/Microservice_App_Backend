from pydantic import BaseModel

# === User Preferences Model ===
class Preferences(BaseModel):
    number_of_people: int
    craving_type: str
    spice_level: str
    dietary_restrictions: str | None
    budget_level: str
    meal_type: str

# === Recommendation Request Model ===
class RecommendationRequest(BaseModel):
    preferences: Preferences
