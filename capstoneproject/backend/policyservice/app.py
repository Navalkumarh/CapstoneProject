from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Policy
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

DB_URL = os.getenv("POLICY_DB_URL", "sqlite:///policy.db")
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.before_request
def ensure_db():
    with app.app_context():
        db.create_all()

def _date_ok(start:str, end:str):
    try:
        s = datetime.fromisoformat(start)
        e = datetime.fromisoformat(end)
        return e > s
    except Exception:
        return False

@app.get("/policies")
def list_policies():
    q = Policy.query.order_by(Policy.policy_id.desc()).all()
    return jsonify([p.to_dict() for p in q])

@app.post("/policies")
def create_policy():
    data = request.json or {}
    required = ["policy_number","customer_name","type","premium","start_date","end_date","user_id"]
    if not all(k in data for k in required):
        return jsonify({"error":"missing fields"}), 400
    try:
        premium = float(data["premium"]); user_id = int(data["user_id"])
    except Exception:
        return jsonify({"error":"premium must be number and user_id integer"}), 400
    if premium < 0 or user_id < 0:
        return jsonify({"error":"premium and user_id must be non-negative"}), 400
    if not _date_ok(data["start_date"], data["end_date"]):
        return jsonify({"error":"end_date must be greater than start_date"}), 400
    if Policy.query.filter_by(policy_number=data["policy_number"]).first():
        return jsonify({"error":"policy_number exists"}), 409
    p = Policy(
        policy_number=data["policy_number"],
        customer_name=data["customer_name"],
        type=data["type"],
        premium=premium,
        start_date=data["start_date"],
        end_date=data["end_date"],
        user_id=user_id
    )
    db.session.add(p); db.session.commit()
    return jsonify(p.to_dict()), 201

@app.get("/policies/<int:pid>")
def get_policy(pid):
    p = Policy.query.get_or_404(pid)
    return jsonify(p.to_dict())

@app.put("/policies/<int:pid>")
def update_policy(pid):
    p = Policy.query.get_or_404(pid)
    data = request.json or {}
    sd = data.get("start_date", p.start_date)
    ed = data.get("end_date", p.end_date)
    if not _date_ok(sd, ed):
        return jsonify({"error":"end_date must be greater than start_date"}), 400
    for k in ["policy_number","customer_name","type","start_date","end_date"]:
        if k in data: setattr(p, k, data[k])
    if "premium" in data:
        try:
            val = float(data["premium"])
            if val < 0: return jsonify({"error":"premium must be non-negative"}), 400
            p.premium = val
        except Exception:
            return jsonify({"error":"premium must be number"}), 400
    if "user_id" in data:
        try:
            uid = int(data["user_id"])
            if uid < 0: return jsonify({"error":"user_id must be non-negative"}), 400
            p.user_id = uid
        except Exception:
            return jsonify({"error":"user_id must be integer"}), 400
    db.session.commit()
    return jsonify(p.to_dict())

@app.delete("/policies/<int:pid>")
def delete_policy(pid):
    p = Policy.query.get_or_404(pid)
    db.session.delete(p); db.session.commit()
    return jsonify({"success": True})

@app.get("/policies/search")
def search():
    q = (request.args.get("q") or "").strip().lower()
    if not q: return list_policies()
    res = Policy.query.filter(
        (Policy.policy_number.ilike(f"%{q}%")) |
        (Policy.customer_name.ilike(f"%{q}%")) |
        (Policy.type.ilike(f"%{q}%"))
    ).order_by(Policy.policy_id.desc()).all()
    return jsonify([p.to_dict() for p in res])

@app.get("/policies/by-user/<int:user_id>")
def by_user(user_id:int):
    res = Policy.query.filter_by(user_id=user_id).order_by(Policy.policy_id.desc()).all()
    return jsonify([p.to_dict() for p in res])

@app.get("/policies/verify/<policy_number>")
def verify(policy_number:str):
    p = Policy.query.filter_by(policy_number=policy_number).first()
    return jsonify({"exists": bool(p), "policy": p.to_dict() if p else None})

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=int(os.getenv("PORT", 5000)), debug=True)
