from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from frontend.routers import indicators, exports
import os

# ── App Setup ──────────────────────────────────────────────
app = FastAPI(
    title="GIPC Economic Intelligence Platform",
    description="Economic data API for the Ghana Investment Promotion Centre",
    version="1.0.0",
)

# ── Routers ────────────────────────────────────────────────
app.include_router(indicators.router)
app.include_router(exports.router)

# ── Static Files ───────────────────────────────────────────
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")),
    name="static",
)

# ── Root Route ─────────────────────────────────────────────
@app.get("/")
def root():
    return FileResponse(
        os.path.join(os.path.dirname(__file__), "static", "index.html")
    )


# ── Health Check ───────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "platform": "GIPC Economic Intelligence Platform"}