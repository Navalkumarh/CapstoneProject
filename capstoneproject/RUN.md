# Run (No Docker)

Delete auth.db in gateway service
delete node_modules

## 1) Policy Service (5001)

```
cd backend\policyservice
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

```
cd backend\policyservice
.venv\Scripts\activate
python app.py
```

## 2) Claim Service (5002)

```
cd backend\claimservice
rmdir /s /q .venv
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
```
cd backend\claimservice
.venv\Scripts\activate
python app.py
```

## 3) Gateway (5000)

```
cd backend\gateway
rmdir /s /q .venv
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
```
cd backend\gateway
.venv\Scripts\activate
python app.py
```

## 4) Frontend (4200)

```
cd frontend/ims-frontend
npm install
npm start
```

### Default Admin

- Email: `admin@ims.com`
- Password: `admin123`
