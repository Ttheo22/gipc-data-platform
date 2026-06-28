output "s3_bucket_name" {
  description = "S3 bucket name"
  value       = aws_s3_bucket.gipc_data.bucket
}

output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = aws_db_instance.gipc.endpoint
}

output "rds_db_name" {
  description = "RDS database name"
  value       = aws_db_instance.gipc.db_name
}

output "security_group_id" {
  description = "RDS security group ID"
  value       = aws_security_group.rds.id
}
