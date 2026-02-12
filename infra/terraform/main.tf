provider "aiven" {
  api_token = var.aiven_api_token
}

# ── Aiven Dragonfly (managed Redis-compatible cache) ──────────────────
resource "aiven_dragonfly" "cache" {
  project      = var.aiven_project
  service_name = "jadecli-cache"
  cloud_name   = var.cloud_name
  plan         = var.dragonfly_plan

  maintenance_window_dow  = "sunday"
  maintenance_window_time = "06:00:00"

  dragonfly_user_config {
    cache_mode = true
  }

  tag {
    key   = "env"
    value = "development"
  }
  tag {
    key   = "team"
    value = "jadecli"
  }
  tag {
    key   = "managed-by"
    value = "opentofu"
  }
}
