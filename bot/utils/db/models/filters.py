class FilterQueries:
    async def create_table_saved_filters(self):
        sql = """
        CREATE TABLE IF NOT EXISTS SavedFilters (
        id SERIAL PRIMARY KEY,
        user_id BIGINT REFERENCES Users(telegram_id),
        min_price DECIMAL,
        max_price DECIMAL,
        district VARCHAR(100),
        min_rooms SMALLINT,
        max_rooms SMALLINT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        await self.execute(sql, execute=True)

    async def save_user_filter(self, user_id, min_price=None, max_price=None,
                             district=None, min_rooms=None, max_rooms=None):
        sql = """
        INSERT INTO SavedFilters (
            user_id, min_price, max_price, district, min_rooms, max_rooms
        ) VALUES ($1, $2, $3, $4, $5, $6) RETURNING *
        """
        return await self.execute(sql, user_id, min_price, max_price,
                                district, min_rooms, max_rooms, fetchrow=True)

    async def get_user_filters(self, user_id):
        sql = "SELECT * FROM SavedFilters WHERE user_id = $1 ORDER BY created_at DESC"
        return await self.execute(sql, user_id, fetch=True)

    async def delete_user_filter(self, filter_id, user_id):
        sql = """
        DELETE FROM SavedFilters 
        WHERE id = $1 AND user_id = $2 
        RETURNING *
        """
        return await self.execute(sql, filter_id, user_id, fetchrow=True)