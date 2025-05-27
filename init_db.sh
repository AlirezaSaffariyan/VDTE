docker exec vdte-app-1 alembic revision --autogenerate -m "Initial schema"
docker exec vdte-app-1 alembic upgrade head