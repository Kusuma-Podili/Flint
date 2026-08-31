output "compute_status" {
  value       = "healthy"
  description = "Status of compute module in gcp"
}

output "compute_id" {
  value       = "${var.environment}-compute-active"
  description = "Resource ID"
}
