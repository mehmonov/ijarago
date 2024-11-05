class ApartmentQueries:
    async def create_table_apartments(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Apartments (
        id SERIAL PRIMARY KEY,
        owner_id BIGINT REFERENCES Users(telegram_id),
        
        district VARCHAR(100) NOT NULL,
        address TEXT NOT NULL,
        rooms SMALLINT NOT NULL,
        floor SMALLINT NOT NULL,
        total_floors SMALLINT NOT NULL,
        price DECIMAL NOT NULL,
        area DECIMAL NOT NULL,
        description TEXT,
        has_furniture BOOLEAN DEFAULT false,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_available BOOLEAN DEFAULT true
        );
        """
        await self.execute(sql, execute=True)

    async def add_apartment(self, owner_id: int, district: str, address: str, rooms: int, 
                           floor: int, total_floors: int, price: float, area: float, 
                           description: str = None, has_furniture: bool = False):
        sql = """
        INSERT INTO Apartments (
            owner_id, district, address, rooms, floor, total_floors, 
            price, area, description, has_furniture, created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW())
        RETURNING *, (
            SELECT username 
            FROM Users 
            WHERE telegram_id = $1
        ) as owner_username
        """
        return await self.execute(
            sql, owner_id, district, address, rooms, floor, total_floors,
            price, area, description, has_furniture, fetchrow=True
        )

    async def get_all_available_apartments(self):
        sql = """
        SELECT a.*, u.full_name as owner_name, u.username as owner_username 
        FROM Apartments a 
        JOIN Users u ON a.owner_id = u.telegram_id 
        WHERE is_available = true 
        ORDER BY created_at DESC
        """
        return await self.execute(sql, fetch=True)

    async def get_apartments_by_filters(self, min_price=None, max_price=None, 
                                      district=None, min_rooms=None, max_rooms=None):
        conditions = ["is_available = true"]
        params = []
        param_counter = 1

        if min_price is not None:
            conditions.append(f"price >= ${param_counter}")
            params.append(min_price)
            param_counter += 1

        if max_price is not None:
            conditions.append(f"price <= ${param_counter}")
            params.append(max_price)
            param_counter += 1

        if district is not None:
            conditions.append(f"district = ${param_counter}")
            params.append(district)
            param_counter += 1

        if min_rooms is not None:
            conditions.append(f"rooms >= ${param_counter}")
            params.append(min_rooms)
            param_counter += 1

        if max_rooms is not None:
            conditions.append(f"rooms <= ${param_counter}")
            params.append(max_rooms)
            param_counter += 1

        sql = f"""
        SELECT a.*, u.full_name as owner_name, u.username as owner_username 
        FROM Apartments a 
        JOIN Users u ON a.owner_id = u.telegram_id 
        WHERE {' AND '.join(conditions)}
        ORDER BY created_at DESC
        """
        return await self.execute(sql, *params, fetch=True)

    async def get_user_apartments(self, user_id: int):
        sql = """
        SELECT a.*, u.full_name as owner_name, u.username as owner_username 
        FROM Apartments a
        JOIN Users u ON a.owner_id = u.telegram_id
        WHERE a.owner_id = $1 AND a.is_available = true
        ORDER BY a.created_at DESC
        """
        return await self.execute(sql, user_id, fetch=True)

    async def update_apartment_status(self, apartment_id, is_available):
        sql = """
        UPDATE Apartments 
        SET is_available = $2 
        WHERE id = $1 RETURNING *
        """
        return await self.execute(sql, apartment_id, is_available, fetchrow=True)
    
    async def get_apartment_by_id(self, apartment_id: int):
        sql = """
        SELECT a.*, u.full_name as owner_name, u.username as owner_username 
        FROM Apartments a
        JOIN Users u ON a.owner_id = u.telegram_id
        WHERE a.id = $1 AND a.is_available = true
        """
        return await self.execute(sql, apartment_id, fetchrow=True)

    async def get_apartments_by_district(self, district: str):
        sql = """
        SELECT a.*, u.full_name as owner_name, u.username as owner_username 
        FROM Apartments a 
        JOIN Users u ON a.owner_id = u.telegram_id 
        WHERE district = $1 AND is_available = true 
        ORDER BY created_at DESC
        """
        return await self.execute(sql, district, fetch=True)

    async def get_similar_apartments(self, district: str, rooms: int, price_range: tuple):
        sql = """
        SELECT a.*, u.full_name as owner_name, u.username as owner_username 
        FROM Apartments a
        JOIN Users u ON a.owner_id = u.telegram_id
        WHERE district = $1 
        AND rooms = $2
        AND CAST(price AS FLOAT) BETWEEN $3 AND $4
        AND is_available = true
        ORDER BY created_at DESC
        """
        return await self.execute(sql, district, rooms, price_range[0], price_range[1], fetch=True)

    async def delete_apartment(self, apartment_id: int):
        try:
            # Tranzaksiyani boshlaymiz
            async with self.pool.acquire() as connection:
                async with connection.transaction():
                    # Avval rasmlarni o'chiramiz
                    await connection.execute(
                        "DELETE FROM ApartmentPhotos WHERE apartment_id = $1",
                        apartment_id
                    )
                    
                    # Keyin kvartira ma'lumotlarini o'chiramiz
                    sql = "DELETE FROM Apartments WHERE id = $1 RETURNING id"
                    result = await connection.fetchrow(sql, apartment_id)
                    
                    return result
                    
        except Exception as e:
            print(f"Delete error: {e}")
            return None