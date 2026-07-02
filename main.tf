terraform {
  required_version = ">=1.0"
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {
  host = "unix:///var/run/docker.sock"
}


resource "docker_network" "warden" {
  name   = "warden-network"
  driver = "bridge"
}


resource "docker_volume" "redis_data" {
  name = "redis-data"
}


resource "docker_image" "redis" {
  name         = "redis:alpine"
  keep_locally = true
}


resource "docker_image" "nginx" {
  name         = "nginx:alpine"
  keep_locally = true
}


resource "docker_image" "warden" {
  name = "warden:latest"
  build {
    context    = "."
    dockerfile = "Dockerfile"
  }
  keep_locally = true
}


resource "docker_container" "redis" {
  name    = "redis"
  image   = docker_image.redis.image_id
  restart = "unless-stopped"

  ports {
    internal = 6379
    external = 6379
  }

  volumes {
    volume_name    = docker_volume.redis_data.name
    container_path = "/data"
  }

  networks_advanced {
    name = docker_network.warden.name
  }

  healthcheck {
    test     = ["CMD", "redis-cli", "ping"]
    interval = "10s"
    timeout  = "5s"
    retries  = 3
  }
}


resource "docker_container" "proxy" {
  name    = "proxy"
  image   = docker_image.nginx.image_id
  restart = "unless-stopped"

  ports {
    internal = 80
    external = 80
  }

  ports {
    internal = 443
    external = 443
  }

  volumes {
    host_path      = abspath("warden/nginx/configs")
    container_path = "/etc/nginx/configs"
  }

  volumes {
    host_path      = abspath("warden/nginx/configs/nginx.conf")
    container_path = "/etc/nginx/nginx.conf"
  }

  networks_advanced {
    name = docker_network.warden.name
  }
}


resource "docker_container" "warden" {
  name    = "warden"
  image   = docker_image.warden.image_id
  restart = "unless-stopped"

  volumes {
    host_path      = "/var/run/docker.sock"
    container_path = "/var/run/docker.sock"
  }

  volumes {
    host_path      = abspath("warden/nginx/configs")
    container_path = "/etc/nginx/configs"
  }

  env = [
    "REGISTRY_TYPE=dockerhub",
    "REGISTRY_URL=repo.warden.com",
    "REGISTRY_USERNAME=admin",
    "REGISTRY_PASSWORD=admin123",
    "AUTOMATIC_DEPLOYMENT=true",
    "IMAGE_NAME=demo-app",
    "IMAGE_TAG=latest",
    "REDIS_DB=0",
    "PROXY_CONTAINER_NAME=proxy",
    "PROXY_CONTAINER_TYPE=nginx",
    "UPSTREAM_CONFIG=/etc/nginx/configs/upstream.conf",
    "APP_NAME=demo-app",
    "APP_TYPE=nextjs",
  ]

  networks_advanced {
    name = docker_network.warden.name
  }
}
