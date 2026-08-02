data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "gipc_lambda_etl_role" {
  name               = "gipc_lambda_etl_role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json

  tags = merge(
    local.common_tags, {
      Name = "gipc_lambda_etl_role"
    }
  )
}

resource "aws_iam_role_policy" "gipc_lambda_etl_policy" {
  name   = "gipc_lambda_etl_policy"
  role   = aws_iam_role.gipc_lambda_etl_role.id
  policy = data.aws_iam_policy_document.lambda_policy.json
}

data "aws_iam_policy_document" "lambda_policy" {
  statement {
    effect    = "Allow"
    actions   = ["secretsmanager:GetSecretValue"]
    resources = [aws_secretsmanager_secret.gipc_db_credentials.arn]
  }

  statement {
    effect  = "Allow"
    actions = ["s3:GetObject", "s3:PutObject"]
    resources = [
      "${aws_s3_bucket.gipc_platform_raw_datagh26.arn}/*",
      "${aws_s3_bucket.gipc_platform_processed_datagh26.arn}/*",
    ]
  }
}

resource "aws_iam_role_policy_attachment" "gipc_lambda_vpc_access" {
  role       = aws_iam_role.gipc_lambda_etl_role.id
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

data "aws_iam_policy_document" "ec2_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "gipc_bastion_role" {
  name               = "gipc_bastion_role"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume_role.json

  tags = merge(
    local.common_tags, {
      Name = "gipc_bastion_role"
    }
  )
}

resource "aws_iam_role_policy_attachment" "gipc_bastion_ssm_access" {
  role       = aws_iam_role.gipc_bastion_role.id
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "gipc_bastion_profile" {
  name = "gipc_bastion_profile"
  role = aws_iam_role.gipc_bastion_role.name
}

data "aws_iam_policy_document" "gipc_frontend_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "gipc_frontend_role" {
  name               = "gipc_frontend_role"
  assume_role_policy = data.aws_iam_policy_document.gipc_frontend_role.json

  tags = merge(
    local.common_tags, {
      Name = "gipc_frontend_role"
    }
  )
}

resource "aws_iam_role_policy_attachment" "gipc_frontend_ssm_access" {
  role       = aws_iam_role.gipc_frontend_role.id
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "gipc_frontend_profile" {
  name = "gipc_frontend_profile"
  role = aws_iam_role.gipc_frontend_role.name
}

data "aws_iam_policy_document" "gipc_frontend_secrets_policy" {
  statement {
    effect    = "Allow"
    actions   = ["secretsmanager:GetSecretValue"]
    resources = [aws_secretsmanager_secret.gipc_db_credentials.arn]
  }
}

resource "aws_iam_role_policy" "gipc_frontend_secrets_access" {
  name   = "gipc_frontend_secrets_access"
  role   = aws_iam_role.gipc_frontend_role.id
  policy = data.aws_iam_policy_document.gipc_frontend_secrets_policy.json
}