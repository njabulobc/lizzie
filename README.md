# Fraud Detection Project

This repository contains a Django-based fraud detection project. The application can now be run inside Docker for a consistent development environment.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2 or later)

## Running the application

1. Build the Docker image and start the service:

   ```bash
   docker compose up --build
   ```

2. Visit the application at [http://localhost:8000](http://localhost:8000).

   The entrypoint automatically applies database migrations before the server starts. The default command runs Django's development server which reloads when files change (thanks to the mounted volume).

## Management commands

To run Django management commands inside the container, use `docker compose run` (for one-off commands) or `docker compose exec` (for commands against a running container). Examples:

```bash
# Run a custom command without starting the web server
docker compose run --rm web python manage.py createsuperuser

# Open a shell inside the running container
docker compose exec web /bin/sh
```

## Testing the image build

You can verify that the Docker image builds successfully without starting the service:

```bash
docker build -t fraud-detection:latest .
```

This command uses the Dockerfile to install Python dependencies and prepares the containerized environment.
