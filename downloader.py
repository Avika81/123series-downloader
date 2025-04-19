from concurrent.futures import ThreadPoolExecutor
import threading
import yt_dlp
import queue
from concurrent.futures import ThreadPoolExecutor


def download(name: str, req):
    options = {
        "outtmpl": str(name),  # Output filename format
        "merge_output_format": "mp4",  # Merge video and audio into MKV
        "http_headers": req.headers,
        "quiet": True,
    }

    print(f"Downloading {name}")
    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([req.url])


class DownloadVideos:
    def __init__(self, to_download=None, max_workers=16):
        self.to_download = to_download
        self.input_queue = queue.Queue()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._queue_worker_thread = None
        self._start_queue_worker()

    def add(self, download_args: tuple):
        self.input_queue.put(download_args)

    # Function to continuously consume the queue and submit tasks to the executor
    def _start_queue_worker(self):
        self._queue_worker_thread = threading.Thread(target=self._queue_worker)
        self._queue_worker_thread.start()

    def _queue_worker(self):
        while True:
            args = self.input_queue.get()
            if args is None:  # Poison pill to shut down
                break
            self.executor.submit(lambda: download(*args))

    def wait_for_downloads(self):
        self.input_queue.put(None)
        self._queue_worker_thread.join()
        self.executor.shutdown(wait=True)

    # def start_downloads(
    #     self,
    # ):
    #     with ThreadPoolExecutor(max_workers=16) as executor:
    #         executor.map(lambda args: download(*args), list(self.to_download.items()))
