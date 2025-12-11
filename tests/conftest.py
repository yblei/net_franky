"""Pytest configuration and fixtures."""
import pytest
from net_franky.setup import cfg


@pytest.fixture(autouse=True)
def reset_config():
    """Reset configuration between tests."""
    yield
    # Reset config after each test
    cfg.IS_SETUP = False
    cfg.IP = None
    cfg.PORT = None
