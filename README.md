# 🧠 PredictX AI Portal — VSCode Setup Guide

A full-stack ML web application with 4 real-time AI prediction modules.

---

## 📁 FOLDER STRUCTURE

```
PredictX/
├── backend/                        ← Flask REST API (Python)
│   ├── app.py                      ← Flask entry point
│   ├── requirements.txt            ← Python dependencies
│   ├── train_models.py             ← Train all 4 ML models
│   ├── .env                        ← Environment variables
│   ├── routes/
│   │   ├── auth.py                 ← Signup / Login / JWT verify
│   │   ├── gold.py                 ← Indian gold price prediction
│   │   ├── fraud.py                ← Credit card fraud detection
│   │   ├── spam.py                 ← Spam email detection
│   │   └── rainfall.py             ← Rainfall prediction
│   ├── middleware/
│   │   └── auth_middleware.py      ← JWT token decorator
│   ├── models/                     ← Trained .pkl model files (auto-created)
│   └── data/                       ← Put your CSV datasets here
│       ├── gold_data.csv           ← Indian gold MCX data (2015–2022)
│       ├── email_spam.csv          ← Email spam dataset
│       ├── Rainfall.csv            ← Rainfall dataset
│       └── card_transdata.csv      ← Credit card fraud dataset
│
└── frontend/                       ← React app
    ├── package.json
    ├── public/
    │   └── index.html
    └── src/
        ├── index.js                ← React entry point
        ├── App.js                  ← Router & protected routes
        ├── contexts/
        │   └── AuthContext.js      ← JWT user state (login/logout)
        ├── utils/
        │   └── api.js              ← Axios API calls
        ├── styles/
        │   └── global.css          ← Design system (dark theme, tokens)
        ├── components/
        │   ├── Navbar.js
        │   └── Navbar.css
        └── pages/
            ├── LoginPage.js / .css
            ├── Dashboard.js / .css
            ├── GoldPage.js  / .css ← Indian gold (₹/10g)
            ├── FraudPage.js / .css
            ├── SpamPage.js  / .css
            └── RainfallPage.js / .css
```

---

## 🛠️ STEP-BY-STEP SETUP IN VSCODE

### PREREQUISITES — Install these first

| Tool        | Download link                        |
|-------------|--------------------------------------|
| Python 3.10+| https://www.python.org/downloads/    |
| Node.js 18+ | https://nodejs.org/                  |
| VSCode      | https://code.visualstudio.com/       |
| Git         | https://git-scm.com/ (optional)      |

### RECOMMENDED VSCODE EXTENSIONS
Install from Extensions panel (Ctrl+Shift+X):
- **Python** (Microsoft)
- **ES7+ React/Redux/GraphQL** snippets
- **Prettier - Code Formatter**
- **Thunder Client** (test API endpoints inside VSCode)

---

## 🐍 BACKEND SETUP (Flask)

Open a terminal in VSCode (`Ctrl+`` ` ``):

```bash
# 1. Navigate to backend folder
cd PredictX/backend

# 2. Create a Python virtual environment
python -m venv venv

# 3. Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Install all Python packages
pip install -r requirements.txt

# 5. Add your datasets to the data/ folder:
#    data/gold_data.csv
#    data/email_spam.csv
#    data/Rainfall.csv
#    data/card_transdata.csv

# 6. Train the ML models (creates .pkl files in models/)
python train_models.py

# 7. Start the Flask server
python app.py
```

✅ Backend running at: **http://localhost:5000**
✅ Health check: **http://localhost:5000/api/health**

---

## ⚛️ FRONTEND SETUP (React)

Open a **second terminal** in VSCode:

```bash
# 1. Navigate to frontend folder
cd PredictX/frontend

# 2. Install Node packages
npm install

# 3. Start the React dev server
npm start
```

✅ Frontend running at: **http://localhost:3000**

> The `"proxy": "http://localhost:5000"` in package.json automatically
> forwards all `/api/` requests to Flask — no CORS issues!

---

## 🚀 HOW TO RUN (DAILY USE)

Every time you open the project:

**Terminal 1 — Backend:**
```bash
cd PredictX/backend
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
python app.py
```

**Terminal 2 — Frontend:**
```bash
cd PredictX/frontend
npm start
```

Then open **http://localhost:3000** in your browser.

---

## 🔌 API ENDPOINTS REFERENCE

| Method | Endpoint               | Description            |
|--------|------------------------|------------------------|
| POST   | /api/auth/signup       | Create account         |
| POST   | /api/auth/login        | Login → JWT token      |
| GET    | /api/auth/verify       | Verify JWT token       |
| POST   | /api/gold/predict      | Indian gold price (₹)  |
| GET    | /api/gold/history      | Historical chart data  |
| POST   | /api/fraud/predict     | Fraud detection        |
| POST   | /api/spam/predict      | Spam email detection   |
| POST   | /api/rainfall/predict  | Rainfall prediction    |
| GET    | /api/health            | Server health check    |

---

## 📊 ML MODELS SUMMARY

| Module    | Algorithm              | Accuracy   | Output          |
|-----------|------------------------|------------|-----------------|
| Gold      | Gradient Boosting      | R² 99.96%  | ₹ per 10 grams  |
| Fraud     | Random Forest          | 99.8%      | Fraud / Legit   |
| Spam      | TF-IDF + Logistic Reg  | 97.6%      | Spam / Not Spam |
| Rainfall  | Random Forest          | 100%       | Rain / No Rain  |

---

## ☁️ DEPLOYMENT (OPTIONAL)

**Backend → Render.com (free)**
1. Push `backend/` to GitHub
2. New Web Service on render.com
3. Build command: `pip install -r requirements.txt`
4. Start command:  `gunicorn app:create_app()`
5. Add env variable: `SECRET_KEY=your-secret-key`

**Frontend → Vercel.com (free)**
1. Push `frontend/` to GitHub
2. Import on vercel.com
3. Set env variable: `REACT_APP_API_URL=https://your-render-url.onrender.com`
4. Update `frontend/src/utils/api.js` to use `process.env.REACT_APP_API_URL`

---

## 🐛 COMMON ISSUES

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` with venv activated |
| `npm: command not found` | Install Node.js from nodejs.org |
| CORS error in browser | Make sure Flask is running on port 5000 |
| Model not found error | Run `python train_models.py` first |
| Port 3000 already in use | React will ask to use port 3001 — press Y |
| Port 5000 already in use | Change port in `app.py`: `app.run(port=5001)` and update package.json proxy |
