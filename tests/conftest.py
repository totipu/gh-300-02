from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


_BASELINE_ACTIVITIES = deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities_state():
    app_module.activities.clear()
    app_module.activities.update(deepcopy(_BASELINE_ACTIVITIES))


@pytest.fixture
def client():
    return TestClient(app_module.app)