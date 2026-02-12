# ── Docker (local dev containers) ────────────────────────────────────
provider "docker" {
  host = "unix:///var/run/docker.sock"
}

# Qdrant vector DB (local dev — pgvector replaces this in prod)
resource "docker_image" "qdrant" {
  name = "qdrant/qdrant:latest"
}

resource "docker_container" "qdrant" {
  name  = "qdrant-dev"
  image = docker_image.qdrant.image_id
  ports {
    internal = 6333
    external = 6333
  }
  ports {
    internal = 6334
    external = 6334
  }
  restart = "unless-stopped"
}
