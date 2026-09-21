from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

# --------------------------------------------------
# Create FastAPI app
# --------------------------------------------------

app = FastAPI(
    title="Women Safety Safe Route API",
    description="Area-level women safety intelligence API",
    version="1.0.0"
)

# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Load dataset
# --------------------------------------------------

df = pd.read_csv("data/safe_route_dataset.csv")

# --------------------------------------------------
# Score mappings
# --------------------------------------------------

lighting_score = {
    "Poor": 1,
    "Medium": 2,
    "Good": 3
}

patrol_score = {
    "Low": 1,
    "Medium": 2,
    "High": 3
}

# --------------------------------------------------
# Safety score calculation
# --------------------------------------------------

def calculate_safety_score(row):
    lighting = str(row["Lighting"]).strip()
    patrol = str(row["Patrol"]).strip()

    score = (
        (float(row["CCTV_Count"]) * 2)
        + (lighting_score[lighting] * 10)
        + (patrol_score[patrol] * 10)
        - (float(row["Incidents"]) * 2)
    )

    return max(score, 0)


df["Safety_Score"] = df.apply(
    calculate_safety_score,
    axis=1
)

# --------------------------------------------------
# Root endpoint
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Women Safety Safe Route API Running",
        "status": "online"
    }

# --------------------------------------------------
# Safe Route Intelligence endpoint
# --------------------------------------------------

@app.get("/safe-routes")
def get_safe_routes():

    result = df.sort_values(
        by="Safety_Score",
        ascending=False
    ).copy()

    # Make values JSON-friendly
    result["CCTV_Count"] = result["CCTV_Count"].astype(int)
    result["Incidents"] = result["Incidents"].astype(int)
    result["Safety_Score"] = result["Safety_Score"].astype(int)

    # Remove extra spaces from text fields
    result["Area"] = result["Area"].astype(str).str.strip()
    result["Lighting"] = result["Lighting"].astype(str).str.strip()
    result["Patrol"] = result["Patrol"].astype(str).str.strip()

    return result.to_dict(orient="records")
