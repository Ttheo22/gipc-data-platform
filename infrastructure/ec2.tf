data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

resource "aws_instance" "gipc_frontend_app" {
  ami                    = data.aws_ami.amazon_linux_2023.id
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.gipc_subnet_private1_eu_west_2a.id
  vpc_security_group_ids = [aws_security_group.gipc_frontend_ec2_sg.id]
  iam_instance_profile   = aws_iam_instance_profile.gipc_frontend_profile.name


  user_data = <<-EOF
    #!/bin/bash
    set -e

    # Install dependencies
    dnf install -y git python3.12 python3.12-pip jq

    # Clone the repo
    cd /home/ec2-user
    git clone https://github.com/Ttheo22/gipc-data-platform.git
    cd gipc-data-platform

    # Set up venv and install deps
    python3.12 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

    # Fetch DB credentials from Secrets Manager and write .env
    SECRET=$(aws secretsmanager get-secret-value --secret-id gipc/platform-db-credentials --region eu-west-2 --query SecretString --output text)
    DB_HOST=$(echo $SECRET | jq -r .host)
    DB_PORT=$(echo $SECRET | jq -r .port)
    DB_NAME=$(echo $SECRET | jq -r .dbname)
    DB_USER=$(echo $SECRET | jq -r .username)
    DB_PASSWORD=$(echo $SECRET | jq -r .password)

    cat > .env <<EOT
    DB_HOST=$DB_HOST
    DB_PORT=$DB_PORT
    DB_NAME=$DB_NAME
    DB_USER=$DB_USER
    DB_PASSWORD=$DB_PASSWORD
    EOT

    # Fix ownership
    chown -R ec2-user:ec2-user /home/ec2-user/gipc-data-platform

    # Create systemd service
    cat > /etc/systemd/system/gipc-frontend.service <<EOT
    [Unit]
    Description=GIPC Frontend FastAPI App
    After=network.target

    [Service]
    Type=simple
    User=ec2-user
    WorkingDirectory=/home/ec2-user/gipc-data-platform
    Environment="PATH=/home/ec2-user/gipc-data-platform/venv/bin"
    ExecStart=/home/ec2-user/gipc-data-platform/venv/bin/uvicorn frontend.app:app --host 0.0.0.0 --port 8000
    Restart=always
    RestartSec=5

    [Install]
    WantedBy=multi-user.target
    EOT

    # Enable and start the service
    systemctl daemon-reload
    systemctl enable gipc-frontend
    systemctl start gipc-frontend
  EOF

  tags = merge(
    local.common_tags, {
      Name = "gipc_frontend_app"
    }
  )
}