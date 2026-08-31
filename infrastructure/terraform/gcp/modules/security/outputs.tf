output "security_status" {
  value       = "healthy"
  description = "Status of security module in gcp"
}

output "security_id" {
  value       = "${var.environment}-security-active"
  description = "Resource ID"
}
