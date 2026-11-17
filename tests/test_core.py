import json
from pathlib import Path
import pytest
from pydantic import ValidationError
from core import Community, AIExplanation, assess, compare_intervention, digest, validate_evidence
from storage import save_review, list_reviews
DATA=json.loads((Path(__file__).resolve().parents[1]/'data/communities.json').read_text())
def c(i=0): return Community.model_validate(DATA[i])
def test_three_scenarios(): assert len(DATA)==3
def test_all_synthetic(): assert all(x['source_type']=='synthetic' for x in DATA)
def test_flood(): assert assess(c())['flood_exposure_pct']==65
def test_heat(): assert assess(c(1))['heat_exposure_pct']==75
def test_missing_flag(): assert 'MISSING_DATA' in assess(c(2))['quality_flags']
def test_stale_flag(): assert 'STALE_DATA' in assess(c(2))['quality_flags']
def test_missing_not_zero(): assert assess(c(2))['flood_exposure_pct'] is None
def test_ready(): assert assess(c())['ready_for_comparison']
def test_not_ready(): assert not assess(c(2))['ready_for_comparison']
def test_intervention(): assert compare_intervention(c(),10,20)['cooling_access_after_pct']==45
def test_intervention_caps_at_100(): assert compare_intervention(c(),100,100)['accessible_shelters_after_pct']==100
def test_intervention_missing(): assert not compare_intervention(c(2),10,10)['available']
def test_intervention_negative():
    with pytest.raises(ValueError): compare_intervention(c(),-1,0)
def test_intervention_nan():
    with pytest.raises(ValueError): compare_intervention(c(),float('nan'),0)
def test_bad_percentage():
    with pytest.raises(ValidationError): Community.model_validate({**DATA[0],'flood_exposure_pct':101})
def test_hash_stable(): assert digest({'a':1,'b':2})==digest({'b':2,'a':1})
def test_evidence_good(): assert validate_evidence(AIExplanation(summary='A synthetic community with limited evidence.',evidence_ids=['COMM_A'],suggested_checks=['Review'],limitations=['Synthetic']),['COMM_A'])
def test_evidence_bad(): assert not validate_evidence(AIExplanation(summary='A synthetic community with limited evidence.',evidence_ids=['BAD'],suggested_checks=['Review'],limitations=['Synthetic']),['COMM_A'])
def test_review_roundtrip(tmp_path):
    db=tmp_path/'audit.sqlite3'; save_review(db,'COMM_A','needs_revision','Reviewer','Check data',{},{}); assert list_reviews(db)[0]['decision']=='needs_revision'
def test_review_rejects_bad_decision(tmp_path):
    with pytest.raises(ValueError): save_review(tmp_path/'audit.sqlite3','COMM_A','unknown','Reviewer','Check data',{}, {})
