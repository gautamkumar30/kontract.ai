# Makefile Quick Reference

## Most Common Commands

```bash
# First time setup
make quickstart          # Complete setup and start everything

# Daily development
make up                  # Start all services
make down                # Stop all services
make logs                # View all logs
make dev                 # Start dev environment with migrations

# Database
make db-migrate          # Run migrations
make db-shell            # Open database shell
make db-reset            # Reset database (WARNING: destroys data)

# Testing
make test                # Run all tests
make lint                # Lint all code
make format              # Format all code

# Monitoring
make status              # Show service status
make health              # Check health of all services
make logs-backend        # View backend logs only
make logs-frontend       # View frontend logs only
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
make down
make clean-docker        # WARNING: Removes all Docker data
make quickstart
```

### View Logs
```bash
make logs                # All services
make logs-backend        # Backend only
make logs-frontend       # Frontend only
make logs-db             # Database only
```

### Database Issues
```bash
make db-reset            # Reset database
make db-shell            # Open PostgreSQL shell
```

## Full Command List

Run `make help` to see all available commands organized by category.
