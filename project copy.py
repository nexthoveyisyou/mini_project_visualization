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

BUY_COLOR  = "#2962FF"
SELL_COLOR = "#D32F2F"
MKT_COLOR  = "#78909C"
EXCESS_COLOR = "#00897B"

def chart_tip(text):
    st.markdown(f"""
    <div style='background:#f0f7ff; border-left:4px solid #2962FF;
                padding:10px 16px; border-radius:0 6px 6px 0;
                margin-top:2px; margin-bottom:18px;
                font-size:0.88rem; color:#333; line-height:1.7;'>
    📖 <b>이 차트 읽는 법</b><br>{text}
    </div>
    """, unsafe_allow_html=True)

def style_trade(df, col="매수매도"):
    def row_color(row):
        if col in row.index and row[col] == "매수":
            return ["background-color:#EEF2FF"] * len(row)
        elif col in row.index and row[col] == "매도":
            return ["background-color:#FFF0F0"] * len(row)
        return [""] * len(row)

    def col_color(s):
        return [
            "background-color:#1565C0; color:white; font-weight:bold; text-align:center" if v == "매수"
            else ("background-color:#C62828; color:white; font-weight:bold; text-align:center" if v == "매도" else "")
            for v in s
        ]

    styled = df.style.apply(row_color, axis=1)
    if col in df.columns:
        styled = styled.apply(col_color, subset=[col])
    return styled

@st.cache_data
def load_data():
    perf   = pd.read_csv("국민연금_기간별_성과분석_통합_진짜.csv",       encoding="utf-8-sig")
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
st.markdown("## 프로젝트 개요")
col1, col2, col3 = st.columns(3)
col1.info("**공시 규칙**\n\n국민연금은 지분율 **5% 이상** 종목이거나, 해당 종목에서 **1%p 이상** 변동 시 의무 공시")
col2.info("**공시 지연**\n\n공시는 변동 발생 후 최대 **90일** 내 이루어짐 → 개인 투자자는 90일 늦은 정보를 받는 셈")
col3.info("**이 분석의 질문**\n\n공시 후 **90 / 180 / 270 / 360일** 중 어느 시점에 따라 사고 팔아야 가장 유리한가?")

st.markdown("#### 📅 공시 지연 타임라인 — 개인 투자자가 정보를 받는 순서")
st.markdown("""
<div style='display:flex; align-items:center; justify-content:center; gap:0;
            padding:20px; background:#FAFAFA; border-radius:12px; margin-bottom:4px; flex-wrap:wrap;'>
    <div style='text-align:center; padding:10px 18px; background:#1565C0; color:white; border-radius:8px; min-width:110px;'>
        <div style='font-size:1.4rem'>🏦</div>
        <b>국민연금 매매</b><br><small>D day</small>
    </div>
    <div style='color:#bbb; font-size:1.8rem; padding:0 10px'>→</div>
    <div style='text-align:center; padding:10px 18px; background:#E65100; color:white; border-radius:8px; min-width:110px;'>
        <div style='font-size:1.4rem'>📋</div>
        <b>공시 의무 기한</b><br><small>최대 D+90일</small>
    </div>
    <div style='color:#bbb; font-size:1.8rem; padding:0 10px'>→</div>
    <div style='text-align:center; padding:10px 18px; background:#2E7D32; color:white; border-radius:8px; min-width:110px;'>
        <div style='font-size:1.4rem'>👀</div>
        <b>개인 투자자 확인</b><br><small>D+90일 이후</small>
    </div>
    <div style='color:#bbb; font-size:1.8rem; padding:0 10px'>→</div>
    <div style='text-align:center; padding:10px 18px; background:#6A1B9A; color:white; border-radius:8px; min-width:110px;'>
        <div style='font-size:1.4rem'>💰</div>
        <b>매수 후 보유</b><br><small>D+90~450일</small>
    </div>
</div>
""", unsafe_allow_html=True)
chart_tip("국민연금이 주식을 사고 판 뒤 <b>최대 90일이 지나서야 공시</b>가 됩니다. 즉, 개인 투자자는 항상 '90일 늦은 정보'를 보는 셈이에요. 그래도 공시 후 얼마나 오래 보유하느냐에 따라 수익이 달라질 수 있습니다!")

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
    chart_tip("막대가 <b>길수록</b> 국민연금이 더 많은 돈을 투자한 종목입니다. 상위 종목일수록 국민연금이 장기적으로 신뢰하는 대형 우량주일 가능성이 높습니다.")

with col_r:
    st.markdown("#### 연도별 Top5 포트폴리오 변화")
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
    chart_tip("연도별로 <b>색깔이 다른 막대</b>를 비교하면 포트폴리오가 어떻게 바뀌었는지 알 수 있습니다. 같은 종목이 계속 상위권에 있다면 국민연금이 장기적으로 신뢰하는 종목입니다.")

st.markdown("#### 평균 지분율 및 보유 종목 수 추이")
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
chart_tip("<b>파란 선(지분율)</b>: 국민연금이 각 종목 주식을 평균 몇 % 보유하는지 &nbsp;|&nbsp; <b>하늘색 막대(종목 수)</b>: 전체 몇 개 종목에 투자하는지<br>지분율이 오르면 '집중 투자 전략', 종목 수가 늘면 '분산 투자 전략'으로 바뀐 것입니다.")

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
    chart_tip("<b>파란 영역이 0선 위</b>에 있으면 그 시기에 수익, <b>0선 아래</b>면 손실입니다.<br>국민연금의 수익률 흐름을 보면 '지금이 좋은 투자 환경인지' 감을 잡을 수 있어요.")

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
    chart_tip("<b>파란 선(전년도)</b>이 초록 선(3개년 평균)보다 높으면 최근 성과가 더 좋다는 뜻입니다.<br>3개년 수익률이 꾸준히 양수(0 위)를 유지한다면 국민연금 운용이 안정적이라는 신호예요.")

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

# ── 3-A ────────────────────────────────────────────────────
st.markdown("### 3-A. 공시 유형별 평균 수익률")

rows = []
for p in PERIODS:
    col_r = f"{p}_종목수익률"
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

fig_main.add_trace(go.Bar(
    x=stat["기간"], y=(stat["매수신호_수익률"] * 100).round(2),
    name="매수 공시 후", marker_color=BUY_COLOR,
    text=(stat["매수신호_수익률"] * 100).round(1).astype(str) + "%",
    textposition="outside",
), row=1, col=1)
fig_main.add_trace(go.Bar(
    x=stat["기간"], y=(stat["매도신호_수익률"] * 100).round(2),
    name="매도 공시 후", marker_color=SELL_COLOR,
    text=(stat["매도신호_수익률"] * 100).round(1).astype(str) + "%",
    textposition="outside",
), row=1, col=1)
fig_main.add_trace(go.Scatter(
    x=stat["기간"], y=(stat["시장수익률"] * 100).round(2),
    name="시장(KOSPI)", mode="lines+markers",
    line=dict(color=MKT_COLOR, width=2.5, dash="dot"),
), row=1, col=1)

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
chart_tip("🔵 <b>파란 막대(매수 공시 후)</b> vs 🔴 <b>빨간 막대(매도 공시 후)</b> 수익률을 비교합니다.<br>"
          "점선(KOSPI)보다 파란 막대가 높으면 '국민연금 매수 따라가기'가 시장 평균보다 유리했다는 뜻입니다.<br>"
          "<b>오른쪽 초과수익률 차트</b>: 0선 위면 시장을 이긴 것, 아래면 시장에 진 것입니다.")

# ── 3-B ────────────────────────────────────────────────────
st.markdown("### 3-B. 수익 달성 승률 (수익률 > 0%)")

win_rows = []
for p in PERIODS:
    col_r = f"{p}_종목수익률"
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
chart_tip("승률 = '수익이 난 비율'. <b>점선(50%)</b>이 기준선입니다.<br>"
          "🔵 파란 선이 50% 위에 있으면 → 매수 공시를 따랐을 때 절반 이상에서 수익이 났다는 뜻!<br>"
          "🔴 빨간 선이 50% 아래면 → 매도 공시 후 따라 팔면 절반 이상에서 손해 가능성이 있다는 신호입니다.")

# ── 3-C ────────────────────────────────────────────────────
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
fig_heat.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(fig_heat, use_container_width=True)
chart_tip("🟢 <b>초록색(양수)</b>: 해당 섹터에서 국민연금 따라가기가 시장 평균보다 더 수익이 났습니다.<br>"
          "🔴 <b>빨간색(음수)</b>: 시장 평균에 못 미쳤습니다.<br>"
          "💡 국민연금 매수 공시를 참고할 때, 초록색 섹터 종목에 집중하면 수익 확률을 높일 수 있습니다!")

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

    if "매수매도" in recent.columns:
        styled_recent = style_trade(recent, "매수매도")
    else:
        styled_recent = recent.style.background_gradient(subset=["지분율(퍼센트)"], cmap="Blues")

    st.dataframe(styled_recent, use_container_width=True, height=380)
    chart_tip("🔵 <b>파란색(매수)</b>: 국민연금이 해당 종목 지분을 늘렸습니다.<br>"
              "🔴 <b>빨간색(매도)</b>: 국민연금이 해당 종목 지분을 줄였습니다.<br>"
              "지분율 숫자가 높을수록 국민연금이 그 종목을 더 많이 보유하고 있다는 뜻입니다.")

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
    chart_tip("공시 건수가 많은 해는 국민연금이 포트폴리오를 <b>많이 조정</b>한 해입니다. 보통 시장 변동이 클수록 공시가 늘어납니다.")

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
    chart_tip("막대가 <b>높은 구간</b>이 공시가 가장 많이 발생하는 지분율 범위입니다.<br>"
              "5~10% 사이에 집중된다면 대부분의 공시가 최소 의무 수준에서 이루어진다는 뜻입니다.")

st.divider()

# ══════════════════════════════════════════════════════════
# 섹션 5: 종목 탐색기
# ══════════════════════════════════════════════════════════
st.markdown("## 5. 종목별 주가 추적 탐색기")

all_stocks = sorted(price["종목명"].unique())
selected = st.selectbox("종목을 선택하세요", all_stocks)

stock_perf  = perf[perf["종목명"] == selected]
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
            base   = sp["기준주가"]
            labels = list(valid_prices.keys())
            vals   = list(valid_prices.values())
            changes = [(v / base - 1) * 100 for v in vals]
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
            chart_tip("공시 기준일부터 각 시점까지 주가가 어떻게 변했는지 보여줍니다.<br>"
                      "선이 <b>우상향</b>할수록 국민연금을 따라 산 것이 좋은 선택이었다는 의미입니다.")

    with col_s2:
        st.markdown("#### 기준 대비 등락률")
        if valid_prices:
            bar_colors = [BUY_COLOR if c >= 0 else SELL_COLOR for c in changes]
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
            chart_tip("🔵 <b>파란 막대(플러스)</b>: 기준가 대비 수익 &nbsp;|&nbsp; 🔴 <b>빨간 막대(마이너스)</b>: 기준가 대비 손실<br>"
                      "어떤 시점에 팔았을 때 가장 높은 수익을 얻었는지 한눈에 확인하세요!")

    if not stock_perf.empty:
        st.markdown(f"#### {selected} 공시 이력")
        disp = stock_perf[["변동일자", "섹터", "매수매도",
                            "90일_종목수익률", "180일_종목수익률", "270일_종목수익률", "360일_종목수익률",
                            "90일_초과수익률", "360일_초과수익률"]].copy()
        disp["변동일자"] = disp["변동일자"].dt.strftime("%Y-%m-%d")
        for c in ["90일_종목수익률", "180일_종목수익률", "270일_종목수익률", "360일_종목수익률",
                  "90일_초과수익률", "360일_초과수익률"]:
            disp[c] = (disp[c] * 100).round(2)

        st.dataframe(style_trade(disp.reset_index(drop=True), "매수매도"), use_container_width=True)
        chart_tip("🔵 <b>파란 행(매수)</b>: 국민연금이 그 시점에 지분을 늘린 공시 &nbsp;|&nbsp; 🔴 <b>빨간 행(매도)</b>: 지분을 줄인 공시<br>"
                  "수익률 숫자가 <b>양수(+)</b>면 그 기간 동안 주가가 올랐고, <b>음수(-)</b>면 내렸다는 뜻입니다.")

st.divider()

# ══════════════════════════════════════════════════════════
# 투자 용어 사전
# ══════════════════════════════════════════════════════════
st.markdown("## 📚 초보 투자자를 위한 용어 사전")

with st.expander("📖 모르는 단어가 있다면 여기서 확인하세요! (클릭해서 펼치기)"):
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown("""
**📌 대량보유 공시**
특정 주식을 5% 이상 보유하거나, 1%p 이상 변동 시 금융당국에 의무 신고하는 것
→ 국민연금이 몰래 주식을 사고 팔 수 없도록 만든 제도

---
**📌 지분율**
해당 회사의 전체 주식 중 국민연금이 가진 비율 (%)
→ 10%면 그 회사 주식 10개 중 1개는 국민연금 소유

---
**📌 초과수익률**
내 수익률에서 시장 평균(KOSPI) 수익률을 뺀 값
→ 양수(+) = 시장보다 잘한 것 / 음수(-) = 시장보다 못한 것

---
**📌 승률**
전체 투자 중 수익이 난 비율
→ 60% 승률 = 10번 투자 중 6번은 수익이 났다는 뜻
        """)
    with col_t2:
        st.markdown("""
**📌 공시 지연**
국민연금이 주식을 사고 판 날부터 최대 90일 후에 공시됨
→ 개인 투자자는 항상 '최소 며칠~90일 늦은 정보'를 받음

---
**📌 섹터 (업종)**
비슷한 사업을 하는 회사들의 묶음
→ 예: IT 섹터(삼성전자, SK하이닉스), 금융 섹터(KB금융, 신한지주)

---
**📌 포트폴리오**
투자한 종목들의 전체 목록
→ 국민연금이 어떤 종목을 얼마나 갖고 있는지의 묶음

---
**📌 KOSPI (코스피)**
한국 주식시장 전체의 평균 지수
→ 국민연금 수익률 비교의 기준이 되는 시장 평균
        """)

st.divider()

# ══════════════════════════════════════════════════════════
# 섹션 6: 투자 결론
# ══════════════════════════════════════════════════════════
st.markdown("## 6. 투자 결론 및 가이드라인")

best_period  = stat.loc[stat["매수신호_수익률"].idxmax(), "기간"]
best_return  = stat["매수신호_수익률"].max() * 100
best_excess  = stat.loc[stat["매수신호_수익률"].idxmax(), "매수신호_초과"] * 100
best_win_row = win.loc[win["매수_절대승률"].idxmax()]

col_c1, col_c2, col_c3, col_c4 = st.columns(4)
col_c1.metric("최고 평균 수익률 시점", best_period, f"{best_return:.1f}%")
col_c2.metric("해당 시점 초과수익률", "", f"{best_excess:+.1f}%")
col_c3.metric("최고 승률 시점", best_win_row["기간"], f"{best_win_row['매수_절대승률']:.1f}%")
col_c4.metric("분석 공시 건수", f"{len(perf):,}건")

st.markdown("---")

st.markdown("### ✅ 투자 전 체크리스트")
st.markdown("""
<div style='background:#F1F8E9; border:1px solid #8BC34A; border-radius:10px;
            padding:16px 22px; margin-bottom:18px; line-height:2;'>
<b>국민연금 공시를 따라 투자하기 전, 이것만 확인하세요!</b><br>
☑️ &nbsp; <b>매수 공시인지 매도 공시인지</b> 먼저 확인 — 매수 공시 종목만 추종 대상<br>
☑️ &nbsp; <b>섹터 확인</b> — 히트맵에서 해당 섹터가 초록색(양수)인지 체크<br>
☑️ &nbsp; <b>보유 기간 결정</b> — 180~360일 장기 보유 전략이 평균적으로 유리<br>
☑️ &nbsp; <b>분산 투자</b> — 한 종목에 몰빵 금지! 여러 종목에 나눠서 투자<br>
☑️ &nbsp; <b>국민연금 운용 성과 확인</b> — 최근 수익률이 마이너스라면 시장 전체가 좋지 않은 환경<br>
☑️ &nbsp; <b>손실 한도 설정</b> — 투자 전 "얼마까지 잃으면 팔겠다"는 기준을 미리 정하기
</div>
""", unsafe_allow_html=True)

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

st.markdown("""
<div style='background:#FFF3E0; border:1px solid #FF9800; border-radius:10px;
            padding:14px 20px; margin-top:18px; line-height:1.8;'>
⚠️ <b>투자 주의사항</b><br>
이 분석은 과거 데이터를 기반으로 한 <b>참고 자료</b>입니다. 과거 수익률이 미래를 보장하지 않습니다.
국민연금 공시를 따라 투자하더라도 <b>손실이 발생할 수 있으며</b>, 모든 투자 결정과 그 결과는
투자자 본인의 책임입니다. 항상 본인의 투자 성향과 여유 자금 범위 내에서 투자하세요.
</div>
""", unsafe_allow_html=True)

st.caption("데이터 출처: 국민연금공단 공시 정보 | 분석 기간: 2022~2025 | 본 자료는 투자 참고용이며 투자 손익에 대한 책임은 투자자 본인에게 있습니다.")
