# Operations

## Recovery
On startup the worker resets PROCESSING/UPLOADING jobs to PENDING. Idempotency keys prevent duplicate logical submissions.

## Scaling
Run multiple worker replicas with the same Redis consumer group. For high scale, split processing and upload streams into separate Redis Streams.

## Telegram limits
Respect Telegram Bot API limits and throttle status edits. For very large files or advanced MTProto workflows, evaluate Telegram's current limits and account/channel policies before deployment.

## Secrets
Never commit `.env`. Rotate keys if they are ever exposed.

## Authorized media only
Only process files you are authorized to upload and distribute.
