#!/usr/bin/env python3
"""Generate timed neural narration and mix the original LPS-Bench film score.

Requires edge-tts, NumPy, SciPy, and a complete FFmpeg binary. Cached narration
is reused only when its text, voice, and rate match. No credentials are needed;
the Edge speech service requires a working internet connection.

Example:
    tmp/video-tools/venv/bin/python scripts/video_narration.py \
        --ffmpeg tmp/video-tools/ffmpeg --voice en-US-AndrewMultilingualNeural
"""

from __future__ import annotations

import argparse
import asyncio
from difflib import SequenceMatcher
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

import edge_tts
import numpy as np

from video_audio import SAMPLE_RATE, write_pcm24


ROOT = Path(__file__).resolve().parents[1]


def run_ffmpeg(ffmpeg: str, args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run([ffmpeg, "-hide_banner", "-nostdin", "-y", *args], check=True, capture_output=True)


def read_audio(ffmpeg: str, path: Path, channels: int = 1) -> np.ndarray:
    result = run_ffmpeg(ffmpeg, ["-i", str(path), "-f", "f32le", "-acodec", "pcm_f32le", "-ar", str(SAMPLE_RATE), "-ac", str(channels), "-"])
    audio = np.frombuffer(result.stdout, dtype="<f4").astype(np.float64)
    return audio if channels == 1 else audio.reshape(-1, channels)


def measure_loudness(ffmpeg: str, path: Path, target: float = -16.0, peak: float = -1.5) -> dict:
    result = run_ffmpeg(ffmpeg, ["-i", str(path), "-af", f"loudnorm=I={target}:TP={peak}:LRA=11:print_format=json", "-f", "null", "-"])
    match = re.search(r'\{\s*"input_i"[\s\S]*?\}', result.stderr.decode())
    if not match:
        raise RuntimeError("FFmpeg did not return loudness measurements")
    return json.loads(match.group())


def normalize_loudness(ffmpeg: str, source: Path, destination: Path, target: float = -16.0, peak: float = -1.5) -> dict:
    measured = measure_loudness(ffmpeg, source, target, peak)
    filter_text = (
        f"loudnorm=I={target}:TP={peak}:LRA=11:"
        f"measured_I={measured['input_i']}:measured_TP={measured['input_tp']}:"
        f"measured_LRA={measured['input_lra']}:measured_thresh={measured['input_thresh']}:"
        f"offset={measured['target_offset']}:linear=true"
    )
    run_ffmpeg(ffmpeg, ["-i", str(source), "-af", filter_text, "-ar", str(SAMPLE_RATE), "-ac", "2", "-c:a", "pcm_s24le", str(destination)])
    return measure_loudness(ffmpeg, destination, target, peak)


async def synthesize_scene(scene: dict, voice: str, directory: Path, semaphore: asyncio.Semaphore) -> tuple[Path, dict]:
    scene_id = scene["id"]
    mp3 = directory / f"{scene_id}.mp3"
    metadata_path = directory / f"{scene_id}.source.json"
    signature = hashlib.sha256(json.dumps({"voice": voice, "text": scene["voiceover"], "rate": "+0%"}, sort_keys=True).encode()).hexdigest()
    if mp3.is_file() and metadata_path.is_file():
        metadata = json.loads(metadata_path.read_text())
        if metadata.get("signature") == signature:
            print(f"Using cached narration: {scene_id}", flush=True)
            return mp3, metadata
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    boundaries = []
    async with semaphore:
        for attempt in range(3):
            try:
                speech = edge_tts.Communicate(
                    scene["voiceover"], voice, rate="+0%", boundary="WordBoundary",
                    proxy=proxy, connect_timeout=15, receive_timeout=45,
                )
                boundaries = []
                with mp3.open("wb") as output:
                    async for chunk in speech.stream():
                        if chunk["type"] == "audio":
                            output.write(chunk["data"])
                        elif chunk["type"] == "WordBoundary":
                            boundaries.append({
                                "text": chunk["text"],
                                "start": chunk["offset"] / 10_000_000,
                                "duration": chunk["duration"] / 10_000_000,
                            })
                break
            except Exception as error:
                if attempt == 2:
                    raise RuntimeError(f"Speech generation failed for {scene_id}: {type(error).__name__}") from None
                await asyncio.sleep(1.5 * (attempt + 1))
    metadata = {"signature": signature, "voice": voice, "rate": "+0%", "text": scene["voiceover"], "word_boundaries": boundaries}
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"Synthesized narration: {scene_id}", flush=True)
    return mp3, metadata


async def synthesize_all(scenes: list[dict], voice: str, directory: Path) -> list:
    semaphore = asyncio.Semaphore(3)
    return await asyncio.gather(*(synthesize_scene(scene, voice, directory, semaphore) for scene in scenes))


def trim_silence(audio: np.ndarray) -> tuple[np.ndarray, float]:
    frame = round(0.010 * SAMPLE_RATE)
    peaks = np.array([np.max(np.abs(audio[i:i + frame])) for i in range(0, len(audio), frame)])
    active = np.flatnonzero(peaks > 10 ** (-46 / 20))
    if not len(active):
        raise ValueError("Narration contains no audible speech")
    start = max(0, int(active[0] * frame - 0.045 * SAMPLE_RATE))
    end = min(len(audio), int((active[-1] + 1) * frame + 0.100 * SAMPLE_RATE))
    return audio[start:end].copy(), start / SAMPLE_RATE


def tempo_fit(ffmpeg: str, audio: np.ndarray, speed: float, stem: Path) -> np.ndarray:
    source = stem.with_suffix(".trimmed.wav")
    target = stem.with_suffix(".timed.wav")
    write_pcm24(source, np.column_stack((audio, audio)))
    run_ffmpeg(ffmpeg, ["-i", str(source), "-af", f"atempo={speed:.8f}", "-ar", str(SAMPLE_RATE), "-ac", "1", "-c:a", "pcm_s24le", str(target)])
    return read_audio(ffmpeg, target)


def speech_tokens(text: str) -> list[str]:
    """Normalize the film's displayed numbers/model name to their spoken forms."""
    text = text.lower().replace("claude-4.5-sonnet", "claude sonnet four point five")
    numbers = {
        "58.55%": "fifty eight point five five percent",
        "95.77%": "ninety five point seven seven",
        "2026": "twenty twenty six", "570": "five hundred seventy",
        "252": "two hundred fifty two", "318": "three hundred eighteen",
        "40": "forty", "13": "thirteen", "10": "ten", "7": "seven",
        "9": "nine", "4": "four",
    }
    for digits, spoken in numbers.items():
        text = re.sub(r"(?<!\w)" + re.escape(digits) + r"(?!\w)", spoken, text)
    return re.findall(r"[a-z]+(?:'[a-z]+)?", text)


def align_captions(storyboard: dict, timeline: list[dict]) -> list[dict]:
    aligned = []
    for segment in timeline:
        cues = [cue for cue in storyboard["captions"] if segment["scene_start"] <= cue["start"] < segment["scene_end"]]
        spoken = []
        for word in segment["words"]:
            spoken.extend({"token": token, "start": word["start"], "end": word["end"]} for token in speech_tokens(word["text"]))
        caption_tokens = []
        spans = []
        for cue in cues:
            start = len(caption_tokens)
            caption_tokens.extend(speech_tokens(cue["en"]))
            spans.append((start, len(caption_tokens)))
        matcher = SequenceMatcher(None, caption_tokens, [word["token"] for word in spoken], autojunk=False)
        mapping = {}
        for block in matcher.get_matching_blocks():
            mapping.update({block.a + offset: block.b + offset for offset in range(block.size)})
        scene_cues = []
        for cue, (first, last) in zip(cues, spans):
            matched = [mapping[index] for index in range(first, last) if index in mapping]
            if len(matched) / max(last - first, 1) < 0.55:
                raise ValueError(f"Caption text does not align reliably in {segment['scene']}: {cue['en']}")
            start = max(segment["scene_start"], spoken[min(matched)]["start"] - 0.04)
            end = min(segment["scene_end"] - 0.02, spoken[max(matched)]["end"] + 0.16)
            scene_cues.append({**cue, "start": round(start, 3), "end": round(end, 3)})
        for index, cue in enumerate(scene_cues[:-1]):
            cue["end"] = round(min(cue["end"], scene_cues[index + 1]["start"] - 0.025), 3)
        for cue in scene_cues:
            if cue["end"] <= cue["start"]:
                raise ValueError(f"Caption has a non-positive duration: {cue['en']}")
        aligned.extend(scene_cues)
    return aligned


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--storyboard", type=Path, default=ROOT / "scripts/video_storyboard.json")
    parser.add_argument("--voice", default="en-US-AndrewMultilingualNeural")
    parser.add_argument("--ffmpeg", default=str(ROOT / "tmp/video-tools/ffmpeg"))
    parser.add_argument("--score", type=Path, default=ROOT / "tmp/video-audio/score.wav")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "tmp/video-audio")
    args = parser.parse_args()
    ffmpeg = shutil.which(args.ffmpeg)
    if not ffmpeg:
        parser.error("A complete FFmpeg binary is required; provide it with --ffmpeg")
    storyboard = json.loads(args.storyboard.read_text())
    scenes = storyboard["scenes"]
    directory = args.output_dir
    segments_dir = directory / "segments"
    segments_dir.mkdir(parents=True, exist_ok=True)
    clips = asyncio.run(synthesize_all(scenes, args.voice, segments_dir))
    narration = np.zeros((round(float(storyboard["duration"]) * SAMPLE_RATE), 2))
    timeline = []
    failures = []
    for scene, (mp3, metadata) in zip(scenes, clips):
        raw = read_audio(ffmpeg, mp3)
        audio, removed = trim_silence(raw)
        natural_duration = len(audio) / SAMPLE_RATE
        start = float(scene["start"]) + 0.45
        deadline = float(scene["end"]) - 0.30
        available = deadline - start
        speed = max(1.0, natural_duration / (available - 0.025))
        if speed > 1.12:
            failures.append({"scene": scene["id"], "duration": round(natural_duration, 3), "available": round(available, 3), "required_speed": round(speed, 3)})
            continue
        if speed > 1.0:
            audio = tempo_fit(ffmpeg, audio, speed, segments_dir / scene["id"])
        if len(audio) / SAMPLE_RATE > available:
            failures.append({"scene": scene["id"], "duration_after_tempo": len(audio) / SAMPLE_RATE, "available": available})
            continue
        # A short edge fade removes any residual crop discontinuity.
        fade = min(round(0.012 * SAMPLE_RATE), len(audio) // 2)
        audio[:fade] *= np.sin(np.linspace(0, np.pi / 2, fade)) ** 2
        audio[-fade:] *= np.cos(np.linspace(0, np.pi / 2, fade)) ** 2
        offset = round(start * SAMPLE_RATE)
        narration[offset:offset + len(audio)] = audio[:, None]
        words = []
        for word in metadata["word_boundaries"]:
            onset = start + (word["start"] - removed) / speed
            words.append({"text": word["text"], "start": round(max(start, onset), 3), "end": round(min(start + len(audio) / SAMPLE_RATE, onset + word["duration"] / speed), 3)})
        timeline.append({
            "scene": scene["id"], "scene_start": scene["start"], "scene_end": scene["end"],
            "start": start, "end": round(start + len(audio) / SAMPLE_RATE, 5),
            "natural_trimmed_duration": round(natural_duration, 5), "atempo": round(speed, 8),
            "trimmed_leading_seconds": removed, "voiceover": scene["voiceover"], "words": words,
        })
        print(f"Timed {scene['id']}: {start:.2f}–{start + len(audio) / SAMPLE_RATE:.2f}s, speed {speed:.3f}", flush=True)
    if failures:
        (directory / "timing-errors.json").write_text(json.dumps(failures, indent=2) + "\n")
        raise SystemExit("Narration exceeds scene limits; shorten these passages: " + json.dumps(failures))
    (directory / "timing-errors.json").unlink(missing_ok=True)

    aligned = align_captions(storyboard, timeline)
    (directory / "aligned-captions.json").write_text(json.dumps(aligned, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    raw_narration_path = directory / "narration-unmastered.wav"
    narration_path = directory / "narration.wav"
    write_pcm24(raw_narration_path, narration)
    narration_measurement = normalize_loudness(ffmpeg, raw_narration_path, narration_path, target=-17.0, peak=-2.0)
    narration = read_audio(ffmpeg, narration_path, 2)
    score = read_audio(ffmpeg, args.score, 2)
    if len(score) != len(narration):
        raise ValueError("Score and narration must have the same 90-second duration")

    active = np.zeros(len(score), dtype=bool)
    duck = np.ones(len(score))
    for segment in timeline:
        first = round(segment["start"] * SAMPLE_RATE)
        last = round(segment["end"] * SAMPLE_RATE)
        active[first:last] = True
        duck[first:last] = 0.0
        attack = min(first, round(0.18 * SAMPLE_RATE))
        release = min(len(duck) - last, round(0.70 * SAMPLE_RATE))
        ramp = 0.5 * (1 + np.cos(np.linspace(0, np.pi, attack)))
        duck[first - attack:first] = np.minimum(duck[first - attack:first], ramp)
        ramp = 0.5 * (1 - np.cos(np.linspace(0, np.pi, release)))
        duck[last:last + release] = np.minimum(duck[last:last + release], ramp)
    voice_rms = float(np.sqrt(np.mean(narration[active] ** 2)))
    music_rms = float(np.sqrt(np.mean(score[active] ** 2)))
    quiet_gain = voice_rms / music_rms * 10 ** (-12 / 20)
    open_gain = quiet_gain * 10 ** (5.5 / 20)
    gain = quiet_gain + (open_gain - quiet_gain) * duck
    mixed = narration + score * gain[:, None]
    peak = float(np.max(np.abs(mixed)))
    if peak >= 0.97:
        mixed *= 0.97 / peak
    premaster = directory / "mix-premaster.wav"
    master = directory / "master.wav"
    write_pcm24(premaster, mixed)
    # Reserve a little headroom for AAC reconstruction in the final MP4.
    master_measurement = normalize_loudness(ffmpeg, premaster, master, target=-16.0, peak=-1.8)
    metadata = {
        "duration": storyboard["duration"], "sample_rate": SAMPLE_RATE, "channels": 2,
        "voice": args.voice, "rate": "+0%", "timeline": timeline,
        "speech_music_rms_difference_db": 12.0,
        "music_gain_during_speech_db": round(float(20 * np.log10(quiet_gain)), 3),
        "music_gap_lift_db": 5.5, "duck_attack_seconds": 0.18, "duck_release_seconds": 0.70,
        "narration_loudness": narration_measurement, "master_loudness": master_measurement,
    }
    (directory / "narration-timing.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps({"master": str(master), "integrated_lufs": master_measurement["input_i"], "true_peak_dbfs": master_measurement["input_tp"], "music_gain_during_speech_db": metadata["music_gain_during_speech_db"]}, indent=2))


if __name__ == "__main__":
    main()
