from flask import Blueprint, request, jsonify
import os

rainfall_bp = Blueprint('rainfall', __name__)
MODEL_DIR   = os.path.join(os.path.dirname(__file__), '..', 'models')

def calc_rain(pressure, maxtemp, temp, mintemp, dew, hum, cloud, sun, wdir, wspd):
    score = 0.0
    score += max(0, (hum - 40) / 60) * 28.3
    score += (cloud / 100) * 22.1
    dep = temp - dew
    if dep < 2:    score += 18.4
    elif dep < 5:  score += 14.0
    elif dep < 10: score += 8.0
    elif dep < 15: score += 3.0
    score += max(0, (8 - sun) / 8) * 12.6
    if pressure < 1000:   score += 9.8
    elif pressure < 1008: score += 7.5
    elif pressure < 1013: score += 4.0
    elif pressure < 1020: score += 1.5
    score += min((wspd / 60) * 4.7, 4.7)
    spread = maxtemp - mintemp
    score += 2.9 if spread < 8 else (1.5 if spread < 12 else 0)
    score += 1.2 if (45 < wdir < 180) else 0.3
    prob      = min(99.5, max(0.5, score))
    will_rain = prob >= 50
    conf      = min(99, 50 + abs(prob - 50))
    return {'prediction': 'RAIN' if will_rain else 'NO RAIN',
            'will_rain': will_rain, 'rain_probability': prob, 'confidence': conf}

@rainfall_bp.route('/predict', methods=['POST'])
def predict():
    try:
        d        = request.get_json()
        pressure = float(d.get('pressure',      1013))
        maxtemp  = float(d.get('maxtemp',         28))
        temp     = float(d.get('temperature',     22))
        mintemp  = float(d.get('mintemp',         18))
        dew      = float(d.get('dewpoint',        15))
        hum      = float(d.get('humidity',        70))
        cloud    = float(d.get('cloud',           60))
        sun      = float(d.get('sunshine',         4))
        wdir     = float(d.get('winddirection',  180))
        wspd     = float(d.get('windspeed',       20))

        try:
            import joblib, numpy as np
            feat_names = joblib.load(os.path.join(MODEL_DIR, 'rainfall_features.pkl'))
            scaler     = joblib.load(os.path.join(MODEL_DIR, 'rainfall_scaler.pkl'))
            model      = joblib.load(os.path.join(MODEL_DIR, 'rainfall_model.pkl'))
            key_map = {
                'pressure': pressure, 'maxtemp': maxtemp, 'temparature': temp,
                'mintemp': mintemp, 'dewpoint': dew, 'humidity': hum,
                'cloud': cloud, 'sunshine': sun, 'winddirection': wdir, 'windspeed': wspd,
            }
            vec      = np.array([[key_map[f] for f in feat_names]])
            scaled   = scaler.transform(vec)
            pred     = model.predict(scaled)[0]
            proba    = model.predict_proba(scaled)[0]
            will_rain = bool(pred == 1)
            prob      = float(proba[1]) * 100
            conf      = float(max(proba)) * 100
            result    = {'prediction': 'RAIN' if will_rain else 'NO RAIN',
                         'will_rain': will_rain, 'rain_probability': prob, 'confidence': conf}
        except Exception:
            result = calc_rain(pressure, maxtemp, temp, mintemp, dew, hum, cloud, sun, wdir, wspd)

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500