# ══════════════════════════════════════════════════════════════════════════════
# PROXIMA STRATEGIC INTELLIGENCE — CONFIGURATION
# Edit this file to update all data without touching app logic
# When you have access to internal systems, replace illustrative values here
# ══════════════════════════════════════════════════════════════════════════════

from datetime import date


def _days(year, month, day):
    """Calculate days from today to a target date. Returns 0 if past."""
    return max(0, (date(year, month, day) - date.today()).days)


# ── Whitespace scorecard target classes ───────────────────────────────────────
# Competitor counts are manually maintained — update as landscape shifts
# NeoLink Coverage: "High" / "Medium" / "Low"
# Proxima Program / Partner: use "None" if not applicable

WHITESPACE_TARGETS = [
    {
        "Target Class":    "E3 Ligase / Molecular Glue",
        "Modality":        "Molecular Glue",
        "Competitors":     4,
        "Proxima Program": "PRX-001 (Lead Opt)",
        "Proxima Partner": "J&J",
        "NeoLink Coverage":"High",
        "Indication":      "Oncology",
        "Whitespace Notes":"Crowded in oncology. Immunology and CNS applications remain largely unexplored. Neo-1 glue design speed is the key differentiator against Monte Rosa and Kymera.",
    },
    {
        "Target Class":    "BRD / Transcription Factor",
        "Modality":        "PROTAC",
        "Competitors":     3,
        "Proxima Program": "PRX-002 (Hit Discovery)",
        "Proxima Partner": "BMS",
        "NeoLink Coverage":"High",
        "Indication":      "Oncology",
        "Whitespace Notes":"BRD4 is crowded but novel BRD family members remain accessible via NeoLink proteome coverage. Strong structural data advantage where competitors lack coverage.",
    },
    {
        "Target Class":    "Kinase / Scaffolding Protein",
        "Modality":        "Molecular Glue",
        "Competitors":     1,
        "Proxima Program": "PRX-003 (Target Validation)",
        "Proxima Partner": "None",
        "NeoLink Coverage":"Medium",
        "Indication":      "Immunology",
        "Whitespace Notes":"Significant whitespace. Low competition. Only internal immunology program — underdeveloped relative to opportunity size.",
    },
    {
        "Target Class":    "RIPTAC Targets",
        "Modality":        "RIPTAC",
        "Competitors":     1,
        "Proxima Program": "HALDA-PRX-01/02",
        "Proxima Partner": "Halda",
        "NeoLink Coverage":"High",
        "Indication":      "Oncology",
        "Whitespace Notes":"Wide open. Minimal competition. Neo-1 ternary complex strength is uniquely suited. First mover advantage available if Halda programs accelerate.",
    },
    {
        "Target Class":    "Immune Modulators",
        "Modality":        "PROTAC",
        "Competitors":     2,
        "Proxima Program": "BMS-PRX-01",
        "Proxima Partner": "BMS",
        "NeoLink Coverage":"Medium",
        "Indication":      "Immunology",
        "Whitespace Notes":"Emerging area. BMS partnership provides beachhead. Room for additional partners in autoimmune and inflammatory indications.",
    },
    {
        "Target Class":    "CNS Targets",
        "Modality":        "Molecular Glue / PROTAC",
        "Competitors":     0,
        "Proxima Program": "None",
        "Proxima Partner": "None",
        "NeoLink Coverage":"Medium",
        "Indication":      "Neurodegeneration",
        "Whitespace Notes":"Significant unmet need. Almost no ProMod competition. High-value partnership opportunity with no current Proxima presence.",
    },
    {
        "Target Class":    "Cardiovascular Targets",
        "Modality":        "PROTAC",
        "Competitors":     1,
        "Proxima Program": "None",
        "Proxima Partner": "None",
        "NeoLink Coverage":"Medium",
        "Indication":      "Cardiovascular",
        "Whitespace Notes":"Underexplored. Large unmet need. Potential new partnership vertical with no current Proxima presence.",
    },
    {
        "Target Class":    "Viral / Infectious Disease",
        "Modality":        "Molecular Glue",
        "Competitors":     0,
        "Proxima Program": "None",
        "Proxima Partner": "None",
        "NeoLink Coverage":"Low",
        "Indication":      "Infectious Disease",
        "Whitespace Notes":"Very early. Limited NeoLink coverage. Low near-term priority but worth monitoring as platform matures.",
    },
]


# ── Competitor landscape ───────────────────────────────────────────────────────
# Update as competitive positions shift
# Threat Level: "High" / "Medium" / "Low" / "Partner"
# Computational Platform: "Very Strong" / "Strong" / "Moderate" / "Limited"

COMPETITORS = [
    {
        "Company": "Arvinas",
        "Modality": "PROTAC",
        "Lead Indication": "ER+ Breast Cancer, Prostate Cancer",
        "Most Advanced": "Phase 3",
        "Funding": "Public (ARVN)",
        "Computational Platform": "Limited",
        "Proxima Relevance": "Most advanced PROTAC player globally. Phase 3 data will validate or stress-test the modality broadly. Not a direct platform competitor — wet-lab heavy with no meaningful computational moat.",
        "Threat Level": "Medium",
    },
    {
        "Company": "Kymera Therapeutics",
        "Modality": "PROTAC / Molecular Glue",
        "Lead Indication": "Immunology, Oncology",
        "Most Advanced": "Phase 2",
        "Funding": "Public (KYMR)",
        "Computational Platform": "Moderate",
        "Proxima Relevance": "Expanding into molecular glues and building computational capabilities. Closest public-company analog. If their platform matures it narrows Proxima's differentiation window.",
        "Threat Level": "High",
    },
    {
        "Company": "Monte Rosa Therapeutics",
        "Modality": "Molecular Glue",
        "Lead Indication": "Oncology",
        "Most Advanced": "Phase 1",
        "Funding": "Public (GLUE)",
        "Computational Platform": "Strong",
        "Proxima Relevance": "QuEEN platform is the most direct analog to Neo-1 in the glue space. Key benchmark for Proxima's differentiation claims — Neo-1 needs to demonstrably outperform QuEEN on ternary complex design.",
        "Threat Level": "High",
    },
    {
        "Company": "Revolution Medicines",
        "Modality": "Molecular Glue / RAS Inhibitor",
        "Lead Indication": "RAS-driven Cancers",
        "Most Advanced": "Phase 3",
        "Funding": "Public (RVMD)",
        "Computational Platform": "Moderate",
        "Proxima Relevance": "Daraxonrasib Phase 3 success is a rising tide — validates the entire modality and strengthens Proxima's partnership pitch to pharma.",
        "Threat Level": "Medium",
    },
    {
        "Company": "C4 Therapeutics",
        "Modality": "PROTAC / Molecular Glue",
        "Lead Indication": "Oncology",
        "Most Advanced": "Phase 1/2",
        "Funding": "Public (CCCC)",
        "Computational Platform": "Moderate",
        "Proxima Relevance": "Commercially challenged despite a credible platform — cautionary signal that platform credibility alone doesn't translate without a strong data flywheel.",
        "Threat Level": "Medium",
    },
    {
        "Company": "Halda Therapeutics",
        "Modality": "RIPTAC",
        "Lead Indication": "Oncology",
        "Most Advanced": "Preclinical",
        "Funding": "Private",
        "Computational Platform": "Limited",
        "Proxima Relevance": "Active Proxima partner ($1B+ deal). Proxima is their entire computational backbone — Neo-1's performance directly determines Halda's clinical trajectory. Monitor closely.",
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
        "Proxima Relevance": "Gold standard for AI-native biotech execution. Not in ProMod space but sets the benchmark Proxima should aspire to in platform credibility.",
        "Threat Level": "Low",
    },
]


# ── Partnerships ───────────────────────────────────────────────────────────────
# Confirmed = sourced from public announcements (shown in green)
# Days Until calculated dynamically from target date each page load
# Risk: "High" / "Medium" / "Low"
# Replace estimated (~) fields with actuals once you have access

PARTNERSHIPS = [
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
        "Days Until": _days(2026, 9, 30),
        "Data Obligations": "Quarterly structural data packages via NeoLink",
        "Joint Steering": "Bi-monthly",
        "Notes": "J&J publicly confirmed first program on track to enter clinical trials in 2026. Most milestone-critical near-term event — triggers first significant milestone payment and validates the platform commercially.",
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
        "Days Until": _days(2026, 12, 31),
        "Data Obligations": "~Monthly Neo-1 generation reports",
        "Joint Steering": "~Quarterly",
        "Notes": "BMS has deep internal PROTAC expertise — partnership likely anchored on NeoLink structural data for novel targets. Lowest operational urgency in the portfolio right now. Milestone timing estimated.",
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
        "Days Until": _days(2026, 6, 30),
        "Data Obligations": "~Target structural packages on demand",
        "Joint Steering": "~Monthly",
        "Notes": "Blueprint acquired by Sanofi — post-acquisition reprioritization is common. Q2 milestone is the early warning signal. Any delay should trigger a proactive conversation. Milestone timing estimated.",
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
        "Days Until": _days(2026, 9, 30),
        "Data Obligations": "~Neo-1 RIPTAC design packages, NeoLink ternary complex data",
        "Joint Steering": "~Monthly",
        "Notes": "Deepest technical integration. $1B+ confirmed August 2025. Proxima is Halda's entire computational backbone. Highest strategic value partnership. Program stage and timing estimated.",
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
        "Days Until": _days(2026, 6, 30),
        "Data Obligations": "~NeoLink proteome scan for target class",
        "Joint Steering": "~Quarterly",
        "Notes": "Most urgent near-term deliverable. Partnership confirmed — all program details and timing estimated. BI likely scoping NeoLink for target identification rather than computational design.",
        "Risk": "Low",
        "Confirmed": False,
    },
]


# ── Internal programs ──────────────────────────────────────────────────────────
# All fields are illustrative — replace with actuals once you have access
# Internal vs Partner: "Internal" / partner name (e.g. "J&J", "BMS", "Halda")
# NeoLink Coverage: "High" / "Medium" / "Low"
# Competitive Pressure: "High" / "Medium" / "Low"

INTERNAL_PROGRAMS = [
    {
        "Program": "PRX-001",
        "Target Class": "E3 Ligase / Substrate",
        "Modality": "Molecular Glue",
        "Indication": "Oncology",
        "Stage": "Lead Optimization",
        "Internal vs Partner": "Internal",
        "NeoLink Coverage": "High",
        "Competitive Pressure": "High",
        "FTEs Allocated": 8,
        "Notes": "Most advanced internal program. Direct overlap with Monte Rosa and Kymera. Worth evaluating whether better positioned as a partner program.",
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
        "FTEs Allocated": 6,
        "Notes": "Strong NeoLink structural data advantage. Novel BRD family members accessible with our proteome coverage.",
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
        "FTEs Allocated": 4,
        "Notes": "Immunology whitespace. Only internal immunology program — underweighted relative to opportunity size.",
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
        "FTEs Allocated": 5,
        "Notes": "First program approaching IND. Most time-sensitive partner deliverable. J&J owns clinical development from IND onward.",
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
        "FTEs Allocated": 4,
        "Notes": "Proxima's first meaningful immunology exposure via partner program. Important for portfolio diversification.",
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
        "FTEs Allocated": 5,
        "Notes": "Lead RIPTAC program. Neo-1 ternary complex strength uniquely suited. Minimal competition — press the advantage.",
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
        "FTEs Allocated": 3,
        "Notes": "Earlier stage RIPTAC program. NeoLink proteome scan ongoing.",
    },
]


# ── Strategic flags ────────────────────────────────────────────────────────────
# Add, remove, or edit flags as portfolio dynamics shift
# color: hex string, icon: text symbol, title + body: plain text

STRATEGIC_FLAGS = [
    {
        "color": "#cf4f4f",
        "icon": "⚠",
        "title": "High competitive pressure on PRX-001",
        "body": "PRX-001 faces direct competition from Monte Rosa and Kymera — both well-funded and clinically advanced. Neo-1's structural design advantage needs to be demonstrably faster or better to justify the internal resource load. Worth a leadership conversation about whether this target class is better positioned as a partner program.",
    },
    {
        "color": "#3ecf8e",
        "icon": "↑",
        "title": "Immunology whitespace is underweighted",
        "body": "PRX-003 is our only immunology program with 4 FTEs. External data shows low competitive pressure in ProMod immunology. The BMS partnership provides a beachhead. Is the underweighting a deliberate sequencing choice or an allocation gap?",
    },
    {
        "color": "#3ecf8e",
        "icon": "↑",
        "title": "RIPTAC space is wide open — press the advantage",
        "body": "Almost no external competition. Neo-1 ternary complex prediction strength uniquely suited to this modality. Likely the highest-leverage area for deeper investment alongside the Halda partnership.",
    },
    {
        "color": "#3ea8cf",
        "icon": "→",
        "title": "54% of FTE allocation is on partner programs",
        "body": "Appropriate at seed stage — partners fund the work. But as Proxima scales toward Series A, the internal vs. partner balance needs active management to preserve long-term equity value.",
    },
    {
        "color": "#d4a017",
        "icon": "⚠",
        "title": "Blueprint/Sanofi acquisition creates near-term uncertainty",
        "body": "Post-acquisition reprioritization is common and can quietly deprioritize in-flight collaborations. The Q2 2026 milestone is the early warning signal — any delay should trigger a proactive partner conversation before it becomes a formal issue.",
    },
]


# ── Competitor detail panels ───────────────────────────────────────────────────
# Maps target class names to known competitors for the scorecard drill-down
# Update as new entrants emerge or existing players shift focus

COMPETITOR_DETAIL = {
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