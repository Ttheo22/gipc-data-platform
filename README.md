# GIPC Economic Intelligence Platform

An ETL pipeline that extracts economic indicators for Ghana from the World Bank and IMF, transforms and loads them into PostgreSQL, and serves them through a FastAPI dashboard — built locally, then migrated to AWS twice: once manually through the console to learn the underlying services, then again fully automated in Terraform.

**Live demo**: infrastructure is deployed on-demand to manage cost — see [Running This Project](#running-this-project) below.

---

## What It Does

- **Extracts** economic indicators (GDP, inflation, FDI, trade, exchange rates, and more) from the World Bank and IMF APIs, plus a placeholder path for domestic sources (Bank of Ghana, Ghana Statistical Service, Ministry of Finance)
- **Transforms** and normalizes the data — tagging sources, calculating derived metrics (e.g. trade balance), and cleaning null/unknown records
- **Loads** the result into PostgreSQL with upsert semantics (`ON CONFLICT DO NOTHING`) to avoid duplicate records across runs
- **Runs monthly** on an automated schedule, matching how often the underlying source data actually publishes
- **Exports** a CSV snapshot of every run to S3
- **Serves** the data through a FastAPI dashboard with charts, KPI cards, and CSV downloads

## Architecture

```
                          ┌─────────────────────────────────────────┐
                          │                  VPC                     │
                          │                                          │
   Internet ──────────────┼──▶ ALB (public subnets) ──▶ EC2 (private)│──▶ RDS PostgreSQL
                          │         │                    FastAPI      │      (private subnets)
                          │         │                                │
   EventBridge ───────────┼──▶ Lambda (private subnets, containerized)│
   Scheduler               │         │                                │
   (monthly)                │         ▼                                │
                          │    Secrets Manager, S3                    │
                          └─────────────────────────────────────────┘
```

- **Networking**: VPC across 2 AZs, public/private subnet split, single NAT Gateway, IGW
- **Compute**: containerized Lambda (ECR-hosted image) for the ETL pipeline; EC2 for the FastAPI frontend, behind an Application Load Balancer
- **Data**: RDS PostgreSQL (private, no public access), S3 for raw/processed data exports
- **Secrets**: AWS Secrets Manager — no credentials in code or `.env` files in production paths
- **Automation**: EventBridge Scheduler (monthly cron) with bounded retries and a dead-letter queue
- **Security**: least-privilege IAM roles per component (Lambda, EC2 frontend, bastion, scheduler), security groups referenced by identity rather than IP where possible

## Tech Stack

| Layer | Tools |
|---|---|
| ETL | Python, pandas, SQLAlchemy, psycopg2, requests, requests-cache |
| Frontend | FastAPI, uvicorn |
| Database | PostgreSQL (RDS) |
| Infrastructure | Terraform, Docker |
| Cloud | AWS (VPC, Lambda, ECR, RDS, S3, Secrets Manager, IAM, EventBridge Scheduler, SQS, ALB, EC2, ACM) |

## Project Structure

```
gipc-data-platform/
├── extractors/              # World Bank, IMF, domestic source extraction
├── transformers/             # Cleaning and normalization
├── loaders/                  # RDS load logic (Secrets Manager + S3 aware)
├── frontend/                 # FastAPI app, routers, static assets
├── handler.py                 # Lambda entry point
├── Dockerfile                 # Lambda container image build
├── requirements.txt            # Full project dependencies
├── requirements-lambda.txt      # Trimmed dependencies for the Lambda image
└── infrastructure/               # Terraform configuration
    ├── provider.tf
    ├── locals.tf
    ├── variables.tf
    ├── vpc.tf
    ├── security_groups.tf
    ├── rds.tf
    ├── secrets.tf
    ├── s3.tf
    ├── iam.tf
    ├── ecr.tf                     # ECR repo + automated Docker build/push
    ├── eventbridge.tf              # Scheduler + DLQ
    ├── acm.tf                       # Self-signed TLS cert (via the tls provider)
    ├── alb.tf
    └── ec2.tf                        # Frontend instance, self-bootstrapping via user_data
```

## Design Approach

Infrastructure was implemented in two passes: a manual build to validate the architecture end-to-end against real AWS behavior (routing, IAM trust boundaries, container image compatibility, security group dependencies), followed by a full Terraform implementation once the design was proven.

The Terraform implementation goes beyond a direct translation of the manual setup:
- The Lambda container image build and push to ECR is fully automated (`null_resource` + `local-exec`), so no manual `docker build`/`push` is ever required
- The frontend EC2 instance is self-bootstrapping via `user_data` — repo clone, dependency install, credential retrieval from Secrets Manager, and systemd service startup all happen automatically on first boot
- The result is a single-command deployment: `terraform apply` takes the environment from nothing to a fully running, load-balanced, scheduled data platform

## Running This Project

**Prerequisites**: Terraform, Docker Desktop (running), AWS CLI configured with credentials.

```bash
cd infrastructure
terraform init
terraform apply
```

You'll be prompted for `db_password` (or set it in a `terraform.tfvars` file — never committed, see `.gitignore`).

To tear everything down:
```bash
terraform destroy
```

The configuration is fully idempotent — `force_destroy`, `skip_final_snapshot`, and `recovery_window_in_days = 0` are set throughout specifically so the stack can be destroyed and rebuilt repeatedly without manual cleanup, which keeps this cheap to run only when actually needed rather than leaving infrastructure (and its cost) running 24/7.

## Known Limitations

- Domestic sources (BoG, GSS, MoF) extraction currently reads from a local path that doesn't exist in Lambda's environment — needs to be rewritten to read from S3.
- The frontend uses a self-signed TLS certificate (no owned domain yet), so browsers will show a security warning on HTTPS.
- No CI/CD pipeline yet — deployment is manual (`terraform apply`).

## What's Next

- CI/CD via GitHub Actions to rebuild and redeploy on push
- S3-based ingestion for domestic data sources
- CloudWatch alarms and SNS notifications on pipeline failures
