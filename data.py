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

@st.cache_data(ttl=3600)  # Cache for 1 hour so we don't hammer the API
def fetch_clinical_trials():
    """
    Pulls ProMod-related clinical trials from ClinicalTrials.gov API v2.
    Returns a cleaned pandas DataFrame.
    """
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
            response = requests.get(CLINICALTRIALS_BASE, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                studies = data.get("studies", [])
                all_studies.extend(studies)
        except Exception:
            continue

    if not all_studies:
        return pd.DataFrame()

    # Deduplicate by NCT ID
    seen = set()
    unique_studies = []
    for s in all_studies:
        nct_id = s.get("protocolSection", {}).get("identificationModule", {}).get("nctId", "")
        if nct_id and nct_id not in seen:
            seen.add(nct_id)
            unique_studies.append(s)

    # Parse into rows
    rows = []
    for s in unique_studies:
        proto = s.get("protocolSection", {})
        id_mod = proto.get("identificationModule", {})
        status_mod = proto.get("statusModule", {})
        sponsor_mod = proto.get("sponsorCollaboratorsModule", {})
        conditions_mod = proto.get("conditionsModule", {})
        design_mod = proto.get("designModule", {})
        interventions_mod = proto.get("armsInterventionsModule", {})
        desc_mod = proto.get("descriptionModule", {})

        # Phase
        phases = design_mod.get("phases", [])
        phase_raw = phases[0] if phases else "NA"
        phase = PHASE_MAP.get(phase_raw, phase_raw)

        # Status
        status_raw = status_mod.get("overallStatus", "UNKNOWN")
        status = STATUS_MAP.get(status_raw, status_raw)

        # Conditions
        conditions = conditions_mod.get("conditions", [])
        condition_str = ", ".join(conditions[:2]) if conditions else "—"

        # Interventions
        interventions = interventions_mod.get("interventions", [])
        intervention_names = [i.get("name", "") for i in interventions[:2]]
        intervention_str = ", ".join(intervention_names) if intervention_names else "—"

        # Dates
        start = status_mod.get("startDateStruct", {}).get("date", "—")
        completion = status_mod.get("primaryCompletionDateStruct", {}).get("date", "—")

        # Sponsor
        sponsor = sponsor_mod.get("leadSponsor", {}).get("name", "—")

        # Modality tag — infer from title/summary
        title = id_mod.get("briefTitle", "—")
        summary = desc_mod.get("briefSummary", "")
        modality = infer_modality(title + " " + summary)

        rows.append({
            "NCT ID": id_mod.get("nctId", "—"),
            "Title": title,
            "Sponsor": sponsor,
            "Phase": phase,
            "Status": status,
            "Indication": condition_str,
            "Modality": modality,
            "Start Date": start,
            "Est. Completion": completion,
            "Intervention": intervention_str,
        })

    df = pd.DataFrame(rows)

    # Sort by phase (most advanced first)
    phase_order = {
        "Phase 3": 0, "Phase 2/3": 1, "Phase 2": 2,
        "Phase 1/2": 3, "Phase 1": 4, "Early Phase 1": 5, "N/A": 6
    }
    df["_phase_sort"] = df["Phase"].map(phase_order).fillna(99)
    df = df.sort_values("_phase_sort").drop(columns=["_phase_sort"])
    df = df.reset_index(drop=True)

    return df


def infer_modality(text):
    """Infer ProMod modality from free text."""
    text_lower = text.lower()
    if "riptac" in text_lower:
        return "RIPTAC"
    elif "protac" in text_lower or "bifunctional" in text_lower:
        return "PROTAC"
    elif "molecular glue" in text_lower:
        return "Molecular Glue"
    elif "protein degrad" in text_lower or "targeted degrad" in text_lower:
        return "Protein Degrader"
    elif "proximity" in text_lower:
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
    recent = df[df["_start_parsed"] >= cutoff].drop(columns=["_start_parsed"])
    return recent
