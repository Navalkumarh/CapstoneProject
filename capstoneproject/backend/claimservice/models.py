from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()

class Claim(db.Model):
    __tablename__ = "claims"
    claim_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    policy_number = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Pending")
    remarks = db.Column(db.String(500), nullable=True)
    attachment = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
