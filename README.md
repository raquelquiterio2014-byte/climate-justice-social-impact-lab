# Climate Justice & Social Impact Lab V1.0

**COP31 AI Solutions Lab — Day 10 | November 18, 2026**

An independent, educational Python/Streamlit application exploring **community-level** climate exposure, accessibility of adaptation services, data quality, hypothetical improvements, and optional human-reviewed AI explanations.

## Four modules

1. **Social Impact Overview** — three illustrative communities and independent exposure/access indicators.
2. **Climate Vulnerability Analysis** — flood and heat exposure, cooling and accessible shelter access, missing/stale data, and transparent what-if arithmetic. **No vulnerability scores or rankings.**
3. **AI & Human Review** — optional Gemini 2.5 Flash JSON explanations (schema validated, scenario ID checked) and SQLite human review records.
4. **Export & Methodology** — CSV/JSON, SHA-256 fingerprints, references, caveats.

## Install and run (Windows, Python 3.12)

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q
python -m streamlit run app.py
```

For optional Gemini calls, copy `.env.example` to `.env` and replace the placeholder with your own API key. Never commit `.env`. No GPU is needed.

## Data and ethics

All three communities in `data/communities.json` are **synthetic** and do not describe real places, people or vulnerable groups. The data is not sourced from COP31, IPCC, UNFCCC or UNDRR. Reference links are background reading only. No personal information is collected. Missing values remain missing, not zero. The 30-day staleness threshold is illustrative, not an official rule. There is no combined vulnerability score, ranking, automated resource allocation or individual-level classification.

Intervention sliders add **hypothetical percentage points** to two access measures, capped at 100%. They do not predict actual effectiveness, cost, feasibility or policy impact. Gemini may hallucinate even with structured output; a valid ID does not verify a claim. SQLite audit records are locally editable, and SHA-256 does not provide immutable provenance.

## Validation checklist

- Run the automated tests and record the actual result.
- Open all four Streamlit tabs; verify missing data displays as null/N/A, not zero.
- Confirm COMM_C is marked both missing and stale.
- Compare a 10 percentage-point cooling access improvement in COMM_A (35% to 45%).
- Optionally test Gemini with a valid personal API key, inspect output and save a human review.
- Export CSV/JSON and inspect local audit records.

**Status:** Educational source code, sample data, and automated tests provided. Do not claim the Streamlit interface or live Gemini integration has been verified until tested in the target environment.

**Evidence first. Engineering second. Measurable impact as the goal.**
