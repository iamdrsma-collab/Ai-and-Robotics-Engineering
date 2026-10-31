"""
Cinematic 720p HD Lecture Video Builder (1280x720, 16:9, 30fps, Mono Studio Audio)
Supports frame-exact FADE and MORPH transitions, stationary institutional footer,
waveform-aligned scene boundaries, and synchronized SRT + ASS captions.
"""

import json
import math
import os
import re
import subprocess
import time
import wave
import imageio_ffmpeg
import numpy as np
from PIL import Image

FPS = 30
W, H = 1280, 720
FOOTER_Y = 676  # y = 676..720 remains rock-steady institutional footer during MORPH


def load_wav_mono(path: str) -> tuple[int, np.ndarray]:
    with wave.open(path, "rb") as w:
        sr = w.getframerate()
        ch = w.getnchannels()
        raw = w.readframes(w.getnframes())
        arr = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        if ch > 1:
            arr = arr.reshape(-1, ch).mean(axis=1)
    return sr, arr


def save_wav_mono(path: str, sr: int, data: np.ndarray) -> None:
    clipped = np.clip(data, -0.99, 0.99)
    pcm = (clipped * 32767.0).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def find_silence_splits(sr: int, data: np.ndarray, texts: list[str]) -> list[float]:
    """Find exact silence-valley timestamps between multi-scene narration paragraphs."""
    dur = len(data) / sr
    if len(texts) <= 1:
        return [0.0, dur]

    win = int(sr * 0.02)
    n_frames = len(data) // win
    rms = np.sqrt(np.mean(data[: n_frames * win].reshape(n_frames, win) ** 2, axis=1))
    smooth_rms = np.convolve(rms, np.ones(11) / 11.0, mode="same")

    total_chars = sum(len(t) for t in texts)
    splits = [0.0]
    cum = 0
    for t in texts[:-1]:
        cum += len(t)
        expected = (cum / total_chars) * dur
        span = max(1.5, dur * 0.12)
        lo = max(8, int((expected - span) / 0.02))
        hi = min(n_frames - 8, int((expected + span) / 0.02))
        idxs = np.arange(lo, hi)
        penalty = 0.015 * np.abs(idxs * 0.02 - expected) / span
        best = lo + int(np.argmin(smooth_rms[lo:hi] + penalty))
        splits.append(best * 0.02)
    splits.append(dur)
    return splits


def split_into_caption_chunks(narration: str, max_chars: int = 82) -> list[str]:
    """Split scene narration into clean, readable subtitle sentences/clauses."""
    raw_sents = [s.strip() for s in re.split(r"(?<=[.?!])\s+", narration.strip()) if s.strip()]
    chunks = []
    for sent in raw_sents:
        if len(sent) <= max_chars:
            chunks.append(sent)
        else:
            # Split long sentence near middle comma or space
            parts = [p.strip() for p in re.split(r"(?<=,)\s+", sent) if p.strip()]
            cur = ""
            for p in parts:
                if not cur:
                    cur = p
                elif len(cur) + 1 + len(p) <= max_chars:
                    cur = f"{cur} {p}"
                else:
                    chunks.append(cur)
                    cur = p
            if cur:
                # If a single clause is still > max_chars, wrap by words
                while len(cur) > max_chars:
                    cut = cur.rfind(" ", 0, max_chars)
                    if cut <= 0:
                        cut = max_chars
                    chunks.append(cur[:cut].strip())
                    cur = cur[cut:].strip()
                if cur:
                    chunks.append(cur)
    return chunks


def fmt_srt_time(sec: float) -> str:
    ms = int(round(max(0.0, sec) * 1000))
    h, rem = divmod(ms, 3600000)
    m, rem = divmod(rem, 60000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def fmt_ass_time(sec: float) -> str:
    cs = int(round(max(0.0, sec) * 100))
    h, rem = divmod(cs, 360000)
    m, rem = divmod(rem, 6000)
    s, cs = divmod(rem, 100)
    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"


def write_subtitles(captions: list[tuple[float, float, str]], srt_path: str, ass_path: str) -> None:
    with open(srt_path, "w", encoding="utf-8") as f:
        for idx, (t0, t1, txt) in enumerate(captions, 1):
            # Clean spoken 'A I' -> 'AI' and 'P E A S' -> 'PEAS' for crisp visual reading
            disp = (
                txt.replace("A I", "AI")
                .replace("P E A S", "PEAS")
                .replace("G P S", "GPS")
                .replace("dot py", ".py")
            )
            f.write(f"{idx}\n{fmt_srt_time(t0)} --> {fmt_srt_time(t1)}\n{disp}\n\n")

    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: LectureCap,DejaVu Sans,21,&H00F8FAFC,&H00D4AF37,&H28060913,&HBF060A16,0,0,0,0,100,100,0.2,0,3,8,0,2,90,90,54,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header)
        for t0, t1, txt in captions:
            disp = (
                txt.replace("A I", "AI")
                .replace("P E A S", "PEAS")
                .replace("G P S", "GPS")
                .replace("dot py", ".py")
            )
            f.write(f"Dialogue: 0,{fmt_ass_time(t0)},{fmt_ass_time(t1)},LectureCap,,0,0,0,,{disp}\n")


def zoom_content_region(arr: np.ndarray, scale: float) -> np.ndarray:
    """Scale only the slide body above FOOTER_Y so institutional footer stays 100% locked."""
    if abs(scale - 1.0) < 1e-4:
        return arr
    body = Image.fromarray(arr[:FOOTER_Y, :, :])
    bw, bh = W, FOOTER_Y
    nw, nh = int(round(bw * scale)), int(round(bh * scale))
    resized = body.resize((nw, nh), Image.Resampling.BILINEAR)

    if scale >= 1.0:
        left = (nw - bw) // 2
        top = (nh - bh) // 2
        cropped = np.asarray(resized.crop((left, top, left + bw, top + bh)), dtype=np.uint8)
    else:
        canvas = Image.new("RGB", (bw, bh), (6, 9, 19))
        canvas.paste(resized, ((bw - nw) // 2, (bh - nh) // 2))
        cropped = np.asarray(canvas, dtype=np.uint8)

    out = arr.copy()
    out[:FOOTER_Y, :, :] = cropped
    return out


def render_transition_frame(
    slide_a: np.ndarray,
    slide_b: np.ndarray,
    mode: str,
    progress: float,
    locked_diagram: bool = False,
) -> bytes:
    """Render smooth S-curve FADE or spatial-optical MORPH frame (keeping footer stationary)."""
    alpha = 0.5 - 0.5 * math.cos(math.pi * progress)  # Smooth cosine S-curve [0..1]

    if mode == "FADE":
        blended = (slide_a.astype(np.float32) * (1.0 - alpha) + slide_b.astype(np.float32) * alpha)
        out = np.clip(blended, 0, 255).astype(np.uint8)
        out[FOOTER_Y:, :, :] = slide_b[FOOTER_Y:, :, :]
        return out.tobytes()

    # MORPH mode
    if locked_diagram:
        # Seamless state-morph for consecutive progressive diagrams / quiz reveal:
        # Subtle horizontal golden energy wave + smooth S-curve state interpolation
        blended = slide_a.astype(np.float32) * (1.0 - alpha) + slide_b.astype(np.float32) * alpha
        wave_x = int(W * progress)
        xs = np.arange(W, dtype=np.float32)[None, :, None]
        glow = np.exp(-((xs - wave_x) ** 2) / (2 * (75.0 ** 2))) * math.sin(math.pi * progress) * 18.0
        gold_tint = np.array([1.0, 0.84, 0.32], dtype=np.float32)[None, None, :]
        blended[:FOOTER_Y] = blended[:FOOTER_Y] + glow * gold_tint
        out = np.clip(blended, 0, 255).astype(np.uint8)
        out[FOOTER_Y:, :, :] = slide_b[FOOTER_Y:, :, :]
        return out.tobytes()

    # Geometric convergence MORPH between distinct slides (footer stays locked!)
    scale_a = 1.0 + 0.032 * alpha
    scale_b = 0.968 + 0.032 * alpha
    warped_a = zoom_content_region(slide_a, scale_a).astype(np.float32)
    warped_b = zoom_content_region(slide_b, scale_b).astype(np.float32)
    blended = warped_a * (1.0 - alpha) + warped_b * alpha
    out = np.clip(blended, 0, 255).astype(np.uint8)
    out[FOOTER_Y:, :, :] = slide_b[FOOTER_Y:, :, :]
    return out.tobytes()


def build_module_video(
    manifest_path: str,
    audio_dir: str,
    slide_dir: str,
    out_mp4: str,
    out_srt: str,
) -> dict:
    t_start_wall = time.time()
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    sr = 44100
    lead_in_sec = 0.90
    inter_clip_sec = 0.80
    lead_out_sec = 1.40

    master_audio_parts = [np.zeros(int(sr * lead_in_sec), dtype=np.float32)]
    cursor_sec = lead_in_sec

    scenes_timeline = []  # list of dicts: slide_idx, start_sec, end_sec, transition, narration
    captions = []

    slide_counter = 0
    for c_idx, clip in enumerate(manifest["clips"]):
        cid = clip["clip_id"]
        wav_path = os.path.join(audio_dir, f"{cid}.wav")
        c_sr, c_data = load_wav_mono(wav_path)
        assert c_sr == sr, f"Unexpected sample rate {c_sr}"

        texts = [s["narration"] for s in clip["scenes"]]
        local_splits = find_silence_splits(sr, c_data, texts)

        for s_idx, scene in enumerate(clip["scenes"]):
            slide_counter += 1
            s_local_0 = local_splits[s_idx]
            s_local_1 = local_splits[s_idx + 1]

            abs_0 = cursor_sec + s_local_0
            abs_1 = cursor_sec + s_local_1

            # Include lead-in on very first slide, inter-clip pause on last scene of clip
            seg_start = 0.0 if (c_idx == 0 and s_idx == 0) else abs_0
            if s_idx == len(clip["scenes"]) - 1:
                pause_pad = lead_out_sec if c_idx == len(manifest["clips"]) - 1 else inter_clip_sec
                seg_end = abs_1 + pause_pad
            else:
                seg_end = abs_1

            scenes_timeline.append({
                "slide_num": slide_counter,
                "slide_path": os.path.join(slide_dir, f"slide_{slide_counter:02d}.png"),
                "layout": scene["layout"],
                "transition": scene["transition"],
                "seg_start": seg_start,
                "seg_end": seg_end,
                "speech_start": abs_0,
                "speech_end": abs_1,
                "narration": scene["narration"],
            })

            # Align sentence-level captions inside [s_local_0, s_local_1]
            c_chunks = split_into_caption_chunks(scene["narration"])
            sub_slice = c_data[int(s_local_0 * sr) : int(s_local_1 * sr)]
            chunk_splits = find_silence_splits(sr, sub_slice, c_chunks)
            for k, ch_txt in enumerate(c_chunks):
                ct0 = abs_0 + chunk_splits[k]
                ct1 = abs_0 + chunk_splits[k + 1] - 0.04
                if ct1 > ct0 + 0.25:
                    captions.append((ct0, ct1, ch_txt))

        master_audio_parts.append(c_data)
        pause = lead_out_sec if c_idx == len(manifest["clips"]) - 1 else inter_clip_sec
        master_audio_parts.append(np.zeros(int(sr * pause), dtype=np.float32))
        cursor_sec += (len(c_data) / sr) + pause

    full_audio = np.concatenate(master_audio_parts)
    # Peak-safe gentle studio normalization (-1.5 dBFS peak ceiling)
    peak = float(np.max(np.abs(full_audio)))
    if peak > 1e-5:
        full_audio = full_audio * (0.84 / peak)

    os.makedirs(".cache/build_video", exist_ok=True)
    master_wav = ".cache/build_video/master_mono.wav"
    ass_path = ".cache/build_video/captions.ass"
    save_wav_mono(master_wav, sr, full_audio)

    os.makedirs(os.path.dirname(out_mp4), exist_ok=True)
    write_subtitles(captions, out_srt, ass_path)

    # Load all 24 slide images into RGB uint8 arrays
    slide_arrays = []
    for st in scenes_timeline:
        im = Image.open(st["slide_path"]).convert("RGB")
        assert im.size == (W, H)
        slide_arrays.append(np.asarray(im, dtype=np.uint8))

    total_duration = len(full_audio) / sr
    total_frames = int(round(total_duration * FPS))
    boundaries = [int(round(st["seg_end"] * FPS)) for st in scenes_timeline[:-1]]
    half_tr = 14  # 28 frames (~0.93s) transition centered on each scene boundary

    # Pre-build frame plan: either ('hold', slide_idx, count) or ('trans', i, mode, locked, n_frames)
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    log_path = ".cache/build_video/ffmpeg.log"
    cmd = [
        ffmpeg_exe, "-y",
        "-loglevel", "warning",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-pix_fmt", "rgb24",
        "-s", f"{W}x{H}",
        "-r", str(FPS),
        "-i", "-",
        "-i", master_wav,
        "-vf", f"ass={ass_path}",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "21",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-ac", "1",
        "-ar", "44100",
        "-b:a", "96k",
        "-movflags", "+faststart",
        "-shortest",
        out_mp4,
    ]

    with open(log_path, "w", encoding="utf-8") as log_f:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=log_f)

        # Opening fade-from-black on Slide 1 (first 20 frames)
        black_arr = np.zeros_like(slide_arrays[0])
        black_arr[FOOTER_Y:, :, :] = slide_arrays[0][FOOTER_Y:, :, :]

        slide_bytes = [arr.tobytes() for arr in slide_arrays]

        written = 0
        n_slides = len(scenes_timeline)
        for i in range(n_slides):
            start_f = 0 if i == 0 else (boundaries[i - 1] + half_tr)
            end_f = total_frames if i == n_slides - 1 else (boundaries[i] - half_tr)

            if i == 0:
                intro_fade = min(20, end_f - start_f)
                for k in range(intro_fade):
                    p = (k + 1) / intro_fade
                    proc.stdin.write(render_transition_frame(black_arr, slide_arrays[0], "FADE", p))
                    written += 1
                start_f += intro_fade

            hold_count = max(0, end_f - start_f)
            raw_b = slide_bytes[i]
            for _ in range(hold_count):
                proc.stdin.write(raw_b)
                written += 1

            if i < n_slides - 1:
                next_mode = scenes_timeline[i + 1]["transition"]
                lay_a = scenes_timeline[i]["layout"]
                lay_b = scenes_timeline[i + 1]["layout"]
                locked = (
                    (lay_a.startswith("agent_loop") and lay_b.startswith("agent_loop"))
                    or (lay_a == "quiz_questions" and lay_b == "quiz_answers")
                )
                tr_len = 2 * half_tr
                for k in range(tr_len):
                    p = (k + 1) / (tr_len + 1)
                    frame_b = render_transition_frame(slide_arrays[i], slide_arrays[i + 1], next_mode, p, locked)
                    proc.stdin.write(frame_b)
                    written += 1

        proc.stdin.close()
        ret = proc.wait()

    if ret != 0:
        with open(log_path, "r", encoding="utf-8", errors="replace") as lf:
            stderr_out = lf.read()
        raise RuntimeError(f"FFmpeg failed ({ret}):\n{stderr_out[-1500:]}")

    elapsed = time.time() - t_start_wall
    size_mb = os.path.getsize(out_mp4) / (1024 * 1024)
    return {
        "mp4_path": out_mp4,
        "srt_path": out_srt,
        "duration_sec": round(total_duration, 2),
        "frames_written": written,
        "size_mb": round(size_mb, 2),
        "elapsed_sec": round(elapsed, 2),
        "captions_count": len(captions),
    }


if __name__ == "__main__":
    stats = build_module_video(
        manifest_path="courses/AI.101/Module_01_Foundations_and_Intelligent_Agents/lecture_manifest.json",
        audio_dir=".cache/audio/ai101_m01",
        slide_dir=".cache/slides/ai101_m01",
        out_mp4="courses/AI.101/Module_01_Foundations_and_Intelligent_Agents/AI.101_Module_01_Foundations_of_AI.mp4",
        out_srt="courses/AI.101/Module_01_Foundations_and_Intelligent_Agents/AI.101_Module_01_Foundations_of_AI.srt",
    )
    print("VIDEO BUILD COMPLETE:", json.dumps(stats, indent=2))
