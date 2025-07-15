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
        last_notified_apartment_id INT DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        await self.execute(sql, execute=True)

    async def save_filter(self, user_id: int, district: str, min_price: int, 
                         max_price: int, min_rooms: int):
        sql = """
        INSERT INTO SavedFilters (user_id, district, min_price, max_price, min_rooms, last_notified_apartment_id)
        VALUES ($1, $2, $3, $4, $5, $6) RETURNING *
        """
        return await self.execute(sql, user_id, district, min_price, max_price, 
                                min_rooms, 0, fetchrow=True)

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

    async def update_last_notified_apartment_id(self, filter_id: int, apartment_id: int):
        sql = """
        UPDATE SavedFilters
        SET last_notified_apartment_id = $2
        WHERE id = $1
        """
        return await self.execute(sql, filter_id, apartment_id, execute=True)

    async def find_similar_filters(self, district: str, min_rooms: int, min_price: float, max_price: float, current_filter_id: int = None):
        sql = """
        SELECT f.*, u.full_name as user_name, u.telegram_id
        FROM SavedFilters f
        JOIN Users u ON f.user_id = u.telegram_id
        WHERE f.district = $1 
        AND f.min_rooms = $2
        AND (
            ($3 BETWEEN f.min_price AND f.max_price)
            OR
            ($4 BETWEEN f.min_price AND f.max_price)
            OR
            (f.min_price BETWEEN $3 AND $4)
        )
        """
        params = [district, min_rooms, min_price, max_price]
        
        if current_filter_id:
            sql += " AND f.id != $5"
            params.append(current_filter_id)
        
        return await self.execute(sql, *params, fetch=True)