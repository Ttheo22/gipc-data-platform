# ── Provider ──────────────────────────────────────────────
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# ── S3 Bucket ─────────────────────────────────────────────
resource "aws_s3_bucket" "gipc_data" {
  bucket = "${var.project_name}-theo2026"

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "gipc_data" {
  bucket = aws_s3_bucket.gipc_data.id
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 folder structure via empty objects
resource "aws_s3_object" "folders" {
  for_each = toset([
    "raw/world_bank/",
    "raw/imf/",
    "processed/economic_indicators/",
    "manual_uploads/gss/",
    "manual_uploads/bog/",
    "manual_uploads/mof/",
    "manual_uploads/gipc/",
  ])

  bucket  = aws_s3_bucket.gipc_data.id
  key     = each.value
  content = ""
}

# ── VPC & Security Group ───────────────────────────────────
data "aws_vpc" "default" {
  default = true
}

resource "aws_security_group" "rds" {
  name        = "${var.project_name}-rds-sg"
  description = "Allow PostgreSQL access for GIPC data platform"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [var.allowed_cidr]
    description = "PostgreSQL access from allowed IP"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound"
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# ── RDS PostgreSQL ─────────────────────────────────────────
resource "aws_db_instance" "gipc" {
  identifier              = "${var.project_name}-db"
  engine                  = "postgres"
  engine_version          = "18"
  instance_class          = "db.t3.micro"
  allocated_storage       = 20
  db_name                 = "gipc_platform"
  username                = var.db_username
  password                = var.db_password
  vpc_security_group_ids  = [aws_security_group.rds.id]
  publicly_accessible     = true
  skip_final_snapshot     = true
  backup_retention_period = 1

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}
