output "security_status" {
  value       = "healthy"
  description = "Status of security module in aws"
}

output "security_id" {
  value       = "${var.environment}-security-active"
  description = "Resource ID"
}
