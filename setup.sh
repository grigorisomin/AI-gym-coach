#!/usr/bin/env bash
set -e

echo "=== AI Gym Coach — Setup ==="

# --- Backend ---
echo ""
echo ">> Setting up Python backend..."
cd backend

if ! command -v python3 &> /dev/null; then
  echo "ERROR: python3 not found. Install Python 3.9+ first."
  exit 1
fi

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "   Backend dependencies installed."

if [ ! -f .env ]; then
  cp .env.example .env
  echo "   Created backend/.env from template. Fill in your credentials."
fi

cd ..

# --- Ollama ---
echo ""
echo ">> Checking Ollama..."
if ! command -v ollama &> /dev/null; then
  echo "   Ollama not found. Install with: brew install ollama"
  echo "   Then run: ollama pull llama3.1:8b"
else
  echo "   Ollama found. Pulling llama3.1:8b model (this may take a while)..."
  ollama pull llama3.1:8b
fi

# --- Flutter ---
echo ""
echo ">> Setting up Flutter app..."
if ! command -v flutter &> /dev/null; then
  echo "   Flutter not found. Install from https://docs.flutter.dev/get-started/install"
  echo "   Then re-run this script or manually run: cd mobile && flutter create . --platforms=macos && flutter pub get"
else
  cd mobile
  flutter config --enable-macos-desktop
  flutter create . --org com.gymcoach --project-name ai_gym_coach --platforms=macos 2>/dev/null || true
  flutter pub get
  cd ..
  echo "   Flutter app ready."
fi

echo ""
echo "=== Setup complete ==="
echo ""
echo "Next steps:"
echo "  1. Edit backend/.env with your Garmin credentials and Google OAuth path"
echo "  2. Download Google OAuth credentials.json from Google Cloud Console"
echo "     (Enable Calendar API at https://console.cloud.google.com)"
echo "  3. Start the backend:  cd backend && source .venv/bin/activate && uvicorn main:app --reload"
echo "  4. Run the app:        cd mobile && flutter run -d macos"
