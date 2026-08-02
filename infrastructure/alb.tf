resource "aws_lb" "gipc_frontend_alb" {
  name               = "gipc-frontend-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.gipc_frontend_sg.id]
  subnets            = [aws_subnet.gipc_subnet_public1_eu_west_2a.id, aws_subnet.gipc_subnet_public2_eu_west_2b.id]

  tags = merge(
    local.common_tags, {
      Name = "gipc_alb"
    }
  )

}

resource "aws_lb_target_group" "gipc_frontend_tg" {
  name     = "gipc-frontend-tg"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = aws_vpc.gipc_vpc.id
  target_type = "instance"

  health_check {
    path                = "/health"
    protocol            = "HTTP"
    healthy_threshold   = 3
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
  }

  tags = merge(
    local.common_tags, {
      Name = "gipc_frontend_tg"
    }
  )
}

resource "aws_lb_listener" "gipc_http_listener" {
  load_balancer_arn = aws_lb.gipc_frontend_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.gipc_frontend_tg.arn
  }
}

resource "aws_lb_listener" "gipc_https_listener" {
  load_balancer_arn = aws_lb.gipc_frontend_alb.arn
  port              = 443
  protocol          = "HTTPS"
  certificate_arn   = aws_acm_certificate.gipc_frontend_cert.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.gipc_frontend_tg.arn
  }
}

resource "aws_lb_target_group_attachment" "gipc_frontend_attachment" {
  target_group_arn = aws_lb_target_group.gipc_frontend_tg.arn
  target_id        = aws_instance.gipc_frontend_app.id
  port              = 8000
}