# handler.py
import logging
from extractors.world_bank import run as wb_run
from extractors.imf import run as imf_run
from extractors.domestic_sources import run as domestic_run
from transformers.normalize import run as transform_run
from loaders.rds_loader import run as load_run, load_domestic, export_csv

logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    logger.info("Pipeline started (Lambda invocation)")

    wb_data = wb_run()
    imf_data = imf_run()
    domestic_data = domestic_run()

    df = transform_run(wb_data, imf_data)

    success = load_run(df)

    logger.info("=== Loading domestic sources ===")
    domestic_success = load_domestic(domestic_data)

    export_path = None
    if success:
        export_path = export_csv(df)
        logger.info("Pipeline finished successfully")
    else:
        logger.error("Pipeline finished with errors")

    return {
        "statusCode": 200 if success else 500,
        "body": {
            "load_success": success,
            "domestic_load_success": domestic_success,
            "records_loaded": len(df) if df is not None else 0,
            "export_path": export_path,
        }
    }