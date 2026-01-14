from pydantic import BaseModel, Field
from typing import Optional

# === User Preferences Schema ===
class Preferences(BaseModel):
    number_of_people: int = Field(gt=0, description="Number of people")
    craving_type: str = Field(description="Type of craving, e.g. bbq, pizza")
    spice_level: str = Field(description="Low, medium, high")
    dietary_restrictions: Optional[str] = Field(
        default=None,
        description="Halal, vegan, gluten free, etc"
    )
    budget_level: str = Field(description="Low, medium, high")
    meal_type: str = Field(description="Breakfast, lunch, dinner")

# === Recommendation Request Schema ===
class RecommendationRequest(BaseModel):
    preferences: Preferences
