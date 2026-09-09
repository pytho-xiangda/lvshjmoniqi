"""Render the courtroom music set through a local 16bits-audio MCP server.

Python standard library only. The separately installed MIT server supplies all
composition and audio effects. No network access or model/API calls are made.
"""
from __future__ import annotations

import argparse
from array import array
import hashlib
import json
import math
from pathlib import Path
import queue
import subprocess
import sys
import tempfile
import threading
import wave

ROOT = Path(__file__).resolve().parents[1]


class AudioMcp:
    def __init__(self, executable: Path):
        self.errors = tempfile.TemporaryFile(mode="w+b")
        self.proc = subprocess.Popen(
            [str(executable)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=self.errors, text=True, encoding="utf-8", bufsize=1,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        self.responses: queue.Queue = queue.Queue()
        self.counter = 0
        threading.Thread(target=self._read, daemon=True).start()
        self.info = self.request("initialize", {
            "protocolVersion": "2024-11-05", "capabilities": {},
            "clientInfo": {"name": "court-bgm-renderer", "version": "1.0.0"},
        })
        self.send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def _read(self):
        try:
            for line in self.proc.stdout:
                self.responses.put(json.loads(line))
        except Exception as error:
            self.responses.put(error)
        finally:
            self.responses.put(EOFError("MCP server closed stdout"))

    def send(self, message):
        self.proc.stdin.write(json.dumps(message, ensure_ascii=True) + "\n")
        self.proc.stdin.flush()

    def request(self, method, params):
        self.counter += 1
        self.send({"jsonrpc": "2.0", "id": self.counter, "method": method, "params": params})
        while True:
            reply = self.responses.get(timeout=180)
            if isinstance(reply, Exception):
                raise reply
            if reply.get("id") != self.counter:
                continue
            if "error" in reply:
                raise RuntimeError(reply["error"])
            return reply["result"]

    def call(self, name, arguments):
        result = self.request("tools/call", {"name": name, "arguments": arguments})
        if result.get("isError"):
            raise RuntimeError(result)
        return result

    def close(self):
        try:
            self.proc.stdin.close()
            self.proc.wait(timeout=5)
        except (OSError, subprocess.TimeoutExpired):
            self.proc.kill()
            self.proc.wait()
        finally:
            self.errors.close()


def read_pcm(path):
    with wave.open(str(path), "rb") as stream:
        if stream.getnchannels() != 1 or stream.getsampwidth() != 2:
            raise ValueError("Expected mono 16-bit PCM from 16bits-audio")
        rate = stream.getframerate()
        pcm = array("h", stream.readframes(stream.getnframes()))
    if sys.byteorder != "little":
        pcm.byteswap()
    return rate, pcm


def finish_loop(source, target):
    rate, pcm = read_pcm(source)
    # Preserve the exact bar length. Smooth only 4 ms on each side of the wrap;
    # both endpoints meet at a shared value instead of fading the music to silence.
    width = min(round(rate * 0.004), len(pcm) // 4)
    boundary = (pcm[0] + pcm[-1]) / 2
    for i in range(width):
        weight = (1 - i / (width - 1)) ** 2
        pcm[i] = round(pcm[i] * (1 - weight) + boundary * weight)
        pcm[-1-i] = round(pcm[-1-i] * (1 - weight) + boundary * weight)
    peak = max(abs(v) for v in pcm)
    if peak == 0:
        raise ValueError("Renderer produced silence")
    gain = (32767 * 10 ** (-3 / 20)) / peak
    pcm = array("h", (round(v * gain) for v in pcm))
    if sys.byteorder != "little":
        pcm.byteswap()
    with wave.open(str(target), "wb") as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(rate)
        stream.writeframes(pcm.tobytes())


def inspect_audio(path, track, rate_expected):
    rate, pcm = read_pcm(path)
    peak = max(abs(v) for v in pcm)
    rms = math.sqrt(sum(v*v for v in pcm) / len(pcm))
    expected = track["duration_bars"] * track["beats_per_bar"] * 60 / track["bpm"]
    stats = {
        "frames": len(pcm), "sample_rate": rate, "channels": 1, "bits": 16,
        "duration_seconds": round(len(pcm) / rate, 6),
        "peak_dbfs": round(20 * math.log10(peak / 32768), 3),
        "rms_dbfs": round(20 * math.log10(rms / 32768), 3),
        "clipped_samples": sum(abs(v) >= 32767 for v in pcm),
        "loop_boundary_delta": abs(pcm[0] - pcm[-1]),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }
    assert rate == rate_expected and abs(len(pcm)/rate - expected) < 0.002, stats
    assert stats["clipped_samples"] == 0 and stats["loop_boundary_delta"] == 0, stats
    assert -40 < stats["rms_dbfs"] < -3, stats
    return stats


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server", type=Path, default=ROOT / ".audio_runtime/16bits-audio-mcp/zig-out/bin/16bits-audio-mcp.exe")
    parser.add_argument("--manifest", type=Path, default=ROOT / "docs/design/audio/court_bgm_16bits.json")
    parser.add_argument("--out", type=Path, default=ROOT / "assets/audio/bgm/court_16bits")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    args.out.mkdir(parents=True, exist_ok=True)
    targets = [args.out / (track["id"] + ".wav") for track in manifest["tracks"]]
    if not args.force and any(path.exists() for path in targets):
        parser.error("Output exists; use a new --out directory or --force")
    report = {"source": manifest["source"], "revision": manifest["revision"], "tracks": []}
    with tempfile.TemporaryDirectory(prefix="court-audio-") as work:
        for track, target in zip(manifest["tracks"], targets):
            # A fresh server resets upstream global percussion noise state, making
            # each result independent of earlier tool calls in an MCP session.
            client = AudioMcp(args.server.resolve())
            try:
                listing = client.request("tools/list", {})
                names = {item["name"] for item in listing["tools"]}
                assert {"bgm_compose", "wav_fx", "wav_info"} <= names
                raw = Path(work) / (track["id"] + "_raw.wav")
                processed = Path(work) / (track["id"] + "_fx.wav")
                fields = ("style", "bpm", "duration_bars", "key", "scale", "seed", "melody_density", "swing")
                params = {key: track[key] for key in fields}
                params.update(output=str(raw), sample_rate=manifest["sample_rate"], chord_progression=[
                    dict(zip(("root", "quality"), chord.split(":"))) for chord in track["chords"]
                ])
                client.call("bgm_compose", params)
                client.call("wav_fx", {"input": str(raw), "output": str(processed), "effects": track["effects"]})
                finish_loop(processed, target)
                stats = inspect_audio(target, track, manifest["sample_rate"])
                client.call("wav_info", {"path": str(target.resolve())})
                report["server"] = client.info["serverInfo"]
                report["tool_count"] = len(names)
                report["tracks"].append({"id": track["id"], "title": track["title"], **stats})
                print(json.dumps({"title": track["title"], **stats}, ensure_ascii=False), flush=True)
            finally:
                client.close()
    (args.out / "audio_validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
