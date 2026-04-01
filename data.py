import requests
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st

# ── ClinicalTrials.gov API ─────────────────────────────────────────────────────

CLINICALTRIALS_BASE = "https://clinicaltrials.gov/api/v2/studies"

PROMOD_SEARCH_TERMS = [
    "molecular glue",
    "PROTAC",
    "protein degrader",
    "proximity modulator",
    "targeted protein degradation",
    "bifunctional degrader",
    "RIPTAC",
    "molecular glue degrader",
]

PHASE_MAP = {
    "PHASE1": "Phase 1",
    "PHASE2": "Phase 2",
    "PHASE3": "Phase 3",
    "PHASE1_PHASE2": "Phase 1/2",
    "PHASE2_PHASE3": "Phase 2/3",
    "EARLY_PHASE1": "Early Phase 1",
    "NA": "N/A",
}

STATUS_MAP = {
    "RECRUITING": "Recruiting",
    "ACTIVE_NOT_RECRUITING": "Active",
    "COMPLETED": "Completed",
    "NOT_YET_RECRUITING": "Not Yet Recruiting",
    "TERMINATED": "Terminated",
    "WITHDRAWN": "Withdrawn",
    "SUSPENDED": "Suspended",
    "ENROLLING_BY_INVITATION": "By Invitation",
    "UNKNOWN": "Unknown",
}


@st.cache_data(ttl=3600)
def fetch_clinical_trials():
    all_studies = []
    for term in PROMOD_SEARCH_TERMS:
        params = {
            "query.term": term,
            "filter.overallStatus": "RECRUITING,ACTIVE_NOT_RECRUITING,NOT_YET_RECRUITING,ENROLLING_BY_INVITATION",
            "fields": "NCTId,BriefTitle,OverallStatus,Phase,StartDate,PrimaryCompletionDate,LeadSponsorName,Condition,InterventionName,BriefSummary",
            "pageSize": 100,
            "format": "json",
        }
        try:
            response = requests.get(
                CLINICALTRIALS_BASE, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                all_studies.extend(data.get("studies", []))
        except Exception:
            continue

    if not all_studies:
        return pd.DataFrame()

    seen = set()
    unique_studies = []
    for s in all_studies:
        nct_id = s.get("protocolSection", {}).get(
            "identificationModule", {}).get("nctId", "")
        if nct_id and nct_id not in seen:
            seen.add(nct_id)
            unique_studies.append(s)

    rows = []
    for s in unique_studies:
        proto          = s.get("protocolSection", {})
        id_mod         = proto.get("identificationModule", {})
        status_mod     = proto.get("statusModule", {})
        sponsor_mod    = proto.get("sponsorCollaboratorsModule", {})
        conditions_mod = proto.get("conditionsModule", {})
        design_mod     = proto.get("designModule", {})
        desc_mod       = proto.get("descriptionModule", {})

        phases    = design_mod.get("phases", [])
        phase_raw = phases[0] if phases else "NA"
        phase     = PHASE_MAP.get(phase_raw, phase_raw)

        status_raw = status_mod.get("overallStatus", "UNKNOWN")
        status     = STATUS_MAP.get(status_raw, status_raw)

        conditions    = conditions_mod.get("conditions", [])
        condition_str = ", ".join(conditions[:2]) if conditions else "—"

        start      = status_mod.get("startDateStruct", {}).get("date", "—")
        completion = status_mod.get(
            "primaryCompletionDateStruct", {}).get("date", "—")
        sponsor    = sponsor_mod.get("leadSponsor", {}).get("name", "—")

        title   = id_mod.get("briefTitle", "—")
        summary = desc_mod.get("briefSummary", "")
        modality = infer_modality(title + " " + summary)

        rows.append({
            "NCT ID":          id_mod.get("nctId", "—"),
            "Title":           title,
            "Sponsor":         sponsor,
            "Phase":           phase,
            "Status":          status,
            "Indication":      condition_str,
            "Modality":        modality,
            "Start Date":      start,
            "Est. Completion": completion,
        })

    df = pd.DataFrame(rows)
    phase_order = {
        "Phase 3": 0, "Phase 2/3": 1, "Phase 2": 2,
        "Phase 1/2": 3, "Phase 1": 4, "Early Phase 1": 5, "N/A": 6
    }
    df["_phase_sort"] = df["Phase"].map(phase_order).fillna(99)
    df = df.sort_values("_phase_sort").drop(
        columns=["_phase_sort"]).reset_index(drop=True)
    return df


def infer_modality(text):
    t = text.lower()
    if "riptac" in t:                              return "RIPTAC"
    elif "protac" in t or "bifunctional" in t:     return "PROTAC"
    elif "molecular glue" in t:                    return "Molecular Glue"
    elif "protein degrad" in t or "targeted degrad" in t:
                                                   return "Protein Degrader"
    elif "proximity" in t:                         return "Proximity Modulator"
    else:                                          return "ProMod (other)"


@st.cache_data(ttl=3600)
def fetch_recent_trials(days=365):
    df = fetch_clinical_trials()
    if df.empty:
        return df
    cutoff = datetime.now() - timedelta(days=days)

    def parse_date(d):
        for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
            try:
                return datetime.strptime(d, fmt)
            except Exception:
                continue
        return None

    df["_start_parsed"] = df["Start Date"].apply(parse_date)
    recent = df[df["_start_parsed"] >= cutoff].drop(
        columns=["_start_parsed"])
    return recent


@st.cache_data(ttl=3600)
def build_whitespace_scorecard(trials_df: pd.DataFrame) -> pd.DataFrame:
    protac_count = len(trials_df[
        trials_df["Modality"] == "PROTAC"
    ]) if not trials_df.empty else 0
    glue_count = len(trials_df[
        trials_df["Modality"] == "Molecular Glue"
    ]) if not trials_df.empty else 0
    riptac_count = len(trials_df[
        trials_df["Modality"] == "RIPTAC"
    ]) if not trials_df.empty else 0

    target_classes = [
        {
            "Target Class":    "E3 Ligase / Molecular Glue",
            "Modality":        "Molecular Glue",
            "Clinical Trials": glue_count,
            "Competitors":     4,
            "Proxima Program": "PRX-001 (Lead Opt)",
            "Proxima Partner": "J&J",
            "NeoLink Coverage":"High",
            "Indication":      "Oncology",
            "Whitespace Notes":"Crowded in oncology. Immunology and CNS glue applications remain largely unexplored. Neo-1 glue design speed is the key differentiator against Monte Rosa and Kymera.",
        },
        {
            "Target Class":    "BRD / Transcription Factor",
            "Modality":        "PROTAC",
            "Clinical Trials": protac_count,
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
            "Clinical Trials": 2,
            "Competitors":     1,
            "Proxima Program": "PRX-003 (Target Validation)",
            "Proxima Partner": "None",
            "NeoLink Coverage":"Medium",
            "Indication":      "Immunology",
            "Whitespace Notes":"Significant whitespace. Low competition, strong biological rationale. Only Proxima internal immunology program — underdeveloped relative to the opportunity size.",
        },
        {
            "Target Class":    "RIPTAC Targets",
            "Modality":        "RIPTAC",
            "Clinical Trials": riptac_count,
            "Competitors":     1,
            "Proxima Program": "HALDA-PRX-01/02",
            "Proxima Partner": "Halda",
            "NeoLink Coverage":"High",
            "Indication":      "Oncology",
            "Whitespace Notes":"Wide open. Minimal competition. Neo-1 ternary complex prediction strength is uniquely suited to RIPTAC design. First mover advantage available if Halda programs accelerate.",
        },
        {
            "Target Class":    "Immune Modulators",
            "Modality":        "PROTAC",
            "Clinical Trials": 3,
            "Competitors":     2,
            "Proxima Program": "BMS-PRX-01",
            "Proxima Partner": "BMS",
            "NeoLink Coverage":"Medium",
            "Indication":      "Immunology",
            "Whitespace Notes":"Emerging area. BMS partnership provides a beachhead. Significant room for additional partners in autoimmune and inflammatory indications.",
        },
        {
            "Target Class":    "CNS Targets",
            "Modality":        "Molecular Glue / PROTAC",
            "Clinical Trials": 1,
            "Competitors":     0,
            "Proxima Program": "None",
            "Proxima Partner": "None",
            "NeoLink Coverage":"Medium",
            "Indication":      "Neurodegeneration",
            "Whitespace Notes":"Significant unmet need. Almost no ProMod competition. BBB penetration is a challenge but not insurmountable. High-value partnership opportunity with no current Proxima presence.",
        },
        {
            "Target Class":    "Cardiovascular Targets",
            "Modality":        "PROTAC",
            "Clinical Trials": 2,
            "Competitors":     1,
            "Proxima Program": "None",
            "Proxima Partner": "None",
            "NeoLink Coverage":"Medium",
            "Indication":      "Cardiovascular",
            "Whitespace Notes":"Underexplored. Large unmet need. NeoLink coverage growing. Potential new partnership vertical with no current Proxima presence.",
        },
        {
            "Target Class":    "Viral / Infectious Disease",
            "Modality":        "Molecular Glue",
            "Clinical Trials": 1,
            "Competitors":     0,
            "Proxima Program": "None",
            "Proxima Partner": "None",
            "NeoLink Coverage":"Low",
            "Indication":      "Infectious Disease",
            "Whitespace Notes":"Very early stage. Limited NeoLink coverage currently. Low near-term priority but worth monitoring as the platform matures.",
        },
    ]

    df = pd.DataFrame(target_classes)

    def score_validation(t):
        if t >= 8:   return 3
        elif t >= 3: return 2
        else:        return 1

    def score_crowding(c):
        if c == 0:   return 3
        elif c <= 2: return 2
        else:        return 1

    def score_coverage(prog, part):
        if prog != "None" and part != "None": return 3
        elif prog != "None" or part != "None": return 2
        else:                                  return 1

    def score_neolink(n):
        return {"High": 3, "Medium": 2, "Low": 1}.get(n, 1)

    df["Validation Score"] = df["Clinical Trials"].apply(score_validation)
    df["Whitespace Score"] = df["Competitors"].apply(score_crowding)
    df["Coverage Score"]   = df.apply(
        lambda r: score_coverage(
            r["Proxima Program"], r["Proxima Partner"]), axis=1)
    df["NeoLink Score"]    = df["NeoLink Coverage"].apply(score_neolink)
    df["Opportunity Score"] = (
        df["Validation Score"] +
        df["Whitespace Score"] +
        df["NeoLink Score"]
    )
    df["Strategic Priority"] = df.apply(
        lambda r:
            "🔴 Act Now"    if r["Opportunity Score"] >= 7
                               and r["Coverage Score"] == 1
            else "🟡 Strengthen" if r["Opportunity Score"] >= 6
                                    and r["Coverage Score"] <= 2
            else "🟢 Maintain"   if r["Coverage Score"] == 3
            else "⚪ Monitor",
        axis=1
    )
    return df.sort_values("Opportunity Score", ascending=False)
