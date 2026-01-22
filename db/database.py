import csv
import os

# Path to data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MENU_CSV = os.path.join(BASE_DIR, "data", "menu.csv")
ORDERS_CSV = os.path.join(BASE_DIR, "data", "orders.csv")

# === Fetch Menu Items ===
async def fetch_menu(branch: int):
    results = []
    try:
        with open(MENU_CSV, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Filter by branch. CSV read values are strings, need conversion.
                try:
                    row_branch = int(row['branch'])
                except ValueError:
                    continue

                if row_branch == branch:
                    # Convert types to match previous behavior
                    # "SELECT id, branch, name, category, portion, price, serves"
                    item = {
                        "id": int(row['id']),
                        "branch": int(row['branch']),
                        "name": row['name'],
                        "category": row['category'],
                        "portion": row['portion'],
                        "price": int(row['price']),
                        "serves": int(row['serves'])
                    }
                    results.append(item)
    except FileNotFoundError:
        print(f"File not found: {MENU_CSV}")
        return []
    except Exception as e:
        print(f"Error reading menu csv: {e}")
        return []
    return results

# === Fetch Recent Orders Count ===
async def fetch_recent_orders(branch: int):
    counts = {}
    try:
        with open(ORDERS_CSV, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    row_branch = int(row['branch'])
                except ValueError:
                    continue

                if row_branch == branch:
                    item_name = row['item_name']
                    counts[item_name] = counts.get(item_name, 0) + 1
    except FileNotFoundError:
        print(f"File not found: {ORDERS_CSV}")
        return {}
    except Exception as e:
        print(f"Error reading orders csv: {e}")
        return {}
    return counts

# === Fetch Menu Items with Reviews ===
async def fetch_menu_with_reviews():
    """
    Fetch menu items with reviews.
    Returns a list of menu items, each with a reviews list.
    Mock data implementation - treat as real DB source.
    """
    # Mock menu items with reviews
    menu_items = [
        {
            "id": 1,
            "name": "Margherita Pizza",
            "category": "Pizza",
            "price": 1200,
            "reviews": [
                {
                    "id": 1,
                    "review": "Excellent pizza! The cheese was perfect and the crust was crispy.",
                    "customer_name": "John Doe",
                    "date": "2024-01-15"
                },
                {
                    "id": 2,
                    "review": "Not bad, but could use more toppings. The base was good though.",
                    "customer_name": "Jane Smith",
                    "date": "2024-01-20"
                },
                {
                    "id": 3,
                    "review": "Terrible experience. The pizza was cold and the cheese was rubbery.",
                    "customer_name": "Bob Wilson",
                    "date": "2024-01-25"
                }
            ]
        },
        {
            "id": 2,
            "name": "Chicken Burger",
            "category": "Burger",
            "price": 800,
            "reviews": [
                {
                    "id": 4,
                    "review": "Amazing burger! The chicken was juicy and well-seasoned. Highly recommend!",
                    "customer_name": "Alice Brown",
                    "date": "2024-01-18"
                },
                {
                    "id": 5,
                    "review": "Good burger, decent price. Nothing special but satisfying.",
                    "customer_name": "Charlie Davis",
                    "date": "2024-01-22"
                }
            ]
        },
        {
            "id": 3,
            "name": "Caesar Salad",
            "category": "Salad",
            "price": 600,
            "reviews": [
                {
                    "id": 6,
                    "review": "Fresh and delicious! The dressing was perfect. Love this salad!",
                    "customer_name": "Diana Prince",
                    "date": "2024-01-16"
                },
                {
                    "id": 7,
                    "review": "The salad was okay, but the lettuce was a bit wilted.",
                    "customer_name": "Edward Lee",
                    "date": "2024-01-24"
                },
                {
                    "id": 8,
                    "review": "Horrible! The salad was old and the dressing was too salty. Waste of money.",
                    "customer_name": "Fiona Green",
                    "date": "2024-01-26"
                }
            ]
        },
        {
            "id": 4,
            "name": "BBQ Platter",
            "category": "BBQ",
            "price": 2500,
            "reviews": [
                {
                    "id": 9,
                    "review": "Outstanding BBQ! The meat was tender and flavorful. Best meal I've had!",
                    "customer_name": "George Harris",
                    "date": "2024-01-17"
                },
                {
                    "id": 10,
                    "review": "Great value for money. The portion was huge and everything was delicious.",
                    "customer_name": "Helen White",
                    "date": "2024-01-21"
                }
            ]
        },
        {
            "id": 5,
            "name": "Chocolate Cake",
            "category": "Dessert",
            "price": 500,
            "reviews": [
                {
                    "id": 11,
                    "review": "Perfect dessert! Rich and chocolatey. Could eat this every day!",
                    "customer_name": "Ian Black",
                    "date": "2024-01-19"
                },
                {
                    "id": 12,
                    "review": "The cake was too sweet for my taste, but it was fresh.",
                    "customer_name": "Julia Gray",
                    "date": "2024-01-23"
                },
                {
                    "id": 13,
                    "review": "Disgusting! The cake was dry and tasted like it was made days ago.",
                    "customer_name": "Kevin Blue",
                    "date": "2024-01-27"
                }
            ]
        }
    ]
    
    return menu_items
