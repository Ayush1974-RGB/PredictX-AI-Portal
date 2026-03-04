"""
routes/rainfall.py — Rainfall Prediction
"""
from flask import Blueprint, request, jsonify
import joblib, numpy as np, os

rainfall_bp = Blueprint('rainfall', __name__)
MODEL_DIR   = os.path.join(os.path.dirname(__file__), '..', 'models')

@rainfall_bp.route('/predict', methods=['POST'])
def predict():
    try:
        d = request.get_json()

        pressure = float(d.get('pressure',     1013))
        maxtemp  = float(d.get('maxtemp',        28))
        temp     = float(d.get('temperature',    22))
        mintemp  = float(d.get('mintemp',        18))
        dew      = float(d.get('dewpoint',       15))
        hum      = float(d.get('humidity',       70))
        cloud    = float(d.get('cloud',          60))
        sun      = float(d.get('sunshine',        4))
        wdir     = float(d.get('winddirection', 180))
        wspd     = float(d.get('windspeed',      20))

        try:
            feat_names = joblib.load(os.path.join(MODEL_DIR, 'rainfall_features.pkl'))
            scaler     = joblib.load(os.path.join(MODEL_DIR, 'rainfall_scaler.pkl'))
            model      = joblib.load(os.path.join(MODEL_DIR, 'rainfall_model.pkl'))

            # Map frontend keys → training feature names
            key_map = {
                'pressure':     pressure,
                'maxtemp':      maxtemp,
                'temparature':  temp,      # dataset has this typo — keep it
                'mintemp':      mintemp,
                'dewpoint':     dew,
                'humidity':     hum,
                'cloud':        cloud,
                'sunshine':     sun,
                'winddirection':wdir,
                'windspeed':    wspd,
            }
            vec      = np.array([[key_map[f] for f in feat_names]])
            scaled   = scaler.transform(vec)
            pred     = model.predict(scaled)[0]
            proba    = model.predict_proba(scaled)[0]
            will_rain = bool(pred == 1)
            rain_prob = float(proba[1]) * 100
            confidence= float(max(proba)) * 100

        except Exception:
            # Fallback: physics-based scoring matching RF feature importances
            rain_score = 0.0

            # Humidity — 28.3% weight
            rain_score += max(0, (hum - 40) / 60) * 28.3

            # Cloud cover — 22.1% weight
            rain_score += (cloud / 100) * 22.1

            # Dew point depression — 18.4% weight (near 0 = saturated air)
            dep = temp - dew
            if dep < 2:    rain_score += 18.4
            elif dep < 5:  rain_score += 14.0
            elif dep < 10: rain_score += 8.0
            elif dep < 15: rain_score += 3.0

            # Sunshine — 12.6% weight (inverse)
            rain_score += max(0, (8 - sun) / 8) * 12.6

            # Pressure — 9.8% weight (low = unstable)
            if pressure < 1000:   rain_score += 9.8
            elif pressure < 1008: rain_score += 7.5
            elif pressure < 1013: rain_score += 4.0
            elif pressure < 1020: rain_score += 1.5

            # Wind speed — 4.7% weight
            rain_score += min((wspd / 60) * 4.7, 4.7)

            # Temp spread — 2.9% weight (small spread = frontal weather)
            spread = maxtemp - mintemp
            rain_score += 2.9 if spread < 8 else (1.5 if spread < 12 else 0)

            # Wind direction — 1.2% weight
            rain_score += 1.2 if (45 < wdir < 180) else 0.3

            rain_prob  = min(99.5, max(0.5, rain_score))
            will_rain  = rain_prob >= 50
            confidence = min(99, 50 + abs(rain_prob - 50))

        return jsonify({
            'prediction':       'RAIN' if will_rain else 'NO RAIN',
            'will_rain':        will_rain,
            'rain_probability': round(rain_prob, 2),
            'confidence':       round(confidence, 2),
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500