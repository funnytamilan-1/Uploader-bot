from pathlib import Path
from app.services.ffmpeg import FFmpegService
import hashlib

class ThumbnailService:
    def __init__(self, ffmpeg: FFmpegService):
        self.ffmpeg=ffmpeg

    async def extract(self, video: str, output: str, timestamp: float=0):
        await self.ffmpeg.thumbnail(video, output, timestamp)
        return output

    @staticmethod
    def sha256(path: str) -> str:
        h=hashlib.sha256()
        with open(path,"rb") as f:
            for chunk in iter(lambda:f.read(1024*1024), b""): h.update(chunk)
        return h.hexdigest()
