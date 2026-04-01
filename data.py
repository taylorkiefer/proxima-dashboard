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

# ── PubMed Literature Signals ───────────────────────────────────────

PUBMED_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

LITERATURE_QUERIES = [
    "molecular glue degrader",
    "PROTAC protein degradation",
    "proximity modulator therapeutic",
    "RIPTAC targeted degradation",
    "induced proximity drug discovery",
]

@st.cache_data(ttl=3600)
def fetch_pubmed_articles(query: str, max_results: int = 5) -> list:
    """
    Fetches recent PubMed articles for a given query.
    Returns a list of article dicts.
    """
    try:
        # Step 1: Search for IDs
        search_url = f"{PUBMED_BASE}/esearch.fcgi"
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "sort": "date",
            "retmode": "json",
            "datetype": "pdat",
            "reldate": 180,  # Last 6 months
        }
        search_resp = requests.get(search_url, params=search_params, timeout=10)
        if search_resp.status_code != 200:
            return []

        id_list = search_resp.json().get("esearchresult", {}).get("idlist", [])
        if not id_list:
            return []

        # Step 2: Fetch details for those IDs
        fetch_url = f"{PUBMED_BASE}/esummary.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(id_list),
            "retmode": "json",
        }
        fetch_resp = requests.get(fetch_url, params=fetch_params, timeout=10)
        if fetch_resp.status_code != 200:
            return []

        result = fetch_resp.json().get("result", {})
        articles = []
        for uid in id_list:
            item = result.get(uid, {})
            if not item:
                continue

            # Authors
            authors = item.get("authors", [])
            author_str = authors[0].get("name", "") if authors else "—"
            if len(authors) > 1:
                author_str += f" et al."

            # Journal
            journal = item.get("source", "—")

            # Date
            pub_date = item.get("pubdate", "—")

            # Title
            title = item.get("title", "—").rstrip(".")

            articles.append({
                "title": title,
                "authors": author_str,
                "journal": journal,
                "date": pub_date,
                "pmid": uid,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{uid}/",
                "source": "PubMed",
                "query": query,
            })

        return articles

    except Exception:
        return []


@st.cache_data(ttl=3600)
def fetch_biorxiv_articles(query: str, max_results: int = 5) -> list:
    """
    Fetches recent bioRxiv preprints via Europe PMC API,
    which reliably indexes bioRxiv content.
    """
    try:
        url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
        params = {
            "query": f"{query} SOURCE:PPR",  # PPR = preprints incl. bioRxiv
            "format": "json",
            "pageSize": max_results,
            "sort": "P_PDATE_D desc",
            "resultType": "core",
        }
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code != 200:
            return []

        results = resp.json().get("resultList", {}).get("result", [])
        if not results:
            return []

        articles = []
        for item in results:
            # Authors
            author_list = item.get("authorList", {}).get("author", [])
            if author_list:
                first = author_list[0]
                author_str = first.get("fullName",
                             first.get("lastName", "—"))
                if len(author_list) > 1:
                    author_str += " et al."
            else:
                author_str = "—"

            # Source label
            source_str = item.get("bookOrReportDetails", {})
            journal = item.get("journalTitle", "")
            if not journal:
                journal = "bioRxiv (preprint)"

            # URL
            doi = item.get("doi", "")
            url_link = f"https://doi.org/{doi}" if doi \
                       else "https://europepmc.org"

            # Date
            date = item.get("firstPublicationDate",
                   item.get("pubYear", "—"))

            articles.append({
                "title":   item.get("title", "—").rstrip("."),
                "authors": author_str,
                "journal": journal,
                "date":    date,
                "pmid":    doi,
                "url":     url_link,
                "source":  "bioRxiv",
                "query":   query,
            })

        return articles

    except Exception:
        return []

@st.cache_data(ttl=3600)
def fetch_all_literature() -> pd.DataFrame:
    """
    Fetches and combines PubMed + bioRxiv articles across all queries.
    Returns a deduplicated, sorted DataFrame.
    """
    all_articles = []

    for query in LITERATURE_QUERIES:
        pubmed = fetch_pubmed_articles(query, max_results=4)
        biorxiv = fetch_biorxiv_articles(query, max_results=3)
        all_articles.extend(pubmed)
        all_articles.extend(biorxiv)

    if not all_articles:
        return pd.DataFrame()

    df = pd.DataFrame(all_articles)

    # Deduplicate by title
    df = df.drop_duplicates(subset=["title"])

    # Sort by date descending
    df = df.sort_values("date", ascending=False).reset_index(drop=True)

    return df

@st.cache_data(ttl=60)
def debug_europepmc(query: str) -> dict:
    """Temporary debug function to see raw API response."""
    try:
        url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
        params = {
            "query": f"{query} (SRC:PPR OR SRC:MED)",
            "format": "json",
            "pageSize": 5,
            "sort": "P_PDATE_D desc",
            "resultType": "core",
        }
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        # Just return the first result so we can see the structure
        results = data.get("resultList", {}).get("result", [])
        return {
            "status": resp.status_code,
            "hitCount": data.get("hitCount", 0),
            "first_result": results[0] if results else "no results",
        }
    except Exception as e:
        return {"error": str(e)}
    
@st.cache_data(ttl=3600)
def build_whitespace_scorecard(trials_df: pd.DataFrame) -> pd.DataFrame:
    """
    Builds a whitespace scorecard scoring ProMod target classes
    across clinical validation, competitive crowding, and Proxima coverage.
    """

    target_classes = [
        {
            "Target Class": "E3 Ligase / Molecular Glue",
            "Modality": "Molecular Glue",
            "Clinical Trials": len(trials_df[
                trials_df["Modality"] == "Molecular Glue"
            ]) if not trials_df.empty else 0,
            "Competitors": 4,
            "Proxima Program": "PRX-001 (Lead Opt)",
            "Proxima Partner": "J&J",
            "NeoLink Coverage": "High",
            "Indication": "Oncology",
            "Whitespace Notes": "Crowded in oncology. Immunology and CNS applications remain largely unexplored. Neo-1 glue design speed is the differentiator.",
        },
        {
            "Target Class": "BRD / Transcription Factor",
            "Modality": "PROTAC",
            "Clinical Trials": len(trials_df[
                trials_df["Modality"] == "PROTAC"
            ]) if not trials_df.empty else 0,
            "Competitors": 3,
            "Proxima Program": "PRX-002 (Hit Discovery)",
            "Proxima Partner": "BMS",
            "NeoLink Coverage": "High",
            "Indication": "Oncology",
            "Whitespace Notes": "BRD4 is crowded. Novel BRD family members remain accessible via NeoLink proteome coverage. Strong structural data advantage.",
        },
        {
            "Target Class": "Kinase / Scaffolding Protein",
            "Modality": "Molecular Glue",
            "Clinical Trials": 2,
            "Competitors": 1,
            "Proxima Program": "PRX-003 (Target Validation)",
            "Proxima Partner": "None",
            "NeoLink Coverage": "Medium",
            "Indication": "Immunology",
            "Whitespace Notes": "Significant whitespace. Low competition, strong biological rationale. Only Proxima internal program in immunology. Partnership opportunity.",
        },
        {
            "Target Class": "RIPTAC Targets",
            "Modality": "RIPTAC",
            "Clinical Trials": len(trials_df[
                trials_df["Modality"] == "RIPTAC"
            ]) if not trials_df.empty else 0,
            "Competitors": 1,
            "Proxima Program": "HALDA-PRX-01/02",
            "Proxima Partner": "Halda",
            "NeoLink Coverage": "High",
            "Indication": "Oncology",
            "Whitespace Notes": "Wide open. Minimal competition. Neo-1 ternary complex strength is uniquely suited. First mover advantage available if programs accelerate.",
        },
        {
            "Target Class": "Immune Modulators",
            "Modality": "PROTAC",
            "Clinical Trials": 3,
            "Competitors": 2,
            "Proxima Program": "BMS-PRX-01",
            "Proxima Partner": "BMS",
            "NeoLink Coverage": "Medium",
            "Indication": "Immunology",
            "Whitespace Notes": "Emerging area. BMS partnership provides beachhead. Significant room for additional partners in autoimmune and inflammatory indications.",
        },
        {
            "Target Class": "CNS Targets",
            "Modality": "Molecular Glue / PROTAC",
            "Clinical Trials": 1,
            "Competitors": 0,
            "Proxima Program": "None",
            "Proxima Partner": "None",
            "NeoLink Coverage": "Medium",
            "Indication": "Neurodegeneration",
            "Whitespace Notes": "Significant unmet need. Almost no ProMod competition. Blood-brain barrier penetration is a challenge but not insurmountable. High-value partnership opportunity.",
        },
        {
            "Target Class": "Viral / Infectious Disease",
            "Modality": "Molecular Glue",
            "Clinical Trials": 1,
            "Competitors": 0,
            "Proxima Program": "None",
            "Proxima Partner": "None",
            "NeoLink Coverage": "Low",
            "Indication": "Infectious Disease",
            "Whitespace Notes": "Very early. Limited NeoLink coverage. Low near-term priority but worth monitoring as ProMod platform matures.",
        },
        {
            "Target Class": "Cardiovascular Targets",
            "Modality": "PROTAC",
            "Clinical Trials": 2,
            "Competitors": 1,
            "Proxima Program": "None",
            "Proxima Partner": "None",
            "NeoLink Coverage": "Medium",
            "Indication": "Cardiovascular",
            "Whitespace Notes": "Underexplored. One competitor adjacent. Large unmet need. NeoLink coverage growing. Potential new partnership vertical.",
        },
    ]

    df = pd.DataFrame(target_classes)

    def score_validation(trials):
        if trials >= 8:   return 3
        elif trials >= 3: return 2
        else:             return 1

    def score_crowding(competitors):
        if competitors == 0:   return 3
        elif competitors <= 2: return 2
        else:                  return 1

    def score_coverage(program, partner):
        if program != "None" and partner != "None": return 3
        elif program != "None" or partner != "None": return 2
        else:                                        return 1

    def score_neolink(coverage):
        return {"High": 3, "Medium": 2, "Low": 1}.get(coverage, 1)

    df["Validation Score"] = df["Clinical Trials"].apply(score_validation)
    df["Whitespace Score"] = df["Competitors"].apply(score_crowding)
    df["Coverage Score"]   = df.apply(
        lambda r: score_coverage(r["Proxima Program"], r["Proxima Partner"]),
        axis=1
    )
    df["NeoLink Score"]    = df["NeoLink Coverage"].apply(score_neolink)

    df["Opportunity Score"] = (
        df["Validation Score"] +
        df["Whitespace Score"] +
        df["NeoLink Score"]
    )

    df["Strategic Priority"] = df.apply(
        lambda r: "🔴 Act Now"    if r["Opportunity Score"] >= 7
                                     and r["Coverage Score"] == 1
             else "🟡 Strengthen" if r["Opportunity Score"] >= 6
                                     and r["Coverage Score"] <= 2
             else "🟢 Maintain"   if r["Coverage Score"] == 3
             else "⚪ Monitor",
        axis=1
    )

    df = df.sort_values("Opportunity Score", ascending=False)
    return df