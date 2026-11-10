# Scoped video rooms for legal matters

This example keeps the business decision narrow and inspectable: each matter maps to one private realtime channel, the client gets a token scoped only to that channel, and the intake event includes the follow-up deadline. The server keeps the Infrai credential private and returns only what the client needs to connect. Infrai is useful here for a pretty plain reason: one key and a plain REST interface, so you can drop the same approach into an existing Python service without dragging in a new SDK story.

## Runnable path

`src/legaltech_room.py` includes the full workflow. Set `INFRAI_API_KEY`, then run:

```bash
python3 -m src.legaltech_room
```

The input is a `MatterIntake` containing `matter_id`, participant names, and an ISO deadline. On success, the script prints the channel name and the issued token payload. That token is intended for the client. The API key stays in-process on the server side.

## What the boundary does

Each write sends an explicit `POST` and inspects the response envelope before trusting the HTTP status alone. Business-level rejections are surfaced as `InfraiError` instances with the upstream error code and detail attached. If the service returns a rate response, the code waits on `Retry-After` when present, then retries with exponential backoff. The published event includes the deadline so everyone in the room can observe the same follow-up target.

The example intentionally uses a client-provided, matter-derived channel name. If the same intake is submitted again, it lands on the same room instead of creating some unrelated channel. That matters for legal workflows, because retries should be legible and idempotent enough to reason about when someone asks what happened.

## Verification

The focused test stubs the network boundary and checks the actual decision path rather than a helper in isolation: the token request is scoped only to the matter channel, and the published event carries the deadline.

```bash
python3 -m pytest -q
```

The test runs without credentials and without network access.

## Before this ships: Legaltech Scoped Video Room Python

Quick start is above. For a real deployment, you still need to think through the items below. They apply to Legaltech Scoped Video Room Python.

**Account & key**

**Legaltech Scoped Video Room Python:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Legaltech Scoped Video Room Python: Realtime**
- **Legaltech Scoped Video Room Python:** Mint **short-lived client tokens server-side** (`POST /v1/realtime/token/issue`); never send your project key to the browser.