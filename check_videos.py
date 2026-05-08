#!/usr/bin/env python3
## This code is AI generated, actually (almost) worked on first try!

import concurrent.futures
import json
import subprocess
from pathlib import Path

from tqdm import tqdm

# ============================================
# CONFIG
# ============================================

# Change this if you want a different directory
ROOT_DIRECTORY = Path(".")  # current directory

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

MAX_WORKERS = 8  # os.cpu_count()

# Black screen detection settings
BLACK_THRESHOLD = 0.98
BLACK_MIN_DURATION = 5

# ============================================


def is_video_file(path: Path) -> bool:
    return path.suffix.lower() in VIDEO_EXTENSIONS


def ffprobe_streams(video_path: Path):
    """
    Verify that ffprobe can read the video metadata/streams.
    """
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_streams",
        "-show_format",
        "-of",
        "json",
        str(video_path),
    ]

    result = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    if result.returncode != 0:
        return False, f"ffprobe failed: {result.stderr.strip()}"

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return False, "Invalid ffprobe JSON output"

    streams = data.get("streams", [])
    video_streams = [s for s in streams if s.get("codec_type") == "video"]

    if not video_streams:
        return False, "No video stream found"

    return True, None


def ffmpeg_decode_check(video_path: Path):
    """
    Fully decode the video and fail on corruption/errors.
    """
    cmd = ["ffmpeg", "-v", "error", "-xerror", "-i", str(video_path), "-f", "null", "-"]

    result = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    if result.returncode != 0:
        return False, result.stderr.strip()

    return True, None


def blackscreen_check(video_path: Path):
    """
    Detect long black sections using ffmpeg blackdetect.
    """
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-i",
        str(video_path),
        "-vf",
        f"blackdetect=d={BLACK_MIN_DURATION}:pic_th={BLACK_THRESHOLD}",
        "-an",
        "-f",
        "null",
        "-",
    ]

    result = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    stderr = result.stderr.lower()

    if "black_start" in stderr:
        return False, "Contains long black screen"

    return True, None


def validate_video(video_path: Path):
    errors = []

    ok, err = ffprobe_streams(video_path)
    if not ok:
        errors.append(err)
        return video_path, errors

    ok, err = ffmpeg_decode_check(video_path)
    if not ok:
        errors.append(err)

    ok, err = blackscreen_check(video_path)
    if not ok:
        errors.append(err)

    return video_path, errors


def find_videos(root_dir: Path):
    for path in root_dir.rglob("*"):
        if path.is_file() and is_video_file(path):
            yield path


def main():
    videos = list(find_videos(ROOT_DIRECTORY))

    if not videos:
        print("No video files found.")
        return

    print(f"Found {len(videos)} video files")

    invalid_videos = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

        futures = [executor.submit(validate_video, video) for video in videos]

        with tqdm(total=len(futures), desc="Checking videos") as pbar:
            for future in concurrent.futures.as_completed(futures):
                video_path, errors = future.result()

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
