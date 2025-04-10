#!/bin/bash

# DeepScan Setup Script
# This script sets up the DeepScan application with a single command

echo "===== DeepScan Setup Script ====="
echo "Setting up your development environment..."

# Create and activate virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Determine OS for activation command
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Linux/macOS
    source venv/bin/activate
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements-light.txt

# Initialize database
echo "Initializing database..."
cd src
python manage.py create_db
python manage.py seed_db
cd ..

echo "===== Setup Complete! ====="
echo "To run the application:"
echo "1. Activate the virtual environment (if not already activated):"
echo "   - On Windows: venv\\Scripts\\activate"
echo "   - On macOS/Linux: source venv/bin/activate"
echo "2. Run the application:"
echo "   - Full application: python src/run.py"
echo "   - Minimal demo: cd minimal_app && python -m http.server 3000"
echo ""
echo "Default credentials:"
echo "- Client: client@example.com / password123"
echo "- Analyst: analyst@example.com / password123"
echo "- Admin: admin@growthguard.com / password123"
