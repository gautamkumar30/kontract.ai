# Test Suite for Contracts Router

Comprehensive test cases for the contracts API endpoints.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and test database setup
├── contracts.test.py        # Contract router tests (40+ test cases)
├── fixtures/
│   ├── sample_contract.pdf  # Sample PDF for upload testing
│   └── sample_contract.txt  # Sample TXT for upload testing
└── run_tests.sh            # Test execution script
```

## Running Tests

### Quick Start

```bash
# Run all tests with coverage
./tests/run_tests.sh

# Or using pytest directly
pytest tests/contracts.test.py -v --cov=routers.contracts
```

### Test Execution Options

The `run_tests.sh` script provides multiple options:

```bash
./tests/run_tests.sh all         # All tests with coverage (default)
./tests/run_tests.sh quick       # All tests without coverage
./tests/run_tests.sh create      # Test contract creation only
./tests/run_tests.sh list        # Test contract listing only
./tests/run_tests.sh get         # Test get by ID only
./tests/run_tests.sh delete      # Test deletion only
./tests/run_tests.sh upload      # Test file upload only
./tests/run_tests.sh integration # Test integration scenarios
./tests/run_tests.sh coverage    # Generate HTML coverage report
./tests/run_tests.sh failed      # Re-run only failed tests
./tests/run_tests.sh help        # Show help message
```

## Test Coverage

### Endpoints Tested

- ✅ **POST /api/contracts/** - Create contract
  - With/without source URL
  - Validation errors
  - All contract types
  
- ✅ **GET /api/contracts/** - List contracts
  - Empty database
  - Pagination (skip, limit)
  - Filter by vendor (exact, partial)
  - Filter by contract type
  - Combined filters

- ✅ **GET /api/contracts/{id}** - Get by ID
  - Success case
  - 404 for non-existent
  - 422 for invalid UUID
  
- ✅ **DELETE /api/contracts/{id}** - Delete contract
  - Success case
  - 404 for non-existent
  - Cascade deletion
  
- ✅ **POST /api/contracts/upload** - Upload file
  - PDF upload
  - TXT upload
  - Invalid file type rejection
  - File size validation

### Test Statistics

- **Total Test Cases**: 40+
- **Test Classes**: 6
- **Coverage Target**: >90%
- **Test Isolation**: Each test uses fresh in-memory database

## Test Database

Tests use an in-memory SQLite database for:
- **Speed**: Fast test execution
- **Isolation**: No pollution between tests
- **Simplicity**: No external database required

## Fixtures

### Database Fixtures
- `test_db` - Fresh database session for each test
- `client` - FastAPI TestClient with overridden dependencies

### Data Fixtures
- `sample_contract_data` - Contract with URL
- `sample_contract_no_url` - Contract without URL
- `create_test_contract` - Factory for creating test contracts
- `create_test_version` - Factory for creating test versions

### File Fixtures
- `sample_pdf_file` - Path to sample PDF
- `sample_txt_file` - Path to sample TXT

## Adding New Tests

1. Add test methods to appropriate test class in `contracts.test.py`
2. Use existing fixtures from `conftest.py`
3. Follow naming convention: `test_<action>_<scenario>`
4. Run tests to verify: `./tests/run_tests.sh quick`

## CI/CD Integration

Add to your CI pipeline:

```yaml
- name: Run Tests
  run: |
    cd backend
    source venv/bin/activate
    pytest tests/contracts.test.py -v --cov=routers.contracts --cov-report=xml
```
