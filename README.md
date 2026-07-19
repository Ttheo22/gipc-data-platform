# GIPC Economic Intelligence Platform

A production-inspired cloud data platform that automates the collection, transformation, storage, and publication of Ghana's economic indicators. The platform extracts data from authoritative international sources, transforms it into a consistent format, stores it in Amazon RDS PostgreSQL, and serves it through a FastAPI web application.

The solution is designed using AWS managed services to provide a secure, event-driven, and cost-effective architecture suitable for periodic data collection workloads.

**Live Demo:** [https://gipc-frontend-alb-1316479457.eu-west-2.elb.amazonaws.com/](https://gipc-frontend-alb-1316479457.eu-west-2.elb.amazonaws.com/)

> **Note:** The application currently uses a temporary self-signed TLS certificate because a custom domain has not yet been configured. Your browser will display a security warning until a trusted certificate is installed.

---

# Features

* Automated monthly ETL pipeline
* Data ingestion from World Bank and IMF APIs
* Data transformation and normalization using pandas
* PostgreSQL data warehouse hosted on Amazon RDS
* CSV export to Amazon S3
* FastAPI web application for browsing and visualizing indicators
* Event-driven serverless ETL using AWS Lambda
* Secure deployment inside a custom Amazon VPC
* Automated monthly execution using Amazon EventBridge Scheduler

---

# Data Sources

| Source                 | Description                                                                                   |
| ---------------------- | --------------------------------------------------------------------------------------------- |
| **World Bank API**     | 25 macroeconomic, trade, fiscal, infrastructure and development indicators                    |
| **IMF DataMapper API** | GDP forecasts and key macroeconomic indicators (5 indicators)                                 |
| **Domestic Sources**   | Planned integration with Bank of Ghana, Ghana Statistical Service and other national datasets |

---

# Technology Stack

### Programming

* Python
* pandas
* SQLAlchemy
* FastAPI

### Database

* PostgreSQL (Amazon RDS)

### Infrastructure

* AWS Lambda
* Amazon EC2
* Amazon RDS
* Amazon S3
* Amazon EventBridge Scheduler
* Application Load Balancer
* Amazon VPC
* AWS Secrets Manager
* IAM
* Docker

### Planned

* Terraform
* GitHub Actions

---

# Solution Architecture

```
                World Bank API
                      │
                      │
                IMF DataMapper
                      │
                      ▼
          EventBridge Scheduler
                      │
                      ▼
            AWS Lambda (Docker)
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
 Amazon RDS PostgreSQL      Amazon S3 (CSV Export)
          │
          ▼
      FastAPI Application
        (Amazon EC2)
          │
          ▼
Application Load Balancer
          │
          ▼
        Internet
```

---

# Architecture Overview

The platform follows an event-driven architecture.

On a monthly schedule, Amazon EventBridge Scheduler invokes a containerized AWS Lambda function deployed inside private subnets of a custom Amazon VPC. The ETL process retrieves data from the World Bank and IMF APIs, validates and transforms the datasets using pandas, loads the results into Amazon RDS PostgreSQL, and archives a CSV copy in Amazon S3.

The FastAPI application runs continuously on an Amazon EC2 instance within the same VPC. Public traffic is routed through an Application Load Balancer while database communication remains private within the VPC.

Separating the ETL workload from the web application allows each component to scale independently while reducing operational costs by only running compute resources when needed.

---

# Architecture Decisions

| Decision                      | Reason                                                                    |
| ----------------------------- | ------------------------------------------------------------------------- |
| **AWS Lambda**                | Eliminates idle compute costs for scheduled ETL workloads                 |
| **Docker Container**          | Ensures dependency consistency and avoids Lambda package size limitations |
| **Amazon RDS PostgreSQL**     | Structured relational storage with SQL querying capabilities              |
| **Amazon S3**                 | Durable storage for exported datasets                                     |
| **FastAPI on EC2**            | Persistent web application independent of ETL execution                   |
| **Application Load Balancer** | Secure public access and HTTP(S) routing                                  |
| **Amazon VPC**                | Isolates application and database resources from the public internet      |
| **Secrets Manager**           | Secure storage of Lambda database credentials                             |
| **EventBridge Scheduler**     | Fully managed scheduling without cron servers                             |

---

# Deployment Architecture

The infrastructure is deployed inside a custom Amazon VPC.

* Public subnets host the Application Load Balancer.
* Private subnets host Amazon RDS and the AWS Lambda function.
* The FastAPI application runs on Amazon EC2 and communicates privately with the database.
* Lambda accesses the database using credentials stored in AWS Secrets Manager.
* Amazon EventBridge Scheduler triggers the ETL process once every month.
* Processed datasets are archived in Amazon S3.

---

# Dataset Summary

| Metric                      |           Value |
| --------------------------- | --------------: |
| International Data Sources  |               2 |
| Economic Indicators         |              29 |
| Automated Refresh Frequency |         Monthly |
| Database                    |      PostgreSQL |
| Data Export                 | CSV (Amazon S3) |
| Frontend                    |         FastAPI |
| Deployment                  |             AWS |

---

# Indicators Covered

| Category                         |  Count |
| -------------------------------- | -----: |
| Macroeconomic                    |      5 |
| Fiscal & Debt                    |      4 |
| Trade                            |      5 |
| Foreign Direct Investment        |      2 |
| Labour & Demographics            |      3 |
| Sectoral Indicators              |      2 |
| Infrastructure & Digital Economy |      3 |
| Governance *(planned)*           |      5 |
| **Total**                        | **29** |

---

# Running the Project Locally

## Install dependencies

```bash
pip install -r requirements.txt
```

## Configure environment variables

```bash
cp .env.example .env
```

Update the `.env` file with your PostgreSQL connection details.

## Run the ETL pipeline

```bash
python loaders/rds_loader.py
```

---

# Building the Lambda Container

The Lambda deployment uses a lightweight dependency set defined in `requirements-lambda.txt`.

Build the container image using:

```bash
docker build --provenance=false --sbom=false -t gipc-etl-lambda .
```

The `--provenance=false` and `--sbom=false` flags are required because Docker's default build metadata is not compatible with AWS Lambda container deployments.

---

# Project Structure

```text
gipc-data-platform/
│
├── handler.py                    # Lambda entry point
├── extractors/                   # Data source connectors
├── transformers/                 # Data cleaning and normalization
├── loaders/                      # Database loader and CSV export
├── frontend/
│   ├── routers/
│   ├── static/
│   ├── database.py
│   └── app.py
├── infrastructure/               # Database schema
├── requirements.txt
├── requirements-lambda.txt
├── Dockerfile
└── tests/
```

---

# Current Status

| Component                       | Status         |
| ------------------------------- | -------------- |
| Local ETL Pipeline              | ✅ Complete     |
| Data Transformation             | ✅ Complete     |
| PostgreSQL Warehouse            | ✅ Complete     |
| CSV Export                      | ✅ Complete     |
| AWS Lambda Deployment           | ✅ Complete     |
| Amazon RDS                      | ✅ Complete     |
| Amazon S3 Export                | ✅ Complete     |
| EventBridge Automation          | ✅ Complete     |
| FastAPI Frontend                | ✅ Complete     |
| EC2 Deployment                  | ✅ Complete     |
| Application Load Balancer       | ✅ Complete     |
| Dockerized Lambda               | ✅ Complete     |
| Domestic Data Sources           | 🚧 In Progress |
| CloudWatch Monitoring           | 🚧 Planned     |
| Terraform Infrastructure        | 🚧 Planned     |
| GitHub Actions CI/CD            | 🚧 Planned     |
| Power BI Dashboard              | 🚧 Planned     |
| Custom Domain & TLS Certificate | 🚧 Planned     |

---

# Known Limitations

### Domestic Data Sources

The domestic data extractor currently expects local files and has not yet been migrated to read datasets directly from Amazon S3. As a result, domestic indicators currently return zero records.

### Monitoring

CloudWatch alarms and automated operational notifications have not yet been configured. ETL failures are currently sent to an Amazon SQS Dead Letter Queue without alerting.

### Frontend Secrets

The FastAPI application currently stores database credentials in a local `.env` file. This will be migrated to AWS Secrets Manager to align with the Lambda deployment.

### TLS Certificate

The public application currently uses a temporary self-signed certificate until a custom domain is purchased and an ACM-issued certificate is configured.

---

# Planned Improvements

* Integrate Bank of Ghana and Ghana Statistical Service datasets
* Infrastructure provisioning with Terraform
* GitHub Actions CI/CD pipeline
* CloudWatch dashboards and alarms
* Automated notification of ETL failures
* Power BI reporting dashboard
* Custom domain with trusted TLS certificate
* Increased automated test coverage

---

# Future Enhancements

Potential future enhancements include:

* Historical trend analysis
* Interactive dashboards
* API endpoints for third-party consumers
* Multi-country economic comparisons
* Data quality validation framework
* Automated schema migration
* Infrastructure autoscaling
* Cost monitoring dashboards

---

## License

This project is intended as a portfolio demonstration of cloud architecture, serverless ETL, and AWS infrastructure engineering.
