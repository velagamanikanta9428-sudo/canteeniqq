"""
CanteenIQ — Python Backend Server
===================================
Run :  python server.py
Open:  http://localhost:5000

Notepad files written automatically:
  users.txt          - all registered users (human-readable)
  orders.txt         - all placed orders    (human-readable)
  canteeniq_data.txt - combined report (users + orders together)
"""

from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context
from flask_cors import CORS
import json, os, datetime, threading, queue, time

app = Flask(__name__, static_folder=".")
CORS(app)

# SSE: connected owner clients (each gets a queue)
_owner_clients = []
_clients_lock  = threading.Lock()

def push_to_owners(event_type, data):
    """Push a Server-Sent Event to all connected owner browsers."""
    msg = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
    with _clients_lock:
        dead = []
        for q in _owner_clients:
            try:
                q.put_nowait(msg)
            except Exception:
                dead.append(q)
        for q in dead:
            _owner_clients.remove(q)

# File paths
USERS_JSON   = "users.json"
ORDERS_JSON  = "orders.json"
USERS_TXT    = "users.txt"
ORDERS_TXT   = "orders.txt"
COMBINED_TXT = "canteeniq_data.txt"

lock = threading.Lock()

def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def now_str():
    return datetime.datetime.now().strftime("%d %b %Y  %I:%M:%S %p")

def write_users_txt(users_dict):
    user_list = list(users_dict.values())
    lines = []
    lines.append("=" * 65)
    lines.append("       CanteenIQ  --  REGISTERED USERS")
    lines.append("       Last updated : " + now_str())
    lines.append("       Total users  : " + str(len(user_list)))
    lines.append("=" * 65)
    lines.append("")
    for i, u in enumerate(user_list, 1):
        lines.append("  User #" + str(i) + "  " + "-" * 48)
        lines.append("    Name         : " + u.get("fname","") + " " + u.get("lname",""))
        lines.append("    Email        : " + u.get("email",""))
        lines.append("    Student ID   : " + u.get("sid",""))
        lines.append("    Department   : " + u.get("dept",""))
        lines.append("    Year / Batch : " + u.get("year",""))
        lines.append("    Registered   : " + u.get("registeredAt",""))
        lines.append("    Total Orders : " + str(u.get("orders", 0)))
        lines.append("    Total Spent  : " + str(u.get("spent", "0")))
        lines.append("    Reward Pts   : " + str(u.get("points", 0)))
        lines.append("")
    lines.append("=" * 65)
    lines.append("  NOTE: Passwords are NOT stored in this file.")
    lines.append("=" * 65)
    with open(USERS_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def write_orders_txt(orders_dict):
    order_list = list(orders_dict.values())
    order_list.sort(key=lambda o: o.get("time",""), reverse=True)
    lines = []
    lines.append("=" * 65)
    lines.append("       CanteenIQ  --  ALL ORDERS")
    lines.append("       Last updated : " + now_str())
    lines.append("       Total orders : " + str(len(order_list)))
    lines.append("=" * 65)
    lines.append("")
    if not order_list:
        lines.append("  No orders placed yet.")
        lines.append("")
    for i, o in enumerate(order_list, 1):
        lines.append("  Order #" + str(i) + "  " + "-" * 47)
        lines.append("    Order ID     : " + o.get("id",""))
        lines.append("    Item         : " + o.get("item",""))
        lines.append("    Student Name : " + o.get("student",""))
        lines.append("    Student ID   : " + o.get("sid",""))
        lines.append("    Department   : " + o.get("dept",""))
        lines.append("    Pickup Slot  : " + o.get("slot",""))
        lines.append("    Amount       : " + o.get("amt",""))
        lines.append("    Payment Mode : " + o.get("pay",""))
        lines.append("    Ordered At   : " + o.get("time",""))
        lines.append("    Status       : " + o.get("status","").upper())
        lines.append("")
    lines.append("=" * 65)
    with open(ORDERS_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def write_combined_txt(users_dict, orders_dict):
    user_list  = list(users_dict.values())
    order_list = list(orders_dict.values())
    order_list.sort(key=lambda o: o.get("time",""), reverse=True)
    lines = []
    lines.append("*" * 65)
    lines.append("*      CanteenIQ  --  COMPLETE DATA REPORT                   *")
    lines.append("*      Generated : " + now_str())
    lines.append("*" * 65)
    lines.append("")
    lines.append("=" * 65)
    lines.append("  SECTION 1 : REGISTERED USERS  (" + str(len(user_list)) + " total)")
    lines.append("=" * 65)
    lines.append("")
    for i, u in enumerate(user_list, 1):
        lines.append("  User #" + str(i) + "  " + "-" * 48)
        lines.append("    Name         : " + u.get("fname","") + " " + u.get("lname",""))
        lines.append("    Email        : " + u.get("email",""))
        lines.append("    Student ID   : " + u.get("sid",""))
        lines.append("    Department   : " + u.get("dept",""))
        lines.append("    Year / Batch : " + u.get("year",""))
        lines.append("    Registered   : " + u.get("registeredAt",""))
        lines.append("    Total Orders : " + str(u.get("orders", 0)))
        lines.append("    Total Spent  : " + str(u.get("spent", "0")))
        lines.append("    Reward Pts   : " + str(u.get("points", 0)))
        lines.append("")
    lines.append("  NOTE: Passwords are NOT stored in this file.")
    lines.append("")
    lines.append("=" * 65)
    lines.append("  SECTION 2 : ALL ORDERS  (" + str(len(order_list)) + " total)")
    lines.append("=" * 65)
    lines.append("")
    if not order_list:
        lines.append("  No orders placed yet.")
        lines.append("")
    for i, o in enumerate(order_list, 1):
        lines.append("  Order #" + str(i) + "  " + "-" * 47)
        lines.append("    Order ID     : " + o.get("id",""))
        lines.append("    Item         : " + o.get("item",""))
        lines.append("    Student Name : " + o.get("student",""))
        lines.append("    Student ID   : " + o.get("sid",""))
        lines.append("    Department   : " + o.get("dept",""))
        lines.append("    Pickup Slot  : " + o.get("slot",""))
        lines.append("    Amount       : " + o.get("amt",""))
        lines.append("    Payment Mode : " + o.get("pay",""))
        lines.append("    Ordered At   : " + o.get("time",""))
        lines.append("    Status       : " + o.get("status","").upper())
        lines.append("")
    lines.append("*" * 65)
    lines.append("*               END OF REPORT                                *")
    lines.append("*" * 65)
    with open(COMBINED_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def refresh_all_txt():
    write_users_txt(users_db)
    write_orders_txt(orders_db)
    write_combined_txt(users_db, orders_db)

# Load stored data
users_db  = load_json(USERS_JSON)
orders_db = load_json(ORDERS_JSON)
refresh_all_txt()

# USERS API
@app.route("/api/users", methods=["GET"])
def get_users():
    safe = [{k: v for k, v in u.items() if k != "password"} for u in users_db.values()]
    return jsonify(safe)

@app.route("/api/users/register", methods=["POST"])
def register_user():
    data  = request.json
    email = (data.get("email") or "").strip().lower()
    sid   = (data.get("sid")   or "").strip().lower()
    with lock:
        if email in users_db:
            return jsonify({"ok": False, "error": "email_taken"}), 409
        for u in users_db.values():
            if u.get("sid", "").lower() == sid:
                return jsonify({"ok": False, "error": "sid_taken"}), 409
        user = {
            "fname":        data.get("fname", "").strip(),
            "lname":        data.get("lname", "").strip(),
            "email":        email,
            "sid":          data.get("sid", "").strip(),
            "dept":         data.get("dept", ""),
            "year":         data.get("year", ""),
            "password":     data.get("password", ""),
            "registeredAt": datetime.datetime.now().strftime("%d %b %Y, %I:%M %p"),
            "orders":       0,
            "spent":        "0",
            "points":       0,
        }
        users_db[email] = user
        save_json(USERS_JSON, users_db)
        refresh_all_txt()
    safe = {k: v for k, v in user.items() if k != "password"}
    return jsonify({"ok": True, "user": safe}), 201

@app.route("/api/users/login", methods=["POST"])
def login_user():
    data  = request.json
    ident = (data.get("email") or "").strip().lower()
    pw    = data.get("password", "")
    with lock:
        for u in users_db.values():
            match = (u["email"].lower() == ident or u.get("sid", "").lower() == ident)
            if match and u.get("password", "") == pw:
                safe = {k: v for k, v in u.items() if k != "password"}
                return jsonify({"ok": True, "user": safe})
    return jsonify({"ok": False, "error": "invalid_credentials"}), 401

@app.route("/api/users/email-exists", methods=["GET"])
def email_exists():
    email = (request.args.get("email", "")).strip().lower()
    return jsonify({"exists": email in users_db})

@app.route("/api/users/sid-exists", methods=["GET"])
def sid_exists():
    sid   = (request.args.get("sid", "")).strip().lower()
    found = any(u.get("sid", "").lower() == sid for u in users_db.values())
    return jsonify({"exists": found})

@app.route("/api/users/update", methods=["POST"])
def update_user():
    data  = request.json
    email = (data.get("email", "")).strip().lower()
    with lock:
        if email in users_db:
            users_db[email].update({k: v for k, v in data.items() if k not in ("email","password")})
            save_json(USERS_JSON, users_db)
            refresh_all_txt()
    return jsonify({"ok": True})

# ORDERS API
@app.route("/api/orders", methods=["GET"])
def get_orders():
    return jsonify(list(orders_db.values()))

# SSE stream — owner browsers subscribe here
@app.route("/api/owner-events")
def owner_events():
    q = queue.Queue(maxsize=50)
    with _clients_lock:
        _owner_clients.append(q)
    def generate():
        # Send a keep-alive comment immediately
        yield ": connected\n\n"
        try:
            while True:
                try:
                    msg = q.get(timeout=25)
                    yield msg
                except queue.Empty:
                    yield ": ping\n\n"   # keep connection alive
        except GeneratorExit:
            pass
        finally:
            with _clients_lock:
                if q in _owner_clients:
                    _owner_clients.remove(q)
    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )

@app.route("/api/orders/save", methods=["POST"])
def save_order():
    order = request.json
    oid   = order.get("id", "")
    with lock:
        orders_db[oid] = order
        save_json(ORDERS_JSON, orders_db)
        refresh_all_txt()
    # Push real-time notification to all connected owner devices
    push_to_owners("new_order", order)
    return jsonify({"ok": True})

@app.route("/api/orders/update", methods=["POST"])
def update_order():
    order = request.json
    oid   = order.get("id", "")
    with lock:
        if oid in orders_db:
            orders_db[oid].update(order)
        else:
            orders_db[oid] = order
        save_json(ORDERS_JSON, orders_db)
        refresh_all_txt()
    return jsonify({"ok": True})

# Serve HTML
@app.route("/")
def index():
    return send_from_directory(".", "canteeniq.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("=" * 60)
    print("  CanteenIQ Backend Server")
    print(f"  Open in browser  ->  http://localhost:{port}")
    print("")
    print("  Notepad files auto-updated in same folder:")
    print("    " + os.path.abspath(USERS_TXT))
    print("    " + os.path.abspath(ORDERS_TXT))
    print("    " + os.path.abspath(COMBINED_TXT))
    print("=" * 60)
    app.run(debug=False, port=port, host="0.0.0.0")
