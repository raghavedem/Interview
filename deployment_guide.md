# React + FastAPI Deployment Roadmap for Senior Full Stack Engineers

## Goal

Build, containerize, deploy, and maintain a production-ready React + FastAPI application.

Target Stack:

* React + TypeScript
* FastAPI
* PostgreSQL
* Docker
* AWS EC2
* Nginx
* HTTPS
* GitHub Actions (CI/CD)

---

# Architecture

```text
Internet
    │
    ▼
Nginx (Reverse Proxy)
    │
    ├── React Frontend
    │
    └── FastAPI Backend
            │
            ▼
        PostgreSQL
```

---

# Project Structure

```text
project/
│
├── frontend/
│   ├── src/
│   ├── package.json
│   └── Dockerfile
│
├── backend/
│   ├── app/
│   ├── requirements.txt
│   └── Dockerfile
│
└── docker-compose.yml
```

---

# Step 1: Dockerize FastAPI

## Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Build

```bash
docker build -t fastapi-app .
```

## Run

```bash
docker run -p 8000:8000 fastapi-app
```

## Verify

```bash
http://localhost:8000/docs
```

---

# Step 2: Dockerize React

## Dockerfile

```dockerfile
FROM node:20

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

RUN npm run build

RUN npm install -g serve

CMD ["serve", "-s", "build", "-l", "3000"]
```

## Build

```bash
docker build -t react-app .
```

## Run

```bash
docker run -p 3000:3000 react-app
```

## Verify

```bash
http://localhost:3000
```

---

# Step 3: Docker Compose

Create docker-compose.yml

```yaml
version: "3.9"

services:

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"

  backend:
    build: ./backend
    ports:
      - "8000:8000"

  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password
      POSTGRES_DB: appdb
    ports:
      - "5432:5432"
```

## Run

```bash
docker compose up
```

---

# Step 4: Create AWS EC2 Instance

## Recommended Configuration

* Ubuntu 24.04
* t3.micro
* Security Group:

```text
22   SSH
80   HTTP
443  HTTPS
```

## Connect

```bash
ssh -i key.pem ubuntu@<public-ip>
```

---

# Step 5: Install Docker on EC2

```bash
sudo apt update

sudo apt install docker.io -y

sudo systemctl start docker

sudo systemctl enable docker
```

Verify:

```bash
docker --version
```

---

# Step 6: Install Docker Compose

```bash
sudo apt install docker-compose -y
```

Verify:

```bash
docker-compose --version
```

---

# Step 7: Deploy Application

Clone project:

```bash
git clone <repo-url>

cd project
```

Start services:

```bash
docker compose up -d
```

Verify:

```bash
docker ps
```

---

# Step 8: Install Nginx

```bash
sudo apt install nginx -y
```

Verify:

```bash
systemctl status nginx
```

---

# Step 9: Configure Nginx

Example configuration:

```nginx
server {

    listen 80;

    location / {
        proxy_pass http://localhost:3000;
    }

    location /api {
        proxy_pass http://localhost:8000;
    }
}
```

Restart:

```bash
sudo systemctl restart nginx
```

---

# Step 10: Enable HTTPS

Install Certbot:

```bash
sudo apt install certbot python3-certbot-nginx -y
```

Generate certificate:

```bash
sudo certbot --nginx
```

Verify:

```text
https://your-domain.com
```

---

# Step 11: CI/CD Using GitHub Actions

Folder:

```text
.github/workflows/
```

Create:

```text
deploy.yml
```

Pipeline:

```text
Push Code
    ↓
Build Docker Image
    ↓
Deploy to EC2
    ↓
Restart Containers
```

---

# Bonus Improvements

## Add Redis

Use Redis for:

* Session caching
* API caching
* Background jobs

Docker:

```yaml
redis:
  image: redis:latest
```

---

## Add Monitoring

Tools:

* Prometheus
* Grafana

Track:

* CPU
* Memory
* Request latency
* Error rate

---

## Add Logging

Use:

```python
logging
```

or

```python
loguru
```

Store logs centrally.

---

# Interview Questions

## Why Docker?

Consistent environments across local, QA, and production.

---

## Why Nginx?

* Reverse proxy
* SSL termination
* Load balancing
* Static content serving

---

## Why EC2?

Provides complete control over infrastructure and deployment.

---

## How Would You Scale FastAPI?

* Multiple FastAPI instances
* Load balancer
* Redis cache
* PostgreSQL optimization
* Background workers

---

## How Would You Handle 1 Million Users?

* CDN for frontend
* Load balancers
* Auto scaling
* Redis caching
* Database replicas
* Queue systems (Kafka/RabbitMQ)

---

# Final Target Project

Tech Stack:

* React
* TypeScript
* FastAPI
* PostgreSQL
* Redis
* Docker
* AWS EC2
* Nginx
* HTTPS
* GitHub Actions

Completing this project will give enough practical deployment experience to confidently discuss infrastructure, deployment, scaling, and production readiness during senior-level interviews.
