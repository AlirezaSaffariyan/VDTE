# A Modern Variable Data Template Engine

## How to run:

1. Install Docker on your machine according to your OS.

2. Clone the repository: `git clone https://github.com/AlirezaSaffariyan/VDTE.git`

3. Head to the project directory and create a `.env` file and store the key-value pairs below as you desire:

   ```ini
   # PostgreSQL
   POSTGRES_USER=your_database_user
   POSTGRES_PASSWORD=your_database_password
   POSTGRES_DB=your_database_name

   # FastAPI
   SECRET_KEY=your_jwt_secret_key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30

   # Database URL (for SQLAlchemy)
   DATABASE_URL=postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
   ```

   **!IMPORTANT: Do not change the value of database url**

4. Build and run the project: `docker compose up --build`

5. After running the project, run the migrations:

   ```bash
   docker exec vdte-app-1 alembic revision --autogenerate -m "Initial schema"
   docker exec vdte-app-1 alembic upgrade head
   ```

   or you can just run `chmod 755 init_db.sh` and then `./init_db.sh`
