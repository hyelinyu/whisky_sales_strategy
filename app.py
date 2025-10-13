from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
import pandas as pd

# 내부 모듈
from recommendation_core import load_data, recommend_from_profile, facet_views

app = FastAPI()

# CORS (테스트용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 상태
DATA_DF = None
DATA_PATH = Path(__file__).parent / "data" / "processed" / "whisky_clustered.csv"

@app.get("/")
def root():
    return {"status": "ok", "service": "whisky_sales_strategy"}

@app.get("/health")
def health():
    return {"ok": True}

@app.on_event("startup")
def _startup():
    """
    서버가 뜰 때 한 번만 데이터 로드.
    파일이 없더라도 서버가 죽지 않도록 처리.
    """
    global DATA_DF
    if DATA_PATH.exists():
        df = pd.read_csv(DATA_PATH)
        load_data(df)
        DATA_DF = df
        print(f"[startup] loaded: {DATA_PATH} rows={len(df)}")
    else:
        # 파일이 없어도 서버는 계속 살아있게
        print(f"[startup] WARNING: data file not found: {DATA_PATH}. API will still run.")
        load_data(None)  # 내부에서 None 처리 가능하도록 구현되어 있어야 함.

@app.post("/api/recommend")
async def api_recommend(req: Request):
    body = await req.json()
    reco = recommend_from_profile(
        body=body.get("body"),
        richness=body.get("richness"),
        smoke=body.get("smoke"),
        sweetness=body.get("sweetness"),
        top_k=body.get("top_k", 60),
    )
    views = facet_views(reco, rare_threshold=body.get("rare_threshold", 0.75))
    return JSONResponse({
        "reco": reco.to_dict(orient="records"),
        "views": {k: v.to_dict(orient="records") for k, v in views.items()},
    })
