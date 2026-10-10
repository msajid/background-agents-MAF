---
title: Microsoft Agent Framework Background Agents Demo
description: Beginner-friendly Python demonstration of concurrent background agents
ms.date: 2026-10-10
ms.topic: tutorial
---

## What this demo shows

This project asks a parent agent to plan a three-day Istanbul trip. The parent delegates
three independent tasks to named background agents:

* `attractions_agent` recommends places to visit and activities
* `food_agent` suggests restaurants, neighborhoods, and local dishes
* `budget_agent` estimates accommodation, food, attractions, and transportation costs

The coordinator starts all three tasks before waiting, so they can run concurrently in
separate child-agent sessions. It then retrieves each result, combines the findings, and
creates a consolidated itinerary.

The coordinator also checks task statuses and sends a follow-up request to the existing
food-agent task. That follow-up reuses the child's conversation session instead of starting
a new task without context. Completed tasks are cleared after their results are collected.

The example also uses `AgentLoopMiddleware`. If the coordinator returns while a task is
still running, the middleware invokes it again with a reminder to finish processing its
background work.

> [!IMPORTANT]
> Background agents are experimental. Their APIs may change between Agent Framework
> releases.

This repository is designed for learning, technical blog posts, and live demonstrations.
It is not a production travel-planning service. Recommendations and prices are model
output and must be verified before travel.

## Architecture

```text
Istanbul trip request
    |
    v
Coordinator agent
    |
    +-- attractions task --+
    +-- food task ---------+--> results --> 3-day itinerary
    +-- budget task -------+
             |
             +--> follow-up in the same food-agent session
```

Each child task receives its own session. The parent session stores task IDs and status
metadata. The `finally` block calls `release_session` so in-process task handles and child
sessions are released even when a request fails.

## Prerequisites

* Python 3.11 or later
* [uv](https://docs.astral.sh/uv/)
* [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)
* A Microsoft Foundry project
* A deployed Foundry model that supports tool calling

## Setup

1. Install the dependencies:

   ```powershell
   uv sync
   ```

2. Sign in to Azure:

   ```powershell
   az login
   ```

3. Copy the environment template:

   ```powershell
   Copy-Item .env.example .env
   ```

4. Open `.env` and set:

   * `FOUNDRY_PROJECT_ENDPOINT` to your Foundry project endpoint
   * `FOUNDRY_MODEL` to your model deployment name

The demo authenticates with `AzureCliCredential`, so it uses the Azure CLI identity from
`az login`. No API key is stored in the project.

## Run the demo

Run the default example:

```powershell
uv run python background_agents_demo.py
```

Provide a topic during a live demonstration:

```powershell
uv run python background_agents_demo.py `
  --topic "Plan a 3-day trip to Istanbul, including places to visit, restaurants, and a rough budget."
```

The script logs when delegation starts and prints the coordinator's synthesized response.
The exact wording varies because the parent decides how to call the framework-provided
background-agent tools.

## How the lifecycle maps to the code

1. `BackgroundAgentsProvider` registers the three named child agents with the coordinator.
2. The provider gives the coordinator tools to start, wait for, inspect, continue, and
   clear background tasks.
3. The coordinator starts all independent tasks before waiting, then checks their statuses.
4. It retrieves the initial results and continues the food task with a follow-up request.
5. `AgentLoopMiddleware` keeps the coordinator active while persisted task state reports
   running work.
6. It clears completed tasks after retrieval, then consolidates the results.
7. `release_session` performs host-side cleanup in a `finally` block.

The provider has no model-facing cancellation tool. A running task normally reaches a
terminal state before the agent clears it. Host-side `release_session` can cancel remaining
tasks when the application discards the parent session.

## Run checks

```powershell
uv run ruff check .
uv run pytest
```

The unit tests do not call a model or require a real API key.

## Contributing and support

Contributions are welcome. Read [CONTRIBUTING.md](./CONTRIBUTING.md) before opening a pull
request. Use GitHub Issues for reproducible bugs and focused feature requests.

For security concerns, follow [SECURITY.md](./SECURITY.md) instead of opening a public
issue. General usage guidance is available in [SUPPORT.md](./SUPPORT.md).

## Maintainer publishing checklist

After creating the GitHub repository:

1. Add a concise repository description and the topics `microsoft-agent-framework`,
   `background-agents`, `multi-agent`, and `python`.
2. Enable GitHub Actions and confirm the CI workflow passes.
3. Enable private vulnerability reporting in **Settings > Security**.
4. Enable Dependabot alerts and security updates.
5. Protect the `main` branch by requiring pull requests and the CI status check.
6. Review the repository's visibility, Discussions setting, and notification preferences.

## License

This project is licensed under the MIT License. See [LICENSE](./LICENSE).

## Official references

* [Background Agents documentation](https://learn.microsoft.com/en-us/agent-framework/agents/background-agents?pivots=programming-language-python)
* [Microsoft Agent Framework repository](https://github.com/microsoft/agent-framework)
