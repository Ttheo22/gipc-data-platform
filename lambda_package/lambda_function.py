import json
import logging
import os

# ── Logging ───────────────────────────────────────────────
logger = logging.getLogger()
logger.setLevel(logging.INFO)


# ── Handler ───────────────────────────────────────────────
def handler(event, context):
    """
    AWS Lambda entry point.
    Runs the full GIPC ETL pipeline:
    Extract -> Transform -> Load to RDS -> Upload to S3
    """
    logger.info("GIPC Pipeline Lambda started")
    logger.info(f"Event: {json.dumps(event)}")

    try:
        from extractors.world_bank import run as wb_run
        from extractors.imf import run as imf_run
        from extractors.domestic_sources import run as domestic_run
        from transformers.normalize import run as transform_run
        from loaders.rds_loader import run, load_domestic

        # Extract
        logger.info("Starting extraction...")
        wb_data       = wb_run()
        imf_data      = imf_run()
        domestic_data = domestic_run()

        # Transform
        logger.info("Starting transformation...")
        df = transform_run(wb_data, imf_data)

        # Load to RDS
        logger.info("Loading to RDS...")
        economic_success = run(df)
        domestic_success = load_domestic(domestic_data)

        # Upload to S3 only if the economic load succeeded
        if economic_success:
            upload_to_s3(df)
        else:
            logger.error("Skipping S3 upload because economic load failed")

        # Report real status
        if economic_success:
            logger.info("Pipeline completed successfully")
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Pipeline completed successfully",
                    "records_processed": len(df),
                    "domestic_loaded": domestic_success,
                })
            }
        else:
            logger.error("Pipeline finished with errors: economic load failed")
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "message": "Economic load failed",
                    "records_processed": len(df),
                })
            }

    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Pipeline failed",
                "error": str(e),
            })
        }


def upload_to_s3(df):
    """
    Uploads the processed DataFrame as CSV to S3.
    """
    import boto3
    from datetime import datetime

    bucket   = os.environ.get("S3_BUCKET", "gipc-data-platform-theo2026")
    filename = f"processed/economic_indicators/gipc_indicators_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    s3 = boto3.client("s3")
    s3.put_object(
        Bucket=bucket,
        Key=filename,
        Body=df.to_csv(index=False).encode("utf-8"),
        ContentType="text/csv"
    )
    logger.info(f"Uploaded to s3://{bucket}/{filename}")