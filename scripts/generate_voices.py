#!/usr/bin/env python3
"""Generate broadcast-polished Snow Patrol character voices via fp16 zero-shot cloning in software-mansion/Reverb-TTS."""
import base64
import json
import subprocess
import sys
import time
from pathlib import Path

import soundfile as sf
from reverb_tts import TTS

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "assets" / "voices"
REF_DIR = OUT_DIR / "refs_v2"
OUT_DIR.mkdir(parents=True, exist_ok=True)

VOICES = {
    "maren": {
        "wav": REF_DIR / "hifi_92.wav",
        "ref_text": "and every habit that conduces to purity and rigour in intellectual matters,",
        "source": "HiFi-TTS Studio #92 (Broadcast Female)",
    },
    "gus": {
        "wav": REF_DIR / "hifi_6097.wav",
        "ref_text": "and would have caused you to be slain had I not pleaded for you and called his oath to mind?",
        "source": "HiFi-TTS Studio #6097 (Deep Baritone)",
    },
    "guest": {
        "wav": REF_DIR / "rav_angry_21_clean.wav",
        "ref_text": "Dogs are sitting by the door! Kids are talking by the door!",
        "source": "RAVDESS Studio #21 (Strong Angry)",
    },
}

LINES = [
    # Chief Maren — Base Camp Dispatch
    ("intro_0", "maren", "Copy, Snowcat One. Warm-up shift at Pine Cabin Driveway. Drop the blade and push that fresh powder outside the flags."),
    ("intro_1", "maren", "Summit Ski Plaza is up next, Snowcat One. Watch the lift tower in the center, and stay sharp on that black ice to the east."),
    ("intro_2", "maren", "Morning shift at Chalet Village. Guests are snowed in around the lodge, so take it easy around those parked cars for a clean driver bonus."),
    ("intro_3", "maren", "Storm warning on Pine Ridge Pass. Clear the entire switchback highway, and hit turbo boost to power through the deep drifts."),
    ("intro_4", "maren", "Emergency midnight dispatch, Snowcat One. The rescue chopper needs that summit helipad cleared right away. Good luck out there."),
    ("halfway", "maren", "Fifty percent clear. Clean corduroy lines out there, Snowcat One. Keep up that rhythm."),
    ("almost", "maren", "Eighty percent cleared. Follow the gold beacon on your snow radar to finish off the last drifts."),
    ("ice", "maren", "Heads up, Snowcat One. Slippery black ice on that sector. Feather your steering."),
    ("turbo", "maren", "Twin turbo engaged. Throw that powder, Snowcat One."),
    ("snowman", "maren", "Ha! Snowman down. The lodge kids are going to build an even bigger one tomorrow."),
    ("squall", "maren", "Heads up, heavy blizzard squall rolling over the ridge. Hold steady."),
    ("victory_gold", "maren", "Three-star gold run! That zone is absolute perfection, Snowcat One. Head back to base for hot cocoa."),
    ("victory_clear", "maren", "Copy that, shift complete. The zone is clear and ready for traffic. Great work out there."),
    ("fuel_pickup", "maren", "Turbo canister collected! Fuel cell topped off and ready to roar."),
    ("drift_buster", "maren", "Nice drift bust! You tore right through that avalanche mound."),
    ("rescue_chopper", "maren", "Helipad is spotless! Alpine Rescue One is cleared for final approach. Watch the skies, Snowcat One!"),
    ("horn_dog", "maren", "Haha, Barnaby the lodge husky loves that air horn!"),
    # Angry Lodge Guest — Channel 4
    ("car_hit_1", "guest", "Hey! Watch the paint! That is a brand new four by four!"),
    ("car_hit_2", "guest", "Whoa! Easy with that giant plow blade! You almost took off my mirror!"),
    # Gus — Snowcat Garage Chief
    ("upgrade_blade", "gus", "Wide-wing plow blade is bolted on tight. You will carve clean lanes twice as fast now, Snowcat One."),
    ("upgrade_engine", "gus", "Twin-turbo diesel is tuned up and purring. Even the heaviest avalanche drifts will not slow you down."),
    ("upgrade_tracks", "gus", "Heated ice-grip tracks are fitted and ready. Black ice is going to feel like dry tarmac under your treads."),
    ("upgrade_thrower", "gus", "Rotary powder thrower is online. Angle that blade and watch the snow fly clear over the ridge."),
    ("livery_paint", "gus", "Fresh coat of alpine paint! She is looking sharp enough for the summit postcard."),
]

def main():
    force = "--force" in sys.argv
    t0 = time.time()
    need_gen = [(k, v, t) for (k, v, t) in LINES if force or not (OUT_DIR / f"{k}.mp3").exists()]

    tts = None
    cloned = {}
    if need_gen:
        print(f"Loading software-mansion/Reverb-TTS (fp16) for {len(need_gen)} new lines...", flush=True)
        tts = TTS.from_pretrained("software-mansion/Reverb-TTS", variant="fp16")
        for vid in sorted({v for _, v, _ in need_gen}):
            cfg = VOICES[vid]
            cloned[vid] = tts.voice(str(cfg["wav"]), cfg["ref_text"], language="en")
            print(f"  Cloned [{vid}] <- {cfg['wav'].name}", flush=True)

        for key, vid, text in need_gen:
            ts = time.time()
            audio = tts.generate(text, cloned[vid], language="en")
            wav_path = OUT_DIR / f"{key}.wav"
            mp3_path = OUT_DIR / f"{key}.mp3"
            sf.write(str(wav_path), audio, tts.sample_rate)
            subprocess.run([
                "ffmpeg", "-y", "-loglevel", "error",
                "-i", str(wav_path),
                "-af", "highpass=f=70,silenceremove=start_periods=1:start_threshold=-48dB,areverse,silenceremove=start_periods=1:start_threshold=-48dB,areverse,loudnorm=I=-16:TP=-1.2:LRA=9",
                "-ac", "1", "-ar", "24000", "-b:a", "72k",
                str(mp3_path),
            ], check=True)
            wav_path.unlink(missing_ok=True)
            print(f"  [{key}] ({vid}) -> {mp3_path.stat().st_size:,} bytes ({time.time() - ts:.2f}s)", flush=True)

    manifest = {}
    for key, vid, text in LINES:
        mp3_bytes = (OUT_DIR / f"{key}.mp3").read_bytes()
        manifest[key] = {
            "voice": vid,
            "text": text,
            "b64": base64.b64encode(mp3_bytes).decode("ascii"),
            "bytes": len(mp3_bytes),
        }

    (OUT_DIR / "voices_bundle.json").write_text(json.dumps(manifest))
    total_kb = sum(v["bytes"] for v in manifest.values()) / 1024
    print(f"Bundled {len(manifest)} fp16 studio lines ({total_kb:.1f} KB) in {time.time() - t0:.1f}s", flush=True)

if __name__ == "__main__":
    main()
