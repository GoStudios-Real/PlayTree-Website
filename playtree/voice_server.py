#!/usr/bin/env python3
"""PLAYTREE Hosted Voice & Chat Server.
Provides WebRTC signaling + text chat rooms + player presence for the website.
Deploy to Render/Railway/Fly.io or run locally.

Usage:
  pip install fastapi uvicorn
  uvicorn voice_server:app --host 0.0.0.0 --port 8000

Endpoints:
  GET  /              - health check
  WS   /ws/{room}     - signaling + chat: clients send JSON {type, ...}
  POST /rooms         - list active rooms
"""
import json
import time
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="PLAYTREE Voice & Chat")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

rooms = {}  # room name -> dict of websocket -> player info


@app.get("/")
def health():
    return {"service": "PLAYTREE Voice & Chat", "status": "online",
            "rooms": len(rooms), "version": "1.7.0"}


@app.get("/rooms")
def list_rooms():
    return [{"name": name, "players": len(peers)} for name, peers in rooms.items()]


@app.websocket("/ws/{room}")
async def websocket_endpoint(ws: WebSocket, room: str):
    await ws.accept()
    if room not in rooms:
        rooms[room] = {}
    peers = rooms[room]
    pid = str(int(time.time() * 1000))[-6:]
    peers[ws] = {"id": pid, "name": "Player" + pid[-3:]}

    # Send welcome + existing peer list
    await ws.send_json({"type": "welcome", "id": pid,
                        "peers": [p for p in peers.values() if p["id"] != pid]})
    # Notify others
    for other in list(peers.keys()):
        if other != ws:
            try:
                await other.send_json({"type": "peer_joined", "peer": peers[ws]})
            except Exception:
                pass

    try:
        while True:
            data = await ws.receive_json()
            typ = data.get("type")

            if typ == "rename":
                peers[ws]["name"] = str(data.get("name", "Player"))[:24]
                for other in list(peers.keys()):
                    if other != ws:
                        await other.send_json({"type": "peer_update", "peer": peers[ws]})

            elif typ == "signal":
                # WebRTC offer/answer/ICE - forward to target peer
                target_id = data.get("to")
                for other, info in peers.items():
                    if info["id"] == target_id:
                        await other.send_json({"type": "signal", "from": pid,
                                               "data": data.get("data")})
                        break

            elif typ == "chat":
                text = str(data.get("text", ""))[:500]
                for other in list(peers.keys()):
                    await other.send_json({"type": "chat", "from": peers[ws]["name"],
                                           "text": text, "time": time.time()})

            elif typ == "voice_state":
                # speaking / muted status
                for other in list(peers.keys()):
                    if other != ws:
                        await other.send_json({"type": "voice_state", "from": pid,
                                               "speaking": data.get("speaking", False)})
    except WebSocketDisconnect:
        pass
    finally:
        left = peers.pop(ws, None)
        for other in list(peers.keys()):
            try:
                await other.send_json({"type": "peer_left", "id": left["id"] if left else pid})
            except Exception:
                pass
        if not peers:
            rooms.pop(room, None)
