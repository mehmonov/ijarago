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

    async def add_apartment(self, owner_id, district, address, rooms, floor, 
                          total_floors, price, area, description=None, has_furniture=False):
        sql = """
        INSERT INTO Apartments (
            owner_id, district, address, rooms, floor, 
            total_floors, price, area, description, has_furniture
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) RETURNING *
        """
        return await self.execute(sql, owner_id, district, address, rooms, 
                                floor, total_floors, price, area, 
                                description, has_furniture, fetchrow=True)

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

    async def get_user_apartments(self, owner_id):
        sql = """
        SELECT * FROM Apartments 
        WHERE owner_id = $1 
        ORDER BY created_at DESC
        """
        return await self.execute(sql, owner_id, fetch=True)

    async def update_apartment_status(self, apartment_id, is_available):
        sql = """
        UPDATE Apartments 
        SET is_available = $2 
        WHERE id = $1 RETURNING *
        """
        return await self.execute(sql, apartment_id, is_available, fetchrow=True)
    
    async def get_apartment_by_id(self, apartment_id):
        sql = """
        SELECT * FROM Apartments WHERE id = $1
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