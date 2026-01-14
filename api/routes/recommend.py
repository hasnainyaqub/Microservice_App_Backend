from fastapi import APIRouter, Depends, Path
from schemas.recommend import RecommendationRequest
from services.recommendation import generate_recommendation, InternalQuestion
from core.security import verify_bearer_token

# === Initialize API Router ===
router = APIRouter()

# === /api/recommend/{branch_id} endpoint with Bearer token ===
@router.post(
    "/recommend/{branch_id}",
    dependencies=[Depends(verify_bearer_token)]
)
async def recommend(
    payload: RecommendationRequest,
    branch_id: int,
):
    # === Convert user preferences to internal representation ===
    q = InternalQuestion(payload.preferences)

    # === Generate recommendations asynchronously ===
    deals = await generate_recommendation(
        branch_id,
        q
    )

    # === Debug ===
    print("deals", deals)

    # === Return structured recommendation response ===
    return {
        "branch_id": branch_id,
        "number_of_people": q.peoples,
        "meal_type": q.meal_time,
        "budget_level": q.budget,
        "deals": deals
    }