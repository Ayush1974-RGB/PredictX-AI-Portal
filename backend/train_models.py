"""
PredictX — train_models.py (CORRECTED v2)
==========================================
Run:  python train_models.py  (from inside backend/ folder)

Datasets in backend/data/:
  gold_data.csv       Date, Price(USD/oz), Open, High, Low, Vol
  email_spam.csv      type, text
  Rainfall.csv        pressure,maxtemp,temparature,mintemp,dewpoint,
                      humidity,cloud,sunshine,winddirection,windspeed,rainfall
  card_transdata.csv  distance_from_home,distance_from_last_transaction,
                      ratio_to_median_purchase_price,repeat_retailer,
                      used_chip,used_pin_number,online_order,fraud

KEY POINT — Gold model:
  Trained on raw USD/oz prices. The route (gold.py) converts user ₹/10g
  inputs → USD/oz before predict(), then converts USD/oz output → ₹/10g.
  Do NOT change feature units here.
"""

import os, json, warnings
import numpy  as np
import pandas as pd
from sklearn.model_selection    import train_test_split
from sklearn.preprocessing      import StandardScaler
from sklearn.linear_model       import LogisticRegression
from sklearn.ensemble           import (GradientBoostingRegressor,
                                        RandomForestClassifier)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline           import Pipeline
from sklearn.metrics            import (accuracy_score, r2_score,
                                        mean_absolute_error,
                                        mean_absolute_percentage_error,
                                        classification_report)
import joblib

warnings.filterwarnings('ignore')
os.makedirs('models', exist_ok=True)
import os

# Skip training if data files not present (e.g. on deployment server)
required = ['data/email_spam.csv','data/Rainfall.csv','data/gold_data.csv','data/card_transdata.csv']
if not all(os.path.exists(f) for f in required):
    print("Data files not found — skipping training. Using pre-trained models.")
    exit(0)

# ════════════════════════════════════════════════════════
#  1. SPAM  (TF-IDF + Logistic Regression)
# ════════════════════════════════════════════════════════
print('\n===== [1/4] SPAM EMAIL DETECTION =====')

df = pd.read_csv('data/email_spam.csv')
df.columns = [c.strip().lower() for c in df.columns]

if 'type' in df.columns:
    df['label'] = (df['type'].astype(str).str.strip().str.lower() == 'spam').astype(int)
elif 'label' in df.columns:
    if df['label'].dtype == object:
        df['label'] = (df['label'].astype(str).str.strip().str.lower() == 'spam').astype(int)
    else:
        df['label'] = df['label'].astype(int)
elif 'class' in df.columns:
    df['label'] = (df['class'].astype(str).str.strip().str.lower() == 'spam').astype(int)
else:
    raise ValueError('email_spam.csv needs a type/label/class column')

text_col = next((c for c in ['text','message','body'] if c in df.columns), None)
if not text_col:
    raise ValueError('email_spam.csv needs a text/message/body column')
subj_col = next((c for c in ['title','subject'] if c in df.columns), None)
df['combined'] = (df[subj_col].fillna('') + ' ' if subj_col else '') + df[text_col].fillna('')
df = df.dropna(subset=['combined','label'])

print(f'  Rows: {len(df):,}  Spam={df["label"].sum():,}  Ham={(df["label"]==0).sum():,}')

X_tr, X_te, y_tr, y_te = train_test_split(
    df['combined'], df['label'], test_size=0.2, random_state=42, stratify=df['label']
)
spam_model = Pipeline([
    ('tfidf', TfidfVectorizer(
        max_features=10000, ngram_range=(1,3),
        sublinear_tf=True, stop_words='english', min_df=2
    )),
    ('clf', LogisticRegression(C=5.0, max_iter=2000, class_weight='balanced'))
])
spam_model.fit(X_tr, y_tr)
acc = accuracy_score(y_te, spam_model.predict(X_te))
print(f'  Test Accuracy: {acc*100:.2f}%')
print(classification_report(y_te, spam_model.predict(X_te), target_names=['Ham','Spam']))
joblib.dump(spam_model, 'models/spam_model.pkl')
print('  Saved: models/spam_model.pkl\n')


# ════════════════════════════════════════════════════════
#  2. RAINFALL  (Random Forest)
# ════════════════════════════════════════════════════════
print('===== [2/4] RAINFALL PREDICTION =====')

df = pd.read_csv('data/Rainfall.csv')
df.columns = [c.strip() for c in df.columns]

# Keep the typo 'temparature' — it's in the dataset and route
if 'temperature' in df.columns and 'temparature' not in df.columns:
    df.rename(columns={'temperature': 'temparature'}, inplace=True)

target_col = next(
    (c for c in ['rainfall','RainTomorrow','rain'] if c in df.columns),
    df.columns[-1]
)
df['target'] = (df[target_col].astype(str).str.strip().str.lower()
                .isin(['yes','1','true','rain'])).astype(int)
df = df.dropna()

RAIN_FEAT = [c for c in [
    'pressure','maxtemp','temparature','mintemp',
    'dewpoint','humidity','cloud','sunshine',
    'winddirection','windspeed'
] if c in df.columns]

X = df[RAIN_FEAT].astype(float).values
y = df['target'].values
print(f'  Rows: {len(df):,}  Features: {RAIN_FEAT}')
print(f'  Rain={y.sum():,}  NoRain={(y==0).sum():,}')

X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
rain_scaler = StandardScaler()
X_tr_s = rain_scaler.fit_transform(X_tr)
X_te_s  = rain_scaler.transform(X_te)

rain_model = RandomForestClassifier(
    n_estimators=200, max_depth=12, min_samples_split=4,
    class_weight='balanced', random_state=42, n_jobs=-1
)
rain_model.fit(X_tr_s, y_tr)
acc = accuracy_score(y_te, rain_model.predict(X_te_s))
print(f'  Test Accuracy: {acc*100:.2f}%')
print(classification_report(y_te, rain_model.predict(X_te_s), target_names=['No Rain','Rain']))
joblib.dump(rain_model,  'models/rainfall_model.pkl')
joblib.dump(rain_scaler, 'models/rainfall_scaler.pkl')
joblib.dump(RAIN_FEAT,   'models/rainfall_features.pkl')
print('  Saved: rainfall_model + scaler + features\n')


# ════════════════════════════════════════════════════════
#  3. GOLD  (Gradient Boosting — trained on USD/oz)
#     gold.py route handles all ₹ ↔ USD conversion
# ════════════════════════════════════════════════════════
print('===== [3/4] GOLD PRICE (USD/oz internal) =====')

df = pd.read_csv('data/gold_data.csv')
df.columns = [c.strip() for c in df.columns]

for fmt in ('%d/%m/%Y','%Y-%m-%d','%m/%d/%Y','%d-%m-%Y'):
    try: df['Date'] = pd.to_datetime(df['Date'], format=fmt); break
    except: pass

df = df.sort_values('Date').reset_index(drop=True)

usd_map = {
    2010:45.7, 2011:46.7, 2012:53.4, 2013:58.5, 2014:61.0,
    2015:65.5, 2016:67.1, 2017:65.1, 2018:68.4, 2019:70.4,
    2020:74.1, 2021:73.9, 2022:79.8, 2023:83.0, 2024:84.0
}
df['USD_INR'] = df['Date'].dt.year.map(usd_map).fillna(74.0)

# All features stay in USD/oz (raw dataset units)
df['Price_lag1']     = df['Price'].shift(1)
df['Price_lag3']     = df['Price'].shift(3)
df['Price_lag7']     = df['Price'].shift(7)
df['Price_ma7']      = df['Price'].rolling(7,  min_periods=7).mean()
df['Price_ma14']     = df['Price'].rolling(14, min_periods=14).mean()
df['Price_std7']     = df['Price'].rolling(7,  min_periods=7).std()
df['High_Low_range'] = df['High'] - df['Low']
df['Price_mom5']     = df['Price'].pct_change(5) * 100
df['Month']          = df['Date'].dt.month
df['Quarter']        = df['Date'].dt.quarter
df['DayOfWeek']      = df['Date'].dt.dayofweek
df = df.dropna()

GOLD_FEAT = [c for c in [
    'Price_lag1','Price_lag3','Price_lag7',
    'Open','High_Low_range',
    'Price_ma7','Price_ma14','Price_std7','Price_mom5',
    'USD_INR','Month','Quarter','DayOfWeek'
] if c in df.columns]

X = df[GOLD_FEAT].values
y = df['Price'].values   # ← USD/oz target (NOT ₹)
print(f'  Rows: {len(df):,}  Price: ${y.min():.0f}–${y.max():.0f}/oz (USD)')

split = int(len(X) * 0.8)
X_tr, X_te = X[:split], X[split:]
y_tr, y_te = y[:split], y[split:]

gold_scaler = StandardScaler()
X_tr_s = gold_scaler.fit_transform(X_tr)
X_te_s  = gold_scaler.transform(X_te)

gold_model = GradientBoostingRegressor(
    n_estimators=400, learning_rate=0.04, max_depth=5,
    subsample=0.8, min_samples_split=5, random_state=42
)
gold_model.fit(X_tr_s, y_tr)

y_pred = gold_model.predict(X_te_s)
r2   = r2_score(y_te, y_pred)
mae  = mean_absolute_error(y_te, y_pred)
mape = mean_absolute_percentage_error(y_te, y_pred) * 100
print(f'  Test R²: {r2:.4f}  MAE: ${mae:.2f}/oz  MAPE: {mape:.2f}%')

joblib.dump(gold_model,  'models/gold_india_model.pkl')
joblib.dump(gold_scaler, 'models/gold_india_scaler.pkl')
joblib.dump(GOLD_FEAT,   'models/gold_india_features.pkl')

# Chart history — convert to ₹/10g using historical rates for display
df['Price_INR_10g'] = (df['Price'] * df['USD_INR']) / 3.11035
df_q = df.set_index('Date')['Price_INR_10g'].resample('QE').mean().dropna()
hist = [{'label': d.strftime('%b %y'), 'price': round(float(p))}
        for d, p in df_q.items()]
with open('models/gold_india_history.json', 'w') as f:
    json.dump(hist, f)
print(f'  Saved: gold_india_model + scaler + features + history ({len(hist)} quarters)\n')


# ════════════════════════════════════════════════════════
#  4. FRAUD  (Random Forest — balanced dataset)
# ════════════════════════════════════════════════════════
print('===== [4/4] CREDIT CARD FRAUD DETECTION =====')

df = pd.read_csv('data/card_transdata.csv')
df.columns = [c.strip() for c in df.columns]
df = df.dropna()

FRAUD_FEAT = [c for c in [
    'distance_from_home','distance_from_last_transaction',
    'ratio_to_median_purchase_price',
    'repeat_retailer','used_chip','used_pin_number','online_order'
] if c in df.columns]

fraud_df = df[df['fraud'] == 1]
legit_df = df[df['fraud'] == 0].sample(
    n=min(len(fraud_df) * 4, 240_000), random_state=42
)
df_bal = pd.concat([fraud_df, legit_df]).sample(frac=1, random_state=42)
X = df_bal[FRAUD_FEAT].values
y = df_bal['fraud'].values
print(f'  Balanced rows: {len(df_bal):,}  Fraud={y.sum():,}  Legit={(y==0).sum():,}')

X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
fraud_scaler = StandardScaler()
X_tr_s = fraud_scaler.fit_transform(X_tr)
X_te_s  = fraud_scaler.transform(X_te)

fraud_model = RandomForestClassifier(
    n_estimators=200, max_depth=15, min_samples_split=5,
    class_weight='balanced', random_state=42, n_jobs=-1
)
fraud_model.fit(X_tr_s, y_tr)
acc = accuracy_score(y_te, fraud_model.predict(X_te_s))
print(f'  Test Accuracy: {acc*100:.2f}%')
print(classification_report(y_te, fraud_model.predict(X_te_s), target_names=['Legit','Fraud']))
joblib.dump(fraud_model,  'models/fraud_model.pkl')
joblib.dump(fraud_scaler, 'models/fraud_scaler.pkl')
joblib.dump(FRAUD_FEAT,   'models/fraud_features.pkl')
print('  Saved: fraud_model + scaler + features\n')


# ════════════════════════════════════════════════════════
print('=' * 55)
print('  ALL 4 MODELS TRAINED SUCCESSFULLY')
print('=' * 55)
for fn in sorted(os.listdir('models')):
    kb = os.path.getsize(f'models/{fn}') / 1024
    print(f'  {fn:<45} {kb:>8.1f} KB')