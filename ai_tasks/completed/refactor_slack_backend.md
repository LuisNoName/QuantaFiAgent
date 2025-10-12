# Task: Refactor Slack Backend into a Class-Based System

## Goal

Refactor the existing **Slack Backend** (currently a large procedural
`FastAPI` module) into a **class-based, modular architecture** that
improves readability, flexibility, and extensibility **without
introducing unnecessary complexity**.

The target audience is developers who should be able to **read and
understand `app.py` instantly**.

------------------------------------------------------------------------

## Motivation

The current file is monolithic and blends concerns (event verification,
message routing, Slack communication, and backend forwarding). This
makes onboarding and extension harder. The refactor should aim for
**clear separation of responsibilities** while keeping operational flow
identical.

------------------------------------------------------------------------

## Refactor Objectives

### 1. Core Structure

Convert the module into a class-based system using the following
structure (or a similar, equally clean alternative):

    slack_backend/
    ├── app.py                # Initializes the FastAPI app
    ├── handlers/
    │   ├── slack_gateway.py  # Class: SlackEventGateway (main orchestrator)
    │   ├── verifier.py       # Class: SlackRequestVerifier
    │   ├── normalizer.py     # Class: SlackEventNormalizer
    │   ├── agent_forwarder.py# Class: AgentBackendClient
    │   └── responder.py      # Class: SlackResponder
    └── utils/
        └── cache.py          # Simple TTL cache for event deduplication

Each class should have **clear, single responsibility** with dependency
injection where appropriate.

------------------------------------------------------------------------

### 2. Design Guidelines

-   **Avoid overengineering.** Prefer small, readable classes with
    simple constructors.
-   Use **composition over inheritance** (e.g., `SlackEventGateway`
    composes verifier, forwarder, and responder).
-   Maintain **statelessness** across requests; if state is needed (like
    cache), isolate it in a helper class.
-   Keep all business logic **framework-agnostic** except for the
    FastAPI route registration in `app.py`.
-   Do **not** introduce unnecessary abstractions (e.g., base classes
    unless justified).

------------------------------------------------------------------------

### 3. Expected Classes

#### `SlackRequestVerifier`

-   Verifies Slack signatures.
-   Rejects replay attacks.
-   Returns a boolean or raises exception.

#### `SlackEventNormalizer`

-   Converts Slack events into `AgentRequest` objects.
-   Cleans text, removes mentions, and fetches usernames.

#### `AgentBackendClient`

-   Handles HTTP calls to the Agent Backend.
-   Encapsulates retry and timeout logic.

#### `SlackResponder`

-   Sends messages back to Slack.
-   Wraps `slack_sdk.WebClient`.
-   Logs and handles errors gracefully.

#### `SlackEventGateway`

-   Central orchestrator handling event parsing, deduplication, and
    async processing.
-   Decides whether to respond or just record context.
-   Uses dependency-injected verifier, normalizer, forwarder, and
    responder.

------------------------------------------------------------------------

### 4. app.py Requirements

-   Should only **initialize**:
    -   The `FastAPI` app
    -   Instances of the above classes
    -   Route registration
-   Must **read like a high-level spec**, not a technical
    implementation.

Example (pseudo-code):

``` python
from fastapi import FastAPI
from slack_backend.handlers import SlackEventGateway

gateway = SlackEventGateway()
app = FastAPI(title="Slack Backend", version="2.0")
app.include_router(gateway.router)
```

------------------------------------------------------------------------

### 5. Best Practices to Follow

-   Follow PEP8 and standard typing hints.
-   Use clear, meaningful docstrings.
-   Use consistent logging (keep logger config centralized).
-   Keep environment variable access (`os.getenv`) limited to one config
    module.
-   Maintain the same `/slack/events` and `/healthz` endpoints.

------------------------------------------------------------------------

### 6. Testing & Validation

-   Ensure all current behaviors and response codes remain unchanged.
-   Test signature verification, event deduplication, and Slack posting
    flows.
-   Unit tests for each class are encouraged (especially the Verifier
    and Gateway).

------------------------------------------------------------------------

### 7. Deliverables

-   Fully refactored code, class-based, production-ready.
-   `app.py` should be \<50 lines and read declaratively.
-   Provide minimal inline docstrings; focus on clarity and
    maintainability.

------------------------------------------------------------------------

## Notes from Luis (author)

> Keep this elegant and *human-readable*. No "Enterprise-grade"
> complexity. I just want to open `app.py` and understand everything
> without scrolling or digging.
>
> The technical details --- like verifying HMACs, normalizing events, or
> posting to Slack --- should be hidden behind simple method calls.

------------------------------------------------------------------------

**Date:** 2025-10-12T16:43:57.356732Z **Author:** Luis **Version:** 1.0
