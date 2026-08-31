output "networking_status" {
  value       = "healthy"
  description = "Status of networking module in gcp"
}

output "networking_id" {
  value       = "${var.environment}-networking-active"
  description = "Resource ID"
}
