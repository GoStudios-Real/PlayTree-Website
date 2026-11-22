#!/usr/bin/env python3
"""PLAYTREE Lobby Server - Real multiplayer servers (join/host).

Usage:
  pip install flask flask-cors
  python lobby_server.py
  # Runs on http://localhost:5001

Endpoints:
  GET  /servers          - List all servers
  POST /servers          - Host a new server {name, mode, max_players}
  POST /servers/<id>/join - Join a server {player_name}
  POST /servers/<id>/leave - Leave a server {player_name}
  DELETE /servers/<id>   - Delete a server (host only)
"""
import os, uuid, time
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

servers = {}
MAX_SERVERS = 50

def seed_servers():
    defaults = [
        {"name": "GoStudios Official #1", "detail": "Chapter 0 - Season 0 | PvP Enabled", "max_players": 32, "mode": "pvp"},
        {"name": "GoStudios Official #2", "detail": "Chapter 0 - Season 0 | PvE Only", "max_players": 32, "mode": "pve"},
        {"name": "Community - Fast XP", "detail": "Custom rules | 2x XP | Friendly", "max_players": 32, "mode": "custom"},
    ]
    for d in defaults:
        sid = str(uuid.uuid4())[:8]
        servers[sid] = {
            "id": sid, "name": d["name"], "detail": d["detail"],
            "mode": d["mode"], "max_players": d["max_players"],
            "players": [], "online": True, "created": time.time(),
        }

seed_servers()


@app.route("/servers", methods=["GET"])
def list_servers():
    out = []
    for s in servers.values():
        out.append({
            "id": s["id"], "name": s["name"], "detail": s["detail"],
            "mode": s["mode"], "max_players": s["max_players"],
            "players": len(s["players"]), "online": s["online"],
        })
    return jsonify(out)


@app.route("/servers", methods=["POST"])
def host_server():
    if len(servers) >= MAX_SERVERS:
        return jsonify({"error": "Server limit reached"}), 429
    data = request.get_json() or {}
    name = data.get("name", "Unnamed Server").strip()[:40]
    if not name:
        return jsonify({"error": "Name required"}), 400
    sid = str(uuid.uuid4())[:8]
    servers[sid] = {
        "id": sid, "name": name,
        "detail": data.get("detail", "Custom server"),
        "mode": data.get("mode", "custom"),
        "max_players": min(int(data.get("max_players", 16)), 64),
        "players": [data.get("host", "Host")],
        "online": True, "created": time.time(),
        "host": data.get("host", "Host"),
    }
    return jsonify(servers[sid]), 201


@app.route("/servers/<sid>/join", methods=["POST"])
def join_server(sid):
    s = servers.get(sid)
    if not s:
        return jsonify({"error": "Server not found"}), 404
    if not s["online"]:
        return jsonify({"error": "Server offline"}), 400
    if len(s["players"]) >= s["max_players"]:
        return jsonify({"error": "Server full"}), 400
    data = request.get_json() or {}
    name = data.get("player_name", "Player")
    if name not in s["players"]:
        s["players"].append(name)
    return jsonify({"ok": True, "server": s["id"], "players": len(s["players"])})


@app.route("/servers/<sid>/leave", methods=["POST"])
def leave_server(sid):
    s = servers.get(sid)
    if not s:
        return jsonify({"error": "Server not found"}), 404
    data = request.get_json() or {}
    name = data.get("player_name", "Player")
    if name in s["players"]:
        s["players"].remove(name)
    return jsonify({"ok": True, "players": len(s["players"])})


@app.route("/servers/<sid>", methods=["DELETE"])
def delete_server(sid):
    s = servers.get(sid)
    if not s:
        return jsonify({"error": "Server not found"}), 404
    data = request.get_json() or {}
    if data.get("host") != s.get("host"):
        return jsonify({"error": "Only host can delete"}), 403
    del servers[sid]
    return jsonify({"ok": True})


if __name__ == "__main__":
    port = int(os.environ.get("LOBBY_PORT", 5001))
    print(f"Lobby server running on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
