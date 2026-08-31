output "database_status" {
  value       = "healthy"
  description = "Status of database module in azure"
}

output "database_id" {
  value       = "${var.environment}-database-active"
  description = "Resource ID"
}
