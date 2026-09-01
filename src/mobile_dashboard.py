import json
import os

from flask import Flask, jsonify, render_template_string

app = Flask(__name__)
STATUS_PATH = os.path.join(os.path.dirname(__file__), "..", "bot_status.json")
STATUS_PATH = os.path.abspath(STATUS_PATH)

HTML_PAGE = """
<!doctype html>
<html>
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Gold Scalper Mobile</title>
  <style>
    :root {
      --bg: #0b1220;
      --panel: #111b2d;
      --panel2: #192a41;
      --accent: #2dd4bf;
      --warn: #fbbf24;
      --danger: #f87171;
      --text: #e2e8f0;
      --muted: #94a3b8;
    }
    * { box-sizing: border-box; }
    body { margin: 0; font-family: Arial, sans-serif; background: var(--bg); color: var(--text); padding: 22px; }
    .header { font-size: 24px; font-weight: bold; margin-bottom: 18px; }
    .status-grid { display: grid; gap: 16px; }
    .card { background: linear-gradient(180deg, var(--panel), var(--panel2)); border-radius: 16px; padding: 18px; box-shadow: 0 6px 12px rgba(0,0,0,0.3); }
    .title { color: var(--muted); font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase; }
    .value { font-size: 28px; font-weight: bold; margin-top: 8px; }
    .green { color: var(--accent); }
    .amber { color: var(--warn); }
    .red { color: var(--danger); }
    .row { display: flex; justify-content: space-between; margin-top: 12px; color: var(--muted); }
    .button { margin-top: 16px; background: var(--accent); color: #062c2a; border: none; border-radius: 12px; padding: 14px 18px; font-weight: bold; width: 100%; }
  </style>
</head>
<body>
  <div class="header">MT5 Gold Scalper</div>
  <div class="status-grid">
    <div class="card">
      <div class="title">Bot status</div>
      <div class="value green" id="botStatus">RUNNING</div>
      <div class="row"><span>Symbol</span><span id="symbolValue">XAUUSD</span></div>
      <div class="row"><span>Balance</span><span id="balanceValue">0.0</span></div>
    </div>

    <div class="card">
      <div class="title">Strategy</div>
      <div class="value amber" id="strategyValue">EMA + RSI + ATR</div>
      <div class="row"><span>Signal</span><span id="signalValue">WAIT</span></div>
      <div class="row"><span>Floating P/L</span><span id="pnlValue">0.0</span></div>
    </div>

    <div class="card">
      <div class="title">Execution</div>
      <div class="value red" id="execValue">READY</div>
      <div class="row"><span>Open positions</span><span id="positionsValue">0</span></div>
      <div class="row"><span>Mode</span><span id="modeValue">live_status</span></div>
    </div>
  </div>

  <button class="button" onclick="fetch('/status').then(r => r.json()).then(d => { document.getElementById('botStatus').innerText = d.status.toUpperCase(); document.getElementById('symbolValue').innerText = d.symbol; document.getElementById('balanceValue').innerText = d.account_balance; document.getElementById('strategyValue').innerText = d.strategy; document.getElementById('signalValue').innerText = d.last_signal; document.getElementById('pnlValue').innerText = d.floating_pnl; document.getElementById('positionsValue').innerText = d.positions_count; document.getElementById('modeValue').innerText = d.mode; document.getElementById('execValue').innerText = d.mode.toUpperCase(); })">Refresh</button>
</body>
</html>
"""


def load_status():
    try:
        with open(STATUS_PATH, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {
            "status": "running",
            "symbol": "XAUUSD",
            "strategy": "EMA + RSI + ATR",
            "risk_rule": "Stop loss at entry price",
            "android_ready": True,
            "mode": "live_status",
            "last_signal": "WAIT",
            "account_balance": 0.0,
            "floating_pnl": 0.0,
            "positions_count": 0,
        }


@app.route("/status", methods=["GET"])
def status():
    payload = load_status()
    payload.update({
        "strategy": "EMA + RSI + ATR",
        "risk_rule": "Stop loss at entry price",
        "android_ready": True,
        "mode": "live_status",
    })
    return jsonify(payload)


@app.route("/mobile", methods=["GET"])
def mobile_dashboard():
    return render_template_string(HTML_PAGE)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
