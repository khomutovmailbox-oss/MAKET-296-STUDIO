"""Coalescing background renderer: one active job, at most one pending job.

Rapid zoom/page changes replace obsolete queued work instead of serializing every
expensive SVG/Inkscape render. Active jobs cannot be interrupted, but callers
must use a monotonically increasing token to discard their stale results.
"""
from concurrent.futures import ThreadPoolExecutor
from threading import Lock


class LatestRenderQueue:
    def __init__(self):
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix='vf-preview')
        self._lock = Lock()
        self._pending = None
        self._running = False
        self._closed = False
        self.submitted = 0
        self.coalesced = 0
        self.executed = 0

    def submit(self, job):
        with self._lock:
            if self._closed:
                raise RuntimeError('render queue is closed')
            self.submitted += 1
            if self._running:
                if self._pending is not None:
                    self.coalesced += 1
                self._pending = job
            else:
                self._running = True
                self._executor.submit(self._drain, job)

    def _drain(self, job):
        while job is not None:
            try:
                with self._lock:
                    self.executed += 1
                job()
            except Exception:
                # Render workers report errors to the UI event queue themselves.
                # Keep servicing newer requests even if an unexpected exception occurs.
                pass
            with self._lock:
                if self._closed:
                    self._pending = None
                    self._running = False
                    return
                job = self._pending
                self._pending = None
                if job is None:
                    self._running = False
                    return

    def shutdown(self, wait=True):
        with self._lock:
            self._closed = True
            self._pending = None
        self._executor.shutdown(wait=wait, cancel_futures=True)
