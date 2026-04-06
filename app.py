import streamlit as st
from data import (
    fetch_clinical_trials,
    fetch_recent_trials,
    build_whitespace_scorecard,
)
from synthesis import (
    synthesize_external_landscape,
    synthesize_partnership_portfolio,
    synthesize_resource_allocation,
)
import plotly.express as px
import pandas as pd
from datetime import datetime

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Proxima · Strategic Intelligence",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Styles ─────────────────────────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
    * { font-family: 'Inter', sans-serif !important; }
    .stApp { background-color: #000000; }
    section[data-testid="stSidebar"] { display: none; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 2rem 3rem 4rem 3rem; max-width: 1400px; }

    .stTabs [data-baseweb="tab-list"] {
        background: #0a0a0a;
        border: 1px solid #222;
        border-radius: 10px;
        padding: 6px;
        gap: 4px;
        margin-bottom: 32px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #666;
        border-radius: 7px;
        padding: 10px 24px;
        font-size: 13px;
        font-weight: 500;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background: #141414;
        color: #ffffff;
        border: 1px solid #333;
    }
    .stButton > button {
        background: #0a0a0a;
        color: #cccccc;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 13px;
        font-weight: 500;
    }
    .stButton > button:hover {
        background: #141414;
        border-color: #555;
        color: #ffffff;
    }
    .stSelectbox > div > div {
        background: #0a0a0a !important;
        border: 1px solid #222 !important;
        color: #ddd !important;
        border-radius: 8px !important;
        font-size: 13px !important;
    }
    .stSelectbox label {
        color: #666 !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    .stTextInput > div > div > input {
        background: #0a0a0a !important;
        border: 1px solid #222 !important;
        color: #ddd !important;
        border-radius: 8px !important;
        font-size: 13px !important;
    }
    .stTextInput label {
        color: #666 !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    .stDataFrame {
        border: 1px solid #1a1a1a !important;
        border-radius: 10px !important;
        overflow: hidden;
    }
    .stSpinner > div { border-top-color: #3ea8cf !important; }

    .card {
        background: #0a0a0a;
        border: 1px solid #1e1e1e;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 12px;
    }
    .metric-card {
        background: #0a0a0a;
        border: 1px solid #1e1e1e;
        border-radius: 12px;
        padding: 24px 20px;
        text-align: center;
    }
    .metric-number {
        font-size: 38px;
        font-weight: 700;
        color: #ffffff;
        line-height: 1;
        margin-bottom: 8px;
    }
    .metric-label {
        font-size: 11px;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 500;
    }
    .section-label {
        font-size: 11px;
        font-weight: 600;
        color: #444;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin: 32px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid #151515;
    }
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
    }
    .badge-green  { background:#071a0f; color:#3ecf8e;
                    border:1px solid #0d3320; }
    .badge-yellow { background:#1a1500; color:#d4a017;
                    border:1px solid #332b00; }
    .badge-blue   { background:#051525; color:#3ea8cf;
                    border:1px solid #0d2d45; }
    .badge-red    { background:#1a0505; color:#cf4f4f;
                    border:1px solid #330d0d; }
    .badge-purple { background:#110515; color:#a855f7;
                    border:1px solid #2a0d3a; }
    .insight-card {
        background: #050505;
        border-radius: 10px;
        padding: 20px 24px;
        line-height: 1.9;
        font-size: 14px;
        color: #cccccc;
    }
    .field-label {
        font-size: 10px;
        color: #555;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .field-value {
        font-size: 13px;
        color: #aaaaaa;
        margin-top: 3px;
    }

    /* Inline toggle buttons for scorecard */
    div[data-testid="stButton"] button[kind="secondary"] {
        background: transparent !important;
        border: none !important;
        color: #555 !important;
        font-size: 12px !important;
        padding: 2px 0 !important;
        font-weight: 500 !important;
        text-align: left !important;
    }
    div[data-testid="stButton"] button[kind="secondary"]:hover {
        color: #aaa !important;
        background: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
now = datetime.now().strftime("%B %d, %Y")
st.markdown(f"""
<div style="display:flex; justify-content:space-between; align-items:flex-end;
            padding:8px 0 36px 0; border-bottom:1px solid #151515;
            margin-bottom:32px;">
    <div>
        <div style="font-size:11px; color:#444; letter-spacing:2.5px;
                    text-transform:uppercase; margin-bottom:10px;
                    font-weight:500;">
            PROXIMA · INTERNAL · CONFIDENTIAL
        </div>
        <div style="font-size:32px; font-weight:700; color:#ffffff;
                    letter-spacing:-0.5px; line-height:1.1;">
            Strategic Intelligence
        </div>
        <div style="font-size:14px; color:#666; margin-top:8px;">
            External landscape &nbsp;·&nbsp; Partnership portfolio
            &nbsp;·&nbsp; Resource allocation
        </div>
    </div>
    <div style="text-align:right;">
        <div style="font-size:11px; color:#444; text-transform:uppercase;
                    letter-spacing:1px; margin-bottom:4px;">
            LAST REFRESHED
        </div>
        <div style="font-size:13px; color:#777; font-weight:500;">{now}</div>
        <div style="margin-top:10px;">
            <span class="badge badge-green">● Live data</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Session state initialization ───────────────────────────────────────────────
if "show_trials" not in st.session_state:
    st.session_state.show_trials = False

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "  🌐  External Landscape  ",
    "  🤝  Partnership Portfolio  ",
    "  📊  Resource Allocation  ",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — EXTERNAL LANDSCAPE
# ══════════════════════════════════════════════════════════════════════════════
with tab1:

    st.markdown("""
    <div class="card" style="border-left:2px solid #1e3a4a;">
        <div style="font-size:11px; color:#3ea8cf; font-weight:600;
                    text-transform:uppercase; letter-spacing:1.5px;
                    margin-bottom:8px;">EXTERNAL LANDSCAPE</div>
        <div style="font-size:15px; color:#ffffff; font-weight:600;
                    margin-bottom:6px;">
            Where should Proxima focus next?
        </div>
        <div style="font-size:13px; color:#777; line-height:1.8;">
            Live data from ClinicalTrials.gov mapped against competitive
            positioning. Every target class scored across clinical validation,
            competitive whitespace, and NeoLink data advantage — so the
            answer isn't a guess, it's in the numbers.
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Pulling live data from ClinicalTrials.gov..."):
        trials_df = fetch_clinical_trials()
        recent_df = fetch_recent_trials(days=365)

    st.markdown("<div class='section-label'>Live Market Snapshot</div>",
                unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    total_trials  = len(trials_df)  if not trials_df.empty else 0
    recent_trials = len(recent_df)  if not recent_df.empty else 0
    sponsors      = trials_df["Sponsor"].nunique() if not trials_df.empty else 0
    modalities    = trials_df["Modality"].nunique() if not trials_df.empty else 0

    for col, num, label in zip(
        [m1, m2, m3, m4],
        [total_trials, recent_trials, sponsors, modalities],
        ["Active ProMod trials", "New trials (12 mo)",
         "Unique sponsors", "Modalities tracked"]
    ):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">{num}</div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    # ── Whitespace Scorecard ───────────────────────────────────────────────────
    st.markdown(
        "<div class='section-label'>Strategic Whitespace Scorecard</div>",
        unsafe_allow_html=True)

    st.markdown("""
    <div class="card" style="border-left:2px solid #1e3a4a;
                              margin-bottom:20px;">
        <div style="font-size:13px; color:#aaaaaa; line-height:1.8;">
            Each target class scored across
            <b style="color:#3ea8cf;">Clinical Validation</b>
            (is the biology proven in the clinic?),
            <b style="color:#3ecf8e;">Competitive Whitespace</b>
            (how crowded is this space?), and
            <b style="color:#d4a017;">NeoLink Advantage</b>
            (do we have structural data coverage?).
            Opportunity Score combines all three.
            Strategic Priority shows where the gap between opportunity
            and Proxima's current position is largest.
        </div>
    </div>
    """, unsafe_allow_html=True)

    scorecard_df = build_whitespace_scorecard(trials_df)

    leg1, leg2, leg3, leg4 = st.columns(4)
    for col, icon, label, desc, color in zip(
        [leg1, leg2, leg3, leg4],
        ["🔴", "🟡", "🟢", "⚪"],
        ["Act Now", "Strengthen", "Maintain", "Monitor"],
        ["High opportunity, no Proxima coverage",
         "Strong opportunity, partial coverage",
         "Well positioned, keep investing",
         "Early stage or low priority"],
        ["#cf4f4f", "#d4a017", "#3ecf8e", "#555"]
    ):
        with col:
            st.markdown(f"""
            <div class="metric-card" style="text-align:left; padding:16px;">
                <div style="font-size:18px; margin-bottom:6px;">{icon}</div>
                <div style="font-size:12px; font-weight:700;
                            color:{color}; margin-bottom:4px;">{label}</div>
                <div style="font-size:11px; color:#666;
                            line-height:1.5;">{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:20px;'></div>",
                unsafe_allow_html=True)

    for _, row in scorecard_df.iterrows():
        target_class = row["Target Class"]
        priority = row["Strategic Priority"]
        priority_color = {
            "🔴 Act Now":    "#cf4f4f",
            "🟡 Strengthen": "#d4a017",
            "🟢 Maintain":   "#3ecf8e",
            "⚪ Monitor":    "#444",
        }.get(priority, "#444")

        coverage_badge = {
            3: "<span class='badge badge-green'>Full coverage</span>",
            2: "<span class='badge badge-yellow'>Partial coverage</span>",
            1: "<span class='badge badge-red'>No coverage</span>",
        }.get(row["Coverage Score"], "")

        neolink_badge = {
            "High":   "<span class='badge badge-green'>NeoLink: High</span>",
            "Medium": "<span class='badge badge-yellow'>NeoLink: Medium</span>",
            "Low":    "<span class='badge badge-red'>NeoLink: Low</span>",
        }.get(row["NeoLink Coverage"], "")

        def score_bar(score, max_score=3):
            return ("█" * score) + ("░" * (max_score - score))

        st.markdown(f"""
        <div class="card" style="border-left:2px solid {priority_color};
                                  margin-bottom:4px;">
            <div style="display:flex; justify-content:space-between;
                        align-items:flex-start;">
                <div>
                    <div style="font-size:16px; font-weight:700;
                                color:#ffffff; margin-bottom:4px;">
                        {row["Target Class"]}
                    </div>
                    <div style="font-size:12px; color:#666;">
                        {row["Modality"]} &nbsp;·&nbsp; {row["Indication"]}
                    </div>
                </div>
                <div style="display:flex; gap:6px; flex-wrap:wrap;
                            justify-content:flex-end; align-items:center;">
                    {coverage_badge}
                    {neolink_badge}
                    <span style="font-size:13px; font-weight:700;
                                 color:{priority_color};">{priority}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        trial_key = f"trials_{target_class.replace(' ','_').replace('/','_')}"
        comp_key  = f"comp_{target_class.replace(' ','_').replace('/','_')}"
        if trial_key not in st.session_state:
            st.session_state[trial_key] = False
        if comp_key not in st.session_state:
            st.session_state[comp_key] = False

        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.markdown(f"""
            <div style="padding:14px 0 4px 0;">
                <div class="field-label" style="color:#3ea8cf;">
                    CLINICAL VALIDATION</div>
                <div style="font-size:18px; color:#3ea8cf;
                            font-family:monospace; letter-spacing:3px;
                            margin:8px 0 4px 0;">
                    {score_bar(row["Validation Score"])}
                </div>
            </div>""", unsafe_allow_html=True)
            trial_btn = (
                f"▾ {row['Clinical Trials']} active trials"
                if st.session_state[trial_key]
                else f"▸ {row['Clinical Trials']} active trials"
            )
            if st.button(trial_btn, key=f"btn_{trial_key}"):
                st.session_state[trial_key] = not st.session_state[trial_key]

        with sc2:
            st.markdown(f"""
            <div style="padding:14px 0 4px 0;">
                <div class="field-label" style="color:#3ecf8e;">
                    COMPETITIVE WHITESPACE</div>
                <div style="font-size:18px; color:#3ecf8e;
                            font-family:monospace; letter-spacing:3px;
                            margin:8px 0 4px 0;">
                    {score_bar(row["Whitespace Score"])}
                </div>
            </div>""", unsafe_allow_html=True)
            comp_btn = (
                f"▾ {row['Competitors']} known competitors"
                if st.session_state[comp_key]
                else f"▸ {row['Competitors']} known competitors"
            )
            if st.button(comp_btn, key=f"btn_{comp_key}"):
                st.session_state[comp_key] = not st.session_state[comp_key]

        with sc3:
            st.markdown(f"""
            <div style="padding:14px 0 8px 0;">
                <div class="field-label" style="color:#d4a017;">
                    OPPORTUNITY SCORE</div>
                <div style="font-size:28px; font-weight:700; color:#ffffff;
                            margin:6px 0 4px 0;">
                    {row["Opportunity Score"]}
                    <span style="font-size:14px; color:#444;">/9</span>
                </div>
                <div class="field-value">Combined signal strength</div>
            </div>""", unsafe_allow_html=True)

        target_trial_map = {
            "E3 Ligase / Molecular Glue":
                trials_df[trials_df["Modality"] == "Molecular Glue"][
                    ["Title","Sponsor","Phase","Indication"]
                ].head(5) if not trials_df.empty else pd.DataFrame(),
            "BRD / Transcription Factor":
                trials_df[trials_df["Modality"] == "PROTAC"][
                    ["Title","Sponsor","Phase","Indication"]
                ].head(5) if not trials_df.empty else pd.DataFrame(),
            "RIPTAC Targets":
                trials_df[trials_df["Modality"] == "RIPTAC"][
                    ["Title","Sponsor","Phase","Indication"]
                ].head(5) if not trials_df.empty else pd.DataFrame(),
        }

        competitor_map = {
            "E3 Ligase / Molecular Glue": [
                "Monte Rosa Therapeutics — QuEEN platform, Phase 1",
                "Kymera Therapeutics — expanding to glues, Phase 2",
                "Revolution Medicines — daraxonrasib, Phase 3",
                "C4 Therapeutics — TORPEDO platform, Phase 1/2",
            ],
            "BRD / Transcription Factor": [
                "Arvinas — BRD-targeting PROTACs, Phase 3",
                "Kymera Therapeutics — BRD degraders, Phase 2",
                "Nurix Therapeutics — DEL platform, Phase 2",
            ],
            "Kinase / Scaffolding Protein": [
                "Kymera Therapeutics — adjacent kinase programs",
            ],
            "RIPTAC Targets": [
                "Halda Therapeutics — active Proxima partner, preclinical",
            ],
            "Immune Modulators": [
                "Nurix Therapeutics — immunology focus, Phase 2",
                "Kymera Therapeutics — immunology programs, Phase 2",
            ],
            "CNS Targets": [],
            "Cardiovascular Targets": [
                "Nurix Therapeutics — adjacent degrader programs",
            ],
            "Viral / Infectious Disease": [],
        }

        show_trials     = st.session_state.get(trial_key, False)
        show_comp       = st.session_state.get(comp_key, False)
        relevant_trials = target_trial_map.get(target_class, pd.DataFrame())
        relevant_comps  = competitor_map.get(target_class, [])

        if show_trials or show_comp:
            detail1, detail2 = st.columns(2)
            with detail1:
                if show_trials:
                    if not relevant_trials.empty:
                        for _, t in relevant_trials.iterrows():
                            st.markdown(f"""
                            <div style="background:#050505;
                                        border:1px solid #151515;
                                        border-radius:6px;
                                        padding:10px 14px;
                                        margin-bottom:6px;">
                                <div style="font-size:12px; color:#ccc;
                                            margin-bottom:4px;
                                            line-height:1.5;">
                                    {t['Title'][:75]}{'...' if len(t['Title'])>75 else ''}
                                </div>
                                <div style="display:flex; gap:12px;">
                                    <span style="font-size:11px; color:#555;">
                                        {t['Sponsor'][:30]}
                                    </span>
                                    <span style="font-size:11px;
                                                 color:#3ea8cf;">
                                        {t['Phase']}
                                    </span>
                                </div>
                            </div>""", unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div style="font-size:12px; color:#444;
                                    padding:8px 0;">
                            No exact modality match in current dataset.
                        </div>""", unsafe_allow_html=True)
            with detail2:
                if show_comp:
                    if relevant_comps:
                        for c in relevant_comps:
                            st.markdown(f"""
                            <div style="background:#050505;
                                        border:1px solid #151515;
                                        border-radius:6px;
                                        padding:10px 14px;
                                        margin-bottom:6px;">
                                <div style="font-size:12px; color:#ccc;
                                            line-height:1.5;">{c}</div>
                            </div>""", unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div style="font-size:12px; color:#3ecf8e;
                                    padding:8px 0; font-weight:500;">
                            No known competitors — this space is open.
                        </div>""", unsafe_allow_html=True)

        cv1, cv2 = st.columns(2)
        with cv1:
            st.markdown(f"""
            <div style="padding:4px 0 8px 0;">
                <div class="field-label">PROXIMA PROGRAM</div>
                <div class="field-value">{row["Proxima Program"]}</div>
            </div>""", unsafe_allow_html=True)
        with cv2:
            st.markdown(f"""
            <div style="padding:4px 0 8px 0;">
                <div class="field-label">ACTIVE PARTNER</div>
                <div class="field-value">{row["Proxima Partner"]}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="font-size:13px; color:#888; line-height:1.8;
                    border-top:1px solid #151515; padding-top:12px;
                    margin-bottom:20px;">
            {row["Whitespace Notes"]}
        </div>""", unsafe_allow_html=True)

    # ── Opportunity Matrix ─────────────────────────────────────────────────────
    st.markdown("<div class='section-label'>Opportunity Matrix</div>",
                unsafe_allow_html=True)

    st.markdown("""
    <div class="card" style="margin-bottom:16px;">
        <div style="font-size:13px; color:#777; line-height:1.8;">
            Each bubble is a target class.
            <b style="color:#cccccc;">X-axis</b> = competitive whitespace.
            <b style="color:#cccccc;">Y-axis</b> = clinical validation.
            <b style="color:#cccccc;">Bubble size</b> = NeoLink data coverage.
            Top-right is the sweet spot: validated biology, open field,
            strong data advantage.
        </div>
    </div>""", unsafe_allow_html=True)

    fig_ws = px.scatter(
        scorecard_df,
        x="Whitespace Score",
        y="Validation Score",
        size="NeoLink Score",
        color="Strategic Priority",
        hover_name="Target Class",
        hover_data={
            "Modality": True,
            "Indication": True,
            "Clinical Trials": True,
            "Competitors": True,
            "Proxima Program": True,
            "Whitespace Score": False,
            "Validation Score": False,
            "NeoLink Score": False,
        },
        title="Target Class Opportunity Matrix",
        color_discrete_map={
            "🔴 Act Now":    "#cf4f4f",
            "🟡 Strengthen": "#d4a017",
            "🟢 Maintain":   "#3ecf8e",
            "⚪ Monitor":    "#555",
        },
        size_max=45,
    )
    fig_ws.update_layout(
        plot_bgcolor="#050505", paper_bgcolor="#050505",
        font_color="#555", title_font_color="#888",
        title_font_size=13, margin=dict(t=40,l=10,r=10,b=10),
        xaxis=dict(
            title="Competitive Whitespace",
            tickvals=[1,2,3],
            ticktext=["Crowded","Some room","Wide open"],
            gridcolor="#111", showline=False, range=[0.5,3.5],
            title_font_color="#666", tickfont_color="#555",
        ),
        yaxis=dict(
            title="Clinical Validation",
            tickvals=[1,2,3],
            ticktext=["Early","Emerging","Validated"],
            gridcolor="#111", showline=False, range=[0.5,3.5],
            title_font_color="#666", tickfont_color="#555",
        ),
        legend=dict(bgcolor="#050505", bordercolor="#1a1a1a", borderwidth=1),
    )
    fig_ws.add_annotation(
        x=2.8, y=2.8, text="Sweet spot", showarrow=False,
        font=dict(color="#3ecf8e", size=11),
        bgcolor="#071a0f", bordercolor="#0d3320",
        borderwidth=1, borderpad=4)
    fig_ws.add_annotation(
        x=1.2, y=2.8, text="Crowded but validated", showarrow=False,
        font=dict(color="#d4a017", size=11),
        bgcolor="#1a1500", bordercolor="#332b00",
        borderwidth=1, borderpad=4)
    fig_ws.add_annotation(
        x=2.8, y=1.2, text="Pioneer territory", showarrow=False,
        font=dict(color="#3ea8cf", size=11),
        bgcolor="#051525", bordercolor="#0d2d45",
        borderwidth=1, borderpad=4)
    st.plotly_chart(fig_ws, use_container_width=True)

    # ── Competitive Landscape ──────────────────────────────────────────────────
    st.markdown("<div class='section-label'>Competitive Landscape</div>",
                unsafe_allow_html=True)

    st.markdown("""
    <div class="card" style="margin-bottom:16px;">
        <div style="font-size:13px; color:#777; line-height:1.8;">
            Key players in the ProMod space assessed through Proxima's lens —
            not just who they are, but what they mean for Proxima's
            positioning, partnership strategy, and differentiation.
        </div>
    </div>""", unsafe_allow_html=True)

    competitors = [
        {
            "Company": "Arvinas",
            "Modality": "PROTAC",
            "Lead Indication": "ER+ Breast Cancer, Prostate Cancer",
            "Most Advanced": "Phase 3",
            "Funding": "Public (ARVN)",
            "Computational Platform": "Limited",
            "Proxima Relevance": "Most advanced PROTAC player globally. Phase 3 data will validate or stress-test the modality broadly — either outcome matters for Proxima's BD narrative. Not a direct platform competitor, wet-lab heavy with no meaningful computational moat.",
            "Threat Level": "Medium",
        },
        {
            "Company": "Kymera Therapeutics",
            "Modality": "PROTAC / Molecular Glue",
            "Lead Indication": "Immunology, Oncology",
            "Most Advanced": "Phase 2",
            "Funding": "Public (KYMR)",
            "Computational Platform": "Moderate",
            "Proxima Relevance": "Expanding into molecular glues and building computational capabilities. Closest public-company analog to Proxima's target space. Worth watching as they scale — if their platform matures it narrows Proxima's differentiation window.",
            "Threat Level": "High",
        },
        {
            "Company": "Monte Rosa Therapeutics",
            "Modality": "Molecular Glue",
            "Lead Indication": "Oncology",
            "Most Advanced": "Phase 1",
            "Funding": "Public (GLUE)",
            "Computational Platform": "Strong",
            "Proxima Relevance": "QuEEN computational platform for glue discovery is the most direct analog to Neo-1 in the glue space. The key benchmark for Proxima's differentiation claims — Neo-1 needs to demonstrably outperform QuEEN on ternary complex design.",
            "Threat Level": "High",
        },
        {
            "Company": "Revolution Medicines",
            "Modality": "Molecular Glue / RAS Inhibitor",
            "Lead Indication": "RAS-driven Cancers",
            "Most Advanced": "Phase 3",
            "Funding": "Public (RVMD)",
            "Computational Platform": "Moderate",
            "Proxima Relevance": "Daraxonrasib is the leading clinical proof point for molecular glues as a modality. Phase 3 success is a rising tide — it validates the entire space and strengthens Proxima's partnership pitch to pharma.",
            "Threat Level": "Medium",
        },
        {
            "Company": "C4 Therapeutics",
            "Modality": "PROTAC / Molecular Glue",
            "Lead Indication": "Oncology",
            "Most Advanced": "Phase 1/2",
            "Funding": "Public (CCCC)",
            "Computational Platform": "Moderate",
            "Proxima Relevance": "Commercially challenged despite a credible platform. A cautionary signal: platform credibility alone doesn't translate to value without a strong data flywheel and clinical execution. Proxima should internalize this lesson.",
            "Threat Level": "Medium",
        },
        {
            "Company": "Halda Therapeutics",
            "Modality": "RIPTAC",
            "Lead Indication": "Oncology",
            "Most Advanced": "Preclinical",
            "Funding": "Private",
            "Computational Platform": "Limited",
            "Proxima Relevance": "Active Proxima partner ($1B+ deal). Proxima is their entire computational backbone — Neo-1's performance on RIPTAC ternary complexes directly determines Halda's clinical trajectory. Monitor closely.",
            "Threat Level": "Partner",
        },
        {
            "Company": "Nurix Therapeutics",
            "Modality": "Targeted Protein Degradation",
            "Lead Indication": "Oncology, Immunology",
            "Most Advanced": "Phase 2",
            "Funding": "Public (NRIX)",
            "Computational Platform": "Moderate",
            "Proxima Relevance": "DEL-based degrader discovery — different technical approach. Overlapping indication space but not a direct platform competitor. Phase 2 data in immunology is relevant context for Proxima's own immunology positioning.",
            "Threat Level": "Low",
        },
        {
            "Company": "Relay Therapeutics",
            "Modality": "Small Molecule (Conformational)",
            "Lead Indication": "Oncology",
            "Most Advanced": "Phase 2",
            "Funding": "Public (RLAY)",
            "Computational Platform": "Very Strong",
            "Proxima Relevance": "Not in ProMod space but the gold standard for AI-native biotech execution and platform credibility. What Proxima should aspire to in terms of how the scientific community and pharma partners perceive the platform.",
            "Threat Level": "Low",
        },
    ]

    comp_df = pd.DataFrame(competitors)

    cf1, cf2 = st.columns([1, 1])
    with cf1:
        threat_filter = st.selectbox(
            "Filter by relevance",
            ["All", "High", "Medium", "Low", "Partner"])
    with cf2:
        mod_filter = st.selectbox(
            "Filter by modality",
            ["All"] + sorted(comp_df["Modality"].unique().tolist()),
            key="comp_mod")

    filtered_comp = comp_df.copy()
    if threat_filter != "All":
        filtered_comp = filtered_comp[
            filtered_comp["Threat Level"] == threat_filter]
    if mod_filter != "All":
        filtered_comp = filtered_comp[
            filtered_comp["Modality"] == mod_filter]

    for _, row in filtered_comp.iterrows():
        badge_map = {
            "High":    "badge-red",
            "Medium":  "badge-yellow",
            "Low":     "badge-blue",
            "Partner": "badge-green",
        }
        label_map = {
            "High":    "High relevance",
            "Medium":  "Medium relevance",
            "Low":     "Low relevance",
            "Partner": "Active partner",
        }
        phase_color = {
            "Phase 3":    "badge-red",
            "Phase 2":    "badge-yellow",
            "Phase 1/2":  "badge-yellow",
            "Phase 1":    "badge-blue",
            "Preclinical":"badge-blue",
        }.get(row["Most Advanced"], "badge-blue")

        st.markdown(f"""
        <div class="card">
            <div style="display:flex; justify-content:space-between;
                        align-items:flex-start; margin-bottom:12px;">
                <div>
                    <span style="font-size:16px; font-weight:700;
                                 color:#ffffff;">{row["Company"]}</span>
                    <span style="font-size:12px; color:#555;
                                 margin-left:10px;">{row["Modality"]}</span>
                </div>
                <div style="display:flex; gap:6px; flex-wrap:wrap;">
                    <span class="badge {phase_color}">
                        {row["Most Advanced"]}
                    </span>
                    <span class="badge {badge_map[row['Threat Level']]}">
                        {label_map[row['Threat Level']]}
                    </span>
                </div>
            </div>
            <div style="font-size:13px; color:#888; line-height:1.8;
                        margin-bottom:14px;">
                {row["Proxima Relevance"]}
            </div>
            <div style="display:flex; gap:32px; flex-wrap:wrap;">
                <div>
                    <div class="field-label">INDICATION</div>
                    <div class="field-value">{row["Lead Indication"]}</div>
                </div>
                <div>
                    <div class="field-label">FUNDING</div>
                    <div class="field-value">{row["Funding"]}</div>
                </div>
                <div>
                    <div class="field-label">COMP. PLATFORM</div>
                    <div class="field-value">
                        {row["Computational Platform"]}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Clinical Trials (toggle) ───────────────────────────────────────────────
    if st.button(
        "Hide clinical trial data ↑" if st.session_state.show_trials
        else "View full clinical trial data ↓",
        key="trials_toggle"
    ):
        st.session_state.show_trials = not st.session_state.show_trials

    if st.session_state.show_trials:
        if not trials_df.empty:
            f1, f2, f3 = st.columns([1, 1, 2])
            with f1:
                mod_opts = ["All modalities"] + \
                           sorted(trials_df["Modality"].unique().tolist())
                sel_mod = st.selectbox("Modality", mod_opts)
            with f2:
                phase_opts = ["All phases"] + \
                             sorted(trials_df["Phase"].unique().tolist())
                sel_phase = st.selectbox("Phase", phase_opts)
            with f3:
                search = st.text_input(
                    "Search sponsor, indication, or title", "")

            filtered = trials_df.copy()
            if sel_mod != "All modalities":
                filtered = filtered[filtered["Modality"] == sel_mod]
            if sel_phase != "All phases":
                filtered = filtered[filtered["Phase"] == sel_phase]
            if search:
                mask = (
                    filtered["Sponsor"].str.contains(
                        search, case=False, na=False) |
                    filtered["Indication"].str.contains(
                        search, case=False, na=False) |
                    filtered["Title"].str.contains(
                        search, case=False, na=False)
                )
                filtered = filtered[mask]

            st.markdown(f"""
            <div style="font-size:12px; color:#444; margin-bottom:10px;">
                Showing {len(filtered)} of {len(trials_df)} trials
            </div>""", unsafe_allow_html=True)

            display_cols = ["NCT ID", "Title", "Sponsor", "Phase",
                            "Status", "Modality", "Indication", "Start Date"]
            st.dataframe(filtered[display_cols],
                         use_container_width=True,
                         height=380, hide_index=True)

            c1, c2 = st.columns(2)
            chart_layout = dict(
                plot_bgcolor="#050505", paper_bgcolor="#050505",
                font_color="#555", title_font_color="#888",
                title_font_size=13, margin=dict(t=40,l=10,r=10,b=10),
                xaxis=dict(gridcolor="#111", showline=False),
                yaxis=dict(gridcolor="#111", showline=False),
            )
            with c1:
                phase_counts = trials_df["Phase"].value_counts().reset_index()
                phase_counts.columns = ["Phase", "Count"]
                fig1 = px.bar(
                    phase_counts, x="Phase", y="Count",
                    title="Trials by Phase", color="Count",
                    color_continuous_scale=["#0d2535", "#3ea8cf"])
                fig1.update_layout(**chart_layout, showlegend=False,
                                   coloraxis_showscale=False)
                fig1.update_traces(marker_line_width=0)
                st.plotly_chart(fig1, use_container_width=True)

            with c2:
                mod_counts = trials_df["Modality"].value_counts().reset_index()
                mod_counts.columns = ["Modality", "Count"]
                fig2 = px.pie(
                    mod_counts, names="Modality", values="Count",
                    title="Trials by Modality",
                    color_discrete_sequence=[
                        "#3ea8cf","#3ecf8e","#d4a017",
                        "#cf4f4f","#a855f7","#555"])
                fig2.update_layout(
                    plot_bgcolor="#050505", paper_bgcolor="#050505",
                    font_color="#555", title_font_color="#888",
                    title_font_size=13, margin=dict(t=40,l=10,r=10,b=10))
                fig2.update_traces(textfont_color="#ccc",
                                   marker_line_color="#000",
                                   marker_line_width=2)
                st.plotly_chart(fig2, use_container_width=True)

    
# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — PARTNERSHIP PORTFOLIO
# ══════════════════════════════════════════════════════════════════════════════
with tab2:

    st.markdown("""
    <div class="card" style="border-left:2px solid #1a3a1a;">
        <div style="font-size:11px; color:#3ecf8e; font-weight:600;
                    text-transform:uppercase; letter-spacing:1.5px;
                    margin-bottom:8px;">PARTNERSHIP PORTFOLIO</div>
        <div style="font-size:15px; color:#ffffff; font-weight:600;
                    margin-bottom:6px;">All active collaborations in one place
        </div>
        <div style="font-size:13px; color:#777; line-height:1.8;">
            Milestones, data obligations, and decision checkpoints so nothing
            falls through the cracks. Seeded with publicly available
            information — structured for real data entry.
        </div>
    </div>
    """, unsafe_allow_html=True)

    from datetime import date
    today = date.today()

    def days_until(year, month, day):
        delta = date(year, month, day) - today
        return max(0, delta.days)

    partnerships = [
        {
            "Partner": "Johnson & Johnson",
            "Focus": "Molecular Glues / ProMod",
            "Indication": "Oncology",
            "Status": "Active",
            "Deal Value": "$1B+ potential",
            "Programs": 3,
            "Most Advanced": "Preclinical to IND",
            "Next Milestone": "IND Filing",
            "Milestone Date": "2026 (confirmed)",
            "Days Until": days_until(2026, 9, 30),
            "Data Obligations": "Quarterly structural data packages via NeoLink",
            "Joint Steering": "Bi-monthly",
            "Notes": "J&J publicly confirmed first program on track to enter clinical trials in 2026. This is Proxima's most milestone-critical near-term event — triggers the first significant milestone payment and serves as the public proof point for platform-to-clinic execution.",
            "Risk": "Medium",
            "Confirmed": True,
        },
        {
            "Partner": "Bristol Myers Squibb",
            "Focus": "Targeted Protein Degradation",
            "Indication": "Oncology, Immunology",
            "Status": "Active",
            "Deal Value": "Undisclosed",
            "Programs": 2,
            "Most Advanced": "~Lead Optimization",
            "Next Milestone": "Candidate Nomination",
            "Milestone Date": "~Q4 2026",
            "Days Until": days_until(2026, 12, 31),
            "Data Obligations": "~Monthly Neo-1 generation reports",
            "Joint Steering": "~Quarterly",
            "Notes": "BMS has deep internal PROTAC expertise — this partnership is most likely anchored on NeoLink structural data for novel targets where BMS lacks proteome coverage. Milestone timing and obligations are estimated — not publicly confirmed.",
            "Risk": "Low",
            "Confirmed": False,
        },
        {
            "Partner": "Blueprint Medicines (Sanofi)",
            "Focus": "ProMod — Oncology Targets",
            "Indication": "Oncology",
            "Status": "Active",
            "Deal Value": "Undisclosed",
            "Programs": 2,
            "Most Advanced": "~Hit Discovery",
            "Next Milestone": "Hit-to-Lead Completion",
            "Milestone Date": "~Q2 2026",
            "Days Until": days_until(2026, 6, 30),
            "Data Obligations": "~Target structural packages on demand",
            "Joint Steering": "~Monthly",
            "Notes": "Blueprint was acquired by Sanofi — post-acquisition strategic reprioritization is common. Milestone timing is estimated based on typical hit-to-lead timelines. Any delay on the Q2 milestone should trigger a proactive conversation.",
            "Risk": "Medium",
            "Confirmed": False,
        },
        {
            "Partner": "Halda Therapeutics",
            "Focus": "RIPTAC Discovery",
            "Indication": "Oncology",
            "Status": "Active",
            "Deal Value": "$1B+ potential",
            "Programs": 4,
            "Most Advanced": "~Hit Discovery",
            "Next Milestone": "Lead Series Identification",
            "Milestone Date": "~Q3 2026",
            "Days Until": days_until(2026, 9, 30),
            "Data Obligations": "~Neo-1 RIPTAC design packages, NeoLink ternary complex data",
            "Joint Steering": "~Monthly",
            "Notes": "Deepest technical integration in the portfolio. $1B+ deal value publicly confirmed August 2025. Program stage and milestone timing are estimated. Proxima is Halda's entire computational backbone — highest strategic value partnership.",
            "Risk": "Low",
            "Confirmed": False,
        },
        {
            "Partner": "Boehringer Ingelheim",
            "Focus": "ProMod — Undisclosed Targets",
            "Indication": "Undisclosed",
            "Status": "Active",
            "Deal Value": "Undisclosed",
            "Programs": 1,
            "Most Advanced": "~Target Identification",
            "Next Milestone": "Target Validation Package",
            "Milestone Date": "~Q2 2026",
            "Days Until": days_until(2026, 6, 30),
            "Data Obligations": "~NeoLink proteome scan for target class",
            "Joint Steering": "~Quarterly",
            "Notes": "Partnership publicly confirmed. All program details and milestone timing are estimated based on typical early-stage collaboration timelines. BI has strong internal small molecule capabilities — partnership likely scoping NeoLink for target identification.",
            "Risk": "Low",
            "Confirmed": False,
        },
    ]

    # ── Portfolio metrics ──────────────────────────────────────────────────────
    st.markdown("<div class='section-label'>Portfolio Overview</div>",
                unsafe_allow_html=True)

    pm1, pm2, pm3, pm4 = st.columns(4)
    total_p   = len(partnerships)
    total_prg = sum(p["Programs"] for p in partnerships)
    urgent    = sum(1 for p in partnerships if p["Days Until"] <= 90)
    at_risk   = sum(1 for p in partnerships if p["Risk"] == "High")

    for col, num, label, alert in zip(
        [pm1, pm2, pm3, pm4],
        [total_p, total_prg, urgent, at_risk],
        ["Active partners", "Programs in portfolio",
         "Milestones < 90 days", "Elevated risk items"],
        [False, False, True, True]
    ):
        with col:
            color = "#cf4f4f" if (alert and num > 0) else "#ffffff"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number" style="color:{color};">{num}</div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    # ── Milestone timeline ─────────────────────────────────────────────────────
    st.markdown("<div class='section-label'>Milestone Timeline</div>",
                unsafe_allow_html=True)

    for p in sorted(partnerships, key=lambda x: x["Days Until"]):
        d      = p["Days Until"]
        color  = "#cf4f4f" if d<=60 else "#d4a017" if d<=120 else "#3ea8cf"
        label  = "Urgent"  if d<=60 else "Soon"    if d<=120 else "Upcoming"
        b_cls  = "badge-red" if d<=60 else \
                 "badge-yellow" if d<=120 else "badge-blue"
        confirmed_label = (
            "<span style='font-size:10px; color:#3ecf8e; margin-left:8px;'>"
            "✓ Confirmed</span>"
            if p.get("Confirmed")
            else "<span style='font-size:10px; color:#444; margin-left:8px;'>"
            "Est.</span>"
        )
        st.markdown(f"""
        <div class="card" style="border-left:2px solid {color};
                                  padding:16px 20px;">
            <div style="display:flex; justify-content:space-between;
                        align-items:center;">
                <div style="display:flex; align-items:center; gap:12px;">
                    <span class="badge {b_cls}">{label}</span>
                    <span style="font-size:14px; font-weight:600;
                                 color:#ffffff;">{p["Partner"]}</span>
                    <span style="font-size:13px; color:#666;">
                        {p["Next Milestone"]}
                    </span>
                    {confirmed_label}
                </div>
                <div style="text-align:right;">
                    <div style="font-size:13px; color:{color};
                                font-weight:600;">{p["Milestone Date"]}</div>
                    <div style="font-size:11px; color:#555;">
                        ~{d} days
                    </div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    # ── Partnership cards ──────────────────────────────────────────────────────
    st.markdown("<div class='section-label'>Partnership Detail</div>",
                unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:11px; color:#333; margin-bottom:16px;">
        ⓘ Fields marked ~ are estimated from public information.
        Confirmed fields are sourced from public announcements.
    </div>
    """, unsafe_allow_html=True)

    for p in partnerships:
        risk_cls   = {"High":"badge-red","Medium":"badge-yellow",
                      "Low":"badge-green"}.get(p["Risk"],"badge-blue")
        risk_label = {"High":"High risk","Medium":"Monitor",
                      "Low":"On track"}.get(p["Risk"],"")
        d        = p["Days Until"]
        ms_color = "#cf4f4f" if d<=60 else "#d4a017" if d<=120 else "#3ea8cf"
        confirmed_str = (
            "<span style='font-size:10px; color:#3ecf8e;'>✓ Publicly confirmed</span>"
            if p.get("Confirmed")
            else "<span style='font-size:10px; color:#444;'>~ Estimated timeline</span>"
        )

        # ── Card header ────────────────────────────────────────────────────────
        st.markdown(f"""
        <div class="card">
            <div style="display:flex; justify-content:space-between;
                        align-items:flex-start; margin-bottom:16px;">
                <div>
                    <div style="font-size:18px; font-weight:700;
                                color:#ffffff; margin-bottom:3px;">
                        {p["Partner"]}
                    </div>
                    <div style="font-size:12px; color:#555;">{p["Focus"]}</div>
                </div>
                <div style="display:flex; gap:6px;">
                    <span class="badge badge-green">Active</span>
                    <span class="badge {risk_cls}">{risk_label}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Stats row ──────────────────────────────────────────────────────────
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div style="padding:0 0 12px 0;">
                <div class="field-label">INDICATION</div>
                <div class="field-value">{p["Indication"]}</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div style="padding:0 0 12px 0;">
                <div class="field-label">DEAL VALUE</div>
                <div class="field-value">{p["Deal Value"]}</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div style="padding:0 0 12px 0;">
                <div class="field-label">PROGRAMS</div>
                <div class="field-value">~{p["Programs"]} active</div>
            </div>""", unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div style="padding:0 0 12px 0;">
                <div class="field-label">MOST ADVANCED</div>
                <div class="field-value">{p["Most Advanced"]}</div>
            </div>""", unsafe_allow_html=True)

        # ── Milestone box ──────────────────────────────────────────────────────
        st.markdown(f"""
        <div style="background:#050505; border:1px solid #151515;
                    border-radius:8px; padding:14px 18px;
                    margin-bottom:14px;">
            <div style="display:flex; justify-content:space-between;
                        align-items:center;">
                <div>
                    <div class="field-label">NEXT MILESTONE</div>
                    <div style="font-size:15px; color:#ffffff;
                                font-weight:600; margin-top:4px;">
                        {p["Next Milestone"]}
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:14px; color:{ms_color};
                                font-weight:600;">{p["Milestone Date"]}</div>
                    <div style="font-size:11px; margin-top:2px;">
                        {confirmed_str}
                    </div>
                    <div style="font-size:11px; color:#555; margin-top:2px;">
                        ~{d} days away
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Obligations row ────────────────────────────────────────────────────
        ob1, ob2 = st.columns(2)
        with ob1:
            st.markdown(f"""
            <div style="padding:0 0 12px 0;">
                <div class="field-label">DATA OBLIGATIONS</div>
                <div class="field-value">{p["Data Obligations"]}</div>
            </div>""", unsafe_allow_html=True)
        with ob2:
            st.markdown(f"""
            <div style="padding:0 0 12px 0;">
                <div class="field-label">JOINT STEERING COMMITTEE</div>
                <div class="field-value">{p["Joint Steering"]}</div>
            </div>""", unsafe_allow_html=True)

        # ── Notes ──────────────────────────────────────────────────────────────
        st.markdown(f"""
        <div style="font-size:13px; color:#888; line-height:1.8;
                    border-top:1px solid #151515; padding-top:12px;
                    margin-bottom:24px;">
            {p["Notes"]}
        </div>""", unsafe_allow_html=True)
        
# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — RESOURCE ALLOCATION
# ══════════════════════════════════════════════════════════════════════════════
with tab3:

    st.markdown("""
    <div class="card" style="border-left:2px solid #2a1a00;">
        <div style="font-size:11px; color:#d4a017; font-weight:600;
                    text-transform:uppercase; letter-spacing:1.5px;
                    margin-bottom:8px;">RESOURCE ALLOCATION</div>
        <div style="font-size:15px; color:#ffffff; font-weight:600;
                    margin-bottom:6px;">
            Is effort going where the opportunity is?
        </div>
        <div style="font-size:13px; color:#777; line-height:1.8;">
            Internal and partner programs mapped against competitive pressure
            and NeoLink data advantage. Surfaces the resource allocation
            questions leadership needs to answer — and flags where
            the portfolio may be out of balance.
        </div>
    </div>
    """, unsafe_allow_html=True)

    internal_programs = [
        {
            "Program": "PRX-001",
            "Target Class": "E3 Ligase / Substrate",
            "Modality": "Molecular Glue",
            "Indication": "Oncology",
            "Stage": "Lead Optimization",
            "Internal vs Partner": "Internal",
            "NeoLink Coverage": "High",
            "Competitive Pressure": "High",
            "Strategic Fit": "Core",
            "FTEs Allocated": 8,
            "Notes": "Most advanced internal program. Direct overlap with Monte Rosa and Kymera — Neo-1's structural design advantage must be the differentiator. Worth evaluating whether this is better positioned as a partner program.",
        },
        {
            "Program": "PRX-002",
            "Target Class": "BRD / Transcription Factor",
            "Modality": "PROTAC",
            "Indication": "Oncology",
            "Stage": "Hit Discovery",
            "Internal vs Partner": "Internal",
            "NeoLink Coverage": "High",
            "Competitive Pressure": "Medium",
            "Strategic Fit": "Core",
            "FTEs Allocated": 6,
            "Notes": "Strong NeoLink structural data advantage. BRD4 space is crowded but novel BRD family members remain accessible with our proteome coverage.",
        },
        {
            "Program": "PRX-003",
            "Target Class": "Kinase / Scaffolding Protein",
            "Modality": "Molecular Glue",
            "Indication": "Immunology",
            "Stage": "Target Validation",
            "Internal vs Partner": "Internal",
            "NeoLink Coverage": "Medium",
            "Competitive Pressure": "Low",
            "Strategic Fit": "Emerging",
            "FTEs Allocated": 4,
            "Notes": "Immunology whitespace. Limited competition. Our only internal immunology program — underweighted relative to the opportunity size.",
        },
        {
            "Program": "JNJ-PRX-01",
            "Target Class": "Undisclosed",
            "Modality": "ProMod",
            "Indication": "Oncology",
            "Stage": "Preclinical to IND",
            "Internal vs Partner": "J&J",
            "NeoLink Coverage": "High",
            "Competitive Pressure": "Medium",
            "Strategic Fit": "Core",
            "FTEs Allocated": 5,
            "Notes": "First program approaching IND. Most time-sensitive partner deliverable. J&J owns clinical development from IND onward — our job is execution.",
        },
        {
            "Program": "JNJ-PRX-02",
            "Target Class": "Undisclosed",
            "Modality": "ProMod",
            "Indication": "Oncology",
            "Stage": "Lead Optimization",
            "Internal vs Partner": "J&J",
            "NeoLink Coverage": "High",
            "Competitive Pressure": "Low",
            "Strategic Fit": "Core",
            "FTEs Allocated": 3,
            "Notes": "Second J&J program. Earlier stage. Strong NeoLink coverage on target class.",
        },
        {
            "Program": "BMS-PRX-01",
            "Target Class": "Immune Modulator",
            "Modality": "PROTAC",
            "Indication": "Immunology",
            "Stage": "Lead Optimization",
            "Internal vs Partner": "BMS",
            "NeoLink Coverage": "Medium",
            "Competitive Pressure": "Low",
            "Strategic Fit": "Expanding",
            "FTEs Allocated": 4,
            "Notes": "Proxima's first meaningful immunology exposure. Important signal for portfolio diversification — watch BMS data closely.",
        },
        {
            "Program": "HALDA-PRX-01",
            "Target Class": "RIPTAC Target A",
            "Modality": "RIPTAC",
            "Indication": "Oncology",
            "Stage": "Hit Discovery",
            "Internal vs Partner": "Halda",
            "NeoLink Coverage": "High",
            "Competitive Pressure": "Low",
            "Strategic Fit": "Core",
            "FTEs Allocated": 5,
            "Notes": "Lead RIPTAC program. Neo-1 ternary complex strength is uniquely suited here. Minimal external competition — this is where we press the advantage.",
        },
        {
            "Program": "HALDA-PRX-02",
            "Target Class": "RIPTAC Target B",
            "Modality": "RIPTAC",
            "Indication": "Oncology",
            "Stage": "Target Identification",
            "Internal vs Partner": "Halda",
            "NeoLink Coverage": "Medium",
            "Competitive Pressure": "Low",
            "Strategic Fit": "Core",
            "FTEs Allocated": 3,
            "Notes": "Earlier stage RIPTAC program. NeoLink proteome scan ongoing.",
        },
    ]

    prog_df = pd.DataFrame(internal_programs)

    st.markdown("<div class='section-label'>Portfolio Overview</div>",
                unsafe_allow_html=True)

    rm1, rm2, rm3, rm4 = st.columns(4)
    total_p2   = len(prog_df)
    internal_n = len(prog_df[prog_df["Internal vs Partner"] == "Internal"])
    partner_n  = total_p2 - internal_n
    total_ftes = prog_df["FTEs Allocated"].sum()

    for col, num, label in zip(
        [rm1, rm2, rm3, rm4],
        [total_p2, internal_n, partner_n, total_ftes],
        ["Total programs", "Internal", "Partner", "Total FTEs allocated"]
    ):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">{num}</div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown(
        "<div class='section-label'>Opportunity vs. Effort Matrix</div>",
        unsafe_allow_html=True)

    st.markdown("""
    <div class="card" style="margin-bottom:16px;">
        <div style="font-size:13px; color:#777; line-height:1.8;">
            <b style="color:#cccccc;">X-axis</b> = competitive pressure.
            <b style="color:#cccccc;">Y-axis</b> = FTEs allocated.
            <b style="color:#cccccc;">Bubble size</b> = NeoLink data coverage.
            <b style="color:#3ecf8e;">Top-left</b> is the sweet spot —
            high internal effort where competition is low.
            <b style="color:#cf4f4f;">Top-right</b> is high effort in
            crowded spaces — worth scrutinizing.
        </div>
    </div>""", unsafe_allow_html=True)

    pressure_map = {"Low":1,"Medium":2,"High":3}
    coverage_map = {"Low":10,"Medium":22,"High":38}
    owner_colors = {
        "Internal":"#3ecf8e","J&J":"#3ea8cf",
        "BMS":"#d4a017","Halda":"#a855f7",
    }

    prog_df["_p"] = prog_df["Competitive Pressure"].map(pressure_map)
    prog_df["_s"] = prog_df["NeoLink Coverage"].map(coverage_map)

    fig5 = px.scatter(
        prog_df, x="_p", y="FTEs Allocated", size="_s",
        color="Internal vs Partner",
        hover_name="Program",
        hover_data={
            "Target Class":True,"Modality":True,"Stage":True,
            "Competitive Pressure":True,"NeoLink Coverage":True,
            "_p":False,"_s":False,
        },
        title="Program Opportunity vs. Effort",
        color_discrete_map=owner_colors,
        size_max=45,
    )
    fig5.update_layout(
        plot_bgcolor="#050505", paper_bgcolor="#050505",
        font_color="#555", title_font_color="#888",
        title_font_size=13, margin=dict(t=40,l=10,r=10,b=10),
        xaxis=dict(
            tickvals=[1,2,3],
            ticktext=["Low Competition","Medium Competition",
                      "High Competition"],
            gridcolor="#111", showline=False,
            title_font_color="#666", tickfont_color="#555",
        ),
        yaxis=dict(
            title="FTEs Allocated",
            gridcolor="#111", showline=False,
            title_font_color="#666", tickfont_color="#555",
        ),
        legend=dict(bgcolor="#050505",
                    bordercolor="#1a1a1a", borderwidth=1),
    )
    st.plotly_chart(fig5, use_container_width=True)

    st.markdown("<div class='section-label'>Strategic Flags</div>",
                unsafe_allow_html=True)

    flags = [
        {
            "color": "#cf4f4f", "icon": "⚠",
            "title": "High competitive pressure on PRX-001",
            "body": "PRX-001 faces direct competition from Monte Rosa and Kymera — both well-funded and clinically advanced. Neo-1's structural design advantage needs to be demonstrably faster or better to justify the internal resource load. Worth a leadership conversation about whether this target class is better positioned as a partner program than an internal one.",
        },
        {
            "color": "#3ecf8e", "icon": "↑",
            "title": "Immunology whitespace is underweighted",
            "body": "PRX-003 is our only immunology program with 4 FTEs. External data shows low competitive pressure in ProMod immunology. The BMS partnership provides a beachhead. The question for leadership: is the current underweighting a deliberate sequencing choice or an allocation gap that should be corrected?",
        },
        {
            "color": "#3ecf8e", "icon": "↑",
            "title": "RIPTAC space is wide open — press the advantage",
            "body": "The Halda programs are the only RIPTAC work in the portfolio and the clinical trial data shows almost no external competition. Neo-1's ternary complex prediction strength is uniquely suited to this modality. This is likely the highest-leverage area for Proxima to deepen internal investment alongside the Halda partnership.",
        },
        {
            "color": "#3ea8cf", "icon": "→",
            "title": "54% of FTE allocation is on partner programs",
            "body": "More than half of allocated effort is funding partner programs. This is appropriate and expected at seed stage — partners fund the work. But as Proxima scales toward Series A, the balance between platform-as-a-service and proprietary pipeline needs active management to preserve long-term equity value.",
        },
        {
            "color": "#d4a017", "icon": "⚠",
            "title": "Blueprint/Sanofi acquisition creates near-term uncertainty",
            "body": "Post-acquisition reprioritization is common and can quietly deprioritize in-flight collaborations without formal notice. The Q2 2026 Hit-to-Lead milestone in 60 days is the early warning signal — any delay or scope reduction should trigger a proactive partner conversation before it becomes a formal issue.",
        },
    ]

    for f in flags:
        st.markdown(f"""
        <div class="card" style="border-left:2px solid {f['color']};">
            <div style="display:flex; gap:14px; align-items:flex-start;">
                <div style="font-size:16px; color:{f['color']};
                            font-weight:700; margin-top:2px;">{f['icon']}</div>
                <div>
                    <div style="font-size:14px; font-weight:600;
                                color:#ffffff; margin-bottom:6px;">
                        {f['title']}
                    </div>
                    <div style="font-size:13px; color:#888;
                                line-height:1.8;">{f['body']}</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-label'>What I'd Build Next</div>",
                unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <div style="font-size:15px; font-weight:600; color:#ffffff;
                    margin-bottom:6px;">
            This is the foundation.
        </div>
        <div style="font-size:13px; color:#777; line-height:1.8;
                    margin-bottom:20px;">
            With access to internal systems and an understanding of how
            the team actually runs, here is the roadmap for what comes next.
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:32px;">
            <div>
                <div style="font-size:11px; color:#444;
                            text-transform:uppercase; letter-spacing:1.5px;
                            margin-bottom:12px; font-weight:600;">
                    PARTNERSHIP OPS
                </div>
                <div style="font-size:13px; color:#777; line-height:2.2;">
                    <span style="color:#555;">→</span>
                    Milestone alert system with Slack and email triggers<br>
                    <span style="color:#555;">→</span>
                    Data obligation tracker with delivery confirmations<br>
                    <span style="color:#555;">→</span>
                    JSC prep templates auto-populated from program data<br>
                    <span style="color:#555;">→</span>
                    Contract obligation parser from executed deal PDFs<br>
                    <span style="color:#555;">→</span>
                    Partner health scoring updated each quarter
                </div>
            </div>
            <div>
                <div style="font-size:11px; color:#444;
                            text-transform:uppercase; letter-spacing:1.5px;
                            margin-bottom:12px; font-weight:600;">
                    INTELLIGENCE AND PLANNING
                </div>
                <div style="font-size:13px; color:#777; line-height:2.2;">
                    <span style="color:#555;">→</span>
                    Auto-refreshing signals from PubMed and bioRxiv<br>
                    <span style="color:#555;">→</span>
                    Headcount planning tied to program stage gates<br>
                    <span style="color:#555;">→</span>
                    CRO and CMO vendor tracker for IND-readiness<br>
                    <span style="color:#555;">→</span>
                    Internal vs. partner decision scoring rubric<br>
                    <span style="color:#555;">→</span>
                    Board and investor reporting templates auto-generated
                </div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)