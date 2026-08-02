resource "aws_s3_bucket" "gipc_platform_raw_datagh26" {
  bucket        = "gipc-platform-raw-datagh26"
  force_destroy = true

  tags = merge(
    local.common_tags, {
      Name = "gipc_platform_raw_datagh26"
    }
  )
}



resource "aws_s3_bucket" "gipc_platform_processed_datagh26" {
  bucket        = "gipc-platform-processed-datagh26"
  force_destroy = true

  tags = merge(
    local.common_tags, {
      Name = "gipc_platform_processed_datagh26"
    }
  )
}

