"""Four-tab educational climate justice dashboard."""
import json, os
from pathlib import Path
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from core import Community, assess, compare_intervention, digest
from storage import init, list_reviews, save_review
from ai_gateway import explain

ROOT=Path(__file__).resolve().parent
load_dotenv(ROOT/'.env')
COMMUNITIES=[Community.model_validate(x) for x in json.loads((ROOT/'data/communities.json').read_text(encoding='utf-8'))]
REFERENCES=json.loads((ROOT/'data/references.json').read_text(encoding='utf-8'))
DB=ROOT/'local_data/reviews.sqlite3'
init(DB)
st.set_page_config(page_title='Climate Justice & Social Impact Lab',page_icon='🌍',layout='wide')
st.markdown('<style>.stApp{background:#081b31;color:#e7f6ff}h1,h2,h3{color:#b7edff!important}[data-testid="stMetric"]{background:#103550;border:1px solid #24748a;padding:12px;border-radius:10px}</style>',unsafe_allow_html=True)
st.title('🌍 Climate Justice & Social Impact Lab V1.0')
st.caption('COP31 AI Solutions Lab | Day 10 | November 18, 2026')
st.warning('All community records are SYNTHETIC. No personal data, vulnerability ranking, real-world outcomes, or resource eligibility decisions.')
metrics=[assess(c) for c in COMMUNITIES]
tabs=st.tabs(['🌍 Social Impact Overview','🌡️ Climate Vulnerability Analysis','🤖 AI & Human Review','📤 Export & Methodology'])
with tabs[0]:
    st.subheader('Illustrative community-level indicators')
    a,b,c=st.columns(3)
    a.metric('Synthetic communities',len(COMMUNITIES))
    b.metric('Records with quality flags',sum(bool(m['quality_flags']) for m in metrics))
    c.metric('Recorded human reviews',len(list_reviews(DB)))
    st.dataframe(pd.DataFrame(metrics),hide_index=True,use_container_width=True)
    st.info('Compare indicators separately; do not combine them into a vulnerability score or community ranking.')
with tabs[1]:
    st.subheader('Exposure, access, data quality and illustrative intervention')
    selected=st.selectbox('Select synthetic community',[c.name for c in COMMUNITIES],key='analysis')
    c=next(x for x in COMMUNITIES if x.name==selected)
    m=assess(c)
    st.json(m)
    if m['quality_flags']: st.warning('Quality flags: '+', '.join(m['quality_flags']))
    st.markdown('**Hypothetical improvements to access indicators (percentage points)**')
    cooling=st.slider('Cooling access improvement (pp)',0,50,10)
    shelter=st.slider('Accessible shelter improvement (pp)',0,50,10)
    result=compare_intervention(c,cooling,shelter)
    if result['available']: st.json(result)
    else: st.error(result['reason']+'; no value is imputed.')
    st.caption('No claims of cost, feasibility, actual improvement or measured benefits.')
with tabs[2]:
    st.subheader('Optional Gemini explanation with human review')
    selected=st.selectbox('Select synthetic community for explanation',[c.name for c in COMMUNITIES],key='ai')
    c=next(x for x in COMMUNITIES if x.name==selected)
    if 'ai_output' not in st.session_state: st.session_state.ai_output=None
    if 'ai_source' not in st.session_state: st.session_state.ai_source=None
    st.caption('Clicking Generate sends the selected synthetic record and indicators to the Google Gemini API. Do not enter personal data.')
    if st.button('Generate optional AI explanation'):
        try:
            with st.spinner('Requesting structured explanation...'):
                answer=explain(c.model_dump(),assess(c),os.getenv('GEMINI_API_KEY','').strip(),os.getenv('GEMINI_MODEL','gemini-2.5-flash'))
            st.session_state.ai_output=answer.model_dump()
            st.session_state.ai_source=c.model_dump()
            st.success('Structured explanation returned. Human review is required.')
        except Exception as exc: st.error(f'AI request failed: {exc}')
    if st.session_state.ai_output and st.session_state.ai_source and st.session_state.ai_source['id'] != c.id:
        st.info('The saved AI explanation belongs to another community. Generate a new explanation before reviewing this selection.')
    if st.session_state.ai_output and st.session_state.ai_source and st.session_state.ai_source['id'] == c.id:
        st.json(st.session_state.ai_output)
        with st.form('review'):
            role=st.text_input('Reviewer role (no personal names required)',value='Educational reviewer')
            decision=st.selectbox('Decision',['needs_revision','approved','rejected'])
            rationale=st.text_area('Rationale',value='Verify evidence provenance and review uncertainty.')
            if st.form_submit_button('Save human review'):
                try:
                    rid=save_review(DB,st.session_state.ai_source['id'],decision,role,rationale,st.session_state.ai_source,st.session_state.ai_output)
                    st.success(f'Local review #{rid} saved')
                except Exception as exc: st.error(str(exc))
with tabs[3]:
    st.subheader('Export, evidence and methodology')
    st.download_button('Download indicators CSV',pd.DataFrame(metrics).to_csv(index=False).encode('utf-8'),'climate_justice_indicators.csv','text/csv')
    review_df=pd.DataFrame(list_reviews(DB),columns=['id','timestamp_utc','community_id','decision','reviewer_role','rationale','input_sha256','output_sha256'])
    st.download_button('Download human review CSV',review_df.to_csv(index=False).encode('utf-8'),'human_reviews.csv','text/csv')
    data={'communities':[c.model_dump() for c in COMMUNITIES],'indicators':metrics,'reviews':list_reviews(DB),'references':REFERENCES,'data_sha256':digest([c.model_dump() for c in COMMUNITIES])}
    st.download_button('Download full JSON',json.dumps(data,indent=2,ensure_ascii=False),'climate_justice_lab.json','application/json')
    st.markdown('**Background references — not sources for synthetic numbers**')
    for ref in REFERENCES: st.markdown(f"- [{ref['name']}]({ref['url']}) — {ref['role']}")
    st.markdown('**Method:** validate community-level synthetic inputs; display exposure and access measures separately; flag missing/stale data; calculate hypothetical percentage-point changes; optionally generate structured AI explanations; record human review.')
    st.warning('No calibrated vulnerability model, personal profiling, individual-level decisions, live data or verified real-world impact. Local SQLite logs and SHA-256 hashes are not tamper-proof.')
