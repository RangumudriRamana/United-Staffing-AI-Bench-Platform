from datetime import datetime, timezone
from types import SimpleNamespace

from app.communications.timeline import TimelineComposer


def make_communication(
    public_id,
    communication_type,
    direction,
    subject,
    body_preview,
    occurred_at,
):
    return SimpleNamespace(
        public_id=public_id,
        communication_type=communication_type,
        direction=direction,
        subject=subject,
        body_preview=body_preview,
        occurred_at=occurred_at,
    )


def test_merge_and_sort_activities_maps_communication():
    older = make_communication(
        public_id="old-1",
        communication_type=SimpleNamespace(value="INTERNAL_NOTE"),
        direction=SimpleNamespace(value="INTERNAL"),
        subject="Older note",
        body_preview="Old content",
        occurred_at=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
    )

    newer = make_communication(
        public_id="new-1",
        communication_type=SimpleNamespace(value="INTERNAL_NOTE"),
        direction=SimpleNamespace(value="INTERNAL"),
        subject="Newer note",
        body_preview="New content",
        occurred_at=datetime(2026, 1, 2, 10, 0, tzinfo=timezone.utc),
    )

    result = TimelineComposer.merge_and_sort_activities([older, newer])

    assert len(result) == 2

    assert result[0]["source"] == "COMMUNICATION"
    assert result[0]["public_id"] == "new-1"
    assert result[0]["type"] == "INTERNAL_NOTE"
    assert result[0]["direction"] == "INTERNAL"
    assert result[0]["title"] == "Newer note"
    assert result[0]["content"] == "New content"
    assert result[0]["timestamp"] == "2026-01-02T10:00:00+00:00"


def test_merge_and_sort_activities_sorts_newest_first():
    first = make_communication(
        public_id="1",
        communication_type=SimpleNamespace(value="INTERNAL_NOTE"),
        direction=SimpleNamespace(value="INTERNAL"),
        subject="First",
        body_preview="First body",
        occurred_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )

    second = make_communication(
        public_id="2",
        communication_type=SimpleNamespace(value="INTERNAL_NOTE"),
        direction=SimpleNamespace(value="INTERNAL"),
        subject="Second",
        body_preview="Second body",
        occurred_at=datetime(2026, 1, 3, tzinfo=timezone.utc),
    )

    third = make_communication(
        public_id="3",
        communication_type=SimpleNamespace(value="INTERNAL_NOTE"),
        direction=SimpleNamespace(value="INTERNAL"),
        subject="Third",
        body_preview="Third body",
        occurred_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
    )

    result = TimelineComposer.merge_and_sort_activities([first, second, third])

    assert [item["public_id"] for item in result] == ["2", "3", "1"]


def test_merge_and_sort_activities_handles_empty_list():
    result = TimelineComposer.merge_and_sort_activities([])

    assert result == []


def test_merge_and_sort_activities_preserves_optional_body_preview():
    communication = make_communication(
        public_id="optional-1",
        communication_type=SimpleNamespace(value="INTERNAL_NOTE"),
        direction=SimpleNamespace(value="INTERNAL"),
        subject="No body",
        body_preview=None,
        occurred_at=datetime(2026, 2, 1, tzinfo=timezone.utc),
    )

    result = TimelineComposer.merge_and_sort_activities([communication])

    assert result[0]["content"] is None