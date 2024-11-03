class FilterQueries:
    async def create_table_saved_filters(self):
        sql = """
        CREATE TABLE IF NOT EXISTS SavedFilters (
        id SERIAL PRIMARY KEY,
        user_id BIGINT REFERENCES Users(telegram_id),
        district VARCHAR(100) NOT NULL,
        min_price DECIMAL NOT NULL,
        max_price DECIMAL NOT NULL,
        min_rooms SMALLINT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        await self.execute(sql, execute=True)

    async def save_filter(self, user_id: int, district: str, min_price: int, 
                         max_price: int, min_rooms: int):
        sql = """
        INSERT INTO SavedFilters (user_id, district, min_price, max_price, min_rooms)
        VALUES ($1, $2, $3, $4, $5) RETURNING *
        """
        return await self.execute(sql, user_id, district, min_price, max_price, 
                                min_rooms, fetchrow=True)

    async def get_user_filters(self, user_id: int):
        sql = """
        SELECT * FROM SavedFilters 
        WHERE user_id = $1 
        ORDER BY created_at DESC
        """
        return await self.execute(sql, user_id, fetch=True)

    async def delete_filter(self, filter_id: int):
        sql = "DELETE FROM SavedFilters WHERE id = $1"
        return await self.execute(sql, filter_id, execute=True)

    async def get_filter_by_id(self, filter_id: int):
        sql = """
        SELECT * FROM SavedFilters 
        WHERE id = $1
        """
        return await self.execute(sql, filter_id, fetchrow=True)