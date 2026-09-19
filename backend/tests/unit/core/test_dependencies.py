from unittest.mock import patch

from app.core.dependencies import get_app_settings


def test_get_app_settings_returns_settings():
    expected_settings = object()

    with patch(
        "app.core.dependencies.get_settings",
        return_value=expected_settings,
    ) as mock_get_settings:
        result = get_app_settings()

    assert result is expected_settings
    mock_get_settings.assert_called_once_with()