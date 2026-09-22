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
    # ---------------------------------------------------------
# 3. 총 관객 수 분포(히스토그램)
# ---------------------------------------------------------
st.header("3. 총 관객 수 분포")

hist_df = df.dropna(subset=["total_audi"]).copy()

fig_hist = px.histogram(
    hist_df,
    x="total_audi",
    nbins=30,
    title="총 관객 수 분포",
)

st.plotly_chart(fig_hist, use_container_width=True)

max_movie = hist_df.loc[hist_df["total_audi"].idxmax()]

most_common = (
    pd.cut(hist_df["total_audi"], bins=10)
    .value_counts()
    .idxmax()
)

st.info(
    f"대부분의 영화는 약 {int(most_common.left):,}명 ~ "
    f"{int(most_common.right):,}명 구간에 분포합니다.\n\n"
    f"가장 많은 관객을 모은 영화는 "
    f"'{max_movie[movie_col]}'이며 "
    f"총 {int(max_movie['total_audi']):,}명의 관객을 기록했습니다."
)
# ---------------------------------------------------------
# 4. 개봉 스크린 수와 총 관객 수의 관계
# ---------------------------------------------------------
st.header("4. 개봉 스크린 수와 총 관객 수의 관계")

scatter_df = df.dropna(
    subset=["first_scrn", "total_audi", "genre_first"]
).copy()

fig_scatter = px.scatter(
    scatter_df,
    x="first_scrn",
    y="total_audi",
    color="genre_first",
    hover_name=movie_col,
    title="개봉 스크린 수와 총 관객 수의 관계",
)

st.plotly_chart(fig_scatter, use_container_width=True)
# ---------------------------------------------------------
# 5. 장르별 총 관객 수 분포
# ---------------------------------------------------------
st.header("5. 장르별 총 관객 수 분포")

genre_count = df["genre_first"].value_counts()
valid_genres = genre_count[genre_count >= 10].index

box_df = df[
    df["genre_first"].isin(valid_genres)
].dropna(
    subset=["genre_first", "total_audi"]
).copy()

fig_box = px.box(
    box_df,
    x="genre_first",
    y="total_audi",
    color="genre_first",
    points="outliers",
    hover_name=movie_col,
)

fig_box.update_layout(showlegend=False)

st.plotly_chart(fig_box, use_container_width=True)
# ---------------------------------------------------------
# 6. 버블 그래프
# ---------------------------------------------------------
st.header("6. 버블 그래프로 보는 흥행 관계")

bubble_df = df.dropna(
    subset=[
        "first_scrn",
        "first_week_audi",
        "total_audi",
        "genre_first",
    ]
).copy()

fig_bubble = px.scatter(
    bubble_df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre_first",
    hover_name=movie_col,
    size_max=50,
    title="개봉 스크린 수, 첫 주 관객 수, 총 관객 수의 관계",
)

st.plotly_chart(fig_bubble, use_container_width=True)
# ---------------------------------------------------------
# 7. 제작 국가 → 장르 선버스트 그래프
# ---------------------------------------------------------
st.header("7. 제작 국가와 장르의 관계")

nation_col = None
for col in ["nation", "nationNm"]:
    if col in df.columns:
        nation_col = col
        break

if nation_col is not None:

    sunburst_df = df.dropna(
        subset=[nation_col, "genre_first"]
    ).copy()

    fig_sunburst = px.sunburst(
        sunburst_df,
        path=[nation_col, "genre_first"],
        title="제작 국가 → 장르 선버스트 그래프",
    )

    st.plotly_chart(fig_sunburst, use_container_width=True)
    # ---------------------------------------------------------
# 8. 오래 상영된 영화가 관객도 많을까?
# ---------------------------------------------------------
st.header("8. 오래 상영된 영화가 관객도 많을까?")

top10_df = df.dropna(
    subset=["days_in_top10", "total_audi"]
).copy()

fig_top10 = px.scatter(
    top10_df,
    x="days_in_top10",
    y="total_audi",
    color="genre_first",
    hover_name=movie_col,
    title="TOP10 유지 기간과 총 관객 수의 관계",
    labels={
        "days_in_top10": "TOP10 유지 일수",
        "total_audi": "총 관객 수",
        "genre_first": "장르",
    },
)

fig_top10.update_layout(
    legend_title="장르",
    margin=dict(t=60, b=20, l=20, r=20),
)

st.plotly_chart(fig_top10, use_container_width=True)

st.markdown("---")
st.subheader("이 그래프로 알 수 있는 것")
st.info(
    "각 점은 하나의 영화를 의미합니다. "
    "x축은 박스오피스 TOP10 안에 머문 기간(days_in_top10), "
    "y축은 총 관객 수(total_audi)입니다. "
    "오른쪽 위에 있는 영화일수록 오랫동안 인기를 유지하면서 많은 관객을 모은 영화라고 볼 수 있습니다."
)
