from fastapi import FastAPI
from database import get_connection
from routers.kpi import router as kpi_router
from fastapi.middleware.cors import CORSMiddleware
from routers.status import router as status_router
from routers.pipeline import router as pipeline_router
from services.pipeline_service import resume_if_needed
from routers.powerbi import router as powerbi_router
from routers import insights
from routers.activity import router as activity_router


app = FastAPI(
    title="SalesPulse360 API",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_pipeline():

    print("=" * 60)
    print("SalesPulse360 Backend Started")
    print("Checking saved pipeline state...")
    print("=" * 60)

    resume_if_needed()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://salespulse360-frontend.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    kpi_router,
    prefix="/api",
    tags=["KPIs"]
)

app.include_router(
    status_router,
    prefix="/api",
    tags=["Status"]
)

app.include_router(
    pipeline_router,
    prefix="/api",
    tags=["Pipeline"]
)

app.include_router(
    powerbi_router,
    prefix="/api",
    tags=["PowerBI"])

app.include_router(
    insights.router,
    prefix="/api"
)

app.include_router(
    activity_router,
    prefix="/api",
    tags=["Activity"]
)

@app.get("/")
def home():
    return {
        "message": "Welcome to SalesPulse360 Backend",
        "status": "Running Successfully"
    }


@app.get("/test-db")
def test_database():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT CURRENT_VERSION()")

    version = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return {
        "status": "Connected Successfully",
        "snowflake_version": version
    }

