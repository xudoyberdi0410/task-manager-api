# Local Development with Docker Services

This guide explains how to run databases and services in Docker while running your application code locally on your machine.

## Benefits of This Approach

- **Faster development**: No need to rebuild Docker images when changing code
- **Better debugging**: Direct access to your IDE's debugging tools
- **Hot reloading**: Instant code changes without container restart
- **Resource efficiency**: Only services run in containers

## Quick Start

### 1. Start Services Only

Run only the database services in Docker:

```bash
make services
# or manually:
# docker-compose -f docker-compose.services.yml up -d
```

This will start:
- PostgreSQL database on `localhost:5432`
- pgAdmin on `http://localhost:5050`

### 2. Install Dependencies Locally

Make sure you have Python dependencies installed locally:

```bash
uv sync
```

### 3. Run Application Locally

Run your FastAPI application directly on your machine:

```bash
uv run uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload
```

The application will connect to the Docker services using the configuration in `.env`:

```bash
DATABASE_URL=postgresql://postgres:password@localhost:5432/taskmanager
```

## Available Commands

```bash
make services        # Start only services (db, pgadmin)
make services-down   # Stop services
make services-logs   # View services logs
make dev-local       # Start services and show local run command
```

## Database Access

- **Application**: Uses `localhost:5432`
- **pgAdmin**: Access at `http://localhost:5050`
  - Email: `admin@admin.com`
  - Password: `admin`

## Switching Between Modes

### Full Docker Mode (Original)
```bash
make up  # Everything in Docker
```

### Hybrid Mode (Services in Docker, App Local)
```bash
make services  # Only services in Docker
uv run uvicorn src.app:app --reload  # App runs locally
```

### Fully Local (if you have local PostgreSQL)
```bash
# Update .env with local service URLs
DATABASE_URL=postgresql://postgres:password@localhost:5432/taskmanager
```

## Environment Variables

The application uses these key environment variables for connecting to services:

- `DATABASE_URL`: PostgreSQL connection string
- `ENVIRONMENT`: development/production

Check `.env` file for current configuration.

## Troubleshooting

### Port Conflicts
If you have local PostgreSQL running, you might see port conflicts:

```bash
# Change ports in docker-compose.services.yml
ports:
  - "5433:5432"  # PostgreSQL on different port
```

Then update your `.env`:
```bash
DATABASE_URL=postgresql://postgres:password@localhost:5433/taskmanager
```

### Connection Issues
Make sure Docker services are running:
```bash
docker-compose -f docker-compose.services.yml ps
```

Check service logs:
```bash
make services-logs
```
