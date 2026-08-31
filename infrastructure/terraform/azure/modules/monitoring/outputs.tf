output "monitoring_status" {
  value       = "healthy"
  description = "Status of monitoring module in azure"
}

output "monitoring_id" {
  value       = "${var.environment}-monitoring-active"
  description = "Resource ID"
}
