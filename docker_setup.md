# Docker Setup

## Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

## Start MongoDB

```bash
docker run -d --name imdb-mongo -p 27017:27017 mongo:latest
```

MongoDB will be available at `localhost:27017`.

## Stopping and Starting

```bash
docker stop imdb-mongo   # stop the container
docker start imdb-mongo  # start it again later
```

## Check if Running 
```bash
docker ps
```

