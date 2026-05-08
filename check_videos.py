#!/usr/bin/env python3

import concurrent.futures
import json
import os
import subprocess
from pathlib import Path

from tqdm import tqdm

# ============================================
# CONFIG
# ============================================

ROOT_DIRECTORY = Path(".")

VIDEO_EXTENSIONS = {
    ".mp4",
    ".mkv",
    ".avi",
    ".mov",
    ".wmv",
    ".flv",
    ".webm",
    ".m4v",
    ".mpeg",
    ".mpg",
    ".ts",
    ".3gp",
}

MAX_WORKERS = os.cpu_count()

# How many frames to sample total
SAMPLED_FRAMES = 3

# ============================================


def is_video_file(path: Path) -> bool:
    return path.suffix.lower() in VIDEO_EXTENSIONS


def ffprobe_check(video_path: Path):
    """
    Extremely fast metadata/container validation.
    """

    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=codec_name,width,height",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        str(video_path),
    ]

    result = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
    )

    if result.returncode != 0:
        return False, "ffprobe failed"

    try:
        data = json.loads(result.stdout)
    except Exception:
        return False, "Invalid metadata"

    streams = data.get("streams", [])

    if not streams:
        return False, "No video stream"

    return True, None


def quick_decode_check(video_path: Path):
    """
    Decode only a VERY small sample of frames.

    This catches most broken/corrupt videos while remaining fast.
    """

    cmd = [
        "ffmpeg",
        "-v",
        "error",
        "-hwaccel",
        "auto",
        "-i",
        str(video_path),
        # only decode a few frames
        "-frames:v",
        str(SAMPLED_FRAMES),
        "-f",
        "null",
        "-",
    ]

    result = subprocess.run(
        cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True
    )

    if result.returncode != 0:
        return False, result.stderr.strip()

    return True, None


def validate_video(video_path: Path):
    errors = []

    ok, err = ffprobe_check(video_path)

    if not ok:
        errors.append(err)
        return str(video_path), errors

    ok, err = quick_decode_check(video_path)

    if not ok:
        errors.append(err)

    return str(video_path), errors


def find_videos(root_dir: Path):
    for path in root_dir.rglob("*"):
        if path.is_file() and is_video_file(path):
            yield path


def main():
    videos = list(find_videos(ROOT_DIRECTORY))

    if not videos:
        print("No video files found.")
        return

    print(f"Found {len(videos)} videos")
    print(f"Using {MAX_WORKERS} workers\n")

    invalid_videos = []

    # ProcessPool is faster for ffmpeg-heavy workloads
    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:

        results = executor.map(validate_video, videos)

        with tqdm(total=len(videos), desc="Checking", unit="video") as pbar:

            for video_path, errors in results:

                if errors:
                    invalid_videos.append((video_path, errors))

                pbar.update(1)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if not invalid_videos:
        print("All videos are valid.")
    else:
        print(f"Found {len(invalid_videos)} invalid videos:\n")

        for path, errors in invalid_videos:
            print(path)

            for err in errors:
                print(f"    - {err}")


if __name__ == "__main__":
    main()
