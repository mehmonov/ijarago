import asyncpg
from typing import Optional, Any, List, Union

class Database:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def create_pool(self, user, password, database, host):
        self.pool = await asyncpg.create_pool(
            user=user,
            password=password,
            database=database,
            host=host
        )

    async def execute(self, command, *args,
                     fetch: bool = False,
                     fetchval: bool = False,
                     fetchrow: bool = False,
                     execute: bool = False
                     ) -> Union[List[asyncpg.Record], asyncpg.Record, Any, None]:
        async with self.pool.acquire() as connection:
            try:
                result = await connection.execute(command, *args)
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                return result
            except Exception as e:
                print(f"Execute error: {e}")
                return None
