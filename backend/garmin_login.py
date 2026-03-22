"""
One-time interactive Garmin login with MFA support.

Run this once to authenticate and save session tokens to disk.
After that, the API server reuses the tokens automatically (~30 day validity).

Usage:
    cd backend
    source .venv/bin/activate
    python garmin_login.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from garminconnect import Garmin

load_dotenv()

TOKEN_STORE = Path(__file__).parent / ".garth_tokens"


def main():
    email = os.getenv("GARMIN_EMAIL")
    password = os.getenv("GARMIN_PASSWORD")

    if not email or not password:
        print("ERROR: Set GARMIN_EMAIL and GARMIN_PASSWORD in backend/.env first.")
        return

    print(f"Logging in as {email}...")

    def prompt_mfa():
        return input("Enter the MFA code sent to your email: ").strip()

    client = Garmin(email, password, prompt_mfa=prompt_mfa)
    client.login()
    client.garth.dump(str(TOKEN_STORE))

    print(f"\nLogin successful! Tokens saved to {TOKEN_STORE}")
    print("The backend will now use these tokens automatically.")
    print(f"Logged in as: {client.get_full_name()}")


if __name__ == "__main__":
    main()
