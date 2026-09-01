#!/bin/bash

# Exit on any error
set -e

echo "🚀 Starting Synkora Deployment Process..."

# 1. Pull the latest code
echo "📦 Pulling latest changes from Git..."
git pull origin main

# 2. Rebuild Docker Images
echo "🏗️ Rebuilding Docker images (this may take a while)..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache

# 3. Apply any database migrations (Assuming Alembic is set up)
# docker-compose exec -T api alembic upgrade head

# 4. Restart the services
echo "🔄 Restarting services..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 5. Clean up dangling images to free up space
echo "🧹 Cleaning up old Docker images..."
docker image prune -f

echo "✅ Deployment completed successfully!"
