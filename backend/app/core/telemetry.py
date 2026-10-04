from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TelemetryEvent:
    """Minimal event container used for workflow and service observability."""

    event_name: str
    metadata: dict[str, object] | None = None


class Telemetry:
    """Placeholder telemetry implementation.

    This will later emit workflow events to a backend logger, analytics service, or tracing system.
    """

    def __init__(self) -> None:
        self.events: list[TelemetryEvent] = []

    def emit(self, event_name: str, **metadata: object) -> None:
        self.events.append(TelemetryEvent(event_name=event_name, metadata=metadata))
