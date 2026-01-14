import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

payload = {
    "preferences": {
        "number_of_people": 6,
        "craving_type": "spicy",
        "spice_level": "high",
        "dietary_restrictions": None,
        "budget_level": "tight",
        "meal_type": "dinner"
    }
}

# Replace 1 with the actual branch_id you want to test
branch_id = 1

# Get API Bearer token from environment
api_token = os.getenv("API_BEARER_TOKEN")
if not api_token:
    print("Error: API_BEARER_TOKEN not found in environment variables")
    exit(1)

# Set up headers with Bearer token
headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json"
}

resp = requests.post(
    f"http://localhost:8001/api/recommend/{branch_id}",
    json=payload,
    headers=headers
)
print(resp.status_code)
print(resp.json())