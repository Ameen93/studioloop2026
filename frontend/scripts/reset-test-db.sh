#!/bin/bash
#
# Reset and seed the test database for E2E testing.
#
# Prerequisites:
#   - Backend Docker containers running (docker compose up -d)
#   - Backend virtual environment set up
#
# Usage:
#   ./scripts/reset-test-db.sh
#
# This script will:
#   1. Navigate to the backend directory
#   2. Run the seed script with --reset flag
#   3. Return to the frontend directory
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$(dirname "$FRONTEND_DIR")/backend"

echo "🔄 Resetting and seeding test database..."
echo "   Backend directory: $BACKEND_DIR"

if [ ! -d "$BACKEND_DIR" ]; then
    echo "❌ Error: Backend directory not found at $BACKEND_DIR"
    exit 1
fi

cd "$BACKEND_DIR"

# Check if uv is available
if command -v uv &> /dev/null; then
    uv run python scripts/seed.py --reset
elif [ -d ".venv" ]; then
    .venv/bin/python scripts/seed.py --reset
else
    echo "❌ Error: Neither 'uv' nor '.venv' found. Please run from backend with proper Python environment."
    exit 1
fi

cd "$FRONTEND_DIR"

echo ""
echo "✅ Test database reset and seeded successfully!"
echo ""
echo "Test user credentials:"
echo "   Email: test@studioloop.com"
echo "   Password: testpassword123"
