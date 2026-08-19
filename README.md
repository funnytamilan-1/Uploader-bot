# Advanced Telegram Media Auto-Uploader

Production-oriented, restart-safe Telegram media automation for media the operator has the legal right to upload/distribute.

## Architecture

- **Bot layer:** Pyrogram handlers + inline admin/user UI.
- **Persistence:** PostgreSQL via SQLAlchemy 2.x async ORM and Alembic.
- **Queue:** Redis Streams for durable worker delivery and retry scheduling.
- **Workers:** asynchronous upload worker and processing worker.
- **Media:** FFmpeg wrapper using argument arrays only.
- **Metadata:** provider abstraction with a configurable HTTP provider; cached in DB/Redis.
- **Rename:** deterministic local parser plus optional OpenAI-compatible structured JSON service.
- **Thumbnails:** FFmpeg frame extraction + JPEG normalization.
- **Scheduler:** APScheduler backed by persistent PostgreSQL job records; recurring jobs are persisted as application records.
- **Reliability:** idempotency keys, explicit job states, recovery of PROCESSING/UPLOADING jobs, exponential backoff, graceful shutdown.
- **Security:** all secrets from environment variables; admin IDs parsed server-side; secrets are redacted from logs.

## Database schema

Core relationships:

`users -> uploads -> files/media`
`users -> subscriptions -> plans`
`channels -> uploads`
`queue_jobs -> uploads`
`scheduled_jobs -> uploads`
`media -> episodes`
`media -> thumbnails`
`rename_rules` and `settings` provide configuration.
`audit_logs` records security-sensitive administrative actions.

Important indexes exist on upload status, queue priority, scheduled time, Telegram IDs, and idempotency keys.

## Run

1. Copy `.env.example` to `.env`.
2. Fill credentials.
3. Start PostgreSQL and Redis.
4. Run migrations:
   `alembic upgrade head`
5. Start bot:
   `python -m app`
6. Start workers:
   `python -m app.workers.worker`
7. Start scheduler:
   `python -m app.scheduler`

Docker Compose starts all services.

## Legal/content constraint

This project intentionally does **not** implement piracy-source scraping, unauthorized downloading, DRM circumvention, torrent/leech automation for copyrighted releases, or copyright-evasion functionality. It accepts media supplied by an authorized operator and automates processing/distribution from configured destinations.
