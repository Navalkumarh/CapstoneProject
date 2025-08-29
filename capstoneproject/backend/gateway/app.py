from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import requests, os, datetime, jwt, functools

POLICY_URL = os.getenv("POLICY_SERVICE_URL", "http://policy-service:5001")
CLAIM_URL = os.getenv("CLAIM_SERVICE_URL", "http://claim-service:5002")
DB_URL = os.getenv("AUTH_DB_URL", "sqlite:///auth.db")
JWT_SECRET = os.getenv("JWT_SECRET", "devsecret")

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default="user")
    user_id = db.Column(db.Integer, nullable=True)

@app.before_request
def ensure_db():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username="admin@ims.com").first():
            db.session.add(User(username="admin@ims.com", password="admin123", role="admin", user_id=0))
            db.session.commit()

def issue_token(u: User):
    payload = {"sub": u.id, "username": u.username, "role": u.role, "user_id": u.user_id,
               "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=8)}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def read_token():
    auth = request.headers.get("Authorization","")
    token = auth.split(" ",1)[1] if auth.startswith("Bearer ") else request.args.get("token")
    if not token: return None
    try: return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except Exception: return None

def require_auth(role=None):
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            claims = read_token()
            if not claims: return jsonify({"error":"unauthorized"}), 401
            if role and claims.get("role") != role: return jsonify({"error":"forbidden"}), 403
            request.user = claims
            return fn(*args, **kwargs)
        return wrapper
    return deco

def proxy(method, url, payload=None, files=None):
    r = requests.request(method, url, json=None if files else payload, data=payload if files else None, files=files, timeout=20)
    try: return (r.json(), r.status_code, r.headers)
    except Exception: return (r.text, r.status_code, r.headers)

# Auth
@app.post("/api/auth/register")
def register():
    data = request.json or {}
    username = data.get("username"); password = data.get("password"); user_id = data.get("user_id")
    if user_id is None or username is None or password is None:
        return jsonify({"error":"username, password, user_id required"}), 400
    try: user_id = int(user_id)
    except Exception: return jsonify({"error":"user_id must be integer"}), 400
    if user_id < 0: return jsonify({"error":"user_id must be non-negative"}), 400
    if User.query.filter_by(username=username).first(): return jsonify({"error":"username exists"}), 409
    u = User(username=username, password=password, role="user", user_id=user_id)
    db.session.add(u); db.session.commit()
    token = issue_token(u)
    return jsonify({"message":"registered","token":token,"role":u.role,"user_id":u.user_id})

@app.post("/api/auth/login")
def login():
    data = request.json or {}
    u = User.query.filter_by(username=data.get("username"), password=data.get("password")).first()
    if not u: return jsonify({"error":"invalid credentials"}), 401
    token = issue_token(u)
    return jsonify({"token":token,"role":u.role,"username":u.username,"user_id":u.user_id})

# Policies
@app.get("/api/policies/by-user/<int:user_id>")
@require_auth()
def policies_by_user(user_id):
    if request.user.get("role") != "admin" and request.user.get("user_id") != user_id:
        return jsonify({"error":"forbidden"}), 403
    body, code, _ = proxy("GET", f"{POLICY_URL}/policies/by-user/{user_id}")
    return (body, code)

@app.route("/api/policies", methods=["GET","POST"])
@require_auth("admin")
def policies():
    payload = request.json if request.method == "POST" else None
    body, code, _ = proxy(request.method, f"{POLICY_URL}/policies", payload)
    return (body, code)

@app.route("/api/policies/<int:pid>", methods=["GET","PUT","DELETE"])
@require_auth("admin")
def policy_detail(pid):
    payload = request.json if request.method in ["PUT"] else None
    body, code, _ = proxy(request.method, f"{POLICY_URL}/policies/{pid}", payload)
    return (body, code)

@app.get("/api/policies/search")
@require_auth("admin")
def policy_search():
    import requests as rq
    q = request.args.get("q","")
    body, code, _ = proxy("GET", f"{POLICY_URL}/policies/search?q={rq.utils.quote(q)}")
    return (body, code)

@app.get("/api/policies/verify/<policy_number>")
@require_auth()
def verify(policy_number):
    import requests as rq
    body, code, _ = proxy("GET", f"{POLICY_URL}/policies/verify/{rq.utils.quote(policy_number)}")
    return (body, code)

# Claims
@app.route("/api/claims", methods=["GET","POST"])
@require_auth()
def claims():
    import requests as rq
    if request.method == "POST":
        policy_number = request.form.get("policy_number") if request.files else (request.json or {}).get("policy_number")
        if request.user.get("role") != "admin":
            vr, vc, _ = proxy("GET", f"{POLICY_URL}/policies/verify/{rq.utils.quote(policy_number)}")
            if vc != 200 or not vr.get("policy") or vr["policy"]["user_id"] != request.user.get("user_id"):
                return jsonify({"error":"policy not owned by user"}), 403
        if request.files:
            files = {"file": request.files.get("file")} if request.files.get("file") else None
            data = {k: request.form.get(k) for k in ["policy_number","description"]}
            body, code, _ = proxy("POST", f"{CLAIM_URL}/claims", payload=data, files=files)
            return (body, code)
        else:
            body, code, _ = proxy("POST", f"{CLAIM_URL}/claims", payload=request.json)
            return (body, code)
    if request.user.get("role") == "admin":
        body, code, _ = proxy("GET", f"{CLAIM_URL}/claims")
        return (body, code)
    return claims_by_user(request.user.get("user_id"))

@app.get("/api/claims/by-user/<int:user_id>")
@require_auth()
def claims_by_user(user_id:int):
    import requests as rq
    if request.user.get("role") != "admin" and request.user.get("user_id") != user_id:
        return jsonify({"error":"forbidden"}), 403
    pr, pc, _ = proxy("GET", f"{POLICY_URL}/policies/by-user/{user_id}")
    if pc != 200: return jsonify({"error":"failed to fetch policies"}), 502
    pnos = {p.get("policy_number") for p in pr}
    cr, cc, _ = proxy("GET", f"{CLAIM_URL}/claims")
    if cc != 200: return jsonify({"error":"failed to fetch claims"}), 502
    return jsonify([c for c in cr if c.get("policy_number") in pnos])

@app.route("/api/claims/<int:cid>", methods=["GET","PUT","DELETE"])
@require_auth()
def claim_detail(cid):
    import requests as rq
    if request.method == "DELETE" and request.user.get("role") != "admin":
        cr, cc, _ = proxy("GET", f"{CLAIM_URL}/claims")
        if cc == 200:
            found = next((c for c in cr if c.get("claim_id")==cid), None)
            if found:
                vr, vc, _ = proxy("GET", f"{POLICY_URL}/policies/verify/{rq.utils.quote(found.get('policy_number'))}")
                if vc==200 and vr.get("policy") and vr["policy"]["user_id"] != request.user.get("user_id"):
                    return jsonify({"error":"forbidden"}), 403
    payload = request.json if request.method in ["PUT"] else None
    body, code, _ = proxy(request.method, f"{CLAIM_URL}/claims/{cid}", payload)
    return (body, code)

@app.post("/api/claims/<int:cid>/approve")
@require_auth("admin")
def claim_approve(cid):
    body, code, _ = proxy("POST", f"{CLAIM_URL}/claims/{cid}/approve", request.json)
    return (body, code)

@app.post("/api/claims/<int:cid>/reject")
@require_auth("admin")
def claim_reject(cid):
    body, code, _ = proxy("POST", f"{CLAIM_URL}/claims/{cid}/reject", request.json)
    return (body, code)

@app.get("/uploads/<path:name>")
def uploads(name):
    import requests as rq
    claims = read_token()
    if not claims: return jsonify({"error":"unauthorized"}), 401
    if claims.get("role") != "admin":
        cr = rq.get(f"{CLAIM_URL}/claims", timeout=20)
        if cr.status_code != 200: return jsonify({"error":"failed to fetch claims"}), 502
        claim_list = cr.json()
        found = next((c for c in claim_list if c.get("attachment")==name), None)
        if not found: return jsonify({"error":"not found"}), 404
        vr = rq.get(f"{POLICY_URL}/policies/verify/{found.get('policy_number')}", timeout=20)
        if vr.status_code != 200 or not vr.json().get("policy") or vr.json()["policy"]["user_id"] != claims.get("user_id"):
            return jsonify({"error":"forbidden"}), 403
    r = rq.get(f"{CLAIM_URL}/uploads/{name}", stream=True, timeout=20)
    headers = { "Content-Type": r.headers.get("Content-Type", "application/octet-stream") }
    if request.args.get("dl") == "1":
        headers["Content-Disposition"] = f'attachment; filename="{name}"'
    else:
        headers["Content-Disposition"] = f'inline; filename="{name}"'
    return Response(r.content, status=r.status_code, headers=headers)

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=int(os.getenv("PORT", 5000)), debug=True)
