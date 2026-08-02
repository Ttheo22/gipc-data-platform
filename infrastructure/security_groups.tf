resource "aws_security_group" "gipc_lambda_sg" {
  name        = "gipc_lambda_sg"
  description = "handles etl lambda"
  vpc_id      = aws_vpc.gipc_vpc.id
  # no inbound rules ever for lambda

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    local.common_tags, {
      Name = "gipc_lambda_sg"
    }
  )
}

resource "aws_security_group" "gipc_bastion_sg" {
  name        = "gipc_bastion_sg"
  description = "security group for bastion instance"
  vpc_id      = aws_vpc.gipc_vpc.id

  #no inbound, ssm-only access

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    local.common_tags, {
      Name = "gipc_bastion_sg"
    }
  )
}

resource "aws_security_group" "gipc_frontend_sg" {
  name        = "gipc_frontend_sg"
  description = "security group attached to the alb"
  vpc_id      = aws_vpc.gipc_vpc.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    local.common_tags, {
      Name = "gipc_frontend_sg"
    }
  )
}

resource "aws_security_group" "gipc_frontend_ec2_sg" {
  name        = "gipc_frontend_ec2_sg"
  description = "attached to the frontend ec2"
  vpc_id      = aws_vpc.gipc_vpc.id

  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.gipc_frontend_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    local.common_tags, {
      Name = "gipc_frontend_ec2_sg"
    }
  )
}

resource "aws_security_group" "gipc_rds_sg" {
  name        = "gipc_rds_sg"
  description = "attached to rds_postgres"
  vpc_id      = aws_vpc.gipc_vpc.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.gipc_lambda_sg.id]

  }

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.gipc_bastion_sg.id]

  }

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.gipc_frontend_ec2_sg.id]

  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    local.common_tags, {
      Name = "gipc_rds_sg"
    }
  )
}
