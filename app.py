from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import os

app = Flask(__name__)
#CORS(app)


# CORS 설정: 개발용으로 모든 도메인 허용. 배포 시에는 특정 도메인만 허용하도록 수정 필요.
#CORS(app, resources={r"/api/*": {"origins": ["http://127.0.0.1:5500", "http://localhost:5500", "http://127.0.0.1:8080"]}})

# 루트 경로 엔드포인트
@app.route('/')
def home():
    return "Flask 서버가 실행 중입니다."

# Favicon 요청 처리
@app.route('/favicon.ico')
def favicon():
    return '', 204  # 또는 app.send_static_file('favicon.ico')



# 파일 경로 설정
base_dir = os.path.dirname(os.path.abspath(__file__))
card_data_path = os.path.join(base_dir, 'mnt/data/데이터 카드1234.xlsx')
cluster_paths = {i: os.path.join(base_dir, f'mnt/data/encoding_cluster_{i}.csv') for i in [0, 1, 2, 3]}

try:
    card_df = pd.read_excel(card_data_path, engine='openpyxl')
    cluster_data = {key: pd.read_csv(path, encoding='ANSI') for key, path in cluster_paths.items()}
except FileNotFoundError as e:
    raise RuntimeError(f"필요한 파일이 없습니다: {e}")

card_df['소비관광지역명칭'] = card_df['소비관광지역명칭'].str.replace(r'\(.*?\)', '', regex=True).str.replace(r'\s+', '', regex=True)
# 범주화 사전 정의
category_mapping = {
    '유흥': '유흥',
    '외식업기타': '외식',
    '중식/일식/양식': '외식',
    '한식': '외식',
    '음/식료품': '소매/쇼핑',
    '할인점/슈퍼마켓': '소매/쇼핑',
    '백화점/면세점': '소매/쇼핑',
    '숙박': '숙박',
    '스포츠/문화/레저': '스포츠 및 문화'
}

# 데이터프레임의 카테고리 열 범주화
card_df['대분류'] = card_df['대분류'].map(category_mapping)


industry_group = card_df.groupby(["소비관광지역명칭", "대분류"]).agg({
    "카드이용금액_업종별": "sum",
    "카드이용건수_업종별": "sum"
}).reset_index()
industry_group['평균 소비 금액_업종'] = (industry_group['카드이용금액_업종별'] / industry_group['카드이용건수_업종별']).round(0)
industry_group = industry_group[['소비관광지역명칭', '대분류', '평균 소비 금액_업종']]

gender_age_group = card_df.groupby(["소비관광지역명칭", "성별", "연령대"]).agg({
    "카드이용금액_성별연령별": "sum",
    "카드이용건수_성별연령별": "sum"
}).reset_index()

gender_age_group['평균 소비 금액_성별연령별'] = (gender_age_group['카드이용금액_성별연령별'] / gender_age_group['카드이용건수_성별연령별']).round(0)
gender_age_group = gender_age_group[['소비관광지역명칭', '성별', '연령대', '평균 소비 금액_성별연령별']]



industry_vector = industry_group.pivot_table(
    index='소비관광지역명칭',
    columns='대분류',
    values= '평균 소비 금액_업종',
    aggfunc='sum',
    fill_value=0
)
industry_vector = industry_vector.reset_index()  # 기존 인덱스가 소비관광지역명칭이라면 리셋
industry_vector.columns = ["소비관광지역명칭", "소매/쇼핑", "숙박", "스포츠 및 문화", "외식", "유흥"]
industry_vector.rename(columns={"소비관광지역명칭": "관광지"}, inplace=True)

demographic_vector = gender_age_group.pivot_table(
    index='소비관광지역명칭',
    columns= ['성별', '연령대'],
    values= '평균 소비 금액_성별연령별',
    aggfunc='sum',
    fill_value=0
)


# 유사도 계산 함수
def calculate_similarity(user_vector, region_vector, weights):
    valid_indices = np.where((user_vector != 0) & (region_vector != 0))[0]
    if len(valid_indices) == 0:
        return 0
    filtered_user_vector = user_vector[valid_indices]
    filtered_region_vector = region_vector[valid_indices]
    filtered_weights = weights[valid_indices]
    weighted_user_vector = filtered_user_vector * filtered_weights
    weighted_region_vector = filtered_region_vector * filtered_weights
    return cosine_similarity(
        weighted_user_vector.reshape(1, -1),
        weighted_region_vector.reshape(1, -1)
    )[0][0]

# 나이대 변환 함수
def map_age_range(age_input):
    if age_input < 20:
        return 20
    elif age_input < 30:
        return 20
    elif age_input < 40:
        return 30
    elif age_input < 50:
        return 40
    elif age_input < 60:
        return 50
    else:
        return 60



@app.route('/api/recommend', methods=['POST'])
def recommend():
    try:
        # 요청 데이터 받기
        user_data = request.json
        print(f"[REQUEST RECEIVED] 요청 데이터: {user_data}")

        cluster = user_data.get('cluster')
        age = user_data.get('age')
        gender = user_data.get('gender')
        spending = user_data.get('spending')


        # 클러스터와 나이 값 검증
        if cluster not in cluster_data or age < 0 or age > 120:
            return jsonify({"error": "입력 값이 비정상적입니다."}), 400


        # 나이대 변환
        age_group = map_age_range(age)
        print(f"[INFO] Mapped age {age} to age group {age_group}")

        # spending 데이터 처리
        if not isinstance(spending, dict):
            return jsonify({"error": "spending 데이터는 dict 형식이어야 합니다."}), 400

        selected_cluster = cluster_data[cluster]
        tourist_spots = selected_cluster["관광지"].unique()

        # 업종별 데이터 필터링
        filtered_card_data_업종별 = industry_vector[industry_vector["관광지"].isin(tourist_spots)]

        # 성별/연령별 데이터 필터링
        filtered_card_data_성별연령별 = demographic_vector.loc[
            demographic_vector.index.isin(tourist_spots), (gender, age_group)
        ].reset_index()

        filtered_card_data_성별연령별.columns = ["소비관광지역명칭", "소비벡터"]


        # Step 1: 사용자 소비 벡터화
        user_vector = np.array([
            spending.get("소매/쇼핑", 0),
            spending.get("숙박", 0),
            spending.get("스포츠 및 문화", 0),
            spending.get("외식", 0),
            spending.get("유흥", 0)
        ]).reshape(1, -1)

        # MinMaxScaler로 demographic_weights 스케일링
        scaler = MinMaxScaler()
        weights = scaler.fit_transform(filtered_card_data_성별연령별['소비벡터'].to_numpy().reshape(-1, 1)).flatten()
        alpha = 0.9
        adjusted_weights = 1 + alpha * (weights - 1)

        # Step 2: 유사도 계산
        similarity_results = []
        for _, row in filtered_card_data_업종별.iterrows():
            region_vector = row[1:].to_numpy()  # 관광지 벡터
            similarity = calculate_similarity(user_vector.flatten(), region_vector, adjusted_weights).round(4)
            similarity_results.append({"관광지": row["관광지"], "유사도": similarity})

        # Step 3: 결과 정리
        similarity_df = pd.DataFrame(similarity_results).sort_values(by="유사도", ascending=False)
        top_tourist_spots = similarity_df["관광지"].head(5).tolist()

        # 클러스터 데이터에서 top_tourist_spots에 해당하는 행 필터링
        filtered_cluster = selected_cluster[selected_cluster["관광지"].isin(top_tourist_spots)]
        unique_filtered_cluster = filtered_cluster.drop_duplicates(subset=["관광지", "가맹점명"])

        final_result = pd.merge(
            unique_filtered_cluster,
            similarity_df[["관광지", "유사도"]],
            on="관광지",
            how="inner"
        )


        final_output = final_result[[
            "ID", "분류", "관광지", "가맹점명", "가게 이미지 URL", "별점", "리뷰 수", "주소", "위치값 주소", "위도", "경도", "유사도"
        ]].sort_values(by="유사도", ascending=False)




        response = final_output.to_dict(orient='records')
        print(f"[RESPONSE SENT] 응답 데이터: {response}")
        return jsonify(response)

    except Exception as e:
        print(f"[ERROR] 서버 오류 발생: {str(e)}")
        return jsonify({"error": "서버 처리 중 오류 발생", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
