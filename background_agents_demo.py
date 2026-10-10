#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# SPDX-License-Identifier: MIT
"""Demonstrate concurrent background agents with Microsoft Agent Framework.

Run:
    uv run python background_agents_demo.py
    uv run python background_agents_demo.py --topic "Plan a 3-day trip to Istanbul."
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys
from dataclasses import dataclass

from agent_framework import (
    Agent,
    AgentLoopMiddleware,
    BackgroundAgentsProvider,
    background_tasks_running,
    background_tasks_running_message,
)
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_CONFIGURATION_ERROR = 2
DEFAULT_TOPIC = (
    "Plan a 3-day trip to Istanbul, including places to visit, restaurants, "
    "and a rough budget."
)

logger = logging.getLogger(__name__)


class ConfigurationError(ValueError):
    """Report missing or invalid demo configuration."""


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    project_endpoint: str
    model: str


def load_settings() -> Settings:
    """Load and validate environment variables used by the Foundry client.

    Returns:
        Validated runtime settings.

    Raises:
        ConfigurationError: If the Foundry project endpoint or model is missing.
    """
    project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT", "").strip()
    if not project_endpoint:
        raise ConfigurationError(
            "FOUNDRY_PROJECT_ENDPOINT is not set. Copy .env.example to .env and add "
            "your Microsoft Foundry project endpoint."
        )

    model = os.getenv("FOUNDRY_MODEL", "").strip()
    if not model:
        raise ConfigurationError(
            "FOUNDRY_MODEL is not set. Add your Foundry model deployment name to .env."
        )

    return Settings(project_endpoint=project_endpoint, model=model)


def create_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""
    parser = argparse.ArgumentParser(
        description="Run a Microsoft Agent Framework background agents demonstration."
    )
    parser.add_argument(
        "--topic",
        default=DEFAULT_TOPIC,
        help="Topic that the coordinator delegates to its background agents.",
    )
    return parser


def create_agent_team(
    client: FoundryChatClient,
) -> tuple[Agent, BackgroundAgentsProvider]:
    """Create three specialists and their coordinating parent agent.

    Args:
        client: Chat client shared by the parent and child agents.

    Returns:
        The coordinator agent and its background-agent provider.
    """
    attractions_agent = Agent(
        client=client,
        name="attractions_agent",
        description="Recommends Istanbul attractions, activities, and efficient daily groupings.",
        instructions=(
            "You are an Istanbul attractions specialist. Recommend major sights, cultural "
            "experiences, and activities for a three-day visit. Group nearby places to reduce "
            "travel time, mention approximate visit durations, and keep the pace realistic. "
            "Do not invent current opening hours or ticket prices."
        ),
    )
    food_agent = Agent(
        client=client,
        name="food_agent",
        description="Suggests Istanbul restaurants, neighborhoods, and local dishes.",
        instructions=(
            "You are an Istanbul food specialist. Suggest local dishes and practical restaurant "
            "or neighborhood options that fit a three-day itinerary. Include choices at different "
            "price points and clearly label recommendations that should be verified before travel."
        ),
    )
    budget_agent = Agent(
        client=client,
        name="budget_agent",
        description="Estimates accommodation, food, attractions, and local transportation costs.",
        instructions=(
            "You are a travel budget specialist. Estimate a rough three-day Istanbul budget for "
            "one traveler, excluding international flights. Break down accommodation, food, "
            "attractions, and local transportation. Use a clearly stated currency, provide a "
            "range, and label every pricing assumption as an estimate that should be verified."
        ),
    )

    background_provider = BackgroundAgentsProvider(
        [attractions_agent, food_agent, budget_agent],
        wait_timeout_seconds=30,
    )
    coordinator = Agent(
        client=client,
        name="coordinator",
        instructions=(
            "You are a travel coordinator planning a three-day Istanbul trip. For every request:\n"
            "1. Start one independent task on attractions_agent, food_agent, and budget_agent. "
            "Start all three tasks before waiting so they run concurrently.\n"
            "2. Call the task-list tool after starting them to inspect and report their statuses.\n"
            "3. Wait for tasks and retrieve every initial result.\n"
            "4. Demonstrate session continuity by continuing the completed food_agent task with "
            "this follow-up: 'Add one vegetarian local dish and one dessert option.' Retrieve the "
            "updated result.\n"
            "5. Clear every completed task only after all initial and follow-up results have been "
            "retrieved.\n"
            "6. Consolidate the results into a practical Day 1, Day 2, and Day 3 itinerary. "
            "Include meals near each day's attractions, a budget table, stated assumptions, and "
            "a reminder to verify current prices, opening hours, and reservations.\n"
            "Do not finish while any background task is still running."
        ),
        context_providers=[background_provider],
        middleware=[
            AgentLoopMiddleware(
                background_tasks_running(),
                next_message=background_tasks_running_message,
                max_iterations=10,
            )
        ],
    )
    return coordinator, background_provider


async def run_demo(settings: Settings, topic: str) -> None:
    """Run one coordinated background-agent task.

    Args:
        settings: Validated runtime settings.
        topic: Topic to delegate to the child agents.
    """
    client = FoundryChatClient(
        project_endpoint=settings.project_endpoint,
        model=settings.model,
        credential=AzureCliCredential(),
    )
    coordinator, background_provider = create_agent_team(client)
    session = coordinator.create_session()

    logger.info("Topic: %s", topic)
    logger.info(
        "Starting attractions, food, and budget agents as concurrent background tasks..."
    )

    try:
        response = await coordinator.run(topic, session=session)
        logger.info("Coordinator response:\n%s", response.text)
    finally:
        await background_provider.release_session(session)


def configure_logging() -> None:
    """Configure concise console logging for the demonstration."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")


def main() -> int:
    """Run the command-line application and return its process exit code."""
    configure_logging()
    load_dotenv()
    args = create_parser().parse_args()

    try:
        settings = load_settings()
        asyncio.run(run_demo(settings, args.topic))
    except ConfigurationError as error:
        logger.error("Configuration error: %s", error)
        return EXIT_CONFIGURATION_ERROR
    except KeyboardInterrupt:
        logger.error("Interrupted by user.")
        return 130
    except Exception:
        logger.exception("The background agents demo failed.")
        return EXIT_FAILURE

    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
