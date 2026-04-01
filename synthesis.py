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

def synthesize_resource_allocation(programs: list) -> str:
    client = get_client()
    if not client:
        return "API key not configured."

    program_summary = ""
    for p in programs:
        program_summary += (
            f"- {p['Program']} ({p['Modality']}, {p['Indication']}): "
            f"{p['Stage']}, {p['FTEs Allocated']} FTEs, "
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
        "Review how resources are allocated and write a strategic read "
        "in exactly this format — no headers, no markdown, "
        "no bullet points:\n\n"
        f"Portfolio:\n{program_summary}\n"
        f"FTE split: {internal_ftes} internal "
        f"({round(internal_ftes/total_ftes*100)}%), "
        f"{partner_ftes} partner "
        f"({round(partner_ftes/total_ftes*100)}%)\n\n"
        "ALLOCATION READ: [One sentence on whether the current "
        "resource allocation makes sense given Proxima's stage.]\n\n"
        "UNDERWEIGHTED: [One sentence on where resources are too "
        "light relative to the opportunity.]\n\n"
        "OVEREXPOSED: [One sentence on where competitive pressure "
        "makes the current allocation worth scrutinizing.]\n\n"
        "RECOMMENDATION: [2-3 sentences on the one hiring or "
        "reallocation decision leadership should make. Specific.]\n\n"
        "Be direct. Write like you're briefing the CEO. No hedging."
    )

    try:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        return f"Synthesis unavailable: {str(e)}"


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
            f"- {p['Partner']}: {p['Programs']} programs, "
            f"most advanced at {p['Most Advanced']}, "
            f"next milestone {p['Next Milestone']} "
            f"in {p['Milestone Date']} (~{p['Days Until']} days), "
            f"risk: {p['Risk']}\n"
        )

    prompt = (
        "You are a senior Strategy & Operations team member at Proxima. "
        "Review the partnership portfolio and write a strategic read "
        "in exactly this format — no headers, no markdown, "
        "no bullet points:\n\n"
        f"Portfolio status:\n{partner_summary}\n\n"
        "PORTFOLIO HEALTH: [One sentence on the overall state of "
        "the partnership portfolio right now.]\n\n"
        "BIGGEST RISK: [One sentence on the single most important "
        "risk in the next 90 days.]\n\n"
        "BIGGEST OPPORTUNITY: [One sentence on what this portfolio "
        "unlocks if milestones hit.]\n\n"
        "RECOMMENDATION: [2-3 sentences on the one operational "
        "priority leadership should act on this week. Specific.]\n\n"
        "Be direct. Write like you're briefing the CEO. No hedging."
    )

    try:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        return f"Synthesis unavailable: {str(e)}"


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
        "an AI-native biotech pioneering proximity-based therapeutics. "
        "Proxima's assets: Neo-1 (unified structure prediction + molecular "
        "generation, strongest on ternary complexes), NeoLink (proteome-wide "
        "XLMS structural data platform), active partnerships with J&J, BMS, "
        "Blueprint/Sanofi, Halda, and BI. $80M seed closed January 2026.\n\n"
        f"Current external landscape data:\n{trial_summary}\n\n"
        "Write a strategic read in exactly this format — no headers, "
        "no markdown, no bullet points:\n\n"
        "SIGNAL: [One sentence on the single most important thing the "
        "clinical data is telling us right now.]\n\n"
        "WHITESPACE: [One sentence on where the biggest opportunity is "
        "that competitors are missing.]\n\n"
        "PROXIMA EDGE: [One sentence on why Proxima is specifically "
        "positioned to win in that whitespace.]\n\n"
        "RECOMMENDATION: [2-3 sentences max on the one thing Proxima "
        "should do differently based on this data. Specific and actionable.]\n\n"
        "Be direct. No hedging. Write like you're briefing the CEO "
        "before a board meeting, not writing a report."
    )

    try:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        return f"Synthesis unavailable: {str(e)}"