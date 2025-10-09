# =========================================================
# 06_recommendation_system (taste-first + facet views)
# =========================================================
import re
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

# 전역 상태 (load_data 호출 후 세팅됨)
df_feat: pd.DataFrame | None = None
scaler: StandardScaler | None = None
X: np.ndarray | None = None

# 자동 매핑 결과 보관
taste_cols: list[str] = []
col_price = col_abv = col_cask = col_type = col_year = col_vintage = col_rarity = None

# -----------------------------
# 0) Column Resolver (유연 매핑)
# -----------------------------
def _resolve(df, patterns, required=False):
    cols_map = {c.lower().strip(): c for c in df.columns}
    for pat in patterns:
        low = pat.lower()
        if low in cols_map:
            return cols_map[low]
        rx = re.compile(pat, re.I)
        for k, orig in cols_map.items():
            if rx.search(k):
                return orig
    if required:
        raise KeyError(f"Column not found for patterns: {patterns}")
    return None

def _resolve_taste_cols(df):
    return dict(
        body=_resolve(df, [r"^style_body_last$", r"^style_body$", r"\bbody\b"], required=True),
        richness=_resolve(df, [r"^style_richness_last$", r"^style_richness$", r"\brichness\b"], required=True),
        smoke=_resolve(df, [r"^style_smoke_last$", r"^style_smoke$", r"\bsmoke|peat\b"], required=True),
        sweetness=_resolve(df, [r"^style_sweetness_last$", r"^style_sweetness$", r"\bsweet(ness)?\b"], required=True),
    )

def _vintage_flag_series(df, vintage_col):
    if vintage_col is None or vintage_col not in df.columns:
        return pd.Series(False, index=df.index, name="is_vintage")
    s = df[vintage_col].astype(str).str.strip().str.lower()
    na_like = {"", "na", "n/a", "none", "nan", "null"}
    return (~s.isin(na_like)) & (s != "0")

def _price_bucket_series(s: pd.Series, mode="quantile"):
    s = pd.to_numeric(s, errors="coerce")
    if s.notna().sum() == 0:
        return pd.Series("Unknown", index=s.index, name="price_bucket")
    if mode == "quantile":
        try:
            q = pd.qcut(s, 4, labels=["Q1-Low","Q2","Q3","Q4-High"])
        except ValueError:
            q = pd.cut(s, bins=4, labels=["Q1-Low","Q2","Q3","Q4-High"])
        return q.astype(str).rename("price_bucket")
    return s

# ---------------------------------------------
# 1) 초기화: 원본 df를 받아 피처/스케일러 세팅
# ---------------------------------------------
def load_data(df: pd.DataFrame):
    global df_feat, scaler, X, taste_cols
    global col_price, col_abv, col_cask, col_type, col_year, col_vintage, col_rarity

    # 자동 매핑
    tmap = _resolve_taste_cols(df)
    col_price   = _resolve(df, [r"^price", r"price.*£", r"price_?usd", r"price_?krw"])
    col_abv     = _resolve(df, [r"^alcohol\(%\)$", r"\babv\b", r"alcohol", r"alc[%]?" ])
    col_cask    = _resolve(df, [r"^cask[_ ]?type$", r"\bcask(type)?\b", r"cask.*group"])
    col_type    = _resolve(df, [r"^whisky[_ ]?type$", r"\b(type|category|style)$", r"whiskey[_ ]?type"])
    col_year    = _resolve(df, [r"\bbottling[_ ]?year\b", r"\byear\b", r"vintage_year"])
    col_vintage = _resolve(df, [r"^vintage_clean$", r"\bvintage\b"])
    col_rarity  = _resolve(df, [r"^rarity_score$", r"^rare_score$", r"\brarity\b", r"rare_index"])

    taste_cols = [tmap["body"], tmap["richness"], tmap["smoke"], tmap["sweetness"]]

    # 피처 준비
    df_feat = df.copy()
    for c in taste_cols:
        df_feat[c] = pd.to_numeric(df_feat[c], errors="coerce")
    med = df_feat[taste_cols].median(numeric_only=True)
    df_feat[taste_cols] = df_feat[taste_cols].fillna(med).clip(lower=0, upper=5)

    # 스케일링
    scaler = StandardScaler()
    X = scaler.fit_transform(df_feat[taste_cols])
    X[:] = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)

    # 파생
    df_feat["is_vintage"] = _vintage_flag_series(df_feat, col_vintage)
    if col_year:
        df_feat[col_year] = pd.to_numeric(df_feat[col_year], errors="coerce").astype("Int64")
    if col_price:
        df_feat["price_bucket"] = _price_bucket_series(df_feat[col_price], mode="quantile")
    else:
        df_feat["price_bucket"] = "Unknown"

# ---------------------------------------------
# 2) 고객 입력 기반 추천 (이름 불필요)
# ---------------------------------------------
def recommend_from_profile(
    *,
    body: float, richness: float, smoke: float, sweetness: float,
    top_k: int = 60,
    weights: dict | None = None,
    extra_filters: dict | None = None,
) -> pd.DataFrame:
    assert df_feat is not None and scaler is not None and X is not None, "call load_data(df) first"

    # 사전 필터
    base = df_feat
    if extra_filters:
        for k, allow in extra_filters.items():
            if k in base.columns:
                base = base[base[k].isin(allow)]
    if len(base) == 0:
        raise ValueError("사전 필터 결과가 비어있습니다. 조건을 완화하세요.")

    # 쿼리
    q = np.array([
        np.clip(float(body), 0, 5),
        np.clip(float(richness), 0, 5),
        np.clip(float(smoke), 0, 5),
        np.clip(float(sweetness), 0, 5),
    ]).reshape(1, -1)

    # 축 가중치
    if weights is not None:
        w = np.array([
            float(weights.get("body",1.0)),
            float(weights.get("richness",1.0)),
            float(weights.get("smoke",1.0)),
            float(weights.get("sweetness",1.0)),
        ]).reshape(1, -1)
        X_used = X * w
        # 표준화 좌표로 변환 + 가중치
        q_std = (q - scaler.mean_) / np.where(scaler.scale_==0, 1, scaler.scale_)
        q_used = q_std * w
    else:
        X_used = X
        q_used = (q - scaler.mean_) / np.where(scaler.scale_==0, 1, scaler.scale_)

    # 부분집합에서 KNN
    idx_map = base.index.to_numpy()
    X_sub   = X_used[idx_map]
    nns = min(int(top_k), len(X_sub))
    dist, nn_idx = NearestNeighbors(metric="euclidean", n_neighbors=nns)\
        .fit(X_sub).kneighbors(q_used, n_neighbors=nns)

    res = df_feat.loc[idx_map[nn_idx[0]]].copy()
    res["distance"] = dist[0]

    show_cols = ["name","country","region"]
    if "cluster_taste" in res.columns: show_cols.append("cluster_taste")
    if col_price: show_cols.append(col_price)
    if col_abv:   show_cols.append(col_abv)
    if col_cask:  show_cols.append(col_cask)
    if col_type:  show_cols.append(col_type)
    if col_year:  show_cols.append(col_year)
    show_cols += ["is_vintage","distance"]
    show_cols = [c for c in show_cols if c in res.columns]
    return res[show_cols].reset_index(drop=True)

# ---------------------------------------------
# 3) Facet Views: 결과를 '따로' 보여주기
# ---------------------------------------------
def _topn_by_group(df_in, group_col, topn=5, max_groups=8, sort_col="distance"):
    if (group_col is None) or (group_col not in df_in.columns):
        return pd.DataFrame(columns=df_in.columns)
    tmp = df_in.sort_values(sort_col, ascending=True).copy()
    top = tmp.groupby(group_col, group_keys=True).head(topn)
    if max_groups is not None:
        keep_groups = (
            top.groupby(group_col)[sort_col].mean()
               .sort_values().head(max_groups).index
        )
        top = top[top[group_col].isin(keep_groups)]
    return top

def facet_views(
    base_reco: pd.DataFrame,
    *,
    price_topn=5, cask_topn=5, type_topn=5, year_topn=5,
    rare_threshold: float | None = None,
    max_groups=8
):
    out = {}
    br = base_reco.copy()

    # price
    if "price_bucket" not in br.columns and (df_feat is not None) and ("price_bucket" in df_feat.columns):
        br = br.merge(df_feat[["name","price_bucket"]], on="name", how="left")
    out["by_price_bucket"] = _topn_by_group(br, "price_bucket", topn=price_topn, max_groups=max_groups)

    # cask/type/year
    out["by_cask_group"]   = _topn_by_group(br, col_cask, topn=cask_topn, max_groups=max_groups)
    out["by_whisky_type"]  = _topn_by_group(br, col_type, topn=type_topn, max_groups=max_groups)
    out["by_bottling_year"]= _topn_by_group(br, col_year, topn=year_topn, max_groups=max_groups)

    # vintage
    if "is_vintage" in br.columns:
        out["vintage_yes"] = br[br["is_vintage"]==True].sort_values("distance").head(10)
        out["vintage_no"]  = br[br["is_vintage"]==False].sort_values("distance").head(10)
    else:
        out["vintage_yes"] = pd.DataFrame(columns=br.columns)
        out["vintage_no"]  = pd.DataFrame(columns=br.columns)

    # rarity
    if (rare_threshold is not None):
        if (col_rarity not in br.columns) and (df_feat is not None) and (col_rarity in df_feat.columns):
            br = br.merge(df_feat[["name", col_rarity]], on="name", how="left")
        if (col_rarity in br.columns):
            r = pd.to_numeric(br[col_rarity], errors="coerce")
            out["rarity_over_threshold"] = br[r >= float(rare_threshold)]\
                .sort_values("distance").head(15)
        else:
            out["rarity_over_threshold"] = pd.DataFrame(columns=br.columns)
    else:
        out["rarity_over_threshold"] = pd.DataFrame(columns=br.columns)

    return out
