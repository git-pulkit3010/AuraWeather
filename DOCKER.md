# Docker Setup Guide for AuraWeather

This guide will help you run AuraWeather using Docker, whether you're running it locally or deploying it.

## Prerequisites

- Docker installed on your system
- Docker Compose (optional, but recommended)

## Quick Start

### 1. Environment Setup

First, create your environment file:

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your API keys
nano .env  # or use your preferred editor
```

Add your OpenRouter API key to the `.env` file:
```
OPENROUTER_API_KEY=your_actual_api_key_here
```

### 2. Using Docker Compose (Recommended)

```bash
# Build and start the application
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

The application will be available at http://localhost:8000

### 3. Using Docker directly

```bash
# Build the image
docker build -t aura-weather .

# Run the container
docker run -p 8000:8000 --env-file .env aura-weather
```

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key | - | Yes |
| `OPENROUTER_MODEL` | AI model to use | `openai/gpt-3.5-turbo` | No |
| `PORT` | Server port | `8000` | No |
| `HOST` | Server host | `0.0.0.0` | No |

## API Endpoints

Once running, you can access:

- **Main Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## Development

For development with hot reload:

```bash
# Mount your code as a volume for development
docker run -p 8000:8000 \
  --env-file .env \
  -v $(pwd):/app \
  aura-weather
```

## Production Deployment

For production, consider:

1. **Using a reverse proxy** (nginx, traefik)
2. **Setting up SSL/TLS certificates**
3. **Using environment variables instead of .env files**
4. **Setting up logging and monitoring**

Example production docker-compose.yml:

```yaml
version: '3.8'
services:
  aura-weather:
    image: aura-weather:latest
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - OPENROUTER_MODEL=${OPENROUTER_MODEL:-openai/gpt-3.5-turbo}
    ports:
      - "8000:8000"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import httpx; httpx.get('http://localhost:8000/api/health', timeout=10)"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Troubleshooting

### Common Issues

1. **Port already in use**: Change the port mapping in docker-compose.yml or use `-p 8001:8000`
2. **API key not working**: Ensure your `.env` file is properly formatted and the key is valid
3. **Container won't start**: Check logs with `docker-compose logs` or `docker logs <container-name>`

### Health Check

Check if the application is running properly:

```bash
curl http://localhost:8000/api/health
```

### Viewing Logs

```bash
# Docker Compose
docker-compose logs -f

# Docker directly
docker logs -f <container-name>
```

## Security Notes

- Never commit your `.env` file to version control
- Use Docker secrets in production for sensitive data
- Run containers as non-root user (already configured)
- Keep your base images updated