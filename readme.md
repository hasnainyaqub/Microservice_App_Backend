# Restaurant Recommendation Backend

A high-performance backend service built with **FastAPI**, designed to provide food recommendations. It uses **CSV files** for lightweight data storage and **Redis** for efficient caching. The system also leverages LLM capabilities via **LangChain** and **Groq** for intelligent recommendations.

---

## 🚀 Features

- **FastAPI**: Modern, fast (high-performance) web framework.
- **CSV Data Source**: Simple file-based database for Menus and Orders (`data/menu.csv`, `data/orders.csv`).
- **Redis Caching**: Caches menu data to reduce file I/O and improve response times.
- **LangChain + Groq**: powered recommendations.

---

## 🛠️ Prerequisites

- Python 3.12+ and a running Redis instance.

---

## 📝 Configuration

Create a `.env` file in the root directory. You can copy the example below:

```ini
# Server Config
HOST=0.0.0.0
PORT=8000

# Redis Configuration
REDIS_HOST=localhost      # Redis Host
REDIS_PORT=6379
REDIS_TTL=300         # Cache Time-To-Live in seconds

# LLM Configuration (Required for recommendations)
GROQ_API_KEY=your_groq_api_key_here
```

---



---

## 🏃 Running Locally

1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Start Redis**:
    Ensure you have a Redis server running locally on port `6379`.
    ```bash
    # Ubuntu
    sudo service redis-server start
    # Mac
    brew services start redis
    ```

3.  **Update `.env`**:
    Set `REDIS_HOST=localhost`.

4.  **Run the application**:
    ```bash
    uvicorn main:app --reload --port 8001
    ```

---

## 🔌 API Endpoints

### Health Check
**GET** `/health`
Returns the status of the API.

### Get Recommendations
**POST** `/api/recommend/{branch_id}`

Get food recommendations based on user preferences.

**Curl Example:**
```bash
curl -X POST http://localhost:8001/api/recommend/1 \
-H "Content-Type: application/json" \
-d '{
    "preferences": {
        "number_of_people": 2,
        "craving_type": "spicy",
        "spice_level": "medium",
        "dietary_restrictions": "none",
        "budget_level": "moderate",
        "meal_type": "dinner"
    }
}'
```

**Request Body Schema:**
```json
{
    "preferences": {
        "number_of_people": 6,
        "craving_type": "spicy",
        "spice_level": "high",
        "dietary_restrictions": null,
        "budget_level": "tight",
        "meal_type": "dinner"
    }
}
```

---

## 📂 Project Structure

```
.
├── api/             # API routes and logic
├── cache/           # Redis caching logic
├── core/            # Configuration and settings
├── data/            # CSV data files (menu.csv, orders.csv)
├── db/              # Database/Data access layer
├── main.py          # Application entry point
└── requirements.txt # Python dependencies
```