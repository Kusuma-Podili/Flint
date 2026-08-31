variable "environment" {
  type        = string
  description = "Deployment environment (production, staging, qa)"
  default     = "production"
}

variable "region" {
  type        = string
  description = "Target cloud region"
  default     = "us-east-1"
}

variable "enable_ha" {
  type        = bool
  description = "Enable High Availability Multi-AZ deployment"
  default     = true
}

variable "tags" {
  type        = map(string)
  description = "Additional resource tags"
  default     = {}
}
