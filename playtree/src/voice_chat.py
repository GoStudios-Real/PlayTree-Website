"""PLAYTREE Voice Chat - push-to-talk VOIP over UDP.
Uses sounddevice for mic capture and playback, numpy for level detection.
Press V (push-to-talk) to transmit your voice to other players on the server.

Voice protocol: raw 16-bit mono PCM @ 16kHz, 20ms frames (320 samples).
Packets: b'PTVO' + 4-byte sequence + 4-byte sender id + PCM bytes.
"""
import socket
import struct
import threading
import time
import os

RATE = 16000
FRAME = 320  # 20ms
MAGIC = b'PTVO'

try:
    import sounddevice as sd
    import numpy as np
    HAS_AUDIO = True
except Exception:
    sd = None
    np = None
    HAS_AUDIO = False


class VoiceChat:
    def __init__(self, player_id=0):
        self.available = HAS_AUDIO
        self.enabled = False  # toggled on/off
        self.ptt = False  # push-to-talk state (V held)
        self.muted = False
        self.volume = 1.0
        self.player_id = player_id
        self.sock = None
        self.target = None  # (ip, port) for outbound
        self.bind_port = 7778
        self.running = False
        self._thread = None
        self._out_stream = None
        self.last_packet_time = 0
        self.active_speakers = {}  # player_id -> timestamp

    def start(self, target_ip="127.0.0.1", target_port=7778, player_id=0):
        if not self.available or self.running:
            return False
        self.player_id = player_id
        self.target = (target_ip, target_port)
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(("0.0.0.0", self.bind_port + player_id))
            self.sock.settimeout(0.05)
            self._out_stream = sd.OutputStream(samplerate=RATE, channels=1,
                                               dtype='int16', blocksize=FRAME)
            self._out_stream.start()
            self.running = True
            self._thread = threading.Thread(target=self._recv_loop, daemon=True)
            self._thread.start()
            return True
        except Exception as e:
            print("VoiceChat start error:", e)
            return False

    def stop(self):
        self.running = False
        if self._out_stream:
            try:
                self._out_stream.stop()
                self._out_stream.close()
            except Exception:
                pass
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass

    def set_ptt(self, active):
        """Call on V keydown/keyup."""
        self.ptt = active

    def send_frame(self, audio_bytes):
        if not self.enabled or not self.sock or not self.target or self.muted:
            return
        seq = int(time.time() * 1000) & 0xFFFFFFFF
        pkt = MAGIC + struct.pack("<II", seq, self.player_id) + audio_bytes
        try:
            self.sock.sendto(pkt, self.target)
        except Exception:
            pass

    def capture_and_send(self):
        """Blocking capture of one frame; call from a background thread."""
        if not self.available or not self.running:
            return
        try:
            data = sd.rec(FRAME, samplerate=RATE, channels=1, dtype='int16', blocking=True)
            flat = data.flatten()
            level = float(np.abs(flat.astype(np.float32)).mean()) if np else 0
            if self.ptt and level > 40:  # gate: only speak above noise floor
                self.send_frame(flat.astype('<i2').tobytes())
        except Exception:
            pass

    def _recv_loop(self):
        while self.running:
            try:
                data, _ = self.sock.recvfrom(4096)
                if len(data) < 12 or data[:4] != MAGIC:
                    continue
                pid = struct.unpack("<I", data[8:12])[0]
                pcm = data[12:]
                if len(pcm) == FRAME * 2 and pid != self.player_id and self.enabled and not self.muted:
                    self.active_speakers[pid] = time.time()
                    if self._out_stream:
                        audio = np.frombuffer(pcm, dtype='<i2') if np else None
                        if audio is not None:
                            self._out_stream.write((audio * self.volume).astype('<i2'))
            except Exception:
                pass

    def speaking_now(self):
        """Return list of player IDs speaking in last 0.3s."""
        now = time.time()
        return [pid for pid, t in self.active_speakers.items() if now - t < 0.3]
