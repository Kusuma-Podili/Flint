output "database_status" {
  value       = "healthy"
  description = "Status of database module in aws"
}

output "database_id" {
  value       = "${var.environment}-database-active"
  description = "Resource ID"
}
