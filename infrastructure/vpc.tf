resource "aws_vpc" "gipc_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = merge(
    local.common_tags, {
      Name = "gipc_vpc"
    }
  )
}

resource "aws_internet_gateway" "gipc_igw" {
  vpc_id = aws_vpc.gipc_vpc.id

  tags = merge(
    local.common_tags, {
      Name = "gipc_igw"
    }
  )
}

resource "aws_subnet" "gipc_subnet_public1_eu_west_2a" {
  vpc_id                  = aws_vpc.gipc_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "eu-west-2a"
  map_public_ip_on_launch = true

  tags = merge(
    local.common_tags, {
      Name = "gipc_subnet_public1_eu_west_2a"
    }
  )
}

resource "aws_subnet" "gipc_subnet_public2_eu_west_2b" {
  vpc_id                  = aws_vpc.gipc_vpc.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "eu-west-2b"
  map_public_ip_on_launch = true

  tags = merge(
    local.common_tags, {
      Name = "gipc_subnet_pulic2_eu_west_2b"
    }
  )
}

resource "aws_subnet" "gipc_subnet_private1_eu_west_2a" {
  vpc_id            = aws_vpc.gipc_vpc.id
  cidr_block        = "10.0.3.0/24"
  availability_zone = "eu-west-2a"

  tags = merge(
    local.common_tags, {
      Name = "gipc_subnet_private1_eu_west_2a"
    }
  )
}

resource "aws_subnet" "gipc_subnet_private2_eu_west_2b" {
  vpc_id            = aws_vpc.gipc_vpc.id
  cidr_block        = "10.0.4.0/24"
  availability_zone = "eu-west-2b"

  tags = merge(
    local.common_tags, {
      Name = "gipc_subnet_private2_eu_west_2b"
    }
  )
}

resource "aws_eip" "gipc_nat_eip" {
  domain = "vpc"

  tags = merge(
    local.common_tags, {
      Name = "gipc_nat_eip"
    }
  )
}

resource "aws_nat_gateway" "gipc_nat_gateway" {
  subnet_id     = aws_subnet.gipc_subnet_public1_eu_west_2a.id
  allocation_id = aws_eip.gipc_nat_eip.id

  tags = merge(
    local.common_tags, {
      Name = "gipc_nat_gateway"
    }
  )
}

resource "aws_route_table" "public_rtb" {
  vpc_id = aws_vpc.gipc_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gipc_igw.id
  }

  tags = merge(
    local.common_tags, {
      Name = "public_rtb"
    }
  )
}

resource "aws_route_table" "private_rtb_1" {
  vpc_id = aws_vpc.gipc_vpc.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.gipc_nat_gateway.id
  }

  tags = merge(
    local.common_tags, {
      Name = "private_rtb_1"
    }
  )
}

resource "aws_route_table" "private_rtb_2" {
  vpc_id = aws_vpc.gipc_vpc.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.gipc_nat_gateway.id
  }

  tags = merge(
    local.common_tags, {
      Name = "private_rtb_2"
    }
  )
}

resource "aws_route_table_association" "gipc_subnet_public1_eu_west_2a" {
  route_table_id = aws_route_table.public_rtb.id
  subnet_id      = aws_subnet.gipc_subnet_public1_eu_west_2a.id
}

resource "aws_route_table_association" "gipc_subnet_public2_eu_west_2b" {
  route_table_id = aws_route_table.public_rtb.id
  subnet_id      = aws_subnet.gipc_subnet_public2_eu_west_2b.id
}

resource "aws_route_table_association" "gipc_subnet_private1_eu_west_2a" {
  route_table_id = aws_route_table.private_rtb_1.id
  subnet_id      = aws_subnet.gipc_subnet_private1_eu_west_2a.id
}

resource "aws_route_table_association" "gipc_subnet_private2_eu_west_2b" {
  route_table_id = aws_route_table.private_rtb_2.id
  subnet_id      = aws_subnet.gipc_subnet_private2_eu_west_2b.id
}

