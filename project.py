import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

st.set_page_config(
    page_title="국민연금 투자 추종 가이드",
    page_icon="📊",
    layout="wide",
)

# ── 공통 색상 ──────────────────────────────────────────────
BUY_COLOR = "#2962FF"
SELL_COLOR = "#D32F2F"
MKT_COLOR = "#78909C"
EXCESS_COLOR = "#00897B"

# ── 데이터 로드 ────────────────────────────────────────────
@st.cache_data
def load_data():
    perf   = pd.read_csv("국민연금_통합_성과분석_90_360.csv",       encoding="utf-8-sig")
    holds  = pd.read_csv("국민연금_대량보유주식_통합_최종본_정렬.csv",  encoding="utf-8-sig")
    assets = pd.read_csv("운용 자산별 성과정보_통합.csv",             encoding="utf-8-sig")
    port   = pd.read_csv("국내주식_통합_사명변경_1.csv",              encoding="utf-8-sig")
    price  = pd.read_csv("국민연금_기간별_주가추적_리스트.csv",        encoding="utf-8-sig")
    holds["날짜"] = pd.to_datetime(holds["날짜"])
    perf["변동일자"] = pd.to_datetime(perf["변동일자"])
    return perf, holds, assets, port, price

perf, holds, assets, port, price = load_data()

PERIODS = ["90일", "180일", "270일", "360일"]
buy_df  = perf[perf["매수매도"] == "매수"]
sell_df = perf[perf["매수매도"] == "매도"]

# ══════════════════════════════════════════════════════════
# 헤더
# ══════════════════════════════════════════════════════════
st.markdown("""
<h1 style='text-align:center; font-size:2.4rem; margin-bottom:0'>
    📊 국민연금 공시 추종 투자 가이드
</h1>
<p style='text-align:center; color:#666; font-size:1.05rem; margin-top:6px'>
    국민연금이 사고 판 종목을 따라 살 때 — <b>언제</b> 매수·매도해야 수익이 날까?
</p>
""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════════
# 섹션 0: 프로젝트 개요
# ══════════════════════════════════════════════════════════
with st.container():
    st.markdown("## 프로젝트 개요")
    col1, col2, col3 = st.columns(3)
    col1.info("**공시 규칙**\n\n국민연금은 지분율 **5% 이상** 종목이거나, 해당 종목에서 **1%p 이상** 변동 시 의무 공시")
    col2.info("**공시 지연**\n\n공시는 변동 발생 후 최대 **90일** 내 이루어짐 → 개인 투자자는 90일 늦은 정보를 받는 셈")
    col3.info("**이 분석의 질문**\n\n공시 후 **90 / 180 / 270 / 360일** 중 어느 시점에 따라 사고 팔아야 가장 유리한가?")

st.divider()

# ══════════════════════════════════════════════════════════
# 섹션 1: 국민연금 국내주식 포트폴리오 현황
# ══════════════════════════════════════════════════════════
st.markdown("## 1. 국민연금 국내주식 포트폴리오 현황")

latest_year = int(port["기준일"].max())
port_latest = port[port["기준일"] == latest_year].copy()

col_l, col_r = st.columns([1.2, 1])

with col_l:
    st.markdown(f"#### Top 10 보유 종목 ({latest_year}년 기준)")
    top10 = port_latest.nlargest(10, "평가액(억 원)").reset_index(drop=True)
    fig_bar = go.Figure(go.Bar(
        x=top10["평가액(억 원)"],
        y=top10["종목명"],
        orientation="h",
        marker_color=BUY_COLOR,
        text=top10["평가액(억 원)"].apply(lambda v: f"{v:,.0f}억"),
        textposition="outside",
    ))
    fig_bar.update_layout(
        height=380,
        margin=dict(l=10, r=80, t=10, b=10),
        xaxis_title="평가액 (억 원)",
        yaxis=dict(autorange="reversed"),
        plot_bgcolor="white",
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_r:
    st.markdown(f"#### 연도별 Top5 포트폴리오 변화")
    years = sorted(port["기준일"].unique())
    colors = px.colors.qualitative.Set2
    fig_trend = go.Figure()
    for i, yr in enumerate(years):
        yr_df = port[port["기준일"] == yr].nlargest(5, "평가액(억 원)")
        fig_trend.add_trace(go.Bar(
            name=str(yr),
            x=yr_df["종목명"],
            y=yr_df["평가액(억 원)"],
            marker_color=colors[i % len(colors)],
        ))
    fig_trend.update_layout(
        barmode="group",
        height=380,
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis_title="평가액 (억 원)",
        legend=dict(orientation="h", y=1.1),
        plot_bgcolor="white",
    )
    st.plotly_chart(fig_trend, use_container_width=True)

# 지분율 & 비중 요약
st.markdown("#### 평균 지분율 및 자산군 내 비중 추이")
port_agg = port.groupby("기준일").agg(
    평균지분율=("지분율(퍼센트)", "mean"),
    평균비중=("자산군 내 비중(퍼센트)", "mean"),
    종목수=("종목명", "count"),
).reset_index()

fig_stat = make_subplots(specs=[[{"secondary_y": True}]])
fig_stat.add_trace(go.Scatter(
    x=port_agg["기준일"], y=port_agg["평균지분율"],
    name="평균 지분율 (%)", mode="lines+markers", line=dict(color=BUY_COLOR, width=2.5),
), secondary_y=False)
fig_stat.add_trace(go.Bar(
    x=port_agg["기준일"], y=port_agg["종목수"],
    name="보유 종목 수", marker_color="#BBDEFB", opacity=0.6,
), secondary_y=True)
fig_stat.update_layout(
    height=300, margin=dict(l=10, r=10, t=10, b=10),
    plot_bgcolor="white", legend=dict(orientation="h", y=1.1),
)
fig_stat.update_yaxes(title_text="평균 지분율 (%)", secondary_y=False)
fig_stat.update_yaxes(title_text="보유 종목 수", secondary_y=True)
st.plotly_chart(fig_stat, use_container_width=True)

st.divider()

# ══════════════════════════════════════════════════════════
# 섹션 2: 국민연금 운용 성과
# ══════════════════════════════════════════════════════════
st.markdown("## 2. 국민연금 국내주식 운용 성과")

domestic = assets[assets["구분"] == "금융부문(국내주식)"].copy()
domestic["기준년월"] = pd.to_datetime(domestic["기준년월"])

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("#### 기간 수익률 추이 (국내주식)")
    fig_ret = go.Figure()
    fig_ret.add_trace(go.Scatter(
        x=domestic["기준년월"], y=domestic["기간수익률"],
        mode="lines", fill="tozeroy",
        line=dict(color=BUY_COLOR, width=2),
        fillcolor="rgba(41,98,255,0.12)",
        name="기간수익률",
    ))
    fig_ret.add_hline(y=0, line_dash="dash", line_color="#999", line_width=1)
    fig_ret.update_layout(
        height=300, margin=dict(l=10, r=10, t=10, b=10),
        yaxis_title="수익률 (%)", plot_bgcolor="white",
    )
    st.plotly_chart(fig_ret, use_container_width=True)

with col_b:
    st.markdown("#### 전년도 vs 3개년 수익률")
    fig_comp = go.Figure()
    fig_comp.add_trace(go.Scatter(
        x=domestic["기준년월"], y=domestic["전년도수익률"],
        mode="lines", name="전년도 수익률", line=dict(color=BUY_COLOR, width=2),
    ))
    fig_comp.add_trace(go.Scatter(
        x=domestic["기준년월"], y=domestic["3개년수익률"],
        mode="lines", name="3개년 수익률", line=dict(color=EXCESS_COLOR, width=2),
    ))
    fig_comp.add_hline(y=0, line_dash="dash", line_color="#999", line_width=1)
    fig_comp.update_layout(
        height=300, margin=dict(l=10, r=10, t=10, b=10),
        yaxis_title="수익률 (%)", plot_bgcolor="white",
        legend=dict(orientation="h", y=1.1),
    )
    st.plotly_chart(fig_comp, use_container_width=True)

# 가장 최근 지표 요약
latest_perf = domestic.sort_values("기준년월").iloc[-1]
m1, m2, m3, m4 = st.columns(4)
m1.metric("최근 기간수익률", f"{latest_perf['기간수익률']:.2f}%")
m2.metric("전년도 수익률",   f"{latest_perf['전년도수익률']:.2f}%")
m3.metric("3개년 수익률",    f"{latest_perf['3개년수익률']:.2f}%")
m4.metric("설정후 수익률",   f"{latest_perf['설정후수익률']:.2f}%")

st.divider()

# ══════════════════════════════════════════════════════════
# 섹션 3: 핵심 — 공시 추종 전략 수익률 분석
# ══════════════════════════════════════════════════════════
st.markdown("## 3. 핵심 분석 — 공시 후 언제 사고 팔아야 하는가?")

st.markdown("""
> 국민연금이 **매수 공시**를 낸 종목을 개인이 따라 살 때,
> 공시 후 **90 / 180 / 270 / 360일** 시점에 매도하면 각각 얼마나 벌 수 있는지 비교합니다.
""")

# ── 3-A: 기간별 평균 수익률 비교 (매수 vs 매도 신호) ──────
st.markdown("### 3-A. 공시 유형별 평균 수익률")

rows = []
for p in PERIODS:
    col_r = f"{p}_수익률"
    col_m = f"{p}_시장수익률"
    col_e = f"{p}_초과수익률"
    rows.append({
        "기간": p,
        "매수신호_수익률": buy_df[col_r].mean(),
        "매도신호_수익률": sell_df[col_r].mean(),
        "시장수익률":      buy_df[col_m].mean(),
        "매수신호_초과":   buy_df[col_e].mean(),
        "매도신호_초과":   sell_df[col_e].mean(),
    })
stat = pd.DataFrame(rows)

fig_main = make_subplots(
    rows=1, cols=2,
    subplot_titles=["기간별 평균 수익률 (절대)", "기간별 평균 초과수익률 (시장 대비)"],
)

# 절대 수익률
fig_main.add_trace(go.Bar(
    x=stat["기간"], y=(stat["매수신호_수익률"] * 100).round(2),
    name="매수 공시 후", marker_color=BUY_COLOR, text=(stat["매수신호_수익률"] * 100).round(1).astype(str) + "%",
    textposition="outside",
), row=1, col=1)
fig_main.add_trace(go.Bar(
    x=stat["기간"], y=(stat["매도신호_수익률"] * 100).round(2),
    name="매도 공시 후", marker_color=SELL_COLOR, text=(stat["매도신호_수익률"] * 100).round(1).astype(str) + "%",
    textposition="outside",
), row=1, col=1)
fig_main.add_trace(go.Scatter(
    x=stat["기간"], y=(stat["시장수익률"] * 100).round(2),
    name="시장(KOSPI)", mode="lines+markers", line=dict(color=MKT_COLOR, width=2.5, dash="dot"),
), row=1, col=1)

# 초과 수익률
fig_main.add_trace(go.Bar(
    x=stat["기간"], y=(stat["매수신호_초과"] * 100).round(2),
    name="매수 초과", marker_color=BUY_COLOR, showlegend=False,
    text=(stat["매수신호_초과"] * 100).round(1).astype(str) + "%",
    textposition="outside",
), row=1, col=2)
fig_main.add_trace(go.Bar(
    x=stat["기간"], y=(stat["매도신호_초과"] * 100).round(2),
    name="매도 초과", marker_color=SELL_COLOR, showlegend=False,
    text=(stat["매도신호_초과"] * 100).round(1).astype(str) + "%",
    textposition="outside",
), row=1, col=2)
fig_main.add_hline(y=0, line_dash="dash", line_color="#999", row=1, col=2)

fig_main.update_layout(
    height=420, barmode="group",
    margin=dict(l=10, r=10, t=40, b=10),
    plot_bgcolor="white",
    legend=dict(orientation="h", y=-0.12, x=0.3),
)
fig_main.update_yaxes(ticksuffix="%")
st.plotly_chart(fig_main, use_container_width=True)

# ── 3-B: 승률 분석 ────────────────────────────────────────
st.markdown("### 3-B. 수익 달성 승률 (수익률 > 0%)")

win_rows = []
for p in PERIODS:
    col_r = f"{p}_수익률"
    col_e = f"{p}_초과수익률"
    win_rows.append({
        "기간": p,
        "매수_절대승률":  (buy_df[col_r] > 0).mean() * 100,
        "매도_절대승률":  (sell_df[col_r] > 0).mean() * 100,
        "매수_초과승률":  (buy_df[col_e] > 0).mean() * 100,
        "매도_초과승률":  (sell_df[col_e] > 0).mean() * 100,
    })
win = pd.DataFrame(win_rows)

fig_win = make_subplots(rows=1, cols=2,
    subplot_titles=["절대 수익 달성 승률", "시장 초과 달성 승률"])

for col_name, col_idx, buy_col, sell_col in [
    ("절대", 1, "매수_절대승률", "매도_절대승률"),
    ("초과", 2, "매수_초과승률", "매도_초과승률"),
]:
    fig_win.add_trace(go.Scatter(
        x=win["기간"], y=win[buy_col].round(1),
        name="매수 공시", mode="lines+markers+text",
        text=win[buy_col].round(1).astype(str) + "%",
        textposition="top center",
        line=dict(color=BUY_COLOR, width=2.5),
        marker=dict(size=10),
        showlegend=(col_idx == 1),
    ), row=1, col=col_idx)
    fig_win.add_trace(go.Scatter(
        x=win["기간"], y=win[sell_col].round(1),
        name="매도 공시", mode="lines+markers+text",
        text=win[sell_col].round(1).astype(str) + "%",
        textposition="bottom center",
        line=dict(color=SELL_COLOR, width=2.5),
        marker=dict(size=10),
        showlegend=(col_idx == 1),
    ), row=1, col=col_idx)
    fig_win.add_hline(y=50, line_dash="dash", line_color="#aaa", row=1, col=col_idx)

fig_win.update_layout(
    height=380, margin=dict(l=10, r=10, t=40, b=10),
    plot_bgcolor="white",
    legend=dict(orientation="h", y=-0.15, x=0.35),
)
fig_win.update_yaxes(ticksuffix="%", range=[25, 60])
st.plotly_chart(fig_win, use_container_width=True)

# ── 3-C: 섹터별 초과수익률 히트맵 ─────────────────────────
st.markdown("### 3-C. 섹터별 초과수익률 히트맵 (매수 공시 기준)")

sector_rows = []
for sector in perf["섹터"].unique():
    s_buy = buy_df[buy_df["섹터"] == sector]
    row = {"섹터": sector}
    for p in PERIODS:
        row[p] = round(s_buy[f"{p}_초과수익률"].mean() * 100, 2) if len(s_buy) > 0 else np.nan
    sector_rows.append(row)

sector_df = pd.DataFrame(sector_rows).set_index("섹터").dropna(how="all")
sector_df = sector_df.sort_values("360일", ascending=False)

fig_heat = go.Figure(go.Heatmap(
    z=sector_df.values,
    x=sector_df.columns.tolist(),
    y=sector_df.index.tolist(),
    colorscale="RdYlGn",
    zmid=0,
    text=sector_df.round(1).values,
    texttemplate="%{text}%",
    colorbar=dict(title="초과수익률(%)"),
))
fig_heat.update_layout(
    height=380,
    margin=dict(l=10, r=10, t=10, b=10),
)
st.plotly_chart(fig_heat, use_container_width=True)

st.divider()

# ══════════════════════════════════════════════════════════
# 섹션 4: 대량보유 공시 현황
# ══════════════════════════════════════════════════════════
st.markdown("## 4. 국민연금 대량보유 공시 현황")

col_h1, col_h2 = st.columns(2)

with col_h1:
    st.markdown("#### 최근 공시 내역 (최신 30건)")
    recent = holds.sort_values("날짜", ascending=False).head(30).reset_index(drop=True)
    recent["날짜"] = recent["날짜"].dt.strftime("%Y-%m-%d")
    st.dataframe(
        recent.style.background_gradient(subset=["지분율(퍼센트)"], cmap="Blues"),
        use_container_width=True, height=380,
    )

with col_h2:
    st.markdown("#### 연도별 공시 건수")
    holds["연도"] = holds["날짜"].dt.year
    yearly = holds.groupby("연도").size().reset_index(name="공시건수")
    fig_ycnt = go.Figure(go.Bar(
        x=yearly["연도"].astype(str), y=yearly["공시건수"],
        marker_color=BUY_COLOR,
        text=yearly["공시건수"], textposition="outside",
    ))
    fig_ycnt.update_layout(
        height=220,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="white",
        yaxis_title="공시 건수",
    )
    st.plotly_chart(fig_ycnt, use_container_width=True)

    st.markdown("#### 지분율 분포")
    fig_hist = go.Figure(go.Histogram(
        x=holds["지분율(퍼센트)"],
        nbinsx=30,
        marker_color=BUY_COLOR,
        opacity=0.8,
    ))
    fig_hist.update_layout(
        height=180,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="white",
        xaxis_title="지분율 (%)",
        yaxis_title="건수",
    )
    st.plotly_chart(fig_hist, use_container_width=True)

st.divider()

# ══════════════════════════════════════════════════════════
# 섹션 5: 종목 탐색기
# ══════════════════════════════════════════════════════════
st.markdown("## 5. 종목별 주가 추적 탐색기")

all_stocks = sorted(price["종목명"].unique())
selected = st.selectbox("종목을 선택하세요", all_stocks)

stock_perf = perf[perf["종목명"] == selected]
stock_price = price[price["종목명"] == selected]

if not stock_price.empty:
    sp = stock_price.iloc[0]
    col_s1, col_s2 = st.columns(2)

    with col_s1:
        st.markdown(f"#### {selected} — 공시 후 주가 변화")
        price_vals = {
            "공시 기준가": sp["기준주가"],
            "90일 후":    sp["90일후_주가"],
            "180일 후":   sp["180일후_주가"],
            "270일 후":   sp["270일후_주가"],
            "360일 후":   sp["360일후_주가"],
        }
        valid_prices = {k: v for k, v in price_vals.items() if pd.notna(v)}
        if valid_prices:
            base = sp["기준주가"]
            labels = list(valid_prices.keys())
            vals   = list(valid_prices.values())
            changes = [(v / base - 1) * 100 for v in vals]
            bar_colors = [BUY_COLOR if c >= 0 else SELL_COLOR for c in changes]
            fig_sp = go.Figure()
            fig_sp.add_trace(go.Scatter(
                x=labels, y=vals, mode="lines+markers",
                line=dict(color=BUY_COLOR, width=2.5), marker=dict(size=10),
            ))
            for lbl, val in zip(labels, vals):
                fig_sp.add_annotation(x=lbl, y=val, text=f"{val:,.0f}원",
                    showarrow=False, yshift=14, font=dict(size=11))
            fig_sp.update_layout(
                height=300, margin=dict(l=10, r=10, t=10, b=10),
                plot_bgcolor="white", yaxis_title="주가 (원)",
            )
            st.plotly_chart(fig_sp, use_container_width=True)

    with col_s2:
        st.markdown(f"#### 기준 대비 등락률")
        if valid_prices:
            fig_chg = go.Figure(go.Bar(
                x=labels, y=changes,
                marker_color=bar_colors,
                text=[f"{c:+.1f}%" for c in changes],
                textposition="outside",
            ))
            fig_chg.add_hline(y=0, line_dash="dash", line_color="#999")
            fig_chg.update_layout(
                height=300, margin=dict(l=10, r=10, t=10, b=10),
                plot_bgcolor="white", yaxis_title="등락률 (%)",
            )
            st.plotly_chart(fig_chg, use_container_width=True)

    # 해당 종목 공시 히스토리
    if not stock_perf.empty:
        st.markdown(f"#### {selected} 공시 이력")
        disp = stock_perf[["변동일자", "섹터", "매수매도",
                            "90일_수익률", "180일_수익률", "270일_수익률", "360일_수익률",
                            "90일_초과수익률", "360일_초과수익률"]].copy()
        disp["변동일자"] = disp["변동일자"].dt.strftime("%Y-%m-%d")
        for c in ["90일_수익률", "180일_수익률", "270일_수익률", "360일_수익률",
                  "90일_초과수익률", "360일_초과수익률"]:
            disp[c] = (disp[c] * 100).round(2)
        st.dataframe(disp, use_container_width=True)

st.divider()

# ══════════════════════════════════════════════════════════
# 섹션 6: 투자 결론
# ══════════════════════════════════════════════════════════
st.markdown("## 6. 투자 결론 및 가이드라인")

# 결론 계산
best_period = stat.loc[stat["매수신호_수익률"].idxmax(), "기간"]
best_return  = stat["매수신호_수익률"].max() * 100
best_excess  = stat.loc[stat["매수신호_수익률"].idxmax(), "매수신호_초과"] * 100
best_win_row = win.loc[win["매수_절대승률"].idxmax()]

col_c1, col_c2, col_c3, col_c4 = st.columns(4)
col_c1.metric("최고 평균 수익률 시점", best_period, f"{best_return:.1f}%")
col_c2.metric("해당 시점 초과수익률", "", f"{best_excess:+.1f}%")
col_c3.metric("최고 승률 시점", best_win_row["기간"], f"{best_win_row['매수_절대승률']:.1f}%")
col_c4.metric("분석 공시 건수", f"{len(perf):,}건")

st.markdown("---")

st.markdown(f"""
### 핵심 요약

| 항목 | 내용 |
|------|------|
| **공시 후 최고 수익 시점** | {best_period} 보유 후 평균 {best_return:.1f}% 수익 |
| **시장 대비 초과수익** | {best_excess:+.1f}%p (시장 수익률보다 낮은 경향) |
| **매수 vs 매도 공시** | 매수 공시 종목이 매도 공시 종목 대비 모든 기간에서 높은 수익률 |
| **시장 초과 달성 확률** | 전 기간 50% 미만 → 국민연금 공시만으로 시장 이기기 어려움 |

### 개인 투자자 가이드

1. **단기 (90일)**: 평균 수익률이 가장 낮고 변동성 크다. 국민연금 공시 직후 추종은 비효율적.
2. **중기 (180~270일)**: 수익률이 본격 상승하는 구간. 공시 확인 후 6~9개월 보유 전략 유효.
3. **장기 (360일)**: 평균 수익률 최대. 다만 시장 수익률에는 못 미치므로 **종목 선별이 핵심**.
4. **섹터 선택**: 초과수익률이 양수인 섹터(히트맵 참고)에 집중하면 승률 개선 가능.
5. **공시 신뢰도**: 국민연금의 국내주식 전년도 수익률 추이를 함께 확인해 시장 국면을 파악할 것.
""")

st.caption("데이터 출처: 국민연금공단 공시 정보 | 분석 기간: 2022~2025 | 본 자료는 투자 참고용이며 투자 손익에 대한 책임은 투자자 본인에게 있습니다.")
 