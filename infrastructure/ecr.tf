resource "aws_ecr_repository" "gipc_etl_lambda" {
  name                 = "gipc-etl-lambda"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  tags = merge(
    local.common_tags, {
      Name = "gipc_etl_lambda"
    }
  )
}

resource "null_resource" "docker_build_push" {
  depends_on = [aws_ecr_repository.gipc_etl_lambda]

  triggers = {
    dockerfile_hash = filemd5("${path.module}/../Dockerfile")
    handler_hash    = filemd5("${path.module}/../handler.py")
  }

  provisioner "local-exec" {
    working_dir = "${path.module}/.."
    interpreter = ["PowerShell", "-Command"]
    command     = <<-EOT
  $token = aws ecr get-login-password --region eu-west-2
  docker login --username AWS --password $token ${split("/", aws_ecr_repository.gipc_etl_lambda.repository_url)[0]}
  docker build --provenance=false --sbom=false -t gipc-etl-lambda .
  docker tag gipc-etl-lambda:latest ${aws_ecr_repository.gipc_etl_lambda.repository_url}:latest
  docker push ${aws_ecr_repository.gipc_etl_lambda.repository_url}:latest
EOT
  }
}


resource "aws_lambda_function" "gipc_etl_pipeline" {
  function_name = "gipc-etl-pipeline"
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.gipc_etl_lambda.repository_url}:latest"

  role = aws_iam_role.gipc_lambda_etl_role.arn

  timeout     = 600
  memory_size = 1024

  vpc_config {
    subnet_ids         = [aws_subnet.gipc_subnet_private1_eu_west_2a.id, aws_subnet.gipc_subnet_private2_eu_west_2b.id]
    security_group_ids = [aws_security_group.gipc_lambda_sg.id]
  }

  depends_on = [null_resource.docker_build_push]

  tags = merge(
    local.common_tags, {
      Name = "gipc_etl_pipeline"
    }
  )
}