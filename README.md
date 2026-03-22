# AI Gym Coach

A local-first AI coaching app that syncs your Garmin fitness data and Google Calendar, then lets you chat with an AI coach that knows your training history.

## What It Does

- **Garmin sync** — pulls activities, HRV, sleep scores from Garmin Connect
- **Google Calendar sync** — imports upcoming events so the coach knows your schedule
- **AI Coach chat** — powered by a local LLM (Ollama / Llama 3.1) with full context of your data
- **Flutter macOS app** — native desktop UI; designed to extend to iOS/Android

## Architecture

```
backend/          Python FastAPI server (localhost:8000)
  routers/        REST endpoints for Garmin, Calendar, Coach
  services/       Garmin, Calendar, and LLM business logic
  db/             SQLite models via SQLModel
mobile/           Flutter app (macOS desktop, future iOS/Android)
  lib/
    models/       Activity, SleepRecord, CalendarEvent, ChatMessage
    services/     ApiService (HTTP client)
    screens/      DashboardScreen, ChatScreen
```

## Quick Start

### Prerequisites

| Tool | Install |
|------|---------|
| Python 3.9+ | Already on macOS, or `brew install python` |
| Ollama | `brew install ollama` |
| Flutter | [flutter.dev/get-started](https://docs.flutter.dev/get-started/install/macos) |

### 1. Run Setup

```bash
./setup.sh
```

This creates the Python virtualenv, installs dependencies, initializes the Flutter project, and pulls the Ollama model.

### 2. Configure Credentials

Edit `backend/.env`:

```env
GARMIN_EMAIL=your@email.com
GARMIN_PASSWORD=yourpassword
GOOGLE_CREDENTIALS_PATH=credentials.json
OLLAMA_MODEL=llama3.1:8b
```

**Google Calendar setup:**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project → Enable **Google Calendar API**
3. Create **OAuth 2.0 Desktop credentials** → download as `credentials.json`
4. Place `credentials.json` in the `backend/` directory
5. First calendar sync will open a browser for OAuth consent

### 3. Start the Backend

```bash
cd backend
source .venv/bin/activate
uvicorn main:app --reload
```

API docs available at http://localhost:8000/docs

### 4. Run the App

```bash
cd mobile
flutter run -d macos
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/garmin/sync` | Sync activities + sleep from Garmin |
| `GET` | `/garmin/activities?days=7` | List recent activities |
| `GET` | `/garmin/sleep?days=7` | List sleep records |
| `POST` | `/calendar/sync` | Sync Google Calendar events |
| `GET` | `/calendar/events?days=14` | List upcoming events |
| `POST` | `/coach/chat` | Send message to AI coach |
| `GET` | `/coach/history` | Get chat history |
| `DELETE` | `/coach/history` | Clear chat history |

## Roadmap

- [ ] Video analysis with MediaPipe (form checking)
- [ ] iOS / Android deployment
- [ ] Workout planning and periodization
- [ ] Garmin real-time streaming via ANT+
