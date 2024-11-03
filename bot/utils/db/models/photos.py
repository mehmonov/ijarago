class PhotoQueries:
    async def create_table_apartment_photos(self):
        sql = """
        CREATE TABLE IF NOT EXISTS ApartmentPhotos (
        id SERIAL PRIMARY KEY,
        apartment_id INTEGER REFERENCES Apartments(id) ON DELETE CASCADE,
        photo_file_id TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        await self.execute(sql, execute=True)

    async def add_apartment_photo(self, apartment_id, photo_file_id):
        sql = """
        INSERT INTO ApartmentPhotos (apartment_id, photo_file_id)
        VALUES ($1, $2) RETURNING *
        """
        return await self.execute(sql, apartment_id, photo_file_id, fetchrow=True)

    async def get_apartment_photos(self, apartment_id):
        sql = """
        SELECT * FROM ApartmentPhotos 
        WHERE apartment_id = $1 
        ORDER BY created_at
        """
        return await self.execute(sql, apartment_id, fetch=True)