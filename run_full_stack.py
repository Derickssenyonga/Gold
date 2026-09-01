import os
import subprocess
import sys
import time

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


def run_process(target, label):
    print(f"Starting {label}...")
    return subprocess.Popen(
        [sys.executable, target],
        cwd=PROJECT_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def main():
    print("Starting Gold Scalper full stack...")
    bot = run_process(os.path.join(PROJECT_DIR, "src", "bot.py"), "bot")
    dashboard = run_process(os.path.join(PROJECT_DIR, "src", "mobile_dashboard.py"), "dashboard")
    telegram = run_process(os.path.join(PROJECT_DIR, "src", "telegram_bot_controller.py"), "telegram controller")
    admin = run_process(os.path.join(PROJECT_DIR, "admin_panel.py"), "admin panel")

    print("Services started.")
    print("Dashboard: http://localhost:5000/mobile")
    print("Telegram controller: http://localhost:5001/health")
    print("Admin panel: http://localhost:5050/")
    print("Press Ctrl+C to stop all services.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping services...")
        for proc in [bot, dashboard, telegram, admin]:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        print("All services stopped.")


if __name__ == "__main__":
    main()
