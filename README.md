
1. 프로젝트 개요 (Project Overview)

2. 데이터 (Data)

3. 방법론 (Methodology)

4. 결과 (Results)

5. 활용 방안 (Applications)



7. 디렉토리 구조 (Project Structure)
```
whisky-project/
├── 01_data_collection.ipynb        # 데이터 수집 & 정리
├── 02_data_preprocessing.ipynb     # 전처리 & 결측치/스케일링 처리
├── 03_feature_engineering.ipynb    # 맛 노트 텍스트 임베딩, 스타일 변수 생성
├── 04_exploratory_analysis.ipynb   # EDA, 시각화 (풍미 분포, 국가별 비교)
├── 05_clustering_analysis.ipynb    # KMeans, DBSCAN, PCA/t-SNE 시각화
├── 06_recommendation_system.ipynb  # TF-IDF+KNN, CF, Hybrid 추천 구현
├── 07_evaluation_metrics.ipynb     # 추천 성능 평가 (NDCG, MAP, coverage 등)
├── 08_business_strategy.ipynb      # 진열 최적화, 고객 접점 전략 설계
│
├── data/                           # 원본/전처리 데이터
│   ├── raw/
│   ├── processed/
│
├── utils/                          # 공통 함수 모듈
│   ├── text_cleaning.py
│   ├── clustering_helpers.py
│   ├── recommender_helpers.py
│
├── results/                        # 시각화 이미지, 결과 CSV
│
└── README.md                       # 프로젝트 설명
```
