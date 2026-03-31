import streamlit as st
from data import fetch_clinical_trials, fetch_recent_trials
from synthesis import (
    synthesize_external_landscape,
    synthesize_partnership_portfolio,
    synthesize_resource_allocation,
)
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Proxima · Strategic Intelligence",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Google Font + Global Styles ────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
    /* ── Reset & Base ── */
    * { font-family: 'Inter', sans-serif !important; }
    .stApp {
        background-color: #000000;
        color: #e0e0e0;
    }
    section[data-testid="stSidebar"] { display: none; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container {
        padding: 2rem 3rem 4rem 3rem;
        max-width: 1400px;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: #0a0a0a;
        border: 1px solid #1a1a1a;
        border-radius: 10px;
        padding: 6px;
        gap: 4px;
        margin-bottom: 32px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #555;
        border-radius: 7px;
        padding: 10px 24px;
        font-size: 13px;
        font-weight: 500;
        border: none;
        transition: all 0.2s;
    }
    .stTabs [aria-selected="true"] {
        background: #141414;
        color: #ffffff;
        border: 1px solid #2a2a2a;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #aaa;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: #0a0a0a;
        color: #aaaaaa;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 13px;
        font-weight: 500;
        transition: all 0.2s;
        width: auto;
    }
    .stButton > button:hover {
        background: #141414;
        border-color: #444;
        color: #ffffff;
    }

    /* ── Inputs ── */
    .stSelectbox > div > div,
    .stTextInput > div > div > input {
        background: #0a0a0a !important;
        border: 1px solid #1e1e1e !important;
        color: #e0e0e0 !important;
        border-radius: 8px !important;
        font-size: 13px !important;
    }
    .stSelectbox label, .stTextInput label {
        color: #555 !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
    }

    /* ── Dataframe ── */
    .stDataFrame {
        border: 1px solid #1a1a1a !important;
        border-radius: 10px !important;
        overflow: hidden;
    }
    .stDataFrame thead th {
        background: #0d0d0d !important;
        color: #555 !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
        border-bottom: 1px solid #1a1a1a !important;
    }
    .stDataFrame tbody td {
        color: #ccc !important;
        font-size: 13px !important;
        border-color: #111 !important;
    }
    .stDataFrame tbody tr:hover td {
        background: #0d0d0d !important;
    }

    /* ── Spinner ── */
    .stSpinner > div { border-top-color: #3ea8cf !important; }

    /* ── Custom components ── */
    .proxima-card {
        background: #080808;
        border: 1px solid #1a1a1a;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 12px;
        transition: border-color 0.2s;
    }
    .proxima-card:hover { border-color: #2a2a2a; }

    .metric-card {
        background: #080808;
        border: 1px solid #1a1a1a;
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
        font-size: 12px;
        color: #444;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-weight: 500;
    }

    .section-label {
        font-size: 11px;
        font-weight: 600;
        color: #333;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin: 32px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid #111;
    }

    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    .badge-green  { background:#071a0f; color:#3ecf8e; border:1px solid #0d3320; }
    .badge-yellow { background:#1a1500; color:#d4a017; border:1px solid #332b00; }
    .badge-blue   { background:#051525; color:#3ea8cf; border:1px solid #0d2d45; }
    .badge-red    { background:#1a0505; color:#cf4f4f; border:1px solid #330d0d; }
    .badge-purple { background:#110515; color:#a855f7; border:1px solid #2a0d3a; }

    .insight-card {
        background: #050505;
        border-radius: 10px;
        padding: 20px 24px;
        margin-bottom: 10px;
        line-height: 1.8;
        font-size: 14px;
        color: #bbb;
    }

    .divider {
        border: none;
        border-top: 1px solid #111;
        margin: 32px 0;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
now = datetime.now().strftime("%B %d, %Y")
st.markdown(f"""
<div style="display:flex; justify-content:space-between;
            align-items:flex-end; padding: 8px 0 36px 0;
            border-bottom: 1px solid #111; margin-bottom: 32px;">
    <div>
        <div style="font-size:11px; color:#333; letter-spacing:2.5px;
                    text-transform:uppercase; margin-bottom:10px;
                    font-weight:500;">
            PROXIMA · INTERNAL · CONFIDENTIAL
        </div>
        <div style="font-size:32px; font-weight:700; color:#ffffff;
                    letter-spacing:-0.5px; line-height:1.1;">
            Strategic Intelligence
        </div>
        <div style="font-size:14px; color:#444; margin-top:8px;
                    font-weight:400;">
            External landscape &nbsp;·&nbsp; Partnership portfolio
            &nbsp;·&nbsp; Resource allocation
        </div>
    </div>
    <div style="text-align:right;">
        <div style="font-size:11px; color:#333; text-transform:uppercase;
                    letter-spacing:1px; margin-bottom:4px;">
            LAST REFRESHED
        </div>
        <div style="font-size:13px; color:#555; font-weight:500;">
            {now}
        </div>
        <div style="margin-top:10px;">
            <span class="badge badge-green">● Live data</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

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
    <div class="proxima-card" style="border-left: 2px solid #1e3a4a;">
        <div style="font-size:13px; color:#3ea8cf; font-weight:600;
                    text-transform:uppercase; letter-spacing:1px;
                    margin-bottom:8px;">
            EXTERNAL LANDSCAPE
        </div>
        <div style="font-size:15px; color:#ffffff; font-weight:500;
                    margin-bottom:6px;">
            What's moving in the ProMod space
        </div>
        <div style="font-size:13px; color:#555; line-height:1.7;">
            Live clinical trial data from ClinicalTrials.gov, mapped against
            the competitive landscape. Framed around the decisions Proxima
            needs to make — not just what exists, but what it means.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Load data ──────────────────────────────────────────────────────────────
    with st.spinner("Pulling live data from ClinicalTrials.gov..."):
        trials_df = fetch_clinical_trials()
        recent_df = fetch_recent_trials(days=365)

    # ── Metrics ────────────────────────────────────────────────────────────────
    st.markdown("<div class='section-label'>Overview</div>",
                unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    total_trials  = len(trials_df)  if not trials_df.empty  else 0
    recent_trials = len(recent_df)  if not recent_df.empty  else 0
    sponsors      = trials_df["Sponsor"].nunique()  if not trials_df.empty else 0
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

    # ── Trial tracker ──────────────────────────────────────────────────────────
    st.markdown("<div class='section-label'>Clinical Trial Tracker</div>",
                unsafe_allow_html=True)

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
            search = st.text_input("Search sponsor, indication, or title", "")

        filtered = trials_df.copy()
        if sel_mod   != "All modalities": filtered = filtered[filtered["Modality"] == sel_mod]
        if sel_phase != "All phases":     filtered = filtered[filtered["Phase"]    == sel_phase]
        if search:
            mask = (
                filtered["Sponsor"].str.contains(search, case=False, na=False) |
                filtered["Indication"].str.contains(search, case=False, na=False) |
                filtered["Title"].str.contains(search, case=False, na=False)
            )
            filtered = filtered[mask]

        st.markdown(f"""
        <div style="font-size:12px; color:#333; margin-bottom:10px;">
            Showing {len(filtered)} of {len(trials_df)} trials
        </div>""", unsafe_allow_html=True)

        display_cols = ["NCT ID","Title","Sponsor","Phase",
                        "Status","Modality","Indication","Start Date"]
        st.dataframe(filtered[display_cols],
                     use_container_width=True, height=380,
                     hide_index=True)

        # ── Charts ─────────────────────────────────────────────────────────────
        st.markdown("<div class='section-label'>Breakdown</div>",
                    unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        chart_layout = dict(
            plot_bgcolor="#050505", paper_bgcolor="#050505",
            font_color="#444", title_font_color="#aaa",
            title_font_size=13, margin=dict(t=40, l=10, r=10, b=10),
            xaxis=dict(gridcolor="#111", showline=False),
            yaxis=dict(gridcolor="#111", showline=False),
        )

        with c1:
            phase_counts = trials_df["Phase"].value_counts().reset_index()
            phase_counts.columns = ["Phase","Count"]
            fig1 = px.bar(phase_counts, x="Phase", y="Count",
                          title="Trials by Phase",
                          color="Count",
                          color_continuous_scale=["#0d2535","#3ea8cf"])
            fig1.update_layout(**chart_layout, showlegend=False,
                               coloraxis_showscale=False)
            fig1.update_traces(marker_line_width=0)
            st.plotly_chart(fig1, use_container_width=True)

        with c2:
            mod_counts = trials_df["Modality"].value_counts().reset_index()
            mod_counts.columns = ["Modality","Count"]
            fig2 = px.pie(mod_counts, names="Modality", values="Count",
                          title="Trials by Modality",
                          color_discrete_sequence=[
                              "#3ea8cf","#3ecf8e","#d4a017",
                              "#cf4f4f","#a855f7","#555"])
            fig2.update_layout(plot_bgcolor="#050505",
                               paper_bgcolor="#050505",
                               font_color="#444",
                               title_font_color="#aaa",
                               title_font_size=13,
                               margin=dict(t=40,l=10,r=10,b=10))
            fig2.update_traces(textfont_color="#ccc",
                               marker_line_color="#000",
                               marker_line_width=2)
            st.plotly_chart(fig2, use_container_width=True)

        # ── AI Synthesis ───────────────────────────────────────────────────────
        st.markdown("<div class='section-label'>AI Strategic Synthesis</div>",
                    unsafe_allow_html=True)
        st.markdown("""
        <div class="proxima-card">
            <div style="font-size:13px; color:#555; line-height:1.7;">
                Generate a live strategic synthesis of the external landscape —
                written from the perspective of a Proxima Strat/Ops team member,
                grounded in the current data.
            </div>
        </div>""", unsafe_allow_html=True)

        if st.button("Generate External Landscape Synthesis →",
                     key="syn1"):
            with st.spinner("Analyzing..."):
                insight = synthesize_external_landscape(trials_df)
            st.markdown(f"""
            <div class="proxima-card"
                 style="border-left:2px solid #3ea8cf; margin-top:12px;">
                <div style="font-size:10px; color:#3ea8cf; font-weight:700;
                            letter-spacing:2px; text-transform:uppercase;
                            margin-bottom:14px;">
                    AI SYNTHESIS · EXTERNAL LANDSCAPE
                </div>
                <div class="insight-card">
                    {insight.replace(chr(10), '<br><br>')}
                </div>
            </div>""", unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="proxima-card" style="color:#333; font-size:13px;">
            Could not load trial data. Check your internet connection.
        </div>""", unsafe_allow_html=True)

    # ── Competitive Landscape ──────────────────────────────────────────────────
    st.markdown("<div class='section-label'>Competitive Landscape</div>",
                unsafe_allow_html=True)

    competitors = [
        {
            "Company": "Arvinas",
            "Modality": "PROTAC",
            "Lead Indication": "ER+ Breast Cancer, Prostate Cancer",
            "Most Advanced": "Phase 3",
            "Funding": "Public (ARVN)",
            "Computational Platform": "Limited",
            "Proxima Relevance": "Most advanced PROTAC player globally. Phase 3 data will either validate the modality broadly or reveal execution limits. Not a direct platform competitor — wet-lab heavy, no meaningful computational moat.",
            "Threat Level": "Medium",
        },
        {
            "Company": "Kymera Therapeutics",
            "Modality": "PROTAC / Molecular Glue",
            "Lead Indication": "Immunology, Oncology",
            "Most Advanced": "Phase 2",
            "Funding": "Public (KYMR)",
            "Computational Platform": "Moderate",
            "Proxima Relevance": "Expanding into molecular glues and building computational capabilities. Closest public-company analog to Proxima's target space. Worth watching closely as they scale their platform.",
            "Threat Level": "High",
        },
        {
            "Company": "C4 Therapeutics",
            "Modality": "PROTAC / Molecular Glue",
            "Lead Indication": "Oncology",
            "Most Advanced": "Phase 1/2",
            "Funding": "Public (CCCC)",
            "Computational Platform": "Moderate",
            "Proxima Relevance": "TORPEDO platform for degrader design. Commercially challenged — potential cautionary signal on execution risk for platform-first biotechs without a strong data flywheel.",
            "Threat Level": "Medium",
        },
        {
            "Company": "Monte Rosa Therapeutics",
            "Modality": "Molecular Glue",
            "Lead Indication": "Oncology",
            "Most Advanced": "Phase 1",
            "Funding": "Public (GLUE)",
            "Computational Platform": "Strong",
            "Proxima Relevance": "QuEEN computational platform for glue discovery is the most direct analog to Neo-1 in the glue space. Key benchmark for Proxima's computational differentiation claims.",
            "Threat Level": "High",
        },
        {
            "Company": "Revolution Medicines",
            "Modality": "Molecular Glue / RAS Inhibitor",
            "Lead Indication": "RAS-driven Cancers",
            "Most Advanced": "Phase 3",
            "Funding": "Public (RVMD)",
            "Computational Platform": "Moderate",
            "Proxima Relevance": "Daraxonrasib is the leading clinical proof point for molecular glues. Phase 3 success would be a massive tailwind for the entire ProMod modality and directly benefits Proxima's BD narrative.",
            "Threat Level": "Medium",
        },
        {
            "Company": "Halda Therapeutics",
            "Modality": "RIPTAC",
            "Lead Indication": "Oncology",
            "Most Advanced": "Preclinical",
            "Funding": "Private",
            "Computational Platform": "Limited",
            "Proxima Relevance": "Active Proxima partner ($1B+ deal). Proxima is their entire computational backbone. Monitor for clinical progress — their success is directly tied to Neo-1's performance on ternary complexes.",
            "Threat Level": "Partner",
        },
        {
            "Company": "Nurix Therapeutics",
            "Modality": "Targeted Protein Degradation",
            "Lead Indication": "Oncology, Immunology",
            "Most Advanced": "Phase 2",
            "Funding": "Public (NRIX)",
            "Computational Platform": "Moderate",
            "Proxima Relevance": "DEL-based degrader discovery — different technical approach. Overlapping indication space but not a direct platform competitor.",
            "Threat Level": "Low",
        },
        {
            "Company": "Relay Therapeutics",
            "Modality": "Small Molecule (Conformational)",
            "Lead Indication": "Oncology",
            "Most Advanced": "Phase 2",
            "Funding": "Public (RLAY)",
            "Computational Platform": "Very Strong",
            "Proxima Relevance": "Not in ProMod space but sets the benchmark for AI-native biotech execution. What Proxima should aspire to in terms of platform credibility and partner trust.",
            "Threat Level": "Low",
        },
    ]

    comp_df = pd.DataFrame(competitors)

    cf1, cf2 = st.columns([1, 1])
    with cf1:
        threat_filter = st.selectbox("Relevance",
            ["All","High","Medium","Low","Partner"])
    with cf2:
        mod_filter = st.selectbox("Modality",
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
            "High": "High relevance", "Medium": "Medium relevance",
            "Low": "Low relevance",   "Partner": "Active partner",
        }
        phase_color = {
            "Phase 3": "badge-red", "Phase 2": "badge-yellow",
            "Phase 1/2": "badge-yellow", "Phase 1": "badge-blue",
            "Preclinical": "badge-blue",
        }.get(row["Most Advanced"], "badge-blue")

        st.markdown(f"""
        <div class="proxima-card">
            <div style="display:flex; justify-content:space-between;
                        align-items:flex-start; margin-bottom:12px;">
                <div>
                    <span style="font-size:16px; font-weight:700;
                                 color:#fff;">{row["Company"]}</span>
                    <span style="font-size:12px; color:#444;
                                 margin-left:10px;">{row["Modality"]}</span>
                </div>
                <div style="display:flex; gap:6px; flex-wrap:wrap;
                            justify-content:flex-end;">
                    <span class="badge {phase_color}">
                        {row["Most Advanced"]}
                    </span>
                    <span class="badge {badge_map[row['Threat Level']]}">
                        {label_map[row['Threat Level']]}
                    </span>
                </div>
            </div>
            <div style="font-size:13px; color:#666; line-height:1.7;
                        margin-bottom:14px;">
                {row["Proxima Relevance"]}
            </div>
            <div style="display:flex; gap:32px; flex-wrap:wrap;">
                <div>
                    <div style="font-size:10px; color:#333;
                                text-transform:uppercase;
                                letter-spacing:1px;">INDICATION</div>
                    <div style="font-size:13px; color:#888; margin-top:3px;">
                        {row["Lead Indication"]}
                    </div>
                </div>
                <div>
                    <div style="font-size:10px; color:#333;
                                text-transform:uppercase;
                                letter-spacing:1px;">FUNDING</div>
                    <div style="font-size:13px; color:#888; margin-top:3px;">
                        {row["Funding"]}
                    </div>
                </div>
                <div>
                    <div style="font-size:10px; color:#333;
                                text-transform:uppercase;
                                letter-spacing:1px;">COMP. PLATFORM</div>
                    <div style="font-size:13px; color:#888; margin-top:3px;">
                        {row["Computational Platform"]}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — PARTNERSHIP PORTFOLIO
# ══════════════════════════════════════════════════════════════════════════════
with tab2:

    st.markdown("""
    <div class="proxima-card" style="border-left:2px solid #1a3a1a;">
        <div style="font-size:13px; color:#3ecf8e; font-weight:600;
                    text-transform:uppercase; letter-spacing:1px;
                    margin-bottom:8px;">
            PARTNERSHIP PORTFOLIO
        </div>
        <div style="font-size:15px; color:#ffffff; font-weight:500;
                    margin-bottom:6px;">
            All active collaborations in one place
        </div>
        <div style="font-size:13px; color:#555; line-height:1.7;">
            Milestones, data obligations, and decision checkpoints — so
            nothing falls through the cracks. Seeded with publicly available
            information, structured for real data entry.
        </div>
    </div>
    """, unsafe_allow_html=True)

    partnerships = [
        {
            "Partner": "Johnson & Johnson",
            "Focus": "Molecular Glues / ProMod",
            "Indication": "Oncology",
            "Status": "Active",
            "Deal Value": "$1B+ potential",
            "Upfront": "Undisclosed",
            "Programs": 3,
            "Most Advanced": "Preclinical &#8594; IND",
            "Next Milestone": "IND Filing",
            "Milestone Date": "Q3 2026",
            "Days Until": 120,
            "Data Obligations": "Quarterly structural data packages via NeoLink",
            "Joint Steering": "Bi-monthly",
            "Notes": "First program on track for IND in 2026. This is Proxima's most milestone-critical near-term event — triggers first significant milestone payment and validates the platform commercially.",
            "Risk": "Medium",
        },
        {
            "Partner": "Bristol Myers Squibb",
            "Focus": "Targeted Protein Degradation",
            "Indication": "Oncology, Immunology",
            "Status": "Active",
            "Deal Value": "Undisclosed",
            "Upfront": "Undisclosed",
            "Programs": 2,
            "Most Advanced": "Lead Optimization",
            "Next Milestone": "Candidate Nomination",
            "Milestone Date": "Q4 2026",
            "Days Until": 210,
            "Data Obligations": "Monthly Neo-1 generation reports",
            "Joint Steering": "Quarterly",
            "Notes": "BMS has deep PROTAC expertise internally. Partnership likely focused on NeoLink structural data advantage for novel targets where BMS lacks structural coverage.",
            "Risk": "Low",
        },
        {
            "Partner": "Blueprint Medicines (Sanofi)",
            "Focus": "ProMod — Oncology Targets",
            "Indication": "Oncology",
            "Status": "Active",
            "Deal Value": "Undisclosed",
            "Upfront": "Undisclosed",
            "Programs": 2,
            "Most Advanced": "Hit Discovery",
            "Next Milestone": "Hit-to-Lead Completion",
            "Milestone Date": "Q2 2026",
            "Days Until": 60,
            "Data Obligations": "Target structural packages on demand",
            "Joint Steering": "Monthly",
            "Notes": "Blueprint acquired by Sanofi — monitor for strategic reprioritization post-acquisition. Q2 milestone is the near-term test of partnership health. Second expansion of collaboration is a positive signal.",
            "Risk": "Medium",
        },
        {
            "Partner": "Halda Therapeutics",
            "Focus": "RIPTAC Discovery",
            "Indication": "Oncology",
            "Status": "Active",
            "Deal Value": "$1B+ potential",
            "Upfront": "Undisclosed",
            "Programs": 4,
            "Most Advanced": "Hit Discovery",
            "Next Milestone": "Lead Series Identification",
            "Milestone Date": "Q3 2026",
            "Days Until": 150,
            "Data Obligations": "Neo-1 RIPTAC design packages, NeoLink ternary complex data",
            "Joint Steering": "Monthly",
            "Notes": "Deepest technical integration. Proxima is the computational backbone for Halda's entire platform. Neo-1's ternary complex strength is uniquely suited to RIPTAC design. Highest strategic value partnership.",
            "Risk": "Low",
        },
        {
            "Partner": "Boehringer Ingelheim",
            "Focus": "ProMod — Undisclosed Targets",
            "Indication": "Undisclosed",
            "Status": "Active",
            "Deal Value": "Undisclosed",
            "Upfront": "Undisclosed",
            "Programs": 1,
            "Most Advanced": "Target Identification",
            "Next Milestone": "Target Validation Package",
            "Milestone Date": "Q2 2026",
            "Days Until": 45,
            "Data Obligations": "NeoLink proteome scan for target class",
            "Joint Steering": "Quarterly",
            "Notes": "Earliest stage and smallest program. BI has strong internal small molecule capabilities — partnership likely scoping NeoLink for novel target identification rather than computational design.",
            "Risk": "Low",
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
        ["Active partners","Programs in portfolio",
         "Milestones < 90 days","Elevated risk items"],
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

    sorted_partners = sorted(partnerships, key=lambda x: x["Days Until"])
    for p in sorted_partners:
        d = p["Days Until"]
        color  = "#cf4f4f" if d <= 60 else "#d4a017" if d <= 120 else "#3ea8cf"
        label  = "Urgent"  if d <= 60 else "Soon"    if d <= 120 else "Upcoming"
        b_cls  = "badge-red" if d <= 60 else "badge-yellow" if d <= 120 else "badge-blue"
        st.markdown(f"""
        <div class="proxima-card"
             style="border-left:2px solid {color}; padding:16px 20px;">
            <div style="display:flex; justify-content:space-between;
                        align-items:center;">
                <div style="display:flex; align-items:center; gap:12px;">
                    <span class="badge {b_cls}">{label}</span>
                    <span style="font-size:14px; font-weight:600;
                                 color:#fff;">{p["Partner"]}</span>
                    <span style="font-size:13px; color:#444;">
                        &#8594; {p["Next Milestone"]}
                    </span>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:13px; color:{color};
                                font-weight:600;">{p["Milestone Date"]}</div>
                    <div style="font-size:11px; color:#333;">
                        ~{d} days
                    </div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    # ── Partnership cards ──────────────────────────────────────────────────────
    st.markdown("<div class='section-label'>Partnership Detail</div>",
                unsafe_allow_html=True)

    for p in partnerships:
        risk_cls   = {"High":"badge-red","Medium":"badge-yellow",
                      "Low":"badge-green"}.get(p["Risk"],"badge-blue")
        risk_label = {"High":"High risk","Medium":"Monitor",
                      "Low":"On track"}.get(p["Risk"],"")
        d = p["Days Until"]
        ms_color = "#cf4f4f" if d<=60 else "#d4a017" if d<=120 else "#3ea8cf"

        st.markdown(f"""
        <div class="proxima-card">
            <div style="display:flex; justify-content:space-between;
                        align-items:flex-start; margin-bottom:16px;">
                <div>
                    <div style="font-size:18px; font-weight:700;
                                color:#fff; margin-bottom:3px;">
                        {p["Partner"]}
                    </div>
                    <div style="font-size:12px; color:#444;">
                        {p["Focus"]}
                    </div>
                </div>
                <div style="display:flex; gap:6px;">
                    <span class="badge badge-green">Active</span>
                    <span class="badge {risk_cls}">{risk_label}</span>
                </div>
            </div>

            <div style="display:grid; grid-template-columns:repeat(4,1fr);
                        gap:16px; margin-bottom:16px;">
                <div>
                    <div style="font-size:10px; color:#333;
                                text-transform:uppercase;
                                letter-spacing:1px;">INDICATION</div>
                    <div style="font-size:13px; color:#888; margin-top:3px;">
                        {p["Indication"]}
                    </div>
                </div>
                <div>
                    <div style="font-size:10px; color:#333;
                                text-transform:uppercase;
                                letter-spacing:1px;">DEAL VALUE</div>
                    <div style="font-size:13px; color:#888; margin-top:3px;">
                        {p["Deal Value"]}
                    </div>
                </div>
                <div>
                    <div style="font-size:10px; color:#333;
                                text-transform:uppercase;
                                letter-spacing:1px;">PROGRAMS</div>
                    <div style="font-size:13px; color:#888; margin-top:3px;">
                        {p["Programs"]} active
                    </div>
                </div>
                <div>
                    <div style="font-size:10px; color:#333;
                                text-transform:uppercase;
                                letter-spacing:1px;">MOST ADVANCED</div>
                    <div style="font-size:13px; color:#888; margin-top:3px;">
                        {p["Most Advanced"]}
                    </div>
                </div>
            </div>

            <div style="background:#040404; border:1px solid #111;
                        border-radius:8px; padding:14px 18px;
                        margin-bottom:14px;">
                <div style="display:flex; justify-content:space-between;
                            align-items:center;">
                    <div>
                        <div style="font-size:10px; color:#333;
                                    text-transform:uppercase;
                                    letter-spacing:1px;">NEXT MILESTONE</div>
                        <div style="font-size:15px; color:#fff;
                                    font-weight:600; margin-top:4px;">
                            {p["Next Milestone"]}
                        </div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:14px; color:{ms_color};
                                    font-weight:600;">
                            {p["Milestone Date"]}
                        </div>
                        <div style="font-size:11px; color:#333;
                                    margin-top:2px;">
                            ~{d} days away
                        </div>
                    </div>
                </div>
            </div>

            <div style="display:grid; grid-template-columns:1fr 1fr;
                        gap:16px; margin-bottom:14px;">
                <div>
                    <div style="font-size:10px; color:#333;
                                text-transform:uppercase;
                                letter-spacing:1px;">DATA OBLIGATIONS</div>
                    <div style="font-size:13px; color:#666; margin-top:3px;">
                        {p["Data Obligations"]}
                    </div>
                </div>
                <div>
                    <div style="font-size:10px; color:#333;
                                text-transform:uppercase;
                                letter-spacing:1px;">JOINT STEERING</div>
                    <div style="font-size:13px; color:#666; margin-top:3px;">
                        {p["Joint Steering"]}
                    </div>
                </div>
            </div>

            <div style="font-size:13px; color:#555; line-height:1.7;
                        border-top:1px solid #111; padding-top:12px;">
                {p["Notes"]}
            </div>
        </div>""", unsafe_allow_html=True)

    # ── AI Synthesis ───────────────────────────────────────────────────────────
    st.markdown("<div class='section-label'>AI Strategic Synthesis</div>",
                unsafe_allow_html=True)
    st.markdown("""
    <div class="proxima-card">
        <div style="font-size:13px; color:#555; line-height:1.7;">
            Generate a live strategic assessment of the partnership portfolio —
            risk concentration, near-term priorities, and what deserves
            a leadership conversation right now.
        </div>
    </div>""", unsafe_allow_html=True)

    if st.button("Generate Partnership Portfolio Synthesis →", key="syn2"):
        with st.spinner("Analyzing..."):
            insight2 = synthesize_partnership_portfolio(partnerships)
        st.markdown(f"""
        <div class="proxima-card"
             style="border-left:2px solid #3ecf8e; margin-top:12px;">
            <div style="font-size:10px; color:#3ecf8e; font-weight:700;
                        letter-spacing:2px; text-transform:uppercase;
                        margin-bottom:14px;">
                AI SYNTHESIS · PARTNERSHIP PORTFOLIO
            </div>
            <div class="insight-card">
                {insight2.replace(chr(10), '<br><br>')}
            </div>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — RESOURCE ALLOCATION
# ══════════════════════════════════════════════════════════════════════════════
with tab3:

    st.markdown("""
    <div class="proxima-card" style="border-left:2px solid #2a1a00;">
        <div style="font-size:13px; color:#d4a017; font-weight:600;
                    text-transform:uppercase; letter-spacing:1px;
                    margin-bottom:8px;">
            RESOURCE ALLOCATION
        </div>
        <div style="font-size:15px; color:#ffffff; font-weight:500;
                    margin-bottom:6px;">
            Where is effort going versus where is the opportunity?
        </div>
        <div style="font-size:13px; color:#555; line-height:1.7;">
            Internal programs and partner programs mapped against competitive
            activity. Surfaces the questions leadership needs to answer about
            focus, hiring, and portfolio balance.
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
            "Notes": "Most advanced internal program. Direct overlap with Monte Rosa and Kymera. Neo-1 glue design is the key differentiator — needs to be demonstrably faster or better to justify.",
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
            "Notes": "Strong NeoLink structural data advantage. BRD4 space is crowded but novel BRD targets remain accessible with our proteome coverage.",
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
            "Notes": "Immunology whitespace. Limited competition. Our only immunology program — underdeveloped relative to the opportunity size.",
        },
        {
            "Program": "JNJ-PRX-01",
            "Target Class": "Undisclosed",
            "Modality": "ProMod",
            "Indication": "Oncology",
            "Stage": "Preclinical &#8594; IND",
            "Internal vs Partner": "J&J",
            "NeoLink Coverage": "High",
            "Competitive Pressure": "Medium",
            "Strategic Fit": "Core",
            "FTEs Allocated": 5,
            "Notes": "First program approaching IND. Milestone-critical. J&J owns clinical development from IND onward — our job is to get them there on time.",
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
            "Notes": "Second J&J program. Earlier stage. Strong NeoLink coverage provides structural advantage on this target class.",
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
            "Notes": "Proxima's first meaningful immunology exposure via a partner program. Important signal for portfolio diversification beyond oncology.",
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
            "Notes": "Lead RIPTAC program. Neo-1 ternary complex strength is uniquely suited here. Minimal external competition — this is where we should be pressing our advantage.",
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
            "Notes": "Earlier stage RIPTAC program. NeoLink proteome scan ongoing for target identification.",
        },
    ]

    prog_df = pd.DataFrame(internal_programs)

    # ── Portfolio metrics ──────────────────────────────────────────────────────
    st.markdown("<div class='section-label'>Portfolio Overview</div>",
                unsafe_allow_html=True)

    rm1, rm2, rm3, rm4 = st.columns(4)
    total_p2    = len(prog_df)
    internal_n  = len(prog_df[prog_df["Internal vs Partner"] == "Internal"])
    partner_n   = total_p2 - internal_n
    total_ftes  = prog_df["FTEs Allocated"].sum()

    for col, num, label in zip(
        [rm1, rm2, rm3, rm4],
        [total_p2, internal_n, partner_n, total_ftes],
        ["Total programs","Internal","Partner","Total FTEs allocated"]
    ):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">{num}</div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    # ── Charts ─────────────────────────────────────────────────────────────────
    st.markdown("<div class='section-label'>Effort Distribution</div>",
                unsafe_allow_html=True)

    ac1, ac2 = st.columns(2)
    chart_layout2 = dict(
        plot_bgcolor="#050505", paper_bgcolor="#050505",
        font_color="#444", title_font_color="#aaa",
        title_font_size=13, margin=dict(t=40,l=10,r=10,b=10),
        xaxis=dict(gridcolor="#111", showline=False),
        yaxis=dict(gridcolor="#111", showline=False),
    )

    with ac1:
        fte_mod = prog_df.groupby("Modality")["FTEs Allocated"].sum().reset_index()
        fig3 = px.bar(fte_mod, x="Modality", y="FTEs Allocated",
                      title="FTEs by Modality",
                      color="FTEs Allocated",
                      color_continuous_scale=["#1a1a00","#d4a017"])
        fig3.update_layout(**chart_layout2, showlegend=False,
                           coloraxis_showscale=False)
        fig3.update_traces(marker_line_width=0)
        st.plotly_chart(fig3, use_container_width=True)

    with ac2:
        fte_own = prog_df.groupby("Internal vs Partner")["FTEs Allocated"].sum().reset_index()
        fig4 = px.pie(fte_own, names="Internal vs Partner",
                      values="FTEs Allocated",
                      title="FTE Split: Internal vs Partner",
                      color_discrete_sequence=[
                          "#3ecf8e","#3ea8cf","#d4a017","#cf4f4f","#a855f7"])
        fig4.update_layout(plot_bgcolor="#050505", paper_bgcolor="#050505",
                           font_color="#444", title_font_color="#aaa",
                           title_font_size=13,
                           margin=dict(t=40,l=10,r=10,b=10))
        fig4.update_traces(textfont_color="#ccc",
                           marker_line_color="#000",
                           marker_line_width=2)
        st.plotly_chart(fig4, use_container_width=True)

    # ── Bubble chart ───────────────────────────────────────────────────────────
    st.markdown("<div class='section-label'>Opportunity vs. Effort Matrix</div>",
                unsafe_allow_html=True)

    st.markdown("""
    <div class="proxima-card" style="margin-bottom:16px;">
        <div style="font-size:13px; color:#555; line-height:1.7;">
            <b style="color:#aaa;">X-axis</b> = competitive pressure externally.
            <b style="color:#aaa;">Y-axis</b> = FTEs allocated internally.
            <b style="color:#aaa;">Bubble size</b> = NeoLink data coverage.
            Programs in the <b style="color:#3ecf8e;">top-left</b> are high
            effort in low-competition spaces — the sweet spot.
            Programs in the <b style="color:#cf4f4f;">top-right</b> are high
            effort in crowded spaces — worth scrutinizing.
        </div>
    </div>""", unsafe_allow_html=True)

    pressure_map = {"Low":1,"Medium":2,"High":3}
    coverage_map = {"Low":10,"Medium":22,"High":38}
    owner_colors = {
        "Internal":"#3ecf8e","J&J":"#3ea8cf",
        "BMS":"#d4a017","Halda":"#a855f7","Blueprint":"#cf4f4f",
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
        font_color="#444", title_font_color="#aaa", title_font_size=13,
        margin=dict(t=40,l=10,r=10,b=10),
        xaxis=dict(
            tickvals=[1,2,3],
            ticktext=["Low Competition","Medium Competition","High Competition"],
            gridcolor="#111", showline=False,
        ),
        yaxis=dict(title="FTEs Allocated", gridcolor="#111", showline=False),
        legend=dict(bgcolor="#050505", bordercolor="#1a1a1a", borderwidth=1),
    )
    st.plotly_chart(fig5, use_container_width=True)

    # ── Strategic flags ────────────────────────────────────────────────────────
    st.markdown("<div class='section-label'>Strategic Flags</div>",
                unsafe_allow_html=True)

    flags = [
        {
            "color": "#cf4f4f", "icon": "⚠",
            "title": "High competitive pressure on PRX-001",
            "body": "PRX-001 faces direct competition from Monte Rosa and Kymera — both well-funded and clinically advanced. Neo-1's structural design advantage needs to be the differentiator. Worth reviewing whether this target class is better positioned as a partner program than an internal one.",
        },
        {
            "color": "#3ecf8e", "icon": "↑",
            "title": "Immunology whitespace is underweighted",
            "body": "PRX-003 is our only immunology program with 4 FTEs. External data shows low competitive pressure in ProMod immunology. BMS partnership provides a beachhead. The question for leadership: is this a deliberate choice or a resource allocation gap?",
        },
        {
            "color": "#3ecf8e", "icon": "↑",
            "title": "RIPTAC space is wide open — press the advantage",
            "body": "Halda programs are the only RIPTAC work in the portfolio and clinical trial data shows minimal external competition. Neo-1's ternary complex prediction strength is uniquely suited here. This is likely the highest-leverage area for Proxima to deepen internal investment alongside the Halda partnership.",
        },
        {
            "color": "#3ea8cf", "icon": "→",
            "title": "Partner programs represent 54% of FTE allocation",
            "body": "More than half of allocated effort is on partner programs. This is appropriate at seed stage — partners fund the work. But as Proxima scales toward Series A, the balance between platform-as-a-service and proprietary pipeline needs active management to preserve long-term equity value.",
        },
        {
            "color": "#d4a017", "icon": "⚠",
            "title": "Blueprint/Sanofi acquisition creates near-term uncertainty",
            "body": "Post-acquisition strategic reprioritization is common and can delay or deprioritize in-flight collaborations. The Q2 2026 milestone should be closely monitored — any delay may signal reduced partner commitment and should trigger a proactive conversation.",
        },
    ]

    for f in flags:
        st.markdown(f"""
        <div class="proxima-card" style="border-left:2px solid {f['color']};">
            <div style="display:flex; gap:14px; align-items:flex-start;">
                <div style="font-size:16px; color:{f['color']};
                            font-weight:700; margin-top:1px;">
                    {f['icon']}
                </div>
                <div>
                    <div style="font-size:14px; font-weight:600; color:#fff;
                                margin-bottom:6px;">{f['title']}</div>
                    <div style="font-size:13px; color:#555;
                                line-height:1.7;">{f['body']}</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    # ── Program table ──────────────────────────────────────────────────────────
    st.markdown("<div class='section-label'>Full Program List</div>",
                unsafe_allow_html=True)

    display_prog = prog_df[[
        "Program","Modality","Indication","Stage",
        "Internal vs Partner","Competitive Pressure",
        "NeoLink Coverage","FTEs Allocated"
    ]].copy()
    st.dataframe(display_prog, use_container_width=True, hide_index=True)

    # ── AI Synthesis ───────────────────────────────────────────────────────────
    st.markdown("<div class='section-label'>AI Strategic Synthesis</div>",
                unsafe_allow_html=True)
    st.markdown("""
    <div class="proxima-card">
        <div style="font-size:13px; color:#555; line-height:1.7;">
            Generate a live strategic assessment of resource allocation —
            whether effort is going where the opportunity is, and what
            to bring to leadership.
        </div>
    </div>""", unsafe_allow_html=True)

    if st.button("Generate Resource Allocation Synthesis →", key="syn3"):
        with st.spinner("Analyzing..."):
            insight3 = synthesize_resource_allocation(internal_programs)
        st.markdown(f"""
        <div class="proxima-card"
             style="border-left:2px solid #d4a017; margin-top:12px;">
            <div style="font-size:10px; color:#d4a017; font-weight:700;
                        letter-spacing:2px; text-transform:uppercase;
                        margin-bottom:14px;">
                AI SYNTHESIS · RESOURCE ALLOCATION
            </div>
            <div class="insight-card">
                {insight3.replace(chr(10), '<br><br>')}
            </div>
        </div>""", unsafe_allow_html=True)

    # ── What I'd build next ────────────────────────────────────────────────────
    st.markdown("<div class='section-label'>What I'd Build Next</div>",
                unsafe_allow_html=True)

    st.markdown("""
    <div class="proxima-card">
        <div style="font-size:14px; font-weight:600; color:#fff;
                    margin-bottom:16px; line-height:1.5;">
            This tool is the foundation. With access to internal systems
            and an understanding of how the team actually runs,
            here's the roadmap.
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:24px;">
            <div>
                <div style="font-size:10px; color:#333; text-transform:uppercase;
                            letter-spacing:1.5px; margin-bottom:12px;
                            font-weight:600;">
                    PARTNERSHIP OPS
                </div>
                <div style="font-size:13px; color:#555; line-height:2;">
                    → Milestone alert system with Slack / email triggers<br>
                    → Data obligation tracker with delivery confirmations<br>
                    → JSC prep templates auto-populated from program data<br>
                    → Contract obligation parser from deal PDFs<br>
                    → Partner health scoring updated quarterly
                </div>
            </div>
            <div>
                <div style="font-size:10px; color:#333; text-transform:uppercase;
                            letter-spacing:1.5px; margin-bottom:12px;
                            font-weight:600;">
                    INTELLIGENCE & PLANNING
                </div>
                <div style="font-size:13px; color:#555; line-height:2;">
                    → Auto-refreshing signals from PubMed + bioRxiv<br>
                    → Headcount planning tied to program stage gates<br>
                    → CRO / CMO vendor tracker for IND-readiness<br>
                    → Internal vs. partner decision scoring rubric<br>
                    → Board reporting templates auto-generated
                </div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)