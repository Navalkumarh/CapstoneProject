from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Policy(db.Model):
    __tablename__ = "policies"
    policy_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    policy_number = db.Column(db.String(64), unique=True, nullable=False)
    customer_name = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(40), nullable=False)
    premium = db.Column(db.Float, nullable=False, default=0.0)
    start_date = db.Column(db.String(20), nullable=False)  # ISO
    end_date = db.Column(db.String(20), nullable=False)    # ISO
    user_id = db.Column(db.Integer, nullable=False, default=0)
    def to_dict(self):
        return {
            "policy_id": self.policy_id,
            "policy_number": self.policy_number,
            "customer_name": self.customer_name,
            "type": self.type,
            "premium": self.premium,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "user_id": self.user_id,
        }
