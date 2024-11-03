class UserQueries:
    async def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        username varchar(255) NULL,
        telegram_id BIGINT NOT NULL UNIQUE,
        user_type VARCHAR(20) NOT NULL DEFAULT 'renter' CHECK (user_type IN ('renter', 'landlord')),
        phone VARCHAR(20) NULL,
        company VARCHAR(255) NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        await self.execute(sql, execute=True)
    
    async def add_user(self, telegram_id: int, full_name: str, username: str, user_type: str, phone: str, company: str = None):
        existing_user = await self.get_user_by_telegram_id(telegram_id)
        if existing_user:
            sql = """
            UPDATE Users 
            SET full_name = $2, username = $3, user_type = $4, phone = $5, company = $6
            WHERE telegram_id = $1 
            RETURNING *
            """
        else:
            sql = """
            INSERT INTO Users (telegram_id, full_name, username, user_type, phone, company)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING *
            """
        
        return await self.execute(
            sql, 
            telegram_id, full_name, username, user_type, phone, company,
            fetchrow=True
        )
    async def drop_users_table(self):
        """Users jadvalini o'chirish uchun funksiya"""
        sql = """
        DROP TABLE IF EXISTS Users CASCADE;
        """
        await self.execute(sql, execute=True)
    
    async def get_all_users(self):
        sql = "SELECT * FROM Users ORDER BY id"
        return await self.execute(sql, fetch=True)

    async def get_user_by_telegram_id(self, telegram_id: int):
        sql = "SELECT * FROM Users WHERE telegram_id = $1"
        return await self.execute(sql, telegram_id, fetchrow=True)
    
    async def get_users_by_type(self, user_type: str):
        sql = "SELECT * FROM Users WHERE user_type = $1"
        return await self.execute(sql, user_type, fetch=True)
    
    async def update_user_type(self, telegram_id: int, user_type: str):
        sql = """
        UPDATE Users SET user_type = $2 
        WHERE telegram_id = $1 RETURNING *
        """
        return await self.execute(sql, telegram_id, user_type, fetchrow=True)
    
    async def get_users_count(self):
        sql = "SELECT COUNT(*) FROM Users"
        return await self.execute(sql, fetchval=True)

    async def get_users_count_last_week(self):
        sql = "SELECT COUNT(*) FROM Users WHERE created_at >= NOW() - INTERVAL '7 days'"
        return await self.execute(sql, fetchval=True)
    
    async def get_renters_count(self):
        sql = "SELECT COUNT(*) FROM Users WHERE user_type = 'renter'"
        return await self.execute(sql, fetchval=True)
    
    async def get_landlords_count(self):
        sql = "SELECT COUNT(*) FROM Users WHERE user_type = 'landlord'"
        return await self.execute(sql, fetchval=True)

    async def get_apartments_count(self):
        sql = "SELECT COUNT(*) FROM Apartments"
        return await self.execute(sql, fetchval=True)
