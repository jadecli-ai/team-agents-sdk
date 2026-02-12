# ── Config-Only Services (created manually, not Terraform-managed) ───
#
# These services were provisioned via their respective dashboards.
# Variable blocks pass values through tfvars for reference outputs.
#
# Sentry:         sentry.io         -> Project DSN
# Upstash:        console.upstash.com -> Redis connection
# Langfuse:       cloud.langfuse.com -> API Keys
# Snyk:           snyk auth
# Dragonfly Cloud: dragonflydb.cloud
# Redis Cloud:    redis.io/try-free

## ── Neon (Postgres — managed via console + neonctl) ─────────────────
variable "neon_connection_uri" {
  description = "Neon Postgres connection URI (from neonctl connection-string)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "neon_project_id" {
  description = "Neon project ID"
  type        = string
  default     = "damp-star-47314338"
}

## ── Sentry (error tracking — created manually) ──────────────────────
variable "sentry_dsn" {
  description = "Sentry DSN from project settings (sentry.io > Project > Client Keys)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "sentry_project_slug" {
  description = "Sentry project slug"
  type        = string
  default     = "jadecli-ai"
}

## ── Upstash (serverless Redis — created manually) ───────────────────
variable "upstash_redis_url" {
  description = "Upstash Redis connection URL (rediss://...)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "upstash_endpoint" {
  description = "Upstash Redis endpoint hostname"
  type        = string
  default     = ""
}

## ── Langfuse (LLM observability) ────────────────────────────────────
variable "langfuse_public_key" {
  description = "Langfuse public key (cloud.langfuse.com > Settings > API Keys)"
  type        = string
  default     = ""
}

variable "langfuse_secret_key" {
  description = "Langfuse secret key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "langfuse_host" {
  description = "Langfuse host URL"
  type        = string
  default     = "https://cloud.langfuse.com"
}

## ── Snyk (security scanning) ────────────────────────────────────────
variable "snyk_token" {
  description = "Snyk auth token (snyk.io > Account Settings > API Token)"
  type        = string
  sensitive   = true
  default     = ""
}

## ── Dragonfly Cloud (managed cache) ─────────────────────────────────
variable "dragonfly_cloud_url" {
  description = "Dragonfly Cloud connection string (dragonflydb.cloud)"
  type        = string
  sensitive   = true
  default     = ""
}

## ── Redis Cloud (managed cache) ─────────────────────────────────────
variable "redis_cloud_url" {
  description = "Redis Cloud connection string (redis.io/try-free)"
  type        = string
  sensitive   = true
  default     = ""
}

## ── Config-only outputs (pass-through for reference) ────────────────
output "sentry_dsn" {
  description = "Sentry DSN for Python SDK"
  value       = var.sentry_dsn
  sensitive   = true
}

output "sentry_project_slug" {
  description = "Sentry project slug"
  value       = var.sentry_project_slug
}

output "upstash_redis_url" {
  description = "Upstash Redis connection URL"
  value       = var.upstash_redis_url
  sensitive   = true
}

output "upstash_endpoint" {
  description = "Upstash Redis endpoint"
  value       = var.upstash_endpoint
}

output "neon_project_id" {
  description = "Neon project ID"
  value       = var.neon_project_id
}

output "neon_connection_uri" {
  description = "Neon Postgres connection URI"
  value       = var.neon_connection_uri
  sensitive   = true
}

output "langfuse_host" {
  description = "Langfuse host URL"
  value       = var.langfuse_host
}

output "langfuse_configured" {
  description = "Whether Langfuse keys are set"
  value       = var.langfuse_public_key != ""
}

output "snyk_configured" {
  description = "Whether Snyk token is set"
  value       = var.snyk_token != ""
  sensitive   = true
}
