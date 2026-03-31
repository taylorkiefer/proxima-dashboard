import anthropic
import streamlit as st
import os
from dotenv import load_dotenv
import pandas as pd

from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).parent / ".env")


def get_client():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    return anthropic.Anthropic(api_key=api_key)


def synthesize_external_landscape(trials_df: pd.DataFrame) -> str:
    client = get_client()
    if not client:
        return "API key not configured."

    if trials_df.empty:
        trial_summary = "No trial data available."
    else:
        phase_counts = trials_df["Phase"].value_counts().to_dict()
        modality_counts = trials_df["Modality"].value_counts().to_dict()
        top_sponsors = trials_df["Sponsor"].value_counts().head(5).to_dict()
        trial_summary = (
            f"Total active ProMod trials: {len(trials_df)}\n"
            f"Trials by phase: {phase_counts}\n"
            f"Trials by modality: {modality_counts}\n"
            f"Top sponsors by trial count: {top_sponsors}"
        )

    prompt = (
        "You are a senior Strategy & Operations team member at Proxima, "
        "an AI-native biotech company pioneering proximity-based therapeutics "
        "(molecular glues, PROTACs, RIPTACs). Proxima's core assets are:\n"
        "- Neo-1: a unified foundation model for structure prediction and "
        "de novo molecular generation, with particular strength in ternary "
        "complex prediction\n"
        "- NeoLink: a cross-linking mass spectrometry platform that generates "
        "proteome-wide structural data at scale\n"
        "- Active partnerships with J&J, BMS, Blueprint/Sanofi, Halda, and BI\n"
        "- $80M seed round closed January 2026, first program approaching "
        "IND in 2026\n\n"
        "Here is the current external landscape data pulled live from "
        f"ClinicalTrials.gov:\n{trial_summary}\n\n"
        "Key competitors: Arvinas (Phase 3 PROTAC), Kymera (Phase 2, "
        "expanding to glues), Monte Rosa (Phase 1 glues, strong computational "
        "platform), C4 Therapeutics (Phase 1/2), Revolution Medicines "
        "(Phase 3 molecular glue daraxonrasib), Nurix (Phase 2 degraders).\n\n"
        "Write a 3-4 paragraph strategic synthesis of what this external "
        "landscape means for Proxima RIGHT NOW. Be specific and opinionated. "
        "Focus on:\n"
        "1. What the clinical data signals about where the ProMod field is "
        "heading\n"
        "2. Where the competitive whitespace is that Proxima should be paying "
        "attention to\n"
        "3. One concrete recommendation for Proxima's partnership or internal "
        "program strategy based on this data\n\n"
        "Write in first person plural as if you are on the Proxima team. "
        "Be direct, avoid generic statements, and ground every claim in the "
        "data. Do not use bullet points. Write in flowing paragraphs like "
        "an internal memo."
    )

    try:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        return f"Synthesis unavailable: {str(e)}"


def synthesize_partnership_portfolio(partnerships: list) -> str:
    client = get_client()
    if not client:
        return "API key not configured."

    partner_summary = ""
    for p in partnerships:
        partner_summary += (
            f"- {p['Partner']}: {p['Programs']} programs, most advanced at "
            f"{p['Most Advanced']}, next milestone {p['Next Milestone']} "
            f"in {p['Milestone Date']} (~{p['Days Until']} days), "
            f"risk level: {p['Risk']}\n"
        )

    prompt = (
        "You are a senior Strategy & Operations team member at Proxima, "
        "an AI-native biotech company with active partnerships with J&J, "
        "BMS, Blueprint/Sanofi, Halda Therapeutics, and Boehringer Ingelheim.\n\n"
        f"Current partnership portfolio status:\n{partner_summary}\n\n"
        "Additional context:\n"
        "- Blueprint Medicines was recently acquired by Sanofi — "
        "post-acquisition reprioritization is a real risk\n"
        "- The J&J program is Proxima's first approaching IND, expected 2026\n"
        "- Halda is Proxima's deepest technical integration — Proxima is "
        "their entire computational backbone\n"
        "- Multiple milestones are due in the next 60-120 days\n\n"
        "Write a 3-4 paragraph strategic assessment of the partnership "
        "portfolio. Focus on:\n"
        "1. What the portfolio looks like from a risk and concentration "
        "standpoint\n"
        "2. Which partnerships deserve the most operational attention in "
        "the next 90 days and why\n"
        "3. One thing about the portfolio structure that should prompt a "
        "conversation at the leadership level\n\n"
        "Write in first person plural as if you are on the Proxima "
        "Strat/Ops team. Be direct and specific. No bullet points. "
        "Write like an internal memo to the CEO."
    )

    try:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        return f"Synthesis unavailable: {str(e)}"


def synthesize_resource_allocation(programs: list) -> str:
    client = get_client()
    if not client:
        return "API key not configured."

    program_summary = ""
    for p in programs:
        program_summary += (
            f"- {p['Program']} ({p['Modality']}, {p['Indication']}): "
            f"stage {p['Stage']}, {p['FTEs Allocated']} FTEs, "
            f"owned by {p['Internal vs Partner']}, "
            f"competitive pressure: {p['Competitive Pressure']}, "
            f"NeoLink coverage: {p['NeoLink Coverage']}\n"
        )

    total_ftes = sum(p["FTEs Allocated"] for p in programs)
    internal_ftes = sum(
        p["FTEs Allocated"] for p in programs
        if p["Internal vs Partner"] == "Internal"
    )
    partner_ftes = total_ftes - internal_ftes

    prompt = (
        "You are a senior Strategy & Operations team member at Proxima. "
        "You are reviewing how the company's scientific resources are "
        "allocated across its internal and partner programs.\n\n"
        f"Current portfolio:\n{program_summary}\n\n"
        f"Resource summary:\n"
        f"- Total FTEs allocated: {total_ftes}\n"
        f"- FTEs on internal programs: {internal_ftes} "
        f"({round(internal_ftes/total_ftes*100)}% of total)\n"
        f"- FTEs on partner programs: {partner_ftes} "
        f"({round(partner_ftes/total_ftes*100)}% of total)\n\n"
        "Proxima's strategic context:\n"
        "- Neo-1's strongest advantage is in ternary complex prediction\n"
        "- NeoLink covers ~70% of the human proteome\n"
        "- Just raised $80M and is actively hiring\n"
        "- First program approaching IND in 2026 (J&J partnership)\n"
        "- RIPTAC space has minimal external competition\n"
        "- Immunology ProMod space is largely uncrowded\n\n"
        "Write a 3-4 paragraph strategic assessment of how Proxima is "
        "allocating its resources. Focus on:\n"
        "1. Whether the current internal vs. partner FTE split makes sense "
        "given Proxima's stage and strategy\n"
        "2. Where resources appear underweighted relative to the opportunity\n"
        "3. One specific reallocation or hiring decision you would recommend "
        "bringing to leadership\n\n"
        "Write in first person plural as if you are on the Proxima "
        "Strat/Ops team. Be direct, opinionated, and specific. "
        "No bullet points. Write like an internal strategy memo."
    )

    try:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        return f"Synthesis unavailable: {str(e)}"