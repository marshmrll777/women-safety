from fastapi import FastAPI
import pandas as pd

app = FastAPI()

df = pd.read_csv("data/safe_route_dataset.csv")

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

def calculate_safety_score(row):

    lighting = row["Lighting"].strip()
    patrol = row["Patrol"].strip()

    score = (
        (row["CCTV_Count"] * 2)
        + (lighting_score[lighting] * 10)
        + (patrol_score[patrol] * 10)
        - (row["Incidents"] * 2)
    )

    return max(score, 0)

df["Safety_Score"] = df.apply(calculate_safety_score, axis=1)

@app.get("/")
#def home():
    #return {"message": "Women Safety Safe Route API Running"}

@app.get("/safe-routes")
def get_safe_routes():

    result = df.sort_values(
        by="Safety_Score",
        ascending=False
    )

    return result.to_dict(orient="records")