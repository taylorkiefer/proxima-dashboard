import requests
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
from config import WHITESPACE_TARGETS

# ── ClinicalTrials.gov API ─────────────────────────────────────────────────────

CLINICALTRIALS_BASE = "https://clinicaltrials.gov/api/v2/studies"

# Edit these to change what modalities are tracked
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
    """
    Pulls ProMod-related clinical trials from ClinicalTrials.gov API v2.
    Returns a cleaned pandas DataFrame.
    """
    all_studies = []
    for term in PROMOD_SEARCH_TERMS:
        params = {
            "query.term": term,
            "filter.overallStatus": (
                "RECRUITING,ACTIVE_NOT_RECRUITING,"
                "NOT_YET_RECRUITING,ENROLLING_BY_INVITATION"
            ),
            "fields": (
                "NCTId,BriefTitle,OverallStatus,Phase,StartDate,"
                "PrimaryCompletionDate,LeadSponsorName,Condition,"
                "InterventionName,BriefSummary"
            ),
            "pageSize": 100,
            "format": "json",
        }
        try:
            response = requests.get(
                CLINICALTRIALS_BASE, params=params, timeout=10)
            if response.status_code == 200:
                all_studies.extend(
                    response.json().get("studies", []))
        except Exception:
            continue

    if not all_studies:
        return pd.DataFrame()

    # Deduplicate by NCT ID
    seen = set()
    unique_studies = []
    for s in all_studies:
        nct_id = (s.get("protocolSection", {})
                   .get("identificationModule", {})
                   .get("nctId", ""))
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
        completion = (status_mod.get("primaryCompletionDateStruct", {})
                               .get("date", "—"))
        sponsor    = (sponsor_mod.get("leadSponsor", {})
                                 .get("name", "—"))

        title    = id_mod.get("briefTitle", "—")
        summary  = desc_mod.get("briefSummary", "")
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
    df = (df.sort_values("_phase_sort")
            .drop(columns=["_phase_sort"])
            .reset_index(drop=True))
    return df


def infer_modality(text):
    """Infer ProMod modality from free text."""
    t = text.lower()
    if "riptac" in t:
        return "RIPTAC"
    elif "protac" in t or "bifunctional" in t:
        return "PROTAC"
    elif "molecular glue" in t:
        return "Molecular Glue"
    elif "protein degrad" in t or "targeted degrad" in t:
        return "Protein Degrader"
    elif "proximity" in t:
        return "Proximity Modulator"
    else:
        return "ProMod (other)"


@st.cache_data(ttl=3600)
def fetch_recent_trials(days=365):
    """Trials started in the last N days."""
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


def build_whitespace_scorecard(trials_df: pd.DataFrame) -> pd.DataFrame:
    """
    Builds the strategic whitespace scorecard.
    Target class data comes from config.py — edit there, not here.
    Clinical trial counts are pulled live from trials_df.
    """

    # Count trials by modality from live data
    modality_counts = {}
    if not trials_df.empty:
        modality_counts = trials_df["Modality"].value_counts().to_dict()

    # For target classes where the modality label doesn't cleanly map
    # to a single ClinicalTrials modality, use combined counts
    def get_trial_count(target):
        modality = target["Modality"]
        if modality == "Molecular Glue":
            # Count both Molecular Glue and ProMod (other) as proxies
            return (
                modality_counts.get("Molecular Glue", 0) +
                modality_counts.get("ProMod (other)", 0)
            )
        elif modality == "PROTAC":
            return modality_counts.get("PROTAC", 0)
        elif modality == "RIPTAC":
            return modality_counts.get("RIPTAC", 0)
        elif modality == "Molecular Glue / PROTAC":
            return (
                modality_counts.get("Molecular Glue", 0) +
                modality_counts.get("PROTAC", 0) +
                modality_counts.get("ProMod (other)", 0)
            )
        elif modality == "Protein Degrader":
            return modality_counts.get("Protein Degrader", 0)
        else:
            return modality_counts.get("ProMod (other)", 0)

    rows = []
    for t in WHITESPACE_TARGETS:
        trial_count = get_trial_count(t)
        rows.append({**t, "Clinical Trials": trial_count})

    df = pd.DataFrame(rows)

    # Scoring functions
    def score_validation(n):
        if n >= 8:   return 3
        elif n >= 3: return 2
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