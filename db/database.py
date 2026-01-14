import aiomysql
from core.config import settings

_pool = None

# === Create Pool Once ===
async def get_pool():
    global _pool
    if _pool is None:
        _pool = await aiomysql.create_pool(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            db=settings.MYSQL_DB,
            autocommit=True,
            maxsize=5
        )
    return _pool

# === Fetch Menu Items ===
async def fetch_menu(branch: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                """
                SELECT id, branch, name, category, portion, price, serves
                FROM menu
                WHERE branch = %s
                """,
                (branch,)
            )
            return await cur.fetchall()

# === Fetch Recent Orders Count ===
async def fetch_recent_orders(branch: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                """
                SELECT item_name, COUNT(*) AS cnt
                FROM orders
                WHERE branch = %s
                GROUP BY item_name
                """,
                (branch,)
            )
            rows = await cur.fetchall()
            return {row["item_name"]: row["cnt"] for row in rows}
