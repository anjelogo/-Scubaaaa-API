import asyncio
import logging
from collections.abc import AsyncGenerator

import httpx

logger = logging.getLogger(__name__)

_BOUNDARY = b"frame"
_MJPEG_PART_HEADER = (
    b"--frame\r\nContent-Type: image/jpeg\r\nContent-Length: "
)


async def _parse_frames(source_url: str) -> AsyncGenerator[bytes, None]:
    """Stream MJPEG from source_url, yielding raw JPEG bytes per frame."""
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("GET", source_url) as resp:
            resp.raise_for_status()
            buf = b""
            async for chunk in resp.aiter_bytes(8192):
                buf += chunk
                while True:
                    cl_pos = buf.find(b"Content-Length:")
                    if cl_pos == -1:
                        break
                    nl = buf.find(b"\r\n", cl_pos)
                    if nl == -1:
                        break
                    cl = int(buf[cl_pos + 15 : nl].strip())
                    hdr_end = buf.find(b"\r\n\r\n", cl_pos)
                    if hdr_end == -1:
                        break
                    data_start = hdr_end + 4
                    data_end = data_start + cl
                    if len(buf) < data_end:
                        break
                    yield buf[data_start:data_end]
                    buf = buf[data_end:]


class MJPEGBroadcaster:
    """Holds one upstream MJPEG connection; fans frames to N subscribers."""

    def __init__(self, source_url: str):
        self._source_url = source_url
        self._queues: list[asyncio.Queue[bytes]] = []
        self._task: asyncio.Task | None = None
        self._latest: bytes | None = None

    def subscribe(self) -> asyncio.Queue[bytes]:
        q: asyncio.Queue[bytes] = asyncio.Queue(maxsize=2)
        self._queues.append(q)
        if self._latest:
            try:
                q.put_nowait(self._latest)
            except asyncio.QueueFull:
                pass
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._read_loop())
        return q

    def unsubscribe(self, q: asyncio.Queue[bytes]) -> None:
        try:
            self._queues.remove(q)
        except ValueError:
            pass

    async def _read_loop(self) -> None:
        while self._queues:
            try:
                async for frame in _parse_frames(self._source_url):
                    if not self._queues:
                        return
                    self._latest = frame
                    for q in list(self._queues):
                        if q.full():
                            try:
                                q.get_nowait()
                            except asyncio.QueueEmpty:
                                pass
                        try:
                            q.put_nowait(frame)
                        except asyncio.QueueFull:
                            pass
            except Exception as exc:
                logger.warning("Upstream stream error: %s — retrying in 2s", exc)
                await asyncio.sleep(2)

    async def iter_multipart(self, q: asyncio.Queue[bytes]) -> AsyncGenerator[bytes, None]:
        """Yield MJPEG multipart chunks for a single subscriber."""
        try:
            while True:
                frame = await q.get()
                yield _MJPEG_PART_HEADER + str(len(frame)).encode() + b"\r\n\r\n"
                yield frame
                yield b"\r\n"
        finally:
            self.unsubscribe(q)


broadcaster: MJPEGBroadcaster | None = None


def init_broadcaster(source_url: str) -> MJPEGBroadcaster:
    global broadcaster
    broadcaster = MJPEGBroadcaster(source_url)
    return broadcaster
