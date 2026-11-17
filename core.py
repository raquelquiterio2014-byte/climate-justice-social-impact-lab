"""Educational community-level climate adaptation comparisons; not eligibility scoring."""
from __future__ import annotations
import hashlib, json, math
from pydantic import BaseModel, Field
from typing import Literal

class Community(BaseModel):
    id: str
    name: str
    source_type: Literal['synthetic']
    flood_exposure_pct: float | None = Field(default=None, ge=0, le=100)
    heat_exposure_pct: float | None = Field(default=None, ge=0, le=100)
    cooling_access_pct: float | None = Field(default=None, ge=0, le=100)
    accessible_shelters_pct: float | None = Field(default=None, ge=0, le=100)
    observation_age_days: int = Field(ge=0)

class AIExplanation(BaseModel):
    summary: str = Field(min_length=20)
    evidence_ids: list[str] = Field(min_length=1)
    suggested_checks: list[str] = Field(min_length=1)
    limitations: list[str] = Field(min_length=1)

def digest(obj: object) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str, ensure_ascii=False).encode()).hexdigest()

def assess(c: Community) -> dict:
    missing = [field for field in ('flood_exposure_pct','heat_exposure_pct','cooling_access_pct','accessible_shelters_pct') if getattr(c,field) is None]
    flags = []
    if missing: flags.append('MISSING_DATA')
    if c.observation_age_days > 30: flags.append('STALE_DATA')
    # Independent indicators: do not combine into a score or rank communities.
    return {'id':c.id,'community':c.name,'flood_exposure_pct':c.flood_exposure_pct,
            'heat_exposure_pct':c.heat_exposure_pct,'cooling_access_pct':c.cooling_access_pct,
            'accessible_shelters_pct':c.accessible_shelters_pct,'missing_fields':missing,
            'quality_flags':flags,'ready_for_comparison':not flags,'source_type':c.source_type}

def compare_intervention(c: Community, cooling_gain_pp: float, shelter_gain_pp: float) -> dict:
    for x in (cooling_gain_pp,shelter_gain_pp):
        if not math.isfinite(x) or x < 0 or x > 100: raise ValueError('Changes must be finite and between 0 and 100 percentage points')
    if c.cooling_access_pct is None or c.accessible_shelters_pct is None:
        return {'available':False,'reason':'Baseline access indicators are missing'}
    return {'available':True,'community_id':c.id,
            'cooling_access_before_pct':c.cooling_access_pct,
            'cooling_access_after_pct':min(100,round(c.cooling_access_pct+cooling_gain_pp,2)),
            'accessible_shelters_before_pct':c.accessible_shelters_pct,
            'accessible_shelters_after_pct':min(100,round(c.accessible_shelters_pct+shelter_gain_pp,2)),
            'note':'Hypothetical percentage-point arithmetic; not measured outcomes or a policy recommendation.'}

def validate_evidence(result: AIExplanation, allowed: list[str]) -> bool:
    return set(result.evidence_ids).issubset(set(allowed))
