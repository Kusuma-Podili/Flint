output "networking_status" {
  value       = "healthy"
  description = "Status of networking module in aws"
}

output "networking_id" {
  value       = "${var.environment}-networking-active"
  description = "Resource ID"
}
