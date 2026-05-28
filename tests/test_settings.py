import pytest
from app.settings import Settings, load_settings


def test_load_settings_defaults():
    settings = load_settings("config/settings.yaml")
    assert settings.output_limits["mix"] == 300
    assert settings.timeouts["http"] == 15
    assert settings.retry["max_retries"] == 3


def test_settings_is_singleton():
    s1 = load_settings("config/settings.yaml")
    s2 = load_settings("config/settings.yaml")
    assert s1 is s2


def test_settings_from_dict():
    s = Settings({"output_limits": {"mix": 100}})
    assert s.output_limits["mix"] == 100
    assert s.health == {}
