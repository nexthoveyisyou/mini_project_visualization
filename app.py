import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

# ══════════════════════════════════════════════════════════
# 기본 설정
# ══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="국민연금 투자 분석",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BUY   = "#1565C0"
SELL  = "#C62828"
MKT   = "#546E7A"
POS   = "#2E7D32"
GOLD  = "#F57F17"
LIGHT_BUY  = "#BBDEFB"
LIGHT_SELL = "#FFCDD2"

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #FAFAFA; }
.stTabs [data-baseweb="tab-list"] {
    gap: 8px; padding: 0; background: transparent;
}
.stTabs [data-baseweb="tab"] {
    font-size: 1rem; font-weight: 700;
    padding: 10px 28px; border-radius: 10px 10px 0 0;
    background: #E0E0E0; color: #555;
}
.stTabs [aria-selected="true"] {
    background: #1565C0 !important; color: white !important;
}
.hero {
    background: linear-gradient(135deg, #0D47A1 0%, #1565C0 60%, #1976D2 100%);
    color: white; padding: 44px 52px; border-radius: 18px; margin-bottom: 36px;
}
.hero h1 { font-size: 2rem; font-weight: 900; margin: 0 0 10px 0; line-height: 1.25; }
.hero p  { font-size: 1.05rem; opacity: 0.88; margin: 0; line-height: 1.6; }
.hero2 {
    background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 60%, #388E3C 100%);
    color: white; padding: 44px 52px; border-radius: 18px; margin-bottom: 36px;
}
.hero2 h1 { font-size: 2rem; font-weight: 900; margin: 0 0 10px 0; line-height: 1.25; }
.hero2 p  { font-size: 1.05rem; opacity: 0.88; margin: 0; line-height: 1.6; }
.kpi-block {
    background: white; border: 1px solid #E0E0E0;
    border-radius: 12px; padding: 20px 22px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.kpi-label { font-size: 0.78rem; color: #888; font-weight: 600;
             text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 4px; }
.kpi-value { font-size: 1.9rem; font-weight: 900; color: #1565C0; line-height: 1; }
.kpi-sub   { font-size: 0.82rem; color: #666; margin-top: 4px; }
.section-head {
    border-left: 5px solid #1565C0; padding-left: 14px;
    margin: 40px 0 20px 0;
}
.section-head h2 { font-size: 1.35rem; font-weight: 800; margin: 0 0 4px 0; }
.section-head p  { font-size: 0.88rem; color: #666; margin: 0; }
.tip {
    background: #E3F2FD; border-left: 4px solid #1565C0;
    padding: 11px 16px; border-radius: 0 8px 8px 0;
    font-size: 0.86rem; color: #333; line-height: 1.7;
    margin: 4px 0 22px 0;
}
.conclude {
    background: #E8F5E9; border: 1.5px solid #66BB6A;
    border-radius: 14px; padding: 22px 28px; margin: 20px 0;
    line-height: 1.8;
}
.conclude-b {
    background: #E3F2FD; border: 1.5px solid #42A5F5;
    border-radius: 14px; padding: 22px 28px; margin: 20px 0;
    line-height: 1.8;
}
.warn {
    background: #FFF8E1; border: 1.5px solid #FFCA28;
    border-radius: 14px; padding: 18px 24px; margin: 20px 0;
    font-size: 0.88rem; line-height: 1.8;
}
.scenario-card {
    background: white; border: 2px solid #E0E0E0;
    border-radius: 14px; padding: 22px 20px; text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.scenario-card.best { border-color: #1565C0; box-shadow: 0 4px 16px rgba(21,101,192,0.18); }
.tag {
    display: inline-block; padding: 2px 10px; border-radius: 20px;
    font-size: 0.75rem; font-weight: 700; letter-spacing: 0.5px;
}
.tag-blue  { background: #1565C0; color: white; }
.tag-green { background: #2E7D32; color: white; }
.tag-gold  { background: #F57F17; color: white; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# 데이터 로딩
# ══════════════════════════════════════════════════════════
@st.cache_data
def load_data():
    perf   = pd.read_csv("국민연금_기간별_성과분석_통합_진짜.csv", encoding="utf-8-sig")
    holds  = pd.read_csv("국민연금_대량보유주식_통합_최종본_정렬.csv", encoding="utf-8-sig")
    assets = pd.read_csv("운용 자산별 성과정보_통합.csv", encoding="utf-8-sig")
    port   = pd.read_csv("국내주식_통합_사명변경_1.csv", encoding="utf-8-sig")
    price  = pd.read_csv("국민연금_기간별_주가추적_리스트.csv", encoding="utf-8-sig")
    inv    = pd.read_csv("국민연금_개인투자자_추종성과_최종.csv", encoding="utf-8-sig")

    holds["날짜"]       = pd.to_datetime(holds["날짜"])
    perf["변동일자"]    = pd.to_datetime(perf["변동일자"])
    inv["변동일자"]     = pd.to_datetime(inv["변동일자"])
    assets["기준년월"]  = pd.to_datetime(assets["기준년월"])
    return perf, holds, assets, port, price, inv

perf, holds, assets, port, price, inv = load_data()

PERIODS   = ["90일", "180일", "270일", "360일"]
buy_perf  = perf[perf["매수매도"] == "매수"].copy()
sell_perf = perf[perf["매수매도"] == "매도"].copy()
buy_inv   = inv[inv["매수매도"] == "매수"].copy()
sell_inv  = inv[inv["매수매도"] == "매도"].copy()
domestic  = assets[assets["구분"] == "금융부문(국내주식)"].copy()

SCENARIOS = [
    {"label": "시나리오 A",  "tag": "단기",   "col": "90진입_180매도",  "entry": "D+90",  "exit": "D+180", "hold": "90일 보유",  "color": BUY},
    {"label": "시나리오 B",  "tag": "장기",   "col": "90진입_360매도",  "entry": "D+90",  "exit": "D+360", "hold": "270일 보유", "color": POS},
    {"label": "시나리오 C",  "tag": "중기",   "col": "180진입_360매도", "entry": "D+180", "exit": "D+360", "hold": "180일 보유", "color": GOLD},
]


def tip(text):
    st.markdown(f"<div class='tip'>📖 <b>읽는 법</b> — {text}</div>", unsafe_allow_html=True)


def sec(title, desc=""):
    st.markdown(f"""
    <div class='section-head'>
        <h2>{title}</h2>
        {"<p>" + desc + "</p>" if desc else ""}
    </div>""", unsafe_allow_html=True)


def p_fmt(v, already=False):
    x = v if already else v * 100
    sign = "+" if x >= 0 else ""
    return f"{sign}{x:.1f}%"


# ══════════════════════════════════════════════════════════
# 탭 구성
# ══════════════════════════════════════════════════════════
tab1, tab2 = st.tabs([
    "📊  Page 1 — 국민연금 투자 성과 평가",
    "💼  Page 2 — 개인투자자 공시 추종 전략",
])


# ╔══════════════════════════════════════════════════════════╗
# ║  PAGE 1 — 국민연금 투자 성과 평가                         ║
# ╚══════════════════════════════════════════════════════════╝
with tab1:

    # ── 히어로 ───────────────────────────────────────────
    latest_asset = domestic.sort_values("기준년월").iloc[-1]
    total_disclose = len(perf)
    buy_360_excess  = buy_perf["360일_초과수익률"].dropna().mean() * 100

    st.markdown(f"""
    <div class='hero'>
        <h1>📊 국민연금 국내주식 투자 성과 평가</h1>
        <p>국민연금공단이 국내 주식시장에서 어떤 성과를 냈는지, 매수·매도 공시 종목의 이후 수익률과 초과수익률을 통해 투자 판단력을 평가합니다.<br>
        분석 기간: 2022 ~ 2025 &nbsp;|&nbsp; 분석 공시 건수: {total_disclose:,}건 &nbsp;|&nbsp;
        최근 기간수익률: {latest_asset['기간수익률']:.2f}%</p>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI 4개 ─────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        kpi_cnt = f"{total_disclose:,}"
        st.markdown(f"""<div class='kpi-block'>
            <div class='kpi-label'>분석 공시 건수</div>
            <div class='kpi-value'>{kpi_cnt}<span style='font-size:1rem'>건</span></div>
            <div class='kpi-sub'>매수 {len(buy_perf):,}건 / 매도 {len(sell_perf):,}건</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        perf_val = latest_asset['기간수익률']
        color_kpi = POS if perf_val >= 0 else SELL
        st.markdown(f"""<div class='kpi-block'>
            <div class='kpi-label'>최근 기간수익률 (국내주식)</div>
            <div class='kpi-value' style='color:{color_kpi}'>{perf_val:+.2f}%</div>
            <div class='kpi-sub'>{latest_asset['기준년월'].strftime('%Y년 %m월')} 기준</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        yr3 = latest_asset['3개년수익률']
        color_3 = POS if yr3 >= 0 else SELL
        st.markdown(f"""<div class='kpi-block'>
            <div class='kpi-label'>3개년 누적수익률</div>
            <div class='kpi-value' style='color:{color_3}'>{yr3:+.2f}%</div>
            <div class='kpi-sub'>전년도: {latest_asset['전년도수익률']:+.2f}%</div>
        </div>""", unsafe_allow_html=True)
    with k4:
        color_ex = POS if buy_360_excess >= 0 else SELL
        st.markdown(f"""<div class='kpi-block'>
            <div class='kpi-label'>매수 공시 360일 초과수익률</div>
            <div class='kpi-value' style='color:{color_ex}'>{buy_360_excess:+.1f}%p</div>
            <div class='kpi-sub'>KOSPI 대비 매수 종목 성과</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # ══════════════════════════════════════════════════════
    # 섹션 1: 운용 성과
    # ══════════════════════════════════════════════════════
    sec("1. 국민연금 국내주식 운용 성과",
        "국민연금이 운용한 국내주식 펀드의 기간수익률과 누적수익률 추이입니다.")

    c1, c2 = st.columns(2)

    with c1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=domestic["기준년월"], y=domestic["기간수익률"],
            mode="lines", fill="tozeroy",
            line=dict(color=BUY, width=2.5),
            fillcolor="rgba(21,101,192,0.12)",
            name="기간수익률",
        ))
        fig.add_hline(y=0, line_dash="dash", line_color="#999", line_width=1)
        fig.update_layout(
            title="기간수익률 추이",
            height=310, margin=dict(l=10, r=10, t=36, b=10),
            yaxis_title="수익률 (%)", plot_bgcolor="white",
        )
        st.plotly_chart(fig, use_container_width=True)
        tip("파란 영역이 <b>0선 위</b>면 수익, <b>0선 아래</b>면 손실 기간입니다. 주식시장 전체 흐름과 함께 보세요.")

    with c2:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=domestic["기준년월"], y=domestic["전년도수익률"],
            mode="lines", name="전년도 수익률",
            line=dict(color=BUY, width=2.2),
        ))
        fig2.add_trace(go.Scatter(
            x=domestic["기준년월"], y=domestic["3개년수익률"],
            mode="lines", name="3개년 누적수익률",
            line=dict(color=POS, width=2.2),
        ))
        fig2.add_hline(y=0, line_dash="dash", line_color="#999", line_width=1)
        fig2.update_layout(
            title=dict(text="전년도 vs 3개년 누적수익률", x=0, xanchor="left", y=0.97),
            height=330, margin=dict(l=10, r=10, t=70, b=10),
            yaxis_title="수익률 (%)", plot_bgcolor="white",
            legend=dict(orientation="h", y=1.0, x=0, xanchor="left", yanchor="bottom"),
        )
        st.plotly_chart(fig2, use_container_width=True)
        tip("파란 선(전년도)이 초록 선(3개년)보다 높으면 <b>최근 성과가 개선되는 추세</b>입니다.")

    st.divider()

    # ══════════════════════════════════════════════════════
    # 섹션 2: 포트폴리오 현황
    # ══════════════════════════════════════════════════════
    sec("2. 국내주식 포트폴리오 현황",
        "국민연금이 실제로 보유 중인 국내주식 종목과 비중입니다.")

    latest_year = int(port["기준일"].max())
    port_latest = port[port["기준일"] == latest_year].copy()

    cl, cr = st.columns([1.2, 1])

    with cl:
        top10 = port_latest.nlargest(10, "평가액(억 원)").reset_index(drop=True)
        fig_bar = go.Figure(go.Bar(
            x=top10["평가액(억 원)"],
            y=top10["종목명"],
            orientation="h",
            marker_color=BUY,
            text=top10["평가액(억 원)"].apply(lambda v: f"{v:,.0f}억"),
            textposition="outside",
        ))
        fig_bar.update_layout(
            title=f"Top 10 보유 종목 ({latest_year}년 기준)",
            height=380, margin=dict(l=10, r=90, t=36, b=10),
            xaxis_title="평가액 (억 원)",
            yaxis=dict(autorange="reversed"),
            plot_bgcolor="white",
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        tip("막대가 <b>길수록</b> 국민연금이 더 큰 비중으로 보유 중인 종목입니다. 상위 종목일수록 장기 신뢰 종목으로 볼 수 있습니다.")

    with cr:
        years = sorted(port["기준일"].unique())
        colors_yr = px.colors.qualitative.Set2
        fig_trend = go.Figure()
        for i, yr in enumerate(years):
            yr_df = port[port["기준일"] == yr].nlargest(5, "평가액(억 원)")
            fig_trend.add_trace(go.Bar(
                name=str(yr),
                x=yr_df["종목명"],
                y=yr_df["평가액(억 원)"],
                marker_color=colors_yr[i % len(colors_yr)],
            ))
        fig_trend.update_layout(
            title=dict(text="연도별 Top 5 포트폴리오 변화", x=0, xanchor="left", y=0.97),
            barmode="group", height=400,
            margin=dict(l=10, r=10, t=70, b=10),
            yaxis_title="평가액 (억 원)",
            legend=dict(orientation="h", y=1.0, x=0, xanchor="left", yanchor="bottom"),
            plot_bgcolor="white",
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        tip("같은 종목이 연도에 걸쳐 계속 상위권에 있다면 <b>국민연금이 장기적으로 신뢰하는 종목</b>입니다.")

    port_agg = port.groupby("기준일").agg(
        평균지분율=("지분율(퍼센트)", "mean"),
        종목수=("종목명", "count"),
    ).reset_index()

    fig_stat = make_subplots(specs=[[{"secondary_y": True}]])
    fig_stat.add_trace(go.Scatter(
        x=port_agg["기준일"], y=port_agg["평균지분율"],
        name="평균 지분율 (%)", mode="lines+markers",
        line=dict(color=BUY, width=2.5),
    ), secondary_y=False)
    fig_stat.add_trace(go.Bar(
        x=port_agg["기준일"], y=port_agg["종목수"],
        name="보유 종목 수", marker_color=LIGHT_BUY, opacity=0.7,
    ), secondary_y=True)
    fig_stat.update_layout(
        title=dict(text="연도별 평균 지분율 & 보유 종목 수", x=0, xanchor="left", y=0.97),
        height=300, margin=dict(l=10, r=10, t=70, b=10),
        plot_bgcolor="white",
        legend=dict(orientation="h", y=1.0, x=0, xanchor="left", yanchor="bottom"),
    )
    fig_stat.update_yaxes(title_text="평균 지분율 (%)", secondary_y=False)
    fig_stat.update_yaxes(title_text="보유 종목 수", secondary_y=True)
    st.plotly_chart(fig_stat, use_container_width=True)
    tip("파란 선이 올라가면 <b>집중 투자 전략</b>, 하늘색 막대가 늘면 <b>분산 투자 전략</b>으로 전환된 것입니다.")

    st.divider()

    # ══════════════════════════════════════════════════════
    # 섹션 3: 매수·매도 공시 종목 수익률 분석
    # ══════════════════════════════════════════════════════
    sec("3. 국민연금 투자 판단력 평가 — 공시 종목 사후 수익률",
        "국민연금이 매수한 종목과 매도한 종목이 이후 기간에 어떤 성과를 냈는지 평가합니다.")

    rows = []
    for p_lbl in PERIODS:
        rows.append({
            "기간": p_lbl,
            "매수_종목수익률": buy_perf[f"{p_lbl}_종목수익률"].dropna().mean() * 100,
            "매도_종목수익률": sell_perf[f"{p_lbl}_종목수익률"].dropna().mean() * 100,
            "시장수익률":      buy_perf[f"{p_lbl}_시장수익률"].dropna().mean() * 100,
            "매수_초과":       buy_perf[f"{p_lbl}_초과수익률"].dropna().mean() * 100,
            "매도_초과":       sell_perf[f"{p_lbl}_초과수익률"].dropna().mean() * 100,
            "매수_승률":       (buy_perf[f"{p_lbl}_종목수익률"] > 0).mean() * 100,
            "매도_승률":       (sell_perf[f"{p_lbl}_종목수익률"] > 0).mean() * 100,
            "매수_초과승률":   (buy_perf[f"{p_lbl}_초과수익률"] > 0).mean() * 100,
            "매도_초과승률":   (sell_perf[f"{p_lbl}_초과수익률"] > 0).mean() * 100,
        })
    stat = pd.DataFrame(rows)

    fig_main = make_subplots(
        rows=1, cols=2,
        subplot_titles=["기간별 평균 수익률 (절대치)", "기간별 평균 초과수익률 (vs KOSPI)"],
    )
    fig_main.add_trace(go.Bar(
        x=stat["기간"], y=stat["매수_종목수익률"].round(2),
        name="매수 공시 종목", marker_color=BUY,
        text=stat["매수_종목수익률"].round(1).astype(str) + "%",
        textposition="outside",
    ), row=1, col=1)
    fig_main.add_trace(go.Bar(
        x=stat["기간"], y=stat["매도_종목수익률"].round(2),
        name="매도 공시 종목", marker_color=SELL,
        text=stat["매도_종목수익률"].round(1).astype(str) + "%",
        textposition="outside",
    ), row=1, col=1)
    fig_main.add_trace(go.Scatter(
        x=stat["기간"], y=stat["시장수익률"].round(2),
        name="KOSPI 시장수익률", mode="lines+markers",
        line=dict(color=MKT, width=2.5, dash="dot"),
    ), row=1, col=1)

    for row_, col_, buy_col, sell_col, show in [
        (1, 2, "매수_초과", "매도_초과", False),
    ]:
        fig_main.add_trace(go.Bar(
            x=stat["기간"], y=stat[buy_col].round(2),
            name="매수 초과", marker_color=BUY, showlegend=show,
            text=stat[buy_col].round(1).astype(str) + "%p",
            textposition="outside",
        ), row=row_, col=col_)
        fig_main.add_trace(go.Bar(
            x=stat["기간"], y=stat[sell_col].round(2),
            name="매도 초과", marker_color=SELL, showlegend=show,
            text=stat[sell_col].round(1).astype(str) + "%p",
            textposition="outside",
        ), row=row_, col=col_)
        fig_main.add_hline(y=0, line_dash="dash", line_color="#aaa", row=row_, col=col_)

    fig_main.update_layout(
        height=430, barmode="group",
        margin=dict(l=10, r=10, t=44, b=10),
        plot_bgcolor="white",
        legend=dict(orientation="h", y=-0.14, x=0.28),
    )
    fig_main.update_yaxes(ticksuffix="%")
    st.plotly_chart(fig_main, use_container_width=True)
    tip("🔵 파란 막대(매수 공시 종목)와 🔴 빨간 막대(매도 공시 종목)를 비교합니다. 점선(KOSPI)이 기준선 — 파란 막대가 점선보다 높으면 국민연금 매수 판단이 시장 평균을 앞선 것입니다. 오른쪽 초과수익률: 0 위면 KOSPI를 이긴 것, 0 아래면 진 것.")

    # ── 3-B 승률 ──────────────────────────────────────────
    fig_win = make_subplots(rows=1, cols=2,
        subplot_titles=["절대 수익 달성 승률", "시장 초과 달성 승률"])
    for c_idx, (buy_c, sell_c) in enumerate(
        [("매수_승률", "매도_승률"), ("매수_초과승률", "매도_초과승률")], start=1
    ):
        fig_win.add_trace(go.Scatter(
            x=stat["기간"], y=stat[buy_c].round(1),
            name="매수 공시", mode="lines+markers+text",
            text=stat[buy_c].round(1).astype(str) + "%",
            textposition="top center",
            line=dict(color=BUY, width=2.5), marker=dict(size=10),
            showlegend=(c_idx == 1),
        ), row=1, col=c_idx)
        fig_win.add_trace(go.Scatter(
            x=stat["기간"], y=stat[sell_c].round(1),
            name="매도 공시", mode="lines+markers+text",
            text=stat[sell_c].round(1).astype(str) + "%",
            textposition="bottom center",
            line=dict(color=SELL, width=2.5), marker=dict(size=10),
            showlegend=(c_idx == 1),
        ), row=1, col=c_idx)
        fig_win.add_hline(y=50, line_dash="dash", line_color="#aaa", row=1, col=c_idx)

    fig_win.update_layout(
        height=360, margin=dict(l=10, r=10, t=44, b=10),
        plot_bgcolor="white", legend=dict(orientation="h", y=-0.18, x=0.35),
    )
    fig_win.update_yaxes(ticksuffix="%", range=[20, 75])
    st.plotly_chart(fig_win, use_container_width=True)
    tip("승률 50%(점선)이 기준입니다. 🔵 파란 선이 50% 위 → 매수 공시 종목의 절반 이상에서 수익 발생. 🔴 빨간 선이 50% 아래 → 매도 공시 종목의 절반 이상에서 이후에도 주가 하락.")

    # ── 3-C 섹터 히트맵 ──────────────────────────────────
    st.markdown("#### 섹터별 초과수익률 히트맵 (국민연금 매수 공시 기준)")
    sector_rows = []
    for sector in buy_perf["섹터"].dropna().unique():
        s_df = buy_perf[buy_perf["섹터"] == sector]
        row = {"섹터": sector}
        for p_lbl in PERIODS:
            row[p_lbl] = round(s_df[f"{p_lbl}_초과수익률"].dropna().mean() * 100, 2)
        sector_rows.append(row)

    sector_df = pd.DataFrame(sector_rows).set_index("섹터").dropna(how="all")
    sector_df = sector_df.sort_values("360일", ascending=False)

    fig_heat = go.Figure(go.Heatmap(
        z=sector_df.values,
        x=sector_df.columns.tolist(),
        y=sector_df.index.tolist(),
        colorscale="RdYlGn", zmid=0,
        text=np.round(sector_df.values, 1),
        texttemplate="%{text}%p",
        colorbar=dict(title="초과수익률(%)"),
    ))
    fig_heat.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_heat, use_container_width=True)
    tip("🟢 초록(양수) = 해당 섹터에서 국민연금 매수 판단이 KOSPI를 앞섰습니다. 🔴 빨간(음수) = 시장 평균에 못 미쳤습니다. 초록이 진할수록 국민연금의 투자 판단력이 빛난 섹터입니다.")

    # ── 3-D 섹터별 보유 종목 & 지분율 ────────────────────────
    st.markdown("#### 섹터별 보유 종목 수 & 평균 지분율")
    sec_stock = perf[["종목명", "섹터"]].drop_duplicates("종목명")
    port_latest_yr = port[port["기준일"] == int(port["기준일"].max())].copy()
    port_sec = port_latest_yr.merge(sec_stock, on="종목명", how="left").dropna(subset=["섹터"])
    sec_summary = (
        port_sec.groupby("섹터")
        .agg(종목수=("종목명", "count"), 평균지분율=("지분율(퍼센트)", "mean"), 총평가액=("평가액(억 원)", "sum"))
        .reset_index()
        .sort_values("총평가액", ascending=False)
    )

    fig_sec = make_subplots(specs=[[{"secondary_y": True}]])
    fig_sec.add_trace(go.Bar(
        x=sec_summary["섹터"], y=sec_summary["종목수"],
        name="보유 종목 수", marker_color=BUY, opacity=0.75,
        text=sec_summary["종목수"], textposition="outside",
    ), secondary_y=False)
    fig_sec.add_trace(go.Scatter(
        x=sec_summary["섹터"], y=sec_summary["평균지분율"].round(2),
        name="평균 지분율 (%)", mode="lines+markers+text",
        text=sec_summary["평균지분율"].round(1).astype(str) + "%",
        textposition="top center",
        line=dict(color=GOLD, width=2.5), marker=dict(size=9),
    ), secondary_y=True)
    fig_sec.update_layout(
        height=400, margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="white", legend=dict(orientation="h", y=1.1),
    )
    fig_sec.update_yaxes(title_text="보유 종목 수", secondary_y=False)
    fig_sec.update_yaxes(title_text="평균 지분율 (%)", secondary_y=True)
    st.plotly_chart(fig_sec, use_container_width=True)
    tip("🔵 파란 막대: 해당 섹터 내 국민연금 보유 종목 수 (총평가액 순 정렬) | 🟡 노란 선: 섹터 내 종목별 평균 지분율(%). 막대가 높으면 분산 투자, 선이 높으면 집중 투자한 섹터입니다.")

    # ── 섹터 상세 테이블 ────────────────────────────────────
    with st.expander("📋 섹터별 상세 보기 (종목 리스트)"):
        sel_sector = st.selectbox("섹터 선택", sec_summary["섹터"].tolist(), key="sector_detail")
        detail_df = (
            port_sec[port_sec["섹터"] == sel_sector][["종목명", "평가액(억 원)", "지분율(퍼센트)", "자산군 내 비중(퍼센트)"]]
            .sort_values("지분율(퍼센트)", ascending=False)
            .reset_index(drop=True)
        )
        detail_df.index += 1
        st.dataframe(
            detail_df.style.background_gradient(subset=["지분율(퍼센트)"], cmap="Blues")
                           .format({"평가액(억 원)": "{:,.0f}", "지분율(퍼센트)": "{:.2f}%", "자산군 내 비중(퍼센트)": "{:.2f}%"}),
            use_container_width=True,
        )

    # ── 섹션 1 결론 ────────────────────────────────────────
    best_sector = sector_df["360일"].idxmax()
    best_sec_val = sector_df.loc[best_sector, "360일"]
    buy_win_360  = stat.loc[stat["기간"] == "360일", "매수_승률"].values[0]
    buy_360_ret  = stat.loc[stat["기간"] == "360일", "매수_종목수익률"].values[0]

    st.markdown(f"""
    <div class='conclude'>
    <b>🏦 국민연금 투자 판단력 종합 평가</b><br><br>
    ✅ 국민연금이 <b>매수한 종목</b>은 모든 기간(90~360일)에서 매도 공시 종목 대비 <b>우월한 수익률</b>을 기록했습니다.<br>
    ✅ <b>360일 기준</b> 매수 공시 종목의 평균 수익률은 <b>{buy_360_ret:.1f}%</b>, 절대 수익 달성 승률은 <b>{buy_win_360:.1f}%</b>입니다.<br>
    ✅ 초과수익률 측면에서는 KOSPI를 일부 하회하는 구간도 있으나, <b>{best_sector}</b> 섹터에서는 {best_sec_val:+.1f}%p로 시장을 크게 앞섰습니다.<br>
    ⚠️ 매도 공시 종목은 이후에도 추가 하락하는 경향이 있어, 국민연금의 <b>매도 판단도 유효</b>한 시그널로 해석됩니다.
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ══════════════════════════════════════════════════════
    # 섹션 4: 대량보유 공시 현황
    # ══════════════════════════════════════════════════════
    sec("4. 대량보유 공시 현황",
        "국민연금이 보고한 대량보유 공시의 빈도와 지분율 패턴입니다.")

    holds["연도"] = holds["날짜"].dt.year
    yearly = holds.groupby("연도").size().reset_index(name="공시건수")

    ch1, ch2 = st.columns(2)
    with ch1:
        fig_yr = go.Figure(go.Bar(
            x=yearly["연도"].astype(str), y=yearly["공시건수"],
            marker_color=BUY, text=yearly["공시건수"], textposition="outside",
        ))
        fig_yr.update_layout(
            title="연도별 공시 건수",
            height=280, margin=dict(l=10, r=10, t=36, b=10),
            plot_bgcolor="white", yaxis_title="건수",
        )
        st.plotly_chart(fig_yr, use_container_width=True)
        tip("공시 건수가 많은 해는 국민연금이 <b>포트폴리오를 활발히 재편</b>한 해입니다.")

    with ch2:
        fig_hist = go.Figure(go.Histogram(
            x=holds["지분율(퍼센트)"], nbinsx=30,
            marker_color=BUY, opacity=0.8,
        ))
        fig_hist.update_layout(
            title="지분율 분포",
            height=280, margin=dict(l=10, r=10, t=36, b=10),
            plot_bgcolor="white",
            xaxis_title="지분율 (%)", yaxis_title="건수",
        )
        st.plotly_chart(fig_hist, use_container_width=True)
        tip("가장 높은 막대 구간이 <b>공시가 집중되는 지분율 범위</b>입니다. 5~10%대가 많다면 대부분 의무 공시 임계값 근처에서 활동하고 있는 것입니다.")

    st.markdown("""
    <div class='warn'>
    ⚠️ <b>투자 주의사항</b> — 이 분석은 과거 데이터 기반의 참고 자료입니다. 국민연금 공시는 실제 매매일로부터 최대 90일 이내에 이루어지므로, 공시 시점에는 이미 시장이 일부 반응했을 수 있습니다. 과거 성과가 미래를 보장하지 않습니다.
    </div>
    """, unsafe_allow_html=True)

    st.caption("데이터 출처: 국민연금공단 공시 정보 | 분석 기간: 2022~2025 | 본 자료는 투자 참고용이며 모든 투자 손익의 책임은 투자자 본인에게 있습니다.")


# ╔══════════════════════════════════════════════════════════╗
# ║  PAGE 2 — 개인투자자 공시 추종 전략                        ║
# ╚══════════════════════════════════════════════════════════╝
with tab2:

    # ── 히어로 ───────────────────────────────────────────
    st.markdown("""
    <div class='hero2'>
        <h1>💼 개인투자자를 위한 국민연금 공시 추종 전략</h1>
        <p>국민연금 공시를 확인한 개인투자자가 <b>90일·180일 시점에 진입</b>하고 다양한 시점에 매도할 경우,<br>
        실제로 수익이 날 수 있는지 시나리오별 수익률과 초과수익률로 검증합니다.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── 공시 지연 타임라인 ────────────────────────────────
    st.markdown("### ⏱ 왜 개인투자자는 최소 90일 늦게 정보를 받는가?")
    st.markdown("""
    <div style='display:flex; align-items:stretch; justify-content:center; gap:0;
                padding:24px 32px; background:white; border-radius:14px;
                border:1px solid #E0E0E0; margin-bottom:8px; flex-wrap:wrap; gap:6px;'>
        <div style='text-align:center; padding:16px 22px; background:#1565C0;
                    color:white; border-radius:10px; min-width:120px;'>
            <div style='font-size:1.6rem'>🏦</div>
            <b>국민연금 매매</b><br><small style='opacity:.85'>D day</small>
        </div>
        <div style='color:#CCC; font-size:2rem; display:flex; align-items:center; padding:0 8px'>→</div>
        <div style='text-align:center; padding:16px 22px; background:#E65100;
                    color:white; border-radius:10px; min-width:120px;'>
            <div style='font-size:1.6rem'>📋</div>
            <b>공시 의무 기한</b><br><small style='opacity:.85'>최대 D+90일</small>
        </div>
        <div style='color:#CCC; font-size:2rem; display:flex; align-items:center; padding:0 8px'>→</div>
        <div style='text-align:center; padding:16px 22px; background:#2E7D32;
                    color:white; border-radius:10px; min-width:120px;'>
            <div style='font-size:1.6rem'>👀</div>
            <b>개인 공시 확인</b><br><small style='opacity:.85'>D+90일 이후</small>
        </div>
        <div style='color:#CCC; font-size:2rem; display:flex; align-items:center; padding:0 8px'>→</div>
        <div style='text-align:center; padding:16px 22px; background:#6A1B9A;
                    color:white; border-radius:10px; min-width:120px;'>
            <div style='font-size:1.6rem'>💰</div>
            <b>개인 매수 진입</b><br><small style='opacity:.85'>D+90 또는 D+180</small>
        </div>
        <div style='color:#CCC; font-size:2rem; display:flex; align-items:center; padding:0 8px'>→</div>
        <div style='text-align:center; padding:16px 22px; background:#37474F;
                    color:white; border-radius:10px; min-width:120px;'>
            <div style='font-size:1.6rem'>🏁</div>
            <b>매도 (청산)</b><br><small style='opacity:.85'>D+180 또는 D+360</small>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""<div class='tip'>국민연금이 주식을 거래한 후 <b>최대 90일이 지나서야 공시</b>가 됩니다. 즉, 개인투자자는 항상 '정보가 90일 늦은 상태'에서 결정을 내립니다. 그럼에도 공시 확인 후 매수해 얼마나 보유하느냐에 따라 수익이 달라질 수 있습니다.</div>""", unsafe_allow_html=True)

    st.divider()

    # ══════════════════════════════════════════════════════
    # 섹션 1: 3가지 시나리오 개요
    # ══════════════════════════════════════════════════════
    sec("1. 분석 시나리오 — 3가지 진입·청산 전략",
        "국민연금 매수 공시 확인 후 개인투자자가 선택할 수 있는 세 가지 전략입니다.")

    # 매수 공시 기준 시나리오별 통계
    sc_stats = []
    for sc in SCENARIOS:
        key = sc["col"]
        ret_col = f"개인_{key}_종목수익률"
        mkt_col = f"개인_{key}_시장수익률"
        exc_col = f"개인_{key}_초과수익률"
        buy_data  = buy_inv[ret_col].dropna()
        exc_data  = buy_inv[exc_col].dropna()
        sc_stats.append({
            **sc,
            "avg_ret": buy_data.mean() * 100,
            "avg_exc": exc_data.mean() * 100,
            "win_abs": (buy_data > 0).mean() * 100,
            "win_exc": (exc_data > 0).mean() * 100,
            "n":       len(buy_data),
        })

    best_idx = max(range(len(sc_stats)), key=lambda i: sc_stats[i]["avg_ret"])

    cols_sc = st.columns(3)
    for i, sc in enumerate(sc_stats):
        is_best = (i == best_idx)
        # HTML 조각을 변수로 미리 빌드
        border_css  = "border-color:#1565C0;" if is_best else "border-color:#E0E0E0;"
        shadow_css  = "box-shadow:0 4px 18px rgba(21,101,192,0.2);" if is_best else ""
        badge_html  = ("<div style='color:#1565C0;font-weight:900;"
                       "margin-bottom:6px;font-size:0.9rem'>🏆 최고 수익률 전략</div>"
                       if is_best else "")
        ret_color   = POS if sc["avg_ret"] >= 0 else SELL
        exc_color   = POS if sc["avg_exc"] >= 0 else SELL
        ret_str     = f"{sc['avg_ret']:+.1f}%"
        exc_str     = f"{sc['avg_exc']:+.1f}%p"
        win_abs_str = f"{sc['win_abs']:.1f}%"
        win_exc_str = f"{sc['win_exc']:.1f}%"
        n_str       = f"{sc['n']}건"

        card_html = (
            f"<div style='background:white;border:2px solid #E0E0E0;"
            f"border-radius:14px;padding:24px 20px;text-align:center;"
            f"{border_css}{shadow_css}'>"
            f"{badge_html}"
            f"<div style='font-size:1.1rem;font-weight:800;margin-bottom:4px'>{sc['label']}</div>"
            f"<div style='font-size:0.82rem;color:#888;margin-bottom:12px'>"
            f"진입: <b>{sc['entry']}</b> → 청산: <b>{sc['exit']}</b> ({sc['hold']})</div>"
            f"<div style='font-size:2rem;font-weight:900;color:{ret_color}'>{ret_str}</div>"
            f"<div style='font-size:0.78rem;color:#888;margin-bottom:8px'>평균 종목 수익률</div>"
            f"<div style='font-size:1.1rem;font-weight:700;color:{exc_color}'>{exc_str}</div>"
            f"<div style='font-size:0.78rem;color:#888;margin-bottom:10px'>초과수익률 (vs KOSPI)</div>"
            f"<div style='font-size:0.85rem;color:#555'>"
            f"절대 수익 승률 <b>{win_abs_str}</b> | 초과수익 승률 <b>{win_exc_str}</b></div>"
            f"<div style='font-size:0.75rem;color:#aaa;margin-top:6px'>분석 건수: {n_str}</div>"
            f"</div>"
        )
        with cols_sc[i]:
            st.markdown(card_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    tip("세 시나리오 모두 <b>국민연금 매수 공시</b>를 확인한 개인투자자가 따라 매수하는 상황입니다. 진입 시점(D+90 또는 D+180)과 청산 시점(D+180 또는 D+360)의 조합이 다릅니다.")

    st.divider()

    # ══════════════════════════════════════════════════════
    # 섹션 2: 매수 공시 추종 시나리오별 수익률 비교
    # ══════════════════════════════════════════════════════
    sec("2. 매수 공시 추종 — 시나리오별 수익률 상세 비교",
        "국민연금이 매수 공시를 낸 종목에 각 시나리오로 투자했을 때의 결과입니다.")

    sc_labels = [sc["label"] for sc in sc_stats]
    sc_avg_ret = [sc["avg_ret"] for sc in sc_stats]
    sc_avg_exc = [sc["avg_exc"] for sc in sc_stats]
    sc_avg_mkt = []
    for sc in SCENARIOS:
        key = sc["col"]
        mkt_col = f"개인_{key}_시장수익률"
        sc_avg_mkt.append(buy_inv[mkt_col].dropna().mean() * 100)

    fig_sc = make_subplots(
        rows=1, cols=2,
        subplot_titles=["시나리오별 평균 수익률", "시나리오별 초과수익률 (vs KOSPI)"],
    )

    sc_colors = [BUY, POS, GOLD]
    for i, (sc, color) in enumerate(zip(sc_stats, sc_colors)):
        fig_sc.add_trace(go.Bar(
            name=sc["label"],
            x=[sc["label"]],
            y=[sc["avg_ret"]],
            marker_color=color,
            text=[f"{sc['avg_ret']:+.1f}%"],
            textposition="outside",
            showlegend=False,
        ), row=1, col=1)

    fig_sc.add_trace(go.Scatter(
        x=sc_labels, y=sc_avg_mkt,
        name="동기간 KOSPI", mode="lines+markers",
        line=dict(color=MKT, width=2.5, dash="dot"),
        marker=dict(size=10),
    ), row=1, col=1)

    colors_exc = [POS if v >= 0 else SELL for v in sc_avg_exc]
    fig_sc.add_trace(go.Bar(
        x=sc_labels, y=sc_avg_exc,
        marker_color=colors_exc,
        text=[f"{v:+.1f}%p" for v in sc_avg_exc],
        textposition="outside",
        name="초과수익률", showlegend=False,
    ), row=1, col=2)
    fig_sc.add_hline(y=0, line_dash="dash", line_color="#aaa", row=1, col=2)

    fig_sc.update_layout(
        height=400, margin=dict(l=10, r=10, t=44, b=10),
        plot_bgcolor="white",
        legend=dict(orientation="h", y=-0.15, x=0.35),
    )
    fig_sc.update_yaxes(ticksuffix="%")
    st.plotly_chart(fig_sc, use_container_width=True)
    tip("왼쪽: 각 시나리오의 평균 수익률. 점선(KOSPI)이 해당 기간 시장 평균. | 오른쪽: 🟢 초과수익률이 0 위면 시장을 이긴 전략, 🔴 0 아래면 시장에 진 전략.")

    # ── 매도 공시 추종 비교 ───────────────────────────────
    st.markdown("#### 매도 공시 추종 시나리오 — 비교 참고")
    sc_sell_stats = []
    for sc in SCENARIOS:
        key = sc["col"]
        ret_col = f"개인_{key}_종목수익률"
        exc_col = f"개인_{key}_초과수익률"
        ret_data = sell_inv[ret_col].dropna()
        exc_data = sell_inv[exc_col].dropna()
        sc_sell_stats.append({
            "label": sc["label"], "avg_ret": ret_data.mean() * 100,
            "avg_exc": exc_data.mean() * 100,
            "win_abs": (ret_data > 0).mean() * 100,
        })

    sell_labels = [s["label"] for s in sc_sell_stats]
    sell_rets    = [s["avg_ret"] for s in sc_sell_stats]
    sell_excs    = [s["avg_exc"] for s in sc_sell_stats]

    fig_sell = make_subplots(rows=1, cols=2,
        subplot_titles=["매도 공시 추종 — 시나리오별 수익률", "매도 공시 추종 — 초과수익률"])
    for i, (lbl, ret) in enumerate(zip(sell_labels, sell_rets)):
        fig_sell.add_trace(go.Bar(
            x=[lbl], y=[ret], marker_color=SELL,
            text=[f"{ret:+.1f}%"], textposition="outside", showlegend=False,
        ), row=1, col=1)

    sell_exc_colors = [POS if v >= 0 else SELL for v in sell_excs]
    fig_sell.add_trace(go.Bar(
        x=sell_labels, y=sell_excs, marker_color=sell_exc_colors,
        text=[f"{v:+.1f}%p" for v in sell_excs], textposition="outside", showlegend=False,
    ), row=1, col=2)
    fig_sell.add_hline(y=0, line_dash="dash", line_color="#aaa", row=1, col=1)
    fig_sell.add_hline(y=0, line_dash="dash", line_color="#aaa", row=1, col=2)
    fig_sell.update_layout(
        height=340, margin=dict(l=10, r=10, t=44, b=10),
        plot_bgcolor="white",
    )
    fig_sell.update_yaxes(ticksuffix="%")
    st.plotly_chart(fig_sell, use_container_width=True)
    tip("국민연금이 <b>매도 공시</b>를 낸 종목에 (역발상으로) 따라 매수하거나, 해당 종목을 계속 보유했을 때의 결과입니다. 매수 공시 추종 결과와 비교해 보세요.")

    st.divider()

    # ══════════════════════════════════════════════════════
    # 섹션 3: 승률 분석
    # ══════════════════════════════════════════════════════
    sec("3. 시나리오별 수익 달성 승률",
        "각 시나리오에서 실제로 수익이 난 비율(절대 승률)과 KOSPI를 이긴 비율(초과 승률)입니다.")

    win_abs_buy  = [sc["win_abs"] for sc in sc_stats]
    win_exc_buy  = [sc["win_exc"] for sc in sc_stats]
    win_abs_sell = [s["win_abs"] for s in sc_sell_stats]

    fig_winrate = go.Figure()
    fig_winrate.add_trace(go.Bar(
        name="매수 공시 — 절대 승률",
        x=sc_labels, y=win_abs_buy,
        marker_color=BUY,
        text=[f"{v:.1f}%" for v in win_abs_buy], textposition="outside",
    ))
    fig_winrate.add_trace(go.Bar(
        name="매수 공시 — 초과수익 승률",
        x=sc_labels, y=win_exc_buy,
        marker_color=LIGHT_BUY,
        text=[f"{v:.1f}%" for v in win_exc_buy], textposition="outside",
    ))
    fig_winrate.add_trace(go.Bar(
        name="매도 공시 — 절대 승률",
        x=sc_labels, y=win_abs_sell,
        marker_color=LIGHT_SELL,
        text=[f"{v:.1f}%" for v in win_abs_sell], textposition="outside",
    ))
    fig_winrate.add_hline(y=50, line_dash="dash", line_color="#999",
                          annotation_text="50% 기준선", annotation_position="right")

    fig_winrate.update_layout(
        barmode="group", height=380,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="white",
        yaxis_title="승률 (%)", yaxis=dict(range=[0, 85]),
        legend=dict(orientation="h", y=1.05),
    )
    fig_winrate.update_yaxes(ticksuffix="%")
    st.plotly_chart(fig_winrate, use_container_width=True)
    tip("짙은 파란 막대(절대 승률)가 50% 기준선 위면 '절반 이상에서 수익'. 하늘 막대(초과 승률)는 KOSPI를 이긴 비율. 두 막대가 모두 50% 위면 가장 안정적인 전략입니다.")

    st.divider()

    # ══════════════════════════════════════════════════════
    # 섹션 4: 섹터별 성과
    # ══════════════════════════════════════════════════════
    sec("4. 섹터별 시나리오 초과수익률 히트맵 (매수 공시 추종)",
        "어떤 업종에서 어떤 시나리오가 가장 유리한지 한눈에 확인합니다.")

    heat_rows = []
    for sector in buy_inv["섹터"].dropna().unique():
        s_df = buy_inv[buy_inv["섹터"] == sector]
        row = {"섹터": sector}
        for sc in SCENARIOS:
            exc_col = f"개인_{sc['col']}_초과수익률"
            if exc_col in s_df.columns:
                row[sc["label"]] = round(s_df[exc_col].dropna().mean() * 100, 2)
            else:
                row[sc["label"]] = np.nan
        heat_rows.append(row)

    heat_df = pd.DataFrame(heat_rows).set_index("섹터").dropna(how="all")
    heat_df  = heat_df.sort_values("시나리오 B", ascending=False)

    fig_heat2 = go.Figure(go.Heatmap(
        z=heat_df.values,
        x=heat_df.columns.tolist(),
        y=heat_df.index.tolist(),
        colorscale="RdYlGn", zmid=0,
        text=np.round(heat_df.values, 1),
        texttemplate="%{text}%p",
        colorbar=dict(title="초과수익률"),
    ))
    fig_heat2.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_heat2, use_container_width=True)
    tip("🟢 진한 초록 = 해당 섹터·시나리오 조합에서 KOSPI 대비 초과수익 달성. 🔴 빨간 = 시장에 미치지 못했습니다. 섹터를 고를 때 가장 진한 초록 셀을 노리는 전략이 유효합니다.")

    st.divider()

    # ══════════════════════════════════════════════════════
    # 섹션 5: 최종 결론 — 투자 적정 시기
    # ══════════════════════════════════════════════════════
    sec("5. 최종 결론 — 공시 후 개인투자자 투자 적정 시기",
        "세 시나리오의 수익률·초과수익률·승률을 종합해 최적 전략을 도출합니다.")

    best_sc  = sc_stats[best_idx]
    best_lbl = best_sc["label"]

    # 종합 순위표
    rank_data = {
        "순위": ["🥇 1위", "🥈 2위", "🥉 3위"],
        "시나리오": [sc["label"] for sc in sc_stats],
        "진입": [sc["entry"] for sc in sc_stats],
        "청산": [sc["exit"] for sc in sc_stats],
        "보유기간": [sc["hold"] for sc in sc_stats],
        "평균수익률": [f'{sc["avg_ret"]:+.1f}%' for sc in sc_stats],
        "초과수익률": [f'{sc["avg_exc"]:+.1f}%p' for sc in sc_stats],
        "절대승률": [f'{sc["win_abs"]:.1f}%' for sc in sc_stats],
        "초과승률": [f'{sc["win_exc"]:.1f}%' for sc in sc_stats],
    }
    rank_sorted = sorted(zip(
        [sc["avg_ret"] for sc in sc_stats],
        range(3)
    ), reverse=True)

    rank_df = pd.DataFrame({
        "시나리오":  [sc_stats[i]["label"]  for _, i in rank_sorted],
        "진입시점":  [sc_stats[i]["entry"]  for _, i in rank_sorted],
        "청산시점":  [sc_stats[i]["exit"]   for _, i in rank_sorted],
        "보유기간":  [sc_stats[i]["hold"]   for _, i in rank_sorted],
        "평균수익률":[f'{sc_stats[i]["avg_ret"]:+.1f}%' for _, i in rank_sorted],
        "초과수익률":[f'{sc_stats[i]["avg_exc"]:+.1f}%p' for _, i in rank_sorted],
        "절대승률":  [f'{sc_stats[i]["win_abs"]:.1f}%' for _, i in rank_sorted],
        "초과승률":  [f'{sc_stats[i]["win_exc"]:.1f}%' for _, i in rank_sorted],
    })
    rank_df.insert(0, "순위", ["🥇", "🥈", "🥉"])

    st.dataframe(rank_df, use_container_width=True, hide_index=True)

    # 최종 결론 박스
    second_idx = rank_sorted[1][1]
    second_sc  = sc_stats[second_idx]

    st.markdown(f"""
    <div class='conclude'>
    <b>📌 최종 결론: 개인투자자 최적 공시 추종 시기</b><br><br>

    🏆 <b>1순위 — {best_sc["label"]} ({best_sc["entry"]} 진입 → {best_sc["exit"]} 매도, {best_sc["hold"]})</b><br>
    &nbsp;&nbsp;&nbsp;&nbsp;평균 수익률 <b>{best_sc["avg_ret"]:+.1f}%</b>, 초과수익률 <b>{best_sc["avg_exc"]:+.1f}%p</b>, 절대 승률 <b>{best_sc["win_abs"]:.1f}%</b><br>
    &nbsp;&nbsp;&nbsp;&nbsp;→ 국민연금 매수 공시 확인 후 바로 진입하고, 장기 보유할 때 가장 높은 수익을 기대할 수 있습니다.<br><br>

    🥈 <b>2순위 — {second_sc["label"]} ({second_sc["entry"]} 진입 → {second_sc["exit"]} 매도, {second_sc["hold"]})</b><br>
    &nbsp;&nbsp;&nbsp;&nbsp;평균 수익률 <b>{second_sc["avg_ret"]:+.1f}%</b>, 초과수익률 <b>{second_sc["avg_exc"]:+.1f}%p</b>, 절대 승률 <b>{second_sc["win_abs"]:.1f}%</b><br>
    &nbsp;&nbsp;&nbsp;&nbsp;→ 비교적 짧은 보유기간으로도 안정적인 수익을 원하는 투자자에게 적합합니다.<br><br>

    ⚠️ <b>공통 주의사항</b><br>
    &nbsp;&nbsp;&nbsp;&nbsp;• 초과수익률이 음수인 시나리오는 절대 수익이 나더라도 시장 평균에 미치지 못했습니다.<br>
    &nbsp;&nbsp;&nbsp;&nbsp;• 승률이 50%에 가까울수록 '운'의 요소가 크게 작용합니다.<br>
    &nbsp;&nbsp;&nbsp;&nbsp;• 섹터 히트맵을 함께 참고해 초과수익 가능성이 높은 업종에 집중하는 것을 권장합니다.
    </div>
    """, unsafe_allow_html=True)

    # 체크리스트
    st.markdown("### ✅ 공시 추종 투자 전 체크리스트")
    st.markdown("""
    <div style='background:white; border:1px solid #E0E0E0; border-radius:14px;
                padding:22px 28px; line-height:2.1; font-size:0.93rem;'>
    ☑️ &nbsp;<b>매수 공시인지 확인</b> — 매도 공시 추종은 수익률이 낮습니다<br>
    ☑️ &nbsp;<b>섹터 히트맵 확인</b> — 초과수익률이 양수(초록)인 섹터 종목에 집중<br>
    ☑️ &nbsp;<b>공시 날짜 확인</b> — 공시 기준일로부터 90일(시나리오 A·B) 또는 180일(시나리오 C)에 진입<br>
    ☑️ &nbsp;<b>보유 기간 결정</b> — 장기 보유(시나리오 B) 전략이 평균적으로 유리<br>
    ☑️ &nbsp;<b>국민연금 운용 성과 확인</b> — Page 1의 기간수익률이 마이너스이면 시장 전체가 불리한 환경<br>
    ☑️ &nbsp;<b>분산 투자</b> — 승률이 50~60%대이므로 여러 공시 종목에 나눠 투자<br>
    ☑️ &nbsp;<b>손절 기준 사전 설정</b> — 투자 전 "얼마까지 손실 나면 매도" 기준을 미리 정할 것
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='warn' style='margin-top:24px'>
    ⚠️ <b>투자 주의사항</b> — 이 분석은 2022~2025년 과거 데이터에 기반한 참고 자료입니다.
    국민연금 공시를 따라 투자하더라도 <b>손실이 발생할 수 있으며</b>, 모든 투자 결정과 그 결과는
    투자자 본인의 책임입니다. 과거 수익률은 미래 수익을 보장하지 않습니다.
    항상 투자 성향과 여유 자금 범위 내에서 투자하세요.
    </div>
    """, unsafe_allow_html=True)

    st.caption("데이터 출처: 국민연금공단 공시 정보 | 분석 기간: 2022~2025 | 본 자료는 투자 참고용이며 모든 투자 손익의 책임은 투자자 본인에게 있습니다.")
