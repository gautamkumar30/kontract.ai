# Makefile Quick Reference

## Most Common Commands

```bash
# First time setup
make quickstart          # Complete setup and start everything

# Daily development
make docker-up           # Start Docker services (DB + n8n)
make docker-down         # Stop Docker services
make docker-logs         # View Docker logs
make dev-backend         # Start backend (local)
make dev-frontend        # Start frontend (local)
make dev                 # Start Docker services + run migrations

# Database
make db-migrate          # Run migrations
make db-shell            # Open database shell
make db-reset            # Reset database (WARNING: destroys data)

# Testing
make test                # Run all tests
make lint                # Lint all code
make format              # Format all code

# Monitoring
make docker-status       # Show Docker service status
make health              # Check health of all services
# Note: Backend/Frontend logs are visible in their respective terminals.
```

## Service URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **n8n**: http://localhost:5678 (admin/admin123)
- **Database**: localhost:5432

## Development Workflow

### Starting Development
```bash
make dev                 # Start all services + run migrations
```

### Making Database Changes
```bash
# 1. Modify models in backend/models.py
# 2. Create migration
make db-migrate-create MSG="add new field"
# 3. Apply migration
make db-migrate
```

### Running Tests
```bash
make test                # All tests
make test-backend        # Backend only
make test-frontend       # Frontend only
make test-coverage       # With coverage report
```

### Code Quality
```bash
make lint                # Check code style
make format              # Auto-format code
```

## Troubleshooting

### Reset Everything
```bash
make docker-down
make clean-docker        # WARNING: Removes all Docker data
make quickstart
```

### View Logs
```bash
make docker-logs         # All Docker services
make docker-logs-db      # Database only
make docker-logs-n8n     # n8n only
# Note: Backend/Frontend logs are visible in their respective terminals.
```

### Database Issues
```bash
make db-reset            # Reset database
make db-shell            # Open PostgreSQL shell
```

## Full Command List

Run `make help` to see all available commands organized by category.
