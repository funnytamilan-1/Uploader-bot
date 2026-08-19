import asyncio, json
from pathlib import Path
from app.config import get_settings

class FFmpegError(RuntimeError): pass

class FFmpegService:
    def __init__(self, binary="ffmpeg", probe_binary="ffprobe"):
        self.binary, self.probe_binary = binary, probe_binary

    def _validate(self, path: str):
        p=Path(path).resolve()
        root=Path(get_settings().media_root).resolve()
        if root not in p.parents and p != root:
            raise ValueError("Path outside MEDIA_ROOT")
        if not p.exists():
            raise FileNotFoundError(path)
        return p

    async def _run(self, args: list[str]) -> tuple[str,str]:
        proc = await asyncio.create_subprocess_exec(*args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        out, err = await proc.communicate()
        if proc.returncode != 0:
            raise FFmpegError(err.decode(errors="replace")[-4000:])
        return out.decode(errors="replace"), err.decode(errors="replace")

    async def probe(self, path: str) -> dict:
        p=self._validate(path)
        out,_=await self._run([self.probe_binary,"-v","error","-print_format","json","-show_format","-show_streams",str(p)])
        return json.loads(out)

    async def thumbnail(self, input_path: str, output_path: str, timestamp: float=0):
        src=self._validate(input_path); dst=self._validate(output_path)
        dst.parent.mkdir(parents=True, exist_ok=True)
        await self._run([self.binary,"-y","-ss",str(max(0,timestamp)),"-i",str(src),"-frames:v","1","-vf","scale='min(1280,iw)':-2","-q:v","3",str(dst)])

    async def transcode(self, input_path: str, output_path: str, profile: str):
        src=self._validate(input_path); dst=self._validate(output_path)
        dst.parent.mkdir(parents=True, exist_ok=True)
        profiles={
            "Original": [],
            "720p": ["-vf","scale=-2:720","-c:v","libx264","-preset","medium","-crf","23"],
            "1080p": ["-vf","scale=-2:1080","-c:v","libx264","-preset","medium","-crf","22"],
            "H264": ["-c:v","libx264","-c:a","aac"],
            "HEVC": ["-c:v","libx265","-c:a","aac"],
        }
        if profile not in profiles: raise ValueError("Unknown FFmpeg profile")
        await self._run([self.binary,"-y","-i",str(src),*profiles[profile],str(dst)])
