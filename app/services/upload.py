from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pyrogram import Client
from pyrogram.types import Message
from app.models import Upload, Channel, File, JobState
from app.config import get_settings

class UploadService:
    def __init__(self, client: Client):
        self.client=client

    async def send(self, session: AsyncSession, upload_id: int, progress=None) -> Message:
        upload=await session.get(Upload, upload_id)
        if not upload: raise ValueError("Upload not found")
        channel=await session.get(Channel, upload.channel_id)
        file=await session.get(File, upload.file_id)
        if not channel or not file: raise ValueError("Upload dependencies missing")
        upload.state=JobState.UPLOADING
        await session.commit()

        async def cb(current, total):
            if progress: await progress(current,total)

        msg=await self.client.send_document(
            chat_id=channel.telegram_chat_id,
            document=file.path,
            caption=upload.caption or "",
            progress=cb,
        )
        upload.message_id=msg.id
        upload.state=JobState.COMPLETED
        await session.commit()
        return msg
