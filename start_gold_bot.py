import os
import subprocess
import sys


PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    print("Starting Gold Scalper bot...")
    command = [sys.executable, os.path.join(PROJECT_DIR, "src", "bot.py")]
    try:
        subprocess.run(command, cwd=PROJECT_DIR, check=True)
    except KeyboardInterrupt:
        print("Bot stopped by user.")
    except Exception as exc:
        print(f"Bot failed to start: {exc}")
        raise


if __name__ == "__main__":
    main()
