# GIPC Economic Intelligence Platform

An automated ETL pipeline that fetches, transforms, and stores 
economic indicators for Ghana from authoritative global sources.
Built to support the Ghana Investment Promotion Centre (GIPC).

## Data Sources
- **World Bank** — 25 macroeconomic, trade, fiscal and development indicators
- **IMF DataMapper** — 5 indicators including GDP forecasts to 2031

## Tech Stack
- **Python** — extraction, transformation, loading
- **pandas** — data normalisation and transformation
- **PostgreSQL** — data warehouse
- **SQLAlchemy** — database interface
- **Power BI** — dashboard and visualisation
- **AWS** *(coming)* — S3, RDS, Lambda, EventBridge
- **Terraform** *(coming)* — infrastructure as code

## Pipeline Architecture

```
World Bank API ──┐
                 ├──► Transform ──► PostgreSQL ──► Power BI
IMF API ─────────┘                     └──► CSV Export
```

## Running the Pipeline

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run full pipeline
python loaders/rds_loader.py
```

## Project Structure

```
extractors/        # API connectors (World Bank, IMF)
transformers/      # Data cleaning and normalisation
loaders/           # PostgreSQL loader and CSV exporter
infrastructure/    # Database schema SQL
tests/             # Unit tests (coming)
```

## Indicators Covered

| Category | Count |
|---|---|
| Macroeconomic | 5 |
| Fiscal & Debt | 4 |
| FDI & Investment | 2 |
| Trade | 5 |
| Labour & Demographics | 3 |
| Sectoral | 2 |
| Infrastructure & Digital | 3 |
| Governance *(coming)* | 5 |
| **Total** | **29** |

## Status
- [x] Local ETL pipeline
- [x] PostgreSQL data warehouse
- [x] Power BI dashboard
- [x] CSV export
- [x] Error handling and logging
- [ ] AWS deployment
- [ ] Terraform infrastructure
- [ ] Automated scheduling
- [ ] Frontend web app
