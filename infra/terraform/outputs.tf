## ── Dragonfly (Aiven — TF-managed) ──────────────────────────────────
output "dragonfly_uri" {
  description = "Dragonfly connection URI (rediss://)"
  value       = aiven_dragonfly.cache.service_uri
  sensitive   = true
}

output "dragonfly_host" {
  description = "Dragonfly hostname"
  value       = aiven_dragonfly.cache.service_host
}

output "dragonfly_port" {
  description = "Dragonfly port"
  value       = aiven_dragonfly.cache.service_port
}

output "dragonfly_state" {
  description = "Service state (RUNNING when ready)"
  value       = aiven_dragonfly.cache.state
}
