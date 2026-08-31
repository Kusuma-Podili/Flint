output "governance_status" {
  value       = "healthy"
  description = "Status of governance module in aws"
}

output "governance_id" {
  value       = "${var.environment}-governance-active"
  description = "Resource ID"
}
