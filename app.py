# app.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd

app = FastAPI()

# ✅ CORS 허용 (GitHub Pages에서 호출 가능하게)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 나중에 ["https://hyelinyu.github.io"] 로 좁혀도 됨
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 추천 함수 불러오기 (이미 만든 recommend_from_profile, facet_views)
from 06_recommendation_system import recommend_from_profile, facet_views  # 파일명 맞게 조정

@app.post("/api/recommend")
async def recommend_api(request: Request):
    body = await request.json()
    reco = recommend_from_profile(
        body=body["body"],
        richness=body["richness"],
        smoke=body["smoke"],
        sweetness=body["sweetness"],
        top_k=body.get("top_k", 80),
        extra_filters=body.get("extra_filters"),
    )
    views = facet_views(reco, rare_threshold=body.get("rare_threshold"))
    return JSONResponse({
        "reco": reco.to_dict(orient="records"),
        "views": {k: v.to_dict(orient="records") for k, v in views.items()}
    })
