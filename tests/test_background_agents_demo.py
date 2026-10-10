"""Unit tests for the background agents demonstration."""

import pytest

from background_agents_demo import (
    DEFAULT_TOPIC,
    ConfigurationError,
    create_parser,
    load_settings,
)


def test_given_no_topic_when_parsing_arguments_then_uses_istanbul_trip() -> None:
    # Act
    arguments = create_parser().parse_args([])

    # Assert
    assert arguments.topic == DEFAULT_TOPIC


def test_given_foundry_configuration_when_loading_settings_then_returns_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    endpoint = "https://example.services.ai.azure.com/api/projects/demo"
    monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", endpoint)
    monkeypatch.setenv("FOUNDRY_MODEL", "gpt-4.1-mini")

    # Act
    settings = load_settings()

    # Assert
    assert settings.project_endpoint == endpoint
    assert settings.model == "gpt-4.1-mini"


def test_given_missing_project_endpoint_when_loading_settings_then_raises_configuration_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    monkeypatch.delenv("FOUNDRY_PROJECT_ENDPOINT", raising=False)
    monkeypatch.setenv("FOUNDRY_MODEL", "gpt-4.1-mini")

    # Act and Assert
    with pytest.raises(ConfigurationError, match="FOUNDRY_PROJECT_ENDPOINT is not set"):
        load_settings()


def test_given_missing_model_when_loading_settings_then_raises_configuration_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    monkeypatch.setenv(
        "FOUNDRY_PROJECT_ENDPOINT",
        "https://example.services.ai.azure.com/api/projects/demo",
    )
    monkeypatch.delenv("FOUNDRY_MODEL", raising=False)

    # Act and Assert
    with pytest.raises(ConfigurationError, match="FOUNDRY_MODEL is not set"):
        load_settings()
