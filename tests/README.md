# Running Tests

## Setup

Install the package with dev dependencies:

```bash
pip install -e ".[dev]"
```

## Run Tests

Run all tests:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=net_franky --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_setup.py
```

Run tests with verbose output:
```bash
pytest -v
```

## Test Structure

- `tests/test_setup.py` - Tests for the setup functionality
- `tests/test_cb_robot.py` - Tests for the CBRobot callback system
- `tests/conftest.py` - Pytest configuration and fixtures
