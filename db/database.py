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
