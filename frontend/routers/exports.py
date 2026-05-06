import io
import csv
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from frontend.database import query

router = APIRouter(prefix="/api", tags=["exports"])


@router.get("/export/csv")
def export_csv():
    """
    Streams the full economic_indicators table as a CSV download.
    """
    sql = """
        SELECT indicator_name, source, country, year, value, unit
        FROM economic_indicators
        ORDER BY indicator_name, source, year
    """
    rows = query(sql)

    if not rows:
        return {"error": "No data to export"}

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=gipc_economic_indicators.csv"
        }
    )


@router.get("/export/domestic/csv")
def export_domestic_csv():
    """
    Streams the domestic_indicators table as a CSV download.
    """
    sql = """
        SELECT indicator_name, source, country, year,
               period, quarter, month, value, unit, notes
        FROM domestic_indicators
        ORDER BY source, indicator_name, year
    """
    rows = query(sql)

    if not rows:
        return {"error": "No domestic data to export"}

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=gipc_domestic_indicators.csv"
        }
    )