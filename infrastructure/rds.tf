resource "aws_db_subnet_group" "gipc_db_subnet_group" {
  name = "gipc_db_subnet_group"

  subnet_ids = [
    aws_subnet.gipc_subnet_private1_eu_west_2a.id,
    aws_subnet.gipc_subnet_private2_eu_west_2b.id
  ]

  tags = merge(
    local.common_tags, {
      Name = "gipc_db_subnet_group"
    }
  )
}

resource "aws_db_instance" "gipc-platform-db" {
  identifier = "gipc-platform-db"

  engine         = "postgres"
  engine_version = "17"

  instance_class    = "db.t3.micro"
  allocated_storage = 20
  storage_type      = "gp2"

  db_name  = "gipc_platform"
  username = "postgres"
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.gipc_db_subnet_group.name
  vpc_security_group_ids = [aws_security_group.gipc_rds_sg.id]

  multi_az            = false
  publicly_accessible = false
  skip_final_snapshot = true #because this isn't prod. we're just learning


  tags = merge(
    local.common_tags, {
      Name = "gipc_platform_db"
    }
  )

}