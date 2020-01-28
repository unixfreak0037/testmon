
import pytest

from testmon import MonitorIn

def test_custom_monitor_in_validator_app_id_failure():
    _dict = {
        "app_id": "012abcABC!",
        "action": "start",
        "duration": 3600,
    }
    with pytest.raises(ValueError):
        m = MonitorIn(**_dict)

def test_custom_monitor_in_validator_app_id_success():
    _dict = {
        "app_id": "0123abcABC",
        "action": "start",
        "duration": 3600,
    }
    m = MonitorIn(**_dict)
    assert m.app_id == _dict['app_id']
    assert m.action == _dict['action']
    assert m.duration == _dict['duration']

def test_custom_monitor_in_validator_action_failure():
    _dict = {
        "app_id": "0123abcABC",
        "action": "not_valid",
        "duration": 3600,
    }
    with pytest.raises(ValueError):
        m = MonitorIn(**_dict)

def test_custom_monitor_in_validator_action_start():
    _dict = {
        "app_id": "0123abcABC",
        "action": "start",
        "duration": 3600,
    }
    m = MonitorIn(**_dict)
    assert m.action == _dict['action']

def test_custom_monitor_in_validator_action_stop():
    _dict = {
        "app_id": "0123abcABC",
        "action": "stop",
        "duration": 3600,
    }
    m = MonitorIn(**_dict)
    assert m.action == _dict['action']