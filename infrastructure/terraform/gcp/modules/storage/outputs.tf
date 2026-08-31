output "storage_status" {
  value       = "healthy"
  description = "Status of storage module in gcp"
}

output "storage_id" {
  value       = "${var.environment}-storage-active"
  description = "Resource ID"
}
