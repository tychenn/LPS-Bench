#!/usr/bin/env python3
"""Synthesize the original 90-second LPS-Bench film score and transition sounds.

Requires NumPy and SciPy. No samples, prerecorded music, speech, or network
services are used. The deterministic arrangement follows the film's eight
scenes; export is a stereo, 48 kHz, 24-bit PCM WAV with generous voiceover space.

Example:
    python scripts/video_audio.py --output tmp/video-audio/score.wav
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import wave

import numpy as np
from scipy import signal


SAMPLE_RATE = 48_000
DURATION = 90.0
TEMPO = 82.0
SEED = 847
SCENE_HITS = (8.0, 20.0, 30.0, 43.0, 57.0, 71.0, 81.0)
# start, end, bass MIDI note, open upper voicing. Shared notes soften changes.
HARMONY = (
    (0.0, 8.0, 38, (50, 57, 60, 65, 76)),
    (8.0, 14.0, 38, (50, 57, 60, 65, 76)),
    (14.0, 20.0, 34, (53, 58, 62, 65, 72)),
    (20.0, 25.0, 41, (53, 60, 64, 67, 69)),
    (25.0, 30.0, 36, (55, 60, 62, 67, 76)),
    (30.0, 36.5, 43, (55, 58, 62, 65, 69)),
    (36.5, 43.0, 34, (53, 58, 62, 65, 72)),
    (43.0, 50.0, 38, (50, 57, 60, 65, 76)),
    (50.0, 57.0, 36, (55, 60, 62, 67, 76)),
    (57.0, 64.0, 34, (53, 58, 62, 65, 72)),
    (64.0, 71.0, 41, (53, 60, 64, 67, 69)),
    (71.0, 76.0, 43, (55, 58, 62, 65, 69)),
    (76.0, 81.0, 36, (55, 60, 62, 67, 76)),
    (81.0, 90.0, 41, (53, 60, 64, 67, 69)),
)


def midi_frequency(note: float) -> float:
    return 440.0 * 2.0 ** ((note - 69.0) / 12.0)


def times(duration: float) -> np.ndarray:
    return np.arange(round(duration * SAMPLE_RATE), dtype=np.float64) / SAMPLE_RATE


def envelope(t: np.ndarray, attack: float, release: float) -> np.ndarray:
    duration = len(t) / SAMPLE_RATE
    rise = np.clip(t / attack, 0.0, 1.0)
    fall = np.clip((duration - t) / release, 0.0, 1.0)
    return np.sin(rise * np.pi / 2.0) ** 2 * np.sin(fall * np.pi / 2.0) ** 2


def add(
    target: np.ndarray,
    audio: np.ndarray,
    start: float,
    gain: float = 1.0,
    pan: float = 0.0,
) -> None:
    offset = round(start * SAMPLE_RATE)
    trim = max(0, -offset)
    offset = max(0, offset)
    length = min(len(audio) - trim, len(target) - offset)
    if length <= 0:
        return
    audio = audio[trim : trim + length]
    if audio.ndim == 1:
        angle = (pan + 1.0) * np.pi / 4.0
        target[offset : offset + length, 0] += gain * np.cos(angle) * audio
        target[offset : offset + length, 1] += gain * np.sin(angle) * audio
    else:
        target[offset : offset + length] += gain * audio


def chord_at(time: float) -> tuple:
    return next(chord for chord in HARMONY if chord[0] <= time < chord[1])


def filtered_noise(rng: np.random.Generator, duration: float, low: float, high: float) -> np.ndarray:
    noise = rng.normal(0.0, 1.0, round(duration * SAMPLE_RATE))
    sos = signal.butter(2, (low, high), btype="bandpass", fs=SAMPLE_RATE, output="sos")
    noise = signal.sosfilt(sos, noise)
    return noise / max(np.std(noise), 1e-9)


def render_pads(track: np.ndarray, rng: np.random.Generator) -> None:
    for start, end, _, notes in HARMONY:
        onset = start - 0.8 if start else 0.0
        t = times(end - onset + 2.6)
        pad = np.zeros((len(t), 2))
        for index, note in enumerate(notes):
            frequency = midi_frequency(note)
            phase = rng.uniform(0.0, 2.0 * np.pi)
            for channel, cents in enumerate((-3.1, 3.4)):
                detuned = frequency * 2 ** (cents / 1200.0)
                drift = 0.045 * np.sin(2 * np.pi * (0.073 + index * 0.009) * t + phase)
                angle = 2 * np.pi * detuned * t + phase + drift
                voice = np.sin(angle) + 0.17 * np.sin(2 * angle + 0.4)
                voice += 0.045 * np.sin(3 * angle + 1.2)
                breathe = 0.86 + 0.14 * np.sin(2 * np.pi * 0.09 * t + index)
                pad[:, channel] += voice * breathe / (len(notes) ** 0.5)
        pad *= envelope(t, 2.1, 3.0)[:, None]
        gain = 0.080 if start < 20 else 0.092
        if start >= 57:
            gain = 0.108
        add(track, pad, onset, gain)


def render_pulses(track: np.ndarray, rng: np.random.Generator) -> None:
    beat = 60.0 / TEMPO
    for index, onset in enumerate(np.arange(0.8, 85.0, beat)):
        _, _, bass, _ = chord_at(float(onset))
        if onset < 8 and index % 2:
            continue
        if 30 < onset < 43 and index % 4 == 3:
            continue
        if onset > 81 and index % 2:
            continue
        t = times(0.82 if onset < 20 else 0.66)
        frequency = midi_frequency(bass)
        phase = 2.0 * np.pi * frequency * t
        body = np.sin(phase) + 0.24 * np.sin(phase * 2.0)
        body += 0.05 * np.sin(phase * 3.0)
        pulse = body * envelope(t, 0.035, 0.25) * np.exp(-t * 2.3)
        accent = 1.0 if index % 4 == 0 else 0.75
        add(track, pulse, float(onset), 0.115 * accent * rng.uniform(0.92, 1.02))

        if onset >= 20 and onset < 81 and index % 2 == 0:
            kt = times(0.42)
            kick_phase = 2 * np.pi * (43 * kt + 22 * 0.035 * (1 - np.exp(-kt / 0.035)))
            kick = np.sin(kick_phase) * np.exp(-kt * 12) * envelope(kt, 0.006, 0.1)
            add(track, kick, float(onset), 0.11 if onset >= 43 else 0.075)


def render_details(track: np.ndarray, rng: np.random.Generator) -> None:
    beat = 60.0 / TEMPO
    pattern = (0, 2, 3, 1, 4, 2, 1, 3)
    echo = np.zeros_like(track)
    for index, onset in enumerate(np.arange(8.15, 84.0, beat / 2.0)):
        if onset < 20 and index % 2:
            continue
        if 30 < onset < 43 and index % 3 == 2:
            continue
        if onset > 81 and index % 3:
            continue
        if index % 16 == 15:
            continue
        _, _, _, notes = chord_at(float(onset))
        note = notes[pattern[index % len(pattern)]] + 12
        t = times(1.4)
        frequency = midi_frequency(note)
        phase = 2 * np.pi * frequency * t
        pluck = np.sin(phase) * np.exp(-t * 4.3)
        pluck += 0.11 * np.sin(phase * 2) * np.exp(-t * 8.0)
        pluck *= envelope(t, 0.012, 0.22)
        pan = (-0.47, 0.31, -0.16, 0.57)[index % 4]
        velocity = rng.uniform(0.75, 1.0)
        gain = (0.029 if onset < 43 else 0.043) * velocity
        actual_onset = float(onset) + rng.uniform(-0.008, 0.008)
        add(track, pluck, actual_onset, gain, pan)
        for delay, decay in ((beat * 0.75, 0.28), (beat * 1.5, 0.14), (beat * 2.25, 0.065)):
            add(echo, pluck, actual_onset + delay, gain * decay, -pan)

    # Airy, quiet percussion introduces motion without competing with narration.
    for index, onset in enumerate(np.arange(20.25, 80.5, beat / 2)):
        if index % 4 in (0, 3):
            continue
        t = times(0.13)
        hat = filtered_noise(rng, len(t) / SAMPLE_RATE, 4400, 8500)
        hat *= np.exp(-t * 42) * envelope(t, 0.005, 0.055)
        add(track, hat, float(onset), rng.uniform(0.010, 0.016), rng.uniform(-0.65, 0.65))
    track += echo

    # A spacious upper motif is introduced only in the second half.
    motif = ((57.8, 77), (60.8, 74), (64.9, 76), (67.8, 79), (71.8, 81), (75.0, 77), (78.1, 76), (82.0, 81), (84.0, 79))
    for index, (onset, note) in enumerate(motif):
        t = times(4.6)
        phase = 2 * np.pi * midi_frequency(note) * t
        bell = (np.sin(phase) + 0.15 * np.sin(phase * 2.0)) * np.exp(-t * 0.8)
        bell *= envelope(t, 0.035, 1.5)
        add(track, bell, onset, 0.041, 0.24 * (-1) ** index)
        add(track, bell, onset + beat * 1.5, 0.014, -0.30 * (-1) ** index)


def render_transitions(track: np.ndarray, rng: np.random.Generator) -> None:
    for index, hit in enumerate(SCENE_HITS):
        # Gentle stereo riser, with a gap before the low impact.
        t = times(1.8)
        noise = filtered_noise(rng, 1.8, 650, 5200)
        swell = np.sin(np.clip(t / 1.8, 0, 1) * np.pi / 2) ** 2.7
        swell *= envelope(t, 0.35, 0.13)
        air = noise * swell
        add(track, air, hit - 1.85, 0.021, -0.35)
        add(track, air, hit - 1.81, 0.016, 0.42)

        t = times(2.2)
        phase = 2 * np.pi * (39 * t + 30 * 0.11 * (1 - np.exp(-t / 0.11)))
        impact = np.sin(phase) * np.exp(-t * 3.2) * envelope(t, 0.009, 0.35)
        add(track, impact, hit, 0.23 if index in (3, 4, 6) else 0.18)

        tail = filtered_noise(rng, 2.2, 1100, 6300)
        tail *= np.exp(-t * 2.9) * envelope(t, 0.018, 0.5)
        add(track, tail, hit + 0.018, 0.013, 0.42)
        add(track, tail, hit + 0.048, 0.010, -0.45)


def write_pcm24(path: Path, audio: np.ndarray) -> None:
    pcm = np.round(np.clip(audio, -1.0, 1.0 - 1 / 2**23) * (2**23)).astype(np.int32)
    packed = np.empty((pcm.size, 3), dtype=np.uint8)
    values = pcm.ravel()
    packed[:, 0] = values & 255
    packed[:, 1] = (values >> 8) & 255
    packed[:, 2] = (values >> 16) & 255
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as output:
        output.setnchannels(2)
        output.setsampwidth(3)
        output.setframerate(SAMPLE_RATE)
        output.writeframes(packed.tobytes())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("tmp/video-audio/score.wav"))
    args = parser.parse_args()
    rng = np.random.default_rng(SEED)
    score = np.zeros((round(DURATION * SAMPLE_RATE), 2), dtype=np.float64)
    render_pads(score, rng)
    render_pulses(score, rng)
    render_details(score, rng)
    render_transitions(score, rng)

    # Remove rumble/DC, tame highs, and add a quiet diffuse stereo room.
    filters = signal.butter(2, (29, 11000), btype="bandpass", fs=SAMPLE_RATE, output="sos")
    score = signal.sosfilt(filters, score, axis=0)
    dry = score.copy()
    for delay, gain in ((0.071, 0.09), (0.113, 0.065), (0.179, 0.048), (0.293, 0.034), (0.467, 0.023)):
        samples = round(delay * SAMPLE_RATE)
        score[samples:] += dry[:-samples, ::-1] * gain
    del dry

    timeline = times(DURATION)
    score *= envelope(timeline, 1.4, 4.8)[:, None]
    # Smooth peak control with plenty of headroom; no hard clipping.
    score = np.tanh(score * 1.3) / 1.3
    peak = float(np.max(np.abs(score)))
    score *= 10 ** (-4.0 / 20) / max(peak, 1e-9)
    write_pcm24(args.output, score)

    peak = float(np.max(np.abs(score)))
    rms = float(np.sqrt(np.mean(score**2)))
    stats = {
        "file": str(args.output),
        "duration_seconds": DURATION,
        "sample_rate": SAMPLE_RATE,
        "channels": 2,
        "bit_depth": 24,
        "peak_dbfs": round(float(20 * np.log10(peak)), 2),
        "rms_dbfs": round(float(20 * np.log10(rms)), 2),
        "scene_hits_seconds": SCENE_HITS,
        "tempo_bpm": TEMPO,
        "seed": SEED,
        "provenance": "Original procedural composition; no third-party recordings or samples.",
    }
    args.output.with_suffix(".json").write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
