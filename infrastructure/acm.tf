resource "tls_private_key" "gipc_acm_private_key" {
  algorithm = "RSA"
  rsa_bits  = 2048

}

resource "tls_self_signed_cert" "gipc_acm_cert" {
  private_key_pem = tls_private_key.gipc_acm_private_key.private_key_pem

  subject {
    common_name  = "gipc.example.com"
    organization = "GIPC"
  }

  validity_period_hours = 8760
  early_renewal_hours   = 168

  allowed_uses = [
    "key_encipherment",
    "digital_signature",
    "server_auth",
  ]
}

resource "aws_acm_certificate" "gipc_frontend_cert" {
  private_key      = tls_private_key.gipc_acm_private_key.private_key_pem
  certificate_body = tls_self_signed_cert.gipc_acm_cert.cert_pem

  tags = merge(
    local.common_tags, {
      Name = "gipc_frontend_cert"
    }
  )

  lifecycle {
    create_before_destroy = true
  }
}