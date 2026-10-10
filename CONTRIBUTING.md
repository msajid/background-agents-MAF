---
title: Contributing
description: How to contribute changes to the background agents demonstration
ms.date: 2026-10-10
ms.topic: contributor-guide
---

## Before you contribute

Thank you for improving this demonstration. Keep changes focused on making Microsoft
Agent Framework background agents easier to understand, run, and explain.

By participating, you agree to follow [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md).

## Development setup

1. Fork and clone the repository.
2. Install [uv](https://docs.astral.sh/uv/).
3. Install the project and development dependencies:

   ```powershell
   uv sync
   ```

4. Copy the environment template only when you need to run the live demo:

   ```powershell
   Copy-Item .env.example .env
   ```

5. Set your Foundry project endpoint and model deployment in `.env`, then authenticate
   with `az login`. Never commit `.env` or any credential.

## Make a change

* Keep the example beginner-friendly and avoid unnecessary abstractions.
* Preserve concurrent delegation and explicit background-task cleanup.
* Add or update tests for behavior that does not require a live model.
* Update the README when setup, output, or lifecycle behavior changes.
* Do not include generated environments, caches, credentials, or model output.

## Validate your change

Run the same checks used by continuous integration:

```powershell
uv run ruff check .
uv run pytest
```

If your change affects live agent behavior, also run the demo with a supported
tool-calling model. Remove sensitive output before sharing logs.

## Open a pull request

Describe:

* The problem being solved
* The approach taken
* The validation performed
* Any Agent Framework API or behavior changes readers should know about

Keep each pull request small enough to review and demonstrate independently.
