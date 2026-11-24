#!/usr/bin/env python3
"""Generate deeply expressive 48 kHz Snow Patrol character voices via FixedSeed/Robin."""
import base64
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import soundfile as sf
import torch
from huggingface_hub import snapshot_download
from robin import pieces
from robin.pipeline import Robin

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "assets" / "voices"
ANCHOR_DIR = OUT_DIR / "refs_robin"
OUT_DIR.mkdir(parents=True, exist_ok=True)
ANCHOR_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATTERNS = [
    "config.json",
    "tokenizer.json",
    "robin_v1.safetensors",
    "robin_vae.safetensors",
    "speech_tokenizer_v3_25hz.onnx",
]

# Character anchor definitions: each character gets a dedicated 48 kHz studio anchor
# so voice identity stays rock-solid across all 24 lines while emotion adapts per line.
CHARACTERS = {
    "maren": {
        "base_voice": (
            "a warm, confident woman in her late thirties with a clear, crisp mezzo-soprano voice, "
            "seasoned mountain search-and-rescue radio dispatcher, natural close studio microphone"
        ),
        "anchor_text": (
            "Copy that, Snowcat One. Visibility is holding steady over the summit ridge, "
            "so drop your blade and take it nice and smooth out there."
        ),
        "anchor_seed": 42,
    },
    "gus": {
        "base_voice": (
            "a warm, gravelly, deep baritone man in his mid-fifties with a weathered, slightly raspy voice "
            "like a friendly veteran mountain diesel mechanic, hearty and proud, clean close studio microphone"
        ),
        "anchor_text": (
            "She is bolted up tight and purring like a mountain lion. "
            "You drop that steel blade into the powder and nothing on this ridge is gonna slow you down."
        ),
        "anchor_seed": 107,
    },
    "guest": {
        "base_voice": (
            "an indignant, high-strung man in his mid-thirties with a sharp, frantic, exasperated voice, "
            "panicked and outraged ski-resort guest yelling about his luxury four by four, close studio microphone"
        ),
        "anchor_text": (
            "[shouting] Hey! Are you kidding me right now?! "
            "Watch where you are swinging that giant steel plow blade!"
        ),
        "anchor_seed": 211,
    },
}

# (key, character, emotion_cue, spoken_text_with_tags, seed)
LINES = [
    # --- Chief Maren — Base Camp Dispatch ---
    (
        "intro_0", "maren",
        "warm, welcoming, calm morning dispatch tone, gentle reassuring smile in her voice",
        "Copy, Snowcat One. Warm-up shift at Pine Cabin Driveway. Drop the blade and push that fresh powder outside the flags.",
        1001,
    ),
    (
        "intro_1", "maren",
        "steady, focused, alert alpine dispatch guidance with crisp clear pronunciation",
        "Summit Ski Plaza is up next, Snowcat One. Watch the lift tower in the center, and stay sharp on that black ice to the east.",
        1102,
    ),
    (
        "intro_2", "maren",
        "friendly, bright morning energy with a hint of amused caution, crisp clear pronunciation",
        "Morning shift at Shallay Village. Guests are snowed in around the lodge, so take it easy around those parked cars for a clean driver bonus.",
        1108,
    ),
    (
        "intro_3", "maren",
        "urgent, braced, intense storm-warning dispatch, serious and energizing",
        "Storm warning on Pine Ridge Pass! Clear the entire switchback highway, and hit turbo boost to power through the deep drifts.",
        1004,
    ),
    (
        "intro_4", "maren",
        "tense, urgent midnight search-and-rescue command, heartfelt sincerity on the closing words",
        "Red alert, Snowcat One. Emergency midnight dispatch. The rescue chopper needs that summit helipad cleared right away. Good luck out there.",
        1109,
    ),
    (
        "halfway", "maren",
        "warm, encouraging, genuinely pleased with steady rhythm",
        "Fifty percent clear! Clean corduroy lines out there, Snowcat One. Keep up that rhythm.",
        1006,
    ),
    (
        "almost", "maren",
        "upbeat, motivated, rallying for the final stretch",
        "Eighty percent cleared! Follow the gold beacon on your snow radar to finish off the last drifts.",
        1007,
    ),
    (
        "ice", "maren",
        "sharp, quick, protective safety alert",
        "Heads up, Snowcat One! Slippery black ice on that sector. Feather your steering.",
        1008,
    ),
    (
        "turbo", "maren",
        "thrilled, hyped, grinning with adrenaline",
        "Twin turbo engaged! Throw that powder, Snowcat One!",
        1009,
    ),
    (
        "snowman", "maren",
        "playful, genuinely amused, chuckling warmly",
        "[laughs] Snowman down! The lodge kids are going to build an even bigger one tomorrow.",
        1010,
    ),
    (
        "squall", "maren",
        "bracing, firm, urgent severe-weather warning",
        "Heads up, heavy blizzard squall rolling over the ridge! Hold steady!",
        1011,
    ),
    (
        "victory_gold", "maren",
        "joyful, beaming, proud celebration with warm cozy charm",
        "Three-star gold run! That zone is absolute perfection, Snowcat One. Head back to base for hot cocoa!",
        1012,
    ),
    (
        "victory_clear", "maren",
        "warm, relieved, proud mission-accomplished tone",
        "Copy that, shift complete. The zone is clear and ready for traffic. Great work out there.",
        1013,
    ),
    (
        "fuel_pickup", "maren",
        "crisp, upbeat, energetic boost callout",
        "Turbo canister collected! Fuel cell topped off and ready to roar.",
        1014,
    ),
    (
        "drift_buster", "maren",
        "impressed, excited, cheering over the radio",
        "Nice drift bust! You tore right through that avalanche mound!",
        1015,
    ),
    (
        "rescue_chopper", "maren",
        "triumphant, deeply relieved, soaring rescue-mission finale energy",
        "Helipad is spotless! Alpine Rescue One is cleared for final approach. Watch the skies, Snowcat One!",
        1016,
    ),
    (
        "horn_dog", "maren",
        "delighted, bursting with warm affection and genuine laughter",
        "[laughs] Barnaby the lodge husky loves that air horn!",
        1017,
    ),

    # --- Outraged SUV Owner — Channel 4 Lodge Guest ---
    (
        "car_hit_1", "guest",
        "furious, panicked shouting in utter disbelief, clear crisp outraged bursts",
        "[shouting] Hey! Watch the paint! That is a brand new four by four!",
        2101,
    ),
    (
        "car_hit_2", "guest",
        "frantic, exasperated yelling in shock, terrified for his luxury car",
        "[shouting] Whoa! Easy with that giant plow blade! You almost took off my mirror!",
        2002,
    ),

    # --- Gus — Snowcat Garage Chief ---
    (
        "upgrade_blade", "gus",
        "proud veteran craftsman satisfaction, warm confident grin",
        "Wide-wing plow blade is bolted on tight. You will carve clean lanes twice as fast now, Snowcat One.",
        3001,
    ),
    (
        "upgrade_engine", "gus",
        "gleeful old-school gearhead pride, admiring a tuned diesel engine",
        "Twin-turbo diesel is tuned up and purring. Even the heaviest avalanche drifts will not slow you down.",
        3002,
    ),
    (
        "upgrade_tracks", "gus",
        "reassuring, seasoned confidence, gravelly warmth",
        "Heated ice-grip tracks are fitted and ready. Black ice is going to feel like dry tarmac under your treads.",
        3003,
    ),
    (
        "upgrade_thrower", "gus",
        "enthusiastic, rugged excitement, proud of his custom build",
        "Rotary powder thrower is online! Angle that blade and watch the snow fly clear over the ridge.",
        3004,
    ),
    (
        "livery_paint", "gus",
        "hearty amused chuckle, admiring a shiny fresh paint job",
        "[laughs] Fresh coat of alpine paint! She is looking sharp enough for the summit postcard.",
        3005,
    ),
]


def clean_subtitle(text: str) -> str:
    """Remove inline Robin acting tags and restore clean spelling for HUD subtitles."""
    cleaned = re.sub(r"\[[^\]]+\]\s*", "", text).strip()
    return cleaned.replace("Shallay", "Chalet")


def resolve_model_dir() -> str:
    try:
        return snapshot_download("FixedSeed/Robin", allow_patterns=MODEL_PATTERNS, local_files_only=True)
    except Exception:
        return snapshot_download("FixedSeed/Robin", allow_patterns=MODEL_PATTERNS)


def ensure_speech_tokenizer_safe(robin: Robin):
    """Load SpeechTokenizer on MPS if supported, falling back to CPU cleanly if needed."""
    from robin.speech import SpeechTokenizer
    onnx_path = robin.weights_file.parent / "speech_tokenizer_v3_25hz.onnx"
    try:
        robin._speech = SpeechTokenizer(onnx_path, robin.device)
        # Quick smoke test on 0.5s silence
        _ = robin._speech(torch.zeros(24000, dtype=torch.float32).numpy(), 48000)
        print(f"  SpeechTokenizer active on {robin.device}", flush=True)
    except Exception as exc:
        print(f"  SpeechTokenizer falling back to cpu ({exc})", flush=True)
        robin._speech = SpeechTokenizer(onnx_path, "cpu")


def main():
    force = "--force" in sys.argv
    only_keys = {a for a in sys.argv[1:] if not a.startswith("-")}
    t0 = time.time()

    need_gen = [
        item for item in LINES
        if (only_keys and item[0] in only_keys)
        or (not only_keys and (force or not (OUT_DIR / f"{item[0]}.mp3").exists()))
    ]

    if need_gen:
        model_dir = resolve_model_dir()
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        dtype = torch.bfloat16 if device != "cpu" else torch.float32
        print(f"Loading FixedSeed/Robin (48 kHz) on {device} ({dtype}) for {len(need_gen)} lines...", flush=True)
        robin = Robin.from_pretrained(model_dir, device=device, dtype=dtype)
        ensure_speech_tokenizer_safe(robin)

        # Ensure every needed character has a 48 kHz Robin anchor clip for rock-solid identity
        anchors = {}
        for vid in sorted({v for _, v, _, _, _ in need_gen}):
            cfg = CHARACTERS[vid]
            anchor_wav_path = ANCHOR_DIR / f"{vid}_anchor.wav"
            if not anchor_wav_path.exists():
                print(f"  Generating 48 kHz anchor for [{vid}]...", flush=True)
                awav = pieces.read(
                    robin,
                    cfg["anchor_text"],
                    voice=cfg["base_voice"],
                    lang="en",
                    seed=cfg["anchor_seed"],
                    cfg=3.0,
                    retries=2,
                )
                sf.write(str(anchor_wav_path), awav, pieces.RATE, subtype="PCM_24")
            awav, arate = sf.read(str(anchor_wav_path), dtype="float32", always_2d=True)
            anchors[vid] = (awav.mean(1), arate, cfg["anchor_text"])
            print(f"  Anchor ready [{vid}] <- {anchor_wav_path.name} ({len(awav)/arate:.2f}s @ {arate}Hz)", flush=True)

        for key, vid, emotion, spoken_text, seed in need_gen:
            ts = time.time()
            cfg = CHARACTERS[vid]
            ref_wav, ref_rate, ref_text = anchors[vid]
            voice_prompt = f"{cfg['base_voice']}; delivery: {emotion}"
            audio = pieces.read(
                robin,
                spoken_text,
                voice=voice_prompt,
                reference=ref_wav,
                reference_rate=ref_rate,
                reference_text=ref_text,
                lang="en",
                seed=seed,
                cfg=2.5,
                retries=2,
            )
            wav_path = OUT_DIR / f"{key}.wav"
            mp3_path = OUT_DIR / f"{key}.mp3"
            sf.write(str(wav_path), audio, pieces.RATE, subtype="PCM_24")
            subprocess.run([
                "ffmpeg", "-y", "-loglevel", "error",
                "-i", str(wav_path),
                "-af", "highpass=f=65,loudnorm=I=-16:TP=-1.2:LRA=9",
                "-ac", "1", "-ar", "48000", "-b:a", "80k",
                str(mp3_path),
            ], check=True)
            wav_path.unlink(missing_ok=True)
            dur = len(audio) / pieces.RATE
            print(
                f"  [{key}] ({vid}) {dur:.2f}s -> {mp3_path.stat().st_size:,} bytes ({time.time() - ts:.1f}s)",
                flush=True,
            )

    manifest = {}
    for key, vid, _emotion, spoken_text, _seed in LINES:
        mp3_bytes = (OUT_DIR / f"{key}.mp3").read_bytes()
        manifest[key] = {
            "voice": vid,
            "text": clean_subtitle(spoken_text),
            "b64": base64.b64encode(mp3_bytes).decode("ascii"),
            "bytes": len(mp3_bytes),
        }

    (OUT_DIR / "voices_bundle.json").write_text(json.dumps(manifest))
    total_kb = sum(v["bytes"] for v in manifest.values()) / 1024
    print(f"Bundled {len(manifest)} FixedSeed/Robin 48kHz lines ({total_kb:.1f} KB) in {time.time() - t0:.1f}s", flush=True)


if __name__ == "__main__":
    main()
