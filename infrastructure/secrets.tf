resource "aws_secretsmanager_secret" "gipc_db_credentials" {
  name                    = "gipc/platform-db-credentials"
  description             = "Credentials for the GIPC platform database"
  recovery_window_in_days = 0

  tags = merge(
    local.common_tags, {
      Name = "gipc_platform_db_credentials"
    }
  )
}

resource "aws_secretsmanager_secret_version" "gipc_db_credentials-version" {
  secret_id = aws_secretsmanager_secret.gipc_db_credentials.id
  secret_string = jsonencode({
    username = "postgres"
    password = var.db_password
    host     = aws_db_instance.gipc-platform-db.address
    port     = aws_db_instance.gipc-platform-db.port
    dbname   = aws_db_instance.gipc-platform-db.db_name

  })
}