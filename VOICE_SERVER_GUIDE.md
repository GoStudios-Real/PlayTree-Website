# PLAYTREE Voice & Chat Server - Deployment Guide
================================================

The hosted voice server (voice_server.py) provides WebRTC signaling + text chat
rooms for PLAYTREE Voice at https://gostudios-real.github.io/PlayTree-Website/voice.html

## Run locally
  pip install fastapi uvicorn
  uvicorn voice_server:app --host 0.0.0.0 --port 8000
  Then open http://localhost:8000/ and voice.html will connect via ws://localhost:8000

## Deploy to a free host (Render.com - recommended)
  1. Create a free account at https://render.com
  2. New > Web Service > connect your GitHub repo GoStudios-Real/PlayTree-Website
  3. Settings:
     - Build Command:  pip install fastapi uvicorn
     - Start Command:  uvicorn playtree.voice_server:app --host 0.0.0.0 --port $PORT
  4. Deploy. You'll get a URL like https://playtree-voice.onrender.com
  5. Edit website/voice.html: set VOICE_SERVER to your URL (wss://...)
     or add <meta name="voice-server" content="wss://your-url">

## Deploy to Railway/Fly.io
  Similar: install fastapi+uvicorn, run "uvicorn voice_server:app --host 0.0.0.0 --port $PORT"

## In-game voice (desktop)
  Voice chat in the .exe uses direct UDP (src/voice_chat.py) on ports 7778+playerID
  for players on the same game server. Hold V to push-to-talk.
  For internet-wide in-game voice, host a UDP relay or use the web voice page.
