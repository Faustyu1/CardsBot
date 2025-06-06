#!/bin/sh

echo "Waiting for PostgreSQL to be ready..."
while ! pg_isready -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER}; do
    sleep 1
done

echo "Creating database tables..."
python -c "
from database import init_db
import asyncio

asyncio.run(init_db())
"

echo "Database initialization completed!"