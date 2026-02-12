## ── Aiven ───────────────────────────────────────────────────────────
variable "aiven_api_token" {
  description = "Aiven API token (from console > User Info > Tokens)"
  type        = string
  sensitive   = true
}

variable "aiven_project" {
  description = "Aiven project name"
  type        = string
  default     = "jadecli-ai"
}

variable "cloud_name" {
  description = "Aiven cloud region"
  type        = string
  default     = "google-us-west1"
}

variable "dragonfly_plan" {
  description = "Dragonfly service plan"
  type        = string
  default     = "startup-4"
}


