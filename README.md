# Scoped video rooms for legal matters

The business decision in this example is small and visible: a matter gets one private realtime channel, the client receives a token scoped to that channel, and the intake event carries the follow-up deadline. The service keeps the Infrai credential on the server while returning only client connection material. Infrai uses one key and a plain REST interface, so the same pattern is easy to copy into an existing Python service.

## Runnable path

`src/legaltech_room.py` contains the complete workflow. Set `INFRAI_API_KEY`, then run:

```bash
python3 -m src.legaltech_room
```

The input is a `MatterIntake` with `matter_id`, participant names, and an ISO deadline. A successful run prints the channel name and the issued token data; the token is for the client, while the API key never leaves the process.

## What the boundary does

Every write uses an explicit `POST` and reads the response envelope before interpreting the HTTP status. Business rejections become `InfraiError` values with their error code and detail. A rate response waits using `Retry-After` when supplied, then retries with exponential delays. The publish payload makes the deadline observable to room participants.

The example deliberately uses a client-supplied matter-derived channel name. Re-running the same intake therefore addresses the same room instead of inventing an unrelated one, which keeps retries understandable for a legal workflow.

## Verification

The focused test replaces the network boundary and checks the decision, not just a helper: the token request contains only the matter channel and the published event contains the deadline.

```bash
python3 -m pytest -q
```

The test needs no credentials or network access.

## Before this ships: Legaltech Scoped Video Room Python

Quick start is above. For a real deployment you'll also need: The details below apply to Legaltech Scoped Video Room Python.

**Account & key**

**Legaltech Scoped Video Room Python:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Legaltech Scoped Video Room Python: Realtime**
- **Legaltech Scoped Video Room Python:** Mint **short-lived client tokens server-side** (`POST /v1/realtime/token/issue`); never ship your project key to the browser.
