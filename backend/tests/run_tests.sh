#!/bin/bash
# Test execution scripts for easy testing

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Contract Router Test Suite${NC}\n"

# Function to run tests
run_test() {
    local test_name=$1
    local test_command=$2
    
    echo -e "${YELLOW}Running: ${test_name}${NC}"
    eval "$test_command"
    echo ""
}

# Check if we're in the backend directory
if [ ! -f "main.py" ]; then
    echo "Error: Please run this script from the backend directory"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

case "${1:-all}" in
    "all")
        echo -e "${GREEN}Running all tests with coverage${NC}\n"
        pytest tests/test_contracts.py -v --cov=routers.contracts --cov-report=term-missing
        ;;
    
    "quick")
        echo -e "${GREEN}Running quick tests (no coverage)${NC}\n"
        pytest tests/test_contracts.py -v
        ;;
    
    "create")
        echo -e "${GREEN}Testing contract creation${NC}\n"
        pytest tests/test_contracts.py::TestCreateContract -v
        ;;
    
    "list")
        echo -e "${GREEN}Testing contract listing${NC}\n"
        pytest tests/test_contracts.py::TestListContracts -v
        ;;
    
    "get")
        echo -e "${GREEN}Testing get contract by ID${NC}\n"
        pytest tests/test_contracts.py::TestGetContractById -v
        ;;
    
    "delete")
        echo -e "${GREEN}Testing contract deletion${NC}\n"
        pytest tests/test_contracts.py::TestDeleteContract -v
        ;;
    
    "upload")
        echo -e "${GREEN}Testing file upload${NC}\n"
        pytest tests/test_contracts.py::TestUploadContract -v
        ;;
    
    "integration")
        echo -e "${GREEN}Testing integration scenarios${NC}\n"
        pytest tests/test_contracts.py::TestContractIntegration -v
        ;;
    
    "coverage")
        echo -e "${GREEN}Running tests with HTML coverage report${NC}\n"
        pytest tests/test_contracts.py --cov=routers.contracts --cov-report=html
        echo -e "\n${GREEN}Coverage report generated at: htmlcov/index.html${NC}"
        ;;
    
    "watch")
        echo -e "${GREEN}Running tests in watch mode${NC}\n"
        pytest-watch tests/test_contracts.py -v
        ;;
    
    "failed")
        echo -e "${GREEN}Re-running only failed tests${NC}\n"
        pytest tests/test_contracts.py --lf -v
        ;;
    
    "help")
        echo "Usage: ./run_tests.sh [option]"
        echo ""
        echo "Options:"
        echo "  all         - Run all tests with coverage (default)"
        echo "  quick       - Run all tests without coverage"
        echo "  create      - Test contract creation only"
        echo "  list        - Test contract listing only"
        echo "  get         - Test get by ID only"
        echo "  delete      - Test deletion only"
        echo "  upload      - Test file upload only"
        echo "  integration - Test integration scenarios only"
        echo "  coverage    - Generate HTML coverage report"
        echo "  watch       - Run tests in watch mode"
        echo "  failed      - Re-run only failed tests"
        echo "  help        - Show this help message"
        ;;
    
    *)
        echo "Unknown option: $1"
        echo "Run './run_tests.sh help' for usage information"
        exit 1
        ;;
esac
