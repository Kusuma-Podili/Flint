output "security_status" {
  value       = "healthy"
  description = "Status of security module in azure"
}

output "security_id" {
  value       = "${var.environment}-security-active"
  description = "Resource ID"
}
