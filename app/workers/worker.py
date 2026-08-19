import asyncio, socket
from app.queue import RedisQueue
from app.db import SessionLocal
from app.repositories import recover_inflight
from app.logging import configure_logging, get_logger

log=get_logger("worker")

async def run():
    configure_logging()
    q=RedisQueue()
    await q.ensure_group()
    async with SessionLocal() as session:
        await recover_inflight(session)
    consumer=f"{socket.gethostname()}-{id(q)}"
    try:
        while True:
            rows=await q.read(consumer,count=1,block_ms=5000)
            for _, messages in rows:
                for msg_id, data in messages:
                    upload_id=int(data["upload_id"])
                    try:
                        # Wire UploadService here after choosing a bot session/client lifecycle.
                        # Keeping the queue consumer separate makes processing restart-safe.
                        log.info("job_received", upload_id=upload_id)
                        await q.ack(msg_id)
                    except Exception as exc:
                        log.error("job_failed", upload_id=upload_id, error=str(exc))
    finally:
        await q.close()

if __name__=="__main__":
    asyncio.run(run())
