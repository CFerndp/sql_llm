# Docker Setup Guide

This guide explains how to run the Testing Blade SQL Agent using Docker.

## Prerequisites

- Docker and Docker Compose installed on your system
- OpenAI API key (required for LLM functionality)

## Quick Start

### 1. Set up environment variables

Create a `.env` file in the project root with your OpenAI API key:

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Build and start the container in detached mode

```bash
# Build and start the container in detached mode
docker-compose up -d --build
```

### 3. Connect to the container and run the SQL Agent

```bash
# Connect to the running container
docker-compose exec sql-agent bash

# Inside the container, run the SQL agent
python testing_blade.py
```

## Manual Docker Commands

### Build the image

```bash
docker build -t testing-blade-sql-agent .
```

### Run the container

```bash
# Run in detached mode
docker run -d --name sql-agent \
  -e OPENAI_API_KEY="your_api_key_here" \
  -v $(pwd)/Chinook.db:/app/Chinook.db \
  testing-blade-sql-agent

# Connect to the running container
docker exec -it sql-agent bash

# Inside the container, run the SQL agent
python testing_blade.py

# With custom environment variables
docker run -d --name sql-agent \
  -e OPENAI_API_KEY="your_api_key_here" \
  -e DEBUG_MODE=true \
  -e BATCH_MODE=true \
  -v $(pwd)/Chinook.db:/app/Chinook.db \
  testing-blade-sql-agent
```

## Configuration

### Environment Variables

The following environment variables can be configured:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | **Required**: Your OpenAI API key |
| `DATABASE_URI` | `sqlite:///Chinook.db` | Database connection string |
| `DATABASE_TYPE` | `SQLite` | Database type for prompts |
| `LLM_MODEL` | `gpt-4o-mini` | OpenAI model to use |
| `LLM_PROVIDER` | `openai` | LLM provider |
| `DEBUG_MODE` | `false` | Show SQL queries in output |
| `BATCH_MODE` | `true` | Enable batch execution mode |
| `RECURSION_LIMIT` | `50` | Agent recursion limit |
| `TOP_K_RESULTS` | `5` | Max results per query |

### Using PostgreSQL

To use PostgreSQL instead of SQLite:

1. Uncomment the PostgreSQL service in `docker-compose.yml`
2. Update the environment variables:
   ```yaml
   environment:
     - DATABASE_URI=postgresql://postgres:postgres@postgres:5432/chinook
     - DATABASE_TYPE=PostgreSQL
   ```

## Volumes

The Docker setup includes these volume mounts:

- `./Chinook.db:/app/Chinook.db` - SQLite database file
- `./logs:/app/logs` - Application logs (create this directory if needed)

## Networking

The containers use a custom bridge network `sql-agent-network` for internal communication.

## Health Checks

Both services include health checks:
- **sql-agent**: Validates Python environment
- **postgres**: Checks database connectivity

## Troubleshooting

### Container won't start

1. Check if the OpenAI API key is set correctly
2. Ensure the Chinook.db file exists and is readable
3. Check Docker logs: `docker-compose logs sql-agent`

### Permission issues

If you encounter permission issues with the database file:

```bash
# Fix file permissions
chmod 666 Chinook.db
```

### Memory issues

If the container runs out of memory:

```bash
# Add memory limits to docker-compose.yml
services:
  sql-agent:
    deploy:
      resources:
        limits:
          memory: 2G
```

## Development

### Rebuilding after code changes

```bash
# Stop the current container
docker-compose down

# Rebuild and restart in detached mode
docker-compose up -d --build

# Connect to the new container
docker-compose exec sql-agent bash
```

### Debugging

```bash
# Start container with debug mode enabled
docker-compose up -d
docker-compose exec -e DEBUG_MODE=true sql-agent bash

# Or modify docker-compose.yml to set DEBUG_MODE=true, then:
docker-compose up -d --build

# Inside the container, run with debug mode
python testing_blade.py
```

## Container Management

### Starting and stopping

```bash
# Start the container
docker-compose up -d

# Stop the container
docker-compose down

# Restart the container
docker-compose restart

# View container status
docker-compose ps

# View container logs
docker-compose logs sql-agent
```

### Multiple sessions

You can connect multiple terminal sessions to the same container:

```bash
# Terminal 1
docker-compose exec sql-agent bash
python testing_blade.py

# Terminal 2 (in another terminal window)
docker-compose exec sql-agent bash
# You can run other commands, check logs, etc.
```

## Configuration

### Environment Variables

The following environment variables can be configured:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | **Required**: Your OpenAI API key |
| `DATABASE_URI` | `sqlite:///Chinook.db` | Database connection string |
| `DATABASE_TYPE` | `SQLite` | Database type for prompts |
| `LLM_MODEL` | `gpt-4o-mini` | OpenAI model to use |
| `LLM_PROVIDER` | `openai` | LLM provider |
| `DEBUG_MODE` | `false` | Show SQL queries in output |
| `BATCH_MODE` | `true` | Enable batch execution mode |
| `RECURSION_LIMIT` | `50` | Agent recursion limit |
| `TOP_K_RESULTS` | `5` | Max results per query |

## Production Deployment

For production deployment:

1. Use environment-specific configuration
2. Set up proper logging and monitoring
3. Configure resource limits
4. Use secrets management for API keys
5. Set up backup strategies for the database

Example production docker-compose override:

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  sql-agent:
    restart: always
    environment:
      - DEBUG_MODE=false
      - BATCH_MODE=true
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

Run with: 
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
docker-compose exec sql-agent bash
python testing_blade.py
```
