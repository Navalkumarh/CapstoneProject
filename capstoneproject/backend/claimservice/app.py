import os
import mimetypes
import logging
from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS
from werkzeug.utils import secure_filename
from models import db, Claim

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('claimservice')

app = Flask(__name__)
CORS(app)

DB_URL = os.getenv('CLAIM_DB_URL', 'sqlite:///claim.db')
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOADS_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'uploads'))
os.makedirs(UPLOADS_DIR, exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.before_request
def ensure_db():
    with app.app_context():
        db.create_all()

def to_dict(c: Claim):
    return {
        'claim_id': c.claim_id,
        'policy_number': c.policy_number,
        'description': c.description,
        'status': c.status,
        'remarks': c.remarks,
        'attachment': c.attachment,
        'created_at': c.created_at.isoformat() if getattr(c, 'created_at', None) else None,
    }

@app.get('/claims')
def list_claims():
    q = Claim.query.order_by(Claim.claim_id.desc()).all()
    return jsonify([to_dict(c) for c in q])

@app.post('/claims')
def create_claim():
    if request.files:
        policy_number = request.form.get('policy_number')
        description = request.form.get('description')
        file = request.files.get('file')
    else:
        data = request.json or {}
        policy_number = data.get('policy_number')
        description = data.get('description')
        file = None

    if not policy_number or not description:
        return jsonify({'error': 'policy_number and description required'}), 400
    if not file or not getattr(file, 'filename', ''):
        return jsonify({'error': 'attachment file is required'}), 400

    safe_name = secure_filename(file.filename) or 'upload.bin'
    path = os.path.join(UPLOADS_DIR, safe_name)
    if os.path.exists(path):
        base, ext = os.path.splitext(safe_name)
        i = 1
        while True:
            candidate = f"{base}_{i}{ext}"
            path = os.path.join(UPLOADS_DIR, candidate)
            if not os.path.exists(path):
                safe_name = candidate
                break
            i += 1

    file.save(path)

    c = Claim(policy_number=policy_number, description=description, status='Pending', remarks=None, attachment=safe_name)
    db.session.add(c); db.session.commit()
    return jsonify(to_dict(c)), 201

@app.get('/claims/<int:cid>')
def get_claim(cid):
    c = Claim.query.get_or_404(cid)
    return jsonify(to_dict(c))

@app.put('/claims/<int:cid>')
def update_claim(cid):
    c = Claim.query.get_or_404(cid)
    data = request.json or {}
    for k in ['policy_number','description','status','remarks','attachment']:
        if k in data:
            setattr(c, k, data[k])
    db.session.commit()
    return jsonify(to_dict(c))

@app.delete('/claims/<int:cid>')
def delete_claim(cid):
    c = Claim.query.get_or_404(cid)
    db.session.delete(c); db.session.commit()
    return jsonify({'success': True})

@app.post('/claims/<int:cid>/approve')
def approve(cid):
    c = Claim.query.get_or_404(cid)
    data = request.json or {}
    c.status = 'Approved'
    c.remarks = data.get('remarks') or 'Approved by admin'
    db.session.commit()
    return jsonify(to_dict(c))

@app.post('/claims/<int:cid>/reject')
def reject(cid):
    c = Claim.query.get_or_404(cid)
    data = request.json or {}
    c.status = 'Rejected'
    c.remarks = data.get('remarks') or 'Rejected by admin'
    db.session.commit()
    return jsonify(to_dict(c))

@app.get('/uploads/<path:name>')
def uploads(name):
    guessed, _ = mimetypes.guess_type(name)
    resp = make_response(send_from_directory(UPLOADS_DIR, name, mimetype=guessed, as_attachment=False))
    resp.headers['Content-Disposition'] = f'inline; filename="{name}"'
    if guessed:
        resp.headers['Content-Type'] = guessed
    return resp

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5002))
    logger.info('Starting Claim Service on http://localhost:%s ...', port)
    app.run(port=port, debug=True, host='0.0.0.0')