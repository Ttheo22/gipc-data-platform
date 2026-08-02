resource "aws_sqs_queue" "gipc_etl_dlq" {
  name = "gipc-etl-dlq"

  tags = merge(
    local.common_tags, {
      Name = "gipc_etl_dlq"
    }
  )
}

data "aws_iam_policy_document" "scheduler_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["scheduler.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "gipc_scheduler_role" {
  name               = "gipc_scheduler_role"
  assume_role_policy = data.aws_iam_policy_document.scheduler_assume_role.json

  tags = merge(
    local.common_tags, {
      Name = "gipc_scheduler_role"
    }
  )
}

data "aws_iam_policy_document" "scheduler_policy" {
  statement {
    effect    = "Allow"
    actions   = ["lambda:InvokeFunction"]
    resources = [aws_lambda_function.gipc_etl_pipeline.arn]
  }

  statement {
    effect    = "Allow"
    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.gipc_etl_dlq.arn]
  }
}

resource "aws_iam_role_policy" "gipc_scheduler_policy_attachment" {
  name   = "gipc_scheduler_policy"
  role   = aws_iam_role.gipc_scheduler_role.id
  policy = data.aws_iam_policy_document.scheduler_policy.json
}

resource "aws_scheduler_schedule" "gipc_etl_monthly_trigger" {
  name = "gipc-etl-monthly-trigger"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(0 6 1 * ? *)" # Run at 6am on the first day of every month

  target {

    arn      = aws_lambda_function.gipc_etl_pipeline.arn
    role_arn = aws_iam_role.gipc_scheduler_role.arn

    retry_policy {
      maximum_event_age_in_seconds = 86400
      maximum_retry_attempts       = 2
    }

    dead_letter_config {
      arn = aws_sqs_queue.gipc_etl_dlq.arn
    }
  }
}