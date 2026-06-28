variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "eu-west-1"
}

variable "project_name" {
  description = "Project name used for naming resources"
  type        = string
  default     = "gipc-data-platform"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "prod"
}

variable "db_password" {
  description = "Master password for RDS PostgreSQL"
  type        = string
  sensitive   = true
}

variable "db_username" {
  description = "Master username for RDS PostgreSQL"
  type        = string
  default     = "postgres"
}

variable "allowed_cidr" {
  description = "Your IP address for RDS access"
  type        = string
}
