from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
from recommendation_core import load_data, recommend_from_profile, facet_views

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 테스트용 (나중에 "https://hyelinyu.github.io"로 변경)
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======== Load Data ========
df = pd.read_csv("data/processed/whisky_clustered.csv")  # or parquet
load_data(df)
# ============================

@app.post("/api/recommend")
async def api_recommend(req: Request):
    body = await req.json()
    reco = recommend_from_profile(
        body=body["body"],
        richness=body["richness"],
        smoke=body["smoke"],
        sweetness=body["sweetness"],
        top_k=body.get("top_k", 60)
    )
    views = facet_views(reco, rare_threshold=body.get("rare_threshold", 0.75))
    return JSONResponse({
        "reco": reco.to_dict(orient="records"),
        "views": {k: v.to_dict(orient="records") for k,v in views.items()}
    })
