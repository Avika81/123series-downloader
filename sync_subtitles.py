from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import ffsubsync
import os
import glob
from persist_cache.persist_cache import cache


def sync_all_series(executor=None):
    for base_path in glob.glob(str(Path(__file__).parent / "series" / "*" / "*")):
        sync_all(base_path=base_path, executor=executor)


def sync_one(subtitles_path, video_path):
    try:
        sync_subtitles(
            video_path=video_path,
            subtitles_path=subtitles_path,
        )
    except ValueError as e:
        if (
            e.args[0]
            == "Unable to detect speech. Perhaps try specifying a different stream / track, or a different vad."
        ):
            print(f"Error with video {video_path}. Removing it.")
            os.remove(video_path)
        else:
            raise


def sync_all(base_path=str(Path(__file__).parent / "movies"), executor=None):
    files = os.listdir(base_path)
    for video_file in files:
        if video_file.endswith(".mp4"):
            subtitles_file = video_file.replace(".mp4", ".vtt")
            video_path = os.path.join(base_path, video_file)
            subtitles_path = os.path.join(base_path, subtitles_file)
            if subtitles_file in files:
                f = lambda: sync_one(
                    subtitles_path=subtitles_path, video_path=video_path
                )
                if executor:
                    executor.submit(f)
                else:
                    f()


@cache
def sync_subtitles(subtitles_path, video_path):
    print(f"Synchronizing: {subtitles_path}")
    args = ffsubsync.ffsubsync.make_parser().parse_args(
        args=["-i", subtitles_path, "--overwrite-input", video_path]
    )
    ffsubsync.ffsubsync.run(
        args,
    )

    return subtitles_path


if __name__ == "__main__":
    executor = ThreadPoolExecutor(max_workers=16)
    sync_all(executor=executor)
    sync_all_series(executor=executor)
    executor.shutdown(wait=True)
    print("Done, your subtitle are snchronized and perfect (I hope) :)")
