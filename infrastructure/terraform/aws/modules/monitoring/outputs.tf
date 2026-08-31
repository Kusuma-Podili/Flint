output "monitoring_status" {
  value       = "healthy"
  description = "Status of monitoring module in aws"
}

output "monitoring_id" {
  value       = "${var.environment}-monitoring-active"
  description = "Resource ID"
}
