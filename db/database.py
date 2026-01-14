import aiomysql
import os
from core.config import settings

# === Create MySQL Connection Pool ===
async def get_pool():
    return await aiomysql.create_pool(
        host=settings.MYSQL_HOST,
        port=int(settings.MYSQL_PORT),
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        db=settings.MYSQL_DB,
        autocommit=True
    )

# === Fetch Menu Items for a Branch ===
async def fetch_menu(branch: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                """
                SELECT id, branch, name, category, portion, price, serves
                FROM menu
                WHERE branch=%s
                """,
                (branch,)
            )
            return await cur.fetchall()

# === Fetch Recent Orders Count for a Branch ===
async def fetch_recent_orders(branch: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                """
                SELECT item_name, COUNT(*) as cnt
                FROM orders
                WHERE branch=%s
                GROUP BY item_name
                """,
                (branch,)
            )
            rows = await cur.fetchall()
            return {row["item_name"]: row["cnt"] for row in rows}
