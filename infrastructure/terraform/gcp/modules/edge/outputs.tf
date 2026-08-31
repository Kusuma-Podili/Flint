output "edge_status" {
  value       = "healthy"
  description = "Status of edge module in gcp"
}

output "edge_id" {
  value       = "${var.environment}-edge-active"
  description = "Resource ID"
}
