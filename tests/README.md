# Testing the Authentication Service

This directory contains tests for the application, including tests for the authentication service.

## Running Tests

You can run the tests using one of the following methods:

### Using the run_tests.py script

```bash
# Run all tests
./run_tests.py

# Run specific test file
./run_tests.py tests/services/authentication/test_authenticate.py

# Run with verbose output
./run_tests.py -v
```

### Using pytest directly

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/services/authentication/test_authenticate.py

# Run with verbose output
pytest -v
```

## Test Structure

- `conftest.py`: Contains global test configurations and fixtures
- `services/`: Contains tests for different services
  - `authentication/`: Tests for the authentication service
    - `test_authenticate.py`: Tests for the AuthenticationService class

## Test Coverage

The tests cover the following scenarios for the authentication service:

1. Valid token authentication
2. Invalid token authentication (wrong secret key)
3. Expired token authentication
4. Malformed token authentication 