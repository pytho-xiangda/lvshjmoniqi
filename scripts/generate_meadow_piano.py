"""Compose and render a gentle solo-piano piece using a local SoundFont.

Requires numpy, mido and tinysoundfont. No network, API or audio device needed.
The MIDI, note timing and audio validation are exported with the recording.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import random
import wave

import mido
import numpy as np
import tinysoundfont

ROOT = Path(__file__).resolve().parents[1]
RATE = 44100
TICKS = 960

# Root-position names describe the harmony; the voicings use gentle inversions.
HARMONIES = [
    ("Dadd9", [50, 57, 66, 64]), ("Aadd9/C#", [49, 57, 64, 71]),
    ("Bm7", [47, 54, 62, 69]), ("Gmaj7", [43, 55, 62, 66]),
    ("D/F#", [54, 57, 62, 66]), ("Em7", [52, 59, 62, 67]),
    ("Gadd9", [43, 55, 62, 69]), ("Asus4", [45, 57, 62, 64]),
]
THEME = [
    [(0.5, 69, 1.0), (2.0, 74, 1.35), (3.5, 76, 0.4)],
    [(0.25, 73, 1.4), (2.25, 71, 0.85), (3.5, 69, 0.4)],
    [(0.5, 71, 1.05), (2.0, 74, 1.6)],
    [(0.25, 71, 1.25), (2.0, 69, 0.7), (3.0, 66, 0.7)],
    [(0.5, 66, 1.2), (2.25, 69, 1.4)],
    [(0.25, 67, 1.4), (2.0, 71, 1.0), (3.5, 69, 0.35)],
    [(0.75, 69, 1.2), (2.5, 67, 1.1)],
    [(0.25, 64, 1.4), (2.0, 66, 0.8), (3.25, 69, 0.5)],
]
MIDDLE = [
    [(0.5, 78, 1.3), (2.25, 76, 1.0), (3.5, 74, 0.4)],
    [(0.5, 76, 1.5), (2.5, 73, 1.0)],
    [(0.25, 74, 1.0), (1.75, 78, 0.7), (3.0, 76, 0.7)],
    [(0.5, 74, 1.3), (2.25, 71, 1.3)],
    [(0.75, 69, 1.1), (2.25, 66, 1.0)],
    [(0.5, 67, 1.0), (2.0, 71, 1.5)],
    [(0.25, 74, 1.4), (2.25, 69, 1.1)],
    [(0.75, 71, 1.0), (2.5, 69, 1.0)],
]


def make_score():
    rng = random.Random(260910)
    events = []
    notes = []
    bars = []
    time = 0.6
    tempi = [64, 63, 64, 62, 64, 63, 62, 61]
    for bar in range(24):
        index = bar % 8
        bpm = tempi[index] + (1 if 8 <= bar < 16 else 0)
        if bar >= 21:
            bpm = [60, 58, 55][bar - 21]
        beat = 60 / bpm
        harmony, voicing = HARMONIES[index]
        motif = (MIDDLE if 8 <= bar < 16 else THEME)[index]
        if bar == 23:
            harmony, voicing = "Dadd9", [50, 57, 66, 64]
            motif = [(0.4, 69, 2.5), (0.46, 74, 2.45)]
        bars.append({"bar": bar + 1, "bpm": bpm, "harmony": harmony, "start_seconds": round(time, 6)})
        for channel in (0, 1):
            events.append((time + 0.06, "cc", channel, 64, 100))
            events.append((time + 3.88 * beat, "cc", channel, 64, 0))

        def add_note(offset, pitch, duration, velocity, channel):
            start = time + max(0.01, offset * beat + rng.uniform(-0.016, 0.016))
            end = min(start + duration * beat, time + 3.8 * beat)
            velocity = max(26, min(62, velocity + rng.randint(-3, 3)))
            events.extend([(start, "on", channel, pitch, velocity), (end, "off", channel, pitch, 0)])
            notes.append({"start": round(start, 6), "end": round(end, 6), "pitch": pitch, "velocity": velocity, "hand": "left" if channel == 0 else "right"})

        # Wide spacing and modest bass velocities keep the accompaniment airy.
        softening = 4 if bar >= 20 else 0
        for i, pitch in enumerate(voicing):
            if bar == 23 and i == 3:
                continue
            offset = [0.0, 1.0, 2.0, 3.0][i]
            if bar == 23:
                offset = i * 0.08
            add_note(offset, pitch, 1.55 if bar != 23 else 3.4, (35 if i == 0 else 39) - softening, 0)
        for index_note, (offset, pitch, duration) in enumerate(motif):
            velocity = 49 + (3 if 8 <= bar < 16 else 0) - softening
            if index_note == len(motif) - 1:
                velocity -= 3
            add_note(offset, pitch, duration, velocity, 1)
        time += 4 * beat
    priority = {"off": 0, "cc": 1, "on": 2}
    events.sort(key=lambda item: (item[0], priority[item[1]]))
    return events, notes, bars, time + 5.5


def export_midi(events, path):
    # Absolute expressive timing is encoded against a constant 60 BPM grid.
    midi = mido.MidiFile(ticks_per_beat=TICKS)
    track = mido.MidiTrack()
    midi.tracks.append(track)
    track.append(mido.MetaMessage("track_name", name="Clouds over the Meadow - Solo Piano"))
    track.append(mido.MetaMessage("set_tempo", tempo=1000000))
    track.append(mido.MetaMessage("time_signature", numerator=4, denominator=4))
    for channel in (0, 1):
        track.append(mido.Message("program_change", channel=channel, program=0))
    previous = 0
    for seconds, kind, channel, value, amount in events:
        tick = round(seconds * TICKS)
        delta = tick - previous
        previous = tick
        if kind == "cc":
            message = mido.Message("control_change", channel=channel, control=value, value=amount, time=delta)
        else:
            message = mido.Message("note_on" if kind == "on" else "note_off", channel=channel, note=value, velocity=amount, time=delta)
        track.append(message)
    track.append(mido.MetaMessage("end_of_track", time=5*TICKS))
    midi.save(path)


def render(soundfont, events, duration):
    synth = tinysoundfont.Synth(gain=-8, samplerate=RATE)
    sfid = synth.sfload(str(soundfont))
    preset = synth.sfpreset_name(sfid, 0, 0)
    for channel in (0, 1):
        synth.program_select(channel, sfid, 0, 0)
    frames = round(duration * RATE)
    audio = np.zeros((frames, 2), dtype=np.float32)
    cursor = 0
    for seconds, kind, channel, value, amount in events:
        target = round(seconds * RATE)
        if target > cursor:
            audio[cursor:target] = np.frombuffer(synth.generate(target-cursor), dtype=np.float32).reshape(-1, 2)
            cursor = target
        if kind == "on":
            synth.noteon(channel, value, amount)
        elif kind == "off":
            synth.noteoff(channel, value)
        else:
            synth.control_change(channel, value, amount)
    audio[cursor:] = np.frombuffer(synth.generate(frames-cursor), dtype=np.float32).reshape(-1, 2)
    # Quiet early reflections add space without a pad or a noticeable echo beat.
    dry = audio.copy()
    for delay, gain in [(0.047, 0.045), (0.083, 0.035), (0.137, 0.025), (0.211, 0.018)]:
        shift = round(delay * RATE)
        audio[shift:] += dry[:-shift, ::-1] * gain
    audio[-2*RATE:] *= np.linspace(1, 0, 2*RATE, dtype=np.float32)[:, None]
    audio *= (10 ** (-5 / 20)) / np.max(np.abs(audio))
    return audio, preset


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--soundfont", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=ROOT / "assets/audio/bgm/meadow_piano")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    name = "07_clouds_over_meadow"
    wav_path = args.out / (name + ".wav")
    if wav_path.exists():
        parser.error("Output already exists; choose a new --out directory")
    events, notes, bars, duration = make_score()
    audio, preset = render(args.soundfont, events, duration)
    assert np.isfinite(audio).all() and np.max(np.abs(audio)) < 1
    pcm = np.rint(audio * 32767).astype("<i2")
    with wave.open(str(wav_path), "wb") as stream:
        stream.setnchannels(2)
        stream.setsampwidth(2)
        stream.setframerate(RATE)
        stream.writeframes(pcm.tobytes())
    export_midi(events, args.out / (name + ".mid"))
    score = {"title": "草地上的云", "key": "D major", "meter": "4/4", "seed": 260910, "bars": bars, "notes": notes}
    (args.out / "score.json").write_text(json.dumps(score, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = {
        "title": score["title"], "duration_seconds": len(audio) / RATE,
        "sample_rate": RATE, "channels": 2, "bits": 16, "preset": preset,
        "soundfont_sha256": hashlib.sha256(args.soundfont.read_bytes()).hexdigest(),
        "peak_dbfs": float(20*np.log10(np.max(np.abs(pcm.astype(float))) / 32768)),
        "rms_dbfs": float(20*np.log10(np.sqrt(np.mean((pcm.astype(float)/32768)**2)))),
        "clipped_samples": int(np.sum(np.abs(pcm.astype(np.int32)) >= 32767)),
        "note_count": len(notes), "sha256": hashlib.sha256(wav_path.read_bytes()).hexdigest(),
        "loop": False,
    }
    assert report["clipped_samples"] == 0 and report["rms_dbfs"] > -40
    (args.out / "audio_validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
