import json
import os
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)
STATUS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "bot_status.json"))
LOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "gold_mt5_trade_log.jsonl"))


def read_status():
    try:
        with open(STATUS_PATH, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {
            "status": "running",
            "symbol": "XAUUSD",
            "last_signal": "WAIT",
            "account_balance": 0.0,
            "floating_pnl": 0.0,
            "positions_count": 0,
        }


def read_logs(limit=30):
    lines = []
    try:
        with open(LOG_PATH, "r", encoding="utf-8") as fh:
            lines = [line.strip() for line in fh if line.strip()]
    except Exception:
        return []
    return lines[-limit:]


PAGE = """
<!doctype html>
<html>
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Gold Scalper Admin</title>
  <style>
    body { font-family: Arial, sans-serif; background: #0f172a; color: #e2e8f0; margin: 0; padding: 24px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; }
    .card { background: #111827; border-radius: 12px; padding: 18px; box-shadow: 0 4px 10px rgba(0,0,0,0.25); }
    .title { color: #94a3b8; font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; }
    .value { font-size: 28px; font-weight: bold; margin-top: 10px; }
    .green { color: #34d399; }
    .amber { color: #fbbf24; }
    .red { color: #f87171; }
    .controls { margin-top: 20px; display: flex; gap: 12px; flex-wrap: wrap; }
    button { background: #14b8a6; color: #062c2a; border: 0; border-radius: 10px; padding: 12px 16px; font-weight: bold; }
    .log { margin-top: 20px; background: #0b1220; border-radius: 12px; padding: 14px; max-height: 420px; overflow: auto; }
    pre { white-space: pre-wrap; word-break: break-word; margin: 0; font-size: 12px; color: #cbd5e1; }
  </style>
</head>
<body>
  <h1>Gold Scalper Admin</h1>
  <div class="grid">
    <div class="card">
      <div class="title">Status</div>
      <div class="value green" id="statusValue">running</div>
    </div>
    <div class="card">
      <div class="title">Symbol</div>
      <div class="value amber" id="symbolValue">XAUUSD</div>
    </div>
    <div class="card">
      <div class="title">Balance</div>
      <div class="value" id="balanceValue">0.0</div>
    </div>
    <div class="card">
      <div class="title">P/L</div>
      <div class="value red" id="pnlValue">0.0</div>
    </div>
  </div>

  <div class="controls">
    <button onclick="fetch('/api/start').then(r => r.json()).then(d => refresh())">Start</button>
    <button onclick="fetch('/api/stop').then(r => r.json()).then(d => refresh())">Stop</button>
    <button onclick="fetch('/api/status').then(r => r.json()).then(d => render(d))">Refresh</button>
  </div>

  <div class="log">
    <pre id="logArea"></pre>
  </div>

  <script>
    async function refresh() {
      const d = await fetch('/api/status').then(r => r.json());
      render(d);
    }

    function render(data) {
      document.getElementById('statusValue').innerText = data.status || 'running';
      document.getElementById('symbolValue').innerText = data.symbol || 'XAUUSD';
      document.getElementById('balanceValue').innerText = data.account_balance || '0.0';
      document.getElementById('pnlValue').innerText = data.floating_pnl || '0.0';
    }

    async function loadLogs() {
      const d = await fetch('/api/logs').then(r => r.json());
      document.getElementById('logArea').innerText = d.logs.join('\n');
    }

    refresh();
    loadLogs();
    setInterval(() => { refresh(); loadLogs(); }, 5000);
  </script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(PAGE)


@app.route("/api/status", methods=["GET"])
def api_status():
    return jsonify(read_status())


@app.route("/api/logs", methods=["GET"])
def api_logs():
    return jsonify({"logs": read_logs(20)})


@app.route("/api/start", methods=["GET"])
def api_start():
    status = read_status()
    status["status"] = "running"
    try:
        with open(STATUS_PATH, "w", encoding="utf-8") as fh:
            json.dump(status, fh)
    except Exception:
        pass
    return jsonify({"ok": True, "status": "running"})


@app.route("/api/stop", methods=["GET"])
def api_stop():
    status = read_status()
    status["status"] = "stopped"
    try:
        with open(STATUS_PATH, "w", encoding="utf-8") as fh:
            json.dump(status, fh)
    except Exception:
        pass
    return jsonify({"ok": True, "status": "stopped"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=False)
