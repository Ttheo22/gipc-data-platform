from fastapi import APIRouter, HTTPException, Query
from frontend.database import query

router = APIRouter(prefix="/api", tags=["indicators"])


# ── All Indicators ─────────────────────────────────────────
@router.get("/indicators")
def get_indicators():
    """Returns list of all available indicators."""
    sql = """
        SELECT DISTINCT indicator_name, source, unit
        FROM economic_indicators
        ORDER BY indicator_name, source
    """
    return query(sql)


# ── Data for a Specific Indicator ──────────────────────────
@router.get("/data")
def get_data(
    indicator: str = Query(..., description="Indicator name"),
    source:    str = Query(None, description="Filter by source"),
    year_from: int = Query(1990, description="Start year"),
    year_to:   int = Query(2031, description="End year"),
):
    """Returns time series data for a given indicator."""
    if source:
        sql = """
            SELECT year, value, source, unit
            FROM economic_indicators
            WHERE indicator_name = :indicator
              AND source = :source
              AND year BETWEEN :year_from AND :year_to
            ORDER BY year
        """
        params = {
            "indicator": indicator,
            "source": source,
            "year_from": year_from,
            "year_to": year_to
        }
    else:
        sql = """
            SELECT year, value, source, unit
            FROM economic_indicators
            WHERE indicator_name = :indicator
              AND year BETWEEN :year_from AND :year_to
            ORDER BY year
        """
        params = {
            "indicator": indicator,
            "year_from": year_from,
            "year_to": year_to
        }

    results = query(sql, params)
    if not results:
        raise HTTPException(status_code=404, detail=f"No data found for {indicator}")
    return results


# ── KPI Summary ────────────────────────────────────────────
@router.get("/kpis")
def get_kpis():
    """Returns latest values for key dashboard indicators."""
    sql = """
        SELECT DISTINCT ON (indicator_name, source)
            indicator_name,
            source,
            year,
            value,
            unit
        FROM economic_indicators
        WHERE indicator_name IN (
            'gdp_current_usd',
            'fdi_net_inflows_usd',
            'inflation_cpi',
            'exchange_rate_usd',
            'gdp_growth_rate',
            'unemployment_rate'
        )
        AND value IS NOT NULL
        ORDER BY indicator_name, source, year DESC
    """
    return query(sql)


# ── Domestic Indicators ────────────────────────────────────
@router.get("/domestic")
def get_domestic(
    indicator: str = Query(None, description="Filter by indicator name"),
    source:    str = Query(None, description="Filter by source: GSS, BoG, MoF"),
):
    """Returns domestic source data (GSS, BoG, MoF)."""
    conditions = []
    params     = {}

    if indicator:
        conditions.append("indicator_name = :indicator")
        params["indicator"] = indicator
    if source:
        conditions.append("source = :source")
        params["source"] = source

    where = "WHERE " + " AND ".join(conditions) if conditions else ""

    sql = f"""
        SELECT indicator_name, source, year, period,
               quarter, month, value, unit, notes
        FROM domestic_indicators
        {where}
        ORDER BY indicator_name, year DESC, period DESC
    """
    return query(sql, params)


# ── Last Updated ───────────────────────────────────────────
@router.get("/last-updated")
def last_updated():
    """Returns when the data was last loaded."""
    sql = """
        SELECT MAX(created_at) as last_updated
        FROM economic_indicators
    """
    result = query(sql)
    return result[0] if result else {"last_updated": None}