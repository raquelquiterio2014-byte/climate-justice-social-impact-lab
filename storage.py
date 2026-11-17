"""Local, editable audit trail. No personal information required."""
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from core import digest

def init(db_path):
    Path(db_path).parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(db_path) as db:
        db.execute('CREATE TABLE IF NOT EXISTS reviews (id INTEGER PRIMARY KEY, timestamp_utc TEXT, community_id TEXT, decision TEXT, reviewer_role TEXT, rationale TEXT, input_sha256 TEXT, output_sha256 TEXT)')

def save_review(db_path, community_id, decision, reviewer_role, rationale, inputs, output):
    if decision not in ('needs_revision','approved','rejected'): raise ValueError('Unknown review decision')
    if len(reviewer_role.strip()) < 2 or len(rationale.strip()) < 5: raise ValueError('Reviewer role and meaningful rationale are required')
    init(db_path)
    with sqlite3.connect(db_path) as db:
        cursor=db.execute('INSERT INTO reviews (timestamp_utc,community_id,decision,reviewer_role,rationale,input_sha256,output_sha256) VALUES (?,?,?,?,?,?,?)',
            (datetime.now(timezone.utc).isoformat(),community_id,decision,reviewer_role.strip(),rationale.strip(),digest(inputs),digest(output)))
        return cursor.lastrowid

def list_reviews(db_path):
    init(db_path)
    with sqlite3.connect(db_path) as db:
        db.row_factory=sqlite3.Row
        return [dict(x) for x in db.execute('SELECT * FROM reviews ORDER BY id DESC')]
