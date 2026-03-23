# Environment Guide

## No keys needed yet

The repository runs in seeded demo mode without secrets.

## Keys to add later

- `ANTHROPIC_API_KEY`: for live signal synthesis and portfolio reasoning.
- `OPENAI_API_KEY`: optional alternative for narrative generation.
- `CLERK_SECRET_KEY`: if authenticated portfolio sessions are enabled.
- `REDIS_URL`: for queueing and pub-sub.
- `POSTGRES_URL`: for persistence.

## When to provide keys

You only need to send keys after you want me to replace the local deterministic adapters with live providers. Until then, the implementation remains unblocked.
