# Testing

This directory contains tests for the Norway Alerts integration.

## Test Structure

- **Unit Tests** (`test_*.py`): Pytest-based unit tests suitable for HA core integration
  - `test_api.py`: Tests for API client classes (LandslideAPI, FloodAPI, AvalancheAPI, MetAlertsAPI)
  - `test_config_flow.py`: Tests for configuration flow
  - `test_sensor.py`: Tests for sensor entity
  - `conftest.py`: Pytest fixtures and shared test configuration

- **Manual Tests** (for API exploration/debugging):
  - `manual_nve_api.py`: Manual script to test NVE API responses
  - `manual_avalanche_api.py`: Manual script to test current avalanche API logic

## Running Unit Tests

Install test dependencies:
```bash
pip install pytest pytest-asyncio pytest-cov pytest-homeassistant-custom-component
```

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=custom_components/norway_alerts --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_api.py
```

Run specific test:
```bash
pytest tests/test_api.py::TestLandslideAPI::test_fetch_warnings_success
```

## Manual Testing Scripts

These scripts are for manual API exploration and require an active internet connection:

```bash
# Test NVE API (landslide/flood)
python tests/manual_nve_api.py

# Test current avalanche API
python tests/manual_avalanche_api.py
```

## For HA Core Integration

When preparing for HA core integration, ensure:
1. All unit tests pass
2. Test coverage is above 90%
3. Tests follow HA core testing patterns
4. No external API calls in unit tests (all mocked)
5. Manual test scripts are excluded from CI/CD

## Test Data

The `test_data/` directory contains sample API responses used for testing and development.
