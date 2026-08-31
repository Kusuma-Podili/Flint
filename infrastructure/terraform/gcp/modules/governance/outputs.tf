output "governance_status" {
  value       = "healthy"
  description = "Status of governance module in gcp"
}

output "governance_id" {
  value       = "${var.environment}-governance-active"
  description = "Resource ID"
}
