# Tests Directory

This directory contains tests for the Databricks GenAI Hackathon project.

## Test Files

### test_environment_unittest.py
Unit tests for the `Environment` class using Python's built-in unittest framework.

### test_environment.py
Unit tests for the `Environment` class using pytest framework (requires pytest installation).

## Running Tests

### Using unittest (no additional dependencies)
```bash
cd tests
python test_environment_unittest.py
```

### Using pytest (requires pytest installation)
```bash
# Install test dependencies
pip install -r tests/requirements-test.txt

# Run pytest tests
cd tests
python -m pytest test_environment.py -v
```

Or run from project root:
```bash
python -m pytest tests/ -v
```

## Test Coverage

The tests cover the following aspects of the Environment class:

1. **Basic Creation**: Testing that Environment can be created with all required fields
2. **Field Validation**: Testing that missing required fields raise validation errors
3. **Type Checking**: Ensuring all fields have the correct types
4. **Inheritance**: Verifying proper inheritance from parent classes
5. **Model Validation**: Testing the custom model validator for mlflow_experiment_base_path
6. **Edge Cases**: Testing empty lists, explicit vs auto-imputed values
7. **Serialization**: Testing model_dump() functionality
8. **Error Handling**: Testing error scenarios in validators
9. **Real-world Data**: Testing with data structures similar to actual project.yml

## Test Structure

Each test follows the Arrange-Act-Assert pattern:
- **Arrange**: Set up test data and mocks
- **Act**: Create Environment instance or call methods
- **Assert**: Verify expected behavior

## Mocking

The tests use mocking for external dependencies:
- `databricks.sdk.WorkspaceClient` is mocked to avoid requiring actual Databricks credentials during testing
- User information is mocked to test path imputation logic

## Adding New Tests

When adding new tests:
1. Follow the existing naming convention (`test_<functionality>`)
2. Include docstrings explaining what the test covers
3. Use descriptive variable names
4. Test both positive and negative cases where applicable
5. Mock external dependencies appropriately