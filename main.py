import pandas as pd
import plotly.express as px
import streamlit as st


DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide",
)


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL, encoding="utf-8-sig")

    # 숫자형 열 변환
    numeric_cols = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 장르가 여러 개 적힌 경우 첫 번째 장르만 사용
    df["genre_first"] = (
        df["genre"]
        .fillna("미상")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    return df


st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.caption("KOBIS 영화 데이터로 살펴보는 영화의 분포와 관계")


try:
    df = load_data()
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()


# ---------------------------------------------------------
# 1. 장르별 영화 편수
# ---------------------------------------------------------
st.header("1. 장르별 영화 편수")

genre_counts = (
    df["genre_first"]
    .value_counts()
    .rename_axis("genre")
    .reset_index(name="count")
)

fig_genre = px.pie(
    genre_counts,
    names="genre",
    values="count",
    hole=0.55,
    title="장르별 영화 편수",
)

fig_genre.update_traces(
    textposition="inside",
    textinfo="percent",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "편수: %{value}편<br>"
        "비율: %{percent}<extra></extra>"
    ),
)

fig_genre.update_layout(
    legend_title="장르",
    margin=dict(t=60, b=20, l=20, r=20),
)

st.plotly_chart(fig_genre, use_container_width=True)

st.markdown("---")
st.subheader("이 그래프로 알 수 있는 것")
st.info(
    "영화 데이터에서 어떤 장르의 영화가 많이 포함되어 있고, "
    "각 장르가 전체 영화에서 어느 정도의 비중을 차지하는지 알 수 있습니다."
)


# ---------------------------------------------------------
# 2. 장르 안의 영화 트리맵
# ---------------------------------------------------------
st.header("2. 장르별 영화 관객 수 트리맵")

# 영화명 열 찾기
movie_col = None
for col in ["movieNm", "movie_nm", "title", "movie_name"]:
    if col in df.columns:
        movie_col = col
        break

if movie_col is None:
    st.error("영화명 열을 찾을 수 없습니다.")
else:
    treemap_df = df.dropna(subset=[movie_col, "total_audi"]).copy()

    fig_treemap = px.treemap(
        treemap_df,
        path=["genre_first", movie_col],
        values="total_audi",
        title="장르별 영화 관객 수 트리맵",
    )

    fig_treemap.update_traces(
        hovertemplate=(
            "<b>%{label}</b><br>"
            "총 관객 수: %{value:,}명"
            "<extra></extra>"
        )
    )

    fig_treemap.update_layout(
        margin=dict(t=60, b=20, l=20, r=20)
    )

    st.plotly_chart(fig_treemap, use_container_width=True)

    st.markdown("---")
    st.subheader("이 그래프로 알 수 있는 것")
    st.info(
        "장르별로 어떤 영화가 많은 관객을 모았는지 확인할 수 있습니다. "
        "칸이 클수록 총 관객 수(total_audi)가 많은 영화입니다."
    )
